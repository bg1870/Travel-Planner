"""Orchestrator nodes -- single agentic loop with tool execution.

The orchestrate node runs the orchestrator LLM with spawn_agent, load_skill,
set_travel_state, and booking tools.  The tool node executes all tool calls.
Together they form a standard ReAct loop:
  orchestrate -> tools -> orchestrate -> ... -> END.

Context engineering applied here:
  - Structured state is injected as a <current_state> block every turn so the
    LLM always has key facts without relying on conversation history retrieval.
  - Old tool results are pruned: only the last 2 spawn_agent results are kept
    in full; older ones are reduced to a one-line summary. set_travel_state
    results are always replaced with "[state updated]" since the state is
    captured in structured fields.
"""

import asyncio
import json
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
from travel_planner.tools.state_updater import set_travel_state

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
# Structured state helpers
# ---------------------------------------------------------------------------

_STATE_UPDATE_KEYS = (
    "stage", "approved_plan", "approved_flight",
    "approved_hotel", "rejection_constraints", "booking_refs",
)


def _find_tool_name_for_call(messages: list, tool_call_id: str) -> str:
    """Return the tool name for a given tool_call_id by scanning AIMessages."""
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and msg.tool_calls:
            for tc in msg.tool_calls:
                if tc["id"] == tool_call_id:
                    return tc["name"]
    return "unknown"


def _extract_state_updates(messages: list) -> dict:
    """Scan messages for set_travel_state results and return state field updates.

    The orchestrator node calls this at the start of each turn so that state
    written by the previous tool loop is applied before the next LLM call.
    """
    updates: dict = {}
    for msg in messages:
        if not isinstance(msg, ToolMessage):
            continue
        tool_name = _find_tool_name_for_call(messages, msg.tool_call_id)
        if tool_name != "set_travel_state":
            continue
        try:
            content = msg.content if isinstance(msg.content, str) else str(msg.content)
            result = json.loads(content)
        except (json.JSONDecodeError, TypeError, AttributeError):
            continue
        if not result.get("__state_update__"):
            continue
        for key in _STATE_UPDATE_KEYS:
            if key not in result:
                continue
            updates[key] = result[key]
    return updates


