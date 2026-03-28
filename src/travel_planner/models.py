"""Model factory: creates LangChain chat models from provider:model strings.

Reads two environment variables:
  - MAIN_MODEL: used by the orchestrator (default: anthropic:claude-sonnet-4-6)
  - SUB_MODEL:  used by sub-agents and utility calls (default: anthropic:claude-haiku-4-5)

Format: "provider:model_name" where provider is "anthropic" or "openai".
"""

import os

from langchain_core.language_models.chat_models import BaseChatModel

MAIN_MODEL_DEFAULT = "anthropic:claude-sonnet-4-6"
SUB_MODEL_DEFAULT = "anthropic:claude-haiku-4-5"


def _parse_model_string(model_string: str) -> tuple[str, str]:
    """Parse 'provider:model_name' into (provider, model_name)."""
    if ":" not in model_string:
        raise ValueError(
            f"Invalid model string '{model_string}'. Expected format: 'provider:model_name'"
        )
    provider, model_name = model_string.split(":", 1)
    provider = provider.strip().lower()
    if provider not in ("anthropic", "openai"):
        raise ValueError(f"Unsupported provider '{provider}'. Use 'anthropic' or 'openai'.")
    return provider, model_name.strip()


def create_model(model_string: str, **kwargs) -> BaseChatModel:
    """Create a LangChain chat model from a provider:model string."""
    provider, model_name = _parse_model_string(model_string)

    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model=model_name, **kwargs)
    else:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=model_name, **kwargs)


def get_main_model(**kwargs) -> BaseChatModel:
    """Get the main orchestrator model from MAIN_MODEL env var."""
    model_string = os.environ.get("MAIN_MODEL", MAIN_MODEL_DEFAULT)
    return create_model(model_string, **kwargs)


def get_sub_model(**kwargs) -> BaseChatModel:
    """Get the sub-agent model from SUB_MODEL env var."""
    model_string = os.environ.get("SUB_MODEL", SUB_MODEL_DEFAULT)
    return create_model(model_string, **kwargs)
