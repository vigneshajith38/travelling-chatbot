from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.models import Trip, ItineraryDay, ItineraryActivity
from app.services.weather_service import get_live_weather
from app.services.routing_service import calculate_route
from app.services.itinerary_service import replan_day_for_weather
from app.schemas.schemas import WeatherReplanRequest

router = APIRouter(prefix="/weather", tags=["Weather & Routing"])

@router.get("")
async def get_weather_forecast(lat: float = 10.0889, lng: float = 77.0595, days: int = 5):
    return await get_live_weather(lat, lng, days)

@router.get("/route")
async def get_route_details(
    origin_lat: float = 10.0889,
    origin_lng: float = 77.0595,
    dest_lat: float = 10.1500,
    dest_lng: float = 77.0600,
    mode: str = "driving"
):
    return await calculate_route((origin_lat, origin_lng), (dest_lat, dest_lng), mode)

@router.post("/replan-day")
def replan_rainy_day(req: WeatherReplanRequest, db: Session = Depends(get_db)):
    """
    Identifies affected outdoor activities on a rainy day, replaces with indoor alternatives,
    and updates the database schedule with clear rationale.
    """
    trip = db.query(Trip).filter(Trip.id == req.trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
        
    day = db.query(ItineraryDay).filter(ItineraryDay.trip_id == req.trip_id, ItineraryDay.day_number == req.day_number).first()
    if not day:
        raise HTTPException(status_code=404, detail=f"Day {req.day_number} not found for this trip")
        
    current_acts = [
        {
            "id": a.id,
            "time_slot": a.time_slot,
            "time_str": a.time_str,
            "title": a.title,
            "desc": a.description,
            "location_name": a.location_name,
            "lat": a.lat,
            "lng": a.lng,
            "cost": a.estimated_cost,
            "dur": a.duration_mins,
            "mode": a.transport_mode,
            "category": a.category,
            "cat": a.category,
            "is_indoor": a.is_indoor
        }
        for a in day.activities
    ]
    
    replanned_acts = replan_day_for_weather(current_acts, req.current_weather_condition)
    
    # Update in database
    for idx, act_data in enumerate(replanned_acts):
        if idx < len(day.activities):
            db_act = day.activities[idx]
            db_act.title = act_data["title"]
            db_act.description = act_data.get("description") or act_data.get("desc")
            db_act.location_name = act_data["location_name"]
            db_act.is_indoor = act_data["is_indoor"]
            db_act.category = act_data.get("category", act_data.get("cat", "culture"))
            db_act.estimated_cost = act_data.get("estimated_cost", db_act.estimated_cost)
            
    day.theme = f"Sheltered Cultural Discovery ({req.current_weather_condition} Adaptive Schedule)"
    day.notes = f"Adapted for {req.current_weather_condition}: outdoor viewpoints and nature hikes replaced with heritage indoor museums, artisanal cafes, and covered markets."
    db.commit()
    
    return {
        "status": "success",
        "day_number": req.day_number,
        "weather_condition": req.current_weather_condition,
        "message": f"Successfully shifted Day {req.day_number} outdoor activities to cozy indoor cultural stops.",
        "updated_day": day
    }
