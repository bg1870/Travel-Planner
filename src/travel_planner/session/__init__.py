"""Session management package — persistence, entries, lifecycle, and checkpointing."""

from travel_planner.session.entries import (
    make_checkpoint_entry,
    make_message_entry,
    make_snapshot_entry,
    make_tool_call_entry,
    make_tool_result_entry,
)
from travel_planner.session.manager import (
    complete_session,
    create_session,
    resume_session,
)
from travel_planner.session.persistence import (
    append_entry,
    load_conversation,
    load_session_meta,
    load_snapshot,
    save_conversation,
    save_session_meta,
    save_snapshot,
)


def __getattr__(name: str):
    """Lazy-import SessionCheckpointer to avoid requiring langgraph at import time."""
    if name == "SessionCheckpointer":
        from travel_planner.session.checkpointer import SessionCheckpointer
        return SessionCheckpointer
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # checkpointer (lazy)
    "SessionCheckpointer",
    # entries
    "make_checkpoint_entry",
    "make_message_entry",
    "make_snapshot_entry",
    "make_tool_call_entry",
    "make_tool_result_entry",
    # manager
    "create_session",
    "resume_session",
    "complete_session",
    # persistence
    "append_entry",
    "load_conversation",
    "load_session_meta",
    "load_snapshot",
    "save_conversation",
    "save_session_meta",
    "save_snapshot",
]
