"""Skill loader tool -- returns specialized prompts on demand."""

from pathlib import Path

from langchain_core.tools import tool

_SKILLS_DIR = Path(__file__).parent.parent / "prompts" / "skills"

_AVAILABLE_SKILLS = {
    "booking": "Handle flight and hotel bookings directly (use after user confirms the itinerary)",
}


@tool
def load_skill(skill_name: str) -> str:
    """Load a specialized skill prompt to gain new capabilities.

    Available skills:
    - booking: Handle flight and hotel bookings directly (use after user confirms the itinerary)

    Args:
        skill_name: The name of the skill to load.

    Returns:
        The skill prompt with instructions and tool usage guidance.
    """
    if skill_name not in _AVAILABLE_SKILLS:
        available = ", ".join(f"{k}: {v}" for k, v in _AVAILABLE_SKILLS.items())
        return f"Error: Unknown skill '{skill_name}'. Available skills: {available}"

    skill_path = _SKILLS_DIR / f"{skill_name}.md"
    if not skill_path.exists():
        return f"Error: Skill file not found for '{skill_name}'"

    return skill_path.read_text()
