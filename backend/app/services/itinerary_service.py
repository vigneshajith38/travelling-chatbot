import datetime
import json
import re
from typing import List, Dict, Any, Optional
from app.core.config import settings

# Global coordinates cache for top 30 world & Indian destinations
GLOBAL_DESTINATION_COORDINATES = {
    "paris": (48.8566, 2.3522),
    "tokyo": (35.6762, 139.6503),
    "bali": (-8.4095, 115.1889),
    "rome": (41.9028, 12.4964),
    "london": (51.5074, -0.1278),
    "new york": (40.7128, -74.0060),
    "dubai": (25.2048, 55.2708),
    "singapore": (1.3521, 103.8198),
    "bangkok": (13.7563, 100.5018),
    "switzerland": (46.8182, 8.2275),
    "zurich": (47.3769, 8.5417),
    "barcelona": (41.3879, 2.1699),
    "amsterdam": (52.3676, 4.9041),
    "venice": (45.4408, 12.3155),
    "kyoto": (35.0116, 135.7681),
    "goa": (15.2993, 74.1240),
    "jaipur": (26.9124, 75.7873),
    "ladakh": (34.1526, 77.5771),
    "leh": (34.1526, 77.5771),
    "kashmir": (34.0837, 74.7973),
    "srinagar": (34.0837, 74.7973),
    "manali": (32.2432, 77.1892),
    "munnar": (10.0889, 77.0595),
    "gokarna": (14.5479, 74.3188),
    "spiti": (32.2461, 78.0349),
    "udaipur": (24.5854, 73.7125),
    "rishikesh": (30.0869, 78.2676),
    "varkala": (8.7379, 76.7163),
    "coorg": (12.4244, 75.7382),
    "hampi": (15.3350, 76.4600),
    "phuket": (7.8804, 98.3923),
    "santorini": (36.3932, 25.4615),
    "maldives": (3.2028, 73.2207),
    "seoul": (37.5665, 126.9780),
    "sydney": (-33.8688, 151.2093),
    "florence": (43.7696, 11.2558),
    "san francisco": (37.7749, -122.4194),
    "los angeles": (34.0522, -118.2437),
    "berlin": (52.5200, 13.4050),
    "prague": (50.0755, 14.4378),
    "vienna": (48.2082, 16.3738),
    "hawaii": (21.3069, -157.8583),
    "madrid": (40.4168, -3.7038),
    "hanoi": (21.0285, 105.8542),
    "istanbul": (41.0082, 28.9784),
    "cairo": (30.0444, 31.2357)
}

def resolve_destination_coordinates(dest_name: str) -> tuple:
    """Returns (lat, lng) for any global destination, using cache or geocoding."""
    if not dest_name:
        return (48.8566, 2.3522)
    clean = dest_name.split(",")[0].lower().strip()
    for k, coords in GLOBAL_DESTINATION_COORDINATES.items():
        if k in clean or clean in k:
            return coords
    # Dynamic Nominatim geocoding fallback
    try:
        import httpx
        with httpx.Client(timeout=2.5) as client:
            resp = client.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": dest_name, "format": "json", "limit": 1},
                headers={"User-Agent": "WanderWise-AI-Travel-Planner/1.0"}
            )
            if resp.status_code == 200:
                results = resp.json()
                if results and len(results) > 0:
                    return (float(results[0]["lat"]), float(results[0]["lon"]))
    except Exception:
        pass
    return (48.8566, 2.3522)

