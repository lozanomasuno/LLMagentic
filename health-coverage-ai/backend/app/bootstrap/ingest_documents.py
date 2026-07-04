"""CLI script — ingest DOCX policy documents into ChromaDB."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from app.ai.parsers.docx_parser import DocxParser
from app.ai.vectorstore.chroma_client import ChromaVectorStore
from app.config.settings import get_settings

logger = logging.getLogger(__name__)

# Supported document filenames (order matters for logging clarity)
_SUPPORTED = {
    "DOC1_Manual_de_Beneficios.docx",
    "DOC2_Terminos_y_Condiciones.docx",
    "DOC3_Criterios_de_Necesidad_Medica.docx",
}


def ingest(data_dir: Path, reset: bool = False) -> dict[str, int]:
    """
    Parse all supported DOCX files in *data_dir* and upsert into ChromaDB.

    Args:
        data_dir: Directory containing the DOCX files.
        reset:    If True, wipe the collection before ingesting.

    Returns:
        Mapping of {filename: chunk_count} for each processed document.

    Raises:
        RuntimeError: If ChromaDB is not reachable.
    """
    settings = get_settings()
    vs = ChromaVectorStore(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)

    if not vs.ping():
        raise RuntimeError(
            f"ChromaDB not reachable at {settings.CHROMA_HOST}:{settings.CHROMA_PORT}. "
            "Make sure the chromadb service is running (docker compose up chromadb)."
        )

    if reset:
        vs.reset_collection()
        logger.info("Vector store collection reset")

    parser = DocxParser()
    results: dict[str, int] = {}

    docx_files = sorted(
        f for f in data_dir.glob("*.docx") if f.name in _SUPPORTED
    )

    if not docx_files:
        logger.warning("No supported DOCX files found in %s", data_dir)
        return results

    for docx_file in docx_files:
        slug = DocxParser._slug(docx_file.name)
        chunks = parser.parse(docx_file)
        # Remove stale data for this document before upserting
        if not reset:
            vs.delete_by_slug(slug)
        vs.upsert_chunks(chunks)
        results[docx_file.name] = len(chunks)
        logger.info("Ingested '%s' → %d chunks", docx_file.name, len(chunks))

    return results


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s \u2014 %(message)s")

    parser = argparse.ArgumentParser(
        description="Ingest DOCX policy documents into ChromaDB"
    )
    parser.add_argument(
        "--dir",
        type=Path,
        default=Path("data"),
        help="Directory containing the DOCX files (default: data/)",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Wipe the collection before ingesting",
    )
    args = parser.parse_args()

    if not args.dir.exists():
        print(f"ERROR: Directory not found: {args.dir}", file=sys.stderr)
        sys.exit(1)

    try:
        results = ingest(args.dir, reset=args.reset)
        for name, count in results.items():
            print(f"  \u2713 {name}: {count} chunks")
        total = sum(results.values())
        print(f"\u2713 Total: {total} chunks across {len(results)} documents")
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
