"""Production environment configuration."""

from app.config.settings import Settings


class ProductionSettings(Settings):
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
