"""Base LLM Provider abstraction."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class LLMProvider(ABC):
    """Abstract base class for all LLM providers (OpenAI, Anthropic, Ollama, etc.)."""
    
    @abstractmethod
    async def complete(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> str:
        """
        Generate a completion given a list of messages.
        
        Args:
            messages: List of message dicts with 'role' and 'content', e.g. [{"role": "user", "content": "hello"}]
            model: The name/ID of the model to use
            temperature: Generation temperature
            max_tokens: Maximum tokens in the response
            
        Returns:
            The raw string content of the response.
        """
        ...
