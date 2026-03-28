"""Custom LangGraph checkpointer that bridges to our session persistence layer.

This is a simplified implementation that:
  - Inherits from ``BaseCheckpointSaver`` (langgraph.checkpoint.base)
  - Stores the LangGraph checkpoint as a serialized dict in
    ``checkpoint.json`` alongside our session files
  - ``put()`` saves the checkpoint and syncs snapshot fields to session.json
  - ``get_tuple()`` loads the checkpoint

Our node functions explicitly call ``persistence.py`` helpers to append
conversation entries.  This checkpointer handles LangGraph's internal
state machinery only — it is a pragmatic bridge, not the primary
persistence mechanism.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator, Optional, Sequence

from langgraph.checkpoint.base import (
    BaseCheckpointSaver,
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
)

from travel_planner.session.persistence import load_session_meta, save_session_meta

# Default sessions root — must match manager.py
SESSIONS_DIR = Path("sessions")


class SessionCheckpointer(BaseCheckpointSaver):
    """A LangGraph checkpointer that persists to our session directory.

    Each session already has ``sessions/{uuid}/`` with ``session.json``
    and ``conversation.json``.  This checkpointer adds a
    ``checkpoint.json`` file for LangGraph's internal checkpoint data.
    """

    def __init__(self, sessions_dir: str | Path = SESSIONS_DIR) -> None:
        super().__init__()
        self.sessions_dir = Path(sessions_dir)

    # -- helpers -------------------------------------------------------------

    def _session_dir(self, config: dict) -> Path:
        """Extract the session directory from a LangGraph config."""
        thread_id = config["configurable"]["thread_id"]
        return self.sessions_dir / thread_id

    def _checkpoint_path(self, config: dict) -> Path:
        return self._session_dir(config) / "checkpoint.json"

    def _load_checkpoint_file(self, config: dict) -> dict | None:
        path = self._checkpoint_path(config)
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None

    def _save_checkpoint_file(self, config: dict, data: dict) -> None:
        path = self._checkpoint_path(config)
        path.write_text(
            json.dumps(data, indent=2, default=str, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    # -- BaseCheckpointSaver interface ---------------------------------------

    def get_tuple(self, config: dict) -> Optional[CheckpointTuple]:
        """Load the LangGraph checkpoint for a session.

        Returns ``None`` if no checkpoint has been saved yet.
        """
        data = self._load_checkpoint_file(config)
        if data is None:
            return None

        checkpoint: Checkpoint = data.get("checkpoint", {})
        metadata: CheckpointMetadata = data.get("metadata", {})

        return CheckpointTuple(
            config=config,
            checkpoint=checkpoint,
            metadata=metadata,
        )

    def put(
        self,
        config: dict,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: Any = None,
    ) -> dict:
        """Save a LangGraph checkpoint and sync snapshot fields to session.json."""
        self._save_checkpoint_file(config, {
            "checkpoint": checkpoint,
            "metadata": metadata,
        })

        # Sync snapshot tracking fields to session.json if present.
        channel_values = checkpoint.get("channel_values", {})
        snap_id = channel_values.get("last_snapshot_id")
        snap_count = channel_values.get("last_snapshot_entry_count")
        if snap_id is not None or snap_count is not None:
            session_dir = self._session_dir(config)
            meta = load_session_meta(session_dir)
            if snap_id is not None:
                meta["last_snapshot_id"] = snap_id
            if snap_count is not None:
                meta["last_snapshot_entry_count"] = snap_count
            save_session_meta(session_dir, meta)

        return config

    def list(
        self,
        config: Optional[dict] = None,
        *,
        filter: Optional[dict[str, Any]] = None,
        before: Optional[dict] = None,
        limit: Optional[int] = None,
    ) -> Iterator[CheckpointTuple]:
        """List checkpoints. We only store one checkpoint per session."""
        if config is None:
            return
        tup = self.get_tuple(config)
        if tup is not None:
            yield tup

    def put_writes(
        self,
        config: dict,
        writes: Sequence[tuple[str, Any]],
        task_id: str,
    ) -> None:
        """Store intermediate writes. Not needed for our simplified checkpointer."""
        pass
