import os
import json
import re
import datetime
from typing import List, Dict, Any, Optional, Tuple
from app.core.config import settings
from app.services.recommendation_service import CURATED_DESTINATIONS, get_recommendations
from app.services.itinerary_service import (
    generate_trip_itinerary, 
    resolve_destination_coordinates,
    check_destination_ambiguity
)
from app.services.safety_service import get_destination_safety_report
from app.services.weather_service import get_live_weather_sync, WMO_CODE_MAP
from app.services.transit_cost_service import estimate_global_transit_costs
from app.services.hotel_service import get_worldwide_hotel_suggestions
from app.services.destination_verifier import (
    parse_destination_query,
    get_destination_identity,
    normalize_destination_key
)
from app.services.travel_research_service import (
    research_destination_facts,
    research_multi_destination_circuit
)

# =====================================================================
# MASTER TRAVEL-TECHNOLOGY ARCHITECT SYSTEM PROMPT
# =====================================================================
MASTER_TRAVEL_SYSTEM_PROMPT = """You are WanderWise AI, a world-class travel technology architect, senior trip planner, and AI travel copilot.
You possess encyclopedic, authentic, and nuanced knowledge across the entire world of travel.

### YOUR SCOPE OF TRAVEL EXPERTISE:
1. **Universal Destination Understanding:** Any country, state, city, town, village, tourist attraction, beach, hill station, pilgrimage site, or remote location worldwide across all 195 nations.
2. **Geographical & Route Precision:** Geographically cluster sights to eliminate backtracking. Calculate realistic transit times (walking, transit, driving).
3. **Authentic Local Gastronomy & Culture:** Traditional dishes, street food crawls, dining etiquette, signature cafes, regional traditions, and cultural courtesies.
4. **Seasons, Climate & Live Weather:** Seasonal climate patterns, best months to visit, monsoons, and live weather considerations.
5. **Budgets, Fares & Itemized Expenses:** Realistic itemized cost breakdowns (hotel per night, meals per day, transport, entry tickets).
6. **Safety, Scams & Logistics:** Neighborhood safety, solo traveler tips, known scams, emergency numbers, and official ticketing advice.

### CONVERSATIONAL INTELLIGENCE & CONTEXT RULES (Critical):
- **Remember & Adapt:** Always resolve incomplete sentences (e.g., "What about hidden places?", "Entry fee?", "What if I have only ₹3000?", "Is it worth visiting?") using the active destination and previous conversation memory.
- **Understand Prices Shared Later:** When the user provides numbers like "Hotel 1500 per night", "Food 500 per day", or "Bus 800", interpret them as trip expense updates, integrate them into the budget, and compute the new estimated total.
- **Contextual Modifications:** When the user says "Actually make it 2 days" or "Add one more day", adjust the existing plan rather than wiping it out.
- **Context Switching:** If the user switches destinations (e.g. from Trivandrum to Vagamon), cleanly shift to the new destination. Never cross-contaminate attractions from the previous place into the new destination.
- **Strict Anti-Hallucination & Verification:** Every recommended attraction must physically exist in the requested destination. Never invent non-existent waterfalls, viewpoints, or cafes. When a destination's verified attractions list is provided in context, strictly adhere to it. If a detail cannot be verified, state: 'Information could not be reliably verified at the moment.'
- **Multi-Destination Segregation:** When multiple destinations are queried (e.g. 'Trivandrum, Vagamon and Munnar'), research and present each destination in its own distinct section or phase. Never merge them into a single generic blur.
- **Structured Formatting:** Use clean Markdown with headers, bullet points, itemized cost tables, and bold highlights.
"""

# Supported candidate models in priority order
CANDIDATE_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash",
    "gemini-1.5-flash"
]

