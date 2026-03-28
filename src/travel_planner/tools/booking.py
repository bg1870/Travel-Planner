"""Booking tools for flights and hotels."""

import random
import string
from datetime import datetime, timezone

from langchain_core.tools import tool

from travel_planner.mock_data import load_flights, load_hotels


def _generate_booking_ref() -> str:
    """Generate a random booking reference like BK-A3F8K2."""
    chars = string.ascii_uppercase + string.digits
    suffix = "".join(random.choices(chars, k=6))
    return f"BK-{suffix}"


def _find_flight(flight_id: str) -> dict | None:
    """Find a flight by ID across all routes."""
    data = load_flights()
    flights_map = data.get("flights", data)
    for route_data in flights_map.values():
        for flight in route_data.get("listings", []):
            if flight.get("flight_id") == flight_id:
                return flight
    return None


def _find_hotel(hotel_id: str) -> dict | None:
    """Find a hotel by ID across all cities."""
    data = load_hotels()
    hotels_map = data.get("hotels", data)
    for city_hotels in hotels_map.values():
        for hotel in city_hotels:
            if hotel.get("hotel_id") == hotel_id:
                return hotel
    return None


@tool
def book_flight(flight_id: str, passenger_name: str = None) -> dict:
    """Book a flight by its ID.

    Args:
        flight_id: The flight ID to book (e.g. "CAI-CDG-001").
        passenger_name: Optional passenger name for the booking.

    Returns:
        Booking confirmation dict with reference, status, and flight details.
    """
    flight = _find_flight(flight_id)
    if flight is None:
        return {"error": f"Flight '{flight_id}' not found"}

    return {
        "booking_reference": _generate_booking_ref(),
        "status": "confirmed",
        "confirmed_at": datetime.now(timezone.utc).isoformat(),
        "flight": flight,
        "passenger_name": passenger_name,
    }


@tool
def book_hotel(
    hotel_id: str,
    guest_name: str = None,
    check_in: str = None,
    check_out: str = None,
) -> dict:
    """Book a hotel by its ID.

    Args:
        hotel_id: The hotel ID to book (e.g. "PAR-HTL-001").
        guest_name: Optional guest name for the booking.
        check_in: Optional check-in date (YYYY-MM-DD).
        check_out: Optional check-out date (YYYY-MM-DD).

    Returns:
        Booking confirmation dict with reference, status, hotel details, and total price.
    """
    hotel = _find_hotel(hotel_id)
    if hotel is None:
        return {"error": f"Hotel '{hotel_id}' not found"}

    confirmation: dict = {
        "booking_reference": _generate_booking_ref(),
        "status": "confirmed",
        "confirmed_at": datetime.now(timezone.utc).isoformat(),
        "hotel": hotel,
        "guest_name": guest_name,
    }

    if check_in and check_out:
        check_in_dt = datetime.strptime(check_in, "%Y-%m-%d")
        check_out_dt = datetime.strptime(check_out, "%Y-%m-%d")
        num_nights = max((check_out_dt - check_in_dt).days, 1)
        total_price = hotel.get("price_per_night_usd", 0) * num_nights
        confirmation["check_in"] = check_in
        confirmation["check_out"] = check_out
        confirmation["num_nights"] = num_nights
        confirmation["total_price"] = total_price

    return confirmation
