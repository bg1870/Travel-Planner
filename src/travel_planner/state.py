"""TravelPlannerState -- the LangGraph runtime state schema.

The orchestrator LLM tracks conversation stage, rejection constraints,
and approved results both through structured state fields (for reliability
across context boundaries) and through conversation history reasoning.
"""

from typing import Annotated, Optional

from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class TravelPlannerState(TypedDict):
    # Conversation history (LangGraph manages via add_messages reducer)
    messages: Annotated[list[BaseMessage], add_messages]

    # Session identity
    session_id: str

    # Snapshot tracking for context compaction
    last_snapshot_id: Optional[int]
    last_snapshot_entry_count: Optional[int]
    # Number of LangGraph state messages at the time of last compaction.
    # Messages at index >= this are "post-snapshot" and sent to the LLM directly.
    last_snapshot_message_count: Optional[int]

    # --- Structured travel state (updated via set_travel_state tool) ---

    # Current pipeline stage: 1=planning, 2=selection, 3=booking (None treated as 1)
    stage: Optional[int]

    # Approved output from trip_advisor at Checkpoint 1.
    # Expected keys: budget_split (flights/hotels/activities), recommended_airlines,
    # hotel_areas, destination_overview.
    approved_plan: Optional[dict]

    # Approved flight at Checkpoint 2.
    # Expected keys: flight_id, airline, price, outbound, inbound.
    approved_flight: Optional[dict]

    # Approved hotel at Checkpoint 2.
    # Expected keys: hotel_id, name, area, price_per_night, total_price.
    approved_hotel: Optional[dict]

    # Accumulated rejection constraints per agent.
    # Format: {"flight_agent": ["no budget airlines", ...], "hotel_agent": [...]}
    rejection_constraints: Optional[dict]

    # Final booking reference numbers set at Checkpoint 3.
    # Expected keys: flight_ref, hotel_ref.
    booking_refs: Optional[dict]
