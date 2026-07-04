"""Consultation ORM model — records each coverage analysis query."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base

if TYPE_CHECKING:
    from app.domain.models.affiliate import Affiliate


class Consultation(Base):
    __tablename__ = "consultations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    affiliate_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("affiliates.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    response_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    # cubierto | no_cubierto | cubierto_con_condiciones
    coverage_result: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    sources_used: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    agent_trace: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    affiliate: Mapped["Affiliate"] = relationship("Affiliate", back_populates="consultations")

    def __repr__(self) -> str:
        return f"<Consultation {self.id} — {self.coverage_result}>"