def _format_state_context(state: dict) -> str:
    """Render the current structured state as a <current_state> block.

    Injected into every LLM call so the orchestrator always has key facts
    without needing to re-derive them from conversation history.
    """
    stage = state.get("stage") or 1
    stage_labels = {1: "Stage 1 — Planning", 2: "Stage 2 — Selection", 3: "Stage 3 — Booking"}
    label = stage_labels.get(stage, f"Stage {stage}")

    approved_plan = state.get("approved_plan")
    approved_flight = state.get("approved_flight")
    approved_hotel = state.get("approved_hotel")
    rejection_constraints = state.get("rejection_constraints") or {}
    booking_refs = state.get("booking_refs")

    lines = [
        "<current_state>",
        f"stage: {label}",
        f"approved_plan: {json.dumps(approved_plan) if approved_plan else 'none'}",
        f"approved_flight: {json.dumps(approved_flight) if approved_flight else 'none'}",
        f"approved_hotel: {json.dumps(approved_hotel) if approved_hotel else 'none'}",
        f"rejection_constraints: {json.dumps(rejection_constraints) if rejection_constraints else 'none'}",
        f"booking_refs: {json.dumps(booking_refs) if booking_refs else 'none'}",
        "</current_state>",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Tool result pruning
# ---------------------------------------------------------------------------

def _prune_tool_results(messages: list, keep_recent: int = 2) -> list:
    """Reduce context size by summarising old tool results.

    Rules:
    - set_travel_state results: always replaced with "[state updated]" — the
      state is captured in structured fields, not in the message list.
    - All other tool results are grouped by their parent AIMessage turn.
      Parallel calls (e.g. flight_agent + hotel_agent in one response) count
      as a single turn and are kept or summarised together.
      The last `keep_recent` turns are kept in full; older turns are summarised.

    The AIMessages containing the tool_calls are left untouched so the LLM
    can still see what it called and why.
    """
    # Build a map: tool_call_id -> parent AIMessage index
    call_id_to_ai_idx: dict[str, int] = {}
    for i, msg in enumerate(messages):
        if isinstance(msg, AIMessage) and msg.tool_calls:
            for tc in msg.tool_calls:
                call_id_to_ai_idx[tc["id"]] = i

    # Group non-state ToolMessage indices by their parent AIMessage index (= one "turn")
    # Ordered by first appearance of each parent.
    turn_order: list[int] = []          # AI message indices in order of first appearance
    turn_to_tool_indices: dict[int, list[int]] = {}  # ai_idx -> [tool_msg_indices]

    for i, msg in enumerate(messages):
        if not isinstance(msg, ToolMessage):
            continue
        tool_name = _find_tool_name_for_call(messages, msg.tool_call_id)
        if tool_name == "set_travel_state":
            continue  # handled separately below
        ai_idx = call_id_to_ai_idx.get(msg.tool_call_id, -1)
        if ai_idx not in turn_to_tool_indices:
            turn_to_tool_indices[ai_idx] = []
            turn_order.append(ai_idx)
        turn_to_tool_indices[ai_idx].append(i)

    # Indices that belong to the last `keep_recent` turns — keep in full
    recent_turns = set(turn_order[-keep_recent:]) if turn_order else set()
    keep_full: set[int] = set()
    for ai_idx in recent_turns:
        keep_full.update(turn_to_tool_indices[ai_idx])

    # Collect all ToolMessage indices to check against
    all_tool_indices: set[int] = {
        idx for indices in turn_to_tool_indices.values() for idx in indices
    }

    pruned: list = []
    for i, msg in enumerate(messages):
        if not isinstance(msg, ToolMessage):
            pruned.append(msg)
            continue

        tool_name = _find_tool_name_for_call(messages, msg.tool_call_id)

        if tool_name == "set_travel_state":
            pruned.append(ToolMessage(
                content="[state updated]",
                tool_call_id=msg.tool_call_id,
                name=getattr(msg, "name", None),
            ))
        elif i in all_tool_indices and i not in keep_full:
            content = msg.content if isinstance(msg.content, str) else str(msg.content)
            first_line = content.split("\n")[0][:200]
            replacement = f"[summarised] {first_line}" + (" …" if len(content) > 200 or "\n" in content else "")
            pruned.append(ToolMessage(
                content=replacement,
                tool_call_id=msg.tool_call_id,
                name=getattr(msg, "name", None),
            ))
        else:
            pruned.append(msg)

    return pruned


# ---------------------------------------------------------------------------
# Orchestrate node
# ---------------------------------------------------------------------------

from travel_planner.models import get_main_model

_model = get_main_model()
_tools = [spawn_agent, load_skill, set_travel_state, book_flight, book_hotel]
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
    """Sync session.json with current progress."""
    from datetime import datetime, timezone

    meta = load_session_meta(session_dir)
    conversation = load_conversation(session_dir)

    meta["updated_at"] = datetime.now(timezone.utc).isoformat()
    meta["last_snapshot_id"] = state.get("last_snapshot_id")
    meta["last_snapshot_entry_count"] = state.get("last_snapshot_entry_count")
    meta["last_snapshot_message_count"] = state.get("last_snapshot_message_count")
    meta["conversation_entries"] = len(conversation)
    # Persist structured state to session.json for inspection / resumption
    meta["stage"] = state.get("stage") or 1
    meta["approved_plan"] = state.get("approved_plan")
    meta["approved_flight"] = state.get("approved_flight")
    meta["approved_hotel"] = state.get("approved_hotel")
    meta["rejection_constraints"] = state.get("rejection_constraints") or {}
    meta["booking_refs"] = state.get("booking_refs")

    save_session_meta(session_dir, meta)


async def orchestrate_node(state: dict) -> dict:
    """Main orchestrator node: apply state updates, prune context, call LLM.

    On first invocation (no session_id), creates a new session.
    Before each LLM call:
      1. Extracts any set_travel_state updates from the last tool loop.
      2. Checks context pressure and compacts if needed.
      3. Injects structured state as a <current_state> block.
      4. Prunes old tool results to reduce token usage.
    Persists all messages to conversation.json.
    """
    updates: dict = {}

    # Create session on first invocation
    session_id = state.get("session_id")
    if not session_id:
        session_id = await asyncio.to_thread(create_session)
        updates["session_id"] = session_id

    session_dir = SESSIONS_DIR / session_id

    # Persist incoming messages (user message or tool results)
    await _persist_incoming(session_dir, state.get("messages", []))

    # Apply structured state updates from set_travel_state tool results
    state_field_updates = _extract_state_updates(state.get("messages", []))
    if state_field_updates:
        logger.info("Structured state updated: %s", list(state_field_updates.keys()))
        updates.update(state_field_updates)

    # Merge updates into a working copy for the rest of this turn
    working_state = {**state, **updates}

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
    compact_update = await maybe_compact(working_state, session_dir, force=force_compact)
    if compact_update:
        logger.info("Compaction applied: %s", compact_update)
        compact_update["last_snapshot_message_count"] = len(msgs)
        updates.update(compact_update)
        working_state = {**working_state, **compact_update}

    if force_compact:
        updates["messages"] = [AIMessage(content="Context compacted.")]
        await asyncio.to_thread(_sync_session_file, session_dir, {**working_state, **updates})
        return updates

    # Build messages for the LLM call
    system_prompt = await asyncio.to_thread(_load_system_prompt)
    state_context = _format_state_context(working_state)

    last_snapshot_id = working_state.get("last_snapshot_id")
    if last_snapshot_id:
        snapshot_content = await asyncio.to_thread(load_snapshot, session_dir, last_snapshot_id)
        msg_count = working_state.get("last_snapshot_message_count") or 0
        recent_messages = list(state.get("messages", []))[msg_count:]
        logger.info(
            "Using snapshot #%d + %d recent messages (total state messages: %d)",
            last_snapshot_id, len(recent_messages), len(state.get("messages", [])),
        )
        recent_messages = _prune_tool_results(recent_messages)
        messages = (
            [SystemMessage(content=system_prompt)]
            + [SystemMessage(content=state_context)]
            + [HumanMessage(content=f"## Prior Conversation Summary\n\n{snapshot_content}")]
            + recent_messages
        )
    else:
        all_messages = _prune_tool_results(list(state.get("messages", [])))
        messages = (
            [SystemMessage(content=system_prompt)]
            + [SystemMessage(content=state_context)]
            + all_messages
        )

    # Call orchestrator LLM
    response = await _model_with_tools.ainvoke(
        messages,
        config={"metadata": {"session_id": session_id}},
    )

    # Persist the AI response
    await _persist_response(session_dir, response)

    # Sync session.json
    await asyncio.to_thread(_sync_session_file, session_dir, working_state)

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
