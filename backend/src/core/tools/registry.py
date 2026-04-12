"""Tool registry: discovers and manages available tools."""
from typing import Dict, Optional
from src.core.tools.base import Tool


class ToolRegistry:
    """
    Central registry of all available tools.

    Tools register themselves here. The orchestrator queries
    the registry to determine which tools to offer the LLM.
    """

    def __init__(self) -> None:
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """Register a tool instance by its name."""
        self._tools[tool.name] = tool

    def get(self, name: str) -> Optional[Tool]:
        """Look up a tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> list[Tool]:
        """Return all registered tools."""
        return list(self._tools.values())

    def describe_all(self) -> list[dict]:
        """Return name + description for each tool (for LLM prompt injection)."""
        return [
            {"name": t.name, "description": t.description}
            for t in self._tools.values()
        ]
