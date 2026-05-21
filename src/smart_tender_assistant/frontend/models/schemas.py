"""Pydantic v2 models per il frontend Smart Tender Assistant.

Mirror dei contratti definiti in docs/block_architecture.md §3-§4.
Solo i tipi che il frontend consuma — non include ParsedDocument (roba B1).
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

# ---------------------------------------------------------------------------
# §3 — Shared data contracts
# ---------------------------------------------------------------------------


class SchemaVersion(BaseModel, frozen=True):
    major: int = 1
    minor: int = 0


class Reference(BaseModel, frozen=True):
    """Riferimento normativo o documentale."""

    law: str
    article: str | None = None
    url: str | None = None


class SourceLocation(BaseModel, frozen=True):
    """Puntatore alla fonte originale — cuore della traceability."""

    document_id: UUID
    document_name: str
    section_id: str | None = None
    section_title: str | None = None
    page: int
    char_start: int | None = None
    char_end: int | None = None


class Money(BaseModel, frozen=True):
    amount: float
    currency: str = "EUR"
    is_net: bool


class Penalty(BaseModel, frozen=True):
    type: Literal["FIXED", "PERCENTAGE", "PER_DAY", "PER_MILLE"]
    value: float
    base: str
    cap_pct: float | None = None
    triggers: list[str]


class Evidence(BaseModel):
    """Singola evidenza del profilo aziendale."""

    evidence_id: str
    type: Literal[
        "CERTIFICATION", "REFERENCE", "COMPETENCY", "FINANCIAL", "DOCUMENT", "PARTNERSHIP"
    ]
    title: str
    description: str
    valid_from: date | None = None
    valid_until: date | None = None
    proof_attachments: list[str] = Field(default_factory=list)
    metadata: dict[str, str] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# B2 — Requirement Extractor
# ---------------------------------------------------------------------------

RequirementCategory = Literal["QUALIFICAZIONE", "NORMATIVA", "TECNICA", "AMMINISTRATIVA"]
RequirementType = Literal["ESCLUDENTE", "PREFERENZIALE", "INFORMATIVO"]


class EvidenceRequest(BaseModel, frozen=True):
    evidence_type: str
    description: str
    mandatory: bool


class Requirement(BaseModel):
    """Singolo requisito estratto da un bando."""

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
    def confidence_in_range(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError("confidence must be in [0, 1]")
        return v


class ExtractionSummary(BaseModel, frozen=True):
    total_requirements: int
    by_category: dict[str, int]
    by_type: dict[str, int]
    avg_confidence: float
    processing_duration_ms: int


# ---------------------------------------------------------------------------
# B4 — Gap Analyzer
# ---------------------------------------------------------------------------

MatchStatus = Literal["FULL", "PARTIAL", "NONE", "UNKNOWN"]
GapSeverity = Literal["CRITICAL", "MAJOR", "MINOR"]


class Gap(BaseModel, frozen=True):
    severity: GapSeverity
    description: str
    remediation_suggestion: str
    remediation_effort: Literal["LOW", "MEDIUM", "HIGH"]
    remediation_time_estimate: str | None = None


class GapAnalysisResult(BaseModel):
    """Risultato dell'analisi gap per un singolo requisito."""

    requirement_id: str
    match_status: MatchStatus
    match_confidence: float
    matching_evidences: list[Evidence] = Field(default_factory=list)
    gap: Gap | None = None
    needs_human_review: bool = False
    reasoning: str

    @field_validator("match_confidence")
    @classmethod
    def match_confidence_in_range(cls, v: float) -> float:
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
    sent_to_review_queue: int


# ---------------------------------------------------------------------------
# B5 — Scoring Engine
# ---------------------------------------------------------------------------

DecisionType = Literal["GO", "GO_WITH_RESERVATIONS", "NO_GO"]


class HardGateResult(BaseModel, frozen=True):
    passed: bool
    blocking_requirements: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)


class SoftScoreResult(BaseModel, frozen=True):
    technical_score_estimate: float | None = None
    max_score_available: float | None = None
    competitiveness: Literal["HIGH", "MEDIUM", "LOW"]


