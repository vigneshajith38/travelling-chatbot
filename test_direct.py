import sys
import os
sys.path.insert(0, os.path.abspath('backend'))

from app.api.destinations import list_destinations, recommend_destinations, surprise_me, list_hidden_gems
from app.schemas.schemas import RecommendationRequest, TripCreate, WhatIfSimulateRequest, ExpenseCreate, WeatherReplanRequest, GroupInviteRequest
from app.database.session import SessionLocal
from app.api.trips import create_trip, list_trips, get_trip_detail, run_what_if_simulation
from app.api.budget import get_trip_budget_summary, add_trip_expense
from app.api.weather import replan_rainy_day
from app.api.group import invite_group_member, calculate_group_settlements
from app.api.safety_packing import get_safety_advisory, toggle_packing_item
from app.api.auth import get_current_user
from app.services.ai_service import generate_conversational_response

def run_full_direct_suite():
    print("🚀 Running WanderWise Full End-to-End Direct Integration Test Suite...")
    db = SessionLocal()
    user = get_current_user(token=None, db=db)
    print(f"  ✓ User session active: {user.full_name} ({user.email})")

    # 1. Destinations & Discovery
    dests = list_destinations()
    assert len(dests) >= 10
    print(f"  ✓ Loaded {len(dests)} curated destinations")

    # 2. Recommendations
    req = RecommendationRequest(interests=["mountains", "scenic"], duration_days=3, travellers_count=2)
    recs = recommend_destinations(req)
    assert len(recs) > 0
    print(f"  ✓ Recommendations engine returned top match: {recs[0]['name']} ({recs[0]['match_score']}%)")

    # 3. Surprise Me
    surprise = surprise_me()
    assert surprise["match_score"] == 98
    print(f"  ✓ 'Surprise Me' generated: {surprise['name']}")

    # 4. Hidden Gems
    gems = list_hidden_gems()
    assert len(gems) > 0
    print(f"  ✓ Found {len(gems)} offbeat hidden gems")

    # 5. Create Trip & Auto-generate Itinerary + Packing list
    new_trip = create_trip(
        TripCreate(
            title="Munnar Tea Mountain Expedition",
            destination="Munnar, Kerala",
            start_date="2026-11-20",
            end_date="2026-11-23",
            travellers_count=3,
            total_budget=22000.0,
            travel_style="Scenic Mountain Vistas",
            is_group=True
        ),
        current_user=user,
        db=db
    )
    assert len(new_trip.itinerary_days) == 3
    assert len(new_trip.packing_items) > 0
    print(f"  ✓ Trip #{new_trip.id} generated with {len(new_trip.itinerary_days)} days and {len(new_trip.packing_items)} packing items")

    # 6. What-If Trip Simulator
    sim = run_what_if_simulation(
        new_trip.id,
        WhatIfSimulateRequest(trip_id=new_trip.id, extra_days=2, transport_mode="train", extra_travellers=1),
        current_user=user,
        db=db
    )
    assert sim["new_duration_days"] == 5
    print(f"  ✓ What-If Simulator: {sim['original_duration_days']}d -> {sim['new_duration_days']}d, Per-Person Cost ₹{sim['per_person_cost']} ({sim['feasibility_status']})")

    # 7. Budget & Expense Tracking
    exp = add_trip_expense(
        new_trip.id,
        ExpenseCreate(payer_name="Aarav", category="Food", title="Lockhart Tea Tasting", amount=650.0),
        current_user=user,
        db=db
    )
    summary = get_trip_budget_summary(new_trip.id, current_user=user, db=db)
    assert summary["total_actual_spent"] >= 650.0
    print(f"  ✓ Logged expense of ₹{exp.amount}, Remaining budget: ₹{summary['remaining_budget']}")

    # 8. Weather-Based Dynamic Replanning
    replan = replan_rainy_day(
        WeatherReplanRequest(trip_id=new_trip.id, day_number=1, current_weather_condition="Rain"),
        db=db
    )
    assert replan["status"] == "success"
    print(f"  ✓ Weather replan applied: Day 1 updated for rainy conditions with indoor venues")

    # 9. Group Collaboration & Expense Settlement
    member = invite_group_member(
        new_trip.id,
        GroupInviteRequest(name="Priya Sen", email="priya@example.com"),
        current_user=user,
        db=db
    )
    settle = calculate_group_settlements(new_trip.id, current_user=user, db=db)
    print(f"  ✓ Group member {member.name} joined. Group settlement engine computed balance.")

    # 10. Safety Directory
    safety = get_safety_advisory("Munnar, Kerala")
    assert len(safety["emergency_numbers"]) >= 4
    print(f"  ✓ Safety directory loaded: {safety['overall_safety_rating']} with {len(safety['emergency_numbers'])} hotlines")

    # 11. Packing Checklist Toggle
    first_item = new_trip.packing_items[0]
    toggled = toggle_packing_item(first_item.id, current_user=user, db=db)
    assert toggled.is_packed is True
    print(f"  ✓ Toggled packing item '{toggled.item_name}' to packed (status: {toggled.is_packed})")

    # 12. Conversational AI Assistant
    ai_resp = generate_conversational_response("I want to travel somewhere peaceful for 4 days.")
    assert ai_resp["structured_type"] == "destination_list"
    print(f"  ✓ Conversational AI generated structured response with type: {ai_resp['structured_type']}")

    db.close()
    print("\n🎉 ALL 12 CORE WORKFLOWS PASSED WITH 100% SUCCESS!")

if __name__ == "__main__":
    run_full_direct_suite()
