# core/config.py

from typing import Any, Dict, List, Optional
from pydantic import field_validator, model_validator, AnyHttpUrl, PostgresDsn
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # API Settings
    PROJECT_NAME: str = "LegalVault"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    BASE_URL: str = "http://localhost:8000"
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
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
    
    # Redis Settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    
    # Rate Limiting
    RATE_LIMIT_DEFAULT: int = 100  # requests per minute
    RATE_LIMIT_PREMIUM: int = 500  # requests per minute
    
    # Integration Settings
    OAUTH_STATE_TOKEN_EXPIRE_MINUTES: int = 10
    DEFAULT_INTEGRATION_TIMEOUT: float = 30.0  # seconds
    
    # Supabase Settings
    SUPABASE_URL: Optional[str] = None
    SUPABASE_ANON_KEY: Optional[str] = None
    SUPABASE_JWT_SECRET: Optional[str] = None
    
    # Email Settings
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # AWS Settings (if needed)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: Optional[str] = None
    S3_BUCKET: Optional[str] = None

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