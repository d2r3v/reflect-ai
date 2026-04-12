"""Conversation routes for creating and managing chat conversations."""
from uuid import UUID
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from src.db.session import get_db
from src.db.models.user import User
from src.db.models.conversation import Conversation
from src.db.models.message import Message
from src.core.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/conversations", tags=["conversations"])

# ── Pydantic schemas ──

class ConversationCreate(BaseModel):
    title: Optional[str] = None

class MessageCreate(BaseModel):
    content: str

class MessageOut(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationOut(BaseModel):
    id: str
    title: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ConversationDetail(ConversationOut):
    messages: list[MessageOut] = []

# ── Routes ──

@router.post("", response_model=ConversationOut, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    body: ConversationCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new conversation for the authenticated user."""
    conversation = Conversation(
        user_id=user.id,
        title=body.title or "New Conversation",
    )
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    return _serialize_conversation(conversation)


@router.get("", response_model=list[ConversationOut])
async def list_conversations(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all conversations for the authenticated user, newest first."""
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user.id)
        .order_by(Conversation.updated_at.desc())
    )
    conversations = result.scalars().all()
    return [_serialize_conversation(c) for c in conversations]


@router.get("/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single conversation with all its messages, ordered by creation time."""
    conversation = await _get_user_conversation(conversation_id, user, db)

    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at.asc())
    )
    messages = result.scalars().all()

    return {
        **_serialize_conversation(conversation),
        "messages": [_serialize_message(m) for m in messages],
    }


@router.post("/{conversation_id}/messages", response_model=list[MessageOut], status_code=status.HTTP_201_CREATED)
async def send_message(
    conversation_id: str,
    body: MessageCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send a message in a conversation. Stores the user message and returns a mocked assistant reply."""
    conversation = await _get_user_conversation(conversation_id, user, db)

    if not body.content.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Message content cannot be empty")

    # Store user message
    user_msg = Message(
        conversation_id=conversation.id,
        role="user",
        content=body.content.strip(),
    )
    db.add(user_msg)

    # Generate mocked assistant reply
    # TODO: Replace with real LLM orchestration
    assistant_msg = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=f"I hear you. You said: \"{body.content.strip()[:100]}\" — I'm here to support you.",
    )
    db.add(assistant_msg)

    await db.commit()
    await db.refresh(user_msg)
    await db.refresh(assistant_msg)

    return [_serialize_message(user_msg), _serialize_message(assistant_msg)]


# ── Helpers ──

async def _get_user_conversation(conversation_id: str, user: User, db: AsyncSession) -> Conversation:
    """Load a conversation and verify it belongs to the authenticated user."""
    try:
        cid = UUID(conversation_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid conversation ID")

    result = await db.execute(select(Conversation).where(Conversation.id == cid))
    conversation = result.scalars().first()

    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    if str(conversation.user_id) != str(user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return conversation


def _serialize_conversation(c: Conversation) -> dict:
    return {"id": str(c.id), "title": c.title, "created_at": c.created_at, "updated_at": c.updated_at}


def _serialize_message(m: Message) -> dict:
    return {"id": str(m.id), "role": m.role, "content": m.content, "created_at": m.created_at}
