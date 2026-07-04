"""Affiliate endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_affiliate_service
from app.core.exceptions import AffiliateNotFoundError
from app.core.logging import get_logger
from app.domain.schemas.affiliate import AffiliateResponse
from app.services.affiliate_service import AffiliateService

router = APIRouter()
logger = get_logger(__name__)


@router.get(
    "/{document}",
    response_model=AffiliateResponse,
    summary="Get affiliate by document number",
)
async def get_affiliate(
    document: str,
    service: Annotated[AffiliateService, Depends(get_affiliate_service)],
) -> AffiliateResponse:
    """
    Retrieve an affiliate's full profile by their identity document number.

    - **document**: CC, CE, TI or PA document number
    """
    try:
        return await service.find_by_document(document)
    except AffiliateNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No affiliate found with document number: {document}",
        )
