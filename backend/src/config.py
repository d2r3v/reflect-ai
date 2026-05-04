"""Configuration management using Pydantic settings."""
from pathlib import Path
from pydantic_settings import BaseSettings

_BACKEND_DIR = Path(__file__).resolve().parent.parent  # /backend
_DEFAULT_DB = f"sqlite+aiosqlite:///{_BACKEND_DIR / 'masc.db'}"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    app_name: str = "Memory-Aware Support Companion"
    app_version: str = "0.1.0"
    environment: str = "development"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True
    
    # Logging
    log_level: str = "INFO"
    
    # Auth
    jwt_secret: str = "changeme"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Safety
    post_crisis_required_low_streak: int = 3
    post_crisis_min_duration_seconds: int = 300
    
    # Database
    database_url: str = _DEFAULT_DB
    
    # Future: LLM/API keys
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

