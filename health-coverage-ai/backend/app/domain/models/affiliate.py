"""Affiliate ORM model — maps the BD_afiliados data structure."""

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.domain.models.consultation import Consultation


class Affiliate(Base):
    __tablename__ = "affiliates"

    # Primary key (internal, auto-increment)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Identifiers
    id_afiliado: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    tipo_documento: Mapped[str] = mapped_column(String(5), nullable=False)
    numero_documento: Mapped[str] = mapped_column(
        String(30), unique=True, nullable=False, index=True
    )

    # Personal data
    primer_nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    primer_apellido: Mapped[str] = mapped_column(String(100), nullable=False)
    segundo_apellido: Mapped[str | None] = mapped_column(String(100), nullable=True)
    sexo: Mapped[str] = mapped_column(String(1), nullable=False)
    fecha_nacimiento: Mapped[date] = mapped_column(Date, nullable=False)
    edad: Mapped[int] = mapped_column(Integer, nullable=False)
    ciudad: Mapped[str] = mapped_column(String(100), nullable=False)
    departamento: Mapped[str] = mapped_column(String(100), nullable=False)

    # Membership
    tipo_afiliado: Mapped[str] = mapped_column(String(20), nullable=False)
    parentesco: Mapped[str] = mapped_column(String(50), nullable=False)
    plan: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    fecha_afiliacion: Mapped[date] = mapped_column(Date, nullable=False)
    antiguedad_meses: Mapped[int] = mapped_column(Integer, nullable=False)

    # Status — key fields for coverage decisions
    estado_afiliacion: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    estado_pagos: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    dias_mora: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    valor_pendiente_cop: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)

    # Prior authorization
    tiene_autorizacion_previa: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    servicio_autorizado: Mapped[str | None] = mapped_column(String(300), nullable=True)
    numero_autorizacion: Mapped[str | None] = mapped_column(String(50), nullable=True)
    fecha_autorizacion: Mapped[date | None] = mapped_column(Date, nullable=True)
    vigencia_autorizacion: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Pre-existing conditions
    preexistencia_declarada: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    descripcion_preexistencia: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Contact (not exposed in public API responses)
    correo_contacto: Mapped[str | None] = mapped_column(String(200), nullable=True)
    telefono_contacto: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Relationships
    consultations: Mapped[list["Consultation"]] = relationship(
        "Consultation", back_populates="affiliate", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<Affiliate {self.id_afiliado} — {self.primer_nombre} {self.primer_apellido}>"
