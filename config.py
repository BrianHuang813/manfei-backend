from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional


class Settings(BaseSettings):
    """Application configuration settings."""
    
    # Database
    DATABASE_URL: str
    
    # LINE Login OAuth
    LINE_CHANNEL_ID: str
    LINE_CHANNEL_SECRET: str
    LINE_AUTHORIZE_URL: str = "https://access.line.me/oauth2/v2.1/authorize"
    LINE_TOKEN_URL: str = "https://api.line.me/oauth2/v2.1/token"
    LINE_PROFILE_URL: str = "https://api.line.me/v2/profile"
    
    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Cloudinary
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    # Application URLs
    FRONTEND_URL: str = "http://localhost:5173"
    BACKEND_URL: str = "http://localhost:8000"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        url = str(value).strip()

        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+asyncpg://", 1)

        if url.startswith("postgresql+psycopg2://"):
            return url.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)

        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)

        return url
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
