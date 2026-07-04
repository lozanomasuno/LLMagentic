"""Document service — metadata about indexed policy documents."""

from __future__ import annotations

from datetime import datetime, timezone

from app.ai.vectorstore.chroma_client import ChromaVectorStore
from app.domain.schemas.system import DocumentInfo

# Canonical document registry (Sprint 2 scope)
_KNOWN_DOCS: dict[str, str] = {
    "doc1": "DOC1_Manual_de_Beneficios.docx",
    "doc2": "DOC2_Terminos_y_Condiciones.docx",
    "doc3": "DOC3_Criterios_de_Necesidad_Medica.docx",
}


class DocumentService:
    def __init__(self, vectorstore: ChromaVectorStore) -> None:
        self._vs = vectorstore

    def list_documents(self) -> list[DocumentInfo]:
        """
        Returns indexing status for each known policy document.
        If ChromaDB is unreachable the counts default to 0 (status=processing).
        """
        try:
            counts = self._vs.chunks_by_slug()
        except Exception:
            counts = {}

        result: list[DocumentInfo] = []
        for slug, name in _KNOWN_DOCS.items():
            chunk_count = counts.get(slug, 0)
            result.append(
                DocumentInfo(
                    id=slug,
                    name=name,
                    status="indexed" if chunk_count > 0 else "processing",
                    chunks=chunk_count,
                    indexed_at=datetime.now(timezone.utc) if chunk_count > 0 else None,
                )
            )
        return result
