"""Memory Engine service.

Responsible for:
- Extracting structured memories from user messages (rule-based, deterministic)
- Persisting memories with deduplication (reinforcement counting)
- Retrieving relevant memories via keyword + recency scoring
"""

import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID as _UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.db.models.user_memory import UserMemory

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Stop words — excluded from keyword indexing
# ---------------------------------------------------------------------------
_STOP_WORDS: frozenset[str] = frozenset({
    "i", "me", "my", "myself", "we", "our", "you", "your", "he", "she", "it",
    "they", "them", "their", "what", "which", "who", "this", "that", "these",
    "those", "am", "is", "are", "was", "were", "be", "been", "being", "have",
    "has", "had", "do", "does", "did", "will", "would", "could", "should",
    "may", "might", "shall", "can", "need", "a", "an", "the", "and", "but",
    "or", "nor", "for", "yet", "so", "as", "at", "by", "from", "in", "into",
    "of", "on", "to", "up", "with", "about", "after", "before", "through",
    "just", "very", "really", "also", "not", "no", "its", "too", "than",
    "then", "when", "how", "all", "both", "few", "more", "most", "other",
    "some", "such", "only", "same", "own", "if", "because", "while",
    "although", "though", "since", "again", "here", "there", "where", "why",
    "any", "each", "every", "get", "got", "feel", "felt", "think", "thought",
    "know", "knew", "like", "make", "made", "much", "many", "little", "lot",
    "something", "anything", "nothing", "everything", "someone", "anyone",
    "always", "never", "sometimes", "often", "usually", "already", "still",
    "bit", "now", "day", "days", "time", "today", "going", "thing", "things",
})


# ---------------------------------------------------------------------------
# MemoryFact — intermediate representation before DB persistence
# ---------------------------------------------------------------------------
@dataclass
class MemoryFact:
    """A single extracted memory, ready to be persisted or scored."""
    category: str
    content: str
    keywords: list[str]
    confidence: float
    source_message_id: Optional[str] = None


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
def _cap(m: re.Match, group: int = 1, max_len: int = 100) -> str:
    """Capture a regex group, strip trailing punctuation/spaces, enforce length."""
    text = m.group(group).strip().rstrip(".,!? ").lower()
    return text[:max_len]


def _keywords(text: str) -> list[str]:
    """Tokenise text into significant lowercase words, excluding stop words."""
    tokens = re.findall(r"[a-z]+", text.lower())
    return sorted({t for t in tokens if len(t) >= 3 and t not in _STOP_WORDS})


# ---------------------------------------------------------------------------
# Extraction rules
# Each tuple: (compiled_pattern, content_fn, category, confidence)
# Patterns are case-insensitive. content_fn receives the Match and returns
# the human-readable memory string.
# ---------------------------------------------------------------------------
_RULES: list[tuple[re.Pattern, any, str, float]] = []

