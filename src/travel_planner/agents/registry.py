"""Agent registry: loads and caches agent definitions from frontmatter MD files."""

import yaml
from pathlib import Path

_registry: dict | None = None


def load_agent_registry(prompts_dir: str | Path | None = None) -> dict:
    """Load all agent definitions from frontmatter MD files in prompts/agents/.

    Returns dict mapping agent_id to {"frontmatter": dict, "system_prompt": str}.
    Cached after first load.
    """
    global _registry
    if _registry is not None:
        return _registry

    if prompts_dir is None:
        prompts_dir = Path(__file__).parent.parent / "prompts" / "agents"
    else:
        prompts_dir = Path(prompts_dir)

    _registry = {}
    for md_file in prompts_dir.glob("*.md"):
        content = md_file.read_text()
        # Split on --- delimiters (first --- starts frontmatter, second --- ends it)
        parts = content.split("---", 2)
        if len(parts) < 3:
            continue
        frontmatter = yaml.safe_load(parts[1])
        system_prompt = parts[2].strip()
        _registry[frontmatter["id"]] = {
            "frontmatter": frontmatter,
            "system_prompt": system_prompt,
        }
    return _registry


def resolve_tools(tool_names: list[str]) -> list:
    """Map tool name strings to actual LangChain tool objects via TOOL_REGISTRY."""
    from travel_planner.tools import TOOL_REGISTRY

    tools = []
    for name in tool_names:
        if name in TOOL_REGISTRY:
            tools.append(TOOL_REGISTRY[name])
        else:
            raise ValueError(f"Unknown tool: {name}")
    return tools


def get_registry_summary() -> str:
    """Build a text summary of available agents for injection into orchestrator context."""
    registry = load_agent_registry()
    sections = []
    for agent_id, agent_def in registry.items():
        fm = agent_def["frontmatter"]
        sections.append(
            f"### {fm['id']}\n"
            f"Description: {fm['description']}\n"
            f"Required inputs: {fm.get('required_inputs', 'N/A')}\n"
            f"Returns: {fm.get('returns', 'N/A')}\n"
            f"Model: {fm['model']}. Tools: {', '.join(fm['tools'])}. "
            f"Max calls: {fm['max_tool_calls']}. Timeout: {fm['timeout']}."
        )
    return "\n\n".join(sections)
