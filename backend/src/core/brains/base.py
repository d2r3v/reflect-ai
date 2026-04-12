"""Base Brain interface for response generation strategies."""
from abc import ABC, abstractmethod
from src.core.context.execution import ExecutionContext


class Brain(ABC):
    """
    A Brain takes an ExecutionContext (which includes the user message,
    retrieved memories, tool results, and response mode) and produces
    a response string.

    Concrete implementations will wrap LLM calls with mode-specific
    system prompts and post-processing.
    """

    @abstractmethod
    async def generate(self, ctx: ExecutionContext) -> str:
        """Generate a response given the execution context."""
        ...
