"""Agent runner: spawns sub-agents with their own tools and model."""

import asyncio

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent

from travel_planner.agents.registry import load_agent_registry, resolve_tools


@tool
async def spawn_agent(agent_id: str, prompt: str) -> str:
    """Spawn a sub-agent by ID with a task prompt.

    The agent runs autonomously with its own tools and model,
    then returns a plain text response.
    The prompt parameter is the only information the sub-agent receives.

    Args:
        agent_id: The agent to spawn (trip_advisor, flight_agent, hotel_agent)
        prompt: Task description with all relevant context for the sub-agent
    """
    registry = await asyncio.to_thread(load_agent_registry)

    if agent_id not in registry:
        return f"Error: Unknown agent '{agent_id}'"

    agent_def = registry[agent_id]
    fm = agent_def["frontmatter"]

    # Resolve tools (may import modules, run in thread to avoid blocking)
    agent_tools = await asyncio.to_thread(resolve_tools, fm["tools"])

    # Create sub-agent (no structured output — plain text response)
    # Graph compilation is sync — run in thread to avoid blocking the event loop.
    def _build_agent():
        from travel_planner.models import create_model
        model = create_model(fm["model"])
        return create_react_agent(
            model=model,
            tools=agent_tools,
            prompt=agent_def["system_prompt"],
        )

    sub_agent = await asyncio.to_thread(_build_agent)

    # Parse timeout from frontmatter (e.g., "15s" -> 15)
    timeout_str = fm.get("timeout", "15s")
    timeout_seconds = int(timeout_str.replace("s", ""))

    # Invoke with timeout
    try:
        result = await asyncio.wait_for(
            sub_agent.ainvoke({"messages": [HumanMessage(content=prompt)]}),
            timeout=timeout_seconds,
        )
    except asyncio.TimeoutError:
        return f"Error: Agent {agent_id} timed out after {timeout_seconds}s"
    except Exception as e:
        return f"Error: Agent {agent_id} failed: {str(e)}"

    # Extract the agent's final message as plain text
    final_messages = result.get("messages", [])
    for msg in reversed(final_messages):
        if hasattr(msg, "content") and msg.content:
            return msg.content

    return "Error: Agent did not produce a response"
