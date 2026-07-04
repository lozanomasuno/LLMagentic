"""System status endpoint."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.vectorstore.chroma_client import ChromaVectorStore
from app.api.deps import get_vectorstore
from app.config.settings import get_settings
from app.core.database import get_db
from app.domain.schemas.system import ServiceStatus, SystemStatusResponse

router = APIRouter()
settings = get_settings()


@router.get(
    "",
    response_model=SystemStatusResponse,
    summary="System health and dependency status",
)
async def get_system_status(
    session: Annotated[AsyncSession, Depends(get_db)],
    vs: Annotated[ChromaVectorStore, Depends(get_vectorstore)],
) -> SystemStatusResponse:
    """
    Returns the operational status of all system dependencies.
    Used by the frontend to display infrastructure health.
    """
    # Check PostgreSQL
    try:
        await session.execute(text("SELECT 1"))
        db_status = ServiceStatus(status="connected")
    except Exception as exc:
        db_status = ServiceStatus(status="disconnected", message=str(exc))

    # Check ChromaDB
    try:
        if vs.ping():
            chunk_count = vs.collection_count()
            vectorstore_status = ServiceStatus(
                status="connected",
                message=f"{chunk_count} chunks indexed",
            )
        else:
            vectorstore_status = ServiceStatus(
                status="disconnected",
                message="ChromaDB not reachable",
            )
    except Exception as exc:
        vectorstore_status = ServiceStatus(status="disconnected", message=str(exc))

    is_operational = (
        db_status.status == "connected" and vectorstore_status.status == "connected"
    )
    is_degraded = not is_operational and db_status.status == "connected"
    overall = "operational" if is_operational else ("degraded" if is_degraded else "down")

    return SystemStatusResponse(
        version=settings.APP_VERSION,
        environment=settings.ENV,
        status=overall,
        database=db_status,
        vectorstore=vectorstore_status,
    )
