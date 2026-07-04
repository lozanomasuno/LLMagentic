"""Suggestion service — query auto-complete hints."""

from __future__ import annotations

from app.core.logging import get_logger

logger = get_logger(__name__)

# Common coverage queries drawn from the policy documents (DOC1-DOC3)
_SUGGESTIONS: list[str] = [
    "¿Está cubierta una resonancia magnética de rodilla?",
    "¿Se cubre una tomografía sin autorización previa?",
    "¿Qué cubre el plan para cirugía de columna?",
    "¿El plan cubre hospitalización programada?",
    "¿Cuáles son los períodos de carencia del plan?",
    "¿Qué terapias de rehabilitación están incluidas?",
    "¿Cubre el plan medicamentos de alto costo?",
    "¿Cuál es el copago para atención ambulatoria?",
    "¿Qué servicios requieren autorización previa?",
    "¿Se cubre la atención de urgencias?",
    "¿El plan cubre procedimientos de salud mental?",
    "¿Qué exclusiones aplican a mi plan?",
    "¿Cubre el plan atención domiciliaria?",
    "¿Cuánto pago de coaseguro en una cirugía electiva?",
    "¿Qué criterios aplican para necesidad médica?",
]


class SuggestionService:
    async def get_suggestions(self, query: str = "") -> list[str]:
        """
        Return up to 5 query suggestions filtered by the user's input.

        Matching is case-insensitive and accent-insensitive (simple heuristic).
        Returns all suggestions when the query is empty or very short.
        """
        logger.debug("Suggestions requested", query_preview=query[:50])

        if not query or len(query) < 3:
            return _SUGGESTIONS[:5]

        q = query.lower()
        matches = [s for s in _SUGGESTIONS if q in s.lower()]

        # Fallback: word-level partial match
        if not matches:
            words = q.split()
            matches = [
                s for s in _SUGGESTIONS if any(w in s.lower() for w in words)
            ]

        return matches[:5] if matches else _SUGGESTIONS[:5]
