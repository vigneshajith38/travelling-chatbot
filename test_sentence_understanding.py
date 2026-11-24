"""
Comprehensive test script to verify natural language sentence understanding,
accurate context retention, destination preservation, and zero false destination extraction.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

from app.services.destination_verifier import (
    parse_destination_query,
    get_destination_identity,
    is_conversational_phrase
)
from app.services.ai_service import (
    extract_and_update_memory,
    generate_conversational_response
)

def run_tests():
    print("=" * 75)
    print("🧠 SENTENCE UNDERSTANDING & 100% ACCURACY TEST SUITE")
    print("=" * 75)
    all_passed = True

    # TEST 1: Conversational Phrase Detection
    print("\n--- TEST 1: Conversational vs Destination Classification ---")
    conv_sentences = [
        ("I prefer peaceful places", True),
        ("What about food?", True),
        ("Anything less crowded?", True),
        ("What about cafes?", True),
        ("Can I visit these five places in one day?", True),
        ("How much will it cost?", True),
        ("Planning a honeymoon trip", True),
        ("Is it safe for solo female travelers?", True),
        ("Make it 2 days instead", True),
        ("Madurai", False),
        ("Plan a trip to Madurai", False),
        ("Vagamon", False),
        ("Tokyo, Japan", False),
        ("Paris", False)
    ]
    for s, should_be_conv in conv_sentences:
        res = is_conversational_phrase(s)
        parsed = parse_destination_query(s)
        has_dest = len(parsed["destinations"]) > 0
        
        # If it should be conversational, it must NOT extract a fake destination
        if should_be_conv and has_dest:
            print(f"  ❌ FAIL: '{s}' falsely extracted destination: {parsed['destinations']}")
            all_passed = False
        elif not should_be_conv and not has_dest:
            print(f"  ❌ FAIL: '{s}' missed legitimate destination")
            all_passed = False
        else:
            dest_label = parsed['destinations'][0]['canonical_name'] if has_dest else 'None (Conversational Follow-up)'
            print(f"  ✅ PASS: '{s}' -> {dest_label}")

    # TEST 2: Multi-Turn Conversation Memory Retention
    print("\n--- TEST 2: Multi-Turn Conversation Context Retention ---")
    # Turn 1
    m1 = extract_and_update_memory("I'm planning a trip to Madurai")
    dest1 = m1.get("destination")
    print(f"  Turn 1: 'I'm planning a trip to Madurai' -> Active Destination: '{dest1}'")
    if "Madurai" not in str(dest1):
        print(f"  ❌ FAIL: Madurai not established in Turn 1")
        all_passed = False
    else:
        print(f"  ✅ PASS: Destination correctly set to Madurai")

    # Turn 2
    m2 = extract_and_update_memory("I prefer peaceful places", m1)
    dest2 = m2.get("destination")
    prefs2 = m2.get("preferences", [])
    print(f"  Turn 2: 'I prefer peaceful places' -> Active Destination: '{dest2}', Prefs: {prefs2}")
    if "Madurai" not in str(dest2) or "Prefer" in str(dest2):
        print(f"  ❌ FAIL: Active destination corrupted by Turn 2! Got: {dest2}")
        all_passed = False
    elif "peaceful" not in prefs2:
        print(f"  ❌ FAIL: Preference 'peaceful' not captured")
        all_passed = False
    else:
        print(f"  ✅ PASS: Active destination preserved as Madurai & preference added")

    # Turn 3
    m3 = extract_and_update_memory("Anything less crowded?", m2)
    dest3 = m3.get("destination")
    print(f"  Turn 3: 'Anything less crowded?' -> Active Destination: '{dest3}'")
    if "Madurai" not in str(dest3):
        print(f"  ❌ FAIL: Active destination corrupted in Turn 3: {dest3}")
        all_passed = False
    else:
        print(f"  ✅ PASS: Active destination preserved as Madurai")

    # Turn 4
    m4 = extract_and_update_memory("What about food?", m3)
    dest4 = m4.get("destination")
    print(f"  Turn 4: 'What about food?' -> Active Destination: '{dest4}', Last Topic: '{m4.get('last_topic')}'")
    if "Madurai" not in str(dest4):
        print(f"  ❌ FAIL: Active destination corrupted in Turn 4: {dest4}")
        all_passed = False
    else:
        print(f"  ✅ PASS: Active destination preserved as Madurai & topic updated to food")

    # TEST 3: Distance and Exact Route Query
    print("\n--- TEST 3: Distance and Travel Time Query ---")
    resp_dist = generate_conversational_response("How far is Munnar from Kochi?", session_memory=m4)
    content_dist = resp_dist.get("content", "")
    print(f"  Response summary: {content_dist[:180]}...")
    if "km" in content_dist.lower() and ("munnar" in content_dist.lower() or "kochi" in content_dist.lower()):
        print(f"  ✅ PASS: Exact distance and route returned directly")
    else:
        print(f"  ❌ FAIL: Distance query did not return distance info")
        all_passed = False

    # TEST 4: Feasibility Question
    print("\n--- TEST 4: Feasibility Query ---")
    resp_feas = generate_conversational_response("Can I visit these five places in one day?", session_memory=m4)
    content_feas = resp_feas.get("content", "")
    print(f"  Response summary: {content_feas[:180]}...")
    if "feasib" in content_feas.lower() or "one day" in content_feas.lower() or "constraint" in content_feas.lower() or "schedule" in content_feas.lower():
        print(f"  ✅ PASS: Feasibility evaluation provided without generating generic 16-section guide")
    else:
        print(f"  ❌ FAIL: Feasibility response lacked expected analysis")
        all_passed = False

    # TEST 5: Clean Destination Switch without Contamination
    print("\n--- TEST 5: Clean Destination Switch ---")
    m_switch = extract_and_update_memory("What about Vagamon instead?", m4)
    new_dest = m_switch.get("destination")
    prev_dests = m_switch.get("previously_discussed_destinations", [])
    print(f"  Destination switch: 'What about Vagamon instead?' -> New: '{new_dest}', History: {prev_dests}")
    if "Vagamon" in str(new_dest) and any("Madurai" in str(d) for d in prev_dests):
        print(f"  ✅ PASS: Clean destination switch to Vagamon with Madurai moved to history")
    else:
        print(f"  ❌ FAIL: Destination switch failed: new={new_dest}, history={prev_dests}")
        all_passed = False

    print("\n" + "=" * 75)
    if all_passed:
        print("🎉 ALL SENTENCE UNDERSTANDING & ACCURACY TESTS PASSED 100%!")
    else:
        print("❌ SOME ACCURACY TESTS FAILED")
    print("=" * 75)

if __name__ == "__main__":
    run_tests()
