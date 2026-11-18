from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.models.models import PackingItem, SavedPlace, Trip, User
from app.schemas.schemas import (
    PackingItemOut, PackingItemCreate, SavedPlaceOut, SavedPlaceCreate
)
from app.api.auth import get_current_user
from app.services.safety_service import get_destination_safety_report

router = APIRouter(prefix="", tags=["Safety, Packing & Saved Places"])

# --- Safety ---
@router.get("/safety/{destination}")
def get_safety_advisory(destination: str):
    return get_destination_safety_report(destination)

# --- Packing ---
@router.get("/trips/{trip_id}/packing", response_model=List[PackingItemOut])
def get_trip_packing_items(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(PackingItem).filter(PackingItem.trip_id == trip_id).all()

@router.post("/trips/{trip_id}/packing", response_model=PackingItemOut)
def add_packing_item(
    trip_id: int,
    item_in: PackingItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    p_item = PackingItem(
        trip_id=trip_id,
        category=item_in.category,
        item_name=item_in.item_name,
        quantity=item_in.quantity,
        is_packed=False,
        is_custom=item_in.is_custom
    )
    db.add(p_item)
    db.commit()
    db.refresh(p_item)
    return p_item

@router.put("/packing/items/{item_id}/toggle", response_model=PackingItemOut)
def toggle_packing_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item = db.query(PackingItem).filter(PackingItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.is_packed = not item.is_packed
    db.commit()
    db.refresh(item)
    return item

@router.delete("/packing/items/{item_id}")
def delete_packing_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item = db.query(PackingItem).filter(PackingItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"status": "deleted", "item_id": item_id}

# --- Saved Places ---
@router.get("/saved-places", response_model=List[SavedPlaceOut])
def get_saved_places(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(SavedPlace).filter(SavedPlace.user_id == current_user.id).order_by(SavedPlace.created_at.desc()).all()

@router.post("/saved-places", response_model=SavedPlaceOut)
def save_place(
    place_in: SavedPlaceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    place = SavedPlace(
        user_id=current_user.id,
        name=place_in.name,
        destination=place_in.destination,
        category=place_in.category,
        rating=place_in.rating,
        image_url=place_in.image_url,
        description=place_in.description,
        lat=place_in.lat,
        lng=place_in.lng,
        estimated_cost=place_in.estimated_cost,
        notes=place_in.notes
    )
    db.add(place)
    db.commit()
    db.refresh(place)
    return place

@router.delete("/saved-places/{place_id}")
def remove_saved_place(
    place_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    place = db.query(SavedPlace).filter(SavedPlace.id == place_id, SavedPlace.user_id == current_user.id).first()
    if not place:
        raise HTTPException(status_code=404, detail="Saved place not found")
    db.delete(place)
    db.commit()
    return {"status": "deleted", "place_id": place_id}

