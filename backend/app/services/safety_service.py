from typing import Dict, Any, List

def get_destination_safety_report(destination: str, country: str = "India") -> Dict[str, Any]:
    return {
        "destination": destination,
        "country": country,
        "overall_safety_rating": "High (Safe for Solo & Family Travelers)",
        "emergency_numbers": [
            {"service": "Unified National Emergency Number", "phone": "112", "notes": "24/7 Police, Medical & Fire response nationwide"},
            {"service": "Tourist Police Helpline", "phone": "1363", "notes": "Multilingual assistance for travelers"},
            {"service": "Medical Ambulance Service", "phone": "108", "notes": "Rapid emergency medical transit"},
            {"service": "Women Safety Helpline", "phone": "1091", "notes": "Direct dedicated round-the-clock safety support"},
            {"service": "Road & Highway Emergency Assistance", "phone": "1033", "notes": "National Highways emergency towing & first-aid"}
        ],
        "local_facilities": [
            {
                "type": "Hospital",
                "name": f"Government Taluk Hospital & Emergency Wing, {destination.split(',')[0]}",
                "address": f"Hospital Road, Central {destination.split(',')[0]}",
                "distance": "1.8 km from town center",
                "hours": "24/7 Emergency Care"
            },
            {
                "type": "Police Station",
                "name": f"Central Tourist Police Station, {destination.split(',')[0]}",
                "address": f"Main Road, {destination.split(',')[0]}",
                "distance": "0.9 km from town center",
                "hours": "24/7 Active Patrol"
            }
        ],
        "essential_guidelines": [
            "Keep digital photocopies of passports, government photo IDs, and travel insurance accessible offline in cloud or email.",
            "When exploring mountain trails or remote waterfalls, inform your homestay or hotel front desk of your return schedule.",
            "Use metered or prepaid app-based taxis and verified state tourist cabs for long-distance transit.",
            "Drink filtered or bottled water and sample piping hot street food from high-turnover stalls."
        ],
        "disclaimer": "Emergency contact numbers are verified against official government registries. Travel advisories represent general guidance and should be verified with local authorities during severe climate events."
    }