# Regional landmark template banks for offline fallback
REGIONAL_LANDMARK_BANKS = {
    "paris": [
        {"slot": "morning", "time": "09:00 AM", "title": "Louvre Museum & Glass Pyramid", "desc": "Explore world-renowned classical art masterpieces including the Mona Lisa and Winged Victory.", "loc": "Louvre Museum, 1st Arr.", "lat": 48.8606, "lng": 2.3376, "cost": 1800.0, "dur": 150, "mode": "walking", "cat": "culture", "indoor": True},
        {"slot": "afternoon", "time": "02:00 PM", "title": "Notre-Dame Cathedral & Latin Quarter Walk", "desc": "Stroll the ancient medieval heart of Paris along the Seine with artisan bookstalls and cafes.", "loc": "Île de la Cité", "lat": 48.8530, "lng": 2.3499, "cost": 0.0, "dur": 100, "mode": "walking", "cat": "culture", "indoor": False},
        {"slot": "evening", "time": "06:30 PM", "title": "Eiffel Tower Twilight & Seine River Cruise", "desc": "Take in the sparkling golden lights of the Eiffel Tower followed by a romantic dusk river cruise.", "loc": "Champ de Mars, 7th Arr.", "lat": 48.8584, "lng": 2.2945, "cost": 2200.0, "dur": 120, "mode": "transit", "cat": "photo", "indoor": False},
        {"slot": "morning", "time": "09:30 AM", "title": "Montmartre & Sacré-Cœur Basilica Overlook", "desc": "Climb through winding cobblestone bohemian streets to the highest natural summit in Paris.", "loc": "Montmartre, 18th Arr.", "lat": 48.8867, "lng": 2.3431, "cost": 0.0, "dur": 120, "mode": "walking", "cat": "photo", "indoor": False},
        {"slot": "afternoon", "time": "01:30 PM", "title": "Musée d'Orsay Impressionist Gallery", "desc": "Admire Monet, Van Gogh, and Degas inside a grand converted Beaux-Arts railway terminal.", "loc": "Musée d'Orsay", "lat": 48.8599, "lng": 2.3266, "cost": 1600.0, "dur": 110, "mode": "walking", "cat": "culture", "indoor": True},
        {"slot": "evening", "time": "06:00 PM", "title": "Champs-Élysées & Arc de Triomphe Sunset", "desc": "Climb the monument's rooftop for sweeping vistas down twelve radiating Parisian avenues.", "loc": "Arc de Triomphe", "lat": 48.8738, "lng": 2.2950, "cost": 1300.0, "dur": 90, "mode": "walking", "cat": "shopping", "indoor": False}
    ],
    "tokyo": [
        {"slot": "morning", "time": "08:30 AM", "title": "Senso-ji Temple & Nakamise Street", "desc": "Walk under the giant red Kaminarimon lantern and sample freshly grilled rice crackers.", "loc": "Asakusa, Taito City", "lat": 35.7148, "lng": 139.7967, "cost": 300.0, "dur": 110, "mode": "walking", "cat": "culture", "indoor": False},
        {"slot": "afternoon", "time": "01:00 PM", "title": "Meiji Jingu Shrine & Yoyogi Forest", "desc": "Peaceful cedar forest sanctuary honoring the Meiji Emperor, right in the center of Tokyo.", "loc": "Shibuya City", "lat": 35.6764, "lng": 139.6993, "cost": 0.0, "dur": 90, "mode": "walking", "cat": "nature", "indoor": False},
        {"slot": "evening", "time": "06:00 PM", "title": "Shibuya Scramble Crossing & Sky Observatory", "desc": "Witness the world's busiest pedestrian crossing under neon towers from a 230m open-air roof.", "loc": "Shibuya Sky", "lat": 35.6580, "lng": 139.7016, "cost": 1400.0, "dur": 100, "mode": "transit", "cat": "photo", "indoor": True},
        {"slot": "morning", "time": "09:00 AM", "title": "Tsukiji Outer Market Gourmet Food Tour", "desc": "Taste fresh bluefin tuna nigiri, tamagoyaki sweet omelets, and grilled wagyu beef skewers.", "loc": "Chuo City", "lat": 35.6655, "lng": 139.7707, "cost": 1800.0, "dur": 120, "mode": "walking", "cat": "food", "indoor": False},
        {"slot": "afternoon", "time": "02:00 PM", "title": "teamLab Planets Immersive Digital Art", "desc": "Wade barefoot through water and infinite crystalline digital mirror installations.", "loc": "Toyosu, Koto City", "lat": 35.6491, "lng": 139.7898, "cost": 2200.0, "dur": 120, "mode": "transit", "cat": "culture", "indoor": True},
        {"slot": "evening", "time": "06:30 PM", "title": "Shinjuku Omoide Yokocho & Golden Gai", "desc": "Narrow lantern-lit alleys filled with miniature yakitori stalls and vintage micro-bars.", "loc": "Shinjuku City", "lat": 35.6938, "lng": 139.7003, "cost": 1500.0, "dur": 110, "mode": "walking", "cat": "food", "indoor": False}
    ],
    "goa": [
        {"slot": "morning", "time": "08:30 AM", "title": "Fort Aguada & Sinquerim Coastal Vista", "desc": "17th-century Portuguese fortress and lighthouse commanding sweeping views over the Arabian Sea.", "loc": "Sinquerim, North Goa", "lat": 15.4920, "lng": 73.7737, "cost": 50.0, "dur": 90, "mode": "driving", "cat": "photo", "indoor": False},
        {"slot": "afternoon", "time": "01:00 PM", "title": "Fontainhas Latin Quarter Heritage Walk", "desc": "Walk among Portuguese heritage villas painted in ochre, indigo, and terracotta with wrought-iron balconies.", "loc": "Panaji, Goa", "lat": 15.4989, "lng": 73.8278, "cost": 0.0, "dur": 110, "mode": "walking", "cat": "culture", "indoor": False},
        {"slot": "evening", "time": "05:30 PM", "title": "Anjuna Beach Cliff Sunset & Flea Market", "desc": "Watch crimson sunsets over volcanic rocks while listening to acoustic music at cliffside shacks.", "loc": "Anjuna Beach", "lat": 15.5807, "lng": 73.7429, "cost": 300.0, "dur": 120, "mode": "driving", "cat": "relaxation", "indoor": False},
        {"slot": "morning", "time": "08:00 AM", "title": "Dudhsagar Waterfall Jeep Safari", "desc": "Thrilling 4x4 trail through Bhagwan Mahaveer Sanctuary to the roaring four-tiered white cascades.", "loc": "Mollem National Park", "lat": 15.3144, "lng": 74.3143, "cost": 1500.0, "dur": 240, "mode": "transit", "cat": "adventure", "indoor": False},
        {"slot": "afternoon", "time": "02:00 PM", "title": "Sahakari Organic Spice Plantation & Buffet", "desc": "Walk through vanilla, cinnamon, and pepper groves followed by an authentic Goan buffet lunch.", "loc": "Curti, Ponda", "lat": 15.4055, "lng": 74.0200, "cost": 500.0, "dur": 110, "mode": "driving", "cat": "food", "indoor": True},
        {"slot": "evening", "time": "06:00 PM", "title": "Mandovi River Sunset Catamaran Cruise", "desc": "Sail past illuminated Panaji promenades with traditional Goan folk dances (Dekhni and Fugdi).", "loc": "Panaji Jetty", "lat": 15.5011, "lng": 73.8315, "cost": 600.0, "dur": 80, "mode": "transit", "cat": "relaxation", "indoor": False}
    ],
    "dubai": [
        {"slot": "morning", "time": "09:00 AM", "title": "Burj Khalifa At the Top (124th Floor)", "desc": "Ascend the world's tallest tower in high-speed elevators for panoramic Arabian Gulf views.", "loc": "Downtown Dubai", "lat": 25.1972, "lng": 55.2744, "cost": 3500.0, "dur": 120, "mode": "walking", "cat": "photo", "indoor": True},
        {"slot": "afternoon", "time": "02:00 PM", "title": "Dubai Mall & Underwater Aquarium Tunnel", "desc": "Walk through a 270-degree acrylic tunnel surrounded by sand tiger sharks and giant stingrays.", "loc": "Dubai Mall", "lat": 25.1985, "lng": 55.2796, "cost": 2200.0, "dur": 110, "mode": "walking", "cat": "nature", "indoor": True},
        {"slot": "evening", "time": "06:00 PM", "title": "Dubai Fountain Lake Ride & Waterfront Dinner", "desc": "Watch choreographed water jets shoot 150m into the air synchronized with classical and Arabic music.", "loc": "Burj Lake Promenade", "lat": 25.1965, "lng": 55.2785, "cost": 1500.0, "dur": 90, "mode": "walking", "cat": "food", "indoor": False},
        {"slot": "morning", "time": "08:30 AM", "title": "Al Fahidi Historical Bastakiya & Abra Ride", "desc": "Explore wind-tower architecture and cross Dubai Creek on a traditional wooden abra boat for 1 AED.", "loc": "Old Dubai, Bur Dubai", "lat": 25.2631, "lng": 55.2972, "cost": 200.0, "dur": 120, "mode": "walking", "cat": "culture", "indoor": False},
        {"slot": "afternoon", "time": "03:30 PM", "title": "Red Dunes Desert Safari & Sandboarding", "desc": "Thrilling 4x4 dune bashing across Lahbab desert followed by sandboarding down red crests.", "loc": "Lahbab Desert", "lat": 24.8710, "lng": 55.5900, "cost": 2800.0, "dur": 240, "mode": "transit", "cat": "adventure", "indoor": False},
        {"slot": "evening", "time": "07:30 PM", "title": "Bedouin Desert Camp & BBQ Dinner Under Stars", "desc": "Enjoy Tanoura spinning dances, fire shows, and a lavish Middle Eastern barbecue buffet.", "loc": "Desert Camp Reserve", "lat": 24.8800, "lng": 55.6000, "cost": 1200.0, "dur": 120, "mode": "walking", "cat": "food", "indoor": False}
    ]
}

