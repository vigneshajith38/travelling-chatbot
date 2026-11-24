import os
import time
import urllib.parse
from typing import Dict, Any, List, Optional
from app.core.config import settings

OPENTRIPMAP_BASE_URL = "https://api.opentripmap.com/0.1/en/places"

# In-memory TTL cache for OpenTripMap calls to avoid repeated requests and respect rate limits
_OTM_CACHE: Dict[str, Dict[str, Any]] = {}
CACHE_TTL_SECONDS = 3600  # 1 hour

def get_opentripmap_api_key() -> str:
    """Retrieves OpenTripMap API key from settings or environment."""
    key = getattr(settings, "OPENTRIPMAP_API_KEY", "") or os.getenv("OPENTRIPMAP_API_KEY", "")
    return key.strip()

def is_opentripmap_available() -> bool:
    """Checks if a valid OpenTripMap API key is configured."""
    key = get_opentripmap_api_key()
    return bool(key and len(key) >= 10 and not key.startswith("your_"))

def _get_from_cache(cache_key: str) -> Optional[Any]:
    entry = _OTM_CACHE.get(cache_key)
    if entry and (time.time() - entry["timestamp"] < CACHE_TTL_SECONDS):
        return entry["data"]
    return None

def _set_in_cache(cache_key: str, data: Any):
    # Keep cache compact (max 500 items)
    if len(_OTM_CACHE) > 500:
        oldest = min(_OTM_CACHE.keys(), key=lambda k: _OTM_CACHE[k]["timestamp"])
        _OTM_CACHE.pop(oldest, None)
    _OTM_CACHE[cache_key] = {
        "timestamp": time.time(),
        "data": data
    }

def get_coordinates_by_name(destination_name: str) -> Optional[Dict[str, float]]:
    """
    Finds geographical coordinates using OpenTripMap geoname endpoint:
    GET /places/geoname?name={name}&apikey={key}
    """
    key = get_opentripmap_api_key()
    if not key:
        return None

    clean_name = destination_name.split(",")[0].strip()
    cache_key = f"geoname:{clean_name.lower()}"
    cached = _get_from_cache(cache_key)
    if cached is not None:
        return cached

    try:
        import httpx
        url = f"{OPENTRIPMAP_BASE_URL}/geoname"
        params = {"name": clean_name, "apikey": key}
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                if "lat" in data and "lon" in data:
                    coords = {"lat": float(data["lat"]), "lng": float(data["lon"])}
                    _set_in_cache(cache_key, coords)
                    return coords
    except Exception as e:
        print(f"OpenTripMap geoname exception for '{clean_name}': {e}")

    return None

