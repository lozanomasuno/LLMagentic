"""API v1 router — aggregates all endpoint modules."""

from fastapi import APIRouter

from app.api.v1 import affiliates, coverage_analysis, documents, suggestions, system

router = APIRouter()

router.include_router(affiliates.router, prefix="/affiliates", tags=["Affiliates"])
router.include_router(
    coverage_analysis.router, prefix="/coverage-analysis", tags=["Coverage Analysis"]
)
router.include_router(documents.router, prefix="/documents", tags=["Documents"])
router.include_router(suggestions.router, prefix="/suggestions", tags=["Suggestions"])
router.include_router(system.router, prefix="/system", tags=["System"])
