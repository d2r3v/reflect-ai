"""Brain Router: Selects the appropriate Brain implementation for the context."""
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.brains.base import Brain
from src.core.brains.companion import CompanionBrain
from src.core.brains.crisis import CrisisBrain
from src.core.context.execution import ExecutionContext, ResponseMode
from src.core.llm.base import LLMProvider
from src.services.memory import MemoryService

class BrainRouter:
    """Routes ExecutionContexts to the appropriate Brain."""

    def __init__(
        self,
        provider: LLMProvider,
        memory_service: Optional[MemoryService] = None,
        db: Optional[AsyncSession] = None,
    ):
        """Initialize the router with dependencies needed by brains.

        Args:
            provider: The LLMProvider used by LLM-backed brains (like CompanionBrain).
            memory_service: Optional MemoryService for RAG context retrieval.
            db: Optional async DB session for fetching stored memories.
        """
        self.companion_brain = CompanionBrain(provider=provider, memory_service=memory_service, db=db)
        self.crisis_brain = CrisisBrain()
        
    def route(self, ctx: ExecutionContext) -> Brain:
        """Select the correct Brain instance based on the response mode.
        
        Args:
            ctx: The current execution context determining the route
            
        Returns:
            An instantiated Brain ready to generate a response
        """
        # CRITICAL bypassing: never route to an LLM if in crisis mode
        if ctx.response_mode == ResponseMode.CRISIS:
            return self.crisis_brain
            
        return self.companion_brain
