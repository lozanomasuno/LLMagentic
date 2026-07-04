"""Coverage analysis schemas — request and response contracts."""

from typing import Optional

from pydantic import BaseModel, Field


class CoverageAnalysisRequest(BaseModel):
    document_number: str = Field(
        ..., min_length=1, max_length=30, description="Affiliate document number"
    )
    query: str = Field(
        ..., min_length=10, max_length=2000, description="Coverage query in natural language"
    )


class DocumentSource(BaseModel):
    document: str
    section: str
    page: Optional[int] = None
    excerpt: str
    relevance_score: Optional[float] = None


class AgentStep(BaseModel):
    step: str
    description: str
    result: Optional[str] = None
    duration_ms: Optional[int] = None


class CoverageAnalysisResponse(BaseModel):
    consultation_id: str
    affiliate_id: str
    coverage_result: str  # cubierto | no_cubierto | cubierto_con_condiciones
    response_text: str
    sources: list[DocumentSource]
    agent_trace: list[AgentStep]
    duration_ms: int
