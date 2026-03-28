"""Comparison tools for flights and hotels."""

from langchain_core.tools import tool

from travel_planner.mock_data import load_flights, load_hotels


@tool
def compare_flights(flight_ids: list[str]) -> list[dict]:
    """Compare specific flights side-by-side by their IDs.

    Args:
        flight_ids: List of flight IDs to compare (e.g. ["CAI-CDG-001", "CAI-CDG-003"]).

    Returns:
        List of matching flight dicts for easy comparison.
    """
    data = load_flights()
    flights_map = data.get("flights", data)

    id_set = set(flight_ids)
    results: list[dict] = []

    for route_data in flights_map.values():
        for flight in route_data.get("listings", []):
            if flight.get("flight_id") in id_set:
                results.append(flight)

    return results


@tool
def compare_hotels(hotel_ids: list[str]) -> list[dict]:
    """Compare specific hotels side-by-side by their IDs.

    Args:
        hotel_ids: List of hotel IDs to compare (e.g. ["PAR-HTL-001", "PAR-HTL-003"]).

    Returns:
        List of matching hotel dicts for easy comparison.
    """
    data = load_hotels()
    hotels_map = data.get("hotels", data)

    id_set = set(hotel_ids)
    results: list[dict] = []

    for city_hotels in hotels_map.values():
        for hotel in city_hotels:
            if hotel.get("hotel_id") in id_set:
                results.append(hotel)

    return results
