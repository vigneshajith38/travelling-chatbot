import datetime
import json
import re
from typing import List, Dict, Any, Optional
from app.core.config import settings

# Global coordinates cache for top world & Indian destinations
GLOBAL_DESTINATION_COORDINATES = {
    # India Major Hubs & States
    "india": (28.6139, 77.2090),
    "delhi": (28.6139, 77.2090),
    "new delhi": (28.6139, 77.2090),
    "mumbai": (19.0760, 72.8777),
    "bengaluru": (12.9716, 77.5946),
    "bangalore": (12.9716, 77.5946),
    "kolkata": (22.5726, 88.3639),
    "chennai": (13.0827, 80.2707),
    "hyderabad": (17.3850, 78.4867),
    "goa": (15.2993, 74.1240),
    "north goa": (15.5807, 73.7429),
    "south goa": (15.0100, 74.0200),
    "jaipur": (26.9124, 75.7873),
    "rajasthan": (26.9124, 75.7873),
    "udaipur": (24.5854, 73.7125),
    "jodhpur": (26.2389, 73.0243),
    "jaisalmer": (26.9157, 70.9083),
    "agra": (27.1767, 78.0081),
    "varanasi": (25.3176, 82.9739),
    "kerala": (9.9312, 76.2673),
    "kochi": (9.9312, 76.2673),
    "munnar": (10.0889, 77.0595),
    "alleppey": (9.4981, 76.3388),
    "alappuzha": (9.4981, 76.3388),
    "varkala": (8.7379, 76.7163),
    "wayanad": (11.6854, 76.1320),
    "manali": (32.2432, 77.1892),
    "himachal": (32.2432, 77.1892),
    "himachal pradesh": (32.2432, 77.1892),
    "shimla": (31.1048, 77.1734),
    "spiti": (32.2461, 78.0349),
    "dharamshala": (32.2190, 76.3234),
    "kasol": (32.0100, 77.3150),
    "kashmir": (34.0837, 74.7973),
    "srinagar": (34.0837, 74.7973),
    "gulmarg": (34.0484, 74.3805),
    "pahalgam": (34.0163, 75.3150),
    "ladakh": (34.1526, 77.5771),
    "leh": (34.1526, 77.5771),
    "rishikesh": (30.0869, 78.2676),
    "uttarakhand": (30.0869, 78.2676),
    "amritsar": (31.6340, 74.8723),
    "gokarna": (14.5479, 74.3188),
    "coorg": (12.4244, 75.7382),
    "hampi": (15.3350, 76.4600),
    "ooty": (11.4102, 76.6950),
    "kodaikanal": (10.2381, 77.4892),
    "pondicherry": (11.9416, 79.8083),
    "andaman": (11.6234, 92.7265),
    "port blair": (11.6234, 92.7265),
    "darjeeling": (27.0410, 88.2663),
    "gangtok": (27.3389, 88.6065),
    "sikkim": (27.3389, 88.6065),
    "shillong": (25.5788, 91.8933),
    "meghalaya": (25.5788, 91.8933),

    # Global Destinations
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
        return (28.6139, 77.2090)
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
    return (28.6139, 77.2090)

# Regional landmark template banks for offline fallback (up to 7+ days each)
REGIONAL_LANDMARK_BANKS = {
    "india": [
        # Day 1: Delhi Heritage
        {"slot": "morning", "time": "08:30 AM", "title": "Red Fort & Mughal Grandeur", "desc": "Explore the historic sandstone bastions and royal Diwan-i-Aam of the Mughal emperors.", "loc": "Old Delhi", "lat": 28.6562, "lng": 77.2410, "cost": 500.0, "dur": 120, "mode": "walking", "cat": "culture", "indoor": False},
        {"slot": "afternoon", "time": "01:00 PM", "title": "Chandni Chowk Street Food & Spice Market", "desc": "Cycle rickshaw food crawl sampling parathas, jalebis, and aromatic Asian spices in Khari Baoli.", "loc": "Chandni Chowk, Delhi", "lat": 28.6506, "lng": 77.2303, "cost": 400.0, "dur": 120, "mode": "walking", "cat": "food", "indoor": True},
        {"slot": "evening", "time": "06:00 PM", "title": "India Gate Twilight & Kartavya Path Walk", "desc": "Stroll down the grand ceremonial avenue past illuminated war memorials and fountains.", "loc": "India Gate, New Delhi", "lat": 28.6129, "lng": 77.2295, "cost": 0.0, "dur": 90, "mode": "walking", "cat": "photo", "indoor": False},
        # Day 2: Agra & Taj Mahal
        {"slot": "morning", "time": "06:00 AM", "title": "Taj Mahal Sunrise at Yamuna Riverside", "desc": "Witness the ivory-white marble monument of eternal love bathed in the soft morning glow.", "loc": "Taj Mahal, Agra", "lat": 27.1751, "lng": 78.0421, "cost": 1100.0, "dur": 150, "mode": "walking", "cat": "photo", "indoor": False},
        {"slot": "afternoon", "time": "01:30 PM", "title": "Agra Fort Royal Palaces & Jahangiri Mahal", "desc": "Wander through the massive red sandstone UNESCO fort overlooking the distant Taj Mahal.", "loc": "Agra Fort, Agra", "lat": 27.1795, "lng": 78.0211, "cost": 650.0, "dur": 110, "mode": "walking", "cat": "culture", "indoor": False},
        {"slot": "evening", "time": "06:00 PM", "title": "Mehtab Bagh Sunset Across the Yamuna", "desc": "Serene charbagh botanical gardens framing the Taj Mahal silhouette at golden hour.", "loc": "Mehtab Bagh, Agra", "lat": 27.1798, "lng": 78.0449, "cost": 300.0, "dur": 90, "mode": "walking", "cat": "relaxation", "indoor": False},
        # Day 3: Jaipur Pink City & Amber Fort
        {"slot": "morning", "time": "08:30 AM", "title": "Amber Fort Hilltop Palace & Sheesh Mahal", "desc": "Climb through ancient sun-kissed royal courtyards and the dazzling Hall of Mirrors.", "loc": "Amer, Jaipur", "lat": 26.9855, "lng": 75.8513, "cost": 500.0, "dur": 150, "mode": "driving", "cat": "culture", "indoor": False},
        {"slot": "afternoon", "time": "01:30 PM", "title": "Jal Mahal & Royal Gaitor Cenotaphs", "desc": "Admire the floating palace in Man Sagar Lake and marble memorials of Jaipur Maharajas.", "loc": "Amer Road, Jaipur", "lat": 26.9534, "lng": 75.8462, "cost": 200.0, "dur": 90, "mode": "driving", "cat": "photo", "indoor": False},
        {"slot": "evening", "time": "06:00 PM", "title": "Hawa Mahal (Palace of Winds) & Pink City Bazaars", "desc": "View the 953 honeycombed jharokha windows followed by Johari Bazaar gemstone and textile walks.", "loc": "Badi Choupad, Jaipur", "lat": 26.9239, "lng": 75.8267, "cost": 250.0, "dur": 120, "mode": "walking", "cat": "shopping", "indoor": True},
        # Day 4: Spiritual Varanasi
        {"slot": "morning", "time": "05:45 AM", "title": "Sunrise Ganges Boat Ride along Ancient Ghats", "desc": "Glide past Dashashwamedh and Assi Ghats as holy chants and morning rituals greet the sun.", "loc": "Assi Ghat, Varanasi", "lat": 25.2905, "lng": 83.0069, "cost": 400.0, "dur": 120, "mode": "transit", "cat": "culture", "indoor": False},
        {"slot": "afternoon", "time": "02:00 PM", "title": "Sarnath Deer Park & Dhamek Stupa", "desc": "Visit the sacred site where Lord Buddha gave his first sermon after attaining enlightenment.", "loc": "Sarnath, Varanasi", "lat": 25.3811, "lng": 83.0214, "cost": 300.0, "dur": 110, "mode": "driving", "cat": "culture", "indoor": True},
        {"slot": "evening", "time": "06:30 PM", "title": "Grand Maha Ganga Aarti at Dashashwamedh", "desc": "Experience the mesmerizing twilight ritual of brass lamps, incense, cymbals, and sacred hymns.", "loc": "Dashashwamedh Ghat", "lat": 25.3076, "lng": 83.0104, "cost": 0.0, "dur": 90, "mode": "walking", "cat": "culture", "indoor": False},
        # Day 5: Coastal Mumbai
        {"slot": "morning", "time": "08:30 AM", "title": "Gateway of India & Colaba Heritage Quarter", "desc": "Iconic basalt arch on the Arabian Sea fronting the legendary Taj Mahal Palace Hotel.", "loc": "Apollo Bunder, Mumbai", "lat": 18.9220, "lng": 72.8347, "cost": 0.0, "dur": 100, "mode": "walking", "cat": "photo", "indoor": False},
        {"slot": "afternoon", "time": "01:30 PM", "title": "Marine Drive Promenade & Chowpatty Street Eats", "desc": "Savor authentic Mumbai pav bhaji, sev puri, and kulfi overlooking Back Bay.", "loc": "Marine Drive, Mumbai", "lat": 18.9432, "lng": 72.8230, "cost": 350.0, "dur": 110, "mode": "walking", "cat": "food", "indoor": False},
        {"slot": "evening", "time": "06:30 PM", "title": "Bandra Bandstand Sunset & Castella de Aguada", "desc": "Watch the sunset behind the Bandra-Worli Sea Link from the historic Portuguese fort ruins.", "loc": "Bandstand, Bandra West", "lat": 19.0434, "lng": 72.8194, "cost": 0.0, "dur": 90, "mode": "driving", "cat": "relaxation", "indoor": False},
        # Day 6: Kerala Backwaters
        {"slot": "morning", "time": "09:00 AM", "title": "Fort Kochi Chinese Fishing Nets & Jew Town", "desc": "Ancient cantilevers, Dutch palace frescoes, and narrow antique and spice streets.", "loc": "Fort Kochi", "lat": 9.9656, "lng": 76.2421, "cost": 150.0, "dur": 120, "mode": "walking", "cat": "culture", "indoor": True},
        {"slot": "afternoon", "time": "01:30 PM", "title": "Alleppey Backwaters Houseboat Cruise", "desc": "Drift through emerald palm-fringed canals sampling freshly prepared Karimeen fish thali.", "loc": "Punnamada Jetty, Alleppey", "lat": 9.5011, "lng": 76.3450, "cost": 2500.0, "dur": 200, "mode": "transit", "cat": "relaxation", "indoor": True},
        {"slot": "evening", "time": "06:30 PM", "title": "Kathakali & Kalaripayattu Cultural Evening", "desc": "Witness traditional Kerala theatrical dance makeup, dramatic eye expressions, and ancient martial arts.", "loc": "Kochi Cultural Centre", "lat": 9.9630, "lng": 76.2460, "cost": 500.0, "dur": 90, "mode": "walking", "cat": "culture", "indoor": True},
        # Day 7: Himalayan Foothills
        {"slot": "morning", "time": "08:00 AM", "title": "Rishikesh Laxman Jhula & Beatles Ashram Trail", "desc": "Walk over suspension bridges spanning the turquoise Ganga and explore graffiti-painted meditation domes.", "loc": "Swarg Ashram, Rishikesh", "lat": 30.1245, "lng": 78.3180, "cost": 150.0, "dur": 130, "mode": "walking", "cat": "adventure", "indoor": False},
        {"slot": "afternoon", "time": "01:30 PM", "title": "Shivpuri White Water River Rafting (Grade III)", "desc": "Exhilarating 16km rafting descent negotiating Roller Coaster and Golf Course rapids.", "loc": "Shivpuri, Rishikesh", "lat": 30.1380, "lng": 78.3890, "cost": 1200.0, "dur": 150, "mode": "driving", "cat": "adventure", "indoor": False},
        {"slot": "evening", "time": "06:00 PM", "title": "Triveni Ghat Evening Ganga Aarti", "desc": "Join hundreds of floating leaf diyas down the sacred river as dusk settles over the Himalayas.", "loc": "Triveni Ghat, Rishikesh", "lat": 30.1037, "lng": 78.2948, "cost": 50.0, "dur": 90, "mode": "walking", "cat": "culture", "indoor": False}
    ],
    "goa": [
        # Day 1: North Goa Heritage & Sunsets
        {"slot": "morning", "time": "08:30 AM", "title": "Fort Aguada & 17th-Century Lighthouse", "desc": "Portuguese fortress overlooking the Arabian Sea with panoramic coastal bastion walks.", "loc": "Sinquerim, North Goa", "lat": 15.4920, "lng": 73.7737, "cost": 50.0, "dur": 90, "mode": "driving", "cat": "photo", "indoor": False},
        {"slot": "afternoon", "time": "01:00 PM", "title": "Fontainhas Latin Quarter Heritage Walk", "desc": "Wander through colorful Portuguese villas painted in ochre and terracotta with quaint bakeries.", "loc": "Panaji, Goa", "lat": 15.4989, "lng": 73.8278, "cost": 0.0, "dur": 110, "mode": "walking", "cat": "culture", "indoor": False},
        {"slot": "evening", "time": "05:30 PM", "title": "Anjuna Beach Cliff Sunset & Acoustic Shacks", "desc": "Watch crimson sunsets over volcanic rocks while listening to chill acoustic beach sessions.", "loc": "Anjuna Beach", "lat": 15.5807, "lng": 73.7429, "cost": 400.0, "dur": 120, "mode": "driving", "cat": "relaxation", "indoor": False},
        # Day 2: Nature & Waterfalls
        {"slot": "morning", "time": "08:00 AM", "title": "Dudhsagar Waterfall 4x4 Jeep Safari", "desc": "Thrilling off-road trail through Bhagwan Mahaveer Sanctuary to the milky four-tiered cascades.", "loc": "Mollem National Park", "lat": 15.3144, "lng": 74.3143, "cost": 1500.0, "dur": 240, "mode": "transit", "cat": "adventure", "indoor": False},
        {"slot": "afternoon", "time": "02:00 PM", "title": "Sahakari Organic Spice Plantation & Feast", "desc": "Walk through vanilla, cardamom, and cinnamon groves followed by an authentic Goan buffet lunch.", "loc": "Curti, Ponda", "lat": 15.4055, "lng": 74.0200, "cost": 500.0, "dur": 110, "mode": "driving", "cat": "food", "indoor": True},
        {"slot": "evening", "time": "06:30 PM", "title": "Mandovi River Sunset Catamaran Cruise", "desc": "Sail past illuminated Panaji promenades with traditional Goan folk music and Dekhni dances.", "loc": "Panaji Jetty", "lat": 15.5011, "lng": 73.8315, "cost": 600.0, "dur": 80, "mode": "transit", "cat": "relaxation", "indoor": False},
        # Day 3: Old Goa World Heritage
        {"slot": "morning", "time": "09:00 AM", "title": "Basilica of Bom Jesus & Se Cathedral", "desc": "UNESCO Baroque masterworks holding the sacred relics of St. Francis Xavier.", "loc": "Old Goa", "lat": 15.5009, "lng": 73.9116, "cost": 0.0, "dur": 120, "mode": "driving", "cat": "culture", "indoor": True},
        {"slot": "afternoon", "time": "01:30 PM", "title": "Divar Island Heritage Cycling Trail", "desc": "Take the river ferry to a quiet emerald island with ancient sleepy hamlets and church viewpoints.", "loc": "Divar Island, Goa", "lat": 15.5180, "lng": 73.8820, "cost": 300.0, "dur": 130, "mode": "transit", "cat": "nature", "indoor": False},
        {"slot": "evening", "time": "06:00 PM", "title": "Vagator Hilltop Sunset & Chapora Fort Ruins", "desc": "Iconic 'Dil Chahta Hai' red laterite fortress commanding 360-degree Arabian Sea sunsets.", "loc": "Chapora, Vagator", "lat": 15.6062, "lng": 73.7380, "cost": 0.0, "dur": 100, "mode": "driving", "cat": "photo", "indoor": False},
        # Day 4: South Goa Peaceful Escapes
        {"slot": "morning", "time": "08:30 AM", "title": "Palolem Crescent Beach & Kayaking", "desc": "Pristine calm waters surrounded by coconut palms, ideal for relaxed kayaking to Butterfly Beach.", "loc": "Palolem, Canacona", "lat": 15.0100, "lng": 74.0231, "cost": 600.0, "dur": 140, "mode": "driving", "cat": "adventure", "indoor": False},
        {"slot": "afternoon", "time": "02:00 PM", "title": "Cabo de Rama Fort Coastal Cliff Walk", "desc": "Wild remote fortress overlooking cobalt blue bays where Lord Rama stayed during exile.", "loc": "Canaguinim, South Goa", "lat": 15.0903, "lng": 73.9219, "cost": 0.0, "dur": 110, "mode": "driving", "cat": "nature", "indoor": False},
        {"slot": "evening", "time": "06:00 PM", "title": "Agonda Beach Silent Sunset Stroll", "desc": "Unspoiled golden shoreline famous for Olive Ridley turtle nesting and bohemian candlelit dinners.", "loc": "Agonda Beach", "lat": 15.0450, "lng": 73.9870, "cost": 500.0, "dur": 90, "mode": "walking", "cat": "relaxation", "indoor": False},
        # Day 5: Water Sports & Islands
        {"slot": "morning", "time": "08:00 AM", "title": "Grande Island Snorkeling & Dolphin Safari", "desc": "Speedboat excursion into deep waters to snorkel above coral beds and spot playful dolphins.", "loc": "Grande Island, Vasco", "lat": 15.3520, "lng": 73.7650, "cost": 1800.0, "dur": 180, "mode": "transit", "cat": "adventure", "indoor": False},
        {"slot": "afternoon", "time": "02:00 PM", "title": "Goan Fish Thali Crawl in Mapusa", "desc": "Savor authentic Kingfish fry, prawn balchao, crab xec xec, and cooling sol kadhi.", "loc": "Mapusa, North Goa", "lat": 15.5925, "lng": 73.8155, "cost": 450.0, "dur": 90, "mode": "driving", "cat": "food", "indoor": True},
        {"slot": "evening", "time": "06:30 PM", "title": "Morjim Beach Sunset Drum Circle", "desc": "Relax under canopy shacks with organic mocktails and acoustic sundowner beats.", "loc": "Morjim Beach", "lat": 15.6178, "lng": 73.7340, "cost": 300.0, "dur": 100, "mode": "walking", "cat": "relaxation", "indoor": False}
    ],
    "manali": [
        # Day 1: Old Manali Vibes
        {"slot": "morning", "time": "09:00 AM", "title": "Hadimba Temple in Ancient Cedar Forest", "desc": "16th-century four-tiered pagoda temple made of intricately carved deodar wood and stone.", "loc": "Dhungri Forest, Manali", "lat": 32.2483, "lng": 77.1706, "cost": 50.0, "dur": 90, "mode": "walking", "cat": "culture", "indoor": False},
        {"slot": "afternoon", "time": "01:30 PM", "title": "Old Manali Riverside Cafes & Trout Tasting", "desc": "Stroll cobblestone village lanes sampling Himalayan wood-fired pizzas and grilled river trout.", "loc": "Old Manali Village", "lat": 32.2530, "lng": 77.1780, "cost": 600.0, "dur": 110, "mode": "walking", "cat": "food", "indoor": True},
        {"slot": "evening", "time": "05:30 PM", "title": "Jogini Waterfall Twilight Trek", "desc": "Scenic hike from Vashisht through apple orchards to cascading mountain cascades.", "loc": "Vashisht, Manali", "lat": 32.2650, "lng": 77.1900, "cost": 0.0, "dur": 120, "mode": "walking", "cat": "nature", "indoor": False},
        # Day 2: High Altitudes & Atal Tunnel
        {"slot": "morning", "time": "08:00 AM", "title": "Solang Valley Paragliding & Ropeway", "desc": "Soar over dramatic snow-capped peaks and glaciers from a 3,200m alpine launch pad.", "loc": "Solang Valley", "lat": 32.3160, "lng": 77.1570, "cost": 2200.0, "dur": 150, "mode": "driving", "cat": "adventure", "indoor": False},
        {"slot": "afternoon", "time": "01:00 PM", "title": "Atal Tunnel & Sissu Lahaul Valley Panorama", "desc": "Cross the 9.02km engineering marvel under Rohtang Pass into dramatic barren Lahaul mountainscapes.", "loc": "Sissu, Lahaul", "lat": 32.4820, "lng": 77.1240, "cost": 0.0, "dur": 140, "mode": "driving", "cat": "photo", "indoor": False},
        {"slot": "evening", "time": "06:00 PM", "title": "Mall Road Shopping for Pashminas & Kullu Shawls", "desc": "Bustling promenade with local Tibetan street food, momos, and traditional wooden handicrafts.", "loc": "Mall Road, Manali", "lat": 32.2396, "lng": 77.1887, "cost": 300.0, "dur": 100, "mode": "walking", "cat": "shopping", "indoor": True},
        # Day 3: Heritage Naggar Castle
        {"slot": "morning", "time": "09:30 AM", "title": "Naggar Castle Wood-and-Stone Architecture", "desc": "Former seat of Kullu kings built with traditional earthquake-resistant Kath-Kuni woodwork.", "loc": "Naggar, Kullu Valley", "lat": 32.1470, "lng": 77.1700, "cost": 100.0, "dur": 110, "mode": "driving", "cat": "culture", "indoor": True},
        {"slot": "afternoon", "time": "01:30 PM", "title": "Nicholas Roerich Himalayan Art Gallery", "desc": "Estate and gallery of the Russian master painter preserving ethereal Himalayan spiritual landscapes.", "loc": "Naggar Estate", "lat": 32.1440, "lng": 77.1720, "cost": 150.0, "dur": 90, "mode": "walking", "cat": "culture", "indoor": True},
        {"slot": "evening", "time": "05:30 PM", "title": "Jana Waterfall & Traditional Himachali Siddu", "desc": "Hidden forest waterfall stop tasting steamed wheat Siddu with pure ghee and walnut chutney.", "loc": "Jana Village, Naggar", "lat": 32.1380, "lng": 77.2100, "cost": 250.0, "dur": 100, "mode": "driving", "cat": "food", "indoor": False}
    ],
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
    ]
}

