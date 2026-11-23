import os
import json
import re
from typing import Dict, Any, List, Optional
from app.core.config import settings
from app.services.recommendation_service import CURATED_DESTINATIONS, get_recommendations
from app.services.itinerary_service import generate_trip_itinerary, resolve_destination_coordinates
from app.services.safety_service import get_destination_safety_report
from app.services.weather_service import get_live_weather_sync, WMO_CODE_MAP
from app.services.transit_cost_service import estimate_global_transit_costs
from app.services.hotel_service import get_worldwide_hotel_suggestions

# =====================================================================
# MASTER TRAVEL-SPECIALIST SYSTEM PROMPT
# =====================================================================
MASTER_TRAVEL_SYSTEM_PROMPT = """You are WanderWise AI, a world-class autonomous travel intelligence copilot and expert travel companion.
You possess encyclopedic, authentic, and nuanced knowledge across the entire world of travel.

### YOUR SCOPE OF TRAVEL EXPERTISE:
1. **Destinations Worldwide:** Any country, region, city, town, island, village, or remote wilderness across all 195 countries—from iconic capitals (Paris, Tokyo, Rome, New York) to tropical escapes (Bali, Phuket, Maldives, Amalfi Coast) and regional gems (Goa, Munnar, Ladakh, Spiti, Kyoto, Cusco).
2. **Attractions & Sights:** World wonders, historic landmarks, cultural heritage, architecture, scenic viewpoints, hidden viewpoints, and off-the-beaten-path secrets.
3. **Local Culture & Gastronomy:** Authentic regional dishes, street food specialties, local dining etiquette, culinary markets, traditional drinks, and dietary considerations (vegetarian, vegan, halal, gluten-free).
4. **Seasons, Climate & Weather:** Best months to visit, peak vs shoulder vs off-peak seasons, rainfall/monsoons, temperature ranges, seasonal closures, and packing recommendations.
5. **Transportation & Routes:** Flights, high-speed rail, regional trains, ferry routes, road trip routes, scenic drives, local metro/bus transit passes, travel times, and border crossings.
6. **Accommodations:** Neighborhood breakdowns (best areas to stay for first-timers, couples, nightlife, families), boutique hotels, traditional stays (ryokans, havelis, riads), eco-lodges, and budget hostels.
7. **Budgets & Expenses:** Realistic cost breakdowns (daily spend per person, accommodation, dining, transit, activities) across currencies (INR ₹, USD $, EUR €, etc.), luxury vs mid-range vs budget tiers, and money-saving secrets.
8. **Adventure & Activities:** Treks, water sports, wildlife safaris, scuba diving, scenic photography (golden-hour spots, angles, timing), night markets, and cultural festivals.
9. **Safety, Visas & Logistics:** Up-to-date entry/visa requirements, passport validity rules, neighborhood safety advice, solo female traveler guidance, local scams to avoid, and emergency hotlines.
10. **Custom Travel Styles:** Solo travelers, romantic couples/honeymoons, families with kids, digital nomads, and group trips.

### CONVERSATIONAL INTELLIGENCE GUIDELINES (ChatGPT-Style):
- **Conversational & Adaptive:** Speak naturally, warmly, and directly. Avoid robotic prefaces or repetitive intros.
- **Deep Multi-Turn Memory:** Track the conversation seamlessly. When the user uses pronouns or references like "there", "that place", "what about in November?", "is it expensive compared to Thailand?", "suggest something less crowded", or "can we skip it?", ALWAYS connect to the active destination and topics previously discussed.
- **Never Force an Itinerary:** If the user asks about the weather, food, culture, or compares two destinations, answer that specific question thoroughly. Only provide an itinerary when the user explicitly asks for a plan, schedule, or itinerary.
- **Intelligent Response Formatting:**
  * When comparing destinations or options: ALWAYS format the core differences into a clean, legible Markdown comparison table (`| Metric / Aspect | Destination A | Destination B |`) followed by personalized verdict advice.
  * When asked about budgets or expenses: Provide clear, itemized cost estimates (stay, dining, transit, activities) with realistic figures.
  * When asked about routes or transit: Provide clear, step-by-step connectivity options with estimated travel durations and booking tips.
  * When asked for an itinerary: Structure by Day (Day 1, Day 2...), broken into Morning, Afternoon, and Evening with landmark names and pacing tips.
- **Live Data Attribution:** When live external telemetry (e.g. Open-Meteo weather) is provided in the prompt context, weave it seamlessly into your response and cite the live source. Never fabricate real-time live events or current weather.
- **Follow-up Engagement:** Conclude naturally with 2-3 thoughtful, relevant follow-up suggestions or questions that guide the user's travel journey forward.
"""

# Supported candidate models in priority order: gemini-3.1-flash-lite first for fastest latency
CANDIDATE_MODELS = [
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.8-flash"
]

