"""Budget calculation tool."""

from langchain_core.tools import tool

from travel_planner.mock_data import load_budget_reference


@tool
def budget_calculator(destination: str, days: int, tier: str) -> dict:
    """Estimate trip costs for a destination based on travel tier and duration.

    Args:
        destination: City name (e.g. "paris").
        days: Number of days for the trip.
        tier: Budget tier — one of "budget", "mid_range", or "luxury".

    Returns:
        Detailed budget breakdown with daily costs, totals, and split percentages.
    """
    data = load_budget_reference()
    ref_map = data.get("budget_reference", data)

    dest_key = destination.lower()
    dest_data = ref_map.get(dest_key)
    if dest_data is None:
        return {"error": f"Destination '{destination}' not found in budget reference"}

    daily_costs_all = dest_data.get("daily_costs_usd", {})
    daily_costs = daily_costs_all.get(tier)
    if daily_costs is None:
        available = list(daily_costs_all.keys())
        return {
            "error": f"Tier '{tier}' not found for {destination}. Available: {available}"
        }

    estimated_daily_total = sum(daily_costs.values())
    estimated_trip_total = estimated_daily_total * days

    split = dest_data.get("default_budget_split", {})
    flights_pct = split.get("flights_pct", 0)
    hotels_pct = split.get("hotels_pct", 0)
    activities_pct = split.get("activities_pct", 0)

    budget_split = {
        "flights": round(estimated_trip_total * flights_pct / 100, 2),
        "hotels": round(estimated_trip_total * hotels_pct / 100, 2),
        "activities": round(estimated_trip_total * activities_pct / 100, 2),
    }

    warnings: list[str] = []

    return {
        "destination": destination,
        "days": days,
        "tier": tier,
        "daily_costs": daily_costs,
        "estimated_daily_total": estimated_daily_total,
        "estimated_trip_total": estimated_trip_total,
        "budget_split": budget_split,
        "warnings": warnings,
    }
