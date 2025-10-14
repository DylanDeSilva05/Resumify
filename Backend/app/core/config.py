"""
Application configuration management
"""
from pydantic_settings import BaseSettings
from pydantic import validator
from typing import List, Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    # Project Info
    PROJECT_NAME: str = "Resumify API"
    DESCRIPTION: str = "AI-Powered HR Recruitment Platform"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql://username:password@localhost:5432/resumify_db"
    TEST_DATABASE_URL: str = "postgresql://username:password@localhost:5432/resumify_test_db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT - These should be set in environment variables
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # Shorter for security
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Security Settings
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 30
    REQUIRE_STRONG_PASSWORDS: bool = True

    # File Upload
    UPLOAD_FOLDER: str = "./uploads"
    MAX_FILE_SIZE: int = 10485760  # 10MB
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "doc", "docx"]

    # AI/ML
    OPENAI_API_KEY: Optional[str] = None
    SPACY_MODEL: str = "en_core_web_md"

    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    # Encryption
    ENCRYPTION_KEY: Optional[str] = None

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
    ]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()

# Ensure upload directory exists
Path(settings.UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)