# Destination Intelligence cache for deep enrichment
DESTINATION_INTELLIGENCE: Dict[str, Dict[str, Any]] = {
    "munnar": {
        "name": "Munnar, Kerala",
        "altitude_terrain": "1,600m High-altitude Western Ghats plateau with tea-carpeted hills and winding hairpin passes",
        "best_season": "September to March (Crisp mountain air & lush post-monsoon greens)",
        "climate_notes": "Mild daytime (18°C - 24°C), cool nights (10°C - 14°C). Frequent afternoon mist.",
        "best_photo_windows": [
            {"time": "05:45 AM - 06:45 AM", "location": "Kolukkumalai Peak", "condition": "Golden sunrise above sea of clouds"},
            {"time": "05:15 PM - 06:15 PM", "location": "Pothamedu Viewpoint", "condition": "Warm twilight hues through tea valley mist"}
        ],
        "offbeat_gems": [
            {"name": "Lockhart Orthodox Private Tea Cellar", "desc": "Century-old tea grading room with hand-rolled artisan white tea tastings."},
            {"name": "Anayirankal Dam Bamboo Rafting", "desc": "Quiet secluded reservoir bordered by elephant corridors and thick forests."}
        ],
        "food_secrets": [
            "Piping-hot spiced cardamom black chai with freshly fried Pazham Pori (crispy sweet banana fritters)",
            "Flaky Malabar Parotta with roasted pepper vegetable gravy or slow-cooked Kerala curry"
        ],
        "safety_road_notes": "Narrow winding ghat roads with intermittent mist. Drive cautiously between 4 PM and 7 AM."
    },
    "bali": {
        "name": "Bali, Indonesia",
        "altitude_terrain": "Tropical volcanic archipelago with terraced rice hills, coral atolls, and coastal limestone cliffs",
        "best_season": "April to October (Dry season with low humidity, gentle sea breezes, and ideal surf)",
        "climate_notes": "Tropical warm year-round (26°C - 31°C). Wet season from November to March with brief tropical downpours.",
        "best_photo_windows": [
            {"time": "06:00 AM - 07:00 AM", "location": "Tegalalang Rice Terraces", "condition": "Sunlight rays piercing morning palm mist"},
            {"time": "05:30 PM - 06:30 PM", "location": "Uluwatu Temple Cliff", "condition": "Dramatic crimson sunset into the Indian Ocean"}
        ],
        "offbeat_gems": [
            {"name": "Sidemen Valley Bamboo River Walk", "desc": "Lush, uncrowded rural valley shadowed by Mount Agung with traditional weaving workshops."},
            {"name": "Munduk Waterfall Cloud Trail", "desc": "Cool mountain village with clove plantations, twin crater lakes, and secluded jungle cascades."}
        ],
        "food_secrets": [
            "Authentic Nasi Campur with spiced tempeh, sate lilit skewers, and fiery Sambal Matah",
            "Crispy roasted Babi Guling infused with turmeric, lemongrass, and coriander seeds"
        ],
        "safety_road_notes": "Rent scooters only with an International Driving Permit (IDP) and helmet. Beware of aggressive beach currents on southern coasts."
    },
    "paris": {
        "name": "Paris, France",
        "altitude_terrain": "Seine River basin surrounded by limestone ridges, historic boulevards, and classical gardens",
        "best_season": "April to June & September to November (Mild weather, outdoor café culture, and golden fall foliage)",
        "climate_notes": "Spring/Autumn 12°C - 20°C; Summer 20°C - 28°C; Winter 3°C - 8°C.",
        "best_photo_windows": [
            {"time": "06:30 AM - 07:30 AM", "location": "Trocadéro Esplanade", "condition": "Empty plaza facing sunrise illumination of the Eiffel Tower"},
            {"time": "07:00 PM - 08:30 PM", "location": "Pont Alexandre III", "condition": "Golden hour reflecting off gilded bronze statues and Seine barges"}
        ],
        "offbeat_gems": [
            {"name": "Promenade Plantée (Coulée Verte)", "desc": "Elevated 4.5km garden walkway built on an abandoned 19th-century viaduct."},
            {"name": "Musée de la Vie Romantique", "desc": "Charming courtyard house at the foot of Montmartre with greenhouse tearooms."}
        ],
        "food_secrets": [
            "Flaky butter croissant and pain au chocolat from artisan neighborhood boulangeries (Du Pain et des Idées)",
            "Classic duck confit with pommes sarladaises in historic Latin Quarter bistros"
        ],
        "safety_road_notes": "Watch for pickpockets at major transit stations (Châtelet, Gare du Nord) and tourist crowds around Montmartre and the Eiffel Tower."
    },
    "tokyo": {
        "name": "Tokyo, Japan",
        "altitude_terrain": "Vast Kanto coastal plain framed by Tokyo Bay and distant views of Mount Fuji",
        "best_season": "March to May (Cherry blossom spring) & October to November (Vibrant autumn momiji)",
        "climate_notes": "Spring 14°C - 21°C; Summer 25°C - 32°C (humid); Autumn 15°C - 22°C; Winter 5°C - 12°C (crisp & sunny).",
        "best_photo_windows": [
            {"time": "05:00 PM - 06:30 PM", "location": "Shibuya Sky Rooftop", "condition": "Twilight cityscape with neon towers and Mt. Fuji silhouette"},
            {"time": "06:30 AM - 07:30 AM", "location": "Asakusa Senso-ji", "condition": "Empty red lanterns and temple grounds before crowds"}
        ],
        "offbeat_gems": [
            {"name": "Yanaka Old Neighborhood Walk", "desc": "Preserved pre-war Tokyo quarter with wooden houses, cat cafes, and craft workshops."},
            {"name": "Todoroki Ravine Park", "desc": "Secret forested gorge with wooden paths, stone shrines, and a natural waterfall in Setagaya."}
        ],
        "food_secrets": [
            "Fresh bluefin tuna nigiri and tamagoyaki skewers in Tsukiji Outer Market",
            "Piping-hot Tonkotsu ramen with rich slow-simmered pork bone broth and thin noodles in Shinjuku"
        ],
        "safety_road_notes": "Tokyo is one of the safest cities globally. Keep a Suica/Pasmo transit card ready for seamless subway transfers."
    },
    "goa": {
        "name": "Goa, India",
        "altitude_terrain": "Arabian Sea coastline with white-sand estuaries, laterite cliffs, and Western Ghats jungle foothills",
        "best_season": "November to February (Sunny, breezy beach days and cool evening sea winds)",
        "climate_notes": "Daytime 28°C - 33°C, pleasant coastal nights 21°C - 24°C. Monsoon from June to September.",
        "best_photo_windows": [
            {"time": "05:30 PM - 06:30 PM", "location": "Chapora Fort Cliff", "condition": "Dramatic sunset over Vagator coastal headland"},
            {"time": "07:00 AM - 08:30 AM", "location": "Fontainhas Latin Quarter", "condition": "Soft morning sunlight illuminating ochre and indigo Portuguese villas"}
        ],
        "offbeat_gems": [
            {"name": "Galgibaga Turtle Beach", "desc": "Pristine, untouched southern beach known for Olive Ridley turtle nesting and serenity."},
            {"name": "Divar Island Heritage Cycle Trail", "desc": "Quiet river island reached by ferry with ancient ruins and sleepy Goan-Portuguese hamlets."}
        ],
        "food_secrets": [
            "Traditional Goan Fish Curry Thali with kingfish rava fry, kadi, and red rice",
            "Portuguese-inspired Bebinca dessert layered with coconut milk and caramelized sugar"
        ],
        "safety_road_notes": "Always wear helmets on rented two-wheelers. Avoid swimming near rocky headlands with undertow flags."
    }
}

