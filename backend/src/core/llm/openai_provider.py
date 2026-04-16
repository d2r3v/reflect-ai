"""OpenAI implementation of the LLMProvider."""
from typing import List, Dict, Any
from openai import AsyncOpenAI
import logging

from src.core.llm.base import LLMProvider

logger = logging.getLogger(__name__)

class OpenAIProvider(LLMProvider):
    """LLM provider wrapper around the official openai Python SDK."""

    def __init__(self, api_key: str, default_model: str = "gpt-4o-mini"):
        """Initialize the OpenAI provider.
        
        Args:
            api_key: The API key for authentication.
            default_model: Default model string if no model is provided (informational).
        """
        self.api_key = api_key
        self.default_model = default_model
        
        if not api_key:
            logger.warning("OpenAIProvider initialized without an API key. Requests will fail unless using a local proxy.")
            
        self.client = AsyncOpenAI(api_key=api_key)

    async def complete(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> str:
        """Call the OpenAI Chat Completions API."""
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"OpenAI complete failed: {e}")
            raise
