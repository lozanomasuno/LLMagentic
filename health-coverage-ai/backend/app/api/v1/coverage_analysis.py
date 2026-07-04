"""Coverage analysis endpoint."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_coverage_analysis_service_v2
from app.core.exceptions import AffiliateNotFoundError
from app.domain.schemas.coverage_analysis import (
    CoverageAnalysisRequest,
    CoverageAnalysisResponse,
)
from app.services.coverage_analysis_service import CoverageAnalysisService

router = APIRouter()


@router.post(
    "",
    response_model=CoverageAnalysisResponse,
    summary="Analyze coverage for an affiliate query",
    status_code=status.HTTP_200_OK,
)
async def analyze_coverage(
    request: CoverageAnalysisRequest,
    service: Annotated[CoverageAnalysisService, Depends(get_coverage_analysis_service_v2)],
) -> CoverageAnalysisResponse:
    """
    Execute a full RAG + LLM coverage analysis for an affiliate.

    Steps:
    1. Locate the affiliate in PostgreSQL by document number
    2. Retrieve relevant policy document chunks via semantic search (ChromaDB)
    3. Analyze coverage using GPT-4o with the retrieved context
    4. Persist the consultation record
    5. Return the structured coverage decision with sources and agent trace
    """
    try:
        return await service.analyze(request)
    except AffiliateNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": str(exc), "document_number": request.document_number},
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Analysis failed. Please try again.", "error": str(exc)},
        ) from exc
