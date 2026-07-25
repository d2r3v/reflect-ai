"""Memory routes: transparency endpoint for insights the AI has stored."""
from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.db.session import get_db
from src.db.models.user import User
from src.db.models.memory import Memory
from src.core.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/memories", tags=["memories"])


class MemoryOut(BaseModel):
    id: str
    category: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("", response_model=list[MemoryOut])
async def list_memories(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return every insight the system has learned about the authenticated user,
    newest first. Powers the Memory Inspector screen."""
    result = await db.execute(
        select(Memory)
        .where(Memory.user_id == user.id)
        .order_by(Memory.created_at.desc())
    )
    memories = result.scalars().all()
    return [
        MemoryOut(
            id=str(m.id),
            category=m.category,
            content=m.content,
            created_at=m.created_at,
        )
        for m in memories
    ]
