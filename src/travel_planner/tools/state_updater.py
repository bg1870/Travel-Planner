"""set_travel_state tool -- lets the orchestrator persist structured state."""

import json
from typing import Optional

from langchain_core.tools import tool


@tool
def set_travel_state(
    stage: Optional[int] = None,
    approved_plan: Optional[dict] = None,
    approved_flight: Optional[dict] = None,
    approved_hotel: Optional[dict] = None,
    rejection_constraints: Optional[dict] = None,
    booking_refs: Optional[dict] = None,
) -> str:
    """Persist structured travel planning state at key conversation transitions.

    Call this tool to record state changes explicitly — do not rely solely on
    conversation history, which may be compacted. Only include fields that are
    changing. Pass the FULL updated value for each field (not just the delta).

    When to call:
    - User approves the travel plan (Checkpoint 1):
        stage=2, approved_plan={"budget_split": {...}, "recommended_airlines": [...], "hotel_areas": [...]}
    - User rejects and adds constraints (any stage):
        rejection_constraints={"flight_agent": ["no budget airlines", ...], "hotel_agent": [...]}
        (pass the full accumulated list for each agent, not just the new constraint)
    - User approves flight and hotel (Checkpoint 2):
        approved_flight={"flight_id": ..., "airline": ..., "price": ...},
        approved_hotel={"hotel_id": ..., "name": ..., "area": ..., "price_per_night": ..., "total_price": ...}
    - Booking confirmed and completed (Checkpoint 3):
        stage=3, booking_refs={"flight_ref": ..., "hotel_ref": ...}

    Args:
        stage: Pipeline stage. 1=planning, 2=selection, 3=booking.
        approved_plan: Budget split and recommendations approved at Checkpoint 1.
        approved_flight: Approved flight details including flight_id and price.
        approved_hotel: Approved hotel details including hotel_id and total price.
        rejection_constraints: Full dict mapping agent_id to all accumulated constraints.
        booking_refs: Final booking reference numbers after successful booking.

    Returns:
        JSON confirmation string consumed by the orchestrator node.
    """
    payload: dict = {"__state_update__": True}
    if stage is not None:
        payload["stage"] = stage
    if approved_plan is not None:
        payload["approved_plan"] = approved_plan
    if approved_flight is not None:
        payload["approved_flight"] = approved_flight
    if approved_hotel is not None:
        payload["approved_hotel"] = approved_hotel
    if rejection_constraints is not None:
        payload["rejection_constraints"] = rejection_constraints
    if booking_refs is not None:
        payload["booking_refs"] = booking_refs
    return json.dumps(payload)