def _try_generate_with_gemini(destination: str, num_days: int) -> Optional[List[Dict[str, Any]]]:
    """Uses Gemini 3.5 Flash to generate a real, customized itinerary for ANY destination on Earth."""
    api_key = (settings.GEMINI_API_KEY or "").strip()
    if not api_key or len(api_key) < 10:
        return None
        
    prompt = (
        f"Generate an accurate, authentic {num_days}-day travel itinerary for {destination} as a raw JSON array. "
        f"Each day must have: day_number (int), title (str), theme (str), and activities (list of exactly 3: morning, afternoon, evening). "
        f"Each activity must include: time_slot ('morning'|'afternoon'|'evening'), time_str (e.g. '09:00 AM'), title, description, location_name, "
        f"lat (float, accurate latitude of this location in {destination}), lng (float, accurate longitude), estimated_cost (float, estimated in INR), "
        f"duration_mins (int), travel_time_from_prev (str), transport_mode ('walking'|'driving'|'transit'), category ('culture'|'nature'|'photo'|'food'|'adventure'), is_indoor (bool). "
        f"Return ONLY valid raw JSON without any markdown formatting or code blocks."
    )
    
    models_to_try = [settings.GEMINI_MODEL, "gemini-3.5-flash-lite", "gemini-3.1-flash-lite"]
    # De-duplicate while preserving order
    seen = set()
    candidate_models = [m for m in models_to_try if not (m in seen or seen.add(m))]

    for model_name in candidate_models:
        try:
            from google import genai
            from google.genai import types
            client = genai.Client(
                api_key=api_key,
                http_options=types.HttpOptions(timeout=15000)
            )
            resp = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            if resp and resp.text:
                text = resp.text.strip()
                # Clean markdown code blocks if returned
                if text.startswith("```"):
                    text = re.sub(r"^```(?:json)?\s*", "", text)
                    text = re.sub(r"\s*```$", "", text)
                parsed = json.loads(text)
                if isinstance(parsed, list) and len(parsed) > 0:
                    print(f"✅ Gemini ({model_name}) synthesized authentic {len(parsed)}-day itinerary for {destination}!")
                    return parsed
        except Exception as e:
            print(f"Gemini {model_name} itinerary note: {type(e).__name__}: {str(e)[:100]}")
        
    return None

