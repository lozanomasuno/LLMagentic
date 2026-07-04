"""Reset the database — drops all tables and re-creates schema.

Usage:
    cd backend
    python -m app.bootstrap.reset_database

⚠️  WARNING: This operation is DESTRUCTIVE. Use only in development.
"""

import asyncio

from app.core.database import Base, engine
from app.core.logging import configure_logging, get_logger
from app.domain.models import affiliate, consultation, log  # noqa: F401 — register models

configure_logging()
logger = get_logger(__name__)


async def reset() -> None:
    logger.warning("Dropping all tables — irreversible in production")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database reset complete")


if __name__ == "__main__":
    asyncio.run(reset())
