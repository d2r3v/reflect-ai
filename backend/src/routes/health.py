"""Health check routes."""
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/health", tags=["health"])


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    version: str


@router.get("", response_model=HealthResponse)
async def health_check():
    """Check application health and readiness."""
    from src.config import settings
    return {
        "status": "healthy",
        "version": settings.app_version,
    }
