from typing import List, Dict, Any

def generate_smart_packing_list(
    destination: str,
    duration_days: int = 4,
    travellers_count: int = 1,
    travel_style: str = "adventure",
    is_rainy: bool = False,
    is_cold: bool = False
) -> List[Dict[str, Any]]:
    items = []
    
    # 1. Clothing
    clothing = [
        {"name": "Comfortable breathable cotton tees", "qty": min(6, duration_days + 1)},
        {"name": "Lightweight travel trousers / cargo pants", "qty": max(2, duration_days // 2)},
        {"name": "Comfortable walking / hiking shoes with grip", "qty": 1},
        {"name": "Slip-on casual sandals / flip-flops", "qty": 1},
        {"name": "Quick-dry undergarments & moisture-wicking socks", "qty": duration_days + 1},
        {"name": "Sleepwear / loungewear", "qty": 2}
    ]
    if is_cold or "mountain" in travel_style.lower() or "munnar" in destination.lower() or "chopta" in destination.lower():
        clothing.extend([
            {"name": "Warm fleece jacket / windcheater", "qty": 1},
            {"name": "Thermal inner tops and bottoms", "qty": 2},
            {"name": "Woolen beanie & neck buff", "qty": 1}
        ])
    if is_rainy or "kerala" in destination.lower():
        clothing.append({"name": "Compact windproof travel umbrella or poncho", "qty": 1})
    if "beach" in travel_style.lower() or "gokarna" in destination.lower() or "varkala" in destination.lower():
        clothing.extend([
            {"name": "UV-protective swimwear / boardshorts", "qty": 2},
            {"name": "Wide-brim sun hat & sunglasses", "qty": 1}
        ])
        
    for c in clothing:
        items.append({"category": "Clothing", "item_name": c["name"], "quantity": c["qty"], "is_packed": False, "is_custom": False})

    # 2. Toiletries
    toiletries = [
        {"name": "SPF 50+ Broad-spectrum Sunscreen", "qty": 1},
        {"name": "Biodegradable wet wipes & pocket tissues", "qty": 2},
        {"name": "Travel toothbrush & organic toothpaste", "qty": 1},
        {"name": "Hydrating lip balm & skin moisturizer", "qty": 1},
        {"name": "Travel-size shampoo & body bar", "qty": 1},
        {"name": "Natural insect & mosquito repellent roll-on", "qty": 1}
    ]
    for t in toiletries:
        items.append({"category": "Toiletries", "item_name": t["name"], "quantity": t["qty"], "is_packed": False, "is_custom": False})

    # 3. Electronics
    electronics = [
        {"name": "High-capacity power bank (10,000–20,000 mAh)", "qty": 1},
        {"name": "Braided fast charging cables (Type-C & Lightning)", "qty": 2},
        {"name": "Universal multi-plug travel adapter", "qty": 1},
        {"name": "Noise-cancelling earbuds or headphones", "qty": 1},
        {"name": "Microfiber lens cleaning cloth for camera/phone", "qty": 1}
    ]
    for e in electronics:
        items.append({"category": "Electronics", "item_name": e["name"], "quantity": e["qty"], "is_packed": False, "is_custom": False})

    # 4. Documents
    docs = [
        {"name": "Government Photo ID (Aadhaar / Passport / Driver License)", "qty": 1},
        {"name": "Hotel booking vouchers & reservation PDFs offline", "qty": 1},
        {"name": "Travel medical insurance policy summary", "qty": 1},
        {"name": "Emergency cash in local banknotes (small denominations)", "qty": 1}
    ]
    for d in docs:
        items.append({"category": "Documents", "item_name": d["name"], "quantity": d["qty"], "is_packed": False, "is_custom": False})

    # 5. Medicines & First-Aid
    medicines = [
        {"name": "Motion sickness tablets (Avomine / Dimenhydrinate)", "qty": 6},
        {"name": "Paracetamol & Ibuprofen for pain / fever", "qty": 10},
        {"name": "Electrolyte ORS rehydration sachets", "qty": 4},
        {"name": "Antiseptic wipes, Band-Aids & blister pads", "qty": 1},
        {"name": "Antacid / digestive relief tablets", "qty": 8}
    ]
    for m in medicines:
        items.append({"category": "Medicines", "item_name": m["name"], "quantity": m["qty"], "is_packed": False, "is_custom": False})

    # 6. Activity
    activities = [
        {"name": "Refillable insulated water bottle (750ml+)", "qty": 1},
        {"name": "Daypack backpack (15–20 Liters)", "qty": 1},
        {"name": "Waterproof ziplock pouches for phone and cash", "qty": 3}
    ]
    if "adventure" in travel_style.lower():
        activities.append({"name": "Headlamp or compact LED torch with extra batteries", "qty": 1})
        
    for a in activities:
        items.append({"category": "Activity", "item_name": a["name"], "quantity": a["qty"], "is_packed": False, "is_custom": False})

    return items

