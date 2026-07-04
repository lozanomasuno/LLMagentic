"""Coverage analysis service — orchestrates the LangGraph agent."""

from __future__ import annotations

import time
import uuid

from app.ai.agents.coverage_agent import CoverageAgent
from app.core.exceptions import AffiliateNotFoundError
from app.core.logging import get_logger
from app.domain.models.consultation import Consultation
from app.domain.schemas.coverage_analysis import (
    AgentStep,
    CoverageAnalysisRequest,
    CoverageAnalysisResponse,
    DocumentSource,
)
from app.repositories.affiliate_repository import AffiliateRepository
from app.repositories.consultation_repository import ConsultationRepository

logger = get_logger(__name__)


def _affiliate_to_dict(affiliate) -> dict:
    """Convert ORM Affiliate to a plain dict for the agent."""
    return {
        "id": affiliate.id,
        "id_afiliado": affiliate.id_afiliado,
        "primer_nombre": affiliate.primer_nombre,
        "primer_apellido": affiliate.primer_apellido,
        "segundo_apellido": affiliate.segundo_apellido,
        "plan": affiliate.plan,
        "tipo_afiliado": affiliate.tipo_afiliado,
        "estado_afiliacion": affiliate.estado_afiliacion,
        "estado_pagos": affiliate.estado_pagos,
        "dias_mora": affiliate.dias_mora,
        "antiguedad_meses": affiliate.antiguedad_meses,
        "tiene_autorizacion_previa": affiliate.tiene_autorizacion_previa,
        "servicio_autorizado": affiliate.servicio_autorizado,
        "vigencia_autorizacion": affiliate.vigencia_autorizacion,
        "preexistencia_declarada": affiliate.preexistencia_declarada,
        "descripcion_preexistencia": affiliate.descripcion_preexistencia,
    }


class CoverageAnalysisService:
    def __init__(
        self,
        affiliate_repo: AffiliateRepository,
        consultation_repo: ConsultationRepository,
        agent: CoverageAgent,
    ) -> None:
        self._affiliate_repo = affiliate_repo
        self._consultation_repo = consultation_repo
        self._agent = agent

    async def analyze(
        self, request: CoverageAnalysisRequest
    ) -> CoverageAnalysisResponse:
        """
        Full coverage analysis pipeline:
          1. Locate affiliate in PostgreSQL
          2. Run the LangGraph agent (RAG + LLM)
          3. Persist the consultation record
          4. Return structured response
        """
        t_start = time.perf_counter()

        # ── 1. Find affiliate ──────────────────────────────────────────────
        affiliate = await self._affiliate_repo.find_by_document(
            request.document_number
        )
        if affiliate is None:
            raise AffiliateNotFoundError(
                f"Affiliate with document '{request.document_number}' not found"
            )

        affiliate_dict = _affiliate_to_dict(affiliate)
        logger.info(
            "Coverage analysis started",
            affiliate=affiliate.id_afiliado,
            plan=affiliate.plan,
        )

        # ── 2. Run agent ───────────────────────────────────────────────────
        result = await self._agent.run(request.query, affiliate_dict)
        duration_ms = int((time.perf_counter() - t_start) * 1000)

        # ── 3. Build sources list ──────────────────────────────────────────
        sources = [
            DocumentSource(
                document=chunk.document_name,
                section=chunk.section,
                excerpt=chunk.text[:300],
                relevance_score=chunk.relevance_score,
            )
            for chunk in result.get("chunks", [])
        ]

        # ── 4. Build agent trace ───────────────────────────────────────────
        agent_trace = [
            AgentStep(
                step=step["step"],
                description=step["description"],
                result=step.get("result"),
                duration_ms=step.get("duration_ms"),
            )
            for step in result.get("steps", [])
        ]

        # ── 5. Persist consultation ────────────────────────────────────────
        consultation_id = uuid.uuid4()
        consultation = Consultation(
            id=consultation_id,
            affiliate_id=affiliate.id,
            query_text=request.query,
            response_text=result.get("response_text", ""),
            coverage_result=result.get("coverage_result", "no_cubierto"),
            sources_used=[s.model_dump() for s in sources],
            agent_trace=[t.model_dump() for t in agent_trace],
            duration_ms=duration_ms,
        )
        await self._consultation_repo.create(consultation)

        logger.info(
            "Coverage analysis complete",
            affiliate=affiliate.id_afiliado,
            result=consultation.coverage_result,
            duration_ms=duration_ms,
        )

        # ── 6. Return response ─────────────────────────────────────────────
        return CoverageAnalysisResponse(
            consultation_id=str(consultation_id),
            affiliate_id=affiliate.id_afiliado,
            coverage_result=consultation.coverage_result,
            response_text=consultation.response_text,
            sources=sources,
            agent_trace=agent_trace,
            duration_ms=duration_ms,
        )
