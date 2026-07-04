"""Affiliate service — business logic for affiliate queries."""

from app.core.exceptions import AffiliateNotFoundError
from app.core.logging import get_logger
from app.domain.schemas.affiliate import AffiliateResponse
from app.repositories.affiliate_repository import AffiliateRepository

logger = get_logger(__name__)


class AffiliateService:
    def __init__(self, repository: AffiliateRepository) -> None:
        self._repository = repository

    async def find_by_document(self, numero_documento: str) -> AffiliateResponse:
        logger.info("Searching affiliate by document", document=numero_documento)
        affiliate = await self._repository.find_by_document(numero_documento)
        if affiliate is None:
            raise AffiliateNotFoundError(
                f"No affiliate found with document: {numero_documento}"
            )
        logger.info(
            "Affiliate found",
            id_afiliado=affiliate.id_afiliado,
            plan=affiliate.plan,
            estado=affiliate.estado_afiliacion,
        )
        return AffiliateResponse.model_validate(affiliate)

    async def find_by_id_afiliado(self, id_afiliado: str) -> AffiliateResponse:
        affiliate = await self._repository.find_by_id_afiliado(id_afiliado)
        if affiliate is None:
            raise AffiliateNotFoundError(f"No affiliate found with id: {id_afiliado}")
        return AffiliateResponse.model_validate(affiliate)