_RAW_RULES: list[tuple[str, any, str, float]] = [

    # ── STRESSORS ────────────────────────────────────────────────────────
    # "stressed / overwhelmed / anxious / worried about X"
    (
        r"\b(stressed\s+(?:out\s+)?|overwhelmed\s+|anxious\s+|worried\s+)(?:about|over|by)\s+(.{4,70})",
        lambda m: f"stressed about {_cap(m, 2)}",
        "stressor", 0.85,
    ),
    # "struggling with X"
    (
        r"\bstruggling\s+with\s+(.{4,60})",
        lambda m: f"struggling with {_cap(m)}",
        "stressor", 0.80,
    ),
    # "my [job/work/relationship/etc.] has been [stressful/hard/...]"
    (
        r"\bmy\s+(\w+(?:\s+\w+)?)\s+(?:has been|is|keeps being|was|keeps)\s+"
        r"(?:really\s+|so\s+|very\s+)?(?:stressful|overwhelming|exhausting|difficult|hard|rough)\b",
        lambda m: f"stressed about {_cap(m)}",
        "stressor", 0.75,
    ),
    # "can't stop thinking / worrying about X"
    (
        r"\bcan't\s+stop\s+(?:thinking|worrying)\s+about\s+(.{4,60})",
        lambda m: f"preoccupied with {_cap(m)}",
        "stressor", 0.80,
    ),
    # "been dealing with X" / "been going through X"
    (
        r"\b(?:been\s+)?(?:dealing|going through)\s+(?:a\s+lot\s+with\s+|with\s+)(.{4,60})",
        lambda m: f"dealing with {_cap(m)}",
        "stressor", 0.75,
    ),

    # ── COPING STRATEGIES ────────────────────────────────────────────────
    # "[gerund phrase] helps me" — gerund ensures it's an activity, not a person
    (
        r"\b(\w+ing(?:\s+(?:for\s+)?\w+){0,3})\s+(?:really\s+|always\s+)?helps?\s+me\b",
        lambda m: f"{_cap(m)} helps",
        "coping", 0.80,
    ),
    # "I find [X] calming / helpful / relaxing"
    (
        r"\bI\s+find\s+(.{4,50}?)\s+(?:calming|helpful|relaxing|soothing|grounding|comforting)\b",
        lambda m: f"finds {_cap(m)} calming",
        "coping", 0.85,
    ),
    # "when I [do X], I feel better / calmer"
    (
        r"\bwhen\s+I\s+(.{4,50}?),\s+I\s+(?:feel|get)\s+(?:better|calmer|less anxious|more settled)\b",
        lambda m: f"{_cap(m)} helps feel better",
        "coping", 0.80,
    ),
    # "X works for me" / "X helps me cope"
    (
        r"\b(.{4,40}?)\s+(?:works|helps?)\s+(?:for me|me cope|me deal)\b",
        lambda m: f"{_cap(m)} helps cope",
        "coping", 0.75,
    ),

    # ── PREFERENCES (directed at the assistant) ───────────────────────────
    # "I prefer you to / I'd prefer you just X"
    (
        r"\bI\s+(?:prefer|would prefer|would rather)\s+you\s+(?:to\s+)?(?:just\s+)?(.{4,60})",
        lambda m: f"prefers: {_cap(m)}",
        "preference", 0.85,
    ),
    # "please don't X" / "please just X"
    (
        r"\bplease\s+(?:just\s+)?(?:don't|do not)\s+(.{4,60})",
        lambda m: f"dislikes: {_cap(m)}",
        "preference", 0.80,
    ),
    # "I don't want/like you to X"
    (
        r"\bI\s+don't\s+(?:want|like)\s+you\s+to\s+(.{4,60})",
        lambda m: f"dislikes when you: {_cap(m)}",
        "preference", 0.85,
    ),

    # ── GOALS ────────────────────────────────────────────────────────────
    # "I'm trying / working to X"
    (
        r"\bI(?:'m|\s+am)\s+(?:trying|working)\s+to\s+(.{4,60})",
        lambda m: f"trying to {_cap(m)}",
        "goal", 0.80,
    ),
    # "my goal is to X"
    (
        r"\bmy\s+goal\s+is\s+(?:to\s+)?(.{4,60})",
        lambda m: f"goal: {_cap(m)}",
        "goal", 0.85,
    ),
    # "I really want to X" (stronger signal than plain "I want to")
    (
        r"\bI\s+really\s+want\s+to\s+(.{4,60})",
        lambda m: f"wants to {_cap(m)}",
        "goal", 0.75,
    ),

    # ── SUPPORT NEEDS ─────────────────────────────────────────────────────
    (
        r"\bI\s+(?:just\s+)?(?:need|want)\s+(?:to\s+)?(?:just\s+)?vent\b",
        lambda m: "needs to vent, not be fixed",
        "support_need", 0.90,
    ),
    (
        r"\b(?:not?|don't)\s+(?:looking for|want(?:ing)?|need(?:ing)?)\s+advice\b",
        lambda m: "not looking for advice",
        "support_need", 0.90,
    ),
    (
        r"\bI\s+(?:just\s+)?need\s+someone\s+to\s+listen\b",
        lambda m: "needs someone to listen",
        "support_need", 0.90,
    ),
    (
        r"\bI\s+(?:just\s+)?need\s+(?:some\s+)?(?:help|support|guidance)\s+(?:figuring|planning|deciding)\b",
        lambda m: "wants help planning or deciding",
        "support_need", 0.80,
    ),

    # ── PERSONAL CONTEXT ─────────────────────────────────────────────────
    # "I'm a/an [profession]" — fixed list keeps this conservative
    (
        r"\bI(?:'m|\s+am)\s+a(?:n)?\s+"
        r"(teacher|nurse|doctor|student|engineer|developer|designer|manager|"
        r"therapist|counselor|lawyer|artist|musician|chef|driver|writer|"
        r"social worker|professor|researcher|caregiver|parent)\b",
        lambda m: f"occupation: {_cap(m)}",
        "personal_context", 0.90,
    ),
    # "I work as a/an [X]"
    (
        r"\bI\s+work\s+as\s+a(?:n)?\s+(\w+(?:\s+\w+)?)\b",
        lambda m: f"occupation: {_cap(m)}",
        "personal_context", 0.90,
    ),
    # "I have [N] kids / children"
    (
        r"\bI\s+(?:have|'ve got)\s+(\w+)\s+(?:kids?|children|daughters?|sons?)\b",
        lambda m: f"has {_cap(m)} kids",
        "personal_context", 0.85,
    ),
    # "I live alone / with my partner / with my family"
    (
        r"\bI\s+live\s+(alone|with\s+my\s+partner|with\s+my\s+family|with\s+roommates?|by\s+myself)\b",
        lambda m: f"lives {_cap(m)}",
        "personal_context", 0.85,
    ),
]

