"""B2 — Requirement Extractor orchestration.

Two-stage pipeline on a tender's parsed documents:
  1. per-document LLM extraction (``llm.extract_raw_requirements``)
  2. cross-document dedup/merge (``merge.consolidate``)
then map onto the ``Requirement`` contract and assemble an ``ExtractionResult``.
"""

from __future__ import annotations

import time
from collections import Counter
from uuid import UUID

from smart_tender_assistant.config import Settings, get_settings
from smart_tender_assistant.extraction.llm import extract_raw_requirements
from smart_tender_assistant.extraction.mapping import map_requirements
from smart_tender_assistant.extraction.merge import consolidate
from smart_tender_assistant.models.schemas import (
    ExtractionResult,
    ExtractionSummary,
    ParsedDocument,
    Requirement,
)

DEFAULT_MIN_CONFIDENCE = 0.7


def extract_requirements(
    documents: list[ParsedDocument],
    tender_id: UUID,
    *,
    min_confidence: float = DEFAULT_MIN_CONFIDENCE,
    settings: Settings | None = None,
) -> ExtractionResult:
    """Extract, merge and classify requirements for all documents of a tender.

    Args:
        documents: ``ParsedDocument`` list (output of B1) for one tender.
        tender_id: Tender these documents belong to.
        min_confidence: Requirements below this land in ``needs_review``.
        settings: Optional override; defaults to the cached ``Settings``.

    Returns:
        An ``ExtractionResult`` validated against the contract.
    """
    settings = settings or get_settings()
    started = time.perf_counter()

    per_document = [
        {
            "document": doc.source.filename,
            "requirements": extract_raw_requirements(doc.raw_text, settings=settings),
        }
        for doc in documents
    ]

    merged = consolidate(per_document, settings=settings)
    requirements = map_requirements(merged, tender_id, documents)
    duration_ms = int((time.perf_counter() - started) * 1000)

    needs_review = [r.requirement_id for r in requirements if r.confidence < min_confidence]

    return ExtractionResult(
        tender_id=tender_id,
        requirements=requirements,
        extraction_summary=_summary(requirements, duration_ms),
        needs_review=needs_review,
    )


def _summary(requirements: list[Requirement], duration_ms: int) -> ExtractionSummary:
    by_category = Counter(r.category for r in requirements)
    by_type = Counter(r.type for r in requirements)
    avg_conf = (
        round(sum(r.confidence for r in requirements) / len(requirements), 4)
        if requirements
        else 0.0
    )
    return ExtractionSummary(
        total_requirements=len(requirements),
        by_category=dict(by_category),
        by_type=dict(by_type),
        avg_confidence=avg_conf,
        processing_duration_ms=duration_ms,
    )
