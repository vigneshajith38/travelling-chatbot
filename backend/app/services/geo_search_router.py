import re
from typing import Dict, Any, List, Optional, Tuple
from app.services.routing_service import haversine_distance_km
from app.services.destination_verifier import get_destination_identity, normalize_destination_key
from app.services.opentripmap_service import (
    is_opentripmap_available,
    search_attractions_by_radius,
    normalize_otm_place
)
from app.services.overpass_service import (
    query_osm_places_by_category,
    normalize_osm_place
)

# Universal Category Mapping (Step 8)
CATEGORY_MAPPINGS = {
    "cafe": {
        "osm_tags": ["amenity=cafe"],
        "otm_kinds": "foods",
        "label": "Cafes & Coffee Spots"
    },
    "restaurant": {
        "osm_tags": ["amenity=restaurant", "amenity=food_court"],
        "otm_kinds": "foods",
        "label": "Restaurants & Local Dining"
    },
    "waterfall": {
        "osm_tags": ["natural=waterfall"],
        "otm_kinds": "natural",
        "label": "Waterfalls & Cascades"
    },
    "viewpoint": {
        "osm_tags": ["tourism=viewpoint"],
        "otm_kinds": "interesting_places",
        "label": "Scenic Viewpoints"
    },
    "hotel": {
        "osm_tags": ["tourism=hotel", "tourism=resort", "tourism=guest_house"],
        "otm_kinds": "other_hotels",
        "label": "Hotels & Stays"
    },
    "park": {
        "osm_tags": ["leisure=park", "leisure=garden"],
        "otm_kinds": "natural",
        "label": "Parks & Gardens"
    },
    "museum": {
        "osm_tags": ["tourism=museum"],
        "otm_kinds": "cultural",
        "label": "Museums & Galleries"
    },
    "temple": {
        "osm_tags": ["amenity=place_of_worship", "historic"],
        "otm_kinds": "religion",
        "label": "Temples & Spiritual Sites"
    },
    "beach": {
        "osm_tags": ["natural=beach"],
        "otm_kinds": "natural",
        "label": "Beaches & Coastal Spots"
    },
    "attraction": {
        "osm_tags": ["tourism=attraction", "historic"],
        "otm_kinds": "interesting_places",
        "label": "Tourist Attractions & Sights"
    }
}

def detect_category_intent(user_message: str) -> Optional[str]:
    """Detects if user is asking for a specific category of place."""
    t = user_message.lower()
    if any(w in t for w in ["cafe", "cafes", "coffee", "roastery", "bakeries"]):
        return "cafe"
    if any(w in t for w in ["waterfall", "waterfalls", "cascade", "falls"]):
        return "waterfall"
    if any(w in t for w in ["restaurant", "restaurants", "dining", "food", "eat", "eateries"]):
        return "restaurant"
    if any(w in t for w in ["viewpoint", "viewpoints", "view point", "sunset point", "lookout", "sunrise"]):
        return "viewpoint"
    if any(w in t for w in ["hotel", "hotels", "resort", "resorts", "stay", "homestay"]):
        return "hotel"
    if any(w in t for w in ["park", "parks", "garden", "gardens", "botanical"]):
        return "park"
    if any(w in t for w in ["museum", "museums", "gallery", "art center"]):
        return "museum"
    if any(w in t for w in ["temple", "temples", "church", "mosque", "shrine", "ashram"]):
        return "temple"
    if any(w in t for w in ["beach", "beaches", "sea", "coast"]):
        return "beach"
    return "attraction"

