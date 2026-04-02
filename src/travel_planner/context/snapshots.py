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

# Fixed overhead added to every estimate to account for tokens that live
# outside the messages list: system prompt (~1 200 tokens), tool definitions
# for the 5 orchestrator tools (~600 tokens), and per-message formatting
# (~4 tokens × message count is handled inline).
_OVERHEAD_TOKENS = 1_800

# ---------------------------------------------------------------------------
# Tokenizer (tiktoken, with chars/4 fallback)
# ---------------------------------------------------------------------------

_TOKENIZER = None
_TOKENIZER_CHECKED = False


def _get_tokenizer():
    """Return a tiktoken encoder, or None if tiktoken is not installed.

    Uses a separate _TOKENIZER_CHECKED flag so None unambiguously means
    "unavailable" rather than "not yet tried".
    """
    global _TOKENIZER, _TOKENIZER_CHECKED
    if _TOKENIZER_CHECKED:
        return _TOKENIZER
    _TOKENIZER_CHECKED = True
    try:
        import tiktoken
        # cl100k_base is used by GPT-4 and is a close approximation for
        # Claude models — significantly more accurate than chars / 4,
        # especially for JSON-heavy tool results.
        _TOKENIZER = tiktoken.get_encoding("cl100k_base")
    except Exception:
        _TOKENIZER = None  # unavailable — fallback to chars / 4
    return _TOKENIZER


def _count_tokens(text: str, enc=None) -> int:
    """Count tokens in a string using tiktoken, falling back to chars / 4."""
    if enc is None:
        enc = _get_tokenizer()
    if enc is not None:
        return len(enc.encode(text, disallowed_special=()))
    return len(text) // 4

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

    Uses tiktoken (cl100k_base) when available, falls back to chars / 4.
    Adds a fixed overhead of _OVERHEAD_TOKENS to account for the system
    prompt and tool definitions that are not present in the messages list.

    Per-message formatting cost (~4 tokens for role + delimiters) is also
    added for accuracy on short conversations.
    """
    token_count = _OVERHEAD_TOKENS
    enc = _get_tokenizer()  # resolve once; avoids repeated global lookup per content block
    for msg in messages:
        # Per-message role/formatting overhead
        token_count += 4
        content = msg.content
        if isinstance(content, str):
            token_count += _count_tokens(content, enc)
        elif isinstance(content, list):
            # Content blocks (e.g. tool result lists, multimodal)
            for block in content:
                if isinstance(block, dict):
                    token_count += _count_tokens(block.get("text", str(block)), enc)
                else:
                    token_count += _count_tokens(str(block), enc)
        else:
            token_count += _count_tokens(str(content), enc)
    return token_count


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
