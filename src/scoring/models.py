from enum import Enum
from pydantic import BaseModel


class RequirementCategory(str, Enum):
    TECHNICAL = "TECHNICAL"
    COMPLIANCE = "COMPLIANCE"
    QUALIFICATION = "QUALIFICATION"
    ADMINISTRATIVE = "ADMINISTRATIVE"


class RequirementStatus(str, Enum):
    COVERED = "COVERED"
    PARTIAL = "PARTIAL"
    GAP = "GAP"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class RequirementType(str, Enum):
    BLOCKING = "BLOCKING"
    PREFERENTIAL = "PREFERENTIAL"
    INFO = "INFO"


class ScoringRequirement(BaseModel):
    id: str
    title: str
    category: RequirementCategory
    status: RequirementStatus
    type: RequirementType
    weight: float = 1.0
    source: str | None = None
    note: str | None = None


class ScoringBreakdown(BaseModel):
    technical: int
    compliance: int
    qualification: int
    administrative: int


class ScoringDecision(str, Enum):
    GO = "GO"
    CONDITIONAL_GO = "CONDITIONAL_GO"
    NO_GO = "NO_GO"


class ScoringResult(BaseModel):
    final_score: int
    decision: ScoringDecision
    breakdown: ScoringBreakdown
    blocking_gaps: list[ScoringRequirement]
    partial_requirements: list[ScoringRequirement]
    rationale: list[str]
    recommended_actions: list[str]