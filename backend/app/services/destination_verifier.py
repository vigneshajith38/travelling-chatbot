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
    "madurai": {
        "canonical_name": "Madurai, Tamil Nadu",
        "destination_type": "Ancient Temple Metropolis & Cultural Capital",
        "district": "Madurai",
        "state": "Tamil Nadu",
        "country": "India",
        "lat": 9.9252,
        "lng": 78.1198,
        "elevation_m": 101,
        "terrain": "Fertile Vaigai River plains framed by historic Dravidian temple gopurams and concentric square streets",
        "official_tourism_url": "https://www.tamilnadutourism.tn.gov.in/destinations/madurai",
        "boundary_radius_km": 25.0
    },
    "kodaikanal": {
        "canonical_name": "Kodaikanal, Tamil Nadu",
        "destination_type": "Princess of Hill Stations",
        "district": "Dindigul",
        "state": "Tamil Nadu",
        "country": "India",
        "lat": 10.2381,
        "lng": 77.4892,
        "elevation_m": 2133,
        "terrain": "Palani Hills granite cliffs, forested slopes, Kurunji flower valleys, and star-shaped mountain lake",
        "official_tourism_url": "https://www.tamilnadutourism.tn.gov.in/destinations/kodaikanal",
        "boundary_radius_km": 25.0
    },
    "chikkamagaluru": {
        "canonical_name": "Chikkamagaluru (Chikmagalur), Karnataka",
        "destination_type": "Highland Coffee & Mountain Trekking Capital",
        "district": "Chikkamagaluru",
        "state": "Karnataka",
        "country": "India",
        "lat": 13.3161,
        "lng": 75.7720,
        "elevation_m": 1090,
        "terrain": "Chandra Drona Western Ghats mountain amphitheater, sprawling shade-grown coffee estates, and Karnataka's highest peaks",
        "official_tourism_url": "https://karnatakatourism.org/tour-item/chikkamagaluru/",
        "boundary_radius_km": 35.0
    },
    "chikmagalur": {
        "canonical_name": "Chikkamagaluru (Chikmagalur), Karnataka",
        "destination_type": "Highland Coffee & Mountain Trekking Capital",
        "district": "Chikkamagaluru",
        "state": "Karnataka",
        "country": "India",
        "lat": 13.3161,
        "lng": 75.7720,
        "elevation_m": 1090,
        "terrain": "Chandra Drona Western Ghats mountain amphitheater, sprawling shade-grown coffee estates, and Karnataka's highest peaks",
        "official_tourism_url": "https://karnatakatourism.org/tour-item/chikkamagaluru/",
        "boundary_radius_km": 35.0
    },
    "chickmagalur": {
        "canonical_name": "Chikkamagaluru (Chikmagalur), Karnataka",
        "destination_type": "Highland Coffee & Mountain Trekking Capital",
        "district": "Chikkamagaluru",
        "state": "Karnataka",
        "country": "India",
        "lat": 13.3161,
        "lng": 75.7720,
        "elevation_m": 1090,
        "terrain": "Chandra Drona Western Ghats mountain amphitheater, sprawling shade-grown coffee estates, and Karnataka's highest peaks",
        "official_tourism_url": "https://karnatakatourism.org/tour-item/chikkamagaluru/",
        "boundary_radius_km": 35.0
    },
    "pondicherry": {
        "canonical_name": "Puducherry (Pondicherry)",
        "destination_type": "French Colonial Heritage & Coastal Town",
        "district": "Puducherry",
        "state": "Puducherry",
        "country": "India",
        "lat": 11.9416,
        "lng": 79.8083,
        "elevation_m": 3,
        "terrain": "French Quarter boulevard grid fronting Coromandel coast with Promenade Beach and Auroville biosphere",
        "official_tourism_url": "https://pondytourism.in/",
        "boundary_radius_km": 20.0
    },
    "puducherry": {
        "canonical_name": "Puducherry (Pondicherry)",
        "destination_type": "French Colonial Heritage & Coastal Town",
        "district": "Puducherry",
        "state": "Puducherry",
        "country": "India",
        "lat": 11.9416,
        "lng": 79.8083,
        "elevation_m": 3,
        "terrain": "French Quarter boulevard grid fronting Coromandel coast with Promenade Beach and Auroville biosphere",
        "official_tourism_url": "https://pondytourism.in/",
        "boundary_radius_km": 20.0
    },
    "varanasi": {
        "canonical_name": "Varanasi (Kashi), Uttar Pradesh",
        "destination_type": "Sacred Ganga Ghats Spiritual Capital",
        "district": "Varanasi",
        "state": "Uttar Pradesh",
        "country": "India",
        "lat": 25.3176,
        "lng": 82.9739,
        "elevation_m": 80,
        "terrain": "Crescent-shaped banks of sacred river Ganga lined with 84 historic stone ghats and ancient labyrinthine alleys",
        "official_tourism_url": "https://uptourism.gov.in/en/post/varanasi",
        "boundary_radius_km": 20.0
    },
    "jaipur": {
        "canonical_name": "Jaipur (Pink City), Rajasthan",
        "destination_type": "UNESCO World Heritage Royal Capital",
        "district": "Jaipur",
        "state": "Rajasthan",
        "country": "India",
        "lat": 26.9124,
        "lng": 75.7873,
        "elevation_m": 431,
        "terrain": "Aravalli range foothills framing pink terracotta walled royal grid city, hill forts, and palace lakes",
        "official_tourism_url": "https://www.tourism.rajasthan.gov.in/jaipur.html",
        "boundary_radius_km": 30.0
    },
    "agra": {
        "canonical_name": "Agra, Uttar Pradesh",
        "destination_type": "Mughal Empire Heritage City",
        "district": "Agra",
        "state": "Uttar Pradesh",
        "country": "India",
        "lat": 27.1767,
        "lng": 78.0081,
        "elevation_m": 171,
        "terrain": "Yamuna River basin hosting the white marble Taj Mahal, red sandstone Agra Fort, and Mughal gardens",
        "official_tourism_url": "https://uptourism.gov.in/en/post/agra",
        "boundary_radius_km": 20.0
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
    },

    # Additional Verified Hubs
    "delhi": {
        "canonical_name": "New Delhi (Delhi)",
        "destination_type": "National Capital & Historic Metropolis",
        "district": "New Delhi",
        "state": "Delhi",
        "country": "India",
        "lat": 28.6139,
        "lng": 77.2090,
        "elevation_m": 216,
        "terrain": "Yamuna River basin surrounded by the historic Aravalli ridge",
        "official_tourism_url": "https://delhitourism.gov.in/",
        "boundary_radius_km": 30.0
    },
    "mumbai": {
        "canonical_name": "Mumbai (Bombay), Maharashtra",
        "destination_type": "Coastal Metropolis & Financial Capital",
        "district": "Mumbai City",
        "state": "Maharashtra",
        "country": "India",
        "lat": 19.0760,
        "lng": 72.8777,
        "elevation_m": 14,
        "terrain": "Arabian Sea peninsula of seven historic islands",
        "official_tourism_url": "https://www.maharashtratourism.gov.in/",
        "boundary_radius_km": 30.0
    },
    "chennai": {
        "canonical_name": "Chennai (Madras), Tamil Nadu",
        "destination_type": "Coastal Metropolis & Cultural Capital",
        "district": "Chennai",
        "state": "Tamil Nadu",
        "country": "India",
        "lat": 13.0827,
        "lng": 80.2707,
        "elevation_m": 6,
        "terrain": "Coromandel Coast along the Bay of Bengal with Marina Beach",
        "official_tourism_url": "https://www.tamilnadutourism.tn.gov.in/",
        "boundary_radius_km": 25.0
    },
    "kolkata": {
        "canonical_name": "Kolkata (Calcutta), West Bengal",
        "destination_type": "Cultural Metropolis & Historic Capital",
        "district": "Kolkata",
        "state": "West Bengal",
        "country": "India",
        "lat": 22.5726,
        "lng": 88.3639,
        "elevation_m": 9,
        "terrain": "Lower Gangetic Delta along the east bank of the Hooghly River",
        "official_tourism_url": "https://www.wbtourism.gov.in/",
        "boundary_radius_km": 25.0
    },
    "hyderabad": {
        "canonical_name": "Hyderabad, Telangana",
        "destination_type": "Historic City & Tech Metropolis",
        "district": "Hyderabad",
        "state": "Telangana",
        "country": "India",
        "lat": 17.3850,
        "lng": 78.4867,
        "elevation_m": 542,
        "terrain": "Hilly Deccan Plateau terrain with granitic formations and artificial lakes",
        "official_tourism_url": "https://tourism.telangana.gov.in/",
        "boundary_radius_km": 30.0
    },
    "shimla": {
        "canonical_name": "Shimla, Himachal Pradesh",
        "destination_type": "Colonial Hill Station & State Capital",
        "district": "Shimla",
        "state": "Himachal Pradesh",
        "country": "India",
        "lat": 31.1048,
        "lng": 77.1734,
        "elevation_m": 2276,
        "terrain": "Seven forested pine and deodar ridges of the northwestern Himalayas",
        "official_tourism_url": "https://himachaltourism.gov.in/",
        "boundary_radius_km": 20.0
    },
    "rishikesh": {
        "canonical_name": "Rishikesh, Uttarakhand",
        "destination_type": "Yoga Capital & Himalayan Ganga Foothills",
        "district": "Dehradun",
        "state": "Uttarakhand",
        "country": "India",
        "lat": 30.0869,
        "lng": 78.2676,
        "elevation_m": 372,
        "terrain": "Where emerald holy Ganga emerges from the Shivalik Himalayan foothills",
        "official_tourism_url": "https://uttarakhandtourism.gov.in/",
        "boundary_radius_km": 15.0
    },
    "leh": {
        "canonical_name": "Leh, Ladakh",
        "destination_type": "High-Altitude Cold Desert & Monasteries",
        "district": "Leh",
        "state": "Ladakh",
        "country": "India",
        "lat": 34.1526,
        "lng": 77.5771,
        "elevation_m": 3524,
        "terrain": "Indus river valley flanked by rugged snow-crested Karakoram and Ladakh ranges",
        "official_tourism_url": "https://ladakh.nic.in/tourism/",
        "boundary_radius_km": 30.0
    },
    "srinagar": {
        "canonical_name": "Srinagar, Jammu & Kashmir",
        "destination_type": "Himalayan Lake Valley & Summer Capital",
        "district": "Srinagar",
        "state": "Jammu and Kashmir",
        "country": "India",
        "lat": 34.0837,
        "lng": 74.7973,
        "elevation_m": 1585,
        "terrain": "Kashmir Valley basin around Dal and Nigeen lakes framed by Zabarwan mountains",
        "official_tourism_url": "https://jktourism.jk.gov.in/",
        "boundary_radius_km": 25.0
    },
    "udaipur": {
        "canonical_name": "Udaipur (City of Lakes), Rajasthan",
        "destination_type": "Historic Mewar Royal Lake City",
        "district": "Udaipur",
        "state": "Rajasthan",
        "country": "India",
        "lat": 24.5854,
        "lng": 73.7125,
        "elevation_m": 598,
        "terrain": "Interconnected lakes (Pichola, Fateh Sagar) framed by the Aravalli Hills",
        "official_tourism_url": "https://www.tourism.rajasthan.gov.in/udaipur.html",
        "boundary_radius_km": 20.0
    },
    "amritsar": {
        "canonical_name": "Amritsar, Punjab",
        "destination_type": "Spiritual Capital & Golden Temple",
        "district": "Amritsar",
        "state": "Punjab",
        "country": "India",
        "lat": 31.6340,
        "lng": 74.8723,
        "elevation_m": 234,
        "terrain": "Fertile Majha agricultural plains of Punjab",
        "official_tourism_url": "https://punjabtourism.punjab.gov.in/",
        "boundary_radius_km": 20.0
    },
    "darjeeling": {
        "canonical_name": "Darjeeling, West Bengal",
        "destination_type": "Himalayan Hill Station & Tea Capital",
        "district": "Darjeeling",
        "state": "West Bengal",
        "country": "India",
        "lat": 27.0410,
        "lng": 88.2663,
        "elevation_m": 2042,
        "terrain": "Steep emerald tea garden slopes facing panoramic views of Kangchenjunga",
        "official_tourism_url": "https://www.wbtourism.gov.in/",
        "boundary_radius_km": 20.0
    },
    "rameswaram": {
        "canonical_name": "Rameswaram, Tamil Nadu",
        "destination_type": "Sacred Island & Coastal Pilgrimage",
        "district": "Ramanathapuram",
        "state": "Tamil Nadu",
        "country": "India",
        "lat": 9.2876,
        "lng": 79.3129,
        "elevation_m": 10,
        "terrain": "Pamban Island situated between peninsular India and Sri Lanka across Gulf of Mannar",
        "official_tourism_url": "https://www.tamilnadutourism.tn.gov.in/",
        "boundary_radius_km": 15.0
    },
    "kanyakumari": {
        "canonical_name": "Kanyakumari, Tamil Nadu",
        "destination_type": "Southernmost Tip & Oceans Confluence",
        "district": "Kanyakumari",
        "state": "Tamil Nadu",
        "country": "India",
        "lat": 8.0883,
        "lng": 77.5385,
        "elevation_m": 30,
        "terrain": "Confluence point of Arabian Sea, Bay of Bengal, and Indian Ocean with rock memorials",
        "official_tourism_url": "https://www.tamilnadutourism.tn.gov.in/",
        "boundary_radius_km": 15.0
    },
    "london": {
        "canonical_name": "London",
        "destination_type": "Global Financial & Cultural Metropolis",
        "district": "Greater London",
        "state": "England",
        "country": "United Kingdom",
        "lat": 51.5074,
        "lng": -0.1278,
        "elevation_m": 25,
        "terrain": "Thames River basin with Royal parks and historic architectural quarters",
        "official_tourism_url": "https://www.visitlondon.com/",
        "boundary_radius_km": 30.0
    },
    "rome": {
        "canonical_name": "Rome",
        "destination_type": "Ancient Capital & Living Open-Air Museum",
        "district": "Lazio",
        "state": "Lazio",
        "country": "Italy",
        "lat": 41.9028,
        "lng": 12.4964,
        "elevation_m": 21,
        "terrain": "Seven historic hills overlooking the Tiber River",
        "official_tourism_url": "https://www.turismoroma.it/en",
        "boundary_radius_km": 25.0
    },
    "dubai": {
        "canonical_name": "Dubai",
        "destination_type": "Ultra-Modern Desert & Coastal Metropolis",
        "district": "Emirate of Dubai",
        "state": "Dubai",
        "country": "United Arab Emirates",
        "lat": 25.2048,
        "lng": 55.2708,
        "elevation_m": 5,
        "terrain": "Arabian Gulf coastline merging into the Arabian Desert with architectural marvels",
        "official_tourism_url": "https://www.visitdubai.com/en",
        "boundary_radius_km": 30.0
    },
    "singapore": {
        "canonical_name": "Singapore",
        "destination_type": "Island City-State & Garden Metropolis",
        "district": "Central Region",
        "state": "Singapore",
        "country": "Singapore",
        "lat": 1.3521,
        "lng": 103.8198,
        "elevation_m": 15,
        "terrain": "Tropical island with nature reserves, botanical gardens, and futuristic bayfront",
        "official_tourism_url": "https://www.visitsingapore.com/",
        "boundary_radius_km": 25.0
    },
    "new york": {
        "canonical_name": "New York City",
        "destination_type": "Global Cultural & Financial Metropolis",
        "district": "New York",
        "state": "New York",
        "country": "United States",
        "lat": 40.7128,
        "lng": -74.0060,
        "elevation_m": 10,
        "terrain": "Hudson and East River archipelago with iconic Central Park and skyscraper canyons",
        "official_tourism_url": "https://www.nyctourism.com/",
        "boundary_radius_km": 25.0
    },
    "bali": {
        "canonical_name": "Bali",
        "destination_type": "Tropical Island & Spiritual Biosphere",
        "district": "Bali Province",
        "state": "Bali",
        "country": "Indonesia",
        "lat": -8.3405,
        "lng": 115.0920,
        "elevation_m": 50,
        "terrain": "Volcanic peaks (Mount Batur, Agung), terraced rice paddies, and coral reef beaches",
        "official_tourism_url": "https://www.indonesia.travel/gb/en/destinations/bali-nusa-tenggara/bali",
        "boundary_radius_km": 40.0
    },
    "bangkok": {
        "canonical_name": "Bangkok",
        "destination_type": "Vibrant Capital & River Metropolis",
        "district": "Bangkok",
        "state": "Bangkok",
        "country": "Thailand",
        "lat": 13.7563,
        "lng": 100.5018,
        "elevation_m": 2,
        "terrain": "Chao Phraya River delta plain with canal networks and golden Buddhist wats",
        "official_tourism_url": "https://www.tourismthailand.org/Destinations/Provinces/Bangkok/219",
        "boundary_radius_km": 25.0
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
        "udhagamandalam": "ooty",
        "chikmagalur": "chikkamagaluru",
        "chickmagalur": "chikkamagaluru",
        "chikmagaluru": "chikkamagaluru",
        "chikkamagalur": "chikkamagaluru",
        "puducherry": "pondicherry",
        "kashi": "varanasi",
        "banaras": "varanasi",
        "calcutta": "kolkata",
        "bombay": "mumbai",
        "madras": "chennai",
        "new delhi": "delhi",
        "nyc": "new york",
        "mamallapuram": "mahabalipuram"
    }
    return alias_map.get(clean, clean)