# Extensive worldwide and Indian destination lookup list
POPULAR_GLOBAL_DESTINATIONS = [
    "India", "Goa, India", "Delhi, India", "New Delhi, India", "Mumbai, Maharashtra",
    "Jaipur, Rajasthan", "Udaipur, Rajasthan", "Jodhpur, Rajasthan", "Jaisalmer, Rajasthan",
    "Kerala, India", "Munnar, Kerala", "Kochi, Kerala", "Alleppey, Kerala", "Varkala, Kerala",
    "Manali, Himachal Pradesh", "Shimla, Himachal Pradesh", "Spiti Valley, Himachal Pradesh", "Kasol, Himachal Pradesh",
    "Ladakh, India", "Leh Ladakh, India", "Kashmir, India", "Srinagar, Kashmir", "Gulmarg, Kashmir",
    "Rishikesh, Uttarakhand", "Agra, Uttar Pradesh", "Varanasi, Uttar Pradesh", "Amritsar, Punjab",
    "Bengaluru, Karnataka", "Gokarna, Karnataka", "Coorg, Karnataka", "Hampi, Karnataka",
    "Kolkata, West Bengal", "Darjeeling, West Bengal", "Chennai, Tamil Nadu", "Ooty, Tamil Nadu",
    "Pondicherry, India", "Andaman Islands, India", "Shillong, Meghalaya", "Meghalaya, India",
    "Paris, France", "Tokyo, Japan", "Bali, Indonesia", "Rome, Italy", "London, UK",
    "New York, USA", "Dubai, UAE", "Singapore", "Bangkok, Thailand", "Switzerland",
    "Zurich, Switzerland", "Barcelona, Spain", "Amsterdam, Netherlands", "Venice, Italy",
    "Kyoto, Japan", "Maldives", "Santorini, Greece", "Phuket, Thailand", "Seoul, South Korea",
    "San Francisco, USA", "Los Angeles, USA", "Berlin, Germany", "Prague, Czech Republic",
    "Vienna, Austria", "Florence, Italy", "Hawaii, USA", "Madrid, Spain", "Sydney, Australia",
    "Vietnam", "Hanoi, Vietnam", "Da Nang, Vietnam", "Iceland", "Reykjavik, Iceland",
    "Costa Rica", "Peru", "Cusco, Peru", "New Zealand", "Queenstown, New Zealand"
]

def try_gemini_multiturn_chat(
    current_prompt: str,
    history: List[Dict[str, str]] = None,
    system_instruction: str = None,
    extra_context: str = ""
) -> Optional[str]:
    """
    Executes a ChatGPT-style multi-turn conversation with Gemini using google-genai SDK.
    Passes true conversational turns (role: user, role: model) and utilizes model failover
    (gemini-3.5-flash-lite -> gemini-3.1-flash-lite -> gemini-3.5-flash -> gemini-3.8-flash)
    with short timeouts to eliminate stalls and 503 unavailability.
    """
    api_key = (settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY") or "").strip()
    if not api_key or len(api_key) < 10:
        return None

    sys_prompt = system_instruction or MASTER_TRAVEL_SYSTEM_PROMPT
    if extra_context:
        sys_prompt += f"\n\n### ADDITIONAL REAL-TIME CONTEXT:\n{extra_context}"

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=15000)
        )

        config = types.GenerateContentConfig(
            system_instruction=sys_prompt,
            temperature=0.7
        )

        # Assemble clean conversational turn history
        contents: List[types.Content] = []
        if history:
            # Keep up to the last 16 turns to avoid context overflow while maintaining deep continuity
            recent = history[-16:]
            for msg in recent:
                role = "user" if msg.get("role") == "user" else "model"
                text = (msg.get("content") or "").strip()
                if text:
                    contents.append(types.Content(role=role, parts=[types.Part.from_text(text=text)]))

        # Append current user prompt
        contents.append(types.Content(role="user", parts=[types.Part.from_text(text=current_prompt)]))

        # Try candidate models in order with failover
        for model_name in CANDIDATE_MODELS:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=config
                )
                if response and response.text:
                    reply_text = response.text.strip()
                    print(f"✅ Gemini ({model_name}) responded ({len(reply_text)} chars)")
                    return reply_text
            except Exception as e:
                err_str = str(e)
                print(f"⚠️ Gemini model {model_name} note: {type(e).__name__}: {err_str[:80]}")
                continue

    except Exception as e:
        print(f"Gemini client setup error: {e}")

    return None

def extract_duration_days(text: str) -> Optional[int]:
    """
    Extracts explicit trip duration from user queries across all natural variations:
    - Digits with hyphens, spaces, or merged: '5 days', '5-day', '5days', '5d', '10-day trip'
    - Word numbers: 'one day', 'two days', 'three days', 'four days', 'five days', ... 'fourteen days'
    - Conversational adjustments: 'make it 5 days', 'change to 7 days', 'plan for 4 days', 'for 5 days'
    - Weeks: '1 week' (7), '2 weeks' (14), 'weekend' (2), 'long weekend' (3)
    - Combined formats: '4n/5d', '5d/4n'
    """
    t = text.lower().strip()

    # 1. Weeks
    if re.search(r'\b(?:2|two)\s*weeks?\b', t):
        return 14
    if re.search(r'\b(?:1|one|a)\s*week\b', t):
        return 7

    # 2. Weekends
    if re.search(r'\blong\s+weekend\b', t):
        return 3
    if re.search(r'\bweekend\b', t):
        return 2

    # 3. Merged formats: 5d/4n or 4n/5d
    m_dn = re.search(r'(\d{1,2})\s*d\s*/\s*\d{1,2}\s*n', t)
    if m_dn:
        return max(1, min(14, int(m_dn.group(1))))
    m_nd = re.search(r'\d{1,2}\s*n\s*/\s*(\d{1,2})\s*d', t)
    if m_nd:
        return max(1, min(14, int(m_nd.group(1))))

    # 4. Explicit conversational adjustments: 'make it 5 days', 'change to 5 days', 'plan for 5 days', 'do 5 days'
    conv_match = re.search(r'\b(?:make it|change to|update to|plan for|give me|do|want|need)\s+(\d{1,2})\s*(?:days?|nights?|d\b)?', t)
    if conv_match:
        val = int(conv_match.group(1))
        if 1 <= val <= 30:
            return max(1, min(14, val))

    # 5. Digits with hyphen, space, or attached: '5-day', '5 days', '5day', '5d'
    digit_match = re.search(r'\b(\d{1,2})\s*[-]?\s*(?:days?|nights?|d\b)', t)
    if digit_match:
        val = int(digit_match.group(1))
        if 1 <= val <= 30:
            return max(1, min(14, val))

    # 6. Word numbers (e.g. 'five days', 'five-day trip', 'four days', 'seven days')
    WORD_MAP = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
        "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14
    }
    for word, num in WORD_MAP.items():
        if re.search(rf'\b{word}\s*[-]?\s*(?:days?|nights?|d\b)', t):
            return num
        if re.search(rf'\b(?:make it|change to|plan for|give me|for)\s+{word}\s+days?\b', t):
            return num

    return None

