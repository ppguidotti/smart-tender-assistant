"""B1 — Document Ingestor.

Apache Tika as a universal MIME router. For the MVP we ship the ``tika_raw``
strategy sanctioned in ``docs/block_architecture.md`` §B1: every file becomes a
single ``ParsedDocument`` with one ``OTHER`` section holding the full text.
Specialised PDF/DOCX/spreadsheet strategies can be slotted in later without
changing the ``ParsedDocument`` contract.

This is the cleaned-up, application-grade evolution of ``extract_with_tika`` /
``join_text`` from the original Colab notebook (``tca_1_2.py``).
"""

from __future__ import annotations

import hashlib
import re
import time
from datetime import UTC, datetime
from pathlib import Path
from uuid import NAMESPACE_URL, UUID, uuid5

from smart_tender_assistant.config import Settings, get_settings
from smart_tender_assistant.models.schemas import (
    ParsedDocument,
    ProcessingStats,
    Section,
    SourceMetadata,
)

# Document UUIDs are derived from the content hash so re-ingesting the same file
# yields the same document_id (idempotency, per §2 of the architecture doc).
_DOC_NAMESPACE = uuid5(NAMESPACE_URL, "smart-tender-assistant/document")


class IngestionError(RuntimeError):
    """Raised when a file cannot be parsed into a usable ParsedDocument."""


def _clean_text(text: str) -> str:
    """Normalise whitespace and smart quotes for the ``text_clean`` field."""
    text = text.replace(" ", " ").replace("“", '"').replace("”", '"')
    text = text.replace("‘", "'").replace("’", "'")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _document_id(file_hash: str, tender_id: UUID) -> UUID:
    return uuid5(_DOC_NAMESPACE, f"{tender_id}:{file_hash}")


def parse_file(
    file_path: str | Path,
    tender_id: UUID,
    *,
    settings: Settings | None = None,
) -> ParsedDocument:
    """Parse a single file into a ``ParsedDocument`` using Apache Tika.

    Args:
        file_path: Local path to the document (any Tika-supported format).
        tender_id: Tender the document belongs to.
        settings: Optional override; defaults to the cached ``Settings``.

    Returns:
        A ``ParsedDocument`` (``tika_raw`` strategy).

    Raises:
        IngestionError: if the file is missing or Tika extracts no text.
    """
    from tika import parser as tika_parser  # lazy: heavy import + JVM warm-up

    settings = settings or get_settings()
    path = Path(file_path)
    if not path.is_file():
        raise IngestionError(f"File not found: {path}")

    raw_bytes = path.read_bytes()
    file_hash = hashlib.sha256(raw_bytes).hexdigest()

    started = time.perf_counter()
    parsed = tika_parser.from_file(
        str(path),
        serverEndpoint=settings.tika_server_url,
        requestOptions={"timeout": settings.tika_timeout_seconds},
    )
    duration_ms = int((time.perf_counter() - started) * 1000)

    content = (parsed.get("content") or "").strip()
    metadata: dict = parsed.get("metadata") or {}
    if not content:
        raise IngestionError(
            f"Tika extracted no text from {path.name} (EMPTY_DOCUMENT). "
            "The file may be a scanned PDF needing OCR."
        )

    mime_type = _first(metadata.get("Content-Type")) or "application/octet-stream"
    language = _first(metadata.get("language")) or "it"
    page_count = _to_int(_first(metadata.get("xmpTPg:NPages")))

    document_id = _document_id(file_hash, tender_id)
    text_clean = _clean_text(content)

    section = Section(
        section_id="full-text",
        type="OTHER",
        title=path.name,
        order=0,
        page_start=1 if page_count else None,
        page_end=page_count,
        text_raw=content,
        text_clean=text_clean,
    )

    return ParsedDocument(
        document_id=document_id,
        tender_id=tender_id,
        source=SourceMetadata(
            filename=path.name,
            mime_type=mime_type,
            detected_format=mime_type,
            pages=page_count,
            language=language,
            hash_sha256=file_hash,
            extracted_at=datetime.now(UTC),
            extraction_strategy="tika_raw",
            tika_metadata={k: _first(v) for k, v in metadata.items()},
        ),
        sections=[section],
        raw_text=content,
        warnings=[],
        processing_stats=ProcessingStats(
            duration_ms=duration_ms,
            strategy_used="tika_raw",
        ),
    )


def parse_files(
    file_paths: list[str | Path],
    tender_id: UUID,
    *,
    settings: Settings | None = None,
) -> list[ParsedDocument]:
    """Parse every file of a tender. Missing/empty files raise immediately (fail loud)."""
    settings = settings or get_settings()
    return [parse_file(p, tender_id, settings=settings) for p in file_paths]


def _first(value: object) -> str | None:
    """Tika returns some metadata fields as lists; take the first scalar."""
    if isinstance(value, list):
        return str(value[0]) if value else None
    if value is None:
        return None
    return str(value)


def _to_int(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None
