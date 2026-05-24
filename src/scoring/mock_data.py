from scoring.models import (
    RequirementCategory,
    RequirementStatus,
    RequirementType,
    ScoringRequirement,
)


MOCK_REQUIREMENTS = [
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