"""Dependency injection providers for FastAPI endpoints."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.agents.coverage_agent import CoverageAgent
from app.ai.providers.openai_provider import OpenAIProvider
from app.ai.rag.retriever import CoverageRetriever
from app.ai.vectorstore.chroma_client import ChromaVectorStore
from app.config.settings import get_settings
from app.core.database import get_db
from app.repositories.affiliate_repository import AffiliateRepository
from app.repositories.consultation_repository import ConsultationRepository
from app.services.affiliate_service import AffiliateService
from app.services.coverage_analysis_service import CoverageAnalysisService
from app.services.document_service import DocumentService
from app.services.suggestion_service import SuggestionService

DbSession = Annotated[AsyncSession, Depends(get_db)]


def get_affiliate_repository(session: DbSession) -> AffiliateRepository:
    return AffiliateRepository(session)


def get_consultation_repository(session: DbSession) -> ConsultationRepository:
    return ConsultationRepository(session)


def get_affiliate_service(
    repo: Annotated[AffiliateRepository, Depends(get_affiliate_repository)],
) -> AffiliateService:
    return AffiliateService(repo)


def get_suggestion_service() -> SuggestionService:
    return SuggestionService()


def get_vectorstore() -> ChromaVectorStore:
    settings = get_settings()
    return ChromaVectorStore(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)


def get_document_service(
    vs: Annotated[ChromaVectorStore, Depends(get_vectorstore)],
) -> DocumentService:
    return DocumentService(vs)


def get_openai_provider() -> OpenAIProvider:
    settings = get_settings()
    return OpenAIProvider(api_key=settings.OPENAI_API_KEY, model=settings.OPENAI_MODEL)


def get_retriever(
    vs: Annotated[ChromaVectorStore, Depends(get_vectorstore)],
) -> CoverageRetriever:
    return CoverageRetriever(vs)


def get_coverage_agent(
    retriever: Annotated[CoverageRetriever, Depends(get_retriever)],
    llm: Annotated[OpenAIProvider, Depends(get_openai_provider)],
) -> CoverageAgent:
    return CoverageAgent(retriever=retriever, llm=llm)


def get_coverage_analysis_service_v2(
    affiliate_repo: Annotated[AffiliateRepository, Depends(get_affiliate_repository)],
    consultation_repo: Annotated[ConsultationRepository, Depends(get_consultation_repository)],
    agent: Annotated[CoverageAgent, Depends(get_coverage_agent)],
) -> CoverageAnalysisService:
    return CoverageAnalysisService(
        affiliate_repo=affiliate_repo,
        consultation_repo=consultation_repo,
        agent=agent,
    )
