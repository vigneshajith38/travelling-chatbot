import re
import urllib.parse
from typing import Dict, Any, List, Optional, Tuple

# Pre-calibrated verified global & Indian destination registry
# With accurate coordinates, canonical names, types, district, state, country, and official portal links
VERIFIED_DESTINATION_REGISTRY: Dict[str, Dict[str, Any]] = {
    # Kerala Hubs
    "trivandrum": {
        "canonical_name": "Thiruvananthapuram (Trivandrum)",
        "destination_type": "Metropolis & Capital City",
        "district": "Thiruvananthapuram",
        "state": "Kerala",
        "country": "India",
        "lat": 8.4882,
        "lng": 76.9476,
        "elevation_m": 10,
        "terrain": "Coastal plains and low laterite rolling hills along the Arabian Sea",
        "official_tourism_url": "https://www.keralatourism.org/destination/thiruvananthapuram/267",
        "boundary_radius_km": 25.0
    },
    "thiruvananthapuram": {
        "canonical_name": "Thiruvananthapuram (Trivandrum)",
        "destination_type": "Metropolis & Capital City",
        "district": "Thiruvananthapuram",
        "state": "Kerala",
        "country": "India",
        "lat": 8.4882,
        "lng": 76.9476,
        "elevation_m": 10,
        "terrain": "Coastal plains and low laterite rolling hills along the Arabian Sea",
        "official_tourism_url": "https://www.keralatourism.org/destination/thiruvananthapuram/267",
        "boundary_radius_km": 25.0
    },
    "vagamon": {
        "canonical_name": "Vagamon",
        "destination_type": "Hill Station & Mountain Village",
        "district": "Idukki & Kottayam Border (Peerumade Taluk)",
        "state": "Kerala",
        "country": "India",
        "lat": 9.6886,
        "lng": 76.9069,
        "elevation_m": 1100,
        "terrain": "Misty high-altitude tea plantations, pine valleys, and undulating grassy meadows (motta kundu)",
        "official_tourism_url": "https://www.keralatourism.org/destination/vagamon/102",
        "boundary_radius_km": 20.0
    },
    "munnar": {
        "canonical_name": "Munnar",
        "destination_type": "High-Altitude Hill Station",
        "district": "Idukki",
        "state": "Kerala",
        "country": "India",
        "lat": 10.0889,
        "lng": 77.0595,
        "elevation_m": 1600,
        "terrain": "Confluence of three mountain rivers (Mudhirapuzha, Nallathanni, Kundala) framed by sprawling tea estates",
        "official_tourism_url": "https://www.keralatourism.org/destination/munnar/202",
        "boundary_radius_km": 30.0
    },
    "kochi": {
        "canonical_name": "Kochi (Cochin)",
        "destination_type": "Historic Coastal Port & Metropolis",
        "district": "Ernakulam",
        "state": "Kerala",
        "country": "India",
        "lat": 9.9312,
        "lng": 76.2673,
        "elevation_m": 5,
        "terrain": "Arabian Sea islands, backwater channels, and colonial heritage quarters (Fort Kochi & Mattancherry)",
        "official_tourism_url": "https://www.keralatourism.org/destination/kochi/264",
        "boundary_radius_km": 25.0
    },
    "alleppey": {
        "canonical_name": "Alappuzha (Alleppey)",
        "destination_type": "Backwater Canal Network & Coastal Town",
        "district": "Alappuzha",
        "state": "Kerala",
        "country": "India",
        "lat": 9.4981,
        "lng": 76.3388,
        "elevation_m": 2,
        "terrain": "Venice of the East backwater canals, Vembanad Lake, and paddy fields below sea level (Kuttanad)",
        "official_tourism_url": "https://www.keralatourism.org/destination/alappuzha/263",
        "boundary_radius_km": 25.0
    },
    "varkala": {
        "canonical_name": "Varkala",
        "destination_type": "Coastal Cliff Beach & Spiritual Center",
        "district": "Thiruvananthapuram",
        "state": "Kerala",
        "country": "India",
        "lat": 8.7379,
        "lng": 76.7163,
        "elevation_m": 25,
        "terrain": "Dramatic red laterite sea cliffs overlooking Papanasam Beach with natural mineral springs",
        "official_tourism_url": "https://www.keralatourism.org/destination/varkala-beach/324",
        "boundary_radius_km": 15.0
    },
    "wayanad": {
        "canonical_name": "Wayanad (Kalpetta)",
        "destination_type": "Highland Mountain Plateau & Biosphere",
        "district": "Wayanad",
        "state": "Kerala",
        "country": "India",
        "lat": 11.6854,
        "lng": 76.1320,
        "elevation_m": 900,
        "terrain": "Western Ghats cloud forests, spice estates, waterfalls, and prehistoric caves (Edakkal)",
        "official_tourism_url": "https://www.keralatourism.org/destination/wayanad/270",
        "boundary_radius_km": 35.0
    },
    "thekkady": {
        "canonical_name": "Thekkady (Periyar)",
        "destination_type": "Wildlife Reserve & Spice Hills",
        "district": "Idukki",
        "state": "Kerala",
        "country": "India",
        "lat": 9.6031,
        "lng": 77.1615,
        "elevation_m": 900,
        "terrain": "Periyar Tiger Reserve lake basin bordered by cardamom, pepper, and cinnamon plantations",
        "official_tourism_url": "https://www.keralatourism.org/destination/periyar-tiger-reserve/308",
        "boundary_radius_km": 20.0
    },

    # Karnataka Hubs
    "bangalore": {
        "canonical_name": "Bengaluru (Bangalore)",
        "destination_type": "Major Tech Metropolis & Garden City",
        "district": "Bengaluru Urban",
        "state": "Karnataka",
        "country": "India",
        "lat": 12.9716,
        "lng": 77.5946,
        "elevation_m": 920,
        "terrain": "High Deccan Plateau with pleasant year-round climate, lakes, and expansive tree canopy",
        "official_tourism_url": "https://karnatakatourism.org/tour-item/bengaluru/",
        "boundary_radius_km": 30.0
    },
    "bengaluru": {
        "canonical_name": "Bengaluru (Bangalore)",
        "destination_type": "Major Tech Metropolis & Garden City",
        "district": "Bengaluru Urban",
        "state": "Karnataka",
        "country": "India",
        "lat": 12.9716,
        "lng": 77.5946,
        "elevation_m": 920,
        "terrain": "High Deccan Plateau with pleasant year-round climate, lakes, and expansive tree canopy",
        "official_tourism_url": "https://karnatakatourism.org/tour-item/bengaluru/",
        "boundary_radius_km": 30.0
    },
    "mysore": {
        "canonical_name": "Mysuru (Mysore)",
        "destination_type": "Royal Heritage Capital",
        "district": "Mysuru",
        "state": "Karnataka",
        "country": "India",
        "lat": 12.2958,
        "lng": 76.6394,
        "elevation_m": 770,
        "terrain": "Chamundi Hill foothills on southern Deccan Plateau with tree-lined royal boulevards",
        "official_tourism_url": "https://karnatakatourism.org/tour-item/mysuru/",
        "boundary_radius_km": 20.0
    },
    "mysuru": {
        "canonical_name": "Mysuru (Mysore)",
        "destination_type": "Royal Heritage Capital",
        "district": "Mysuru",
        "state": "Karnataka",
        "country": "India",
        "lat": 12.2958,
        "lng": 76.6394,
        "elevation_m": 770,
        "terrain": "Chamundi Hill foothills on southern Deccan Plateau with tree-lined royal boulevards",
        "official_tourism_url": "https://karnatakatourism.org/tour-item/mysuru/",
        "boundary_radius_km": 20.0
    },
    "udupi": {
        "canonical_name": "Udupi",
        "destination_type": "Coastal Temple & Heritage Town",
        "district": "Udupi",
        "state": "Karnataka",
        "country": "India",
        "lat": 13.3409,
        "lng": 74.7421,
        "elevation_m": 25,
        "terrain": "Coastal plains between Western Ghats and Arabian Sea with pristine beaches and basalt island rocks",
        "official_tourism_url": "https://karnatakatourism.org/tour-item/udupi/",
        "boundary_radius_km": 25.0
    },
    "gokarna": {
        "canonical_name": "Gokarna",
        "destination_type": "Spiritual Temple Town & Coastal Beach Haven",
        "district": "Uttara Kannada",
        "state": "Karnataka",
        "country": "India",
        "lat": 14.5479,
        "lng": 74.3188,
        "elevation_m": 15,
        "terrain": "Rugged coastal cliffs enclosing secluded crescent-shaped beaches (Om, Kudle, Half Moon, Paradise)",
        "official_tourism_url": "https://karnatakatourism.org/tour-item/gokarna/",
        "boundary_radius_km": 20.0
    },
    "coorg": {
        "canonical_name": "Coorg (Kodagu / Madikeri)",
        "destination_type": "Highland Coffee Estate Hills",
        "district": "Kodagu",
        "state": "Karnataka",
        "country": "India",
        "lat": 12.4244,
        "lng": 75.7382,
        "elevation_m": 1150,
        "terrain": "Western Ghats misty valleys covered with shaded coffee plantations and orange orchards",
        "official_tourism_url": "https://karnatakatourism.org/tour-item/madikeri/",
        "boundary_radius_km": 30.0
    },
    "hampi": {
        "canonical_name": "Hampi",
        "destination_type": "UNESCO World Heritage Bolder Ruins",
        "district": "Vijayanagara",
        "state": "Karnataka",
        "country": "India",
        "lat": 15.3350,
        "lng": 76.4600,
        "elevation_m": 467,
        "terrain": "Dramatic granite boulder landscapes flanking the sacred Tungabhadra River with 14th-century Vijayanagara empire ruins",
        "official_tourism_url": "https://karnatakatourism.org/tour-item/hampi/",
        "boundary_radius_km": 20.0
    },

    # Other Key Indian Destinations
    "goa": {
        "canonical_name": "Goa",
        "destination_type": "Coastal Beach & Portuguese Heritage State",
        "district": "North & South Goa",
        "state": "Goa",
        "country": "India",
        "lat": 15.2993,
        "lng": 74.1240,
        "elevation_m": 10,
        "terrain": "105 km Arabian Sea coastline with golden sand beaches, estuary rivers, and inland Western Ghats forests",
        "official_tourism_url": "https://goa-tourism.com/",
        "boundary_radius_km": 40.0
    },
    "manali": {
        "canonical_name": "Manali",
        "destination_type": "Himalayan Mountain Resort",
        "district": "Kullu",
        "state": "Himachal Pradesh",
        "country": "India",
        "lat": 32.2432,
        "lng": 77.1892,
        "elevation_m": 2050,
        "terrain": "Beas River valley flanked by snow-capped Pir Panjal peaks, cedar forests, and apple orchards",
        "official_tourism_url": "https://himachaltourism.gov.in/destination/manali/",
        "boundary_radius_km": 25.0
    },
    "ooty": {
        "canonical_name": "Udhagamandalam (Ooty)",
        "destination_type": "Nilgiri Blue Mountain Hill Station",
        "district": "Nilgiris",
        "state": "Tamil Nadu",
        "country": "India",
        "lat": 11.4102,
        "lng": 76.6950,
        "elevation_m": 2240,
        "terrain": "Rolling Nilgiri downs, eucalyptus forests, botanical gardens, and heritage mountain toy railway",
        "official_tourism_url": "https://www.tamilnadutourism.tn.gov.in/destinations/ooty",
        "boundary_radius_km": 25.0
    },

    # Global Hubs
    "paris": {
        "canonical_name": "Paris",
        "destination_type": "Global Capital & Cultural Metropolis",
        "district": "Île-de-France",
        "state": "Île-de-France",
        "country": "France",
        "lat": 48.8566,
        "lng": 2.3522,
        "elevation_m": 35,
        "terrain": "Seine River basin surrounded by historic limestone architecture and royal parks",
        "official_tourism_url": "https://en.parisinfo.com/",
        "boundary_radius_km": 20.0
    },
    "tokyo": {
        "canonical_name": "Tokyo",
        "destination_type": "Mega Metropolis & Global Tech/Culture Capital",
        "district": "Kanto",
        "state": "Tokyo Prefecture",
        "country": "Japan",
        "lat": 35.6762,
        "lng": 139.6503,
        "elevation_m": 40,
        "terrain": "Vast Kanto plain fronting Tokyo Bay with distant vistas of Mount Fuji",
        "official_tourism_url": "https://www.gotokyo.org/en/",
        "boundary_radius_km": 30.0
    }
}

