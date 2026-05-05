"""Companion Brain: The core LLM response generation via configured provider."""
import logging
from typing import Dict

from src.core.brains.base import Brain
from src.core.context.execution import ExecutionContext, ResponseMode
from src.core.llm.base import LLMProvider
from src.config import settings

logger = logging.getLogger(__name__)

# Base system prompts by response mode
_BASE_PROMPTS: Dict[ResponseMode, str] = {
    ResponseMode.REFLECT: (
        "You are a supportive, empathetic companion. Listen carefully to the user's message. "
        "Reflect back their feelings to show you understand, and ask a gentle question to explore further. "
        "Keep your response concise and conversational."
    ),
    ResponseMode.VENT: (
        "You are an active listener holding space for the user to vent. "
        "Validate their emotions strongly. Do NOT offer unprompted advice or try to fix it immediately. "
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

# Category labels shown in the memory block
_CATEGORY_LABELS: Dict[str, str] = {
    "stressor": "dealing with",
    "coping": "copes by",
    "preference": "preference",
    "goal": "working toward",
    "support_need": "support style",
    "personal_context": "about them",
}


def _build_memory_block(memories: list[dict]) -> str:
    """
    Format retrieved memories as a compact context block appended to the
    system prompt. Empty list returns an empty string (no block added).
    """
    if not memories:
        return ""

    lines = []
    for m in memories:
        label = _CATEGORY_LABELS.get(m.get("category", ""), m.get("category", ""))
        content = m.get("content", "").strip()
        if content:
            lines.append(f"- [{label}] {content}")

    if not lines:
        return ""

    return (
        "\n\nContext from previous conversations with this person:\n"
        + "\n".join(lines)
        + "\n\nUse this context naturally. Do not announce that you remember it. "
        "Let it quietly inform your empathy, your questions, and how you frame things."
    )


class CompanionBrain(Brain):
    """Brain that uses an LLMProvider to generate responses tailored to the active response mode."""

    def __init__(self, provider: LLMProvider):
        self.provider = provider

    async def generate(self, ctx: ExecutionContext) -> str:
        base_prompt = _BASE_PROMPTS.get(ctx.response_mode, _BASE_PROMPTS[ResponseMode.REFLECT])
        memory_block = _build_memory_block(ctx.retrieved_memories)
        system_prompt = base_prompt + memory_block

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": ctx.message_content},
        ]

        logger.info(
            f"CompanionBrain generating | mode={ctx.response_mode.value} "
            f"memories={len(ctx.retrieved_memories)}"
        )

        try:
            content = await self.provider.complete(
                messages=messages,
                model=settings.openai_model,
                temperature=0.7,
                max_tokens=300,
            )
            return content.strip()
        except Exception as e:
            logger.error(f"CompanionBrain generation failed: {e}")
            return "I'm sorry, I'm having trouble thinking of a response right now. I am here for you though."
