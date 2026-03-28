"""Snapshot generation via LLM-driven conversation compaction.

When the estimated context window usage reaches 30% of the model's context
window, the orchestrate node calls ``maybe_compact`` to produce a structured
9-section summary.  The snapshot is written to a standalone Markdown file
(``sessions/{uuid}/snapshot_{N}.md``) -- conversation.json remains a clean
record of raw entries only.

The snapshot ID and the number of conversation entries it covers are stored
in the graph state.  On resumption the code loads ``snapshot_{id}.md`` +
``conversation.json[entry_count:]`` to reconstruct context.
"""

import asyncio
import json
import logging
from pathlib import Path

from travel_planner.models import get_sub_model
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

logger = logging.getLogger(__name__)

from travel_planner.session.persistence import load_conversation, save_snapshot

# ---------------------------------------------------------------------------
# Context window threshold
# ---------------------------------------------------------------------------

# Claude Sonnet 4.6 context window in tokens.
_MODEL_CONTEXT_WINDOW = 200_000
# Compaction triggers when estimated usage reaches this fraction.
_COMPACTION_THRESHOLD = 0.30
# Rough chars-per-token ratio for estimation.
_CHARS_PER_TOKEN = 4

# ---------------------------------------------------------------------------
# Compaction prompt (loaded once, cached at module level)
# ---------------------------------------------------------------------------

_COMPACTION_PROMPT: str | None = None


def _read_compaction_prompt() -> str:
    global _COMPACTION_PROMPT
    if _COMPACTION_PROMPT is None:
        prompt_path = Path(__file__).parent.parent / "prompts" / "conversation_compaction.prompt.md"
        _COMPACTION_PROMPT = prompt_path.read_text()
    return _COMPACTION_PROMPT


async def _get_compaction_prompt() -> str:
    return await asyncio.to_thread(_read_compaction_prompt)


def estimate_token_usage(messages: list[BaseMessage]) -> int:
    """Estimate total token count from a list of LangChain messages.

    Uses a simple chars / 4 heuristic.  This is intentionally conservative
    -- it only measures message content, not tool definitions or system
    prompt overhead.
    """
    total_chars = 0
    for msg in messages:
        content = msg.content if isinstance(msg.content, str) else str(msg.content)
        total_chars += len(content)
    return total_chars // _CHARS_PER_TOKEN


def should_compact(messages: list[BaseMessage]) -> bool:
    """Return True when estimated context usage >= 30% of the model window."""
    return estimate_token_usage(messages) >= int(_MODEL_CONTEXT_WINDOW * _COMPACTION_THRESHOLD)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def generate_snapshot(
    state: dict,
    snapshot_id: int,
    session_dir: str | Path,
) -> dict:
    """Generate a compaction snapshot when context pressure warrants it.

    The snapshot is written to ``snapshot_{snapshot_id}.md`` in the session
    directory.  ``conversation.json`` is not modified.

    Returns:
        A state-update dict with ``last_snapshot_id`` and
        ``last_snapshot_entry_count``.
    """
    session_dir = Path(session_dir)
    logger.info("Generating snapshot #%d for session %s", snapshot_id, session_dir.name)
    conversation = await asyncio.to_thread(load_conversation, session_dir)
    logger.debug("Loaded %d conversation entries", len(conversation))

    # Determine entries to summarize: everything after the last snapshot's
    # coverage, or the full conversation if no prior snapshot exists.
    prev_count = state.get("last_snapshot_entry_count")
    if prev_count is not None:
        entries_to_summarize = conversation[prev_count:]
    else:
        entries_to_summarize = conversation
    logger.debug("Summarizing %d entries (prev_count=%s)", len(entries_to_summarize), prev_count)

    # Truncate entries for LLM context (keep under ~4000 chars)
    entries_json = json.dumps(entries_to_summarize, indent=2)
    if len(entries_json) > 4000:
        entries_json = entries_json[:4000] + "\n... (truncated)"

    # Build the user message with context
    user_message = (
        f"## Conversation Entries to Summarize\n\n"
        f"```json\n{entries_json}\n```\n\n"
        f"## Context\n\n"
        f"- Snapshot ID: {snapshot_id}\n"
        f"- Session ID: {state.get('session_id', 'unknown')}\n"
    )

    # Invoke Haiku for summary generation
    llm = get_sub_model(max_tokens=1000)
    response = await llm.ainvoke([
        SystemMessage(content=await _get_compaction_prompt()),
        HumanMessage(content=user_message),
    ])
    summary = response.content

    # Write snapshot to its own .md file
    await asyncio.to_thread(save_snapshot, session_dir, snapshot_id, summary)
    logger.info("Snapshot #%d saved (%d entries covered)", snapshot_id, len(conversation))

    return {
        "last_snapshot_id": snapshot_id,
        "last_snapshot_entry_count": len(conversation),
    }


async def maybe_compact(state: dict, session_dir: str | Path, *, force: bool = False) -> dict:
    """Check context pressure and generate a snapshot if needed.

    Called before each LLM call in the orchestrate node.  Returns an
    empty dict if compaction is not needed, otherwise returns the
    state update from ``generate_snapshot``.
    """
    messages = state.get("messages", [])
    estimated = estimate_token_usage(messages)
    threshold = int(_MODEL_CONTEXT_WINDOW * _COMPACTION_THRESHOLD)
    logger.debug(
        "maybe_compact: force=%s, estimated_tokens=%d, threshold=%d",
        force, estimated, threshold,
    )
    if not force and not should_compact(messages):
        logger.debug("Compaction skipped (below threshold and not forced)")
        return {}

    logger.info("Compaction triggered (force=%s)", force)
    last_id = state.get("last_snapshot_id") or 0
    return await generate_snapshot(state, last_id + 1, session_dir)
