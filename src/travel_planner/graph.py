"""LangGraph StateGraph definition.

Three nodes:
  orchestrate  -- ReAct orchestrator (LLM + tool calls)
  tools        -- ToolNode executing all tool calls
  checkpoint   -- interrupt() node for human approval gates

Normal ReAct flow:  orchestrate -> tools -> orchestrate -> ... -> END
Checkpoint flow:    orchestrate -> tools -> orchestrate (detects request_checkpoint,
                    no LLM call) -> checkpoint -> interrupt() -> orchestrate -> ...
"""

from langgraph.graph import StateGraph, START, END

from travel_planner.state import TravelPlannerState
from travel_planner.orchestrator.nodes import (
    checkpoint_node,
    orchestrate_node,
    should_continue,
    tool_node,
)


def build_graph() -> StateGraph:
    """Build the 3-node orchestrator graph."""
    builder = StateGraph(TravelPlannerState)

    builder.add_node("orchestrate", orchestrate_node)
    builder.add_node("tools", tool_node)
    builder.add_node("checkpoint", checkpoint_node)

    builder.add_edge(START, "orchestrate")
    builder.add_conditional_edges(
        "orchestrate",
        should_continue,
        {"tools": "tools", "checkpoint": "checkpoint", END: END},
    )
    builder.add_edge("tools", "orchestrate")
    # checkpoint_node returns Command(goto="orchestrate") — no explicit edge needed.

    return builder


graph = build_graph().compile()