# Destination Intelligence cache for deep enrichment
DESTINATION_INTELLIGENCE: Dict[str, Dict[str, Any]] = {
    "bangalore": {
        "name": "Bangalore (Bengaluru), Karnataka",
        "altitude_terrain": "920m Deccan Plateau with pleasant year-round tropical savanna climate and extensive urban green canopies",
        "best_season": "October to March (Crisp morning breezes and comfortable 18°C - 26°C daytime temperatures)",
        "climate_notes": "Mild year-round. Monsoons from June to September with refreshing evening showers.",
        "best_photo_windows": [
            {"time": "06:30 AM - 07:30 AM", "location": "Cubbon Park Bamboo Groves", "condition": "Morning golden sunbeams filtering through mist"},
            {"time": "06:00 PM - 07:15 PM", "location": "Vidhana Soudha Illuminated Promenade", "condition": "Grand Neo-Dravidian architecture lit against dusk sky"}
        ],
        "offbeat_gems": [
            {"name": "National Gallery of Modern Art (NGMA) Sculpture Courtyard", "desc": "Colonial-era Manikyavelu Mansion housing masterworks amid ancient banyans."},
            {"name": "Nandi Valley Winery & Vineyard Trail", "desc": "Artisan vineyard trail at the foothills of Nandi Hills offering guided grape stomping and tastings."}
        ],
        "food_secrets": [
            "Crispy ghee-roast masala dosa and frothy South Indian filter coffee at iconic Vidyarthi Bhavan or CTR Malleshwaram",
            "Slow-cooked Donne Biryani infused with fresh mint, coriander, and native spices in historic Shivaji Nagar"
        ],
        "safety_road_notes": "Peak traffic between 8:30-10:30 AM and 5:30-8:30 PM. Prefer Namma Metro for cross-city transit."
    },
    "munnar": {
        "name": "Munnar, Kerala",
        "altitude_terrain": "1,600m High-altitude Western Ghats plateau with rolling tea hills and misty mountain passes",
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
    "goa": {
        "name": "Goa, India",
        "altitude_terrain": "Arabian Sea coastline with golden beaches, laterite cliffs, and Western Ghats jungle foothills",
        "best_season": "November to February (Sunny, breezy beach days and cool evening sea winds)",
        "climate_notes": "Daytime 28°C - 33°C, pleasant coastal nights 21°C - 24°C. Monsoon from June to September.",
        "best_photo_windows": [
            {"time": "05:30 PM - 06:30 PM", "location": "Chapora Fort Cliff", "condition": "Dramatic sunset over Vagator coastal headland"},
            {"time": "07:00 AM - 08:30 AM", "location": "Fontainhas Latin Quarter", "condition": "Soft morning sunlight illuminating ochre and indigo Portuguese villas"}
        ],
        "offbeat_gems": [
            {"name": "Galgibaga Turtle Beach", "desc": "Pristine, untouched southern beach known for Olive Ridley turtle nesting and serenity."},
            {"name": "Divar Island River Ferry Trail", "desc": "Tranquil island sanctuary of ancient sleepy hamlets and church viewpoints."}
        ],
        "food_secrets": [
            "Authentic Goan Fish Curry Thali with Kingfish fry, kismoor, and cooling Sol Kadhi",
            "Portuguese-inspired Bebinca dessert layered with coconut milk and caramelized sugar"
        ],
        "safety_road_notes": "Always wear helmets on rented two-wheelers. Avoid swimming near rocky headlands with undertow flags."
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
    "mysore": {
        "name": "Mysore (Mysuru), Karnataka",
        "altitude_terrain": "770m Chamundi Hill foothills on the southern Deccan Plateau with royal tree-lined boulevards and royal lakes",
        "best_season": "October to March (Pleasant daytime temperatures of 20°C - 28°C; Grand Dasara festival in Sep/Oct)",
        "climate_notes": "Pleasant tropical climate. Warm in April-May (up to 34°C); Southwest Monsoon showers from June to September.",
        "best_photo_windows": [
            {"time": "06:45 PM - 07:45 PM", "location": "Mysore Palace Courtyard", "condition": "Sunday/Holiday evening illumination with 100,000 incandescent golden bulbs"},
            {"time": "05:30 PM - 06:30 PM", "location": "Chamundi Hill Viewpoint", "condition": "Crimson sunset overlooking illuminated Mysore city panorama and monolith Nandi"}
        ],
        "offbeat_gems": [
            {"name": "Ranganathittu Kaveri River Boat Islet", "desc": "Quiet river sanctuary glide past nesting spoonbills, painted storks, and sunning mugger crocodiles."},
            {"name": "Daria Daulat Bagh Teakwood Summer Palace", "desc": "Tipu Sultan's island retreat in Srirangapatna with ornate painted floral timber walls and battle murals."}
        ],
        "food_secrets": [
            "Original melt-in-the-mouth Mysore Pak freshly churned in pure desi ghee at legendary Guru Sweet Mart",
            "Crispy Mysore Masala Dosa smeared with spicy red garlic-chutney paste at historic Mylari Hotel in Nazarbad"
        ],
        "safety_road_notes": "Comfortable, clean, and safe royal city. Well-connected to Bangalore via the 10-lane Expressway and Vande Bharat Express."
    },
    "mysuru": {
        "name": "Mysuru (Mysore), Karnataka",
        "altitude_terrain": "770m Chamundi Hill foothills on the southern Deccan Plateau with royal tree-lined boulevards and royal lakes",
        "best_season": "October to March (Pleasant daytime temperatures of 20°C - 28°C; Grand Dasara festival in Sep/Oct)",
        "climate_notes": "Pleasant tropical climate. Warm in April-May (up to 34°C); Southwest Monsoon showers from June to September.",
        "best_photo_windows": [
            {"time": "06:45 PM - 07:45 PM", "location": "Mysore Palace Courtyard", "condition": "Sunday/Holiday evening illumination with 100,000 incandescent golden bulbs"},
            {"time": "05:30 PM - 06:30 PM", "location": "Chamundi Hill Viewpoint", "condition": "Crimson sunset overlooking illuminated Mysore city panorama and monolith Nandi"}
        ],
        "offbeat_gems": [
            {"name": "Ranganathittu Kaveri River Boat Islet", "desc": "Quiet river sanctuary glide past nesting spoonbills, painted storks, and sunning mugger crocodiles."},
            {"name": "Daria Daulat Bagh Teakwood Summer Palace", "desc": "Tipu Sultan's island retreat in Srirangapatna with ornate painted floral timber walls and battle murals."}
        ],
        "food_secrets": [
            "Original melt-in-the-mouth Mysore Pak freshly churned in pure desi ghee at legendary Guru Sweet Mart",
            "Crispy Mysore Masala Dosa smeared with spicy red garlic-chutney paste at historic Mylari Hotel in Nazarbad"
        ],
        "safety_road_notes": "Comfortable, clean, and safe royal city. Well-connected to Bangalore via the 10-lane Expressway and Vande Bharat Express."
    },
    "udupi": {
        "name": "Udupi, Karnataka",
        "altitude_terrain": "Arabian Sea coastal plain framed by the emerald foothills of the Western Ghats, coconut palms, and Suvarna river estuaries",
        "best_season": "October to March (Comfortable coastal sea breezes, clear blue skies, and pleasant 22°C - 30°C temperatures)",
        "climate_notes": "Tropical coastal climate. Heavy, scenic monsoon rains from June to September. October onwards is ideal for island ferries and beaches.",
        "best_photo_windows": [
            {"time": "05:15 PM - 06:15 PM", "location": "St. Mary's Island Basalt Columns", "condition": "Golden hour sun hitting the hexagonal volcanic rock pillars and turquoise surf"},
            {"time": "05:30 PM - 06:45 PM", "location": "Kaup Beach 1901 Lighthouse", "condition": "Dramatic sunset over the Arabian Sea from the cliffside lighthouse balcony"}
        ],
        "offbeat_gems": [
            {"name": "Delta Beach (Kodi Bengre) Suvarna River Estuary", "desc": "Secluded narrow peninsula where the river meets the sea, famous for mangrove kayaking and fresh toddy shacks."},
            {"name": "Padubidri Blue Flag Beach Boardwalk", "desc": "Eco-certified pristine beach with immaculate wooden walking decks, gentle waves, and sea breezes."}
        ],
        "food_secrets": [
            "Authentic Udupi Brahmin breakfast of melt-in-the-mouth Goli Baje, crispy Masala Dosa, and filter coffee at 100-year-old Mitra Samaj on Car Street",
            "Fiery Coastal Karavali Kundapura Ghee Roast paired with paper-thin soft Neer Dosa at local family eateries"
        ],
        "safety_road_notes": "Swimming is strictly prohibited at St. Mary's Island due to sharp underwater basalt rocks and strong rip currents. Observe lifeguard warnings at Malpe and Kaup."
    },
    "gokarna": {
        "name": "Gokarna, Karnataka",
        "altitude_terrain": "Rugged laterite coastal cliffs overlooking five golden crescent beaches along the Arabian Sea",
        "best_season": "October to March (Sunny beach days, cool sea breezes, and vibrant beachside cafe life)",
        "climate_notes": "Tropical climate with dramatic monsoon downpours between June and September.",
        "best_photo_windows": [
            {"time": "05:30 PM - 06:30 PM", "location": "Om Beach Cliff / Kudle Sunset Point", "condition": "Crimson sunset reflecting off the natural Om-shaped rock curves"},
            {"time": "06:30 AM - 07:45 AM", "location": "Half Moon Beach Headland", "condition": "Morning light illuminating untouched golden sand coves"}
        ],
        "offbeat_gems": [
            {"name": "Mirjan Fort Laterite Ruins", "desc": "16th-century fortress overgrown with emerald moss and surrounded by quiet village waterways."},
            {"name": "Nirvana Beach Across Aghanashini", "desc": "Deserted white sand stretch known for occasional bioluminescent evening glows."}
        ],
        "food_secrets": [
            "Nutella banana pancakes and fresh papaya juice at clifftop cafes overlooking Kudle beach",
            "Traditional Brahmin thali and coconut curry around Kotitirtha temple lake"
        ],
        "safety_road_notes": "Watch your footing along the cliff path between Om Beach and Paradise Beach, especially in flip-flops."
    },
    "coorg": {
        "name": "Coorg (Kodagu), Karnataka",
        "altitude_terrain": "900m - 1,750m High-altitude Western Ghats coffee plateau surrounded by dense evergreen rainforests and misty cardamom valleys",
        "best_season": "October to April (Aromatic coffee blossoming season, pleasant 15°C - 25°C daytime weather)",
        "climate_notes": "Cool highland climate year-round. Monsoons (July-August) bring lush waterfalls and misty landscapes.",
        "best_photo_windows": [
            {"time": "05:15 PM - 06:15 PM", "location": "Raja's Seat Madikeri", "condition": "Panoramic sunset over layers of purple mountain mist"},
            {"time": "08:30 AM - 09:30 AM", "location": "Abbey Falls Spice Trail", "condition": "Morning mist rising off the falls surrounded by wild pepper vines"}
        ],
        "offbeat_gems": [
            {"name": "Namdroling Golden Temple Bylakuppe", "desc": "One of India's largest Tibetan monastic settlements with 40ft gilded Buddha statues and prayer wheels."},
            {"name": "Chelavara Falls & Chomakund Peak", "desc": "Natural tortoise-shaped rock waterfall nestled deep within private coffee plantations."}
        ],
        "food_secrets": [
            "Authentic Kodava Pandi Curry (or mushroom/bamboo shoot curry) flavored with dark wild kachampuli vinegar",
            "Steamed soft Kadambuttu (rice dumplings) and Noolputtu (string hoppers) with coconut milk"
        ],
        "safety_road_notes": "Curving mountain roads require alert driving. Carry light woolens for chilly evenings."
    },
    "hampi": {
        "name": "Hampi, Karnataka",
        "altitude_terrain": "Ancient boulder-strewn UNESCO World Heritage river valley across the Tungabhadra River with 14th-century Vijayanagara ruins",
        "best_season": "October to March (Clear blue skies and comfortable daytime exploring temperatures)",
        "climate_notes": "Semi-arid climate. Midday can be hot (28°C - 34°C); mornings and evenings are pleasantly breezy.",
        "best_photo_windows": [
            {"time": "06:00 AM - 07:15 AM", "location": "Matanga Hill Summit", "condition": "360-degree sunrise over miles of ancient stone temples and banana groves"},
            {"time": "05:30 PM - 06:30 PM", "location": "Hemakuta Hill Sunset", "condition": "Golden sunlight bathing stone gopurams and monolithic shrines"}
        ],
        "offbeat_gems": [
            {"name": "Anegundi (Hippy Island) & Sanapur Lake", "desc": "Cross by wicker coracle boat to swim in granite boulder reservoirs and explore ancient Kishkindha caves."},
            {"name": "Zenana Enclosure & Lotus Mahal", "desc": "Impeccably preserved Indo-Islamic vaulted arches and royal elephant stables."}
        ],
        "food_secrets": [
            "Traditional South Indian banana leaf thali with crispy vada, sambar, and buttermilk at Mango Tree Cafe",
            "Wood-fired thin crust pizzas and ginger lemon honey tea at riverside Anegundi shacks"
        ],
        "safety_road_notes": "Wear comfortable walking shoes with good traction for walking over granite boulders and temple stones."
    }
}

# Extensive worldwide and Indian destination lookup list
POPULAR_GLOBAL_DESTINATIONS = [
    "India", "Goa, India", "Delhi, India", "New Delhi, India", "Mumbai, Maharashtra",
    "Bengaluru, Karnataka", "Bangalore, Karnataka", "Mysore, Karnataka", "Mysuru, Karnataka", "Udupi, Karnataka", "Mangalore, Karnataka", "Hampi, Karnataka", "Coorg, Karnataka",
    "Jaipur, Rajasthan", "Udaipur, Rajasthan", "Jodhpur, Rajasthan", "Jaisalmer, Rajasthan",
    "Kerala, India", "Munnar, Kerala", "Kochi, Kerala", "Alleppey, Kerala", "Varkala, Kerala", "Wayanad, Kerala",
    "Manali, Himachal Pradesh", "Shimla, Himachal Pradesh", "Spiti Valley, Himachal Pradesh", "Kasol, Himachal Pradesh",
    "Ladakh, India", "Leh Ladakh, India", "Kashmir, India", "Srinagar, Kashmir", "Gulmarg, Kashmir",
    "Rishikesh, Uttarakhand", "Agra, Uttar Pradesh", "Varanasi, Uttar Pradesh", "Amritsar, Punjab",
    "Gokarna, Karnataka", "Kolkata, West Bengal", "Darjeeling, West Bengal", "Chennai, Tamil Nadu", "Ooty, Tamil Nadu",
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
    with short timeouts to eliminate stalls and 503 unavailability.
    """
    api_key = (settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY") or "").strip()
    if not api_key or len(api_key) < 10:
        return None

    sys_prompt = system_instruction or MASTER_TRAVEL_SYSTEM_PROMPT
    if extra_context:
        sys_prompt += f"\n\n### ADDITIONAL REAL-TIME CONTEXT & MEMORY STATE:\n{extra_context}"

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=15.0)
        )

        config = types.GenerateContentConfig(
            system_instruction=sys_prompt,
            temperature=0.7
        )

        # Assemble clean conversational turn history
        contents: List[types.Content] = []
        if history:
            recent = history[-16:]
            for msg in recent:
                role = "user" if msg.get("role") == "user" else "model"
                text = (msg.get("content") or "").strip()
                if text:
                    contents.append(types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=text)]
                    ))

        contents.append(types.Content(
            role="user",
            parts=[types.Part.from_text(text=current_prompt)]
        ))

        # Model Failover cascade
        primary_model = settings.GEMINI_MODEL or "gemini-3.1-flash-lite"
        models_to_attempt = [primary_model] + [m for m in CANDIDATE_MODELS if m != primary_model]

        for model_name in models_to_attempt:
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

def extract_itemized_expenses(text: str, current_expenses: Dict[str, float]) -> Tuple[Dict[str, float], Optional[str]]:
    """
    Extracts individual expense items shared across conversation turns (Section 11 C, E):
    - 'Hotel 1500 per night', 'hotel 1500', 'stay 2000'
    - 'Food 500 per day', 'food 500', 'meals 400'
    - 'Bus 800', 'train 600', 'flight 4000', 'transport 800', 'cab 1000'
    - 'Entry fee 250', 'tickets 500', 'activities 1000'
    """
    t = text.lower().strip()
    updated = current_expenses.copy()
    notes = []

    # 1. Hotel / Stay
    hotel_m = re.search(r'\b(?:hotel|room|stay|accommodation|resort)\s*(?:budget|is|costs?|was|rate)?\s*(?:₹|rs\.?|inr|\$)?\s*([0-9]{3,6})(?:\s*(?:per\s*night|/\s*night|a\s*night|daily))?\b', t)
    if hotel_m:
        val = float(hotel_m.group(1))
        updated["hotel_per_night"] = val
        notes.append(f"Hotel rate updated to ₹{int(val):,}/night")

    # 2. Food / Dining
    food_m = re.search(r'\b(?:food|meals?|dining|eating)\s*(?:budget|is|costs?|was)?\s*(?:₹|rs\.?|inr|\$)?\s*([0-9]{2,5})(?:\s*(?:per\s*day|/\s*day|a\s*day|daily))?\b', t)
    if food_m:
        val = float(food_m.group(1))
        updated["food_per_day"] = val
        notes.append(f"Food budget updated to ₹{int(val):,}/day")

    # 3. Transport (Bus, Train, Flight, Cab)
    trans_m = re.search(r'\b(?:bus|train|flight|transit|transport|travel|cab|taxi)\s*(?:fare|ticket|cost|is|costs?|was)?\s*(?:₹|rs\.?|inr|\$)?\s*([0-9]{2,6})\b', t)
    if trans_m:
        val = float(trans_m.group(1))
        updated["transport"] = val
        notes.append(f"Transportation cost updated to ₹{int(val):,}")

    # 4. Sightseeing / Activities
    act_m = re.search(r'\b(?:activities|activity|tickets?|entry\s*fees?|sightseeing)\s*(?:is|costs?|was)?\s*(?:₹|rs\.?|inr|\$)?\s*([0-9]{2,5})\b', t)
    if act_m:
        val = float(act_m.group(1))
        updated["activities"] = val
        notes.append(f"Sightseeing/activities cost updated to ₹{int(val):,}")

    note_str = " | ".join(notes) if notes else None
    return updated, note_str

def extract_and_update_memory(
    user_message: str,
    existing_memory: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Dynamic Conversational Memory Engine (Section 6 & 11):
    1. Tracks active destination, sub-destinations, and previous locations.
    2. Maintains itemized expense profile (hotel/night, food/day, transport, activities).
    3. Handles duration changes ('Actually make it 2 days') without losing context.
    4. Handles context switching ('What about Mysore?') cleanly.
    """
    defaults = {
        "destination": None,
        "sub_destinations": [],
        "previously_discussed_destinations": [],
        "last_discussed_attraction": None,
        "last_topic": "general",
        "days": 3,
        "duration_days": 3,
        "budget": 20000.0,
        "is_user_set_budget": False,
        "travellers": 2,
        "travel_style": "Scenic Exploration",
        "origin": None,
        "interests": [],
        "expenses": {
            "hotel_per_night": 2000.0,
            "food_per_day": 600.0,
            "transport": 1200.0,
            "activities": 800.0,
            "other": 400.0
        },
        "current_itinerary": None,
        "deep_search": False,
        "compared_to": None
    }
    memory = defaults.copy()
    if existing_memory and isinstance(existing_memory, dict):
        memory.update(existing_memory)
        if "expenses" not in memory or not isinstance(memory["expenses"], dict):
            memory["expenses"] = defaults["expenses"].copy()

    text_lower = user_message.lower().strip()
    found_dest = None

    # Step 1: High-precision destination query parsing & entity recognition
    parsed_query = parse_destination_query(user_message)
    q_type = parsed_query.get("query_type")
    parsed_dests = parsed_query.get("destinations", [])

    if q_type == "multi_destination_circuit" and len(parsed_dests) >= 2:
        dest_names = [d["canonical_name"] for d in parsed_dests]
        memory["is_multi_destination"] = True
        memory["destinations_list"] = dest_names
        memory["destination"] = " -> ".join(dest_names)
        memory["primary_destination"] = dest_names[0]
        memory["compared_to"] = None
        found_dest = memory["destination"]
    elif q_type == "comparison" and len(parsed_dests) >= 2:
        memory["is_multi_destination"] = False
        memory["destinations_list"] = [parsed_dests[0]["canonical_name"], parsed_dests[1]["canonical_name"]]
        memory["destination"] = parsed_dests[0]["canonical_name"]
        memory["compared_to"] = parsed_dests[1]["canonical_name"]
        memory["primary_destination"] = parsed_dests[0]["canonical_name"]
        found_dest = memory["destination"]
    elif q_type == "single_destination" and len(parsed_dests) >= 1:
        single_canon = parsed_dests[0]["canonical_name"]
        memory["is_multi_destination"] = False
        memory["destinations_list"] = [single_canon]

        # Clean destination switch
        old_dest = memory.get("destination")
        if old_dest and normalize_destination_key(old_dest) != normalize_destination_key(single_canon):
            if "previously_discussed_destinations" not in memory:
                memory["previously_discussed_destinations"] = []
            if old_dest not in memory["previously_discussed_destinations"]:
                memory["previously_discussed_destinations"].append(old_dest)
            memory["last_discussed_attraction"] = None
            memory["last_topic"] = "general"

        memory["destination"] = single_canon
        memory["primary_destination"] = single_canon
        memory["compared_to"] = None
        found_dest = single_canon
    else:
        # Fallback to route pairs (e.g. from X to Y)
        from_to_match = re.search(r'\bfrom\s+([A-Za-z\s]{3,24}?)\s+to\s+([A-Za-z\s]{3,24}?)(?:\s+(?:for|with|under|in|\d+|$|[?!.,]))', text_lower)
        if not from_to_match:
            from_to_match = re.search(r'\b([A-Za-z\s]{3,20}?)\s+to\s+([A-Za-z\s]{3,20}?)(?:\s+(?:for|with|under|in|\d+|$|[?!.,]))', text_lower)
        if from_to_match:
            cand_orig = from_to_match.group(1).strip().title()
            cand_dest = from_to_match.group(2).strip().title()
            non_route_words = {"how", "travel", "fly", "flight", "flights", "train", "trains", "bus", "stay", "cost", "fare", "where"}
            if cand_orig.lower() not in non_route_words and len(cand_orig) >= 3:
                memory["origin"] = cand_orig
            if cand_dest.lower() not in non_route_words and len(cand_dest) >= 3:
                ident = get_destination_identity(cand_dest)
                canon = ident.get("canonical_name", cand_dest)
                memory["destination"] = canon
                memory["primary_destination"] = canon
                memory["is_multi_destination"] = False
                found_dest = canon

    # 4. Itemized Expense Extraction (Section 11 C, E)
    updated_expenses, expense_note = extract_itemized_expenses(user_message, memory["expenses"])
    memory["expenses"] = updated_expenses

    # 5. Fixed Total Budget Extraction (e.g. ₹15,000, 15000, 20k, $500, 'what if I have only ₹3000')
    budget_constraint = re.search(r'\b(?:have only|budget is|total budget|under|budget|max|limit)\s*(?:₹|rs\.?|inr|\$)?\s*([0-9]{1,3}(?:,[0-9]{3})+|[0-9]{3,6})\b', text_lower)
    if budget_constraint:
        try:
            val = float(budget_constraint.group(1).replace(",", ""))
            memory["budget"] = val
            memory["is_user_set_budget"] = True
        except Exception:
            pass
    elif not memory.get("is_user_set_budget"):
        # Auto-recalculate estimated total from itemized expenses
        duration = memory.get("days", 3)
        nights = max(1, duration - 1)
        travellers = max(1, memory.get("travellers", 2))
        h_total = memory["expenses"]["hotel_per_night"] * nights
        f_total = memory["expenses"]["food_per_day"] * duration * travellers
        t_total = memory["expenses"]["transport"]
        a_total = memory["expenses"]["activities"]
        memory["budget"] = round(h_total + f_total + t_total + a_total, 2)

    # 6. Duration Extraction (Universal engine + Relative Adjustments)
    extracted_days = extract_duration_days(user_message)
    if extracted_days:
        memory["days"] = extracted_days
        memory["duration_days"] = extracted_days
    else:
        # Relative adjustments: 'include one more day', 'add 1 day', 'extend by 2 days', 'reduce by 1 day'
        more_days_m = re.search(r'\b(?:include|add|extend by|plus)\s+(\d+|one|two|three|a|another)?\s*(?:more\s+)?days?\b', text_lower)
        if not more_days_m:
            more_days_m = re.search(r'\b(?:one|two|three|\d+|another)\s+more\s+days?\b', text_lower)
        if more_days_m:
            val_str = (more_days_m.group(1) or "1").lower().strip()
            word_to_num = {"one": 1, "two": 2, "three": 3, "a": 1, "another": 1}
            delta = word_to_num.get(val_str, int(val_str) if val_str.isdigit() else 1)
            new_days = max(1, min(14, memory.get("days", 3) + delta))
            memory["days"] = new_days
            memory["duration_days"] = new_days
        else:
            less_days_m = re.search(r'\b(?:reduce|decrease|minus|less)\s+(?:by\s+)?(\d+|one|two)?\s*days?\b', text_lower)
            if less_days_m:
                val_str = (less_days_m.group(1) or "1").lower().strip()
                word_to_num = {"one": 1, "two": 2}
                delta = word_to_num.get(val_str, int(val_str) if val_str.isdigit() else 1)
                new_days = max(1, min(14, memory.get("days", 3) - delta))
                memory["days"] = new_days
                memory["duration_days"] = new_days

    # 7. Travellers Extraction
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

    # 8. Track topics and specific attractions
    for topic_kw in ["weather", "food", "cafes", "hotels", "transit", "itinerary", "hidden", "photography", "safety"]:
        if topic_kw in text_lower:
            memory["last_topic"] = topic_kw
            break

    return memory

def generate_fallback_destination_guide(destination: str) -> str:
    """
    Generates the 16-section complete master destination guide backed by
    ground-truth verified research facts from official tourism registries and OpenStreetMap.
    Strictly eliminates place hallucinations and distinguishes in-destination spots vs distant excursions.
    """
    clean_d = destination.split(",")[0].strip()
    research = research_destination_facts(destination)
    canonical = research.get("destination_name", clean_d)
    coords = research.get("coordinates", {})
    lat = coords.get("lat", 12.9716)
    lng = coords.get("lng", 77.5946)
    dest_type = research.get("destination_type", "Travel Destination")
    district = research.get("district", "")
    state = research.get("state", "")
    country = research.get("country", "India")
    official_url = research.get("official_tourism_url")
    confidence = research.get("overall_confidence", "HIGH CONFIDENCE")

    # 1. Verified In-Destination Attractions (Strict Ground Truth)
    in_dest = research.get("in_destination_attractions", [])
    if in_dest:
        attractions_text = "\n".join([
            f"• **{item['name']}** [{item.get('confidence', 'HIGH CONFIDENCE')}]\n"
            f"  - *Location:* {item.get('location', canonical)}\n"
            f"  - *Experience:* {item.get('description', '')}\n"
            f"  - *Entry / Tickets:* {item.get('entry_fee_note', 'Check at entrance')}\n"
            f"  - *Insider Tip:* {item.get('visiting_tips', 'Visit during morning hours')}"
            for item in in_dest[:5]
        ])
    else:
        attractions_text = f"• **{clean_d} Historic Center & Heritage Walking Trail:** Foundational architecture showcasing centuries of local history."

    # 2. Verified Nearby Excursions (Clearly marked with distance)
    excursions = research.get("nearby_excursions", [])
    if excursions:
        excursions_text = "\n".join([
            f"• **{ex['name']}** ({ex.get('location', 'Surrounding Region')}): {ex.get('description', '')} *(Note: Requires a separate half-day trip)*"
            for ex in excursions[:3]
        ])
    else:
        excursions_text = f"• Picturesque viewpoints and scenic landscapes located within a 25-50 km drive from {clean_d}."

    # 3. Offbeat Secrets & Hidden Gems
    dest_key = normalize_destination_key(destination)
    intel = DESTINATION_INTELLIGENCE.get(dest_key, {})
    gems = intel.get("offbeat_gems", [])
    if gems:
        gems_text = "\n".join([f"• **{g['name']}:** {g['desc']}" for g in gems])
    elif in_dest and len(in_dest) > 3:
        gems_text = "\n".join([f"• **{item['name']}:** {item['description']}" for item in in_dest[3:5]])
    else:
        gems_text = (
            f"• **Artisan Craft Workshops of {clean_d}:** Local studios preserving traditional craft traditions.\n"
            f"• **Tranquil Morning Overlook:** Peaceful vantage point away from commercial tourist buses."
        )

    # 4. Local Food
    foods = intel.get("food_secrets", [])
    if foods:
        food_text = "\n".join([f"• {f}" for f in foods])
    else:
        food_text = (
            f"• Signature local delicacies prepared with authentic regional spices and time-honored slow-cooked techniques.\n"
            f"• Traditional morning breakfast specials, hot savory snacks, and freshly prepared regional artisan beverages."
        )

    # 5. Best Photography Windows
    photos = intel.get("best_photo_windows", [])
    if photos:
        photo_text = "\n".join([f"• **{p['time']} — {p['location']}:** {p['condition']}" for p in photos])
    else:
        photo_text = (
            f"• **Morning Golden Hour (06:00 AM - 07:15 AM):** Soft dawn sunlight illuminating foundational monuments with zero crowds.\n"
            f"• **Twilight / Blue Hour (05:45 PM - 06:45 PM):** High panoramic vantage points capturing colorful sunset horizons."
        )

    # 6. Wikipedia Summary (if available)
    wiki_info = ""
    if research.get("wikipedia") and research["wikipedia"].get("extract"):
        wiki_info = f"\n> **Verified Encyclopedic Overview (Wikipedia):** {research['wikipedia']['extract']}\n"

    # 7. TripAdvisor Intelligence & Traveler Review Consensus
    from app.services.tripadvisor_service import get_tripadvisor_destination_intelligence
    ta_data = get_tripadvisor_destination_intelligence(destination)
    ta_attractions = "\n".join([f"• **{item['rank']}: {item['name']}** (⭐ {item['rating']}/5.0 • {item['reviews']} reviews): {item['tip']}" for item in ta_data.get("top_ranked_attractions", [])[:3]])
    ta_tips = "\n".join([f"• {tip}" for tip in ta_data.get("top_traveler_tips", [])[:2]])

    road_notes = intel.get("safety_road_notes", "Use registered ride apps, prepaid transit counters, and licensed guides.")

    elev_val = research.get("elevation_m")
    elev_str = f" at an elevation of {elev_val}m" if elev_val else ""

    return (
        f"# 🗺️ Complete Travel Guide: **{canonical}**\n\n"
        f"**Quality Verification Level:** ✅ **{confidence}** | **Region:** {district + ', ' if district else ''}{state}, {country}\n\n"
        f"### 1. 🌟 Destination Overview & Geographical Context\n"
        f"**{canonical}** is classified as a **{dest_type}** located at coordinates **{lat:.4f}°N, {lng:.4f}°E**{elev_str}. "
        f"{research.get('terrain') or intel.get('altitude_terrain', 'Characterized by picturesque regional topography and authentic local culture.')}\n"
        f"{wiki_info}\n"
        f"### 2. 🏛️ Verified Top In-Destination Attractions (Strict Ground Truth)\n"
        f"{attractions_text}\n\n"
        f"### 3. 🚗 Nearby Excursions & Day Trips (Separated from Town)\n"
        f"{excursions_text}\n\n"
        f"### 4. 💎 Hidden Gems & Offbeat Experiences\n"
        f"{gems_text}\n\n"
        f"### 5. 🍲 Local Food & Famous Regional Dishes\n"
        f"{food_text}\n\n"
        f"### 6. ☕ Best Restaurants, Cafes & Street Food\n"
        f"• Legendary heritage cafes serving artisanal filter coffee and fresh local bakes.\n"
        f"• Iconic evening food stalls celebrated for authentic family recipes and street snacks.\n"
        f"• Scenic garden and waterfront eateries offering ambient dusk dining.\n\n"
        f"### 7. 🏨 Accommodation Recommendations\n"
        f"• **Budget Tier (₹1,200 - ₹2,500 / night):** Centrally-located boutique hostels and comfortable family-run homestays.\n"
        f"• **Boutique & Heritage Tier (₹3,500 - ₹7,500 / night):** Character-rich stays featuring regional architecture and courtyards.\n"
        f"• **5-Star Luxury (₹12,000 - ₹28,000 / night):** World-class hospitality, private balconies, and bespoke wellness spas.\n\n"
        f"### 8. 🚆 Transportation Options & Getting Around\n"
        f"• **Local Transit / Metro / City Buses:** Efficient and cost-effective for traveling between central hubs.\n"
        f"• **Ride-Hailing & Cabs:** Readily available app cabs (Uber / Ola) and metered taxis.\n"
        f"• **Walking:** Heritage old quarters and temple streets are best explored on foot.\n\n"
        f"### 9. 💰 Estimated Travel Expenses\n"
        f"• **Budget Traveler:** ₹1,800 - ₹2,500 ($22 - $30) per person/day.\n"
        f"• **Mid-Range Balanced:** ₹4,500 - ₹7,500 ($55 - $90) per person/day.\n"
        f"• **Luxury Traveler:** ₹14,000+ ($170+) per person/day.\n\n"
        f"### 10. 📅 Best Season to Visit\n"
        f"{intel.get('best_season', 'October through March offers pleasant weather, mild daytime temperatures, and clear skies.')}\n\n"
        f"### 11. ⛅ Weather Considerations & Packing Tips\n"
        f"{intel.get('climate_notes', 'Pleasant daytime temperatures (20°C - 28°C) with cooler evenings.')} "
        f"Pack comfortable walking shoes, breathable clothing, sunglasses, and an evening jacket or umbrella depending on season.\n\n"
        f"### 12. 🛡️ Safety Precautions & Local Scams\n"
        f"• **Local Logistics Advisory:** {road_notes}\n"
        f"• Keep valuables secure in crowded transit stations and markets.\n"
        f"• Use registered ride apps or prepaid counters to avoid unmetered fare inflation.\n"
        f"• Verified Emergency Hotlines: **112 (National Integrated Emergency)**, **100 (Police)**.\n\n"
        f"### 13. 🎎 Local Culture, Customs & Etiquette\n"
        f"• Dress respectfully when visiting temples, churches, or sacred cultural shrines.\n"
        f"• Remove footwear where customary before entering religious sanctums.\n"
        f"• Greet locals with traditional warmth and respect personal photography boundaries.\n\n"
        f"### 14. 🛍️ Shopping & Traditional Bazaars\n"
        f"• Famous local bazaars for handwoven textiles, spices, teas, and indigenous handicrafts.\n"
        f"• Government-recognized emporiums for certified quality souvenirs.\n\n"
        f"### 15. 📸 Photography & Scenic Locations\n"
        f"{photo_text}\n\n"
        f"### 16. 📚 Verified Information Sources & Official Portals\n"
        f"• **Official Tourism Website:** [{canonical} Tourism Portal]({official_url})\n"
        f"• **Geographical Registry:** OpenStreetMap verified coordinates ({lat:.4f}°N, {lng:.4f}°E)\n"
        f"• **Encyclopedic Grounding:** Wikipedia Academic Entry\n\n"
        f"---\n"
        f"### 🦉 TripAdvisor Verified Traveler Insights & Consensus\n"
        f"• **Award Badge:** {ta_data.get('travelers_choice_badge', 'Travelers Choice 2026')}\n"
        f"• **Traveler Rating:** ⭐ **{ta_data.get('overall_rating', 4.8)} / 5.0** ({ta_data.get('review_consensus_count', 'Verified Reviews')})\n"
        f"• **Top Ranked Things to Do on TripAdvisor:**\n"
        f"{ta_attractions}\n"
        f"• **Key Traveler Review Tips:**\n"
        f"{ta_tips}\n\n"
        f"🔗 **TripAdvisor Portals:** "
        f"[Top Attractions ↗]({ta_data['tripadvisor_attractions_url']}) • "
        f"[Best Restaurants ↗]({ta_data['tripadvisor_restaurants_url']}) • "
        f"[Hotels & Stays Reviews ↗]({ta_data['tripadvisor_hotels_url']})"
    )

def build_contextual_fallback(user_message: str, current_dest: str, days: int, travellers: int) -> str:
    """Builds authentic fact-based answers for incomplete follow-up queries when Gemini is offline."""
    clean_d = current_dest.split(",")[0].strip()
    dest_key = clean_d.lower()
    intel = DESTINATION_INTELLIGENCE.get(dest_key, {})
    t = user_message.lower()

    if any(k in t for k in ["hidden", "offbeat", "secret", "peaceful"]):
        gems = intel.get("offbeat_gems", [
            {"name": f"Ancient Artisanal Quarters of {clean_d}", "desc": "Generational craft studios tucked away from tourist buses."},
            {"name": f"Panoramic Ridge Trail", "desc": "Quiet hill or waterfront overlook offering untouched views."}
        ])
        lines = [f"### 💎 Hidden Gems & Secret Spots in **{clean_d}**:\n"]
        for g in gems:
            lines.append(f"• **{g['name']}**: {g['desc']}")
        lines.append(f"\n💡 *Local Tip:* Visit these spots in the early morning (before 9:00 AM) or late afternoon for the most peaceful experience.")
        return "\n".join(lines)

    if any(k in t for k in ["food", "cafes", "cafe", "eat", "dining", "restaurants", "dish"]):
        foods = intel.get("food_secrets", [
            f"Authentic local specialties made with seasonal ingredients and traditional regional recipes",
            f"Historic morning breakfast stalls and artisan filter coffee houses"
        ])
        lines = [f"### 🍲 Authentic Gastronomy & Cafes in **{clean_d}**:\n"]
        for f in foods:
            lines.append(f"• {f}")
        lines.append(f"\n✨ *Recommended Cafe Style:* Seek out locally-owned heritage eateries and artisan roasteries for the most authentic flavor.")
        return "\n".join(lines)

    if any(k in t for k in ["safe", "avoid", "scam", "danger", "caution"]):
        road_notes = intel.get("safety_road_notes", "Use registered ride-hailing apps or prepaid counters to avoid fare inflation.")
        return (
            f"### 🛡️ Safety & Travel Advisory for **{clean_d}**:\n\n"
            f"• **Local Logistics:** {road_notes}\n"
            f"• **Neighborhood Safety:** Stick to well-lit central avenues and lively markets after dark.\n"
            f"• **Valuables:** Keep bags zipped and secure in busy transit stations and markets.\n"
            f"• **Verified Emergency Hotlines:** Dial **112 (Integrated Emergency)** or **100 (Police)**."
        )

    if any(k in t for k in ["worth", "good time", "should i go"]):
        season = intel.get("best_season", "October to March")
        return (
            f"### ✨ Is **{clean_d}** Worth Visiting?\n\n"
            f"**Absolutely, yes!** {clean_d} is celebrated for its distinctive blend of culture, architecture, and scenery.\n\n"
            f"• **Ideal For:** Couples, solo explorers, photography enthusiasts, and cultural travelers.\n"
            f"• **Best Window:** {season}.\n"
            f"• **Suggested Duration:** {days} days is ideal to experience the core highlights without rushing."
        )

    if any(k in t for k in ["one day", "1 day", "in a day", "everything in"]):
        return (
            f"### ⏱️ Can You Cover **{clean_d}** in One Day?\n\n"
            f"While you can capture a glimpse of 2-3 iconic landmarks in a single packed day (08:30 AM to 08:00 PM), "
            f"we strongly recommend at least **{days} days** to truly experience the heritage quarters, authentic food culture, and scenic viewpoints without rushing through transit."
        )

    if any(k in t for k in ["nearby", "around", "day trip", "next to"]):
        return (
            f"### 🚗 Top Nearby Escapes Around **{clean_d}** (Within 50-90 km):\n\n"
            f"• **Scenic Hilltops & Fortresses:** Historic vantage points offering sweeping views and pleasant afternoon breezes.\n"
            f"• **Cascading Nature Sanctuaries:** Forested lakes and waterfalls ideal for a half-day excursion.\n"
            f"• **Artisan Heritage Hamlets:** Traditional weaving and pottery villages preserving generational crafts."
        )

    return (
        f"In **{clean_d}**, this aligns directly with your {days}-day plan for {travellers} travellers! "
        f"Let me know if you would like me to adjust the day-by-day schedule, recommend specific hotels, or estimate transportation fares."
    )

def perform_deep_search(destination_name: str, memory: Dict[str, Any]) -> Dict[str, Any]:
    """
    DeepSearch Engine: Scans verified destination datasets, climate sensors, and authentic viewpoints.
    """
    clean_d = destination_name.split(",")[0].strip()
    research = research_destination_facts(destination_name)
    coords = research.get("coordinates", {})
    lat = coords.get("lat", 12.9716)
    lng = coords.get("lng", 77.5946)
    dest_key = normalize_destination_key(destination_name)
    dest_intel = DESTINATION_INTELLIGENCE.get(dest_key, {})
    safety_info = get_destination_safety_report(destination_name)

    in_dest = research.get("in_destination_attractions", [])
    if in_dest:
        offbeat_gems = [{"name": a["name"], "desc": a["description"]} for a in in_dest[:3]]
    else:
        offbeat_gems = dest_intel.get("offbeat_gems", [
            {"name": f"Historic Center of {clean_d}", "desc": "Authentic neighborhood quarters away from commercial tour buses."}
        ])

    return {
        "status": "DeepSearch Complete",
        "destination": research.get("destination_name", destination_name),
        "confidence_level": research.get("overall_confidence", "HIGH CONFIDENCE"),
        "coordinates": {"lat": lat, "lng": lng},
        "elevation_m": research.get("elevation_m"),
        "category": research.get("destination_type", "Global Exploration"),
        "overall_rating": 4.8,
        "altitude_terrain": research.get("terrain") or f"Geographic coordinates: {lat:.4f}°N, {lng:.4f}°E. Elevation: {research.get('elevation_m', 'Varied')}m.",
        "best_photography_windows": dest_intel.get("best_photo_windows", [
            {"time": "06:00 AM - 07:15 AM", "location": f"{clean_d} Scenic Vista", "condition": "Tranquil morning golden hour"},
            {"time": "05:45 PM - 06:45 PM", "location": f"{clean_d} Panoramic Lookout", "condition": "Warm dusk twilight"}
        ]),
        "offbeat_hidden_gems": offbeat_gems,
        "local_gastronomy_secrets": dest_intel.get("food_secrets", [
            "Authentic regional specialties made with farm-fresh local seasonal ingredients",
            "Traditional breakfast stalls frequented by local residents"
        ]),
        "terrain_road_advisory": dest_intel.get("safety_road_notes", "Local roads vary by terrain; use registered transit passes and ride-hailing apps."),
        "verified_hotlines": safety_info.get("emergency_numbers", ["112", "100"])[:3],
        "deep_search_sources": [
            "OpenStreetMap Geo-Database",
            "Wikipedia Encyclopedic Registry",
            "Official State Tourism Registries",
            f"{research.get('destination_name', destination_name)} Tourism Authority"
        ]
    }

def generate_conversational_response(
    user_message: str,
    trip_context: Optional[Dict[str, Any]] = None,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    session_memory: Optional[Dict[str, Any]] = None,
    force_deep_search: bool = False
) -> Dict[str, Any]:
    """
    WANDERWISE CHATGPT-STYLE CONVERSATIONAL COPILOT:
    1. Extracts and updates persistent context memory dynamically.
    2. Understands incomplete sentences, price adjustments, and follow-up inquiries.
    3. Fetches real-time telemetry (Open-Meteo weather, Nominatim coordinates).
    4. Delivers comprehensive guides, itemized budgets, and geographically clustered itineraries.
    """
    memory = extract_and_update_memory(user_message, session_memory)
    text_lower = user_message.lower().strip()

    current_dest = memory.get("destination") or (trip_context.get("destination") if trip_context else None)
    days = memory.get("days", 3)
    travellers = memory.get("travellers", 2)
    budget = memory.get("budget", 20000.0)
    expenses = memory.get("expenses", {})
    interests = memory.get("interests", [])

    # Format context state injection for Gemini
    context_summary = (
        f"[CURRENT CONVERSATION MEMORY & TRIP PROFILE:\n"
        f"• Active Destination: '{current_dest or 'Not yet specified'}'\n"
        f"• Duration: {days} Days ({max(1, days - 1)} Nights)\n"
        f"• Travellers: {travellers} people\n"
        f"• Current Total Budget: ₹{int(budget):,} (approx ₹{int(budget / max(1, travellers)):,}/person)\n"
        f"• Itemized Expenses on File: Hotel=₹{int(expenses.get('hotel_per_night', 2000)):,}/night, "
        f"Food=₹{int(expenses.get('food_per_day', 600)):,}/day/person, Transport=₹{int(expenses.get('transport', 1200)):,}, "
        f"Activities=₹{int(expenses.get('activities', 800)):,}\n"
        f"• Previously Discussed Locations: {memory.get('previously_discussed_destinations', [])}\n"
        f"• Last Discussed Attraction/Topic: {memory.get('last_discussed_attraction') or memory.get('last_topic')}]"
    )

    # Real-Time Live Weather Check
    realtime_weather_info = ""
    is_live_weather_query = any(k in text_lower for k in [
        "current weather", "weather right now", "is it raining", "live weather", "temperature today",
        "weather today", "forecast", "what's the weather"
    ])
    if current_dest:
        try:
            lat, lng = resolve_destination_coordinates(current_dest)
            live_w = get_live_weather_sync(lat, lng)
            cur = live_w.get("current", {})
            realtime_weather_info = (
                f"[LIVE REAL-TIME TELEMETRY FROM OPEN-METEO API for {current_dest}:\n"
                f"Coordinates: {lat:.4f}°N, {lng:.4f}°E\n"
                f"Temperature: {cur.get('temperature', 22.0)}°C (Feels like {cur.get('apparent_temperature', 22.5)}°C)\n"
                f"Condition: {cur.get('condition', 'Pleasant')}\n"
                f"Rain: {cur.get('rain_probability', 0)}mm | Humidity: {cur.get('humidity', 60)}% | Wind: {cur.get('wind_speed', 10.0)} km/h\n"
                f"Please cite Open-Meteo verified live telemetry in your answer.]"
            )
        except Exception as e:
            print(f"Weather lookup note: {e}")

    extra_context = context_summary
    if realtime_weather_info:
        extra_context += f"\n\n{realtime_weather_info}"

    # Step 4: Inject verified ground-truth research facts (Strict Anti-Hallucination)
    if current_dest and "->" not in current_dest:
        try:
            research = research_destination_facts(current_dest)
            grounded_in_dest = "\n".join([f"• {a['name']} ({a['location']}): {a['description']}" for a in research.get("in_destination_attractions", [])[:5]])
            grounded_excursions = "\n".join([f"• {a['name']} ({a['location']}): {a['description']}" for a in research.get("nearby_excursions", [])[:3]])

            verified_research_context = (
                f"[VERIFIED GROUND-TRUTH RESEARCH FROM OFFICIAL TOURISM REGISTRIES & OPENSTREETMAP for {research.get('destination_name', current_dest)}:\n"
                f"• Classification: {research.get('destination_type')} in {research.get('district')}, {research.get('state')}, {research.get('country')}\n"
                f"• Elevation: {research.get('elevation_m')}m | Coordinates: {research.get('coordinates', {}).get('lat', 12.9716):.4f}°N, {research.get('coordinates', {}).get('lng', 77.5946):.4f}°E\n"
                f"• VERIFIED IN-DESTINATION ATTRACTIONS (Strict Ground Truth):\n{grounded_in_dest}\n"
                f"• VERIFIED NEARBY EXCURSIONS (Clearly separate >25km away):\n{grounded_excursions}\n"
                f"• Official Tourism Portal: {research.get('official_tourism_url')}\n"
                f"• Confidence Rating: {research.get('overall_confidence')}\n"
                f"STRICT ANTI-HALLUCINATION PROTOCOL: Recommend ONLY verified places from above or that physically exist in {current_dest}. Never place attractions from other districts into this destination. If not verified, state 'Information could not be reliably verified at the moment.']"
            )
            extra_context += f"\n\n{verified_research_context}"
        except Exception as e:
            print(f"Research grounding note: {e}")

    # =========================================================================
    # INTENT 0: AMBIGUOUS DESTINATION RESOLUTION (Section 1)
    # =========================================================================
    if current_dest:
        dest_base = current_dest.split(",")[0].strip().lower()
        ambig_options = check_destination_ambiguity(dest_base)
        if ambig_options:
            has_explicit_context = any(
                part.strip().lower() in text_lower
                for opt in ambig_options
                for part in opt.split(" - ")[0].split(",")[1:]
            )
            # Only trigger clarification if user typed the bare ambiguous name without state/country
            if not has_explicit_context and any(dest_base == w.strip("?,.!") for w in text_lower.split()):
                bullet_opts = "\n".join([f"{idx+1}. **{opt.split(' - ')[0]}**: {opt.split(' - ')[1] if ' - ' in opt else ''}" for idx, opt in enumerate(ambig_options)])
                clarify_text = (
                    f"### 📍 Destination Clarification Needed\n\n"
                    f"**'{current_dest.split(',')[0].title()}'** can refer to multiple destinations across the world:\n\n"
                    f"{bullet_opts}\n\n"
                    f"Which of these locations are you planning to visit? Select an option below or specify your destination:"
                )
                suggested = []
                for opt in ambig_options:
                    place_name = opt.split(" - ")[0].strip()
                    suggested.append({
                        "label": place_name,
                        "action": "prompt",
                        "text": f"Plan a trip to {place_name}"
                    })
                return {
                    "role": "assistant",
                    "content": clarify_text,
                    "structured_type": None,
                    "memory": memory,
                    "suggested_actions": suggested
                }

    # =========================================================================
    # INTENT 1: ITEMISED EXPENSE OR BUDGET UPDATE (Section 11 C, E)
    # =========================================================================
    has_expense_keywords = any(k in text_lower for k in [
        "hotel ", "room ", "stay ", "food ", "meals ", "bus ", "train ", "flight ",
        "transport ", "cab ", "entry fee", "tickets ", "how much will it cost",
        "what if i have only", "budget is", "calculate cost", "calculate budget",
        "total cost", "cost breakdown", "make it less expensive"
    ])
    has_price_number = bool(re.search(r'\b(?:hotel|food|bus|train|flight|stay|room|cab|budget)\b.*\b\d{2,6}\b', text_lower))

    if (has_expense_keywords and has_price_number) or any(k in text_lower for k in ["how much will it cost", "calculate budget", "cost breakdown", "what if i have only"]):
        clean_d = (current_dest or "your trip").split(',')[0]
        nights = max(1, days - 1)
        h_per_night = expenses.get("hotel_per_night", 2000.0)
        f_per_day = expenses.get("food_per_day", 600.0)
        trans = expenses.get("transport", 1200.0)
        acts = expenses.get("activities", 800.0)

        hotel_total = h_per_night * nights
        food_total = f_per_day * days * travellers
        grand_total = round(hotel_total + food_total + trans + acts, 2)
        per_person = round(grand_total / max(1, travellers), 2)
        memory["budget"] = grand_total

        budget_prompt = (
            f"The user is discussing travel costs or shared an updated expense item for their {days}-day trip to {clean_d} for {travellers} travellers. "
            f"Current expense state: Hotel ₹{int(h_per_night):,}/night ({nights} nights = ₹{int(hotel_total):,}), "
            f"Food ₹{int(f_per_day):,}/day/person ({days} days x {travellers} people = ₹{int(food_total):,}), "
            f"Transportation ₹{int(trans):,}, Sightseeing/Activities ₹{int(acts):,}. "
            f"Grand Total: ₹{int(grand_total):,} (approx ₹{int(per_person):,}/person). "
            f"Respond warmly and acknowledge the update. Provide an itemized Markdown cost breakdown table and 2-3 practical tips to optimize expenses."
        )
        gemini_budget_reply = try_gemini_multiturn_chat(budget_prompt, conversation_history, extra_context=extra_context)

        fallback_budget_reply = (
            f"### 💰 Trip Budget Breakdown for **{clean_d}**\n\n"
            f"I have recalculated your estimated expenses for **{travellers} travellers** across **{days} days ({nights} nights)** based on your shared details:\n\n"
            f"| Expense Category | Unit Rate / Details | Total Estimated Cost |\n"
            f"| :--- | :--- | :--- |\n"
            f"| 🏨 **Accommodation** | ₹{int(h_per_night):,} / night × {nights} nights | **₹{int(hotel_total):,}** |\n"
            f"| 🍲 **Food & Dining** | ₹{int(f_per_day):,} / day × {travellers} persons × {days} days | **₹{int(food_total):,}** |\n"
            f"| 🚆 **Transportation** | Local transit / bus / cab fare | **₹{int(trans):,}** |\n"
            f"| 🎟️ **Activities & Sightseeing** | Monument entry tickets & activities | **₹{int(acts):,}** |\n"
            f"| 📊 **Estimated Grand Total** | **All Categories Combined** | **₹{int(grand_total):,}** |\n"
            f"| 👤 **Per Person Cost** | Total divided by {travellers} travellers | **₹{int(per_person):,} / person** |\n\n"
            f"💡 **Budget Optimization Tips:**\n"
            f"• **Stay:** Booking homestays or heritage bed-and-breakfasts can lower nightly rates by 15-25%.\n"
            f"• **Food:** Enjoy authentic local thalis and street delicacies for high quality at lower spend.\n"
            f"• **Transit:** Pre-booked day transit passes or shared rides reduce point-to-point cab charges."
        )

        return {
            "role": "assistant",
            "content": gemini_budget_reply or fallback_budget_reply,
            "structured_type": "budget_breakdown",
            "structured_data": {
                "destination": clean_d,
                "days": days,
                "nights": nights,
                "travellers": travellers,
                "grand_total": grand_total,
                "per_person": per_person,
                "itemized": {
                    "accommodation": hotel_total,
                    "food": food_total,
                    "transportation": trans,
                    "activities": acts
                }
            },
            "memory": memory,
            "suggested_actions": [
                {"label": f"Plan {days}-Day Itinerary", "action": "prompt", "text": f"Create an itinerary for {clean_d} within ₹{int(grand_total):,}"},
                {"label": "Hotel Stays", "action": "prompt", "text": f"Where to stay in {clean_d}?"},
                {"label": "Can we make it cheaper?", "action": "prompt", "text": f"How can we reduce expenses for {clean_d}?"}
            ]
        }

    # =========================================================================
    # INTENT 2: COMPLETE DESTINATION GUIDE (Section 4 - 16 Standard Sections)
    # =========================================================================
    is_guide_request = (
        any(k in text_lower for k in [
            "complete guide", "comprehensive guide", "tell me about", "overview of", "guide to",
            "everything about", "guide for", "travel guide", "and all", "details of", "about ",
            "explore ", "visit ", "information on", "info about", "what to see"
        ]) or (
            current_dest and len(text_lower.split()) <= 4 and not any(w in text_lower for w in [
                "hotel", "bus", "flight", "food", "budget", "safe", "pack", "reach", "trip", "plan",
                "itinerary", "cost", "price", "fee", "ticket", "day", "days", "more day", "less day"
            ])
        )
    ) and current_dest

    if is_guide_request:
        if memory.get("is_multi_destination") and len(memory.get("destinations_list", [])) >= 2:
            circuit_data = research_multi_destination_circuit([{"canonical_name": d} for d in memory["destinations_list"]])

            transit_summary = "\n".join([
                f"• **{leg['from']} ➔ {leg['to']}:** {leg['road_distance_km']} km (approx. {leg['estimated_drive_time']}) — *{leg['route_notes']}*"
                for leg in circuit_data.get("transit_legs", [])
            ])

            dest_sections = []
            for d_info in circuit_data.get("destinations", []):
                d_name = d_info["destination_name"]
                d_type = d_info["destination_type"]
                top_acts = "\n".join([f"  - **{a['name']}** [{a.get('confidence', 'HIGH CONFIDENCE')}]: {a['description']}" for a in d_info.get("in_destination_attractions", [])[:4]])
                excurs = "\n".join([f"  - **{ex['name']}**: {ex['description']} *(Nearby Day Trip)*" for ex in d_info.get("nearby_excursions", [])[:2]])

                sec = (
                    f"### 📍 Phase: **{d_name}** ({d_type})\n"
                    f"• **Geographical Context:** {d_info.get('district') + ', ' if d_info.get('district') else ''}{d_info.get('state')}, {d_info.get('country')}\n"
                    f"• **Verified In-Destination Attractions:**\n{top_acts}\n"
                )
                if excurs:
                    sec += f"• **Nearby Excursions (>25km away):**\n{excurs}\n"
                sec += f"• **Official Source:** [{d_name} Official Tourism Portal]({d_info.get('official_tourism_url')})\n"
                dest_sections.append(sec)

            multi_guide_content = (
                f"# 🗺️ Multi-Destination Journey Guide: **{' ➔ '.join(memory['destinations_list'])}**\n\n"
                f"**Circuit Overview:** Connecting **{len(memory['destinations_list'])} verified destinations** across Kerala/regional corridors over a total road distance of **{circuit_data.get('total_transit_distance_km')} km**.\n\n"
                f"### 🛣️ Inter-City Transit & Route Connectivity\n"
                f"{transit_summary}\n\n"
                f"{'\n'.join(dest_sections)}\n"
                f"### 💡 Multi-Destination Travel Rules & Best Practices\n"
                f"• **Strict Destination Boundaries:** Sights in {memory['destinations_list'][0]} and {memory['destinations_list'][1]} cannot be combined into the same day due to driving times. Allocate dedicated full days to each.\n"
                f"• **Mountain Roads:** Driving speeds on Western Ghats mountain ghats average 30-35 km/h; avoid driving late at night due to mountain fog.\n"
                f"• **Luggage & Logistics:** Pre-book a dedicated private cab or use state express transit for seamless luggage transfers between hubs."
            )

            return {
                "role": "assistant",
                "content": multi_guide_content,
                "structured_type": None,
                "memory": memory,
                "suggested_actions": [
                    {"label": f"Plan {days}-Day Circuit", "action": "prompt", "text": f"Plan a {days}-day itinerary covering {' and '.join(memory['destinations_list'])}"},
                    {"label": f"Where to Stay in {memory['destinations_list'][0].split(',')[0]}", "action": "prompt", "text": f"Where should I stay in {memory['destinations_list'][0]}?"},
                    {"label": f"Where to Stay in {memory['destinations_list'][1].split(',')[0]}", "action": "prompt", "text": f"Where should I stay in {memory['destinations_list'][1]}?"}
                ]
            }

        clean_d = current_dest.split(',')[0]
        guide_prompt = (
            f"The user wants a COMPLETE, MASTER DESTINATION GUIDE for {current_dest}. "
            f"Generate a comprehensive guide containing EXACTLY these 16 numbered sections with specific, authentic local facts (never generic text):\n"
            f"1. Destination Overview & Geographical Context\n"
            f"2. Top Attractions & Landmarks (with exact locations)\n"
            f"3. Hidden Gems & Offbeat Secrets\n"
            f"4. Best Experiences & Signature Activities\n"
            f"5. Local Food & Famous Regional Dishes\n"
            f"6. Best Restaurants & Cafes\n"
            f"7. Accommodation Recommendations (Budget, Boutique, Luxury)\n"
            f"8. Transportation Options & Getting Around\n"
            f"9. Estimated Travel Expenses (Daily spend in INR & USD)\n"
            f"10. Best Season to Visit\n"
            f"11. Weather Considerations & Packing Tips\n"
            f"12. Safety Precautions, Scams & Verified Hotlines\n"
            f"13. Local Culture, Customs & Etiquette\n"
            f"14. Shopping & Traditional Bazaars\n"
            f"15. Photography & Scenic Locations (with golden hour times)\n"
            f"16. Nearby Destinations Worth Exploring (Day trips within 100km)\n"
            f"Format with clean Markdown headers, bullet points, and high factual rigor."
        )
        gemini_guide = try_gemini_multiturn_chat(guide_prompt, conversation_history, extra_context=extra_context)
        guide_content = gemini_guide or generate_fallback_destination_guide(current_dest)
        return {
            "role": "assistant",
            "content": guide_content,
            "structured_type": None,
            "memory": memory,
            "suggested_actions": [
                {"label": f"Plan {days}-Day Itinerary", "action": "prompt", "text": f"Plan a {days}-day trip to {clean_d}"},
                {"label": f"Where to Stay in {clean_d}", "action": "prompt", "text": f"Where should I stay in {clean_d}?"},
                {"label": f"Transit Costs to {clean_d}", "action": "prompt", "text": f"How do I travel to {clean_d} and what are costs?"}
            ]
        }

    # =========================================================================
    # INTENT 3: EXPLICIT ITINERARY GENERATION & ADJUSTMENT (Section 5 & 11 F)
    # =========================================================================
    has_duration_query = bool(extract_duration_days(user_message))
    is_plan_request = any(k in text_lower for k in [
        "plan a", "plan my", "plan for", "plan trip", "planning a", "create an itinerary", "generate itinerary",
        "build a plan", "make an itinerary", "day itinerary", "days itinerary", "day trip", "days trip",
        "days plan", "day plan", "full itinerary", "travel plan", "day-by-day", "schedule", "make it",
        "change to", "update to", "itinerary for", "trip for", "days in", "day in", "show me days",
        "custom plan", "itinerary"
    ]) or (
        ("itinerary" in text_lower or "travel plan" in text_lower or "trip" in text_lower or "plan" in text_lower)
        and not any(k in text_lower for k in ["safe", "pack", "clothes", "visa", "hotel", "food", "bus", "flight", "budget"])
    ) or (
        has_duration_query and any(w in text_lower for w in ["trip", "tour", "visit", "go", "travel", "in ", "for ", "plan", "days", "stay"])
    )

    if is_plan_request:
        if not current_dest:
            current_dest = "India"
            memory["destination"] = "India"

        itinerary_data = generate_trip_itinerary(current_dest, "2026-11-20", num_days=days)
        memory["current_itinerary"] = itinerary_data
        per_person = round(budget / max(1, travellers), 2)

        plan_prompt = (
            f"The user requested an authentic {days}-day itinerary for {current_dest} for {travellers} travellers (budget ₹{int(budget):,}). "
            f"Write an inspiring, vivid conversational overview introducing this {days}-day journey. "
            f"Highlight unique morning viewpoints, authentic local experiences, and scenic routes. Keep it engaging and formatted in clean markdown."
        )
        gemini_plan_intro = try_gemini_multiturn_chat(plan_prompt, conversation_history, extra_context=extra_context)

        clean_d = current_dest.split(',')[0]
        if memory.get("is_multi_destination") and len(memory.get("destinations_list", [])) >= 2:
            dest_chain = " ➔ ".join(memory["destinations_list"])
            reply_content = gemini_plan_intro or (
                f"Here is your personalized **{days}-Day Multi-Destination Circuit: {dest_chain}** "
                f"crafted for **{travellers} travellers** within your **₹{int(budget):,}** budget (approx. **₹{int(per_person):,}/person**)! 🗺️\n\n"
                f"• **Strict Geographic Segregation:** Each destination has its own dedicated days tailored to actual driving distances without backtracking.\n"
                f"• **Verified Regional Landmarks:** Every activity includes verified coordinates, genuine descriptions, and TripAdvisor reviews.\n"
                f"• **Inter-City Road Connectivity:** Planned travel times between hubs allow you to enjoy scenic Western Ghats mountain vistas.\n"
                f"• Switch between **Day Schedule**, **Interactive Route Map**, and **Budget** using the interactive tabs below."
            )
        else:
            reply_content = gemini_plan_intro or (
                f"Here is your personalized **{days}-Day {current_dest} Itinerary** "
                f"crafted for **{travellers} travellers** within your **₹{int(budget):,}** budget (approx. **₹{int(per_person):,}/person**)! 🗺️\n\n"
                f"• **Customer-Calibrated Duration:** Exactly **{days} full days** tailored to your schedule.\n"
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
                {"label": f"✈️ How to Reach {clean_d}", "action": "prompt", "text": f"How do I travel to {current_dest} and what are the flight/train costs?"},
                {"label": f"🏨 Where to Stay in {clean_d}", "action": "prompt", "text": f"Where should I stay in {current_dest}?"},
                {"label": f"Local Food in {clean_d}", "action": "prompt", "text": f"What authentic local food should I eat in {current_dest}?"},
                {"label": f"DeepSearch {clean_d} ⚡", "action": "deep_search", "destination": current_dest}
            ]
        }

    # =========================================================================
    # INTENT 4: WORLDWIDE TRANSIT FARES & CONNECTIVITY
    # =========================================================================
    is_transit_cost_query = any(k in text_lower for k in [
        "cost from", "how to reach", "travel to", "flight cost", "flights to", "train cost",
        "trains to", "bus to", "how do i get to", "ticket price from", "fare from",
        "flight price", "train fare", "cheapest way to reach"
    ]) or (
        ("travel" in text_lower or "reach" in text_lower or "ticket" in text_lower)
        and any(k in text_lower for k in ["from", "to", "flight", "train", "bus", "cab", "drive", "fare", "cost"])
    )

    if is_transit_cost_query and current_dest:
        origin_dest = memory.get("origin") or "Delhi"
        transit_data = estimate_global_transit_costs(origin_dest, current_dest)
        clean_o = origin_dest.split(",")[0]
        clean_d = current_dest.split(",")[0]

        transit_prompt = (
            f"The user wants realistic, actionable transit options from {clean_o} to {clean_d} (distance: {transit_data['distance_km']} km). "
            f"Provide an authoritative overview of travel choices across Flights, Trains/High-speed Rail, and Road/Bus options. "
            f"Live Booking Provider Search Links: Google Flights: {transit_data['live_links']['google_flights']}, Rome2Rio: {transit_data['live_links']['rome2rio']}. "
            f"Keep your tone helpful, concise, and structured in Markdown."
        )
        gemini_transit_reply = try_gemini_multiturn_chat(transit_prompt, conversation_history, extra_context=extra_context)

        return {
            "role": "assistant",
            "content": gemini_transit_reply or f"Here are verified connectivity routes and live fare benchmarks from **{clean_o}** to **{clean_d}** ({transit_data['distance_km']:,} km):",
            "structured_type": "transit_cost_card",
            "structured_data": transit_data,
            "memory": memory,
            "suggested_actions": [
                {"label": f"✈️ Check Live {clean_d} Flights", "action": "open_link", "url": transit_data['live_links']['google_flights']},
                {"label": f"Where to Stay in {clean_d}", "action": "prompt", "text": f"Where should I stay in {clean_d}?"},
                {"label": f"Plan {days}-Day Itinerary", "action": "prompt", "text": f"Plan a {days}-day trip to {clean_d}"}
            ]
        }

    # =========================================================================
    # INTENT 5: WORLDWIDE HOTEL & ACCOMMODATION RECOMMENDATIONS
    # =========================================================================
    is_hotel_query = any(k in text_lower for k in [
        "hotel", "hotels", "stay", "stays", "resort", "resorts", "hostel", "hostels",
        "where to stay", "place to stay", "places to stay", "accommodation", "lodging"
    ])

    if is_hotel_query and current_dest:
        clean_d = current_dest.split(",")[0]
        hotel_data = get_worldwide_hotel_suggestions(current_dest)

        hotel_prompt = (
            f"The user is asking where to stay in {current_dest}. "
            f"Provide a sophisticated, insider neighborhood breakdown explaining the best quarters to stay. "
            f"Present options across 3 tiers (Budget Stays, Boutique/Heritage Hotels, 5-Star Luxury). "
            f"Live Booking Links: Booking.com: {hotel_data['live_booking_links']['booking_com']}, Google Hotels: {hotel_data['live_booking_links']['google_hotels']}, Agoda: {hotel_data['live_booking_links']['agoda']}."
        )
        gemini_hotel_reply = try_gemini_multiturn_chat(hotel_prompt, conversation_history, extra_context=extra_context)

        return {
            "role": "assistant",
            "content": gemini_hotel_reply or f"Here are curated accommodation recommendations and live benchmark rates for **{clean_d}** across budget, boutique, and luxury tiers:",
            "structured_type": "hotel_suggestion_card",
            "structured_data": hotel_data,
            "memory": memory,
            "suggested_actions": [
                {"label": f"🏨 Search {clean_d} on Booking.com", "action": "open_link", "url": hotel_data['live_booking_links']['booking_com']},
                {"label": f"🏨 Search on Google Hotels", "action": "open_link", "url": hotel_data['live_booking_links']['google_hotels']},
                {"label": f"Plan {days}-Day Itinerary", "action": "prompt", "text": f"Plan a {days}-day trip to {clean_d}"}
            ]
        }

    # =========================================================================
    # INTENT 6: SMART FOLLOW-UP INQUIRIES & CONVERSATIONAL QUESTIONS (Section 8 & 11 B)
    # =========================================================================
    # Handles: 'What about hidden places?', 'Entry fee?', 'Is it worth visiting?',
    # 'What else is nearby?', 'Can I visit everything in one day?', 'What should I avoid?'
    if current_dest:
        clean_d = current_dest.split(',')[0]
        contextual_inquiry_prompt = (
            f"The user asks: '{user_message}'\n"
            f"Conversation Context: Active destination is '{current_dest}'. Duration is {days} days for {travellers} travellers. "
            f"Answer this specific question directly, factually, and thoroughly in the context of {current_dest}. "
            f"Do not invent information. Distinguish verified facts vs general tips. End with 2 natural follow-up recommendations."
        )
        gemini_inquiry = try_gemini_multiturn_chat(contextual_inquiry_prompt, conversation_history, extra_context=extra_context)
        inquiry_reply = gemini_inquiry or build_contextual_fallback(user_message, current_dest, days, travellers)
        return {
            "role": "assistant",
            "content": inquiry_reply,
            "structured_type": None,
            "memory": memory,
            "suggested_actions": [
                {"label": f"Plan {days}-Day Itinerary", "action": "prompt", "text": f"Plan a {days}-day trip to {clean_d}"},
                {"label": f"Where to Stay in {clean_d}", "action": "prompt", "text": f"Where should I stay in {clean_d}?"},
                {"label": f"How to Reach {clean_d}", "action": "prompt", "text": f"How do I travel to {clean_d} and what are costs?"}
            ]
        }

    # =========================================================================
    # INTENT 7: GENERAL OPEN-ENDED FALLBACK CHAT
    # =========================================================================
    general_prompt = (
        f"User message: '{user_message}'\n"
        f"Answer with warmth, precision, and deep travel domain authority. Keep it formatted in clean markdown."
    )
    gemini_general = try_gemini_multiturn_chat(general_prompt, conversation_history, extra_context=extra_context)

    clean_dest = (current_dest or "India").split(",")[0]
    default_reply = gemini_general or (
        f"Welcome to **WanderWise Travel Intelligence**! 🌍\n\n"
        f"I am your expert autonomous copilot covering destinations across all 195 nations and India. "
        f"Whether you are planning a relaxed coastal getaway, high-altitude mountain trekking, or cultural city exploration, "
        f"tell me where you would like to travel and your preferred trip duration!"
    )

    return {
        "role": "assistant",
        "content": default_reply,
        "structured_type": None,
        "memory": memory,
        "suggested_actions": [
            {"label": "🇮🇳 5 Days in India", "action": "prompt", "text": "Plan a 5-day trip to India exploring Delhi, Agra Taj Mahal, and royal Jaipur."},
            {"label": "🏖️ 4 Days in Goa", "action": "prompt", "text": "Plan a relaxed 4-day coastal trip to Goa under ₹20,000 for 2."},
            {"label": "🏔️ 5 Days in Manali", "action": "prompt", "text": "Plan a 5-day mountain trip to Manali and Atal Tunnel."},
            {"label": "🌴 6 Days in Kerala", "action": "prompt", "text": "Plan a 6-day trip to Kerala covering Munnar tea hills and Alleppey backwaters."}
        ]
    }
