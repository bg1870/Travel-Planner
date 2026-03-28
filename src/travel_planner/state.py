"""TravelPlannerState -- the LangGraph runtime state schema.

Simplified to 4 fields. The orchestrator LLM tracks conversation stage,
rejection constraints, and approved results through its own reasoning
based on the conversation history and compaction snapshots.
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
