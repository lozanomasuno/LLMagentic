"""Base application settings using Pydantic v2."""

import os
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "Health Coverage AI"
    APP_VERSION: str = "1.0.0"
    ENV: Literal["development", "testing", "production"] = "development"
    DEBUG: bool = False

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    CORS_ORIGINS: list[str] = ["http://localhost:4200"]

    # PostgreSQL
    POSTGRES_USER: str = "health_user"
    POSTGRES_PASSWORD: str = "change_me"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "health_coverage"

    # ChromaDB (Sprint 2+)
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8001

    # OpenAI (Sprint 3+)
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: Literal["json", "console"] = "console"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def CHROMA_URL(self) -> str:
        return f"http://{self.CHROMA_HOST}:{self.CHROMA_PORT}"


@lru_cache()
def get_settings() -> Settings:
    env = os.getenv("ENV", "development")
    if env == "development":
        from app.config.development import DevelopmentSettings
        return DevelopmentSettings()
    if env == "testing":
        from app.config.testing import TestingSettings
        return TestingSettings()
    if env == "production":
        from app.config.production import ProductionSettings
        return ProductionSettings()
    return Settings()
