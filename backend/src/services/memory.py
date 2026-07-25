"""Memory Engine service (SQLite-backed RAG).

Responsible for:
- Extracting lightweight, human-readable insights from user messages
  (coping strategies, recurring stressors, preferences).
- Persisting them as plain strings in the `memories` table.
- Retrieving the most recent insights to augment the LLM's context.

This is deliberately a lightweight, deterministic keyword extractor rather than
a vector database — it stores strings in SQLite so the whole pipeline can be
demoed instantly with no external services.
"""
import logging
import re
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.memory import Memory

logger = logging.getLogger(__name__)


# Ordered by priority. First category whose trigger matches wins.
# Each trigger is a lowercase substring; the sentence containing it is stored.
_TRIGGERS: List[Tuple[str, List[str]]] = [
    (
        "coping_strategy",
        [
            # present tense
            "helps me", "helps my", "helps with", "really helps", "helps calm",
            "that helps", "what helps", "usually helps", "always helps", "helps a lot",
            # past tense / natural phrasing (the common miss)
            "helped me", "helped my", "has helped", "have helped", "that helped",
            "which helped", "helped a lot", "helped with", "really helped",
            # other coping language
            "makes me feel better", "made me feel better", "calms me", "calms me down",
            "grounds me", "i cope by", "i cope with", "helps me relax", "eases my",
            "soothes me", "clears my head", "clear my head",
        ],
    ),
    (
        "preference",
        [
            "i prefer", "i'd rather", "i would rather", "i like it when",
            "i don't like when", "i dont like when", "please don't", "please dont",
            "i hate when", "i wish you would", "i want you to", "i like when",
        ],
    ),
    (
        "recurring_stressor",
        [
            "always stresses me", "stresses me out", "keeps happening", "every time",
            "i always", "constantly", "keeps me up", "my anxiety", "triggers my",
            "makes me anxious", "overwhelms me", "worried about", "keep worrying",
            # natural "stressed with/about X" phrasing
            "stressed with", "stressed about", "stressed at", "stressed because",
            "stressed over", "stress at work", "work stress",
        ],
    ),
]


class MemoryService:
    """Service for managing user memory and context retrieval."""

    def __init__(self):
        """Initialize memory service."""
        pass

    @staticmethod
    def _coerce_uuid(user_id) -> UUID:
        """Accept either a UUID or its string form (routes pass str(user.id))."""
        return user_id if isinstance(user_id, UUID) else UUID(str(user_id))

    @staticmethod
    def _extract_sentence(text: str, trigger: str) -> str:
        """Return the sentence containing the trigger (original casing), trimmed.
        Falls back to the whole message if splitting doesn't isolate it."""
        sentences = re.split(r"(?<=[.!?\n])\s+", text.strip())
        for s in sentences:
            if trigger in s.lower():
                cleaned = s.strip().strip(".!?").strip()
                if cleaned:
                    return cleaned
        return text.strip()

    def _classify(self, message: str) -> Optional[Tuple[str, str]]:
        """Return (category, extracted_content) if the message expresses a clear
        insight, else None."""
        lowered = message.lower()
        for category, triggers in _TRIGGERS:
            for trig in triggers:
                if trig in lowered:
                    content = self._extract_sentence(message, trig)
                    return category, content[:280]
        return None

    async def extract_memory(
        self,
        db: AsyncSession,
        user_id,
        message_content: str,
        source_message_id=None,
    ) -> Optional[Memory]:
        """Extract a structured insight from a single user message and persist it.

        Adds the new Memory to the session (the caller owns the commit) and
        returns it, or returns None if the message contains no clear insight or
        a near-duplicate is already stored.

        Args:
            db: Active async session (the caller's transaction).
            user_id: The user's id (UUID or str).
            message_content: The raw user message.
            source_message_id: Optional id of the originating message (provenance).

        Returns:
            The created Memory, or None.
        """
        if not message_content or not message_content.strip():
            return None

        classified = self._classify(message_content)
        if classified is None:
            return None

        category, content = classified
        uid = self._coerce_uuid(user_id)

        # Dedup: skip if we've already stored this exact insight for the user.
        existing = await db.execute(
            select(Memory.id).where(
                Memory.user_id == uid,
                func.lower(Memory.content) == content.lower(),
            )
        )
        if existing.first() is not None:
            logger.info(f"Memory already stored for user {uid}; skipping duplicate.")
            return None

        memory = Memory(
            user_id=uid,
            category=category,
            content=content,
            source_message_id=(self._coerce_uuid(source_message_id) if source_message_id else None),
        )
        db.add(memory)
        await db.flush()
        logger.info(f"MEMORY | user={uid} category={category} content={content!r}")
        return memory

    async def retrieve_memories(
        self,
        db: AsyncSession,
        user_id,
        limit: int = 5,
    ) -> List[Memory]:
        """Retrieve the user's most recent insights for context augmentation.

        Args:
            db: Active async session.
            user_id: The user's id (UUID or str).
            limit: Maximum number of insights to return (default 5).

        Returns:
            List of Memory rows, newest first.
        """
        uid = self._coerce_uuid(user_id)
        result = await db.execute(
            select(Memory)
            .where(Memory.user_id == uid)
            .order_by(Memory.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
