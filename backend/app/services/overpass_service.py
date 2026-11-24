import os
import time
from typing import Dict, Any, List, Optional, Tuple
from app.core.config import settings

# Primary and fallback public Overpass endpoints
OVERPASS_ENDPOINTS = [
    getattr(settings, "OVERPASS_API_URL", "https://overpass-api.de/api/interpreter"),
    "https://lz4.overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter"
]

# In-memory TTL cache for Overpass responses (TTL 1 hour)
_OVERPASS_CACHE: Dict[str, Dict[str, Any]] = {}
CACHE_TTL_SECONDS = 3600

def _get_from_cache(cache_key: str) -> Optional[Any]:
    entry = _OVERPASS_CACHE.get(cache_key)
    if entry and (time.time() - entry["timestamp"] < CACHE_TTL_SECONDS):
        return entry["data"]
    return None

def _set_in_cache(cache_key: str, data: Any):
    if len(_OVERPASS_CACHE) > 500:
        oldest = min(_OVERPASS_CACHE.keys(), key=lambda k: _OVERPASS_CACHE[k]["timestamp"])
        _OVERPASS_CACHE.pop(oldest, None)
    _OVERPASS_CACHE[cache_key] = {
        "timestamp": time.time(),
        "data": data
    }

def build_overpass_ql_query(
    lat: float,
    lng: float,
    radius_meters: int,
    tag_filters: List[str],
    limit: int = 15
) -> str:
    """
    Constructs an optimized Overpass QL query restricted to a radius around coordinates.
    Uses 'out center' so ways and relations also return a single representative coordinate.
    """
    radius = max(500, min(35000, radius_meters))
    max_items = max(1, min(30, limit))

    query_parts = []
    for tag_filter in tag_filters:
        # e.g. 'amenity=cafe' or 'natural=waterfall'
        query_parts.append(f"node[{tag_filter}](around:{radius},{lat},{lng});")
        query_parts.append(f"way[{tag_filter}](around:{radius},{lat},{lng});")

    statements = "\n  ".join(query_parts)
    return f"""[out:json][timeout:10];
(
  {statements}
);
out center {max_items};"""

def execute_overpass_query(ql_query: str) -> Optional[List[Dict[str, Any]]]:
    """
    Executes an Overpass QL query across configured endpoints with retry and backoff.
    """
    cache_key = f"ql:{hash(ql_query)}"
    cached = _get_from_cache(cache_key)
    if cached is not None:
        return cached

    import httpx

    headers = {
        "User-Agent": "WanderWise-AI-Travel/2.0 (travel@wanderwise.com)",
        "Accept": "application/json"
    }

    # Attempt query across endpoints
    for endpoint in OVERPASS_ENDPOINTS:
        for attempt in range(2):
            try:
                with httpx.Client(timeout=8.0) as client:
                    resp = client.post(endpoint, data={"data": ql_query}, headers=headers)
                    if resp.status_code == 200:
                        data = resp.json()
                        elements = data.get("elements", [])
                        _set_in_cache(cache_key, elements)
                        return elements
                    elif resp.status_code in [429, 504]:
                        # Rate limited or gateway timeout, brief backoff
                        time.sleep(1.0 * (attempt + 1))
            except Exception as e:
                # brief delay before retry
                time.sleep(0.5)

    return None

def query_osm_places_by_category(
    lat: float,
    lng: float,
    category_tags: List[str],
    radius_meters: int = 15000,
    limit: int = 15
) -> List[Dict[str, Any]]:
    """
    High-level runner: executes Overpass query for specific category tags and filters results.
    """
    ql = build_overpass_ql_query(lat, lng, radius_meters, category_tags, limit=limit)
    raw_elements = execute_overpass_query(ql)
    if not raw_elements:
        return []

    # Filter elements that have a valid name and coordinates
    valid_places = []
    seen_names = set()
    for el in raw_elements:
        tags = el.get("tags", {})
        name = tags.get("name") or tags.get("name:en")
        if not name or len(name.strip()) < 2:
            continue

        normalized_name = name.strip().lower()
        if normalized_name in seen_names:
            continue
        seen_names.add(normalized_name)

        # Extract coordinates (node lat/lon or way center lat/lon)
        item_lat = el.get("lat") or el.get("center", {}).get("lat")
        item_lng = el.get("lon") or el.get("center", {}).get("lon")
        if item_lat is None or item_lng is None:
            continue

        valid_places.append({
            "osm_id": f"{el.get('type', 'node')}_{el.get('id')}",
            "name": name.strip(),
            "lat": float(item_lat),
            "lng": float(item_lng),
            "tags": tags
        })

    return valid_places

