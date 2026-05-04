"""Companion Brain: The core LLM response generation via configured provider."""
import logging
from typing import Dict

from src.core.brains.base import Brain
from src.core.context.execution import ExecutionContext, ResponseMode
from src.core.llm.base import LLMProvider
from src.config import settings

logger = logging.getLogger(__name__)

# Very simple v1 system prompts mapped by ResponseMode
SYSTEM_PROMPTS: Dict[ResponseMode, str] = {
    ResponseMode.REFLECT: (
        "You are a supportive, empathetic companion. Listen carefully to the user's message. "
        "Reflect back their feelings to show you understand, and ask a gentle question to explore further. "
        "Keep your response concise and conversational."
    ),
    ResponseMode.VENT: (
        "You are an active listener holding space for the user to vent. "
        "Validate their emotions strongly. Do NOT offer unprompted advice or trying to fix it immediately. "
        "Keep your response concise and supportive."
    ),
    ResponseMode.PLAN: (
        "You are a structured, goal-oriented companion. The user wants to figure something out or plan. "
        "Help them break their problem into small, manageable steps. Keep your tone encouraging and pragmatic."
    ),
    ResponseMode.GROUNDING: (
        "You are a calm, grounding presence. The user is highly distressed or overwhelmed. "
        "Offer a very brief, simple sensory grounding exercise or breathing technique. "
        "Keep sentences short and direct. Speak slowly and calmly (in text form)."
    ),
}

class CompanionBrain(Brain):
    """Brain that uses an LLMProvider to generate responses tailored to the active response mode."""

    def __init__(self, provider: LLMProvider):
        """Initialize the CompanionBrain.
        
        Args:
            provider: The LLMProvider to use for generating text.
        """
        self.provider = provider
        
    async def generate(self, ctx: ExecutionContext) -> str:
        """Generate an LLM response based on the execution context and mode."""
        # Get the appropriate system prompt, fallback to REFLECT if missing
        system_prompt = SYSTEM_PROMPTS.get(ctx.response_mode, SYSTEM_PROMPTS[ResponseMode.REFLECT])
        
        # Build message payload
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": ctx.message_content}
        ]
        
        logger.info(f"CompanionBrain generating response in {ctx.response_mode} mode")
        
        # Call provider (model name comes from settings, passed here or handled by router setup)
        # We fetch it from settings directly here for simplicity since we don't have a complex orchestrator yet
        try:
            content = await self.provider.complete(
                messages=messages,
                model=settings.openai_model,
                temperature=0.7,
                max_tokens=300
            )
            return content.strip()
        except Exception as e:
            logger.error(f"CompanionBrain generation failed: {e}")
            return "I'm sorry, I'm having trouble thinking of a response right now. I am here for you though."
