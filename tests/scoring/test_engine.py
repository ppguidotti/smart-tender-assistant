from scoring.engine import compute_scoring
from scoring.models import (
    RequirementCategory,
    RequirementStatus,
    RequirementType,
    ScoringDecision,
    ScoringRequirement,
)


def test_conditional_go_with_partial_and_preferential_gap():
    requirements = [
        ScoringRequirement(
            id="REQ-001",
            title="Certificazione ISO 27001",
            category=RequirementCategory.COMPLIANCE,
            status=RequirementStatus.COVERED,
            type=RequirementType.BLOCKING,
            weight=3,
        ),
        ScoringRequirement(
            id="REQ-002",
            title="Disponibilità stock licenze",
            category=RequirementCategory.TECHNICAL,
            status=RequirementStatus.PARTIAL,
            type=RequirementType.BLOCKING,
            weight=2,
        ),
        ScoringRequirement(
            id="REQ-003",
            title="Referenze settore pubblico",
            category=RequirementCategory.QUALIFICATION,
            status=RequirementStatus.GAP,
            type=RequirementType.PREFERENTIAL,
            weight=1,
        ),
        ScoringRequirement(
            id="REQ-004",
            title="Documentazione amministrativa completa",
            category=RequirementCategory.ADMINISTRATIVE,
            status=RequirementStatus.COVERED,
            type=RequirementType.INFO,
            weight=1,
        ),
    ]

    result = compute_scoring(requirements)

    assert result.final_score == 62
    assert result.decision == ScoringDecision.CONDITIONAL_GO
    assert len(result.blocking_gaps) == 0
    assert len(result.partial_requirements) == 1
    assert "preferenziale" in " ".join(result.rationale)


def test_no_go_when_blocking_gap_exists():
    requirements = [
        ScoringRequirement(
            id="REQ-001",
            title="Iscrizione MePA obbligatoria",
            category=RequirementCategory.QUALIFICATION,
            status=RequirementStatus.GAP,
            type=RequirementType.BLOCKING,
            weight=3,
        ),
        ScoringRequirement(
            id="REQ-002",
            title="Documentazione amministrativa completa",
            category=RequirementCategory.ADMINISTRATIVE,
            status=RequirementStatus.COVERED,
            type=RequirementType.INFO,
            weight=1,
        ),
    ]

    result = compute_scoring(requirements)

    assert result.decision == ScoringDecision.NO_GO
    assert result.final_score <= 40
    assert len(result.blocking_gaps) == 1