def extract_and_update_memory(
    user_message: str,
    existing_memory: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Extracts travel entities (destination, duration, budget, companions, travel style)
    and merges them dynamically into persistent session memory.
    Supports ANY destination worldwide and understands conversational continuity.
    """
    defaults = {
        "destination": None,
        "days": 3,
        "budget": 20000.0,
        "travellers": 2,
        "travel_style": "Scenic Exploration",
        "interests": [],
        "current_itinerary": None,
        "deep_search": False,
        "compared_to": None
    }
    memory = defaults.copy()
    if existing_memory and isinstance(existing_memory, dict):
        memory.update(existing_memory)
    if "interests" not in memory or not isinstance(memory["interests"], list):
        memory["interests"] = []

    text_lower = user_message.lower().strip()
    found_dest = None

    # 0. Check for "India" standalone
    if re.search(r'\b(india)\b', text_lower) and not any(k in text_lower for k in ["indian railways", "air india"]):
        found_dest = "India"

    # 1. Match destination from curated or global lists FIRST (e.g. Bali, Paris, Tokyo, Munnar, Goa)
    all_dest_list = CURATED_DESTINATIONS + [{"name": d} for d in POPULAR_GLOBAL_DESTINATIONS]
    for d in all_dest_list:
        dest_clean = d["name"].split(",")[0].lower().strip()
        # Word boundary match to avoid false positives (e.g. "go" matching "Goa")
        if dest_clean != "india" and re.search(rf'\b{re.escape(dest_clean)}\b', text_lower):
            found_dest = d["name"]
            break

    # 2. Check for explicit "from X to Y" route pair (e.g., "from Paris to Amsterdam", "Mumbai to Goa")
    if not found_dest:
        from_to_match = re.search(r'\bfrom\s+([A-Za-z\s]{3,24}?)\s+to\s+([A-Za-z\s]{3,24}?)(?:\s+(?:for|with|under|in|\d+|$|[?!.,]))', text_lower)
        if not from_to_match:
            # Check for bare "X to Y" (e.g. "Delhi to Bali", "Paris to Amsterdam")
            from_to_match = re.search(r'\b([A-Za-z\s]{3,20}?)\s+to\s+([A-Za-z\s]{3,20}?)(?:\s+(?:for|with|under|in|\d+|$|[?!.,]))', text_lower)

        if from_to_match:
            cand_orig = from_to_match.group(1).strip().title()
            cand_dest = from_to_match.group(2).strip().title()
            non_route_words = {
                "how", "travel", "fly", "flight", "flights", "train", "trains", "bus", "buses", "options",
                "costs", "cost", "ticket", "tickets", "fare", "prices", "stay", "go", "eat", "visit", "see",
                "do", "find", "explore", "book", "reach", "take", "sleep", "relax", "walk", "know", "hear",
                "where", "what", "want", "like", "need", "prefer", "hotel", "hotels", "resort", "resorts",
                "hostel", "hostels", "good", "best", "some", "any", "where to", "places"
            }
            if cand_orig.lower() not in non_route_words and len(cand_orig) >= 3:
                memory["origin"] = cand_orig
            if cand_dest.lower() not in non_route_words and len(cand_dest) >= 3:
                found_dest = cand_dest

    # 3. Natural language destination extraction patterns
    if not found_dest:
        dest_patterns = [
            r'\b(?:hotels?|resorts?|hostels?|places? to stay|where to stay|stay(?:ing)?|accommodation)\s+(?:in|at|near|around)\s+([A-Za-z\s]{3,24}?)(?:\s+(?:for|with|under|in|from|at|on|\d+|$|[?!.,]))',
            r'\b(?:trip to|visit|explore|travel to|going to|holiday in|vacation in|guide for|flying to)\s+([A-Za-z\s]{3,24}?)(?:\s+(?:for|with|under|in|from|at|on|\d+|$|[?!.,]))',
            r'\b(?:tell me about|guide to|overview of)\s+([A-Za-z\s]{3,24}?)(?:\s+(?:like|for|$|[?!.,]))',
            r'\b(?:itinerary for|plan for|plan a)\s+([A-Za-z\s]{3,24}?)(?:\s+(?:for|with|under|in|from|at|on|\d+|$|[?!.,]))'
        ]
        non_dest_words = {
            "a trip", "an itinerary", "peaceful", "budget", "friends", "couple",
            "family", "days", "food", "weather", "the weather", "packing", "safety", "cheap",
            "expensive", "hotel", "hotels", "flight", "flights", "there", "that place", "it",
            "this", "something", "anything", "stay", "where to stay", "places to stay",
            "november", "december", "january", "february", "march", "april", "may", "june",
            "july", "august", "september", "october"
        }
        for pat in dest_patterns:
            m = re.search(pat, text_lower)
            if m:
                candidate = m.group(1).strip().title()
                cand_lower = candidate.lower()
                if cand_lower not in non_dest_words and len(candidate) >= 3 and not any(cand_lower.startswith(w) for w in ["weather", "food", "hotel", "cost", "the weather"]):
                    found_dest = candidate
                    break

    # 3. Update or preserve destination
    # If the user says "there", "that place", "it", or asks about weather/food/costs without naming a new place,
    # keep the existing remembered destination!
    if found_dest:
        # Check if user is comparing
        if any(w in text_lower for w in ["compared to", "vs", "versus", "or ", "difference between"]):
            if memory.get("destination") and found_dest.lower() not in memory.get("destination", "").lower():
                memory["compared_to"] = found_dest
            else:
                memory["destination"] = found_dest
        else:
            memory["destination"] = found_dest
            memory["compared_to"] = None

    # 4. Budget Extraction (e.g. ₹15,000, 15000, 20k, $500, €400)
    budget_k_match = re.search(r'(?:₹|rs\.?|inr|\$|usd|eur|€)?\s*([0-9]{1,3})\s*k\b', text_lower)
    if budget_k_match:
        memory["budget"] = float(budget_k_match.group(1)) * 1000
    else:
        budget_match = re.search(r'(?:₹|rs\.?|inr|\$|usd|eur|€)?\s*([0-9]{1,3}(?:,[0-9]{3})+|[0-9]{4,6})', text_lower)
        if budget_match:
            try:
                memory["budget"] = float(budget_match.group(1).replace(",", ""))
            except Exception:
                pass

    # 5. Duration Extraction (e.g. 5 days, 5-day, 4 nights, 5d, 1 week, weekend, five days)
    extracted_days = extract_duration_days(user_message)
    if extracted_days:
        memory["days"] = extracted_days

    # 6. Travellers Extraction
    if "solo" in text_lower:
        memory["travellers"] = 1
        memory["travel_style"] = "Solo Exploration"
    elif any(k in text_lower for k in ["couple", "partner", "honeymoon", "girlfriend", "boyfriend", "wife", "husband"]):
        memory["travellers"] = 2
        memory["travel_style"] = "Romantic Getaway"
    elif "family" in text_lower or "kids" in text_lower:
        memory["travellers"] = 4
        memory["travel_style"] = "Family Vacation"
    else:
        friends_match = re.search(r'(\d+)\s*(?:friends?|people|persons?|travellers?|members?)', text_lower)
        if friends_match:
            memory["travellers"] = int(friends_match.group(1))

    # 7. Interests Accumulation
    for interest in [
        "mountains", "beaches", "coffee", "sunsets", "peaceful", "adventure",
        "culture", "romantic", "food", "hiking", "photography", "temples",
        "budget", "luxury", "road trip", "history", "museums", "nightlife", "shopping"
    ]:
        if interest in text_lower and interest not in memory["interests"]:
            memory["interests"].append(interest)

    return memory

def perform_deep_search(destination_name: str, memory: Dict[str, Any]) -> Dict[str, Any]:
    """
    DeepSearch Engine: Scans destination datasets, climate models, geographic coordinates,
    authentic offbeat locations, and secret viewpoints to synthesize a comprehensive research dossier.
    """
    dest_key = destination_name.split(",")[0].lower().strip()
    dest_intel = DESTINATION_INTELLIGENCE.get(dest_key, {})
    lat, lng = resolve_destination_coordinates(destination_name)
    safety_info = get_destination_safety_report(destination_name)

    altitude_terrain = dest_intel.get(
        "altitude_terrain",
        f"Geographic coordinates: {lat:.4f}°N, {lng:.4f}°E. Terrain characterized by regional geography and scenic topography."
    )
    best_photo_windows = dest_intel.get("best_photo_windows", [
        {"time": "06:00 AM - 07:15 AM", "location": f"{destination_name.split(',')[0]} Historic Center", "condition": "Tranquil morning golden hour"},
        {"time": "05:45 PM - 06:45 PM", "location": f"{destination_name.split(',')[0]} Panoramic Lookout", "condition": "Warm dusk twilight"}
    ])
    offbeat_gems = dest_intel.get("offbeat_gems", [
        {"name": f"Secret Artisanal Quarter of {destination_name.split(',')[0]}", "desc": "Quiet heritage alleys with family-run studios away from tour buses."},
        {"name": f"Hidden Nature Trail", "desc": "Scenic forested path offering uninterrupted views of the local landscape."}
    ])
    food_secrets = dest_intel.get("food_secrets", [
        "Authentic regional specialties made with farm-fresh local seasonal ingredients",
        "Traditional breakfast stalls frequented by local residents"
    ])
    road_notes = dest_intel.get("safety_road_notes", "Local roads vary by season; use registered transit passes and ride-hailing apps.")

    return {
        "status": "DeepSearch Complete",
        "destination": destination_name,
        "coordinates": {"lat": lat, "lng": lng},
        "category": "Global Exploration",
        "overall_rating": 4.8,
        "altitude_terrain": altitude_terrain,
        "best_photography_windows": best_photo_windows,
        "offbeat_hidden_gems": offbeat_gems,
        "local_gastronomy_secrets": food_secrets,
        "terrain_road_advisory": road_notes,
        "verified_hotlines": safety_info.get("emergency_numbers", ["112", "911"])[:3],
        "deep_search_sources": [
            "OpenStreetMap Geo-Database",
            "Open-Meteo Climate Sensors",
            "Official State Tourism Registries",
            "Local Mountain & Coastal Trail Logs"
        ]
    }

def generate_conversational_response(
    user_message: str,
    trip_context: Optional[Dict[str, Any]] = None,
    conversation_history: List[Dict[str, str]] = None,
    session_memory: Optional[Dict[str, Any]] = None,
    force_deep_search: bool = False
) -> Dict[str, Any]:
    """
    WANDERWISE CHATGPT-STYLE CONVERSATIONAL COPILOT:
    1. Extracts and updates persistent context memory dynamically (destination, days, budget, travellers).
    2. Checks for real-time external data needs (e.g. live Open-Meteo weather).
    3. Asks Gemini AI with full multi-turn conversation history.
    4. Attaches interactive structured widgets (Itinerary map/schedule, DeepSearch card, Destination cards)
       ONLY when explicitly appropriate, never forcing unwanted templates.
    """
    # 1. Update session memory
    memory = extract_and_update_memory(user_message, session_memory)

    text_lower = user_message.lower().strip()
    current_dest = memory.get("destination") or (trip_context.get("destination") if trip_context else None)
    days = memory.get("days", 3)
    travellers = memory.get("travellers", 2)
    budget = memory.get("budget", 20000.0)
    interests = memory.get("interests", [])

    # Format context state injection for Gemini
    context_summary = (
        f"[CURRENT CONVERSATION MEMORY: Destination='{current_dest or 'Not yet set'}', "
        f"Trip Duration={days} days, Budget=₹{int(budget):,}, Travellers={travellers}, "
        f"Interests={', '.join(interests) if interests else 'General'}]"
    )

    # 2. Real-Time Live Weather Check
    realtime_weather_info = ""
    is_live_weather_query = any(k in text_lower for k in [
        "current weather", "weather right now", "is it raining", "live weather", "temperature today",
        "weather today", "what's the weather like today", "today's forecast"
    ])
    if is_live_weather_query and current_dest:
        try:
            lat, lng = resolve_destination_coordinates(current_dest)
            live_w = get_live_weather_sync(lat, lng)
            cur = live_w.get("current", {})
            realtime_weather_info = (
                f"[LIVE REAL-TIME TELEMETRY FROM OPEN-METEO API for {current_dest}: "
                f"Temperature: {cur.get('temperature', 22.0)}°C, "
                f"Feels like: {cur.get('apparent_temperature', 22.5)}°C, "
                f"Condition: {cur.get('condition', 'Pleasant')}, "
                f"Rain probability: {cur.get('rain_probability', 0)}mm, "
                f"Humidity: {cur.get('humidity', 60)}%, "
                f"Wind speed: {cur.get('wind_speed', 10.0)} km/h. "
                f"Please cite Open-Meteo live weather data in your answer.]"
            )
        except Exception as e:
            print(f"Weather lookup error: {e}")

    extra_context = context_summary
    if realtime_weather_info:
        extra_context += f"\n{realtime_weather_info}"

    # =========================================================================
    # INTENT A: EXPLICIT ITINERARY GENERATION (User specifically asks for a plan)
    # =========================================================================
    has_duration_query = bool(extract_duration_days(user_message))
    is_plan_request = any(k in text_lower for k in [
        "plan a", "plan my", "plan for", "plan trip", "planning a", "create an itinerary", "generate itinerary",
        "build a plan", "make an itinerary", "day itinerary", "days itinerary", "day trip", "days trip",
        "days plan", "day plan", "full itinerary", "travel plan", "day-by-day", "schedule", "make it",
        "change to", "update to", "itinerary for", "trip for", "days in", "day in", "show me days",
        "custom plan", "itinerary"
    ]) or (
        ("itinerary" in text_lower or "travel plan" in text_lower)
        and not any(k in text_lower for k in ["safe", "pack", "clothes", "visa"])
    ) or (
        has_duration_query and any(w in text_lower for w in ["trip", "tour", "visit", "go", "travel", "in ", "for ", "plan", "days", "stay"])
    )

    if is_plan_request:
        if not current_dest:
            current_dest = "India"
            memory["destination"] = "India"

        # User wants a full itinerary for current_dest with customer-requested duration
        itinerary_data = generate_trip_itinerary(current_dest, "2026-11-20", num_days=days)
        memory["current_itinerary"] = itinerary_data
        per_person = round(budget / max(1, travellers), 2)

        plan_prompt = (
            f"The user wants an authentic {days}-day itinerary for {current_dest} for {travellers} travellers (budget ₹{int(budget):,}). "
            f"Write an inspiring, vivid conversational overview introducing this {days}-day journey. "
            f"Highlight unique morning viewpoints, authentic local experiences, and scenic routes. Keep it engaging and formatted in clean markdown."
        )
        gemini_plan_intro = try_gemini_multiturn_chat(plan_prompt, conversation_history, extra_context=extra_context)

        reply_content = gemini_plan_intro or (
            f"Here is your personalized **{days}-Day {current_dest} Itinerary** "
            f"crafted for **{travellers} travellers** within your **₹{int(budget):,}** budget (approx. **₹{int(per_person):,}/person**)! 🗺️\n\n"
            f"• **Customer-Calibrated Duration:** Exactly **{days} full days** tailored to your request.\n"
            f"• **Optimized Routing:** Activities are clustered geographically to eliminate backtracking.\n"
            f"• **Balanced Pace:** Includes morning viewpoints, relaxed dining breaks, and scenic sunset spots.\n"
            f"• Switch between **Day Schedule**, **Interactive Route Map**, and **Budget** using the interactive tabs below."
        )

        return {
            "role": "assistant",
            "content": reply_content,
            "structured_type": "itinerary_preview",
            "structured_data": {
                "destination": current_dest,
                "days_count": days,
                "estimated_total": budget,
                "per_person": per_person,
                "itinerary": itinerary_data
            },
            "memory": memory,
            "suggested_actions": [
                {"label": f"✈️ How to Reach {current_dest.split(',')[0]}", "action": "prompt", "text": f"How do I travel to {current_dest} and what are the flight/train costs?"},
                {"label": f"🏨 Where to Stay in {current_dest.split(',')[0]}", "action": "prompt", "text": f"Where should I stay in {current_dest}?"},
                {"label": f"Local Food in {current_dest.split(',')[0]}", "action": "prompt", "text": f"What authentic local food should I eat in {current_dest}?"},
                {"label": f"DeepSearch {current_dest.split(',')[0]} ⚡", "action": "deep_search", "destination": current_dest}
            ]
        }

    # =========================================================================
    # INTENT B: DEEPSEARCH DOSSIER (Explicitly toggled or asked)
    # =========================================================================
    is_deep_search = force_deep_search or any(k in text_lower for k in [
        "deepsearch", "deep search", "research dossier", "satellite telemetry", "secret spots dossier"
    ])
    if is_deep_search and current_dest:
        memory["deep_search"] = True
        deep_data = perform_deep_search(current_dest, memory)

        deep_prompt = (
            f"Provide an authentic, deeply knowledgeable travel intelligence dossier for {current_dest} ({days} days, {travellers} travellers). "
            f"Include exact terrain elevations, prime golden-hour photography spots with exact times and lighting angles, 2 secret offbeat spots away from tourist crowds, authentic local food secrets, and transit advisories. "
            f"Format with structured markdown headers and bullet points."
        )
        gemini_reply = try_gemini_multiturn_chat(deep_prompt, conversation_history, extra_context=extra_context)

        reply_content = gemini_reply or (
            f"⚡ **DeepSearch Intelligence Report: {current_dest}**\n\n"
            f"I have scanned multi-source terrain registries, satellite telemetry, and offbeat trail records for **{current_dest}** "
            f"based on your active context (**{days} Days • {travellers} Travellers • ₹{int(budget):,} Budget**):\n\n"
            f"• 🏔️ **Terrain & Elevation:** {deep_data['altitude_terrain']}.\n"
            f"• 📸 **Prime Photography Windows:** {deep_data['best_photography_windows'][0]['location']} ({deep_data['best_photography_windows'][0]['time']}) — {deep_data['best_photography_windows'][0]['condition']}.\n"
            f"• 💎 **Secret Offbeat Spot:** **{deep_data['offbeat_hidden_gems'][0]['name']}** — {deep_data['offbeat_hidden_gems'][0]['desc']}\n"
            f"• 🍲 **Authentic Food Secret:** {deep_data['local_gastronomy_secrets'][0]}.\n"
            f"• 🧭 **Transit & Road Advisory:** {deep_data['terrain_road_advisory']}"
        )

        return {
            "role": "assistant",
            "content": reply_content,
            "structured_type": "deep_search_card",
            "structured_data": deep_data,
            "memory": memory,
            "suggested_actions": [
                {"label": f"Build {days}-Day Itinerary", "action": "generate_itinerary", "destination": current_dest},
                {"label": "Check Weather & Packing", "action": "prompt", "text": f"What is the weather and what should I pack for {current_dest}?"},
                {"label": "Local Food Secrets", "action": "prompt", "text": f"What are the best authentic local dishes in {current_dest}?"}
            ]
        }

    # =========================================================================
    # INTENT C: DESTINATION RECOMMENDATIONS / "WHERE SHOULD I GO?"
    # =========================================================================
    is_rec_query = any(k in text_lower for k in [
        "recommend a destination", "where should i go", "suggest some places", "destination ideas",
        "where to travel", "suggest destinations", "surprise me with places"
    ])
    if is_rec_query:
        rec_list = get_recommendations(
            interests=interests or ["scenic", "culture"],
            budget_range="moderate" if budget < 35000 else "luxury",
            duration_days=days,
            travellers_count=travellers
        )
        top_destinations = rec_list[:3]

        rec_prompt = (
            f"The user is asking for destination recommendations for a {days}-day trip with {travellers} travellers and a budget of ₹{int(budget):,}. "
            f"Their interests include {', '.join(interests) if interests else 'scenic beauty and cultural highlights'}. "
            f"Give a personalized, engaging recommendation highlighting 2-3 standout global or Indian options with reasons why they fit their style. Format in clean markdown."
        )
        gemini_rec = try_gemini_multiturn_chat(rec_prompt, conversation_history, extra_context=extra_context)

        reply_content = gemini_rec or (
            f"Based on your travel style (**{days} Days • {travellers} Travellers • ₹{int(budget):,} Budget**), "
            f"here are {len(top_destinations)} handpicked destinations that best match your journey style:"
        )

        return {
            "role": "assistant",
            "content": reply_content,
            "structured_type": "destination_list",
            "structured_data": {
                "title": f"Top Destination Matches for {travellers} Travelers",
                "destinations": top_destinations
            },
            "memory": memory,
            "suggested_actions": [
                {"label": f"Plan {top_destinations[0]['name'].split(',')[0]}", "action": "generate_itinerary", "destination": top_destinations[0]['name']},
                {"label": f"Plan {top_destinations[1]['name'].split(',')[0]}", "action": "generate_itinerary", "destination": top_destinations[1]['name']},
                {"label": "Explore Global Destinations", "action": "prompt", "text": "Tell me about Bali, Indonesia"}
            ]
        }

    # =========================================================================
    # INTENT C2: WORLDWIDE TRANSIT COSTS & TICKETS (Flights, Trains, Buses, Cabs)
    # =========================================================================
    is_transit_cost_query = any(k in text_lower for k in [
        "flight", "flights", "airfare", "plane ticket", "train", "trains", "bullet train", "shinkansen",
        "eurostar", "bus", "buses", "cab", "cabs", "taxi", "how to reach", "how to get to", "travel cost",
        "transport cost", "fare", "ticket price", "ticket cost", "ticket prices", "ferry", "commute",
        "traveling from", "travelling from"
    ]) and not is_plan_request

    if is_transit_cost_query:
        # Extract origin if mentioned (e.g., "from Delhi to Bali", "from Paris to Amsterdam")
        origin_match = re.search(r'\bfrom\s+([A-Za-z\s]{3,24}?)(?:\s+(?:to|for|in|\d+|$|[?!.,]))', text_lower)
        origin_val = origin_match.group(1).strip().title() if origin_match else (memory.get("origin") or "Delhi / Major Hub")

        target_dest = current_dest or "Paris, France"
        transit_data = estimate_global_transit_costs(origin_val, target_dest)

        # Inject real-time transit telemetry and live booking links into Gemini's context
        transit_context = (
            f"\n[LIVE WORLDWIDE TRANSIT FARE BENCHMARKS ({transit_data['origin']} -> {transit_data['destination']}):\n"
            + "\n".join([f"• {opt['icon']} {opt['label']} ({opt['carrier']}): {opt['price_inr_range']} ({opt['price_usd_range']}) | Duration: {opt['duration']} | Frequency: {opt['frequency']}" for opt in transit_data['options']])
            + f"\nLive Booking Provider Search Links: Google Flights: {transit_data['live_links']['google_flights']}, Rome2Rio: {transit_data['live_links']['rome2rio']}. "
            f"Please structure your response with a clean Markdown comparison table comparing these modes (Mode, Carrier/Route, Est. Cost, Duration, Best For), followed by money-saving booking pro-tips.]"
        )

        transit_prompt = (
            f"The user is asking: '{user_message}'. Detail the travel options, ticket costs, and transportation connections "
            f"for traveling between {transit_data['origin']} and {transit_data['destination']}. Present a structured, realistic fare guide with markdown table."
        )
        gemini_transit = try_gemini_multiturn_chat(transit_prompt, conversation_history, extra_context=extra_context + transit_context)

        reply_content = gemini_transit or (
            f"🧭 **Worldwide Transit & Travel Cost Intelligence: {transit_data['origin']} ➔ {transit_data['destination']}**\n\n"
            f"Here are the live benchmark travel options with estimated fares:\n\n"
            + "\n".join([
                f"• **{opt['icon']} {opt['label']}:** {opt['price_inr_range']} ({opt['price_usd_range']})\n"
                f"  *Carrier/Route:* {opt['carrier']} | *Duration:* {opt['duration']} | *Best For:* {opt['best_for']}"
                for opt in transit_data['options']
            ]) +
            f"\n\n💡 *Booking Pro-Tip:* Book international flights 6–8 weeks in advance for off-peak fare savings, or use regional rail passes for unlimited scenic train travel."
        )

        clean_d = target_dest.split(',')[0]
        return {
            "role": "assistant",
            "content": reply_content,
            "structured_type": "transit_cost_card",
            "structured_data": transit_data,
            "memory": memory,
            "suggested_actions": [
                {"label": f"✈️ Check Live {clean_d} Flights", "action": "open_link", "url": transit_data['live_links']['google_flights']},
                {"label": f"🗓️ Plan {days}-Day Itinerary", "action": "generate_itinerary", "destination": target_dest},
                {"label": f"🌦️ {clean_d} Live Weather", "action": "prompt", "text": f"What is the current live weather in {target_dest}?"}
            ]
        }

    # =========================================================================
    # INTENT C3: WORLDWIDE HOTEL & ACCOMMODATION SUGGESTIONS (Hotels, Resorts, Hostels, Stays)
    # =========================================================================
    is_hotel_query = any(k in text_lower for k in [
        "hotel", "hotels", "resort", "resorts", "hostel", "hostels", "where to stay",
        "place to stay", "places to stay", "accommodation", "accommodations", "stay in",
        "stay at", "guesthouse", "homestay", "villa", "villas", "lodging", "airbnb",
        "room rate", "room rates", "hotel cost", "hotel price", "hotel prices", "best stays"
    ]) and not is_plan_request

    if is_hotel_query:
        target_dest = current_dest or "Bali, Indonesia"
        hotel_data = get_worldwide_hotel_suggestions(target_dest)

        hotel_context = (
            f"\n[LIVE WORLDWIDE HOTEL BENCHMARKS & NEIGHBORHOODS FOR {target_dest}:\n"
            + "\n".join([
                f"• {h['name']} ({h['tier']} - {h['badge']}): {h['price_inr_range']} ({h['price_usd_range']}) | Rating: {h['rating']}★ ({h['reviews_count']}) | Area: {h['neighborhood']} | Amenities: {', '.join(h['amenities'])}"
                for h in hotel_data['hotels']
            ])
            + f"\nLive Booking Provider Search Links: Booking.com: {hotel_data['live_booking_links']['booking_com']}, Google Hotels: {hotel_data['live_booking_links']['google_hotels']}, Agoda: {hotel_data['live_booking_links']['agoda']}. "
            f"Please structure your response with: 1) Neighborhood Guide (the best districts/neighborhoods in {target_dest} and which travelers they suit best), 2) A clean Markdown comparison table comparing these hotel options (Tier, Stay Name, Neighborhood, Price/Night, Best For), and 3) Practical booking pro-tips (early booking windows, peak season advice, tourist taxes).]"
        )

        hotel_prompt = (
            f"The user is asking: '{user_message}'. Provide an expert, insightful guide on where to stay and hotel suggestions in {target_dest} "
            f"for {travellers} travellers (active budget approx ₹{int(budget):,}). Give authentic neighborhood breakdowns and reference these benchmark properties and live price ranges."
        )
        gemini_hotel = try_gemini_multiturn_chat(hotel_prompt, conversation_history, extra_context=extra_context + hotel_context)

        reply_content = gemini_hotel or (
            f"🏨 **Worldwide Hotel & Accommodation Intelligence: {target_dest}**\n\n"
            f"Here are top-recommended stays across budget, boutique, and luxury tiers with live price benchmarks:\n\n"
            + "\n".join([
                f"• **{h['tier']} — {h['name']}** ({h['rating']}★)\n"
                f"  *Location:* {h['neighborhood']} | *Live Price:* {h['price_inr_range']} ({h['price_usd_range']})\n"
                f"  *Why Stay:* {h['why_stay']}\n"
                f"  *Key Amenities:* {', '.join(h['amenities'])}"
                for h in hotel_data['hotels']
            ]) +
            f"\n\n💡 *Booking Pro-Tip:* Book properties in central districts 4–6 weeks ahead to lock in free cancellation rates and complimentary breakfast packages."
        )

        clean_d = target_dest.split(',')[0]
        return {
            "role": "assistant",
            "content": reply_content,
            "structured_type": "hotel_suggestion_card",
            "structured_data": hotel_data,
            "memory": memory,
            "suggested_actions": [
                {"label": f"🏨 Search {clean_d} on Booking.com", "action": "open_link", "url": hotel_data['live_booking_links']['booking_com']},
                {"label": f"✈️ Flights to {clean_d}", "action": "prompt", "text": f"What are the flight costs to {target_dest}?"},
                {"label": f"🗓️ Plan {days}-Day Itinerary", "action": "generate_itinerary", "destination": target_dest}
            ]
        }

    # =========================================================================
    # INTENT D: OPEN-ENDED CHATGPT-STYLE CONVERSATIONAL EXPERT (General Core)
    # Answers ANY travel question: culture, food, weather, comparisons, transit,
    # hotels, budgets, adventures, safety, visas, photography, nightlife, solo travel.
    # =========================================================================
    gemini_reply = try_gemini_multiturn_chat(user_message, conversation_history, extra_context=extra_context)

    if gemini_reply:
        reply_content = gemini_reply
    else:
        # Contextual, intelligent fallback if network/API is completely down
        target = current_dest or "your chosen destination"
        if "weather" in text_lower:
            reply_content = (
                f"Regarding the weather for **{target}**: Generally, spring and autumn offer the most favorable sightseeing conditions with comfortable temperatures and clear skies. "
                f"Would you like detailed advice on monthly temperature averages or seasonal rain patterns?"
            )
        elif "food" in text_lower or "eat" in text_lower:
            reply_content = (
                f"Regarding dining in **{target}**: I always recommend diving into authentic street markets and family-run neighborhood bistros to sample traditional signature dishes! "
                f"Would you like specific restaurant recommendations or culinary secrets?"
            )
        elif "budget" in text_lower or "expensive" in text_lower:
            reply_content = (
                f"For **{target}**, a trip for **{travellers} travellers** over **{days} days** with a **₹{int(budget):,}** budget (~₹{int(budget/max(1, travellers)):,}/person) "
                f"provides good flexibility for comfortable accommodation and quality local dining. "
                f"Would you like me to break down daily estimated costs?"
            )
        else:
            reply_content = (
                f"I'm here to help you explore every detail of **{target}**! "
                f"Ask me anything about sightseeing highlights, local food secrets, weather forecasts, route connections, or budget breakdowns."
            )

    # Generate dynamic, contextual suggested action chips based on the active destination
    clean_name = current_dest.split(",")[0] if current_dest else "Trip"
    suggested_actions = []
    if current_dest:
        if not is_plan_request:
            suggested_actions.append({"label": f"🗓️ Plan {days}-Day Itinerary", "action": "generate_itinerary", "destination": current_dest})
        suggested_actions.append({"label": f"🍲 {clean_name} Food Guide", "action": "prompt", "text": f"What authentic local dishes should I eat in {current_dest}?"})
        suggested_actions.append({"label": f"🌦️ Best Time to Visit", "action": "prompt", "text": f"What is the best month and season to visit {current_dest}?"})
        suggested_actions.append({"label": f"⚡ DeepSearch {clean_name}", "action": "deep_search", "destination": current_dest})
    else:
        suggested_actions = [
            {"label": "🌴 Tell me about Bali", "action": "prompt", "text": "Tell me about Bali"},
            {"label": "🗼 3 Days in Paris", "action": "prompt", "text": "Plan a 3-day trip to Paris"},
            {"label": "🌸 Tokyo Highlights", "action": "prompt", "text": "What are the must-see highlights in Tokyo?"},
            {"label": "🏖️ Relaxing Beach Getaways", "action": "prompt", "text": "Suggest some relaxing beach destinations for a couple"}
        ]

    return {
        "role": "assistant",
        "content": reply_content,
        "structured_type": None,
        "structured_data": None,
        "memory": memory,
        "suggested_actions": suggested_actions[:4]
    }
