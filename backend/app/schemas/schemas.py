from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# ----------------- User & Auth Schemas -----------------
class UserPreferenceSchema(BaseModel):
    preferred_styles: List[str] = ["mountains", "relaxation", "food"]
    budget_level: str = "moderate"
    travel_pace: str = "balanced"
    dietary_preferences: str = "none"
    preferred_currency: str = "INR"

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    preferences: Optional[UserPreferenceSchema] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    avatar_url: Optional[str] = None
    preferences: Optional[UserPreferenceSchema] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

# ----------------- Destination Schemas -----------------
class DestinationOut(BaseModel):
    id: int
    name: str
    country: str
    region: Optional[str] = None
    category: str
    description: str
    image_url: str
    budget_level: str
    estimated_daily_budget: float
    best_season: str
    rating: float
    lat: float
    lng: float
    highlights: List[str] = []
    is_hidden_gem: bool = False
    mood_tags: List[str] = []
    match_score: Optional[int] = None
    why_selected: Optional[str] = None
    
    class Config:
        from_attributes = True

class RecommendationRequest(BaseModel):
    interests: List[str] = ["nature", "culture"]
    budget_range: Optional[str] = "moderate" # budget, moderate, luxury
    duration_days: int = 4
    travellers_count: int = 2
    travel_type: Optional[str] = "friends" # solo, couples, friends, family
    origin: Optional[str] = "Mumbai"
    domestic_only: bool = True
    mood: Optional[str] = None

class MoodPlanRequest(BaseModel):
    mood_description: str
    duration_days: int = 4
    budget_total: Optional[float] = 25000.0
    travellers_count: int = 2
    origin: Optional[str] = "Bengaluru"

# ----------------- Itinerary & Activity Schemas -----------------
class ActivityCreate(BaseModel):
    time_slot: str # morning, afternoon, evening
    time_str: str = "10:00 AM"
    title: str
    description: Optional[str] = None
    location_name: str
    lat: float
    lng: float
    estimated_cost: float = 0.0
    duration_mins: int = 90
    travel_time_from_prev: str = "15 mins"
    transport_mode: str = "walking"
    category: str = "sightseeing"
    is_indoor: bool = False
    booking_url: Optional[str] = None
    order_index: int = 0

class ActivityUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    time_slot: Optional[str] = None
    time_str: Optional[str] = None
    estimated_cost: Optional[float] = None
    duration_mins: Optional[int] = None
    transport_mode: Optional[str] = None
    is_indoor: Optional[bool] = None
    order_index: Optional[int] = None

class ActivityOut(BaseModel):
    id: int
    day_id: int
    time_slot: str
    time_str: str
    title: str
    description: Optional[str] = None
    location_name: str
    lat: float
    lng: float
    estimated_cost: float
    duration_mins: int
    travel_time_from_prev: str
    transport_mode: str
    category: str
    is_indoor: bool
    booking_url: Optional[str] = None
    order_index: int
    
    class Config:
        from_attributes = True

class DayOut(BaseModel):
    id: int
    trip_id: int
    day_number: int
    date: str
    title: str
    theme: Optional[str] = None
    notes: Optional[str] = None
    activities: List[ActivityOut] = []
    
    class Config:
        from_attributes = True

# ----------------- Trip Schemas -----------------
class TripCreate(BaseModel):
    title: str
    destination: str
    country: str = "India"
    start_date: str
    end_date: str
    travellers_count: int = 1
    budget_currency: str = "INR"
    total_budget: float = 20000.0
    travel_style: str = "Balanced Adventure"
    mood: Optional[str] = "Scenic & Peaceful"
    cover_image: Optional[str] = None
    is_group: bool = False

class TripUpdate(BaseModel):
    title: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    total_budget: Optional[float] = None
    travel_style: Optional[str] = None
    status: Optional[str] = None
    cover_image: Optional[str] = None

