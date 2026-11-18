from typing import Dict, Any

def simulate_trip_changes(
    original_cost: float,
    original_days: int,
    original_travellers: int,
    extra_days: int = 0,
    budget_change: float = 0.0,
    transport_mode: str = None,
    extra_travellers: int = 0,
    removed_destination: str = None
) -> Dict[str, Any]:
    new_days = max(1, original_days + extra_days)
    new_travellers = max(1, original_travellers + extra_travellers)
    
    # Calculate baseline daily cost per person excluding transit
    daily_cost_per_person = (original_cost * 0.70) / (original_days * original_travellers) if original_days > 0 and original_travellers > 0 else 2500.0
    
    # Transport impact
    transit_cost_base = (original_cost * 0.30) / original_travellers
    transport_impact_desc = "No transport mode changes."
    
    if transport_mode:
        if transport_mode.lower() == "train":
            transit_cost_base = max(800.0, transit_cost_base * 0.45) # 55% cheaper
            transport_impact_desc = "Switched to scenic railway: Saves ~55% on transportation, adds relaxed travel pace."
        elif transport_mode.lower() == "flight":
            transit_cost_base = transit_cost_base * 1.8 # faster, pricier
            transport_impact_desc = "Switched to express air travel: Cuts travel transit time by 70%, adds premium cost."
        elif transport_mode.lower() == "drive":
            transit_cost_base = transit_cost_base * 0.8
            transport_impact_desc = "Switched to road trip: Fuel & toll split makes it cost-effective for groups."

    # Group economies of scale (hotel rooms shared 2 per room)
    room_count = (new_travellers + 1) // 2
    accommodation_daily = 2200.0 * room_count
    food_and_activities_daily = 1400.0 * new_travellers
    
    new_total_cost = (transit_cost_base * new_travellers) + ((accommodation_daily + food_and_activities_daily) * new_days)
    
    if removed_destination:
        new_total_cost *= 0.85 # 15% reduction for fewer inter-city transfers
        
    cost_diff = round(new_total_cost - original_cost, 2)
    per_person = round(new_total_cost / new_travellers, 2)
    
    # Recommendations
    recommendations = []
    if extra_days > 0:
        recommendations.append(f"Adding {extra_days} day(s) allows exploring local heritage villages and unhurried cafes without rushing.")
    if extra_travellers > 0:
        recommendations.append(f"Adding {extra_travellers} member(s) reduces per-person accommodation and cab hire costs by ~{min(35, extra_travellers * 12)}%.")
    if budget_change < 0:
        recommendations.append(f"Compensate for the {abs(budget_change)} budget tightening by choosing cozy verified boutique homestays.")
        
    feasibility = "Within Budget"
    if budget_change != 0 and cost_diff > (budget_change + 1000):
        feasibility = "Slight Overrun"
    if cost_diff > 10000:
        feasibility = "Significant Budget Adjustment Needed"
        
    return {
        "original_cost": round(original_cost, 2),
        "new_cost": round(new_total_cost, 2),
        "cost_difference": cost_diff,
        "original_duration_days": original_days,
        "new_duration_days": new_days,
        "original_travellers": original_travellers,
        "new_travellers": new_travellers,
        "transport_impact": transport_impact_desc,
        "per_person_cost": per_person,
        "recommendations": recommendations,
        "feasibility_status": feasibility
    }

