import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings class"""
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://bitebase:bitebase123@db:5432/bitebase")
    DB_MAX_CONNECTIONS: int = 10
    DB_TIMEOUT: int = 30
    
    # Auth settings
    JWT_SECRET: str = os.getenv("JWT_SECRET", "your_jwt_secret_here")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    
    # API settings
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # AI services
    OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://ollama:11434")
    LANGFLOW_URL: str = os.getenv("LANGFLOW_URL", "http://langflow:7860")
    DEFAULT_LLM_MODEL: str = "llama2"
    
    # CORS settings
    CORS_ORIGINS: list = ["*"]
    CORS_METHODS: list = ["*"]
    CORS_HEADERS: list = ["*"]
    
    # Application metadata
    PROJECT_NAME: str = "BiteBase API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "BiteBase Restaurant Management API"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    """Get application settings with caching"""
    return Settings() 