def search_attractions_by_radius(
    lat: float,
    lng: float,
    radius_meters: int = 15000,
    kinds: str = "interesting_places",
    limit: int = 10,
    rate_filter: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Discovers tourist attractions within a radius using OpenTripMap:
    GET /places/radius?radius={radius}&lon={lon}&lat={lat}&kinds={kinds}&format=json&limit={limit}&apikey={key}
    """
    key = get_opentripmap_api_key()
    if not key:
        return []

    cache_key = f"radius:{round(lat, 4)}:{round(lng, 4)}:{radius_meters}:{kinds}:{limit}"
    cached = _get_from_cache(cache_key)
    if cached is not None:
        return cached

    try:
        import httpx
        url = f"{OPENTRIPMAP_BASE_URL}/radius"
        params = {
            "radius": max(500, min(50000, radius_meters)),
            "lon": lng,
            "lat": lat,
            "kinds": kinds,
            "format": "json",
            "limit": max(1, min(50, limit)),
            "apikey": key
        }
        if rate_filter:
            params["rate"] = rate_filter

        with httpx.Client(timeout=6.0) as client:
            resp = client.get(url, params=params)
            if resp.status_code == 200:
                raw_list = resp.json()
                if isinstance(raw_list, list):
                    # Filter out entries without meaningful names
                    cleaned = []
                    seen_names = set()
                    for item in raw_list:
                        name = (item.get("name") or "").strip()
                        if not name or len(name) < 3:
                            continue
                        normalized_name = name.lower()
                        if normalized_name in seen_names:
                            continue
                        seen_names.add(normalized_name)
                        cleaned.append(item)

                    _set_in_cache(cache_key, cleaned)
                    return cleaned
            else:
                print(f"OpenTripMap radius search status {resp.status_code}: {resp.text[:100]}")
    except Exception as e:
        print(f"OpenTripMap radius search exception: {e}")

    return []

def get_place_details(xid: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves full details for a specific place by its OpenTripMap XID:
    GET /places/xid/{xid}?apikey={key}
    """
    key = get_opentripmap_api_key()
    if not key or not xid:
        return None

    cache_key = f"xid:{xid}"
    cached = _get_from_cache(cache_key)
    if cached is not None:
        return cached

    try:
        import httpx
        url = f"{OPENTRIPMAP_BASE_URL}/xid/{xid}"
        params = {"apikey": key}
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                _set_in_cache(cache_key, data)
                return data
    except Exception as e:
        print(f"OpenTripMap place details exception for '{xid}': {e}")

    return None

def normalize_otm_place(
    otm_item: Dict[str, Any],
    destination_name: str,
    dest_lat: float,
    dest_lng: float
) -> Dict[str, Any]:
    """
    Normalizes an OpenTripMap place item into the Universal Place Data Structure (Step 9).
    """
    name = (otm_item.get("name") or "Unnamed Sight").strip()
    xid = otm_item.get("xid", "")
    point = otm_item.get("point", {})
    lat = point.get("lat")
    lng = point.get("lon")

    # Calculate actual distance
    dist_km = None
    if lat is not None and lng is not None:
        from app.services.routing_service import haversine_distance_km
        dist_km = round(haversine_distance_km(dest_lat, dest_lng, lat, lng), 2)
    elif "dist" in otm_item:
        dist_km = round(float(otm_item["dist"]) / 1000.0, 2)

    # Human-friendly category extraction
    kinds_str = otm_item.get("kinds", "")
    category = "Tourist Attraction"
    if "waterfall" in kinds_str:
        category = "Waterfall & Natural Cascade"
    elif "viewpoint" in kinds_str:
        category = "Scenic Viewpoint & Panoramic Lookout"
    elif "historic" in kinds_str:
        category = "Historical Monument & Heritage Site"
    elif "museum" in kinds_str:
        category = "Museum & Cultural Center"
    elif "religion" in kinds_str or "temple" in kinds_str:
        category = "Spiritual & Temple Sanctuary"
    elif "nature" in kinds_str or "natural" in kinds_str:
        category = "Nature Reserve & Landscape"

    verified_fields = ["name", "provider_id", "category"]
    if lat is not None and lng is not None:
        verified_fields.extend(["latitude", "longitude"])
    if dist_km is not None:
        verified_fields.append("distance_from_destination_km")

    # Extract description / wiki if available
    desc = ""
    wiki = otm_item.get("wikipedia_extracts", {})
    if wiki and "text" in wiki:
        desc = wiki["text"]
    elif "kinds" in otm_item:
        desc = f"Verified point of interest categorized under {category.lower()} in {destination_name}."

    otm_url = otm_item.get("otm") or (f"https://opentripmap.com/en/card/{xid}" if xid else "")

    return {
        "id": xid or f"otm_{abs(hash(name)) % 1000000}",
        "name": name,
        "category": category,
        "provider": "OpenTripMap",
        "latitude": lat,
        "longitude": lng,
        "destination": destination_name,
        "address": otm_item.get("address", {}).get("road", f"{destination_name}"),
        "description": desc,
        "distance_from_destination_km": dist_km,
        "source_url": otm_url,
        "verified_fields": verified_fields,
        "confidence": "HIGH CONFIDENCE (OPENTRIPMAP VERIFIED)" if xid else "MEDIUM CONFIDENCE",
        "raw_kinds": kinds_str
    }
