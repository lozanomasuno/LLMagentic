"""RAG retriever — queries ChromaDB and formats results for the agent."""

from __future__ import annotations

from dataclasses import dataclass

from app.ai.vectorstore.chroma_client import ChromaVectorStore


@dataclass
class RetrievedChunk:
    chunk_id: str
    document_name: str
    document_slug: str
    section: str
    text: str
    relevance_score: float  # cosine distance → converted to similarity


class CoverageRetriever:
    """Retrieves the most relevant policy document chunks for a given query."""

    DEFAULT_N_RESULTS = 6

    def __init__(self, vectorstore: ChromaVectorStore) -> None:
        self._vs = vectorstore

    def retrieve(
        self, query: str, n_results: int = DEFAULT_N_RESULTS
    ) -> list[RetrievedChunk]:
        """
        Perform a vector similarity search and return structured results.

        ChromaDB returns cosine *distance* in [0, 2]; we convert to similarity
        as 1 − distance/2 so that 1.0 = perfect match, 0.0 = orthogonal.
        """
        raw = self._vs.query(query, n_results=n_results)

        ids: list[str] = (raw.get("ids") or [[]])[0]
        docs: list[str] = (raw.get("documents") or [[]])[0]
        metas: list[dict] = (raw.get("metadatas") or [[]])[0]
        distances: list[float] = (raw.get("distances") or [[]])[0]

        chunks: list[RetrievedChunk] = []
        for cid, text, meta, dist in zip(ids, docs, metas, distances):
            similarity = round(max(0.0, 1.0 - dist / 2.0), 4)
            chunks.append(
                RetrievedChunk(
                    chunk_id=cid,
                    document_name=meta.get("document_name", ""),
                    document_slug=meta.get("document_slug", ""),
                    section=meta.get("section", ""),
                    text=text,
                    relevance_score=similarity,
                )
            )

        # Sort by relevance descending
        return sorted(chunks, key=lambda c: c.relevance_score, reverse=True)

    @staticmethod
    def format_context(chunks: list[RetrievedChunk]) -> str:
        """Format retrieved chunks as a readable context block for the LLM."""
        if not chunks:
            return "No se encontraron fragmentos relevantes en los documentos del plan."

        lines: list[str] = []
        for i, chunk in enumerate(chunks, start=1):
            lines.append(
                f"[Fragmento {i} — {chunk.document_name}, sección: {chunk.section}]"
            )
            lines.append(chunk.text)
            lines.append("")
        return "\n".join(lines).strip()
