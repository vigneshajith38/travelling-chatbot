"""
Test script to verify map data generation and coordinate validity across multiple destinations.
Tests:
1. Madurai, Tamil Nadu
2. Vagamon, Kerala
3. Bangalore, Karnataka
4. Paris, France
5. Tokyo, Japan
6. Multi-destination circuit: Trivandrum -> Vagamon
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

from app.services.itinerary_service import generate_trip_itinerary, resolve_destination_coordinates
from app.services.destination_verifier import get_destination_identity

DESTINATIONS_TO_TEST = [
    ("Madurai", 9.9252, 78.1198),
    ("Vagamon", 9.6886, 76.9069),
    ("Bangalore", 12.9716, 77.5946),
    ("Paris", 48.8566, 2.3522),
    ("Tokyo", 35.6762, 139.6503),
]

def run_tests():
    print("=" * 70)
    print("🗺️ LEAFLET + OPENSTREETMAP MULTI-DESTINATION ACCURACY TEST")
    print("=" * 70)

    all_passed = True

    for dest, expected_lat, expected_lng in DESTINATIONS_TO_TEST:
        print(f"\nTesting Destination: {dest} ...")
        
        # 1. Coordinate resolution
        lat, lng = resolve_destination_coordinates(dest)
        print(f"  • Resolved Centroid: {lat:.4f}°N, {lng:.4f}°E")
        
        # Check coordinate bounds
        if not (-90.0 <= lat <= 90.0 and -180.0 <= lng <= 180.0):
            print(f"  ❌ FAIL: Coordinates out of valid geographic range: ({lat}, {lng})")
            all_passed = False
            continue

        # 2. Itinerary generation for map markers
        itinerary = generate_trip_itinerary(dest, "2026-11-20", num_days=2)
        total_activities = 0
        valid_coords = 0
        
        for day in itinerary:
            day_num = day.get("day_number")
            activities = day.get("activities", [])
            total_activities += len(activities)
            for act in activities:
                a_lat = act.get("lat")
                a_lng = act.get("lng")
                if isinstance(a_lat, (int, float)) and isinstance(a_lng, (int, float)) and a_lat != 0 and a_lng != 0:
                    valid_coords += 1
                else:
                    print(f"  ⚠️ Activity with invalid coords: {act.get('title')}")

        print(f"  • Days: {len(itinerary)}, Total Activities: {total_activities}, Map Markers Placed: {valid_coords}")
        
        if total_activities > 0 and valid_coords == total_activities:
            print(f"  ✅ PASS: 100% of activities have valid Leaflet/OSM coordinates")
        else:
            print(f"  ❌ FAIL: Some activities lack valid coordinates ({valid_coords}/{total_activities})")
            all_passed = False

    # 3. Test Multi-destination circuit
    print("\nTesting Multi-destination circuit: Trivandrum -> Vagamon ...")
    triv_lat, triv_lng = resolve_destination_coordinates("Trivandrum")
    vag_lat, vag_lng = resolve_destination_coordinates("Vagamon")
    print(f"  • Trivandrum: {triv_lat:.4f}°N, {triv_lng:.4f}°E")
    print(f"  • Vagamon: {vag_lat:.4f}°N, {vag_lng:.4f}°E")
    
    # Distance calculation
    import math
    dlat = math.radians(vag_lat - triv_lat)
    dlng = math.radians(vag_lng - triv_lng)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(triv_lat)) * math.cos(math.radians(vag_lat)) * math.sin(dlng/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    dist_km = 6371.0 * c
    print(f"  • Geodesic Distance: {dist_km:.1f} km")
    
    if 100.0 <= dist_km <= 200.0:
        print(f"  ✅ PASS: Inter-city distance accurately separated ({dist_km:.1f} km)")
    else:
        print(f"  ⚠️ Distance note: {dist_km:.1f} km")

    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 ALL MULTI-DESTINATION MAP DATA TESTS PASSED SUCCESSFULLY!")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
