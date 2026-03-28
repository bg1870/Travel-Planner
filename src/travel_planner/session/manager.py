"""Session lifecycle management — create, resume, and complete sessions.

Sessions are stored under a configurable root directory (default:
``sessions/`` relative to the project root).  Each session gets its own
sub-directory named by UUID containing ``session.json`` and
``conversation.json``.
"""

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from travel_planner.session.persistence import (
    load_conversation,
    load_session_meta,
    load_snapshot,
    save_conversation,
    save_session_meta,
)

# Default sessions root, relative to the project working directory.
SESSIONS_DIR = Path("sessions")


def _resolve_session_dir(session_id: str, sessions_dir: Path | None = None) -> Path:
    """Return the directory for a given session id."""
    base = sessions_dir if sessions_dir is not None else SESSIONS_DIR
    return base / session_id


# ---------------------------------------------------------------------------
# create
# ---------------------------------------------------------------------------

def create_session(
    confirmation_mode: str = "normal",
    sessions_dir: Path | None = None,
) -> str:
    """Create a new session directory with initial files.

    Args:
        confirmation_mode: One of ``"careful"``, ``"normal"``, ``"fast"``,
            ``"trust"``.
        sessions_dir: Override for the sessions root directory.

    Returns:
        The generated session id (a UUID string).
    """
    session_id = str(uuid4())
    session_dir = _resolve_session_dir(session_id, sessions_dir)
    session_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc).isoformat()

    # session.json — metadata, configuration, and snapshot tracking
    save_session_meta(session_dir, {
        "id": session_id,
        "created_at": now,
        "updated_at": now,
        "status": "in_progress",
        "confirmation_mode": confirmation_mode,
        "models": {
            "orchestrator": "claude-sonnet-4-6",
            "sub_agents": "claude-haiku-4-5",
        },
        "last_snapshot_id": None,
        "last_snapshot_entry_count": None,
        "conversation_entries": 0,
    })

    # conversation.json — empty list (no entries yet)
    save_conversation(session_dir, [])

    return session_id


# ---------------------------------------------------------------------------
# resume
# ---------------------------------------------------------------------------

def resume_session(
    session_id: str,
    sessions_dir: Path | None = None,
) -> dict:
    """Load a session for resumption using the snapshot + tail pattern.

    Snapshots live in standalone ``.md`` files (``snapshot_{id}.md``).
    ``conversation.json`` contains only raw entries.  The snapshot ID and
    the entry count it covers are stored in ``session.json`` so we can
    compute the tail at code level.

    Returns a dict with:
      - ``snapshot``: the snapshot Markdown string, or ``None``.
      - ``tail``: conversation entries after the snapshot coverage (or
        the full conversation if no snapshot exists).
      - ``meta``: the current ``session.json`` contents.
    """
    session_dir = _resolve_session_dir(session_id, sessions_dir)

    meta = load_session_meta(session_dir)
    conversation = load_conversation(session_dir)

    snapshot_id = meta.get("last_snapshot_id")
    entry_count = meta.get("last_snapshot_entry_count")

    if snapshot_id is not None:
        snapshot = load_snapshot(session_dir, snapshot_id)
        if entry_count is not None and entry_count <= len(conversation):
            tail = conversation[entry_count:]
        else:
            tail = conversation
    else:
        snapshot = None
        tail = conversation

    return {
        "snapshot": snapshot,
        "tail": tail,
        "meta": meta,
    }


# ---------------------------------------------------------------------------
# complete
# ---------------------------------------------------------------------------

def complete_session(
    session_id: str,
    status: str = "completed",
    sessions_dir: Path | None = None,
) -> None:
    """Mark a session as completed (or cancelled).

    Updates ``session.json`` with the new status and an ``updated_at``
    timestamp.
    """
    session_dir = _resolve_session_dir(session_id, sessions_dir)
    meta = load_session_meta(session_dir)
    meta["status"] = status
    meta["updated_at"] = datetime.now(timezone.utc).isoformat()
    save_session_meta(session_dir, meta)