# Geocoding cache for dynamically retrieved destinations
_DYNAMIC_GEOCODE_CACHE: Dict[str, Dict[str, Any]] = {}

def normalize_destination_key(name: str) -> str:
    """Strips parentheses, punctuation, state/country suffix, and lowercases for exact matching."""
    if not name:
        return ""
    clean = re.sub(r'\(.*?\)', '', name).split(",")[0].strip().lower()
    # Replace common aliases
    alias_map = {
        "thiruvananthapuram": "trivandrum",
        "bengaluru": "bangalore",
        "mysuru": "mysore",
        "cochin": "kochi",
        "alappuzha": "alleppey",
        "madikeri": "coorg",
        "kodagu": "coorg",
        "udhagamandalam": "ooty"
    }
    return alias_map.get(clean, clean)

def parse_destination_query(user_message: str) -> Dict[str, Any]:
    """
    Parses a user query using high-precision word-boundary regex scanning to identify:
    1. Single destination vs. multiple destinations (e.g. 'Trivandrum, Vagamon and Munnar').
    2. Comparison queries (e.g. 'Vagamon vs Munnar').
    3. Preserves distinct identities without cross-contaminating.
    """
    text = user_message.strip()
    text_lower = text.lower()

    # Check for comparison intent
    is_comparison = any(w in text_lower for w in [" vs ", " versus ", " compared to ", " or ", " difference between "])

    # 1. First Pass: Scan for all registered destinations in order of appearance in the sentence
    registry_keys = sorted(VERIFIED_DESTINATION_REGISTRY.keys(), key=lambda k: len(k), reverse=True)
    matches = []
    
    for k in registry_keys:
        # Don't match standalone "india" if a specific Indian city is also mentioned
        if k == "india" and any(re.search(rf'\b{re.escape(other_k)}\b', text_lower) for other_k in registry_keys if other_k != "india"):
            continue
        for m in re.finditer(rf'\b{re.escape(k)}\b', text_lower):
            matches.append((m.start(), k, VERIFIED_DESTINATION_REGISTRY[k]))

    # Sort matches by position in user's prompt
    matches.sort(key=lambda x: x[0])
    
    recognized_destinations = []
    seen_canonicals = set()
    for pos, k, data in matches:
        canon = data["canonical_name"]
        if canon not in seen_canonicals:
            seen_canonicals.add(canon)
            rec = data.copy()
            rec["key"] = k
            recognized_destinations.append(rec)

    # 2. Second Pass: If no registered destination found, try natural language patterns
    if not recognized_destinations:
        dest_patterns = [
            r'\b(?:plan\s+(?:a\s+)?(?:\d+[- ]?day\s+)?trip\s+to|trip\s+to|travel\s+to|visit|explore|vacation\s+in|holiday\s+in|guide\s+(?:to|for)|itinerary\s+for|about)\s+([A-Za-z\s,]{3,32}?)(?:\s+(?:for|with|under|in|from|at|on|\d+days?)|$|[?!.])',
            r'\b(?:hotels?|resorts?|stay|accommodation)\s+(?:in|at|near)\s+([A-Za-z\s,]{3,30}?)(?:\s+(?:for|with|under|in|from|at|on|\d+)|$|[?!.])',
            r'\b(?:tell me about|overview of|info about|information on)\s+([A-Za-z\s,]{3,30}?)(?:\s+(?:like|for)|$|[?!.])'
        ]
        non_dest_words = {
            "a trip", "an itinerary", "peaceful", "budget", "friends", "couple", "family", "days", "food",
            "weather", "safety", "cheap", "expensive", "hotel", "flight", "there", "that place", "it"
        }
        for pat in dest_patterns:
            m = re.search(pat, text_lower)
            if m:
                cand = m.group(1).strip().title()
                if cand.lower() not in non_dest_words and len(cand) >= 3:
                    cand_info = get_destination_identity(cand)
                    if cand_info and cand_info.get("canonical_name"):
                        rec = cand_info.copy()
                        rec["key"] = normalize_destination_key(cand)
                        recognized_destinations.append(rec)
                        break

    # Determine query classification
    if len(recognized_destinations) >= 2:
        query_type = "comparison" if is_comparison else "multi_destination_circuit"
    elif len(recognized_destinations) == 1:
        query_type = "single_destination"
    else:
        query_type = "general_travel"

    return {
        "query_type": query_type,
        "is_comparison": is_comparison,
        "destinations": recognized_destinations,
        "destination_count": len(recognized_destinations),
        "primary_destination": recognized_destinations[0]["canonical_name"] if recognized_destinations else None
    }

    # Determine query classification
    if len(recognized_destinations) >= 2:
        query_type = "comparison" if is_comparison else "multi_destination_circuit"
    elif len(recognized_destinations) == 1:
        query_type = "single_destination"
    else:
        query_type = "general_travel"

    return {
        "query_type": query_type,
        "is_comparison": is_comparison,
        "destinations": recognized_destinations,
        "destination_count": len(recognized_destinations),
        "primary_destination": recognized_destinations[0]["canonical_name"] if recognized_destinations else None
    }