def _try_generate_with_gemini(destination: str, num_days: int) -> Optional[List[Dict[str, Any]]]:
    """Uses Gemini to generate an accurate, customized itinerary for ANY requested number of days."""
    api_key = (settings.GEMINI_API_KEY or "").strip()
    if not api_key or len(api_key) < 10:
        return None

    prompt = (
        f"You are a master travel planner. Generate an accurate, authentic {num_days}-day travel itinerary for {destination} as a raw JSON array. "
        f"The array MUST contain exactly {num_days} day objects (from Day 1 to Day {num_days}). "
        f"Each day object MUST have: "
        f"  - 'day_number': int (1, 2, ... {num_days})\n"
        f"  - 'title': str (e.g. 'Day 1: Historic Old Quarter & Royal Monuments')\n"
        f"  - 'theme': str (short thematic focus for the day)\n"
        f"  - 'activities': list of exactly 3 distinct items (morning, afternoon, evening)\n"
        f"Each activity item MUST include: "
        f"  - 'time_slot': 'morning' | 'afternoon' | 'evening'\n"
        f"  - 'time_str': str (e.g. '09:00 AM')\n"
        f"  - 'title': str (real specific landmark or experience in {destination})\n"
        f"  - 'description': str (compelling 1-2 sentence description)\n"
        f"  - 'location_name': str (real neighborhood or street address)\n"
        f"  - 'lat': float (accurate latitude of this spot)\n"
        f"  - 'lng': float (accurate longitude of this spot)\n"
        f"  - 'estimated_cost': float (estimated in INR)\n"
        f"  - 'duration_mins': int\n"
        f"  - 'travel_time_from_prev': str\n"
        f"  - 'transport_mode': 'walking' | 'driving' | 'transit'\n"
        f"  - 'category': 'culture' | 'nature' | 'photo' | 'food' | 'adventure'\n"
        f"  - 'is_indoor': bool\n"
        f"Return ONLY the raw JSON array. Do not include markdown backticks or commentary."
    )

    models_to_try = [settings.GEMINI_MODEL, "gemini-3.5-flash-lite", "gemini-3.1-flash-lite"]
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
                if text.startswith("```"):
                    text = re.sub(r"^```(?:json)?\s*", "", text)
                    text = re.sub(r"\s*```$", "", text)
                parsed = json.loads(text)
                if isinstance(parsed, list) and len(parsed) > 0:
                    print(f"✅ Gemini ({model_name}) synthesized authentic {len(parsed)}-day itinerary for {destination}!")
                    return parsed[:num_days]
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
    2. Respects the exact num_days requested by the customer (1 to 14 days).
    3. Falls back to geographically calibrated regional banks if offline.
    """
    # Enforce safe bounds (1 to 14 days)
    num_days = max(1, min(14, int(num_days)))
    dest_clean = destination_name.split(",")[0].strip() if destination_name else "India"
    dest_lower = dest_clean.lower()

    # 1. Try Gemini AI Generation
    ai_itinerary = _try_generate_with_gemini(destination_name, num_days)
    if ai_itinerary and len(ai_itinerary) >= 1:
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
        if k in dest_lower or dest_lower in k:
            bank_key = k
            break

    # Resolve base coordinates for destination
    base_lat, base_lng = resolve_destination_coordinates(destination_name)

    if bank_key:
        bank = REGIONAL_LANDMARK_BANKS[bank_key]
    else:
        # Build dynamic authentic bank calibrated around destination's coordinates
        bank = [
            {"slot": "morning", "time": "09:00 AM", "title": f"Historic Old Town & Heritage Architecture", "desc": f"Explore the foundational architecture, heritage squares, and vibrant morning energy of {dest_clean}.", "loc": f"Old Quarter, {dest_clean}", "lat": base_lat + 0.005, "lng": base_lng + 0.004, "cost": 500.0, "dur": 120, "mode": "walking", "cat": "culture", "indoor": False},
            {"slot": "afternoon", "time": "01:30 PM", "title": f"Local Gastronomy & Artisanal Market", "desc": f"Sample authentic regional delicacies and shop for traditional handcrafted goods in {dest_clean}.", "loc": f"Central Market Hall, {dest_clean}", "lat": base_lat - 0.003, "lng": base_lng + 0.002, "cost": 800.0, "dur": 100, "mode": "walking", "cat": "food", "indoor": True},
            {"slot": "evening", "time": "05:30 PM", "title": f"Panoramic Sunset Overlook & Evening Promenade", "desc": f"Take in sweeping golden-hour vistas as dusk settles across the scenic rooftops of {dest_clean}.", "loc": f"Skyline Vista Point, {dest_clean}", "lat": base_lat + 0.008, "lng": base_lng - 0.006, "cost": 250.0, "dur": 90, "mode": "walking", "cat": "photo", "indoor": False},
            {"slot": "morning", "time": "09:30 AM", "title": f"National Heritage Museum & Galleries", "desc": f"Discover curated historic artifacts, fine art, and archaeological treasures celebrating {dest_clean}.", "loc": f"National Museum Complex, {dest_clean}", "lat": base_lat - 0.004, "lng": base_lng - 0.005, "cost": 650.0, "dur": 110, "mode": "transit", "cat": "culture", "indoor": True},
            {"slot": "afternoon", "time": "02:00 PM", "title": f"Scenic Waterfront & Garden Promenade", "desc": f"Relax by tranquil botanical groves and scenic waterfront bridges surrounded by lush greenery.", "loc": f"Riverfront Botanical Gardens, {dest_clean}", "lat": base_lat + 0.002, "lng": base_lng + 0.007, "cost": 300.0, "dur": 90, "mode": "walking", "cat": "nature", "indoor": False},
            {"slot": "evening", "time": "06:30 PM", "title": f"Atmospheric Evening Dining & Acoustic Music", "desc": f"Unwind with signature local refreshments and dinner accompanied by regional acoustic melodies.", "loc": f"Lantern Quarter, {dest_clean}", "lat": base_lat + 0.001, "lng": base_lng - 0.003, "cost": 1200.0, "dur": 110, "mode": "walking", "cat": "food", "indoor": True},
            {"slot": "morning", "time": "08:30 AM", "title": f"Mountain Vista Trail & Viewpoint Ridge", "desc": f"Early morning scenic trail offering crisp alpine air and breathtaking horizons overlooking {dest_clean}.", "loc": f"Ridge Trailhead, {dest_clean}", "lat": base_lat + 0.012, "lng": base_lng + 0.009, "cost": 200.0, "dur": 130, "mode": "walking", "cat": "adventure", "indoor": False},
            {"slot": "afternoon", "time": "01:00 PM", "title": f"Historic Castle & Royal Citadel Tour", "desc": f"Walk through fortified ramparts and centuries of storied royalty in the heart of {dest_clean}.", "loc": f"Citadel Grounds, {dest_clean}", "lat": base_lat - 0.006, "lng": base_lng + 0.008, "cost": 750.0, "dur": 110, "mode": "transit", "cat": "culture", "indoor": True},
            {"slot": "evening", "time": "06:00 PM", "title": f"Dusk River Cruise & Waterfront Illuminations", "desc": f"Sail along the shimmering city waterways as monuments illuminate the night sky.", "loc": f"Marina Pier, {dest_clean}", "lat": base_lat + 0.003, "lng": base_lng - 0.004, "cost": 1100.0, "dur": 90, "mode": "transit", "cat": "relaxation", "indoor": False}
        ]

    try:
        start_date = datetime.date.fromisoformat(start_date_str)
    except Exception:
        start_date = datetime.date.today() + datetime.timedelta(days=7)

    itinerary = []
    bank_index = 0

    theme_cycle = [
        f"Historic Heart & Cultural Treasures of {dest_clean}",
        f"Scenic Panoramas & Authentic Gastronomy of {dest_clean}",
        f"Hidden Quarters & Golden Sunset Vistas of {dest_clean}",
        f"Nature Sanctuaries & Waterfront Charms of {dest_clean}",
        f"Local Crafts, Markets & Architectural Wonders of {dest_clean}",
        f"Off-the-Beaten-Path Secrets & Tranquil Escapes in {dest_clean}",
        f"Grand Finales & Unforgettable Memories of {dest_clean}"
    ]

    for day_idx in range(1, num_days + 1):
        cur_date = start_date + datetime.timedelta(days=day_idx - 1)
        day_title = f"Day {day_idx}: Highlights of {dest_clean}"
        theme = theme_cycle[(day_idx - 1) % len(theme_cycle)]

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
