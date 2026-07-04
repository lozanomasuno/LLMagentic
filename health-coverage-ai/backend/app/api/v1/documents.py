"""Documents endpoint — indexed policy documents."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_document_service
from app.domain.schemas.system import DocumentInfo
from app.services.document_service import DocumentService

router = APIRouter()


@router.get(
    "",
    response_model=list[DocumentInfo],
    summary="List indexed policy documents",
)
async def list_documents(
    service: Annotated[DocumentService, Depends(get_document_service)],
) -> list[DocumentInfo]:
    """
    Returns the indexing status for each policy document (DOC1–DOC3).
    Run `python -m app.bootstrap.ingest_documents` to populate ChromaDB.
    """
    return service.list_documents()
