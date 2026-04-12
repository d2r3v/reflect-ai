"""Base Tool interface and call/result types for AI capabilities."""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


# ── Data types for tool invocations ──

class ToolCall(BaseModel):
    """A request to invoke a tool, typically produced by the LLM."""
    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)


class ToolResult(BaseModel):
    """The outcome of a single tool invocation."""
    tool_name: str
    success: bool = True
    output: Any = None
    error: Optional[str] = None


# ── Abstract base ──

class Tool(ABC):
    """
    Base class for all tools available to the AI.

    Each tool must declare its name, description, and a `run` method.
    The orchestrator will discover registered tools and make them
    available to the LLM as callable functions.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for the tool."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable explanation of what the tool does."""
        ...

    @abstractmethod
    async def run(self, **kwargs: Any) -> ToolResult:
        """Execute the tool and return a structured result."""
        ...
