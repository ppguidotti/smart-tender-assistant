"""Backend data contracts for B1 (Document Ingestor) and B2 (Requirement Extractor).

Mirrors ``docs/block_architecture.md`` §3 (shared types), §B1 (``ParsedDocument``)
and §B2 (``Requirement`` / ``ExtractionResult``). Pydantic v2, ``extra="forbid"``.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

# ---------------------------------------------------------------------------
# §3 — Shared data contracts
# ---------------------------------------------------------------------------


class SchemaVersion(BaseModel, frozen=True):
    major: int = 1
    minor: int = 0


class Reference(BaseModel, frozen=True):
    """Normative or documentary reference."""

    law: str
    article: str | None = None
    url: str | None = None


class SourceLocation(BaseModel, frozen=True):
    """Pointer back to the source document — backbone of traceability."""

    document_id: UUID
    document_name: str
    section_id: str | None = None
    section_title: str | None = None
    page: int
    char_start: int | None = None
    char_end: int | None = None


class Penalty(BaseModel, frozen=True):
    type: Literal["FIXED", "PERCENTAGE", "PER_DAY", "PER_MILLE"]
    value: float
    base: str
    cap_pct: float | None = None
    triggers: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# §B1 — ParsedDocument family
# ---------------------------------------------------------------------------


class Table(BaseModel):
    model_config = ConfigDict(extra="forbid")

    table_id: str
    caption: str | None = None
    headers: list[str] = Field(default_factory=list)
    rows: list[list[str]] = Field(default_factory=list)
    page: int | None = None
    source_format: Literal["NATIVE_TABLE", "EXTRACTED_FROM_PDF", "SPREADSHEET_SHEET"] = (
        "EXTRACTED_FROM_PDF"
    )


class Section(BaseModel):
    model_config = ConfigDict(extra="forbid")

    section_id: str
    type: Literal[
        "ARTICLE",
        "PREAMBLE",
        "ANNEX",
        "TABLE_BLOCK",
        "EMAIL_HEADER",
        "EMAIL_BODY",
        "SPREADSHEET_SHEET",
        "OTHER",
    ]
    title: str | None = None
    order: int
    page_start: int | None = None
    page_end: int | None = None
    text_raw: str
    text_clean: str
    subsections: list[Section] = Field(default_factory=list)
    tables: list[Table] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class SourceMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    filename: str
    mime_type: str
    detected_format: str
    pages: int | None = None
    language: str = "it"
    hash_sha256: str
    extracted_at: datetime
    extraction_strategy: str = "tika_raw"
    tika_metadata: dict = Field(default_factory=dict)
    is_embedded: bool = False
    parent_document_id: UUID | None = None


class ProcessingStats(BaseModel):
    model_config = ConfigDict(extra="forbid")

    duration_ms: int
    strategy_used: str = "tika_raw"
    ocr_used: bool = False
    ocr_pages: list[int] = Field(default_factory=list)
    tables_extracted: int = 0
    embedded_files_count: int = 0
    warnings_count: int = 0


class ParsedDocument(BaseModel):
    """Format-agnostic output of B1. Stable contract toward B2."""

    model_config = ConfigDict(extra="forbid")

    schema_version: SchemaVersion = SchemaVersion()
    document_id: UUID
    tender_id: UUID
    source: SourceMetadata
    sections: list[Section] = Field(default_factory=list)
    raw_text: str
    warnings: list[str] = Field(default_factory=list)
    processing_stats: ProcessingStats
    embedded_documents: list[UUID] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# §B2 — Requirement family
# ---------------------------------------------------------------------------

RequirementCategory = Literal["QUALIFICAZIONE", "NORMATIVA", "TECNICA", "AMMINISTRATIVA"]
RequirementType = Literal["ESCLUDENTE", "PREFERENZIALE", "INFORMATIVO"]


class EvidenceRequest(BaseModel, frozen=True):
    evidence_type: str
    description: str
    mandatory: bool


class Requirement(BaseModel):
    """Single requirement extracted from a tender. Compatible with the frontend mirror."""

    model_config = ConfigDict(extra="forbid")

    requirement_id: str
    tender_id: UUID
    source: SourceLocation
    text_original: str
    text_normalized: str
    category: RequirementCategory
    type: RequirementType
    subcategory: str | None = None
    normative_references: list[Reference] = Field(default_factory=list)
    required_evidences: list[EvidenceRequest] = Field(default_factory=list)
    deadline: date | str | None = None
    penalty: Penalty | None = None
    confidence: float
    extraction_notes: str = ""

    @field_validator("confidence")
    @classmethod
    def _confidence_in_range(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError("confidence must be in [0, 1]")
        return v


class ExtractionSummary(BaseModel, frozen=True):
    total_requirements: int
    by_category: dict[str, int]
    by_type: dict[str, int]
    avg_confidence: float
    processing_duration_ms: int


class ExtractionResult(BaseModel):
    """Output of B2 — list of requirements plus summary and review flags."""

    model_config = ConfigDict(extra="forbid")

    schema_version: SchemaVersion = SchemaVersion()
    tender_id: UUID
    requirements: list[Requirement] = Field(default_factory=list)
    extraction_summary: ExtractionSummary
    needs_review: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# §B4 — Gap Analyzer
# ---------------------------------------------------------------------------

MatchStatus = Literal["FULL", "PARTIAL", "NONE", "UNKNOWN"]
GapSeverity = Literal["CRITICAL", "MAJOR", "MINOR"]


class Gap(BaseModel, frozen=True):
    severity: GapSeverity
    description: str
    remediation_suggestion: str = ""
    remediation_effort: Literal["LOW", "MEDIUM", "HIGH"] = "MEDIUM"
    remediation_time_estimate: str | None = None


class GapAnalysisResult(BaseModel):
    """Coverage of a single requirement against the company knowledge base."""

    model_config = ConfigDict(extra="forbid")

    requirement_id: str
    match_status: MatchStatus
    match_confidence: float
    matching_evidences: list[dict] = Field(default_factory=list)
    gap: Gap | None = None
    needs_human_review: bool = False
    reasoning: str = ""

    @field_validator("match_confidence")
    @classmethod
    def _conf_in_range(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError("match_confidence must be in [0, 1]")
        return v


class GapAnalysisSummary(BaseModel, frozen=True):
    total_analyzed: int
    full_match: int
    partial_match: int
    no_match: int
    unknown: int
    critical_gaps: int
    sent_to_review_queue: int = 0
    overall_gap_level: Literal["LOW", "MEDIUM", "HIGH"] = "MEDIUM"


class GapAnalysisResponse(BaseModel):
    """Output of B4 — per-requirement coverage plus summary."""

    model_config = ConfigDict(extra="forbid")

    schema_version: SchemaVersion = SchemaVersion()
    tender_id: UUID
    results: list[GapAnalysisResult] = Field(default_factory=list)
    summary: GapAnalysisSummary
