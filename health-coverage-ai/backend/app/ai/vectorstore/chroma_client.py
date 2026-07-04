"""ChromaDB HTTP client wrapper for the health coverage vector store."""

from __future__ import annotations

import logging
from typing import Any

import chromadb
from chromadb.utils import embedding_functions

from app.ai.parsers.docx_parser import DocumentChunk

logger = logging.getLogger(__name__)

COLLECTION_NAME = "health_coverage_docs"


class ChromaVectorStore:
    """
    Thin wrapper around ChromaDB's HTTP client.

    Uses ChromaDB's built-in DefaultEmbeddingFunction (all-MiniLM-L6-v2 via
    ONNX runtime) so no external API key is required for Sprint 2.
    Sprint 3 will swap this for OpenAIEmbeddingFunction via the LLMProvider.
    """

    def __init__(self, host: str, port: int) -> None:
        self._client = chromadb.HttpClient(host=host, port=port)
        self._ef = embedding_functions.DefaultEmbeddingFunction()

    # ── connectivity ───────────────────────────────────────────────────────

    def ping(self) -> bool:
        """Return True if ChromaDB is reachable."""
        try:
            self._client.heartbeat()
            return True
        except Exception:
            return False

    # ── collection helpers ─────────────────────────────────────────────────

    def _collection(self) -> chromadb.Collection:
        return self._client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=self._ef,
            metadata={"hnsw:space": "cosine"},
        )

    # ── write operations ───────────────────────────────────────────────────

    def upsert_chunks(self, chunks: list[DocumentChunk]) -> None:
        """Upsert document chunks (embeddings generated automatically)."""
        if not chunks:
            return
        col = self._collection()
        col.upsert(
            ids=[c.id for c in chunks],
            documents=[c.text for c in chunks],
            metadatas=[
                {
                    "document_name": c.document_name,
                    "document_slug": c.document_slug,
                    "section": c.section,
                    "chunk_index": c.chunk_index,
                    "char_count": c.char_count,
                }
                for c in chunks
            ],
        )

    def delete_by_slug(self, slug: str) -> None:
        """Remove all chunks belonging to a given document slug."""
        try:
            col = self._collection()
            col.delete(where={"document_slug": slug})
        except Exception as exc:
            logger.warning("Failed to delete slug '%s': %s", slug, exc)

    def reset_collection(self) -> None:
        """Delete and recreate the collection, wiping all indexed data."""
        try:
            self._client.delete_collection(COLLECTION_NAME)
            logger.info("Collection '%s' deleted", COLLECTION_NAME)
        except Exception:
            pass  # Collection may not exist yet

    # ── read operations ────────────────────────────────────────────────────

    def query(
        self,
        query_text: str,
        n_results: int = 5,
        where: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Vector similarity search. Returns raw ChromaDB query response."""
        col = self._collection()
        count = col.count()
        if count == 0:
            return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}

        kwargs: dict[str, Any] = {
            "query_texts": [query_text],
            "n_results": min(n_results, count),
        }
        if where:
            kwargs["where"] = where
        return col.query(**kwargs)

    def collection_count(self) -> int:
        """Total number of chunks in the collection."""
        try:
            return self._collection().count()
        except Exception:
            return 0

    def chunks_by_slug(self) -> dict[str, int]:
        """Return {document_slug: chunk_count} for every indexed document."""
        try:
            col = self._collection()
            if col.count() == 0:
                return {}
            result = col.get(include=["metadatas"])
            counts: dict[str, int] = {}
            for meta in result.get("metadatas") or []:
                slug = meta.get("document_slug", "unknown")
                counts[slug] = counts.get(slug, 0) + 1
            return counts
        except Exception:
            return {}
