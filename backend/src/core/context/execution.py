"""ExecutionContext for managing request-scoped state during a turn."""
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class ResponseMode(str, Enum):
    """Determines how the system should respond to the user."""
    REFLECT = "reflect"
    VENT = "vent"
    PLAN = "plan"
    GROUNDING = "grounding"
    CRISIS = "crisis"


class ExecutionContext(BaseModel):
    """
    Manages state for a single request/interaction turn.

    This is the primary data structure that flows through the execution pipeline:
        context → tools → response

    It is built at the start of a turn and passed to the brain/orchestrator.
    """
    session_id: str
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None
    message_content: str = ""

    # Determined by the safety/routing layer before generation
    response_mode: ResponseMode = ResponseMode.REFLECT

    # Populated by memory retrieval (future)
    retrieved_memories: List[Dict[str, Any]] = Field(default_factory=list)

    # Populated by tool execution (future)
    tool_results: List[Dict[str, Any]] = Field(default_factory=list)

    # Arbitrary per-turn metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
