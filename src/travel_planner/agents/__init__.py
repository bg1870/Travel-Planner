"""Agent registry and runner for the travel planner.

Provides tools for loading agent definitions from markdown frontmatter,
resolving tool references, and spawning sub-agents.
"""

from travel_planner.agents.registry import load_agent_registry, resolve_tools
from travel_planner.agents.runner import spawn_agent

__all__ = [
    "load_agent_registry",
    "resolve_tools",
    "spawn_agent",
]
