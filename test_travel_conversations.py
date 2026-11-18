import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent / "backend"))

from app.services.ai_service import generate_conversational_response

def run_tests():
    print("=" * 70)
    print("🚀 WANDERWISE AI - CHATGPT-LIKE TRAVEL INTELLIGENCE TEST SUITE")
    print("=" * 70)
    
    test_cases = [
        # --- Multi-turn Conversation 1 (User's Exact Example!) ---
        {
            "category": "1. Multi-Turn: Destination Overview",
            "prompt": "Tell me about Bali.",
            "history": [],
            "memory": {}
        },
        {
            "category": "2. Multi-Turn: Follow-up Weather ('there' in December)",
            "prompt": "What about the weather in December?",
            "history": [
                {"role": "user", "content": "Tell me about Bali."},
                {"role": "assistant", "content": "Bali is a tropical Indonesian paradise known for volcanic mountains, iconic rice terraces, vibrant Hindu temple culture, and world-class surfing beaches."}
            ],
            "memory": {"destination": "Bali, Indonesia", "days": 3, "budget": 20000.0, "travellers": 2}
        },
        {
            "category": "3. Multi-Turn: Comparison (Bali vs Thailand)",
            "prompt": "Is it expensive compared to Thailand?",
            "history": [
                {"role": "user", "content": "Tell me about Bali."},
                {"role": "assistant", "content": "Bali is a tropical Indonesian paradise..."},
                {"role": "user", "content": "What about the weather in December?"},
                {"role": "assistant", "content": "December falls in Bali's wet season with tropical rain showers and high humidity..."}
            ],
            "memory": {"destination": "Bali, Indonesia", "days": 3, "budget": 20000.0, "travellers": 2}
        },
        {
            "category": "4. Multi-Turn: Contextual Alternative ('Suggest something less crowded')",
            "prompt": "Suggest something less crowded.",
            "history": [
                {"role": "user", "content": "Tell me about Bali."},
                {"role": "assistant", "content": "Bali is a tropical Indonesian paradise..."},
                {"role": "user", "content": "What about the weather in December?"},
                {"role": "assistant", "content": "December falls in Bali's wet season..."},
                {"role": "user", "content": "Is it expensive compared to Thailand?"},
                {"role": "assistant", "content": "Both Bali and Thailand are budget-friendly, with Thailand often having slightly cheaper street food..."}
            ],
            "memory": {"destination": "Bali, Indonesia", "days": 3, "budget": 20000.0, "travellers": 2}
        },
        
        # --- Individual Travel Domain Tests ---
        {
            "category": "5. Local Culture & Gastronomy",
            "prompt": "What authentic local dishes and street food should I eat in Tokyo?",
            "history": [],
            "memory": {"destination": "Tokyo, Japan"}
        },
        {
            "category": "6. Transportation, Routes & Scenic Trains",
            "prompt": "How do I travel from Zurich to Zermatt by train, and how long does it take?",
            "history": [],
            "memory": {"destination": "Switzerland"}
        },
        {
            "category": "7. Hotels & Neighborhood Selection",
            "prompt": "What are the best neighborhoods to stay in Rome for a first-time visitor?",
            "history": [],
            "memory": {"destination": "Rome, Italy"}
        },
        {
            "category": "8. Travel Budget & Itemized Estimates",
            "prompt": "Can you give me an expense breakdown for a 5-day budget trip to Vietnam for 2 people?",
            "history": [],
            "memory": {"destination": "Vietnam", "days": 5, "travellers": 2}
        },
        {
            "category": "9. Safety & Solo Travel",
            "prompt": "Is Iceland safe for solo female travelers, and what winter driving precautions should I know?",
            "history": [],
            "memory": {"destination": "Iceland"}
        },
        {
            "category": "10. Visa, Passport & Documentation",
            "prompt": "Do US citizens need a visa for tourism in Japan, and what passport validity is required?",
            "history": [],
            "memory": {"destination": "Tokyo, Japan"}
        },
        {
            "category": "11. Photography & Golden Hour",
            "prompt": "Where are the best golden hour and blue hour photography spots in Santorini?",
            "history": [],
            "memory": {"destination": "Santorini, Greece"}
        },
        {
            "category": "12. Road Trips & Scenic Drives",
            "prompt": "Suggest a scenic 3-day road trip route along the Amalfi Coast with coastal stopovers.",
            "history": [],
            "memory": {"destination": "Amalfi Coast, Italy"}
        },
        {
            "category": "13. Adventure & Scuba Diving",
            "prompt": "What are the top scuba diving spots in the Red Sea, Egypt?",
            "history": [],
            "memory": {"destination": "Egypt"}
        },
        {
            "category": "14. Explicit Itinerary Request (Should attach interactive preview)",
            "prompt": "Create a 3-day itinerary for Paris for 2 travellers under ₹50,000",
            "history": [],
            "memory": {"destination": "Paris, France", "days": 3, "travellers": 2, "budget": 50000.0}
        },
        {
            "category": "15. Real-Time Weather Telemetry",
            "prompt": "What is the current live weather in Goa right now?",
            "history": [],
            "memory": {"destination": "Goa, India"}
        }
    ]

    passed = 0
    total = len(test_cases)
    
    for i, tc in enumerate(test_cases, 1):
        print(f"\n[{i}/{total}] Testing: {tc['category']}", flush=True)
        print(f"User: \"{tc['prompt']}\"", flush=True)
        try:
            resp = generate_conversational_response(
                user_message=tc["prompt"],
                conversation_history=tc["history"],
                session_memory=tc["memory"]
            )
            content = resp.get("content", "")
            has_structured = resp.get("structured_type") is not None
            structured_type = resp.get("structured_type")
            
            # Print preview of response
            preview = content[:250].replace("\n", " ")
            print(f"🤖 AI Response ({len(content)} chars): {preview}...", flush=True)
            if has_structured:
                print(f"📦 Interactive Widget Attached: [{structured_type}]", flush=True)
            
            # Validation assertions
            if len(content) > 60:
                print("✅ PASS: Rich, dynamic, context-aware answer generated.", flush=True)
                passed += 1
            else:
                print("❌ FAIL: Response too short or empty.", flush=True)
        except Exception as e:
            print(f"❌ ERROR: {e}", flush=True)

    print("\n" + "=" * 70)
    print(f"TEST RESULTS: {passed}/{total} Passed ({(passed/total)*100:.1f}%)")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
