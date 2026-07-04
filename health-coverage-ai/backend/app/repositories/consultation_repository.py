"""Consultation repository — persists and retrieves coverage queries."""

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.consultation import Consultation


class ConsultationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, consultation: Consultation) -> Consultation:
        self._session.add(consultation)
        await self._session.commit()
        await self._session.refresh(consultation)
        return consultation

    async def find_by_id(self, consultation_id: uuid.UUID) -> Optional[Consultation]:
        stmt = select(Consultation).where(Consultation.id == consultation_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_affiliate(
        self, affiliate_id: int, limit: int = 10
    ) -> list[Consultation]:
        stmt = (
            select(Consultation)
            .where(Consultation.affiliate_id == affiliate_id)
            .order_by(Consultation.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
