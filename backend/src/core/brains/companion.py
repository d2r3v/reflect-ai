"""Companion Brain: The core LLM response generation via configured provider."""
import logging
from typing import Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.brains.base import Brain
from src.core.context.execution import ExecutionContext, ResponseMode
from src.core.llm.base import LLMProvider
from src.services.memory import MemoryService

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

    def __init__(
        self,
        provider: LLMProvider,
        memory_service: Optional[MemoryService] = None,
        db: Optional[AsyncSession] = None,
    ):
        """Initialize the CompanionBrain.

        Args:
            provider: The LLMProvider to use for generating text.
            memory_service: Optional MemoryService for RAG context retrieval.
            db: Optional async DB session used to fetch stored memories.

        If either `memory_service` or `db` is omitted, memory augmentation is
        skipped gracefully and the brain behaves as a plain companion.
        """
        self.provider = provider
        self.memory_service = memory_service
        self.db = db

    async def _build_memory_block(self, ctx: ExecutionContext) -> str:
        """Retrieve the user's stored insights and format them for the system
        prompt. Returns an empty string when unavailable or none are stored."""
        if self.memory_service is None or self.db is None or not ctx.user_id:
            return ""
        try:
            memories = await self.memory_service.retrieve_memories(self.db, ctx.user_id, limit=5)
        except Exception as e:  # never let memory failures break a reply
            logger.warning(f"Memory retrieval failed, continuing without it: {e}")
            return ""
        if not memories:
            return ""

        lines = "\n".join(f"- ({m.category}) {m.content}" for m in memories)
        logger.info(f"CompanionBrain injected {len(memories)} memories for user {ctx.user_id}")
        return (
            "\n\nWHAT YOU REMEMBER ABOUT THIS USER (from past conversations):\n"
            f"{lines}\n"
            "If any of the above is relevant to the user's current message, reference it "
            "naturally and specifically — for example, gently remind them of a coping "
            "strategy that has helped them before, or acknowledge a recurring stressor. "
            "Do not force it if none of it is relevant."
        )

    async def generate(self, ctx: ExecutionContext) -> str:
        """Generate an LLM response based on the execution context and mode."""
        # Get the appropriate system prompt, fallback to REFLECT if missing
        base_prompt = SYSTEM_PROMPTS.get(ctx.response_mode, SYSTEM_PROMPTS[ResponseMode.REFLECT])

        # Augment with retrieved long-term memories (RAG)
        system_prompt = base_prompt + await self._build_memory_block(ctx)

        # Build message payload
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": ctx.message_content}
        ]

        logger.info(f"CompanionBrain generating response in {ctx.response_mode} mode")
        
        # The model comes from the active provider, so the brain stays agnostic
        # to which LLM backend (OpenAI, Anthropic, ...) is configured.
        try:
            content = await self.provider.complete(
                messages=messages,
                model=self.provider.default_model,
                temperature=0.7,
                max_tokens=300
            )
            return content.strip()
        except Exception as e:
            logger.error(f"CompanionBrain generation failed: {e}")
            return "I'm sorry, I'm having trouble thinking of a response right now. I am here for you though."
