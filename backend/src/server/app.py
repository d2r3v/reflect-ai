"""FastAPI application factory."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings
from src.logging_config import logger
from src.routes import health, chat, auth, conversations, memory

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="AI support app with structured memory and safety routing",
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # TODO: Restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Routes
    app.include_router(health.router)
    app.include_router(chat.router)
    app.include_router(auth.router)
    app.include_router(conversations.router)
    app.include_router(memory.router)
    
    logger.info(f"FastAPI app initialized: {settings.app_name} v{settings.app_version}")
    
    return app
