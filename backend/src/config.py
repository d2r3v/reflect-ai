"""Configuration management using Pydantic settings."""
from pydantic_settings import BaseSettings


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
    
    # Future: Database
    database_url: str = "postgresql://user:password@localhost/masc_db"
    
    # Future: LLM/API keys
    openai_api_key: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
