"""Mock data loader for the travel planner.

Provides functions to load static JSON datasets used by sub-agent tools
during development and testing. Each loader reads its JSON file once and
caches the result in a module-level dict to avoid repeated disk reads.
"""

import json
from pathlib import Path

_DATA_DIR = Path(__file__).parent
_cache: dict[str, dict] = {}


def _load(filename: str) -> dict:
    """Load a JSON file from the mock_data directory, with caching."""
    if filename not in _cache:
        with open(_DATA_DIR / filename, "r", encoding="utf-8") as f:
            _cache[filename] = json.load(f)
    return _cache[filename]


def load_destinations() -> dict:
    """Load destination profiles (Paris, Tokyo, New York, Bali, Istanbul)."""
    return _load("destinations.json")


def load_flights() -> dict:
    """Load flight listings for routes from Cairo."""
    return _load("flights.json")


def load_hotels() -> dict:
    """Load hotel listings for all destinations."""
    return _load("hotels.json")


def load_web_results() -> dict:
    """Load pre-canned web search result snippets."""
    return _load("web_results.json")


def load_budget_reference() -> dict:
    """Load budget reference data with daily costs and split ratios."""
    return _load("budget_reference.json")