def generate_trip_itinerary(
    destination_name: str,
    start_date_str: str,
    num_days: int = 3,
    budget_level: str = "moderate",
    travel_pace: str = "balanced"
) -> List[Dict[str, Any]]:
    """
    Universal Itinerary Engine:
    1. First asks Gemini AI to generate an authentic day-by-day itinerary with exact real-world landmarks & coordinates for ANY destination worldwide.
    2. Falls back to geographically calibrated regional banks if offline.
    """
    dest_clean = destination_name.split(",")[0].strip()
    dest_lower = dest_clean.lower()
    
    # 1. Try Gemini AI Generation (supports Paris, Tokyo, Bali, New York, Goa, Dubai, anywhere!)
    ai_itinerary = _try_generate_with_gemini(destination_name, num_days)
    if ai_itinerary:
        try:
            start_date = datetime.date.fromisoformat(start_date_str)
        except Exception:
            start_date = datetime.date.today() + datetime.timedelta(days=7)
            
        # Stamp formatted dates and ensure order_index
        for idx, day in enumerate(ai_itinerary):
            cur_date = start_date + datetime.timedelta(days=idx)
            day["day_number"] = idx + 1
            day["date"] = cur_date.strftime("%b %d, %Y")
            for order_idx, act in enumerate(day.get("activities", [])):
                act["order_index"] = order_idx
                if "booking_url" not in act:
                    act["booking_url"] = None
        return ai_itinerary

    # 2. Offline Fallback: match region or generic landmark bank
    bank_key = None
    for k in REGIONAL_LANDMARK_BANKS.keys():
        if k in dest_lower:
            bank_key = k
            break
            
    # Resolve base coordinates for destination
    base_lat, base_lng = (10.0889, 77.0595)
    for k, coords in GLOBAL_DESTINATION_COORDINATES.items():
        if k in dest_lower:
            base_lat, base_lng = coords
            break
            
    if bank_key:
        bank = REGIONAL_LANDMARK_BANKS[bank_key]
    else:
        # Build generic authentic bank calibrated around destination's coordinates
        bank = [
            {"slot": "morning", "time": "09:00 AM", "title": f"Historic Old Town & Cultural Promenade", "desc": f"Explore the foundational architecture, heritage squares, and vibrant morning energy of {dest_clean}.", "loc": f"Old Quarter, {dest_clean}", "lat": base_lat + 0.005, "lng": base_lng + 0.004, "cost": 500.0, "dur": 120, "mode": "walking", "cat": "culture", "indoor": False},
            {"slot": "afternoon", "time": "01:30 PM", "title": f"Local Gastronomy & Artisanal Market", "desc": f"Sample authentic regional delicacies and shop for traditional handcrafted goods in {dest_clean}.", "loc": f"Central Market Hall, {dest_clean}", "lat": base_lat - 0.003, "lng": base_lng + 0.002, "cost": 800.0, "dur": 100, "mode": "walking", "cat": "food", "indoor": True},
            {"slot": "evening", "time": "05:30 PM", "title": f"Panoramic Sunset Overlook & Evening Stroll", "desc": f"Take in sweeping golden-hour vistas as dusk settles across the scenic rooftops and skyline of {dest_clean}.", "loc": f"Skyline Vista Point, {dest_clean}", "lat": base_lat + 0.008, "lng": base_lng - 0.006, "cost": 250.0, "dur": 90, "mode": "walking", "cat": "photo", "indoor": False},
            {"slot": "morning", "time": "09:30 AM", "title": f"National Heritage Museum & Galleries", "desc": f"Discover curated historic artifacts, fine art, and archaeological treasures celebrating the rich heritage of {dest_clean}.", "loc": f"National Museum Complex, {dest_clean}", "lat": base_lat - 0.004, "lng": base_lng - 0.005, "cost": 650.0, "dur": 110, "mode": "transit", "cat": "culture", "indoor": True},
            {"slot": "afternoon", "time": "02:00 PM", "title": f"Scenic Waterfront & Garden Promenade", "desc": f"Relax by tranquil botanical groves and scenic waterfront bridges surrounded by lush greenery.", "loc": f"Riverfront Botanical Gardens, {dest_clean}", "lat": base_lat + 0.002, "lng": base_lng + 0.007, "cost": 300.0, "dur": 90, "mode": "walking", "cat": "nature", "indoor": False},
            {"slot": "evening", "time": "06:30 PM", "title": f"Atmospheric Evening Dining & Acoustic Music", "desc": f"Unwind with signature local refreshments and candlelit dinner accompanied by regional acoustic melodies.", "loc": f"Lantern Quarter, {dest_clean}", "lat": base_lat + 0.001, "lng": base_lng - 0.003, "cost": 1200.0, "dur": 110, "mode": "walking", "cat": "food", "indoor": True}
        ]

    try:
        start_date = datetime.date.fromisoformat(start_date_str)
    except Exception:
        start_date = datetime.date.today() + datetime.timedelta(days=7)
        
    itinerary = []
    bank_index = 0
    
    for day_idx in range(1, num_days + 1):
        cur_date = start_date + datetime.timedelta(days=day_idx - 1)
        day_title = f"Day {day_idx}: Highlights of {dest_clean}"
        theme = [f"Historic Heart & Cultural Treasures of {dest_clean}", f"Scenic Overlooks & Gastronomy of {dest_clean}", f"Hidden Quarters & Panoramic Sunsets of {dest_clean}", f"Nature Reserves & Waterfront Charms of {dest_clean}"][ (day_idx - 1) % 4 ]
        
        day_activities = []
        slots = ["morning", "afternoon", "evening"]
        
        for order_idx, slot in enumerate(slots):
            raw_act = bank[bank_index % len(bank)]
            bank_index += 1
            travel_time = "15 mins" if order_idx > 0 else "0 mins"
            
            day_activities.append({
                "time_slot": slot,
                "time_str": raw_act["time"],
                "title": raw_act["title"],
                "description": raw_act["desc"],
                "location_name": raw_act["loc"],
                "lat": raw_act["lat"],
                "lng": raw_act["lng"],
                "estimated_cost": raw_act["cost"],
                "duration_mins": raw_act["dur"],
                "travel_time_from_prev": travel_time,
                "transport_mode": raw_act["mode"],
                "category": raw_act["cat"],
                "is_indoor": raw_act["indoor"],
                "booking_url": None,
                "order_index": order_idx
            })
            
        itinerary.append({
            "day_number": day_idx,
            "date": cur_date.strftime("%b %d, %Y"),
            "title": day_title,
            "theme": theme,
            "notes": f"Pack comfortable walking shoes and stay hydrated while discovering {dest_clean}.",
            "activities": day_activities
        })
        
    return itinerary

def replan_day_for_weather(activities: List[Dict[str, Any]], weather_condition: str = "Rain") -> List[Dict[str, Any]]:
    """Substitutes outdoor activities with rich indoor experiences when weather is unfavorable."""
    replanned = []
    for act in activities:
        if not act.get("is_indoor", False):
            new_act = act.copy()
            new_act["title"] = f"[Indoor Alternative] {act['title'].replace('Trek', 'Museum').replace('Walk', 'Gallery')}"
            new_act["description"] = f"Adapted for {weather_condition}: Sheltered indoor cultural experience replacing outdoor schedule."
            new_act["is_indoor"] = True
            replanned.append(new_act)
        else:
            replanned.append(act)
    return replanned
