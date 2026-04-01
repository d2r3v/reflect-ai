"""Chat routes for testing."""
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


class ChatResponse(BaseModel):
    """Chat response model."""
    reply: str


@router.get("/test", response_model=ChatResponse)
async def chat_test():
    """Simple test route for E2E verification."""
    return {
        "reply": "test response from backend"
    }
