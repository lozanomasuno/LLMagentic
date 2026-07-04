"""Testing environment configuration."""

from app.config.settings import Settings


class TestingSettings(Settings):
    DEBUG: bool = True
    LOG_LEVEL: str = "WARNING"
    LOG_FORMAT: str = "console"
    POSTGRES_DB: str = "health_coverage_test"
    CORS_ORIGINS: list[str] = ["http://localhost:4200"]
