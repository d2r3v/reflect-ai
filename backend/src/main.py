"""FastAPI application entrypoint."""
from src.server.app import create_app
from src.logging_config import logger
from src.config import settings

app = create_app()

@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info(f"Server starting in {settings.environment} mode")

@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Server shutting down")
