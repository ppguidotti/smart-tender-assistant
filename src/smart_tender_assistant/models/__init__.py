"""Shared data contracts for the backend pipeline (B1–B2).

Canonical Pydantic v2 models mirroring ``docs/block_architecture.md`` §3–§4.
The frontend keeps its own read-only mirror in
``smart_tender_assistant.frontend.models.schemas``; the ``Requirement`` family
here is field-for-field compatible with it so the two can be merged later.
"""

from smart_tender_assistant.models.schemas import (
    EvidenceRequest,
    ExtractionResult,
    ExtractionSummary,
    Gap,
    GapAnalysisResponse,
    GapAnalysisResult,
    GapAnalysisSummary,
    MatchStatus,
    ParsedDocument,
    Penalty,
    ProcessingStats,
    Reference,
    Requirement,
    RequirementCategory,
    RequirementType,
    SchemaVersion,
    Section,
    SourceLocation,
    SourceMetadata,
    Table,
)

__all__ = [
    "EvidenceRequest",
    "ExtractionResult",
    "ExtractionSummary",
    "Gap",
    "GapAnalysisResponse",
    "GapAnalysisResult",
    "GapAnalysisSummary",
    "MatchStatus",
    "ParsedDocument",
    "Penalty",
    "ProcessingStats",
    "Reference",
    "Requirement",
    "RequirementCategory",
    "RequirementType",
    "SchemaVersion",
    "Section",
    "SourceLocation",
    "SourceMetadata",
    "Table",
]
