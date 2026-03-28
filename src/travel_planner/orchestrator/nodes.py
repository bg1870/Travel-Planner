"""Orchestrator nodes -- single agentic loop with tool execution.

The orchestrate node runs the orchestrator LLM with spawn_agent, load_skill,
and booking tools.  The tool node executes all tool calls.  Together they
form a standard ReAct loop: orchestrate -> tools -> orchestrate -> ... -> END.
"""

import asyncio
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.graph import END
from langgraph.prebuilt import ToolNode

from travel_planner.agents.registry import get_registry_summary
from travel_planner.agents.runner import spawn_agent
from travel_planner.context.snapshots import maybe_compact
from travel_planner.session.manager import create_session, SESSIONS_DIR
from travel_planner.session.persistence import (
    append_entry,
    load_conversation,
    load_session_meta,
    load_snapshot,
    save_session_meta,
)
from travel_planner.session.entries import (
    make_message_entry,
    make_tool_call_entry,
    make_tool_result_entry,
)
from travel_planner.skills.loader import load_skill
from travel_planner.tools.booking import book_flight, book_hotel

# ---------------------------------------------------------------------------
# Prompt loading
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT: str | None = None


def _load_system_prompt() -> str:
    """Load orchestrator system prompt and inject the agent registry."""
    global _SYSTEM_PROMPT
    if _SYSTEM_PROMPT is None:
        prompt_path = Path(__file__).parent.parent / "prompts" / "orchestrator.system.md"
        raw = prompt_path.read_text()
        registry_summary = get_registry_summary()
        _SYSTEM_PROMPT = raw.replace("{{AGENT_REGISTRY}}", registry_summary)
    return _SYSTEM_PROMPT


# ---------------------------------------------------------------------------
# Orchestrate node
# ---------------------------------------------------------------------------

from travel_planner.models import get_main_model

_model = get_main_model()
_tools = [spawn_agent, load_skill, book_flight, book_hotel]
_model_with_tools = _model.bind_tools(_tools)


def _find_agent_id_for_tool_call(messages: list, tool_call_id: str) -> str:
    """Walk backwards through messages to find the agent_id for a tool_call_id."""
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and msg.tool_calls:
            for tc in msg.tool_calls:
                if tc["id"] == tool_call_id:
                    return tc["args"].get("agent_id", "unknown")
    return "unknown"


async def _persist_incoming(session_dir: Path, messages: list) -> None:
    """Persist new incoming messages (user messages or tool results)."""
    if not messages:
        return

    last = messages[-1]

    # User turn: persist the user message
    if isinstance(last, HumanMessage):
        content = last.content if isinstance(last.content, str) else str(last.content)
        await asyncio.to_thread(
            append_entry, session_dir,
            make_message_entry("user", content),
        )

    # Tool loop: persist tool result(s) — there may be multiple ToolMessages
    # from a single AI message with multiple tool_calls
    elif isinstance(last, ToolMessage):
        for msg in messages:
            if isinstance(msg, ToolMessage) and not getattr(msg, "_persisted", False):
                agent_id = _find_agent_id_for_tool_call(messages, msg.tool_call_id)
                content = msg.content if isinstance(msg.content, str) else str(msg.content)
                await asyncio.to_thread(
                    append_entry, session_dir,
                    make_tool_result_entry(agent_id, content),
                )


async def _persist_response(session_dir: Path, response: AIMessage) -> None:
    """Persist the AI response — text message and/or tool calls."""
    # Persist tool call entries
    if response.tool_calls:
        for tc in response.tool_calls:
            if tc["name"] == "spawn_agent":
                agent_label = tc["args"].get("agent_id", "unknown")
                prompt_text = tc["args"].get("prompt", "")
            else:
                agent_label = tc["name"]
                prompt_text = str(tc["args"])
            await asyncio.to_thread(
                append_entry, session_dir,
                make_tool_call_entry(agent_label, prompt_text),
            )

    # Persist assistant text (may coexist with tool calls or be standalone)
    content = response.content if isinstance(response.content, str) else str(response.content)
    if content.strip():
        await asyncio.to_thread(
            append_entry, session_dir,
            make_message_entry("assistant", content),
        )


