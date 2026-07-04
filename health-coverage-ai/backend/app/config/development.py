"""Development environment configuration."""

from app.config.settings import Settings


class DevelopmentSettings(Settings):
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    LOG_FORMAT: str = "console"
    CORS_ORIGINS: list[str] = [
        "http://localhost:4200",
        "http://127.0.0.1:4200",
    ]
