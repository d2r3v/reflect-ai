"""SafetyEvent ORM model schema."""
from uuid import uuid4
from sqlalchemy import String, ForeignKey, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.base import TimestampedBase

class SafetyEvent(TimestampedBase):
    __tablename__ = "safety_events"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    message_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("messages.id", ondelete="CASCADE"), index=True, nullable=True)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    level: Mapped[str] = mapped_column(String(50), nullable=False)
    response_mode: Mapped[str] = mapped_column(String(50), nullable=False)
    crisis_bypass: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Relationships
    message = relationship("Message", back_populates="safety_events")
    user = relationship("User")