def route_and_discover_places(
    destination: str,
    user_query: str = "",
    radius_km: float = 25.0,
    limit: int = 8
) -> Dict[str, Any]:
    """
    Intelligent Search Router (Step 5) & Result Validation (Step 6):
    1. Resolves destination identity and coordinates.
    2. Maps user query to categories.
    3. Queries appropriate providers (OpenTripMap, Overpass OSM).
    4. Geographically validates all distances, separates in-destination vs nearby excursions.
    5. Deduplicates and formats normalized output.
    """
    identity = get_destination_identity(destination)
    canonical = identity.get("canonical_name", destination)
    lat = identity.get("lat")
    lng = identity.get("lng")

    if lat is None or lng is None:
        return {
            "destination": canonical,
            "status": "Coordinates Unverified",
            "in_destination": [],
            "nearby_excursions": [],
            "total_found": 0
        }

    category_key = detect_category_intent(user_query) or "attraction"
    cat_cfg = CATEGORY_MAPPINGS.get(category_key, CATEGORY_MAPPINGS["attraction"])

    discovered_places = []
    seen_names = set()

    # Provider 1: Overpass OpenStreetMap (Excellent for cafes, restaurants, waterfalls, viewpoints)
    try:
        osm_results = query_osm_places_by_category(
            lat=lat,
            lng=lng,
            category_tags=cat_cfg["osm_tags"],
            radius_meters=int(radius_km * 1000),
            limit=limit
        )
        for item in osm_results:
            normalized = normalize_osm_place(item, canonical, lat, lng, inferred_category=cat_cfg["label"])
            name_key = normalized["name"].lower()
            if name_key not in seen_names:
                seen_names.add(name_key)
                discovered_places.append(normalized)
    except Exception as e:
        print(f"Overpass discovery note: {e}")

    # Provider 2: OpenTripMap (Excellent for tourist attractions, heritage, culture)
    if is_opentripmap_available() and len(discovered_places) < limit:
        try:
            otm_results = search_attractions_by_radius(
                lat=lat,
                lng=lng,
                radius_meters=int(radius_km * 1000),
                kinds=cat_cfg["otm_kinds"],
                limit=limit - len(discovered_places)
            )
            for item in otm_results:
                normalized = normalize_otm_place(item, canonical, lat, lng)
                name_key = normalized["name"].lower()
                if name_key not in seen_names:
                    seen_names.add(name_key)
                    discovered_places.append(normalized)
        except Exception as e:
            print(f"OpenTripMap discovery note: {e}")

    # Result Validation & Geographic Boundary Enforcement (Step 6)
    in_dest = []
    nearby = []
    max_boundary = identity.get("boundary_radius_km", radius_km)

    for p in discovered_places:
        dist = p.get("distance_from_destination_km")
        if dist is not None:
            # Drop places unreasonably far away (> 75km) as unrelated
            if dist > 75.0:
                continue
            if dist <= max_boundary:
                in_dest.append(p)
            else:
                p["category"] = f"{p['category']} (Nearby Day Trip)"
                nearby.append(p)
        else:
            in_dest.append(p)

    return {
        "destination": canonical,
        "category": cat_cfg["label"],
        "lat": lat,
        "lng": lng,
        "in_destination": in_dest[:limit],
        "nearby_excursions": nearby[:3],
        "total_found": len(in_dest) + len(nearby)
    }

def format_geo_evidence_for_gemini(geo_data: Dict[str, Any]) -> str:
    """Formats structured evidence for Gemini grounding (Step 7)."""
    dest = geo_data.get("destination", "Destination")
    in_dest = geo_data.get("in_destination", [])
    nearby = geo_data.get("nearby_excursions", [])

    lines = [f"[GEOGRAPHIC GROUND TRUTH & VERIFIED PLACES FOR {dest.upper()}:"]
    if in_dest:
        lines.append(f"• IN-DESTINATION VERIFIED {geo_data.get('category', 'PLACES').upper()}:")
        for p in in_dest:
            dist_str = f" ({p['distance_from_destination_km']} km from center)" if p.get('distance_from_destination_km') is not None else ""
            desc_str = f" - {p['description']}" if p.get('description') else ""
            lines.append(f"  - {p['name']}{dist_str} [{p.get('provider', 'OSM')}]: {p.get('category')}{desc_str}")
    
    if nearby:
        lines.append(f"• NEARBY DAY-TRIP EXCURSIONS (Clearly state distance > 25km away):")
        for p in nearby:
            lines.append(f"  - {p['name']} ({p.get('distance_from_destination_km', '?')} km away) [{p.get('provider', 'OSM')}]: {p.get('description', '')}")

    lines.append("STRICT ACCURACY PROTOCOL: Recommend ONLY verified places from above or well-documented real world places. Never invent non-existent cafes or waterfalls. Clearly separate in-city places from nearby day trips.]")
    return "\n".join(lines)
