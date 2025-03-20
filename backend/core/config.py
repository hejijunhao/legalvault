# core/config.py

from typing import Any, Dict, List, Optional
from pydantic import AnyHttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from logging import getLogger

logger = getLogger(__name__)

class Settings(BaseSettings):
    # Environment
    ENV: str = "development"  # Options: development, staging, production
    
    # API Settings
    PROJECT_NAME: str = "LegalVault"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    BASE_URL: str = "http://localhost:8000"
    
    # Security Settings
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    ENCRYPTION_KEY: str  # For encrypting sensitive data
    
    # Database Settings
    DATABASE_URL: PostgresDsn
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info) -> Any:
        if isinstance(v, str):
            return v
        
        values = info.data
        if values.get("DATABASE_URL"):
            return values.get("DATABASE_URL")
        
        return None
    
    # Config for Pydantic v2
    model_config = {
        "case_sensitive": True,
        "env_file": ".env",
        "extra": "allow"  # Allow extra fields from env file
    }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Create a global settings instance
settings = get_settings()