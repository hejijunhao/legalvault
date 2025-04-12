# core/config.py

from typing import Any, Optional
from pydantic import AnyHttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from logging import getLogger
from dotenv import load_dotenv

logger = getLogger(__name__)
load_dotenv()

class Settings(BaseSettings):
    # Constants
    PROJECT_NAME: str = "LegalVault"
    VERSION: str = "1.0.0"  # Could come from CI/CD later
    API_V1_STR: str = "/api/v1"

    # Dynamic Settings
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000")
    BACKEND_CORS_ORIGINS: str = os.getenv("BACKEND_CORS_ORIGINS", "http://localhost:3000")

    # Security (Required)
    # SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    # ENCRYPTION_KEY: str
    SUPABASE_JWT_SECRET: Optional[str] = None

    # Supabase
    SUPABASE_URL: Optional[str] = None
    SUPABASE_ANON_KEY: Optional[str] = None
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None

    # LLM
    OPENAI_API_KEY: str
    PERPLEXITY_API_KEY: Optional[str] = None
    HUGGINGFACE_API_TOKEN: Optional[str] = None

    # Database
    DATABASE_URL: Optional[PostgresDsn] = os.getenv("DATABASE_URL", os.getenv("DATABASE_URL_SESSION"))
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @field_validator("SECRET_KEY", "ENCRYPTION_KEY", "OPENAI_API_KEY", "DATABASE_URL")
    @classmethod
    def validate_required(cls, v: Optional[str], info) -> str:
        if not v:
            raise ValueError(f"{info.field_name} must be set in environment variables")
        return v

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info) -> Any:
        if isinstance(v, str):
            return v
        return info.data.get("DATABASE_URL")

    model_config = {
        "case_sensitive": True,
        "env_file": ".env",
        "extra": "allow"
    }

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()