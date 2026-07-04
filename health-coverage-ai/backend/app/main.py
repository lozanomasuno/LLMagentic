"""Application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as v1_router
from app.config.settings import get_settings
from app.core.logging import configure_logging, get_logger

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    logger = get_logger(__name__)
    logger.info(
        "Application starting",
        name=settings.APP_NAME,
        version=settings.APP_VERSION,
        env=settings.ENV,
    )
    yield
    logger.info("Application shutting down")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered health coverage assistant",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)




@app.get("/health", tags=["Infrastructure"])
async def health_check() -> dict:
    """Basic liveness probe."""
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


app.include_router(v1_router, prefix="/api/v1")