class RiskFactor(BaseModel, frozen=True):
    type: str
    severity: Literal["LOW", "MEDIUM", "HIGH"]
    description: str
    source: SourceLocation


class RiskAssessment(BaseModel):
    overall_risk: Literal["LOW", "MEDIUM", "HIGH"]
    max_penalty_exposure_pct: float
    auto_termination_clauses: list[str] = Field(default_factory=list)
    vendor_lock_in_detected: bool
    sla_complexity: Literal["LOW", "MEDIUM", "HIGH"]
    risk_factors: list[RiskFactor] = Field(default_factory=list)


class DecisionSummary(BaseModel, frozen=True):
    total_requirements: int
    met_full: int
    met_partial: int
    unmet: int
    critical_gaps: int
    avg_confidence: float


class Recommendation(BaseModel, frozen=True):
    priority: Literal["HIGH", "MEDIUM", "LOW"]
    text: str
    targets_requirement_id: str | None = None


class NextAction(BaseModel, frozen=True):
    action: str
    deadline: date | None = None
    owner_role: str


class TenderDecision(BaseModel):
    """Decisione GO/NO-GO prodotta da B5."""

    schema_version: SchemaVersion = SchemaVersion()
    tender_id: UUID
    decision: DecisionType
    decision_timestamp: datetime
    hard_gate: HardGateResult
    soft_score: SoftScoreResult | None = None
    risk_assessment: RiskAssessment
    summary: DecisionSummary
    rationale: str
    recommendations: list[Recommendation] = Field(default_factory=list)
    next_actions: list[NextAction] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# B6 — Report / Dashboard types
# ---------------------------------------------------------------------------


class DocumentTodo(BaseModel, frozen=True):
    """Documento da preparare per la partecipazione."""

    document_type: str
    description: str
    template_available: bool
    template_path: str | None = None
    source_requirement_id: str
    deadline: date | None = None
    owner_role: str


class AuditEntry(BaseModel, frozen=True):
    """Singola voce nell'audit trail."""

    timestamp: datetime
    actor: str
    action: str
    detail: str


# ---------------------------------------------------------------------------
# B7 — Review Queue
# ---------------------------------------------------------------------------


class ReviewContext(BaseModel):
    requirement: Requirement | None = None
    candidate_evidences: list[Evidence] = Field(default_factory=list)
    auto_suggestion: str | None = None


class ReviewItem(BaseModel):
    item_id: UUID
    item_type: Literal["AMBIGUOUS_REQUIREMENT", "UNKNOWN_EVIDENCE_MATCH", "NEW_REQUIREMENT_PATTERN"]
    tender_id: UUID
    payload: dict[str, str] = Field(default_factory=dict)
    created_at: datetime
    priority: Literal["HIGH", "MEDIUM", "LOW"]
    deadline: datetime | None = None
    context: ReviewContext


class ReviewDecision(BaseModel):
    item_id: UUID
    decided_by: str
    decided_at: datetime
    action: Literal["APPROVE_AS_SUGGESTED", "MODIFY", "REJECT", "ADD_NEW_EVIDENCE"]
    modified_payload: dict[str, str] | None = None
    reviewer_notes: str
    propagate_to_profile: bool


# ---------------------------------------------------------------------------
# Frontend-specific view models
# ---------------------------------------------------------------------------

AnalysisStatus = Literal[
    "QUEUED",
    "PARSING",
    "EXTRACTING",
    "ANALYZING",
    "SCORING",
    "REPORTING",
    "COMPLETED",
    "FAILED",
]


class TenderListItem(BaseModel):
    """Riga nella tabella home — vista aggregata di una gara."""

    tender_id: UUID
    name: str
    status: AnalysisStatus
    decision: DecisionType | None = None
    created_at: datetime
    completed_at: datetime | None = None
    total_requirements: int = 0
    critical_gaps: int = 0
    score: float | None = None
    estimated_value: Money | None = None
