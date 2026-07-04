"""DOCX document parser — extracts semantic chunks with section context."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import docx

# Matches numbered headings: "1.", "2.1", "4.1.2 Texto", etc.
_HEADING_RE = re.compile(r"^\d+(?:\.\d+)*\s+\S")
# Matches the document slug prefix: "DOC1", "DOC2", ...
_SLUG_RE = re.compile(r"(doc\d+)", re.IGNORECASE)

MAX_CHUNK_CHARS = 900
MIN_CHUNK_CHARS = 80


@dataclass
class DocumentChunk:
    """A chunk of text from a policy document, ready for embedding and storage."""

    id: str
    document_name: str
    document_slug: str
    section: str
    text: str
    chunk_index: int
    char_count: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        self.char_count = len(self.text)


class DocxParser:
    """
    Parses a DOCX file into semantic chunks suitable for vector indexing.

    Strategy:
    - Paragraphs are grouped into sections delimited by headings.
    - A heading is identified by its Word style name (Heading 1/2/3) or by
      a leading numbered pattern ("1.", "2.1 …").
    - Sections shorter than MAX_CHUNK_CHARS become a single chunk.
    - Longer sections are split at paragraph boundaries with the section
      heading repeated at the start of each sub-chunk for context.
    """

    def parse(self, file_path: Path) -> list[DocumentChunk]:
        document = docx.Document(str(file_path))
        slug = self._slug(file_path.name)

        paragraphs: list[tuple[str, str]] = [
            (p.text.strip(), p.style.name if p.style else "Normal")
            for p in document.paragraphs
            if p.text.strip()
        ]

        # ── Group paragraphs into sections ────────────────────────────────
        sections: list[tuple[str, list[str]]] = []
        current_heading = "Introducción"
        current_body: list[str] = []

        for text, style in paragraphs:
            if self._is_heading(text, style):
                if current_body:
                    sections.append((current_heading, current_body))
                current_heading = text
                current_body = []
            else:
                current_body.append(text)

        if current_body:
            sections.append((current_heading, current_body))

        # ── Build chunks ───────────────────────────────────────────────────
        chunks: list[DocumentChunk] = []
        chunk_index = 0

        for heading, body in sections:
            section_text = heading + "\n" + "\n".join(body)

            if len(section_text) <= MAX_CHUNK_CHARS:
                if len(section_text) >= MIN_CHUNK_CHARS:
                    chunks.append(
                        DocumentChunk(
                            id=f"{slug}_{chunk_index:04d}",
                            document_name=file_path.name,
                            document_slug=slug,
                            section=heading[:100],
                            text=section_text,
                            chunk_index=chunk_index,
                        )
                    )
                    chunk_index += 1
            else:
                for sub_text in self._split_section(heading, body):
                    chunks.append(
                        DocumentChunk(
                            id=f"{slug}_{chunk_index:04d}",
                            document_name=file_path.name,
                            document_slug=slug,
                            section=heading[:100],
                            text=sub_text,
                            chunk_index=chunk_index,
                        )
                    )
                    chunk_index += 1

        return chunks

    # ── helpers ────────────────────────────────────────────────────────────

    @staticmethod
    def _is_heading(text: str, style: str) -> bool:
        if style.startswith("Heading"):
            return True
        return bool(_HEADING_RE.match(text))

    @staticmethod
    def _split_section(heading: str, body: list[str]) -> list[str]:
        """Split a long section into sub-chunks, each prefixed with the heading."""
        sub_chunks: list[str] = []
        current: list[str] = [heading]
        current_len = len(heading)

        for para in body:
            # +1 for the newline separator
            if current_len + len(para) + 1 > MAX_CHUNK_CHARS and len(current) > 1:
                sub_chunks.append("\n".join(current))
                current = [heading, para]
                current_len = len(heading) + len(para) + 1
            else:
                current.append(para)
                current_len += len(para) + 1

        if len(current) > 1:  # more than just the heading
            sub_chunks.append("\n".join(current))

        return sub_chunks or [heading]

    @staticmethod
    def _slug(filename: str) -> str:
        """'DOC1_Manual_de_Beneficios.docx' → 'doc1'"""
        match = _SLUG_RE.search(filename)
        return match.group(1).lower() if match else Path(filename).stem.lower()[:20]