# Comprehensive set of conversational words, pronouns, verbs, and domain terms that must NEVER be extracted as destinations
CONVERSATIONAL_STOPWORDS = {
    # Pronouns & determiners
    "i", "me", "my", "myself", "we", "us", "our", "ours", "ourselves",
    "you", "your", "yours", "yourself", "yourselves",
    "he", "him", "his", "himself", "she", "her", "hers", "herself",
    "it", "its", "itself", "they", "them", "their", "theirs", "themselves",
    "this", "that", "these", "those", "what", "which", "who", "whom", "whose",
    "all", "any", "both", "each", "few", "more", "most", "other", "some", "such",
    "anything", "something", "nothing", "everything", "anyone", "someone", "everyone",
    
    # Common verbs & auxiliaries
    "am", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "having", "do", "does", "did", "doing",
    "would", "should", "could", "ought", "might", "must", "shall", "will", "can",
    "prefer", "prefers", "preferred", "preferring", "preference", "preferences",
    "want", "wants", "wanted", "wanting",
    "like", "likes", "liked", "liking",
    "love", "loves", "loved", "loving",
    "hate", "hates", "hated", "hating",
    "need", "needs", "needed", "needing",
    "plan", "plans", "planned", "planning",
    "visit", "visits", "visited", "visiting",
    "travel", "travels", "traveled", "travelling",
    "go", "goes", "went", "gone", "going",
    "see", "sees", "saw", "seen", "seeing",
    "show", "shows", "showed", "showing",
    "tell", "tells", "told", "telling",
    "give", "gives", "gave", "given", "giving",
    "find", "finds", "found", "finding",
    "make", "makes", "made", "making",
    "look", "looks", "looked", "looking",
    "take", "takes", "took", "taken", "taking",
    "come", "comes", "came", "coming",
    "think", "thinks", "thought", "thinking",
    "know", "knows", "knew", "known", "knowing",
    "suggest", "suggests", "suggested", "suggesting", "suggestion", "suggestions",
    "recommend", "recommends", "recommended", "recommending", "recommendation", "recommendations",
    "help", "helps", "helped", "helping",
    "book", "books", "booked", "booking",
    "cost", "costs", "costing",
    "spend", "spends", "spent", "spending",
    "stay", "stays", "stayed", "staying",
    "eat", "eats", "ate", "eaten", "eating",
    "drink", "drinks", "drank", "drinking",
    "stop", "stops", "stopped", "stopping",
    "avoid", "avoids", "avoided", "avoiding",
    "skip", "skips", "skipped", "skipping",
    "include", "includes", "included", "including",
    "exclude", "excludes", "excluded", "excluding",
    "reduce", "reduces", "reduced", "reducing",
    "increase", "increases", "increased", "increasing",
    "change", "changes", "changed", "changing",
    "update", "updates", "updated", "updating",
    "fit", "fits", "fitted", "fitting",
    "cover", "covers", "covered", "covering",

    # Travel domain terms (nouns/adjectives)
    "trip", "trips", "tour", "tours", "vacation", "vacations", "holiday", "holidays",
    "itinerary", "itineraries", "schedule", "schedules",
    "budget", "budgets", "budgeting", "expense", "expenses", "price", "prices", "fee", "fees", "ticket", "tickets", "rate", "rates", "fare", "fares",
    "food", "foods", "dish", "dishes", "meal", "meals", "dining", "cuisine", "cuisines", "breakfast", "lunch", "dinner", "snack", "snacks",
    "cafe", "cafes", "coffee", "restaurant", "restaurants", "eatery", "eateries", "bar", "bars", "pub", "pubs",
    "hotel", "hotels", "resort", "resorts", "hostel", "hostels", "homestay", "homestays", "lodge", "lodging", "room", "rooms", "accommodation", "accommodations",
    "place", "places", "spot", "spots", "location", "locations", "destination", "destinations", "attraction", "attractions", "sight", "sights", "landmark", "landmarks", "viewpoint", "viewpoints",
    "waterfall", "waterfalls", "beach", "beaches", "mountain", "mountains", "hill", "hills", "lake", "lakes", "river", "rivers", "temple", "temples", "church", "churches", "mosque", "mosques", "museum", "museums", "fort", "forts", "palace", "palaces",
    "peaceful", "quiet", "serene", "calm", "crowded", "touristy", "offbeat", "hidden", "secret", "famous", "popular", "best", "better", "good", "bad", "cheap", "expensive", "affordable", "luxury", "safe", "safety", "danger", "scam", "scams",
    "weather", "climate", "temperature", "rain", "monsoon", "season", "winter", "summer", "autumn", "spring",
    "transit", "transport", "flight", "flights", "train", "trains", "bus", "buses", "cab", "cabs", "taxi", "taxis", "car", "drive", "driving", "walk", "walking", "route", "distance",
    "day", "days", "night", "nights", "week", "weeks", "month", "months", "weekend", "weekends", "today", "tomorrow", "tonight", "morning", "afternoon", "evening",
    "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
    "first", "second", "third", "last", "next", "previous",
    "yes", "no", "ok", "okay", "sure", "please", "thanks", "thank", "hello", "hi", "hey", "instead", "also", "with", "from", "near", "around", "about"
}

