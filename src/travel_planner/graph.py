"""LangGraph StateGraph definition -- 2-node ReAct loop.

The orchestrator is a standard ReAct agent: an orchestrate node calls
the LLM (which may produce tool calls), and a tool node executes them.
The loop continues until the LLM produces a text response with no tool
calls, at which point the graph ends.  The next user message starts a
new invocation with persisted state.
"""

from langgraph.graph import StateGraph, START, END

from travel_planner.state import TravelPlannerState
from travel_planner.orchestrator.nodes import (
    orchestrate_node,
    should_continue,
    tool_node,
)


def build_graph() -> StateGraph:
    """Build the 2-node orchestrator graph."""
    builder = StateGraph(TravelPlannerState)

    builder.add_node("orchestrate", orchestrate_node)
    builder.add_node("tools", tool_node)

    builder.add_edge(START, "orchestrate")
    builder.add_conditional_edges(
        "orchestrate",
        should_continue,
        {"tools": "tools", END: END},
    )
    builder.add_edge("tools", "orchestrate")

    return builder


graph = build_graph().compile()
