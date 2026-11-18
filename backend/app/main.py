import os
import sqlite3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database.session import engine, Base, SessionLocal
from app.models.models import Destination, User, UserPreference, Trip, ItineraryDay, ItineraryActivity, TripMember, PackingItem, SavedPlace
from app.core.security import get_password_hash
from app.services.recommendation_service import CURATED_DESTINATIONS
from app.services.itinerary_service import generate_trip_itinerary
from app.services.packing_service import generate_smart_packing_list

# Include routers
from app.api.auth import router as auth_router
from app.api.destinations import router as destinations_router
from app.api.trips import router as trips_router
from app.api.weather import router as weather_router
from app.api.budget import router as budget_router
from app.api.group import router as group_router
from app.api.chat import router as chat_router
from app.api.safety_packing import router as safety_packing_router

# Create all tables from models
Base.metadata.create_all(bind=engine)

# Safe SQLite migration: add missing columns to existing DB
def _ensure_db_schema():
    db_path = settings.DATABASE_URL.replace("sqlite:///", "").replace("./", "")
    if not os.path.exists(db_path):
        db_path = "wanderwise.db"
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(chat_sessions)")
        existing_cols = [row[1] for row in cur.fetchall()]
        if "context_state" not in existing_cols:
            cur.execute("ALTER TABLE chat_sessions ADD COLUMN context_state TEXT DEFAULT '{}'")
            conn.commit()
            print("✅ DB migration: added context_state to chat_sessions")
        conn.close()
    except Exception as e:
        print(f"DB migration warning: {e}")

_ensure_db_schema()

