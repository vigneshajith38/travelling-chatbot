from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from app.schemas.schemas import DestinationOut, RecommendationRequest, MoodPlanRequest
from app.services.recommendation_service import (
    CURATED_DESTINATIONS, get_recommendations, get_surprise_destination, get_hidden_gems
)
from app.services.itinerary_service import generate_trip_itinerary

router = APIRouter(prefix="/destinations", tags=["Destinations"])

@router.get("", response_model=List[DestinationOut])
def list_destinations(
    category: Optional[str] = None,
    mood: Optional[str] = None,
    search: Optional[str] = None,
    country: Optional[str] = None
):
    results = CURATED_DESTINATIONS.copy()
    
    if search:
        s = search.lower()
        results = [d for d in results if s in d["name"].lower() or s in d["description"].lower() or s in d["country"].lower()]
        
    if category and category.lower() != "all":
        c = category.lower()
        results = [d for d in results if c in d["category"].lower()]
        
    if mood:
        m = mood.lower()
        results = [d for d in results if any(m in tag.lower() for tag in d.get("mood_tags", []))]
        
    if country:
        results = [d for d in results if d["country"].lower() == country.lower()]
        
    return results

@router.post("/recommend", response_model=List[DestinationOut])
def recommend_destinations(req: RecommendationRequest):
    return get_recommendations(
        interests=req.interests,
        budget_range=req.budget_range,
        duration_days=req.duration_days,
        travellers_count=req.travellers_count,
        domestic_only=req.domestic_only,
        mood=req.mood
    )

@router.get("/surprise-me", response_model=DestinationOut)
def surprise_me():
    return get_surprise_destination()

@router.get("/hidden-gems", response_model=List[DestinationOut])
def list_hidden_gems():
    return get_hidden_gems()

@router.post("/mood-plan")
def mood_plan(req: MoodPlanRequest):
    """Translates freeform mood descriptions into destinations, style, and sample itinerary."""
    mood_str = req.mood_description.lower()
    
    # Infer interests from mood
    inferred_interests = []
    if any(w in mood_str for w in ["disconnect", "peace", "quiet", "solitude", "slow"]):
        inferred_interests.extend(["peaceful", "disconnect", "nature"])
    if any(w in mood_str for w in ["romantic", "couple", "candle", "honeymoon"]):
        inferred_interests.extend(["romantic", "luxury", "scenic"])
    if any(w in mood_str for w in ["adventure", "hike", "thrill", "road trip"]):
        inferred_interests.extend(["adventure", "mountains", "thrill"])
    if any(w in mood_str for w in ["photo", "camera", "aesthetic", "sunset"]):
        inferred_interests.extend(["photography", "scenic"])
    if not inferred_interests:
        inferred_interests = ["peaceful", "nature"]
        
    recommendations = get_recommendations(
        interests=inferred_interests,
        budget_range="moderate",
        duration_days=req.duration_days,
        travellers_count=req.travellers_count,
        domestic_only=True,
        mood=req.mood_description
    )
    
    selected_dest = recommendations[0] if recommendations else CURATED_DESTINATIONS[0]
    sample_itinerary = generate_trip_itinerary(selected_dest["name"], "2026-11-25", num_days=req.duration_days)
    
    return {
        "mood_analyzed": req.mood_description,
        "recommended_style": "Slow Scenic Exploration & Curated Vistas",
        "top_destination": selected_dest,
        "sample_itinerary": sample_itinerary,
        "curated_insights": [
            f"Tailored for '{req.mood_description}': emphasis on uncrowded morning trails and relaxed evenings.",
            "Minimal inter-city transfers to maximize on-location serenity.",
            "Handpicked boutique stays with valley or coastal panoramas."
        ]
    }
