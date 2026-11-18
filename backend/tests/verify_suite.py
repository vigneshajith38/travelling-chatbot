import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
import httpx
from app.main import app

async def run_all_tests():
    print("🚀 Starting WanderWise Comprehensive Backend Verification Suite...")
    transport = httpx.ASGITransport(app=app)
    
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Health check
        res = await client.get("/health")
        assert res.status_code == 200, f"Health check failed: {res.text}"
        print("  ✓ Health check passed (/health)")

        # 2. List destinations
        res = await client.get("/api/v1/destinations")
        assert res.status_code == 200
        destinations = res.json()
        assert len(destinations) >= 5
        print(f"  ✓ Listed {len(destinations)} curated destinations (/api/v1/destinations)")

        # 3. Personalized Recommendation Engine
        res = await client.post("/api/v1/destinations/recommend", json={
            "interests": ["mountains", "scenic"],
            "budget_range": "moderate",
            "duration_days": 4,
            "travellers_count": 2
        })
        assert res.status_code == 200
        recs = res.json()
        assert len(recs) > 0
        print(f"  ✓ Personalized AI recommendation engine generated {len(recs)} matches with scores ({recs[0]['name']}: {recs[0]['match_score']}%)")

        # 4. Surprise Me Engine
        res = await client.get("/api/v1/destinations/surprise-me")
        assert res.status_code == 200
        surprise = res.json()
        assert surprise["match_score"] == 98
        print(f"  ✓ 'Surprise Me' engine picked: {surprise['name']}")

        # 5. Hidden Gems Discovery
        res = await client.get("/api/v1/destinations/hidden-gems")
        assert res.status_code == 200
        gems = res.json()
        assert len(gems) > 0
        print(f"  ✓ Discovered {len(gems)} verified offbeat hidden gems")

        # 6. Mood-Based Travel Planner
        res = await client.post("/api/v1/destinations/mood-plan", json={
            "mood_description": "I want to disconnect from everything and drink coffee in misty mountains",
            "duration_days": 3
        })
        assert res.status_code == 200
        mood_plan = res.json()
        assert "recommended_style" in mood_plan
        print(f"  ✓ Mood translated into: '{mood_plan['top_destination']['name']}' ({mood_plan['recommended_style']})")

        # 7. Complete Trip Lifecycle: Create, Days, Activities, Packing
        trip_payload = {
            "title": "Munnar Tea Trails & Solitude",
            "destination": "Munnar, Kerala",
            "country": "India",
            "start_date": "2026-11-20",
            "end_date": "2026-11-23",
            "travellers_count": 2,
            "total_budget": 20000.0,
            "travel_style": "Scenic Mountain Vistas",
            "mood": "Peaceful",
            "is_group": True
        }
        res = await client.post("/api/v1/trips", json=trip_payload)
        assert res.status_code == 200
        trip = res.json()
        trip_id = trip["id"]
        assert len(trip["itinerary_days"]) == 3
        total_acts = sum(len(d["activities"]) for d in trip["itinerary_days"])
        assert total_acts >= 6
        assert len(trip["packing_items"]) > 0
        print(f"  ✓ Created Trip #{trip_id} with {len(trip['itinerary_days'])} days, {total_acts} scheduled activities & {len(trip['packing_items'])} packing items")

        # 8. What-If Trip Simulator
        res = await client.post(f"/api/v1/trips/{trip_id}/simulate", json={
            "trip_id": trip_id,
            "extra_days": 2,
            "budget_change": -3000,
            "transport_mode": "train",
            "extra_travellers": 1
        })
        assert res.status_code == 200
        sim = res.json()
        assert sim["new_duration_days"] == 5
        print(f"  ✓ What-If Simulator: {sim['original_duration_days']}d -> {sim['new_duration_days']}d, Per-Person Cost ₹{sim['per_person_cost']} ({sim['feasibility_status']})")

        # 9. Budget Tracking & Itemized Expenses
        res = await client.post(f"/api/v1/budget/{trip_id}/expenses", json={
            "payer_name": "Aarav",
            "category": "Food",
            "title": "Lockhart Orthodox High-Grown Tea",
            "amount": 850.0
        })
        assert res.status_code == 200
        print("  ✓ Logged itemized travel expense of ₹850.0")

        res = await client.get(f"/api/v1/budget/{trip_id}/summary")
        assert res.status_code == 200
        summary = res.json()
        assert summary["total_actual_spent"] >= 850.0
        print(f"  ✓ Budget breakdown computed across {len(summary['categories'])} categories, remaining: ₹{summary['remaining_budget']}")

        # 10. Weather-Based Dynamic Replanning
        res = await client.post("/api/v1/weather/replan-day", json={
            "trip_id": trip_id,
            "day_number": 1,
            "current_weather_condition": "Heavy Rain"
        })
        assert res.status_code == 200
        replan = res.json()
        print(f"  ✓ Weather-based replanning applied: {replan['message']}")

        # 11. Group Collaboration: Invite & Settle
        res = await client.post(f"/api/v1/group/{trip_id}/invite", json={
            "name": "Rohan Varma",
            "email": "rohan@example.com",
            "role": "member"
        })
        assert res.status_code == 200
        print("  ✓ Invited group member Rohan Varma")

        res = await client.get(f"/api/v1/group/{trip_id}/settlements")
        assert res.status_code == 200
        settlements = res.json()
        print(f"  ✓ Automated group debt settlement calculated ({len(settlements['settlements'])} transfers needed)")

        # 12. Conversational AI Assistant
        res = await client.post("/api/v1/chat/message", json={
            "message": "I want to travel somewhere peaceful for 4 days with friends.",
            "trip_id": trip_id
        })
        assert res.status_code == 200
        chat_data = res.json()
        assert "message" in chat_data
        print(f"  ✓ Conversational AI Assistant responded with structured card type: '{chat_data['message']['structured_type']}'")

        # 13. Safety & Emergency Directory
        res = await client.get("/api/v1/safety/Munnar")
        assert res.status_code == 200
        safety = res.json()
        assert len(safety["emergency_numbers"]) >= 4
        print(f"  ✓ Verified emergency directories retrieved ({len(safety['emergency_numbers'])} hotlines, hospitals & police)")

        # 14. Packing Checklist Toggle
        first_pack = trip["packing_items"][0]
        res = await client.put(f"/api/v1/packing/items/{first_pack['id']}/toggle")
        assert res.status_code == 200
        assert res.json()["is_packed"] is True
        print(f"  ✓ Interactive packing checklist item '{first_pack['item_name']}' toggled to packed")

    print("\n🎉 ALL 14 CORE FUNCTIONAL WORKFLOWS VERIFIED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