def normalize_osm_place(
    osm_item: Dict[str, Any],
    destination_name: str,
    dest_lat: float,
    dest_lng: float,
    inferred_category: str = "Real-World Amenity"
) -> Dict[str, Any]:
    """
    Normalizes an OpenStreetMap Overpass item into the Universal Place Data Structure (Step 9).
    """
    name = osm_item["name"]
    lat = osm_item["lat"]
    lng = osm_item["lng"]
    tags = osm_item.get("tags", {})
    osm_id = osm_item.get("osm_id", "")

    # Calculate actual distance
    from app.services.routing_service import haversine_distance_km
    dist_km = round(haversine_distance_km(dest_lat, dest_lng, lat, lng), 2)

    # Detailed address assembly from OSM tags
    addr_parts = []
    if tags.get("addr:street"):
        addr_parts.append(tags.get("addr:street"))
    if tags.get("addr:suburb"):
        addr_parts.append(tags.get("addr:suburb"))
    if tags.get("addr:city"):
        addr_parts.append(tags.get("addr:city"))
    address_str = ", ".join(addr_parts) if addr_parts else f"{destination_name} Area"

    # Specific category refinement
    cat = inferred_category
    if "amenity" in tags:
        amenity = tags["amenity"].replace("_", " ").title()
        if amenity.lower() == "cafe":
            cat = "Artisan Cafe & Coffee Spot"
        elif amenity.lower() in ["restaurant", "food_court"]:
            cuisine = tags.get("cuisine", "").replace(";", ", ")
            cat = f"Restaurant ({cuisine.title()})" if cuisine else "Authentic Local Restaurant"
        elif amenity.lower() == "hospital":
            cat = "Emergency Medical Hospital"
        elif amenity.lower() == "pharmacy":
            cat = "Pharmacy & Chemist"
        elif amenity.lower() == "atm":
            cat = "24/7 ATM & Banking Point"
        elif amenity.lower() == "bus_station":
            cat = "Public Bus Transit Station"
    elif "natural" in tags:
        nat = tags["natural"].replace("_", " ").title()
        if nat.lower() == "waterfall":
            cat = "Scenic Waterfall & Natural Pool"
        elif nat.lower() in ["peak", "volcano"]:
            cat = "Mountain Peak & Trekking Vista"
        elif nat.lower() == "beach":
            cat = "Sandy Coastal Beach"
    elif "tourism" in tags:
        tour = tags["tourism"].replace("_", " ").title()
        if tour.lower() == "viewpoint":
            cat = "Scenic Viewpoint & Lookout Point"
        elif tour.lower() in ["hotel", "resort"]:
            cat = "Hotel & Resort Accommodation"
        elif tour.lower() == "museum":
            cat = "Museum & Cultural Exhibit"

    # Description and verified attributes
    verified_fields = ["name", "provider_id", "category", "latitude", "longitude", "distance_from_destination_km"]
    desc_elements = []
    if tags.get("cuisine"):
        desc_elements.append(f"Cuisine: {tags.get('cuisine').title()}")
        verified_fields.append("cuisine")
    if tags.get("opening_hours"):
        desc_elements.append(f"Hours: {tags.get('opening_hours')}")
        verified_fields.append("opening_hours")
    if tags.get("phone"):
        desc_elements.append(f"Phone: {tags.get('phone')}")
        verified_fields.append("phone")
    if tags.get("wheelchair") == "yes":
        desc_elements.append("Wheelchair accessible")
    if tags.get("outdoor_seating") == "yes":
        desc_elements.append("Outdoor seating available")

    osm_url = f"https://www.openstreetmap.org/{osm_id.replace('_', '/')}" if osm_id else ""
    desc_str = " | ".join(desc_elements) if desc_elements else f"Verified {cat.lower()} mapped on OpenStreetMap in {destination_name}."

    return {
        "id": osm_id,
        "name": name,
        "category": cat,
        "provider": "OpenStreetMap (Overpass API)",
        "latitude": lat,
        "longitude": lng,
        "destination": destination_name,
        "address": address_str,
        "description": desc_str,
        "distance_from_destination_km": dist_km,
        "source_url": osm_url,
        "verified_fields": verified_fields,
        "confidence": "HIGH CONFIDENCE (OSM GEOGRAPHIC TRUTH)",
        "osm_tags": tags
    }