class TripMemberOut(BaseModel):
    id: int
    trip_id: int
    user_id: Optional[int] = None
    name: str
    email: str
    role: str
    budget_share: float
    status: str
    
    class Config:
        from_attributes = True

class ExpenseOut(BaseModel):
    id: int
    trip_id: int
    payer_id: Optional[int] = None
    payer_name: str
    category: str
    title: str
    amount: float
    currency: str
    split_type: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ExpenseCreate(BaseModel):
    payer_name: str = "Me"
    category: str
    title: str
    amount: float
    currency: str = "INR"
    split_type: str = "equal"

class PackingItemOut(BaseModel):
    id: int
    trip_id: int
    category: str
    item_name: str
    is_packed: bool
    quantity: int
    is_custom: bool
    
    class Config:
        from_attributes = True

class PackingItemCreate(BaseModel):
    category: str
    item_name: str
    quantity: int = 1
    is_custom: bool = True

class TripOut(BaseModel):
    id: int
    user_id: int
    title: str
    destination: str
    country: str
    start_date: str
    end_date: str
    travellers_count: int
    budget_currency: str
    total_budget: float
    estimated_cost: float
    travel_style: str
    mood: Optional[str] = None
    status: str
    cover_image: Optional[str] = None
    is_group: bool
    share_code: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class TripDetailOut(TripOut):
    itinerary_days: List[DayOut] = []
    members: List[TripMemberOut] = []
    expenses: List[ExpenseOut] = []
    packing_items: List[PackingItemOut] = []

# ----------------- What-If Simulator Schema -----------------
class WhatIfSimulateRequest(BaseModel):
    trip_id: int
    extra_days: int = 0
    budget_change: float = 0.0
    transport_mode: Optional[str] = None # flight, train, drive
    extra_travellers: int = 0
    removed_destination: Optional[str] = None

class WhatIfSimulationResult(BaseModel):
    original_cost: float
    new_cost: float
    cost_difference: float
    original_duration_days: int
    new_duration_days: int
    transport_impact: str
    per_person_cost: float
    recommendations: List[str]
    feasibility_status: str # "Within Budget", "Slight Overrun", "High Overrun"

# ----------------- Dynamic Weather Replan -----------------
class WeatherReplanRequest(BaseModel):
    trip_id: int
    day_number: int
    current_weather_condition: str = "Rain" # Rain, Storm, Heatwave, Cold

# ----------------- Group Collaboration -----------------
class GroupInviteRequest(BaseModel):
    name: str
    email: str
    role: str = "member"

class GroupVoteCreate(BaseModel):
    item_type: str
    item_name: str
    vote: str # up, down
    comment: Optional[str] = None

class GroupVoteOut(BaseModel):
    id: int
    trip_id: int
    member_name: str
    item_type: str
    item_name: str
    vote: str
    comment: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# ----------------- Saved Places -----------------
class SavedPlaceCreate(BaseModel):
    name: str
    destination: str
    category: str = "attraction"
    rating: float = 4.8
    image_url: Optional[str] = None
    description: Optional[str] = None
    lat: float
    lng: float
    estimated_cost: float = 0.0
    notes: Optional[str] = None

class SavedPlaceOut(BaseModel):
    id: int
    user_id: int
    name: str
    destination: str
    category: str
    rating: float
    image_url: Optional[str] = None
    description: Optional[str] = None
    lat: float
    lng: float
    estimated_cost: float
    notes: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# ----------------- Chatbot Schemas -----------------
class ChatQueryRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    trip_id: Optional[int] = None
    context_destination: Optional[str] = None
    deep_search: bool = False

class ChatMessageOut(BaseModel):
    id: int
    session_id: str
    role: str
    content: str
    structured_type: Optional[str] = None
    structured_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class ChatSessionOut(BaseModel):
    id: str
    trip_id: Optional[int] = None
    title: str
    context_state: Optional[Dict[str, Any]] = None
    created_at: datetime
    messages: List[ChatMessageOut] = []
    
    class Config:
        from_attributes = True
