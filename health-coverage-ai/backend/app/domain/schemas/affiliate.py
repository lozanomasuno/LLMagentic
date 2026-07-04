"""Affiliate schemas — public API representation."""

from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict


class AffiliateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # Identifiers
    id_afiliado: str
    tipo_documento: str
    numero_documento: str

    # Personal data
    primer_nombre: str
    primer_apellido: str
    segundo_apellido: Optional[str] = None
    sexo: str
    fecha_nacimiento: date
    edad: int
    ciudad: str
    departamento: str

    # Membership
    tipo_afiliado: str
    parentesco: str
    plan: Literal["Esencial", "Clásico", "Premium"]
    fecha_afiliacion: date
    antiguedad_meses: int

    # Status
    estado_afiliacion: Literal["Activo", "Suspendido", "Retirado"]
    estado_pagos: Literal["Al día", "En mora"]
    dias_mora: int
    valor_pendiente_cop: int

    # Prior authorization
    tiene_autorizacion_previa: bool
    servicio_autorizado: Optional[str] = None
    numero_autorizacion: Optional[str] = None
    fecha_autorizacion: Optional[date] = None
    vigencia_autorizacion: Optional[date] = None

    # Pre-existing conditions
    preexistencia_declarada: bool
    descripcion_preexistencia: Optional[str] = None

    @property
    def nombre_completo(self) -> str:
        parts = [self.primer_nombre, self.primer_apellido]
        if self.segundo_apellido:
            parts.append(self.segundo_apellido)
        return " ".join(parts)
