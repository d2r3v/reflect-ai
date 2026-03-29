"""FastAPI application entrypoint."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings
from src.logging_config import logger
from src.routes import health


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
    
    logger.info(f"FastAPI app initialized: {settings.app_name} v{settings.app_version}")
    
    return app


app = create_app()


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info(f"Server starting in {settings.environment} mode")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Server shutting down")
