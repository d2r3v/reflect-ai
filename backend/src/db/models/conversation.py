"""Conversation ORM model."""
from uuid import uuid4
from datetime import datetime
from sqlalchemy import String, ForeignKey, UUID, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.base import TimestampedBase

class Conversation(TimestampedBase):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=True)
    
    # Safety State
    safety_state: Mapped[str] = mapped_column(String(20), nullable=False, default="normal")
    crisis_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    post_crisis_low_streak: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
