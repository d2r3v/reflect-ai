"""UserMemory ORM model — stores durable per-user facts extracted from conversations."""
from uuid import uuid4
from datetime import datetime
from sqlalchemy import String, ForeignKey, Text, UUID, Integer, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.base import TimestampedBase


class UserMemory(TimestampedBase):
    __tablename__ = "user_memories"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    # stressor | coping | preference | goal | support_need | personal_context
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    # Human-readable memory string, e.g. "stressed about work pressure"
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # JSON array of significant words used for keyword-based retrieval scoring
    keywords: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    # Nullable traceability link — not cascade-deleted if message is removed
    source_message_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("messages.id", ondelete="SET NULL"),
        nullable=True,
    )
    # Incremented each time the same fact is re-observed (deduplication)
    times_reinforced: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    last_reinforced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    # Soft delete — allows future "forget this" feature without losing audit trail
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    user = relationship("User")
