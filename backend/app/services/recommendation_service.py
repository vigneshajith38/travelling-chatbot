import random
from typing import List, Dict, Any, Optional

CURATED_DESTINATIONS = [
    {
        "id": 1,
        "name": "Munnar, Kerala",
        "country": "India",
        "region": "South India",
        "category": "Mountains",
        "description": "Rolling emerald tea plantations, mist-draped peaks, cool hill breezes, and tranquil lakes.",
        "image_url": "https://images.unsplash.com/photo-1593693397690-362cb9666fc2?auto=format&fit=crop&w=1200&q=80",
        "budget_level": "moderate",
        "estimated_daily_budget": 3500.0,
        "best_season": "Sep - Mar",
        "rating": 4.9,
        "lat": 10.0889,
        "lng": 77.0595,
        "highlights": ["Kolukkumalai Sunrise", "Eravikulam National Park", "Mattupetty Dam", "Lockhart Tea Factory", "Attukad Waterfalls"],
        "is_hidden_gem": False,
        "mood_tags": ["peaceful", "disconnect", "romantic", "mountains", "scenic", "photography"]
    },
    {
        "id": 2,
        "name": "Ziro Valley, Arunachal Pradesh",
        "country": "India",
        "region": "Northeast India",
        "category": "Culture",
        "description": "A UNESCO heritage candidate cradled by pine-clad hills, Apatani tribal hamlets, and lush paddy fields.",
        "image_url": "https://images.unsplash.com/photo-1626014303757-6564477575f1?auto=format&fit=crop&w=1200&q=80",
        "budget_level": "moderate",
        "estimated_daily_budget": 3200.0,
        "best_season": "Mar - Oct",
        "rating": 4.85,
        "lat": 27.5361,
        "lng": 93.8290,
        "highlights": ["Apatani Tribal Villages", "Kardo Shiva Lingam", "Talo Village Walks", "Pine Groves of Tarin", "Local Rice Wine Tastings"],
        "is_hidden_gem": True,
        "mood_tags": ["disconnect", "cultural", "offbeat", "peaceful", "nature", "photography"]
    },
    {
        "id": 3,
        "name": "Gokarna, Karnataka",
        "country": "India",
        "region": "South India",
        "category": "Beaches",
        "description": "Laidback coastline where coastal cliffs meet golden sands, offering soulful sunsets and peaceful beach treks.",
        "image_url": "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&w=1200&q=80",
        "budget_level": "budget",
        "estimated_daily_budget": 2400.0,
        "best_season": "Oct - Mar",
        "rating": 4.8,
        "lat": 14.5479,
        "lng": 74.3188,
        "highlights": ["Om Beach Cliff Trek", "Half Moon Beach", "Paradise Beach Boat Ride", "Kudle Beach Sunset Cafes", "Mahabaleshwar Temple"],
        "is_hidden_gem": False,
        "mood_tags": ["relaxation", "beaches", "budget", "romantic", "peaceful", "adventure"]
    },
    {
        "id": 4,
        "name": "Spiti Valley, Himachal Pradesh",
        "country": "India",
        "region": "North India",
        "category": "Adventure",
        "description": "High-altitude desert wonderland featuring ancient Tibetan monasteries, star-lit skies, and rugged canyons.",
        "image_url": "https://images.unsplash.com/photo-1596895111956-bf1cf0599ce5?auto=format&fit=crop&w=1200&q=80",
        "budget_level": "moderate",
        "estimated_daily_budget": 3800.0,
        "best_season": "May - Oct",
        "rating": 4.95,
        "lat": 32.2461,
        "lng": 78.0349,
        "highlights": ["Key Gompa Monastery", "Chandratal Lake Camping", "Highest Post Office Hikkim", "Kaza Bazaar", "Chicham Suspension Bridge"],
        "is_hidden_gem": False,
        "mood_tags": ["adventure", "road trip", "disconnect", "photography", "mountains", "thrill"]
    },
    {
        "id": 5,
        "name": "Udaipur, Rajasthan",
        "country": "India",
        "region": "West India",
        "category": "Romantic getaways",
        "description": "The City of Lakes with glittering palaces, heritage havelis, rooftop candlelit dining, and serene boat cruises.",
        "image_url": "https://images.unsplash.com/photo-1615836245337-f5b9b2303f10?auto=format&fit=crop&w=1200&q=80",
        "budget_level": "luxury",
        "estimated_daily_budget": 5500.0,
        "best_season": "Oct - Mar",
        "rating": 4.88,
        "lat": 24.5854,
        "lng": 73.7125,
        "highlights": ["City Palace Lake View", "Lake Pichola Sunset Boat Ride", "Jag Mandir Island", "Saheliyon Ki Bari", "Bagore Ki Haveli Dance"],
        "is_hidden_gem": False,
        "mood_tags": ["romantic", "luxury", "cultural", "photography", "relaxation", "food"]
    },
    {
        "id": 6,
        "name": "Coorg (Kodagu), Karnataka",
        "country": "India",
        "region": "South India",
        "category": "Relaxation",
        "description": "Scotland of India with aromatic coffee plantations, spice trails, gushing waterfalls, and tranquil homestays.",
        "image_url": "https://images.unsplash.com/photo-1598091383021-15ddea10925d?auto=format&fit=crop&w=1200&q=80",
        "budget_level": "moderate",
        "estimated_daily_budget": 3400.0,
        "best_season": "Oct - Apr",
        "rating": 4.78,
        "lat": 12.3375,
        "lng": 75.8069,
        "highlights": ["Coffee Plantation Tour", "Abbey Falls", "Raja's Seat Sunset", "Namdroling Golden Temple", "Dubare Elephant Camp"],
        "is_hidden_gem": False,
        "mood_tags": ["relaxation", "coffee", "mountains", "peaceful", "romantic", "nature"]
    },
    {
        "id": 7,
        "name": "Chopta & Tungnath, Uttarakhand",
        "country": "India",
        "region": "North India",
        "category": "Mountains",
        "description": "Known as the Mini Switzerland of India, offering meadows of alpine flowers and the highest Shiva temple on earth.",
        "image_url": "https://images.unsplash.com/photo-1589182373726-e4f658ab50f0?auto=format&fit=crop&w=1200&q=80",
        "budget_level": "budget",
        "estimated_daily_budget": 2200.0,
        "best_season": "Apr - Nov",
        "rating": 4.9,
        "lat": 30.4878,
        "lng": 79.1762,
        "highlights": ["Tungnath Temple Trek", "Chandrashila 360-deg Peak", "Deoriatal Lake Reflection", "Rohini Bugyal Meadows", "Campfire Stargazing"],
        "is_hidden_gem": True,
        "mood_tags": ["mountains", "adventure", "disconnect", "photography", "peaceful", "budget"]
    },
    {
        "id": 8,
        "name": "Pondicherry (Puducherry)",
        "country": "India",
        "region": "South India",
        "category": "Cultural experiences",
        "description": "Charming French Quarter lanes with pastel bougainvillea villas, indie cafes, seaside promenade, and spiritual ashrams.",
        "image_url": "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&w=1200&q=80",
        "budget_level": "moderate",
        "estimated_daily_budget": 3200.0,
        "best_season": "Oct - Mar",
        "rating": 4.75,
        "lat": 11.9416,
        "lng": 79.8083,
        "highlights": ["French Quarter Cycle Tour", "Promenade Beachfront", "Auroville Matrimandir", "Artisan Boulangeries", "Serenity Beach Surfing"],
        "is_hidden_gem": False,
        "mood_tags": ["cultural", "food", "cafes", "romantic", "relaxation", "photography"]
    },
    {
        "id": 9,
        "name": "Tirthan Valley, Himachal Pradesh",
        "country": "India",
        "region": "North India",
        "category": "Hidden Gems",
        "description": "Pristine gateway to the Great Himalayan National Park with trout-filled streams, traditional wooden chalets, and quiet serenity.",
        "image_url": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1200&q=80",
        "budget_level": "moderate",
        "estimated_daily_budget": 2900.0,
        "best_season": "Mar - Jun, Sep - Nov",
        "rating": 4.92,
        "lat": 31.6428,
        "lng": 77.3468,
        "highlights": ["Chhoie Waterfall Hike", "Jalori Pass & Serolsar Lake", "River Trout Fishing", "Gushaini Riverside Walks", "GHNP Eco Zone Treks"],
        "is_hidden_gem": True,
        "mood_tags": ["disconnect", "peaceful", "nature", "mountains", "scenic", "offbeat"]
    },
    {
        "id": 10,
        "name": "Varkala, Kerala",
        "country": "India",
        "region": "South India",
        "category": "Beaches",
        "description": "Dramatic red laterite cliffs towering over the Arabian Sea, vibrant cliff-top cafes, and bohemian coastal vibes.",
        "image_url": "https://images.unsplash.com/photo-1590523741831-ab7e8b8f9c7f?auto=format&fit=crop&w=1200&q=80",
        "budget_level": "budget",
        "estimated_daily_budget": 2600.0,
        "best_season": "Nov - Mar",
        "rating": 4.82,
        "lat": 8.7379,
        "lng": 76.7163,
        "highlights": ["North Cliff Promenade", "Odayam Beach Sunset", "Kappil Beach & Backwater Lake", "Cliff Yoga Sessions", "Janardhana Swamy Temple"],
        "is_hidden_gem": False,
        "mood_tags": ["beaches", "relaxation", "food", "budget", "romantic", "photography"]
    },
    {
        "id": 11,
        "name": "Kyoto, Japan",
        "country": "Japan",
        "region": "East Asia",
        "category": "Cultural experiences",
        "description": "Ancient imperial capital with thousands of classical Buddhist temples, bamboo groves, sublime gardens, and traditional geisha tea houses.",
        "image_url": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=1200&q=80",
        "budget_level": "luxury",
        "estimated_daily_budget": 12000.0,
        "best_season": "Mar - May, Oct - Nov",
        "rating": 4.96,
        "lat": 35.0116,
        "lng": 135.7681,
        "highlights": ["Fushimi Inari-taisha Torii Gates", "Arashiyama Bamboo Grove", "Kinkaku-ji Golden Pavilion", "Gion Historic Lantern Walk", "Matcha Ceremonies"],
        "is_hidden_gem": False,
        "mood_tags": ["cultural", "photography", "peaceful", "food", "romantic"]
    },
    {
        "id": 12,
        "name": "Bali (Ubud & Nusa), Indonesia",
        "country": "Indonesia",
        "region": "Southeast Asia",
        "category": "Relaxation",
        "description": "Island of Gods boasting cascading green rice terraces, clifftop shrines, sacred waterfall pools, and wellness sanctuaries.",
        "image_url": "https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&w=1200&q=80",
        "budget_level": "moderate",
        "estimated_daily_budget": 4500.0,
        "best_season": "Apr - Oct",
        "rating": 4.87,
        "lat": -8.5069,
        "lng": 115.2625,
        "highlights": ["Tegallalang Rice Terraces", "Campuhan Ridge Walk", "Uluwatu Sunset Kecak Dance", "Tirta Empul Holy Springs", "Kelingking Beach Vista"],
        "is_hidden_gem": False,
        "mood_tags": ["relaxation", "nature", "beaches", "wellness", "romantic", "adventure"]
    }
]

