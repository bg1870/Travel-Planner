"""Low-level JSON file I/O for session persistence.

Each session lives in its own directory with two files:
  - session.json       (metadata, configuration, and snapshot tracking)
  - conversation.json  (full conversation history, the source of truth)

All files use JSON with indent=2 for human readability.
Missing files are handled gracefully — reads return empty list/dict.
"""

import json
from pathlib import Path


# ---------------------------------------------------------------------------
# conversation.json
# ---------------------------------------------------------------------------

def load_conversation(session_dir: str | Path) -> list[dict]:
    """Read conversation.json and return the list of entries.

    Returns an empty list if the file does not exist or is empty.
    """
    path = Path(session_dir) / "conversation.json"
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_conversation(session_dir: str | Path, entries: list[dict]) -> None:
    """Write the full conversation entries list to conversation.json."""
    path = Path(session_dir) / "conversation.json"
    path.write_text(json.dumps(entries, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def append_entry(session_dir: str | Path, entry: dict) -> None:
    """Load conversation.json, append a single entry, and save it back."""
    entries = load_conversation(session_dir)
    entries.append(entry)
    save_conversation(session_dir, entries)


# ---------------------------------------------------------------------------
# session.json
# ---------------------------------------------------------------------------

def load_session_meta(session_dir: str | Path) -> dict:
    """Read session.json and return the metadata dict.

    Returns an empty dict if the file does not exist.
    """
    path = Path(session_dir) / "session.json"
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def save_session_meta(session_dir: str | Path, meta: dict) -> None:
    """Write session metadata to session.json."""
    path = Path(session_dir) / "session.json"
    path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# snapshot_{N}.md  — each snapshot is a standalone Markdown file
# ---------------------------------------------------------------------------

def save_snapshot(session_dir: str | Path, snapshot_id: int, content: str) -> None:
    """Write a compaction snapshot to ``snapshot_{N}.md``."""
    path = Path(session_dir) / f"snapshot_{snapshot_id}.md"
    path.write_text(content, encoding="utf-8")


def load_snapshot(session_dir: str | Path, snapshot_id: int) -> str | None:
    """Read a compaction snapshot from ``snapshot_{N}.md``.

    Returns ``None`` if the file does not exist.
    """
    path = Path(session_dir) / f"snapshot_{snapshot_id}.md"
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")
