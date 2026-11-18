import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_list_destinations():
    response = client.get("/api/v1/destinations")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 5
    assert "name" in data[0]

def test_recommend_destinations():
    response = client.post("/api/v1/destinations/recommend", json={
        "interests": ["mountains", "scenic"],
        "budget_range": "moderate",
        "duration_days": 4,
        "travellers_count": 2
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "match_score" in data[0]

def test_surprise_me():
    response = client.get("/api/v1/destinations/surprise-me")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert data["match_score"] == 98

def test_hidden_gems():
    response = client.get("/api/v1/destinations/hidden-gems")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0

def test_mood_plan():
    response = client.post("/api/v1/destinations/mood-plan", json={
        "mood_description": "I want to disconnect from everything and drink coffee in misty mountains",
        "duration_days": 3
    })
    assert response.status_code == 200
    data = response.json()
    assert "recommended_style" in data
    assert "sample_itinerary" in data

def test_trip_crud_and_simulation():
    # 1. Create Trip
    trip_payload = {
        "title": "Automated Test Expedition to Munnar",
        "destination": "Munnar, Kerala",
        "country": "India",
        "start_date": "2026-12-01",
        "end_date": "2026-12-04",
        "travellers_count": 2,
        "total_budget": 20000.0,
        "travel_style": "Scenic Exploration",
        "mood": "Peaceful"
    }
    create_res = client.post("/api/v1/trips", json=trip_payload)
    assert create_res.status_code == 200
    trip = create_res.json()
    trip_id = trip["id"]
    assert len(trip["itinerary_days"]) > 0
    assert len(trip["packing_items"]) > 0

    # 2. Get Detail
    detail_res = client.get(f"/api/v1/trips/{trip_id}")
    assert detail_res.status_code == 200
    assert detail_res.json()["title"] == trip_payload["title"]

    # 3. Simulate What-If
    sim_res = client.post(f"/api/v1/trips/{trip_id}/simulate", json={
        "trip_id": trip_id,
        "extra_days": 2,
        "budget_change": 3000,
        "transport_mode": "train",
        "extra_travellers": 1
    })
    assert sim_res.status_code == 200
    assert sim_res.json()["new_duration_days"] >= 4

    # 4. Add Expense
    exp_res = client.post(f"/api/v1/budget/{trip_id}/expenses", json={
        "payer_name": "Aarav",
        "category": "Food",
        "title": "Highland Tea House",
        "amount": 750.0
    })
    assert exp_res.status_code == 200

    # 5. Get Budget Summary
    b_summary = client.get(f"/api/v1/budget/{trip_id}/summary")
    assert b_summary.status_code == 200
    assert b_summary.json()["total_actual_spent"] >= 750.0

    # 6. Rainy-Day Replan
    replan_res = client.post("/api/v1/weather/replan-day", json={
        "trip_id": trip_id,
        "day_number": 1,
        "current_weather_condition": "Rain"
    })
    assert replan_res.status_code == 200

    # 7. Delete Trip
    del_res = client.delete(f"/api/v1/trips/{trip_id}")
    assert del_res.status_code == 200

def test_chat_assistant():
    chat_res = client.post("/api/v1/chat/message", json={
        "message": "I want to travel somewhere peaceful for 4 days with friends."
    })
    assert chat_res.status_code == 200
    data = chat_res.json()
    assert "message" in data
    assert "session_id" in data
    assert len(data.get("suggested_actions", [])) > 0

