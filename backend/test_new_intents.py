"""
Test new intent classes and memory enhancements added to ai_service.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.ai_service import extract_and_update_memory, extract_itemized_expenses

PASS = "✅ PASS"
FAIL = "❌ FAIL"

def check(label, condition):
    print(f"{PASS if condition else FAIL}  {label}")

print("=" * 60)
print("MEMORY ENHANCEMENT TESTS")
print("=" * 60)

# Test 1: Preference extraction — peaceful
m = extract_and_update_memory("I prefer peaceful and quiet places", {})
check("Preference: 'peaceful' detected", "peaceful" in m.get("preferences", []))

# Test 2: Preference extraction — adventure
m = extract_and_update_memory("I love trekking and adventure spots", {})
check("Preference: 'adventure' detected", "adventure" in m.get("preferences", []))

# Test 3: Preference extraction — food
m = extract_and_update_memory("I am a foodie and love street food", {})
check("Preference: 'food' detected", "food" in m.get("preferences", []))

# Test 4: Traveller type — couple
m = extract_and_update_memory("Planning a honeymoon trip", {})
check("Traveller type: 'couple' detected", m.get("traveller_type") == "couple")

# Test 5: Traveller type — family
m = extract_and_update_memory("Travelling with family and kids", {})
check("Traveller type: 'family' detected", m.get("traveller_type") == "family")

# Test 6: Trip dates — month
m = extract_and_update_memory("Planning to go in December", {})
check("Trip date: December detected", "December" in str(m.get("trip_dates", "")))

# Test 7: Trip dates — Christmas
m = extract_and_update_memory("Want to go during Christmas", {})
check("Trip date: Christmas detected", m.get("trip_dates") is not None)

# Test 8: Planning objective — itinerary
m = extract_and_update_memory("Build me an itinerary for 3 days", {})
check("Planning objective: 'itinerary'", m.get("current_planning_objective") == "itinerary")

# Test 9: Planning objective — budget
m = extract_and_update_memory("What is the budget for Munnar?", {})
check("Planning objective: 'budget'", m.get("current_planning_objective") == "budget")

# Test 10: Preferences accumulate over turns
m1 = extract_and_update_memory("I want peaceful spots", {})
m2 = extract_and_update_memory("I also love photography viewpoints", m1)
check("Preferences accumulate: peaceful + photography", 
      "peaceful" in m2.get("preferences", []) and "photography" in m2.get("preferences", []))

print()
print("=" * 60)
print("EXPENSE EXTRACTION TESTS")
print("=" * 60)

base = {"hotel_per_night": 2000.0, "food_per_day": 600.0, "transport": 1200.0, "activities": 800.0, "petrol": 0.0, "other": 400.0}

# Test 11: Petrol extraction
updated, note = extract_itemized_expenses("petrol 1800", base)
check("Petrol extracted: 1800", updated.get("petrol") == 1800.0)

# Test 12: Hotel extraction
updated, note = extract_itemized_expenses("hotel 2500 per night", base)
check("Hotel extracted: 2500", updated.get("hotel_per_night") == 2500.0)

# Test 13: Food extraction
updated, note = extract_itemized_expenses("food 1200 per day", base)
check("Food extracted: 1200", updated.get("food_per_day") == 1200.0)

# Test 14: Miscellaneous extraction
updated, note = extract_itemized_expenses("shopping budget 3000", base)
check("Shopping/misc extracted: 3000", updated.get("other") == 3000.0)

# Test 15: Multiple items in one message
updated, note = extract_itemized_expenses("hotel 3000 food 800 petrol 1500", base)
check("Multi-expense: hotel=3000", updated.get("hotel_per_night") == 3000.0)
check("Multi-expense: food=800", updated.get("food_per_day") == 800.0)
check("Multi-expense: petrol=1500", updated.get("petrol") == 1500.0)

print()
print("=" * 60)
print("DESTINATION SWITCH TEST")
print("=" * 60)

# Test 16: Destination switch clears old context
m1 = extract_and_update_memory("I want to visit Delhi", {})
check("First destination: Delhi", "Delhi" in str(m1.get("destination", "")))
m2 = extract_and_update_memory("What about Madurai instead?", m1)
check("Switch to Madurai", "Madurai" in str(m2.get("destination", "")))
check("Delhi moved to previously_discussed", any("Delhi" in str(d) for d in m2.get("previously_discussed_destinations", [])))

print()
print("ALL TESTS COMPLETE")
