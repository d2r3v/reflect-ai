"""Anthropic implementation of the LLMProvider."""
from typing import List, Dict
import logging

from anthropic import AsyncAnthropic

from src.core.llm.base import LLMProvider

logger = logging.getLogger(__name__)


class AnthropicProvider(LLMProvider):
    """LLM provider wrapper around the official anthropic Python SDK."""

    def __init__(self, api_key: str, default_model: str = "claude-sonnet-5"):
        """Initialize the Anthropic provider.

        Args:
            api_key: The API key for authentication.
            default_model: Default model string if no model is provided.
        """
        self.api_key = api_key
        self.default_model = default_model

        if not api_key:
            logger.warning("AnthropicProvider initialized without an API key. Requests will fail.")

        self.client = AsyncAnthropic(api_key=api_key)

    async def complete(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> str:
        """Call the Anthropic Messages API.

        The shared LLMProvider interface passes a `system`-role message inside
        `messages`, but the Anthropic API takes the system prompt as a top-level
        parameter, so we split it out here. `temperature` is accepted for
        interface compatibility but not forwarded: current Opus-tier models
        reject sampling parameters (400), and a supportive chat reply doesn't
        need them.
        """
        system_parts = [m["content"] for m in messages if m.get("role") == "system"]
        turn_messages = [
            {"role": m["role"], "content": m["content"]}
            for m in messages
            if m.get("role") in ("user", "assistant")
        ]
        system_prompt = "\n\n".join(system_parts)

        try:
            response = await self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=turn_messages,
                # Keep chat replies fast: Sonnet 5 runs adaptive thinking by
                # default when `thinking` is omitted, which adds latency and
                # spends the max_tokens budget on reasoning. A supportive reply
                # doesn't need it, so disable it explicitly.
                thinking={"type": "disabled"},
            )
            return "".join(block.text for block in response.content if block.type == "text")
        except Exception as e:
            logger.error(f"Anthropic complete failed: {e}")
            raise
