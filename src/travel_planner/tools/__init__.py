"""Travel planner tool implementations.

Provides a TOOL_REGISTRY mapping tool names to LangChain BaseTool objects
for use by the orchestrator and sub-agents.
"""

from langchain_core.tools import BaseTool

from travel_planner.tools.booking import book_flight, book_hotel
from travel_planner.tools.budget import budget_calculator
from travel_planner.tools.compare import compare_flights, compare_hotels
from travel_planner.tools.search import (
    destination_lookup,
    search_flights,
    search_hotels,
    web_search,
)

TOOL_REGISTRY: dict[str, BaseTool] = {
    "web_search": web_search,
    "destination_lookup": destination_lookup,
    "search_flights": search_flights,
    "search_hotels": search_hotels,
    "compare_flights": compare_flights,
    "compare_hotels": compare_hotels,
    "book_flight": book_flight,
    "book_hotel": book_hotel,
    "budget_calculator": budget_calculator,
}

__all__ = [
    "TOOL_REGISTRY",
    "web_search",
    "destination_lookup",
    "search_flights",
    "search_hotels",
    "compare_flights",
    "compare_hotels",
    "book_flight",
    "book_hotel",
    "budget_calculator",
]
