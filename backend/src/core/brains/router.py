"""Brain Router: Selects the appropriate Brain implementation for the context."""
from src.core.brains.base import Brain
from src.core.brains.companion import CompanionBrain
from src.core.brains.crisis import CrisisBrain
from src.core.context.execution import ExecutionContext, ResponseMode
from src.core.llm.base import LLMProvider

class BrainRouter:
    """Routes ExecutionContexts to the appropriate Brain."""
    
    def __init__(self, provider: LLMProvider):
        """Initialize the router with dependencies needed by brains.
        
        Args:
            provider: The LLMProvider used by LLM-backed brains (like CompanionBrain).
        """
        self.companion_brain = CompanionBrain(provider=provider)
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
