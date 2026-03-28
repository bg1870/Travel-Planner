"""Search tools for destinations, flights, hotels, and web queries."""

from datetime import datetime

from langchain_core.tools import tool

from travel_planner.mock_data import (
    load_destinations,
    load_flights,
    load_hotels,
    load_web_results,
)


@tool
def web_search(query: str) -> list[dict]:
    """Search the web for travel-related information.

    Args:
        query: Free-text search query (e.g. "paris travel tips").

    Returns:
        List of matching search result dicts with title, snippet, and source.
    """
    data = load_web_results()
    results_map = data.get("web_results", data)

    query_tokens = set(query.lower().split())
    matches: list[dict] = []

    for key, snippets in results_map.items():
        key_tokens = set(key.lower().split())
        overlap = query_tokens & key_tokens
        if len(overlap) >= 2:
            matches.extend(snippets)

    return matches


@tool
def destination_lookup(city: str) -> dict:
    """Look up a city's full travel profile including weather, areas, costs, and airlines.

    Args:
        city: City name (e.g. "Paris", "Tokyo").

    Returns:
        Full destination profile dict, or an error dict if not found.
    """
    data = load_destinations()
    destinations = data.get("destinations", data)

    city_key = city.lower()
    if city_key in destinations:
        return destinations[city_key]

    return {"error": "City not found"}


@tool
def search_flights(
    origin: str,
    destination: str,
    date: str,
    return_date: str = None,
    max_price: float = None,
    preferred_airlines: list[str] = None,
) -> list[dict]:
    """Search available flights between two cities.

    Args:
        origin: Origin city name (e.g. "cairo").
        destination: Destination city name (e.g. "paris").
        date: Departure date (YYYY-MM-DD).
        return_date: Optional return date (YYYY-MM-DD).
        max_price: Optional maximum price in USD to filter results.
        preferred_airlines: Optional list of airline names to prioritize.

    Returns:
        List of flight dicts sorted with preferred airlines first.
    """
    data = load_flights()
    flights_map = data.get("flights", data)

    route_key = f"{origin.lower()}_to_{destination.lower()}"
    route = flights_map.get(route_key)
    if route is None:
        return []

    listings = list(route.get("listings", []))

    if max_price is not None:
        listings = [f for f in listings if f.get("price_usd", 0) <= max_price]

    if preferred_airlines:
        pref_lower = {a.lower() for a in preferred_airlines}

        def sort_key(flight: dict) -> int:
            return 0 if flight.get("airline", "").lower() in pref_lower else 1

        listings.sort(key=sort_key)

    return listings


@tool
def search_hotels(
    city: str,
    check_in: str,
    check_out: str,
    max_total_budget: float = None,
    preferred_areas: list[str] = None,
) -> list[dict]:
    """Search available hotels in a city for given dates.

    Args:
        city: City name (e.g. "paris").
        check_in: Check-in date (YYYY-MM-DD).
        check_out: Check-out date (YYYY-MM-DD).
        max_total_budget: Optional max total budget in USD for the entire stay.
        preferred_areas: Optional list of area names to prioritize.

    Returns:
        List of hotel dicts enriched with total_price, sorted with preferred areas first.
    """
    data = load_hotels()
    hotels_map = data.get("hotels", data)

    city_key = city.lower()
    hotels = hotels_map.get(city_key)
    if hotels is None:
        return []

    check_in_dt = datetime.strptime(check_in, "%Y-%m-%d")
    check_out_dt = datetime.strptime(check_out, "%Y-%m-%d")
    num_nights = max((check_out_dt - check_in_dt).days, 1)

    enriched: list[dict] = []
    for h in hotels:
        hotel = dict(h)
        total_price = hotel.get("price_per_night_usd", 0) * num_nights
        hotel["total_price"] = total_price
        enriched.append(hotel)

    if max_total_budget is not None:
        enriched = [h for h in enriched if h["total_price"] <= max_total_budget]

    if preferred_areas:
        pref_lower = {a.lower() for a in preferred_areas}

        def sort_key(hotel: dict) -> int:
            return 0 if hotel.get("area", "").lower() in pref_lower else 1

        enriched.sort(key=sort_key)

    return enriched
