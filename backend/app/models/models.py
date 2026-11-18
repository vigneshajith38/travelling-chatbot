import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
)
from sqlalchemy.orm import relationship
from app.database.session import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    preferences = relationship("UserPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    trips = relationship("Trip", back_populates="owner", cascade="all, delete-orphan")
    saved_places = relationship("SavedPlace", back_populates="user", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")

class UserPreference(Base):
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    preferred_styles = Column(JSON, default=list) # e.g. ["mountains", "relaxation", "food"]
    budget_level = Column(String(50), default="moderate") # budget, moderate, luxury
    travel_pace = Column(String(50), default="balanced") # relaxed, balanced, packed
    dietary_preferences = Column(String(255), default="none")
    preferred_currency = Column(String(10), default="INR")
    
    user = relationship("User", back_populates="preferences")

class Destination(Base):
    __tablename__ = "destinations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    country = Column(String(100), nullable=False, index=True)
    region = Column(String(100), nullable=True)
    category = Column(String(100), nullable=False) # Adventure, Beaches, Mountains, Romantic, Culture, Food, Relaxation, Budget
    description = Column(Text, nullable=False)
    image_url = Column(String(500), nullable=False)
    budget_level = Column(String(50), default="moderate")
    estimated_daily_budget = Column(Float, default=3000.0)
    best_season = Column(String(100), default="Oct - Mar")
    rating = Column(Float, default=4.8)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    highlights = Column(JSON, default=list)
    is_hidden_gem = Column(Boolean, default=False)
    mood_tags = Column(JSON, default=list)

class Trip(Base):
    __tablename__ = "trips"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    destination = Column(String(255), nullable=False)
    country = Column(String(100), default="India")
    start_date = Column(String(50), nullable=False)
    end_date = Column(String(50), nullable=False)
    travellers_count = Column(Integer, default=1)
    budget_currency = Column(String(10), default="INR")
    total_budget = Column(Float, default=20000.0)
    estimated_cost = Column(Float, default=18000.0)
    travel_style = Column(String(100), default="Balanced Adventure")
    mood = Column(String(100), default="Peaceful & Scenic")
    status = Column(String(50), default="planning") # planning, confirmed, completed, archived
    cover_image = Column(String(500), nullable=True)
    is_group = Column(Boolean, default=False)
    share_code = Column(String(50), unique=True, index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    owner = relationship("User", back_populates="trips")
    itinerary_days = relationship("ItineraryDay", back_populates="trip", cascade="all, delete-orphan", order_by="ItineraryDay.day_number")
    members = relationship("TripMember", back_populates="trip", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="trip", cascade="all, delete-orphan")
    group_votes = relationship("GroupVote", back_populates="trip", cascade="all, delete-orphan")
    packing_items = relationship("PackingItem", back_populates="trip", cascade="all, delete-orphan")
    emergency_contacts = relationship("EmergencyContact", back_populates="trip", cascade="all, delete-orphan")

class TripMember(Base):
    __tablename__ = "trip_members"
    
    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    role = Column(String(50), default="member") # organizer, editor, viewer, member
    budget_share = Column(Float, default=0.0)
    status = Column(String(50), default="accepted") # invited, accepted, declined
    
    trip = relationship("Trip", back_populates="members")

class ItineraryDay(Base):
    __tablename__ = "itinerary_days"
    
    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id", ondelete="CASCADE"), nullable=False)
    day_number = Column(Integer, nullable=False)
    date = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    theme = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    
    trip = relationship("Trip", back_populates="itinerary_days")
    activities = relationship("ItineraryActivity", back_populates="day", cascade="all, delete-orphan", order_by="ItineraryActivity.order_index")

class ItineraryActivity(Base):
    __tablename__ = "itinerary_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    day_id = Column(Integer, ForeignKey("itinerary_days.id", ondelete="CASCADE"), nullable=False)
    time_slot = Column(String(50), nullable=False) # morning, afternoon, evening
    time_str = Column(String(50), nullable=False) # e.g. "09:00 AM"
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    location_name = Column(String(255), nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    estimated_cost = Column(Float, default=0.0)
    duration_mins = Column(Integer, default=90)
    travel_time_from_prev = Column(String(50), default="15 mins")
    transport_mode = Column(String(50), default="walking") # walking, driving, transit
    category = Column(String(100), default="sightseeing") # nature, food, culture, adventure, relaxation, photo
    is_indoor = Column(Boolean, default=False)
    booking_url = Column(String(500), nullable=True)
    order_index = Column(Integer, default=0)
    
    day = relationship("ItineraryDay", back_populates="activities")

class SavedPlace(Base):
    __tablename__ = "saved_places"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    destination = Column(String(255), nullable=False)
    category = Column(String(100), default="attraction")
    rating = Column(Float, default=4.7)
    image_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    estimated_cost = Column(Float, default=0.0)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    user = relationship("User", back_populates="saved_places")

class Expense(Base):
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id", ondelete="CASCADE"), nullable=False)
    payer_id = Column(Integer, nullable=True)
    payer_name = Column(String(255), default="Me")
    category = Column(String(100), nullable=False) # Transportation, Accommodation, Food, Activities, Shopping, Miscellaneous, Emergency reserve
    title = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="INR")
    split_type = Column(String(50), default="equal") # equal, individual, custom
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    trip = relationship("Trip", back_populates="expenses")

class GroupVote(Base):
    __tablename__ = "group_votes"
    
    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id", ondelete="CASCADE"), nullable=False)
    member_id = Column(Integer, nullable=True)
    member_name = Column(String(255), nullable=False)
    item_type = Column(String(50), default="activity") # destination, activity, hotel, date
    item_name = Column(String(255), nullable=False)
    vote = Column(String(20), default="up") # up, down, neutral
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    trip = relationship("Trip", back_populates="group_votes")

class PackingItem(Base):
    __tablename__ = "packing_items"
    
    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id", ondelete="CASCADE"), nullable=False)
    category = Column(String(100), nullable=False) # Clothing, Toiletries, Electronics, Documents, Medicines, Activity
    item_name = Column(String(255), nullable=False)
    is_packed = Column(Boolean, default=False)
    quantity = Column(Integer, default=1)
    is_custom = Column(Boolean, default=False)
    
    trip = relationship("Trip", back_populates="packing_items")

class EmergencyContact(Base):
    __tablename__ = "emergency_contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    relation = Column(String(100), nullable=False)
    phone = Column(String(50), nullable=False)
    notes = Column(Text, nullable=True)
    
    trip = relationship("Trip", back_populates="emergency_contacts")

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(String(100), primary_key=True)
    trip_id = Column(Integer, ForeignKey("trips.id", ondelete="SET NULL"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), default="New Travel Conversation")
    context_state = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan", order_by="ChatMessage.created_at")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(50), nullable=False) # user, assistant, system
    content = Column(Text, nullable=False)
    structured_type = Column(String(50), nullable=True) # destination_list, itinerary_preview, budget_summary, weather_alert, action_confirm
    structured_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    session = relationship("ChatSession", back_populates="messages")

