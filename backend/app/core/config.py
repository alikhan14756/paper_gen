import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "ExamForge AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database - Default to canonical absolute path for SQLite to prevent path drift across cwd
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'examforge.db'}"
    
    # Security & Auth
    SECRET_KEY: str = "examforge-super-secret-key-change-in-production-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # AI Providers
    GEMINI_API_KEY: str = ""
    DEFAULT_AI_PROVIDER: str = "gemini"
    DEFAULT_AI_MODEL: str = "gemini-2.5-flash"
    
    # Storage
    STORAGE_DIR: str = str(BASE_DIR / "storage")
    UPLOAD_DIR: str = str(BASE_DIR / "storage" / "uploads")
    EXPORT_DIR: str = str(BASE_DIR / "storage" / "exports")
    MAX_UPLOAD_SIZE_MB: int = 50
    
    # CORS - Include localhost, production domains, and GitHub Pages
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:5000",
        "http://127.0.0.1:5000",
        "https://alikhan14756.github.io",
        "https://aivanolabs.site",
        "http://aivanolabs.site",
    ]

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
