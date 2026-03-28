"""Context Layer -- snapshot-based conversation compaction.

Provides context management through LLM-driven snapshots that compress
the conversation when context usage exceeds 30% of the model's window.
"""

from travel_planner.context.snapshots import (
    generate_snapshot,
    maybe_compact,
    should_compact,
)

__all__ = [
    "generate_snapshot",
    "maybe_compact",
    "should_compact",
]
