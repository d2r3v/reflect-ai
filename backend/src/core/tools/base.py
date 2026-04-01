"""Base Tool interface for AI capabilities."""
from abc import ABC, abstractmethod
from typing import Any, Dict

class Tool(ABC):
    """
    Base class for all tools available to the AI.
    Tools define their inputs, logic, and how they interact with memory or external APIs.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name for the tool."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Detailed description of what the tool does."""
        pass

    @abstractmethod
    async def run(self, **kwargs) -> Any:
        """Execute the tool logic."""
        pass
