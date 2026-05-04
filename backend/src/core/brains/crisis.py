"""Crisis Brain: Deterministic, non-LLM safety net for critical situations."""
import logging

from src.core.brains.base import Brain
from src.core.context.execution import ExecutionContext

logger = logging.getLogger(__name__)

class CrisisBrain(Brain):
    """Brain that immediately bypasses LLM generation to return deterministic crisis resources."""
    
    async def generate(self, ctx: ExecutionContext) -> str:
        """Return a hardcoded crisis response."""
        logger.warning(f"CrisisBrain activated for user {ctx.user_id}")
        
        # This matches the content previously mocked in SafetyService
        return (
            "I'm really glad you said something. You matter, and I'm concerned about your safety.\n\n"
            "Please call or text 988 right now to connect with people who can support you. "
            "You can also text HOME to 741741 to connect with the Crisis Text Line.\n\n"
            "I can stay with you here, but I'm not a substitute for immediate professional support."
        )
