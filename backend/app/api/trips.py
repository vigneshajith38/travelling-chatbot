import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.session import get_db
from app.models.models import Trip, ItineraryDay, ItineraryActivity, TripMember, PackingItem, User
from app.schemas.schemas import (
    TripCreate, TripUpdate, TripOut, TripDetailOut, ActivityCreate, ActivityUpdate, ActivityOut,
    WhatIfSimulateRequest, WhatIfSimulationResult
)
from app.api.auth import get_current_user
from app.services.itinerary_service import generate_trip_itinerary
from app.services.packing_service import generate_smart_packing_list
from app.services.simulator_service import simulate_trip_changes
from app.services.recommendation_service import CURATED_DESTINATIONS

router = APIRouter(prefix="/trips", tags=["Trips"])

@router.post("", response_model=TripDetailOut)
def create_trip(
    trip_in: TripCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Find matching cover image if none provided
    cover_image = trip_in.cover_image
    if not cover_image:
        for d in CURATED_DESTINATIONS:
            if d["name"].split(",")[0].lower() in trip_in.destination.lower():
                cover_image = d["image_url"]
                break
        if not cover_image:
            cover_image = "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?auto=format&fit=crop&w=1200&q=80"
            
    share_code = str(uuid.uuid4())[:8].upper()
    
    new_trip = Trip(
        user_id=current_user.id,
        title=trip_in.title,
        destination=trip_in.destination,
        country=trip_in.country,
        start_date=trip_in.start_date,
        end_date=trip_in.end_date,
        travellers_count=trip_in.travellers_count,
        budget_currency=trip_in.budget_currency,
        total_budget=trip_in.total_budget,
        estimated_cost=trip_in.total_budget * 0.9,
        travel_style=trip_in.travel_style,
        mood=trip_in.mood,
        status="planning",
        cover_image=cover_image,
        is_group=trip_in.is_group,
        share_code=share_code
    )
    db.add(new_trip)
    db.commit()
    db.refresh(new_trip)
    
    # Add organizer as first trip member
    member = TripMember(
        trip_id=new_trip.id,
        user_id=current_user.id,
        name=current_user.full_name,
        email=current_user.email,
        role="organizer",
        budget_share=new_trip.total_budget / max(1, new_trip.travellers_count),
        status="accepted"
    )
    db.add(member)
    
    # Generate itinerary days & activities
    itinerary_data = generate_trip_itinerary(new_trip.destination, new_trip.start_date, num_days=3)
    for day_data in itinerary_data:
        day_record = ItineraryDay(
            trip_id=new_trip.id,
            day_number=day_data["day_number"],
            date=day_data["date"],
            title=day_data["title"],
            theme=day_data.get("theme", ""),
            notes=day_data.get("notes", "")
        )
        db.add(day_record)
        db.commit()
        db.refresh(day_record)
        
        for act in day_data["activities"]:
            act_record = ItineraryActivity(
                day_id=day_record.id,
                time_slot=act["time_slot"],
                time_str=act["time_str"],
                title=act["title"],
                description=act["description"],
                location_name=act["location_name"],
                lat=act["lat"],
                lng=act["lng"],
                estimated_cost=act["estimated_cost"],
                duration_mins=act["duration_mins"],
                travel_time_from_prev=act["travel_time_from_prev"],
                transport_mode=act["transport_mode"],
                category=act["category"],
                is_indoor=act["is_indoor"],
                booking_url=act.get("booking_url"),
                order_index=act["order_index"]
            )
            db.add(act_record)
            
    # Auto-generate packing checklist
    pack_items = generate_smart_packing_list(
        destination=new_trip.destination,
        duration_days=3,
        travellers_count=new_trip.travellers_count,
        travel_style=new_trip.travel_style
    )
    for item in pack_items:
        p_record = PackingItem(
            trip_id=new_trip.id,
            category=item["category"],
            item_name=item["item_name"],
            quantity=item["quantity"],
            is_packed=False,
            is_custom=False
        )
        db.add(p_record)
        
    db.commit()
    db.refresh(new_trip)
    return new_trip

@router.get("", response_model=List[TripOut])
def list_trips(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Trip).filter(Trip.user_id == current_user.id)
    if status:
        query = query.filter(Trip.status == status)
    return query.order_by(Trip.created_at.desc()).all()

@router.get("/{trip_id}", response_model=TripDetailOut)
def get_trip_detail(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip

@router.put("/{trip_id}", response_model=TripOut)
def update_trip(
    trip_id: int,
    trip_in: TripUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
        
    update_data = trip_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(trip, field, val)
        
    db.commit()
    db.refresh(trip)
    return trip

@router.delete("/{trip_id}")
def delete_trip(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
        
    db.delete(trip)
    db.commit()
    return {"status": "deleted", "trip_id": trip_id}

@router.post("/{trip_id}/duplicate", response_model=TripDetailOut)
def duplicate_trip(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    original = db.query(Trip).filter(Trip.id == trip_id).first()
    if not original:
        raise HTTPException(status_code=404, detail="Trip not found")
        
    new_trip = Trip(
        user_id=current_user.id,
        title=f"Copy of {original.title}",
        destination=original.destination,
        country=original.country,
        start_date=original.start_date,
        end_date=original.end_date,
        travellers_count=original.travellers_count,
        budget_currency=original.budget_currency,
        total_budget=original.total_budget,
        estimated_cost=original.estimated_cost,
        travel_style=original.travel_style,
        mood=original.mood,
        status="planning",
        cover_image=original.cover_image,
        is_group=False,
        share_code=str(uuid.uuid4())[:8].upper()
    )
    db.add(new_trip)
    db.commit()
    db.refresh(new_trip)
    
    # Copy days and activities
    for day in original.itinerary_days:
        new_day = ItineraryDay(
            trip_id=new_trip.id,
            day_number=day.day_number,
            date=day.date,
            title=day.title,
            theme=day.theme,
            notes=day.notes
        )
        db.add(new_day)
        db.commit()
        db.refresh(new_day)
        
        for act in day.activities:
            new_act = ItineraryActivity(
                day_id=new_day.id,
                time_slot=act.time_slot,
                time_str=act.time_str,
                title=act.title,
                description=act.description,
                location_name=act.location_name,
                lat=act.lat,
                lng=act.lng,
                estimated_cost=act.estimated_cost,
                duration_mins=act.duration_mins,
                travel_time_from_prev=act.travel_time_from_prev,
                transport_mode=act.transport_mode,
                category=act.category,
                is_indoor=act.is_indoor,
                order_index=act.order_index
            )
            db.add(new_act)
            
    db.commit()
    db.refresh(new_trip)
    return new_trip

@router.post("/{trip_id}/days/{day_id}/activities", response_model=ActivityOut)
def add_activity(
    trip_id: int,
    day_id: int,
    act_in: ActivityCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    day = db.query(ItineraryDay).filter(ItineraryDay.id == day_id, ItineraryDay.trip_id == trip_id).first()
    if not day:
        raise HTTPException(status_code=404, detail="Itinerary day not found")
        
    activity = ItineraryActivity(
        day_id=day.id,
        time_slot=act_in.time_slot,
        time_str=act_in.time_str,
        title=act_in.title,
        description=act_in.description,
        location_name=act_in.location_name,
        lat=act_in.lat,
        lng=act_in.lng,
        estimated_cost=act_in.estimated_cost,
        duration_mins=act_in.duration_mins,
        travel_time_from_prev=act_in.travel_time_from_prev,
        transport_mode=act_in.transport_mode,
        category=act_in.category,
        is_indoor=act_in.is_indoor,
        booking_url=act_in.booking_url,
        order_index=act_in.order_index
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity

@router.put("/activities/{activity_id}", response_model=ActivityOut)
def update_activity(
    activity_id: int,
    act_in: ActivityUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    act = db.query(ItineraryActivity).filter(ItineraryActivity.id == activity_id).first()
    if not act:
        raise HTTPException(status_code=404, detail="Activity not found")
        
    for k, v in act_in.model_dump(exclude_unset=True).items():
        setattr(act, k, v)
        
    db.commit()
    db.refresh(act)
    return act

@router.delete("/activities/{activity_id}")
def delete_activity(
    activity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    act = db.query(ItineraryActivity).filter(ItineraryActivity.id == activity_id).first()
    if not act:
        raise HTTPException(status_code=404, detail="Activity not found")
    db.delete(act)
    db.commit()
    return {"status": "deleted", "activity_id": activity_id}

@router.post("/{trip_id}/simulate", response_model=WhatIfSimulationResult)
def run_what_if_simulation(
    trip_id: int,
    sim_in: WhatIfSimulateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
        
    duration_days = len(trip.itinerary_days) or 3
    result = simulate_trip_changes(
        original_cost=trip.total_budget,
        original_days=duration_days,
        original_travellers=trip.travellers_count,
        extra_days=sim_in.extra_days,
        budget_change=sim_in.budget_change,
        transport_mode=sim_in.transport_mode,
        extra_travellers=sim_in.extra_travellers,
        removed_destination=sim_in.removed_destination
    )
    return result

