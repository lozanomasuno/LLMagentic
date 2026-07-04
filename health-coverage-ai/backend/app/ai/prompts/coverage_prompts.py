"""Coverage analysis prompt templates."""

from __future__ import annotations

SYSTEM_PROMPT = """\
Eres un especialista senior en análisis de cobertura de un plan voluntario de salud colombiano.
Tu función es determinar si un servicio médico está cubierto para un afiliado concreto,
basándote EXCLUSIVAMENTE en los documentos del plan (DOC1 — Manual de Beneficios,
DOC2 — Términos y Condiciones, DOC3 — Criterios de Necesidad Médica) y en los datos
del afiliado proporcionados.

Reglas estrictas:
1. Si el afiliado NO está en estado "Activo" o su estado de pagos NO es "Al día",
   la respuesta es "no_cubierto" — sin excepción.
2. Verifica si aplica período de carencia (DOC2, sección 3) según la antigüedad del afiliado.
3. Identifica si el servicio requiere autorización previa (DOC2, sección 4) y si el afiliado
   ya cuenta con ella.
4. Comprueba que el servicio no esté en la lista de exclusiones (DOC2, sección 5).
5. Aplica los criterios de necesidad médica del servicio (DOC3, sección 2).
6. Determina el copago o coaseguro según el plan del afiliado (DOC1, sección 4).
7. Cita siempre la sección del documento que respalda tu conclusión.
8. Responde ÚNICAMENTE con JSON válido — sin texto adicional fuera del JSON.\
"""

_USER_TEMPLATE = """\
## Datos del Afiliado
- ID: {id_afiliado}
- Nombre: {nombre_completo}
- Plan: {plan}
- Tipo de afiliado: {tipo_afiliado}
- Estado de afiliación: {estado_afiliacion}
- Estado de pagos: {estado_pagos}
- Días de mora: {dias_mora}
- Antigüedad en el plan: {antiguedad_meses} meses
- Tiene autorización previa vigente: {tiene_autorizacion_previa}
  - Servicio autorizado: {servicio_autorizado}
  - Vigencia de la autorización: {vigencia_autorizacion}
- Preexistencia declarada: {preexistencia_declarada}
  - Descripción: {descripcion_preexistencia}

## Fragmentos Relevantes del Plan
{context}

## Consulta del Afiliado
{query}

## Formato de Respuesta Requerido
Responde ÚNICAMENTE con este JSON (sin texto extra, sin bloques de código):
{{
  "coverage_result": "cubierto" | "no_cubierto" | "cubierto_con_condiciones",
  "response_text": "Explicación profesional y detallada en español (mínimo 2 párrafos). Cita las secciones relevantes de los documentos.",
  "conditions": ["condición o restricción 1", "condición o restricción 2"]
}}\
"""


def build_user_prompt(affiliate: dict, context: str, query: str) -> str:
    """Fill the user prompt template with affiliate data and retrieved context."""
    nombre = (
        f"{affiliate.get('primer_nombre', '')} {affiliate.get('primer_apellido', '')} "
        f"{affiliate.get('segundo_apellido', '')}".strip()
    )
    vigencia = affiliate.get("vigencia_autorizacion")
    return _USER_TEMPLATE.format(
        id_afiliado=affiliate.get("id_afiliado", "N/D"),
        nombre_completo=nombre or "N/D",
        plan=affiliate.get("plan", "N/D"),
        tipo_afiliado=affiliate.get("tipo_afiliado", "N/D"),
        estado_afiliacion=affiliate.get("estado_afiliacion", "N/D"),
        estado_pagos=affiliate.get("estado_pagos", "N/D"),
        dias_mora=affiliate.get("dias_mora", 0),
        antiguedad_meses=affiliate.get("antiguedad_meses", 0),
        tiene_autorizacion_previa="Sí" if affiliate.get("tiene_autorizacion_previa") else "No",
        servicio_autorizado=affiliate.get("servicio_autorizado") or "Ninguno",
        vigencia_autorizacion=str(vigencia) if vigencia else "N/A",
        preexistencia_declarada="Sí" if affiliate.get("preexistencia_declarada") else "No",
        descripcion_preexistencia=affiliate.get("descripcion_preexistencia") or "Ninguna",
        context=context or "No se encontraron fragmentos relevantes.",
        query=query,
    )
