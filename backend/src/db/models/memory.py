"""Memory ORM model.

Stores lightweight, human-readable insights the system has learned about a
user (coping strategies, recurring stressors, preferences). This is the
persistence layer for the SQLite-based RAG memory pipeline — intentionally
plain string storage, no vector database.
"""
from uuid import uuid4
from sqlalchemy import String, Text, ForeignKey, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.base import TimestampedBase


class Memory(TimestampedBase):
    __tablename__ = "memories"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    # One of: coping_strategy | recurring_stressor | preference
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # Provenance: the message this insight was extracted from (no FK — provenance only).
    source_message_id: Mapped[str] = mapped_column(UUID(as_uuid=True), nullable=True)

    # Relationships
    user = relationship("User")
