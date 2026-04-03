"""request_checkpoint tool — signals the graph to pause for user approval."""

import json
from typing import Optional

from langchain_core.tools import tool

# Shared key used in both this tool and orchestrate_node to identify checkpoint
# payloads.  Defined once here and imported wherever needed.
CHECKPOINT_REQUEST_KEY = "__checkpoint_request__"


@tool
def request_checkpoint(content: str, next_stage: Optional[int] = None) -> str:
    """Signal the graph to pause at a human approval checkpoint.

    Call this tool when you have fully formatted results ready for the user
    to approve. The graph will pause here (via LangGraph interrupt()), present
    the content to the user, and resume when they respond — without making
    another orchestrator LLM call just to ask the question.

    This replaces the pattern of ending your response with "Do you approve?"
    and waiting for the next turn. Using this tool saves one Sonnet call per
    checkpoint by letting the graph handle the pause deterministically.

    When to call:
    - After generating the travel plan (Checkpoint 1): next_stage=2
    - After generating flight + hotel options (Checkpoint 2): next_stage=3
    - Before confirming booking (Checkpoint 3): next_stage=None (booking
      confirmation handled by the booking skill)

    Args:
        content: The fully formatted presentation to show the user.
                 Include all relevant details — this is exactly what the
                 user will see while deciding whether to approve.
        next_stage: Stage to advance to automatically on a simple approval
                    ("yes", "ok", "looks good", etc.).  If None, the
                    orchestrator always handles routing after the response.

    Returns:
        JSON confirmation consumed by orchestrate_node to set pending_checkpoint.
    """
    return json.dumps({
        CHECKPOINT_REQUEST_KEY: True,
        "content": content,
        "next_stage": next_stage,
    })