def is_conversational_phrase(text: str) -> bool:
    """Returns True if the entire text consists of English stopwords/conversational phrases rather than a destination."""
    if not text:
        return True
    words = [w.strip() for w in re.sub(r'[^\w\s]', ' ', text.lower()).split() if w.strip()]
    if not words:
        return True
    # If all words are in conversational stopwords, it is not a destination
    stopword_count = sum(1 for w in words if w in CONVERSATIONAL_STOPWORDS)
    if stopword_count == len(words):
        return True
    # If 2 or more words and at least 60% are stopwords, reject as a destination
    if len(words) >= 2 and (stopword_count / len(words)) >= 0.6:
        return True
    return False

def parse_destination_query(user_message: str) -> Dict[str, Any]:
    """
    Parses a user query using high-precision word-boundary regex scanning to identify:
    1. Single destination vs. multiple destinations (e.g. 'Trivandrum, Vagamon and Munnar').
    2. Comparison queries (e.g. 'Vagamon vs Munnar').
    3. Preserves distinct identities without cross-contaminating.
    4. Accurately rejects conversational follow-ups ('I prefer peaceful places', 'What about food?').
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
    if not recognized_destinations and not is_conversational_phrase(text):
        dest_patterns = [
            r'\b(?:plan\s+(?:a\s+)?(?:\d+[- ]?day\s+)?trip\s+to|trip\s+to|travel\s+to|visit|explore|vacation\s+in|holiday\s+in|guide\s+(?:to|for)|itinerary\s+for)\s+([A-Za-z\s,]{3,32}?)(?:\s+(?:for|with|under|in|from|at|on|\d+days?)|$|[?!.])',
            r'\b(?:places\s+(?:to\s+visit\s+)?(?:in|around|near)|sights\s+in|attractions\s+in|what\s+to\s+see\s+in|things\s+to\s+do\s+in|cafes?\s+in|restaurants?\s+in|waterfalls?\s+in)\s+([A-Za-z\s,]{3,32}?)(?:\s+(?:for|with|under|in|from|at|on|\d+days?)|$|[?!.])',
            r'\b(?:hotels?|resorts?|stay|accommodation)\s+(?:in|at|near)\s+([A-Za-z\s,]{3,30}?)(?:\s+(?:for|with|under|in|from|at|on|\d+)|$|[?!.])',
            r'\b(?:tell me about|overview of|info about|information on)\s+([A-Za-z\s,]{3,30}?)(?:\s+(?:like|for)|$|[?!.])'
        ]
        for pat in dest_patterns:
            m = re.search(pat, text_lower)
            if m:
                raw_cand = m.group(1).strip()
                clean_cand = re.sub(r'^(?:in|at|to|near|around|about|for|from)\s+', '', raw_cand, flags=re.I).strip().title()
                if not is_conversational_phrase(clean_cand) and len(clean_cand) >= 3:
                    cand_info = get_destination_identity(clean_cand)
                    if cand_info and cand_info.get("canonical_name") and cand_info.get("coordinates_verified"):
                        rec = cand_info.copy()
                        rec["key"] = normalize_destination_key(clean_cand)
                        recognized_destinations.append(rec)
                        break

    # 3. Third Pass: Bare destination only when entire input is 1-3 words and NOT a conversational sentence
    if not recognized_destinations:
        all_words = [w for w in re.sub(r'[^\w\s]', '', text_lower).split() if w]
        # Only evaluate if whole input is 1-3 words and not conversational
        if 1 <= len(all_words) <= 3 and not is_conversational_phrase(text):
            candidate_phrase = " ".join(all_words).title()
            cand_info = get_destination_identity(candidate_phrase)
            if cand_info and cand_info.get("canonical_name") and cand_info.get("coordinates_verified"):
                rec = cand_info.copy()
                rec["key"] = normalize_destination_key(candidate_phrase)
                recognized_destinations.append(rec)

    # Determine query classification
    if len(recognized_destinations) >= 2:
        query_type = "comparison" if is_comparison else "multi_destination_circuit"
    elif len(recognized_destinations) == 1:
        query_type = "single_destination"
    else:
        query_type = "conversational" if is_conversational_phrase(text) else "general_travel"

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
    Uses curated database first, dynamic geocaching, then Nominatim, and avoids fake fallback coordinates.
    Returns {} if input is conversational or cannot be verified as a geographic entity.
    """
    if not dest_name:
        return {}

    # Strip any leading prepositions
    clean_dest = re.sub(r'^(?:in|at|to|near|around|about|for|from)\s+', '', dest_name.strip(), flags=re.I).strip()
    if not clean_dest or is_conversational_phrase(clean_dest):
        return {}

    key = normalize_destination_key(clean_dest)

    if key in VERIFIED_DESTINATION_REGISTRY:
        data = VERIFIED_DESTINATION_REGISTRY[key].copy()
        data["key"] = key
        data["coordinates_verified"] = True
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
                params={"q": clean_dest, "format": "json", "addressdetails": 1, "limit": 1},
                headers={"User-Agent": "WanderWise-AI-Travel/2.0 (travel@wanderwise.com)"}
            )
            if resp.status_code == 200:
                results = resp.json()
                if results and len(results) > 0:
                    r0 = results[0]
                    # Verify it's an actual geographic place class
                    place_class = r0.get("class", "")
                    if place_class in ["place", "boundary", "natural", "landuse", "highway"]:
                        lat = float(r0["lat"])
                        lng = float(r0["lon"])
                        addr = r0.get("address", {})
                        
                        city = addr.get("city") or addr.get("town") or addr.get("village") or addr.get("county") or clean_dest.title()
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
                            "coordinates_verified": True,
                            "key": key
                        }
                        _DYNAMIC_GEOCODE_CACHE[key] = resolved
                        return resolved
    except Exception as e:
        print(f"Nominatim lookup exception for '{clean_dest}': {e}")

    # Parse state / country if comma-separated (e.g. 'Interlaken, Switzerland' or 'Kumbakonam, Tamil Nadu')
    if "," in clean_dest:
        parts = [p.strip().title() for p in clean_dest.split(",")]
        city_name = parts[0]
        inferred_state = parts[1] if len(parts) > 1 else ""
        inferred_country = parts[2] if len(parts) > 2 else ("India" if inferred_state in ["Tamil Nadu", "Karnataka", "Kerala", "Maharashtra", "Goa", "Rajasthan"] else "")

        if city_name and not is_conversational_phrase(city_name):
            return {
                "canonical_name": f"{city_name}, {inferred_state}" if inferred_state else city_name,
                "destination_type": "Travel Destination",
                "district": "",
                "state": inferred_state,
                "country": inferred_country or "World Destination",
                "lat": None,
                "lng": None,
                "elevation_m": None,
                "terrain": f"Regional terrain in {city_name}",
                "official_tourism_url": f"https://www.google.com/search?q={urllib.parse.quote(city_name + ' tourism')}",
                "boundary_radius_km": 25.0,
                "coordinates_verified": False,
                "key": key
            }

    # If unverified and not explicitly qualified, return empty dict rather than fake destination
    return {}
