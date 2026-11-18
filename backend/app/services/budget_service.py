from typing import List, Dict, Any

# Standard benchmark budget allocations
ALLOCATION_PERCENTAGES = {
    "Transportation": 0.28,
    "Accommodation": 0.32,
    "Food": 0.20,
    "Activities": 0.10,
    "Shopping": 0.05,
    "Emergency reserve": 0.05
}

def calculate_budget_breakdown(
    total_budget: float,
    travellers_count: int = 1,
    expenses: List[Dict[str, Any]] = None,
    currency: str = "INR"
) -> Dict[str, Any]:
    if expenses is None:
        expenses = []
        
    per_person_budget = round(total_budget / max(1, travellers_count), 2)
    
    # Category allocations
    categories_breakdown = []
    actual_spent_by_category = {cat: 0.0 for cat in ALLOCATION_PERCENTAGES.keys()}
    actual_spent_by_category["Miscellaneous"] = 0.0
    
    total_actual_spent = 0.0
    for exp in expenses:
        cat = exp.get("category", "Miscellaneous")
        amt = float(exp.get("amount", 0.0))
        total_actual_spent += amt
        if cat in actual_spent_by_category:
            actual_spent_by_category[cat] += amt
        else:
            actual_spent_by_category["Miscellaneous"] += amt
            
    for cat, pct in ALLOCATION_PERCENTAGES.items():
        allocated = round(total_budget * pct, 2)
        spent = round(actual_spent_by_category.get(cat, 0.0), 2)
        diff = allocated - spent
        categories_breakdown.append({
            "category": cat,
            "allocated": allocated,
            "spent": spent,
            "remaining": diff,
            "percentage": int(pct * 100),
            "status": "Safe" if spent <= allocated else "Over Budget"
        })
        
    remaining_budget = round(total_budget - total_actual_spent, 2)
    spending_percentage = round((total_actual_spent / total_budget * 100) if total_budget > 0 else 0, 1)
    
    # Intelligent budget alerts
    alerts = []
    if total_actual_spent > total_budget:
        alerts.append({
            "type": "danger",
            "message": f"Total spending has exceeded budget by {currency} {round(total_actual_spent - total_budget, 2)}!"
        })
    elif spending_percentage > 85:
        alerts.append({
            "type": "warning",
            "message": f"You have utilized {spending_percentage}% of your total budget. Consider cost-free evening activities."
        })
    else:
        alerts.append({
            "type": "success",
            "message": f"Your travel spending is healthy. {currency} {remaining_budget} remaining."
        })
        
    # Check specific category overspends
    for cat_item in categories_breakdown:
        if cat_item["spent"] > cat_item["allocated"]:
            alerts.append({
                "type": "warning",
                "message": f"{cat_item['category']} spend is {currency} {round(cat_item['spent'] - cat_item['allocated'], 2)} above target allocation."
            })
            
    return {
        "currency": currency,
        "total_budget": total_budget,
        "per_person_budget": per_person_budget,
        "total_actual_spent": total_actual_spent,
        "per_person_actual": round(total_actual_spent / max(1, travellers_count), 2),
        "remaining_budget": remaining_budget,
        "spending_percentage": spending_percentage,
        "categories": categories_breakdown,
        "alerts": alerts,
        "is_verified_pricing": False,
        "pricing_notice": "Estimated costs are calculated based on seasonal regional averages. Verified receipts are tracked via logged expenses."
    }

