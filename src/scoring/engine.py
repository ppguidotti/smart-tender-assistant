from scoring.config import (
    BLOCKING_GAP_SCORE_CAP,
    CATEGORY_WEIGHTS,
    CONDITIONAL_GO_THRESHOLD,
    GO_THRESHOLD,
    STATUS_SCORES,
)
from scoring.explanations import build_rationale, build_recommended_actions
from scoring.models import (
    RequirementCategory,
    RequirementType,
    RequirementStatus,
    ScoringBreakdown,
    ScoringDecision,
    ScoringRequirement,
    ScoringResult,
)


def _score_category(
    requirements: list[ScoringRequirement],
    category: RequirementCategory,
) -> int:
    category_requirements = [
        r for r in requirements if r.category == category
    ]

    if not category_requirements:
        return 0

    weighted_sum = 0.0
    total_weight = 0.0

    for requirement in category_requirements:
        score = STATUS_SCORES[requirement.status]
        weighted_sum += score * requirement.weight
        total_weight += requirement.weight

    if total_weight == 0:
        return 100

    return round((weighted_sum / total_weight) * 100)


def compute_scoring(
    requirements: list[ScoringRequirement],
    business_score: int = 70,
) -> ScoringResult:
    blocking_gaps = [
        r for r in requirements
        if r.type == RequirementType.BLOCKING
        and r.status == RequirementStatus.GAP
    ]

    preferential_gaps = [
        r for r in requirements
        if r.type == RequirementType.PREFERENTIAL
        and r.status == RequirementStatus.GAP
    ]

    partial_requirements = [
        r for r in requirements
        if r.status == RequirementStatus.PARTIAL
    ]

    breakdown = ScoringBreakdown(
        technical=_score_category(
            requirements,
            RequirementCategory.TECHNICAL,
        ),
        compliance=_score_category(
            requirements,
            RequirementCategory.COMPLIANCE,
        ),
        qualification=_score_category(
            requirements,
            RequirementCategory.QUALIFICATION,
        ),
        administrative=_score_category(
            requirements,
            RequirementCategory.ADMINISTRATIVE,
        ),
    )

    final_score = (
        breakdown.technical * CATEGORY_WEIGHTS[RequirementCategory.TECHNICAL]
        + breakdown.compliance * CATEGORY_WEIGHTS[RequirementCategory.COMPLIANCE]
        + breakdown.qualification * CATEGORY_WEIGHTS[RequirementCategory.QUALIFICATION]
        + breakdown.administrative * CATEGORY_WEIGHTS[RequirementCategory.ADMINISTRATIVE]
    )

    final_score = round(final_score)

    if blocking_gaps:
        final_score = min(final_score, BLOCKING_GAP_SCORE_CAP)
        decision = ScoringDecision.NO_GO
    elif final_score >= GO_THRESHOLD:
        decision = ScoringDecision.GO
    elif final_score >= CONDITIONAL_GO_THRESHOLD:
        decision = ScoringDecision.CONDITIONAL_GO
    else:
        decision = ScoringDecision.NO_GO

    rationale = build_rationale(
        blocking_gaps,
        partial_requirements,
        preferential_gaps,
    )

    recommended_actions = build_recommended_actions(
        blocking_gaps,
        partial_requirements,
        preferential_gaps,
    )

    return ScoringResult(
        final_score=final_score,
        decision=decision,
        breakdown=breakdown,
        blocking_gaps=blocking_gaps,
        partial_requirements=partial_requirements,
        rationale=rationale,
        recommended_actions=recommended_actions,
    )