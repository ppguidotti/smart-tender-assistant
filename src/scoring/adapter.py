from scoring.models import ScoringRequirement


def mock_to_scoring(
    requirements: list[ScoringRequirement],
) -> list[ScoringRequirement]:
    return requirements