# Compile all patterns once at import time
for _raw_pat, _fn, _cat, _conf in _RAW_RULES:
    _RULES.append((re.compile(_raw_pat, re.IGNORECASE), _fn, _cat, _conf))

# Minimum confidence required to keep a fact
_MIN_CONFIDENCE: float = 0.70

# Keyword overlap ratio needed to consider two memories duplicates
_DEDUP_THRESHOLD: float = 0.50

# Retrieval scoring weights
_W_KEYWORD = 2.0
_W_RECENCY = 1.0
_W_REINFORCEMENT = 0.5


# ---------------------------------------------------------------------------
# MemoryService
# ---------------------------------------------------------------------------
class MemoryService:
    """Deterministic memory extraction and retrieval service."""

    # ── Extraction ──────────────────────────────────────────────────────

    def extract_from_message(
        self,
        content: str,
        source_message_id: Optional[str] = None,
    ) -> list[MemoryFact]:
        """
        Apply extraction rules to a single user message.

        Returns a list of MemoryFacts (not yet persisted). Each fact has
        content, category, keywords, and confidence. Facts below
        _MIN_CONFIDENCE are discarded.

        Never call this for CRISIS-mode messages — callers are responsible
        for that guard.
        """
        facts: list[MemoryFact] = []
        seen_contents: set[str] = set()  # within-message dedup

        for pattern, content_fn, category, confidence in _RULES:
            match = pattern.search(content)
            if not match:
                continue
            if confidence < _MIN_CONFIDENCE:
                continue

            try:
                fact_content = content_fn(match).strip()
            except Exception:
                continue

            if not fact_content or fact_content in seen_contents:
                continue
            seen_contents.add(fact_content)

            kw = _keywords(fact_content)
            facts.append(
                MemoryFact(
                    category=category,
                    content=fact_content,
                    keywords=kw,
                    confidence=confidence,
                    source_message_id=source_message_id,
                )
            )

        return facts

    # ── Persistence ─────────────────────────────────────────────────────

    async def persist_memories(
        self,
        user_id: str,
        facts: list[MemoryFact],
        db: AsyncSession,
    ) -> None:
        """
        Persist a list of MemoryFacts for a user, with deduplication.

        If an existing active memory in the same category shares >= 50%
        keyword overlap with the new fact, we reinforce (increment counter +
        update timestamp) instead of inserting a duplicate.
        """
        if not facts:
            return

        # Load all active memories for this user in one query
        result = await db.execute(
            select(UserMemory).where(
                UserMemory.user_id == _UUID(user_id),
                UserMemory.is_active.is_(True),
            )
        )
        existing: list[UserMemory] = list(result.scalars().all())

        now = datetime.now(timezone.utc)

        for fact in facts:
            duplicate = self._find_duplicate(fact, existing)
            if duplicate:
                duplicate.times_reinforced += 1
                duplicate.last_reinforced_at = now
                logger.debug(
                    f"MEMORY reinforce | user={user_id} cat={fact.category} "
                    f"content='{fact.content}' x{duplicate.times_reinforced}"
                )
            else:
                memory = UserMemory(
                    user_id=_UUID(user_id),
                    category=fact.category,
                    content=fact.content,
                    keywords=json.dumps(fact.keywords),
                    source_message_id=_UUID(fact.source_message_id) if fact.source_message_id else None,
                    times_reinforced=1,
                    last_reinforced_at=now,
                    is_active=True,
                )
                db.add(memory)
                existing.append(memory)  # keep local list in sync for within-batch dedup
                logger.info(
                    f"MEMORY new | user={user_id} cat={fact.category} "
                    f"content='{fact.content}'"
                )

    def _find_duplicate(
        self, fact: MemoryFact, existing: list[UserMemory]
    ) -> Optional[UserMemory]:
        """Return the first existing memory that duplicates this fact, or None."""
        new_kw = set(fact.keywords)
        if not new_kw:
            return None

        for mem in existing:
            if mem.category != fact.category:
                continue
            try:
                existing_kw = set(json.loads(mem.keywords))
            except (json.JSONDecodeError, TypeError):
                existing_kw = set()

            if not existing_kw:
                continue

            overlap = len(new_kw & existing_kw) / min(len(new_kw), len(existing_kw))
            if overlap >= _DEDUP_THRESHOLD:
                return mem

        return None

    # ── Retrieval ───────────────────────────────────────────────────────

    async def retrieve_memories(
        self,
        user_id: str,
        query: str,
        db: AsyncSession,
        limit: int = 5,
    ) -> list[dict]:
        """
        Return the most relevant active memories for a user given the current
        message, as a list of dicts ready for injection into ExecutionContext.

        Scoring (higher = more relevant):
          keyword_overlap × 2.0   — semantic relevance to this message
          recency_score  × 1.0   — (1 - days_old/30), capped at [0, 1]
          reinforcement  × 0.5   — min(times_reinforced/5, 1.0)

        All scored memories are returned ranked; no minimum threshold so that
        fresh users with few memories always get their best context.
        """
        result = await db.execute(
            select(UserMemory).where(
                UserMemory.user_id == _UUID(user_id),
                UserMemory.is_active.is_(True),
            )
        )
        memories: list[UserMemory] = list(result.scalars().all())

        if not memories:
            return []

        query_words = set(_keywords(query))
        now = datetime.now(timezone.utc)
        scored: list[tuple[float, UserMemory]] = []

        for mem in memories:
            score = self._score(mem, query_words, now)
            scored.append((score, mem))

        scored.sort(key=lambda x: x[0], reverse=True)

        return [
            {"category": mem.category, "content": mem.content}
            for _, mem in scored[:limit]
        ]

    def _score(
        self,
        mem: UserMemory,
        query_words: set[str],
        now: datetime,
    ) -> float:
        try:
            mem_kw = set(json.loads(mem.keywords))
        except (json.JSONDecodeError, TypeError):
            mem_kw = set()

        keyword_score = len(mem_kw & query_words) * _W_KEYWORD

        reinforced_at = mem.last_reinforced_at
        if reinforced_at.tzinfo is None:
            reinforced_at = reinforced_at.replace(tzinfo=timezone.utc)
        days_old = max(0.0, (now - reinforced_at).total_seconds() / 86400)
        recency_score = max(0.0, 1.0 - (days_old / 30.0)) * _W_RECENCY

        reinforcement_score = min(mem.times_reinforced / 5.0, 1.0) * _W_REINFORCEMENT

        return keyword_score + recency_score + reinforcement_score

    # ── Legacy stubs (kept for API compatibility) ─────────────────────────

    async def extract_memory(self, conversation_text: str) -> dict:
        """Deprecated — use extract_from_message() instead."""
        facts = self.extract_from_message(conversation_text)
        return {"facts": [{"category": f.category, "content": f.content} for f in facts]}
