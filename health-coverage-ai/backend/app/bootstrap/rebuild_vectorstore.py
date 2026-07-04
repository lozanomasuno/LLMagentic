"""CLI script — wipe and rebuild the entire ChromaDB vector store."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from app.bootstrap.ingest_documents import ingest

logger = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s \u2014 %(message)s")

    parser = argparse.ArgumentParser(
        description="Rebuild ChromaDB vector store from scratch (destructive)"
    )
    parser.add_argument(
        "--dir",
        type=Path,
        default=Path("data"),
        help="Directory containing the DOCX files (default: data/)",
    )
    args = parser.parse_args()

    logger.warning(
        "Rebuilding vector store — all existing embeddings will be erased"
    )

    try:
        results = ingest(args.dir, reset=True)
        for name, count in results.items():
            print(f"  \u2713 {name}: {count} chunks")
        total = sum(results.values())
        print(f"\u2713 Rebuild complete: {total} chunks total")
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
