"""Map merged raw requirements onto the project ``Requirement`` contract.

The Colab notebook uses a participation-centric taxonomy
(``economico_finanziario``, ``certificazione``, …). The application contract
(``docs/block_architecture.md`` §B2) uses
``QUALIFICAZIONE / NORMATIVA / TECNICA / AMMINISTRATIVA`` crossed with
``ESCLUDENTE / PREFERENZIALE / INFORMATIVO``. This module bridges the two and
fills in ``SourceLocation`` for traceability, preserving the raw LLM fields in
``extraction_notes`` so nothing is lost.
"""

from __future__ import annotations

from smart_tender_assistant.models.schemas import (
    ParsedDocument,
    Requirement,
    RequirementCategory,
    SourceLocation,
)

# Colab categoria → project category. Participation requirements map mostly to
# QUALIFICAZIONE; certifications/legal to NORMATIVA; technical capability to TECNICA.
_CATEGORY_MAP: dict[str, RequirementCategory] = {
    "economico_finanziario": "QUALIFICAZIONE",
    "idoneita_professionale": "QUALIFICAZIONE",
    "esperienza": "QUALIFICAZIONE",
    "tecnico_professionale": "TECNICA",
    "certificazione": "NORMATIVA",
    "legale": "NORMATIVA",
    "altro": "AMMINISTRATIVA",
}

_CONFIDENCE_MAP: dict[str, float] = {"alta": 0.95, "media": 0.75, "bassa": 0.5}


def _build_doc_index(documents: list[ParsedDocument]) -> dict[str, ParsedDocument]:
    return {doc.source.filename: doc for doc in documents}


def _source_location(raw: dict, doc_index: dict[str, ParsedDocument]) -> SourceLocation:
    documenti: list[str] = raw.get("documenti") or []
    primary_name = documenti[0] if documenti else next(iter(doc_index), "unknown")
    doc = doc_index.get(primary_name)
    citation = raw.get("fonte_testuale", "") or ""

    char_start: int | None = None
    char_end: int | None = None
    if doc and citation:
        idx = doc.raw_text.find(citation)
        if idx >= 0:
            char_start, char_end = idx, idx + len(citation)

    return SourceLocation(
        document_id=doc.document_id if doc else _placeholder_uuid(),
        document_name=primary_name,
        section_id="full-text",
        section_title=primary_name,
        page=1,  # tika_raw has no reliable page map; refined by specialised B1 strategies
        char_start=char_start,
        char_end=char_end,
    )


def _placeholder_uuid():
    from uuid import NAMESPACE_URL, uuid5

    return uuid5(NAMESPACE_URL, "smart-tender-assistant/unknown-document")


def _extraction_notes(raw: dict) -> str:
    parts = [
        f"categoria_llm={raw.get('categoria')}",
        f"tipo_llm={raw.get('tipo')}",
        f"confidenza_llm={raw.get('confidenza')}",
    ]
    if raw.get("valore") is not None:
        parts.append(f"valore={raw['valore']} {raw.get('unita') or ''}".strip())
    if raw.get("occorrenze", 1) > 1:
        parts.append(f"occorrenze={raw['occorrenze']}")
    docs = raw.get("documenti") or []
    if len(docs) > 1:
        parts.append(f"documenti={', '.join(docs)}")
    return "; ".join(parts)


def to_requirement(raw: dict, index: int, tender_id, doc_index: dict[str, ParsedDocument]) -> Requirement:
    """Convert one merged raw requirement into a contract ``Requirement``."""
    categoria = (raw.get("categoria") or "altro").lower()
    confidenza = (raw.get("confidenza") or "bassa").lower()
    description = raw.get("descrizione", "")
    citation = raw.get("fonte_testuale", "") or description

    return Requirement(
        requirement_id=f"REQ-{index:03d}",
        tender_id=tender_id,
        source=_source_location(raw, doc_index),
        text_original=citation,
        text_normalized=description,
        category=_CATEGORY_MAP.get(categoria, "AMMINISTRATIVA"),
        # The Colab schema has no INFORMATIVO; mandatory→ESCLUDENTE, optional→PREFERENZIALE.
        type="ESCLUDENTE" if raw.get("obbligatorio", True) else "PREFERENZIALE",
        subcategory=raw.get("tipo") or None,
        confidence=_CONFIDENCE_MAP.get(confidenza, 0.5),
        extraction_notes=_extraction_notes(raw),
    )


def map_requirements(merged: list[dict], tender_id, documents: list[ParsedDocument]) -> list[Requirement]:
    """Map all merged raw requirements to the ``Requirement`` contract."""
    doc_index = _build_doc_index(documents)
    return [to_requirement(raw, i, tender_id, doc_index) for i, raw in enumerate(merged, start=1)]
