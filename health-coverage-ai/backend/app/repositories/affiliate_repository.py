"""Affiliate repository — all database access for affiliates."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.affiliate import Affiliate


class AffiliateRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_document(self, numero_documento: str) -> Optional[Affiliate]:
        stmt = select(Affiliate).where(Affiliate.numero_documento == numero_documento)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_id_afiliado(self, id_afiliado: str) -> Optional[Affiliate]:
        stmt = select(Affiliate).where(Affiliate.id_afiliado == id_afiliado)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_id(self, affiliate_id: int) -> Optional[Affiliate]:
        stmt = select(Affiliate).where(Affiliate.id == affiliate_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
