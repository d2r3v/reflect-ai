"""Message ORM model."""
from uuid import uuid4
from sqlalchemy import String, ForeignKey, Text, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.base import TimestampedBase

class Message(TimestampedBase):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    conversation_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), index=True, nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    safety_events = relationship("SafetyEvent", back_populates="message", cascade="all, delete-orphan")
