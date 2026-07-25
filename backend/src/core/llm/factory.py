"""Factory for constructing the configured LLMProvider."""
import logging

from src.config import settings
from src.core.llm.base import LLMProvider
from src.core.llm.openai_provider import OpenAIProvider
from src.core.llm.anthropic_provider import AnthropicProvider

logger = logging.getLogger(__name__)


def create_llm_provider() -> LLMProvider:
    """Instantiate the LLMProvider selected by settings.llm_provider.

    Each provider carries its own `default_model`, so callers (and brains) stay
    agnostic to which provider is active.
    """
    provider = settings.llm_provider.lower()

    if provider == "anthropic":
        return AnthropicProvider(
            api_key=settings.anthropic_api_key,
            default_model=settings.anthropic_model,
        )
    if provider == "openai":
        return OpenAIProvider(
            api_key=settings.openai_api_key,
            default_model=settings.openai_model,
        )

    logger.warning(f"Unknown llm_provider '{settings.llm_provider}', defaulting to Anthropic.")
    return AnthropicProvider(
        api_key=settings.anthropic_api_key,
        default_model=settings.anthropic_model,
    )
