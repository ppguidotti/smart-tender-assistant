from scoring.models import (
    RequirementCategory,
    RequirementStatus,
    RequirementType,
    ScoringRequirement,
)


COVERAGE_STATUS_MAP = {
    "covered": RequirementStatus.COVERED,
    "partially_covered": RequirementStatus.PARTIAL,
    "not_covered": RequirementStatus.GAP,
    "unknown": RequirementStatus.GAP,
}


def gap_analysis_to_scoring(
    gap_analysis: dict,
) -> list[ScoringRequirement]:
    requirements: list[ScoringRequirement] = []

    for item in gap_analysis.get("requirement_gap_analysis", []):
        coverage_status = item.get("coverage_status", "unknown")

        requirements.append(
            ScoringRequirement(
                id=item["requirement_id"],
                title=item["requirement_id"],
                category=RequirementCategory.QUALIFICATION,
                status=COVERAGE_STATUS_MAP.get(
                    coverage_status,
                    RequirementStatus.PARTIAL,
                ),
                type=RequirementType.BLOCKING,
                weight=1.0,
                note=item.get("gap_description"),
            )
        )

    return requirements


def mock_to_scoring(
    requirements: list[ScoringRequirement],
) -> list[ScoringRequirement]:
    return requirements