app = FastAPI(
    title="WanderWise – AI-Powered Smart Travel Planner API",
    description="High-performance backend API for WanderWise AI travel platform.",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def seed_initial_data():
    db = SessionLocal()
    try:
        # 1. Seed Destinations if empty
        if db.query(Destination).count() == 0:
            for item in CURATED_DESTINATIONS:
                dest = Destination(
                    id=item["id"],
                    name=item["name"],
                    country=item["country"],
                    region=item.get("region"),
                    category=item["category"],
                    description=item["description"],
                    image_url=item["image_url"],
                    budget_level=item["budget_level"],
                    estimated_daily_budget=item["estimated_daily_budget"],
                    best_season=item["best_season"],
                    rating=item["rating"],
                    lat=item["lat"],
                    lng=item["lng"],
                    highlights=item.get("highlights", []),
                    is_hidden_gem=item.get("is_hidden_gem", False),
                    mood_tags=item.get("mood_tags", [])
                )
                db.add(dest)
            db.commit()

        # 2. Seed Default User if empty
        demo_user = db.query(User).filter(User.email == "wanderer@wanderwise.com").first()
        if not demo_user:
            demo_user = User(
                email="wanderer@wanderwise.com",
                hashed_password=get_password_hash("travel123"),
                full_name="Aarav Sharma",
                avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80"
            )
            db.add(demo_user)
            db.commit()
            db.refresh(demo_user)
            
            user_pref = UserPreference(
                user_id=demo_user.id,
                preferred_styles=["mountains", "scenic", "peaceful", "coffee", "adventure"],
                budget_level="moderate",
                travel_pace="balanced",
                preferred_currency="INR"
            )
            db.add(user_pref)
            db.commit()

        # 3. Seed Sample Trip if empty
        if db.query(Trip).count() == 0 and demo_user:
            sample_trip = Trip(
                user_id=demo_user.id,
                title="Munnar Mist & Mountain Escape",
                destination="Munnar, Kerala",
                country="India",
                start_date="2026-11-20",
                end_date="2026-11-23",
                travellers_count=3,
                budget_currency="INR",
                total_budget=22000.0,
                estimated_cost=19500.0,
                travel_style="Scenic & Nature Trails",
                mood="Tranquil & Rejuvenating",
                status="planning",
                cover_image="https://images.unsplash.com/photo-1593693397690-362cb9666fc2?auto=format&fit=crop&w=1200&q=80",
                is_group=True,
                share_code="MUNNAR26"
            )
            db.add(sample_trip)
            db.commit()
            db.refresh(sample_trip)

            # Add members
            m1 = TripMember(trip_id=sample_trip.id, user_id=demo_user.id, name="Aarav Sharma", email="wanderer@wanderwise.com", role="organizer", budget_share=7333.0, status="accepted")
            m2 = TripMember(trip_id=sample_trip.id, name="Rohan Varma", email="rohan@example.com", role="member", budget_share=7333.0, status="accepted")
            m3 = TripMember(trip_id=sample_trip.id, name="Priya Sen", email="priya@example.com", role="member", budget_share=7333.0, status="accepted")
            db.add_all([m1, m2, m3])

            # Seed Itinerary
            itinerary_data = generate_trip_itinerary(sample_trip.destination, sample_trip.start_date, num_days=3)
            for d in itinerary_data:
                day_rec = ItineraryDay(
                    trip_id=sample_trip.id,
                    day_number=d["day_number"],
                    date=d["date"],
                    title=d["title"],
                    theme=d["theme"],
                    notes=d["notes"]
                )
                db.add(day_rec)
                db.commit()
                db.refresh(day_rec)

                for act in d["activities"]:
                    act_rec = ItineraryActivity(
                        day_id=day_rec.id,
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
                        order_index=act["order_index"]
                    )
                    db.add(act_rec)

            # Seed packing items
            packing_list = generate_smart_packing_list(sample_trip.destination, 3, 3, "adventure")
            for p in packing_list:
                db.add(PackingItem(
                    trip_id=sample_trip.id,
                    category=p["category"],
                    item_name=p["item_name"],
                    quantity=p["quantity"],
                    is_packed=False,
                    is_custom=False
                ))

            # Seed saved places
            sp1 = SavedPlace(
                user_id=demo_user.id,
                name="Kolukkumalai Sunrise Point",
                destination="Munnar, Kerala",
                category="nature",
                rating=4.95,
                image_url="https://images.unsplash.com/photo-1593693397690-362cb9666fc2?auto=format&fit=crop&w=800&q=80",
                description="Highest tea estate peak with dramatic cloud sea sunrises.",
                lat=10.0880,
                lng=77.1650,
                estimated_cost=1200.0,
                notes="Must book 4x4 jeep safari in advance."
            )
            sp2 = SavedPlace(
                user_id=demo_user.id,
                name="Om Beach Cliff Trail",
                destination="Gokarna, Karnataka",
                category="beaches",
                rating=4.88,
                image_url="https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&w=800&q=80",
                description="Iconic om-shaped beach with rugged cliff pathways.",
                lat=14.5186,
                lng=74.3160,
                estimated_cost=0.0,
                notes="Sunset views from Namaste Cafe are spectacular."
            )
            db.add_all([sp1, sp2])

            db.commit()
    finally:
        db.close()

# Execute initial database seeding
seed_initial_data()

# Register API routes under /api/v1
app.include_router(auth_router, prefix="/api/v1")
app.include_router(destinations_router, prefix="/api/v1")
app.include_router(trips_router, prefix="/api/v1")
app.include_router(weather_router, prefix="/api/v1")
app.include_router(budget_router, prefix="/api/v1")
app.include_router(group_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(safety_packing_router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "WanderWise AI API",
        "version": settings.VERSION
    }

# =====================================================================
# UNIFIED FRONTEND SERVING (Direct single-port architecture)
# =====================================================================
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

if (frontend_dist / "index.html").exists():
    if (frontend_dist / "assets").exists():
        app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")

    @app.get("/")
    async def serve_root():
        return FileResponse(str(frontend_dist / "index.html"))

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api") or full_path.startswith("docs") or full_path == "openapi.json" or full_path == "health":
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Not Found")
        target_file = frontend_dist / full_path
        if target_file.is_file():
            return FileResponse(str(target_file))
        return FileResponse(str(frontend_dist / "index.html"))
else:
    @app.get("/")
    def root():
        return {
            "message": "Welcome to WanderWise AI Travel Planner API",
            "docs_url": "/docs",
            "health_url": "/health"
        }