def score_destination(dest: Dict[str, Any], interests: List[str], budget_level: Optional[str], mood: Optional[str]) -> int:
    score = 70
    
    # Interest matching
    dest_tags = [t.lower() for t in dest.get("mood_tags", [])] + [dest["category"].lower()]
    for interest in interests:
        interest_lower = interest.lower()
        if any(interest_lower in t or t in interest_lower for t in dest_tags):
            score += 8
            
    # Budget compatibility
    if budget_level:
        if dest["budget_level"] == budget_level:
            score += 15
        elif (budget_level == "luxury" and dest["budget_level"] in ["moderate", "luxury"]) or \
             (budget_level == "budget" and dest["budget_level"] == "budget"):
            score += 10
            
    # Mood matching
    if mood:
        mood_words = mood.lower().replace(",", " ").split()
        for word in mood_words:
            if len(word) > 3 and any(word in t for t in dest_tags):
                score += 6
                
    # Rating boost
    score += int((dest.get("rating", 4.5) - 4.0) * 10)
    
    return min(99, max(65, score))

def get_recommendations(
    interests: List[str],
    budget_range: Optional[str] = "moderate",
    duration_days: int = 4,
    travellers_count: int = 2,
    domestic_only: bool = True,
    mood: Optional[str] = None
) -> List[Dict[str, Any]]:
    results = []
    
    for dest in CURATED_DESTINATIONS:
        if domestic_only and dest["country"] != "India":
            continue
            
        match_score = score_destination(dest, interests, budget_range, mood)
        
        # Build intelligent reason
        reasons = []
        if any(i.lower() in [t.lower() for t in dest["mood_tags"]] for i in interests):
            reasons.append(f"Strongly matches your interest in {', '.join(interests[:2])}")
        if dest["budget_level"] == budget_range:
            reasons.append(f"Ideal {dest['budget_level']} daily spending tier")
        if dest.get("is_hidden_gem"):
            reasons.append("Offbeat tranquil haven away from mass tourism crowds")
        if not reasons:
            reasons.append(f"High visitor satisfaction score of {dest['rating']}/5.0")
            
        why_selected = " • ".join(reasons)
        
        item = dest.copy()
        item["match_score"] = match_score
        item["why_selected"] = why_selected
        results.append(item)
        
    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results

def get_surprise_destination() -> Dict[str, Any]:
    dest = random.choice(CURATED_DESTINATIONS).copy()
    dest["match_score"] = 98
    dest["why_selected"] = "Surprise AI pick selected for peak aesthetic vibes, scenic vistas, and unforgettable experiences!"
    return dest

def get_hidden_gems() -> List[Dict[str, Any]]:
    gems = [d for d in CURATED_DESTINATIONS if d.get("is_hidden_gem")]
    return gems if gems else CURATED_DESTINATIONS[:3]