def get_destination_identity(dest_name: str) -> Dict[str, Any]:
    """
    Resolves full geographical identity (type, district, state, country, coordinates).
    Uses curated database first, then cached Nominatim, and avoids ever defaulting to New Delhi for unrelated places.
    """
    if not dest_name:
        return {}

    key = normalize_destination_key(dest_name)
    if key in VERIFIED_DESTINATION_REGISTRY:
        data = VERIFIED_DESTINATION_REGISTRY[key].copy()
        data["key"] = key
        return data

    # Check dynamic cache
    if key in _DYNAMIC_GEOCODE_CACHE:
        return _DYNAMIC_GEOCODE_CACHE[key].copy()

    # Query OpenStreetMap Nominatim with proper headers
    try:
        import httpx
        with httpx.Client(timeout=4.0) as client:
            resp = client.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": dest_name, "format": "json", "addressdetails": 1, "limit": 1},
                headers={"User-Agent": "WanderWise-AI-Travel/2.0 (travel@wanderwise.com)"}
            )
            if resp.status_code == 200:
                results = resp.json()
                if results and len(results) > 0:
                    r0 = results[0]
                    lat = float(r0["lat"])
                    lng = float(r0["lon"])
                    addr = r0.get("address", {})
                    
                    city = addr.get("city") or addr.get("town") or addr.get("village") or addr.get("county") or dest_name.title()
                    district = addr.get("state_district") or addr.get("county") or ""
                    state = addr.get("state") or ""
                    country = addr.get("country") or "India"
                    place_type = r0.get("type", "town").replace("_", " ").title()

                    resolved = {
                        "canonical_name": f"{city}, {state}" if state else city,
                        "destination_type": f"{place_type} & Regional Destination",
                        "district": district,
                        "state": state,
                        "country": country,
                        "lat": lat,
                        "lng": lng,
                        "elevation_m": None,
                        "terrain": f"Regional landscape in {district or state}, {country}",
                        "official_tourism_url": f"https://www.google.com/search?q={urllib.parse.quote(city + ' tourism official website')}",
                        "boundary_radius_km": 25.0,
                        "key": key
                    }
                    _DYNAMIC_GEOCODE_CACHE[key] = resolved
                    return resolved
    except Exception as e:
        print(f"Nominatim lookup exception for '{dest_name}': {e}")

    # Fallback without giving fake New Delhi coordinates if name indicates south/coastal/mountain
    return {
        "canonical_name": dest_name.title(),
        "destination_type": "Travel Destination",
        "district": "",
        "state": "",
        "country": "India",
        "lat": 12.9716, # default to Bangalore regional centroid rather than Delhi if ambiguous
        "lng": 77.5946,
        "elevation_m": None,
        "terrain": "Local regional topography",
        "official_tourism_url": f"https://www.google.com/search?q={urllib.parse.quote(dest_name + ' tourism')}",
        "boundary_radius_km": 25.0,
        "key": key
    }
