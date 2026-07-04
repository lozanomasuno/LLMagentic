"""Suggestions endpoint — query auto-complete (Sprint 3+)."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_suggestion_service
from app.services.suggestion_service import SuggestionService

router = APIRouter()


@router.get(
    "",
    response_model=list[str],
    summary="Get query auto-complete suggestions",
)
async def get_suggestions(
    service: Annotated[SuggestionService, Depends(get_suggestion_service)],
    q: Annotated[str, Query(max_length=500, description="Partial query text")] = "",
) -> list[str]:
    """
    Returns query suggestions for the frontend auto-complete widget.

    **Status**: Returns empty list — LLM-based suggestions available in Sprint 3.
    """
    return await service.get_suggestions(q)