def _sync_session_file(session_dir: Path, state: dict) -> None:
    """Sync session.json with current progress.

    Called after each orchestrate iteration so the session file reflects
    the latest state on disk.
    """
    from datetime import datetime, timezone

    meta = load_session_meta(session_dir)
    conversation = load_conversation(session_dir)

    meta["updated_at"] = datetime.now(timezone.utc).isoformat()
    meta["last_snapshot_id"] = state.get("last_snapshot_id")
    meta["last_snapshot_entry_count"] = state.get("last_snapshot_entry_count")
    meta["last_snapshot_message_count"] = state.get("last_snapshot_message_count")
    meta["conversation_entries"] = len(conversation)

    save_session_meta(session_dir, meta)


async def orchestrate_node(state: dict) -> dict:
    """Main orchestrator node: check compaction, call LLM, return response.

    On first invocation (no session_id), creates a new session.
    Before each LLM call, checks context pressure and compacts if needed.
    Persists all messages to conversation.json.
    """
    updates: dict = {}

    # Create session on first invocation (file I/O — run in thread)
    session_id = state.get("session_id")
    if not session_id:
        session_id = await asyncio.to_thread(create_session)
        updates["session_id"] = session_id

    session_dir = SESSIONS_DIR / session_id

    # Persist incoming messages (user message or tool results)
    await _persist_incoming(session_dir, state.get("messages", []))

    # Check for /compact command or context pressure
    msgs = state.get("messages", [])
    last_msg = msgs[-1] if msgs else None
    def _is_compact_command(msg) -> bool:
        if not isinstance(msg, HumanMessage):
            return False
        c = msg.content
        if isinstance(c, str):
            return c.strip() == "/compact"
        if isinstance(c, list):
            texts = [b["text"] for b in c if isinstance(b, dict) and b.get("type") == "text"]
            return len(texts) == 1 and texts[0].strip() == "/compact"
        return False

    force_compact = _is_compact_command(last_msg)
    if force_compact:
        logger.info("User triggered /compact command")
    compact_update = await maybe_compact(state, session_dir, force=force_compact)
    if compact_update:
        logger.info("Compaction applied: %s", compact_update)
        # Record how many LangGraph messages existed at compaction time so we
        # can slice off pre-snapshot messages on subsequent calls.
        compact_update["last_snapshot_message_count"] = len(msgs)
        updates.update(compact_update)

    if force_compact:
        from langchain_core.messages import AIMessage
        updates["messages"] = [AIMessage(content="Context compacted.")]
        merged_state = {**state, **updates}
        await asyncio.to_thread(_sync_session_file, session_dir, merged_state)
        return updates

    # Build messages with system prompt (file I/O on first call — run in thread)
    system_prompt = await asyncio.to_thread(_load_system_prompt)

    last_snapshot_id = state.get("last_snapshot_id") or updates.get("last_snapshot_id")
    if last_snapshot_id:
        # Load snapshot and only send messages added after compaction
        snapshot_content = await asyncio.to_thread(load_snapshot, session_dir, last_snapshot_id)
        msg_count = state.get("last_snapshot_message_count") or updates.get("last_snapshot_message_count") or 0
        recent_messages = list(state.get("messages", []))[msg_count:]
        logger.info(
            "Using snapshot #%d + %d recent messages (total state messages: %d)",
            last_snapshot_id, len(recent_messages), len(state.get("messages", [])),
        )
        messages = (
            [SystemMessage(content=system_prompt)]
            + [HumanMessage(content=f"## Prior Conversation Summary\n\n{snapshot_content}")]
            + recent_messages
        )
    else:
        messages = [SystemMessage(content=system_prompt)] + list(state.get("messages", []))

    # Call orchestrator LLM (tag with session_id for LangSmith)
    response = await _model_with_tools.ainvoke(
        messages,
        config={"metadata": {"session_id": session_id}},
    )

    # Persist the AI response (text + tool calls)
    await _persist_response(session_dir, response)

    # Sync session.json with current progress
    merged_state = {**state, **updates}
    await asyncio.to_thread(_sync_session_file, session_dir, merged_state)

    updates["messages"] = [response]
    return updates


# ---------------------------------------------------------------------------
# Tool node + routing
# ---------------------------------------------------------------------------

tool_node = ToolNode(_tools)


def should_continue(state: dict) -> str:
    """Route: if last message has tool calls -> 'tools', otherwise -> END."""
    messages = state.get("messages", [])
    if not messages:
        return END

    last_message = messages[-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END
