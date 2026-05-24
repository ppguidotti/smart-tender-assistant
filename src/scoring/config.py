from scoring.models import RequirementCategory, RequirementStatus


STATUS_SCORES: dict[RequirementStatus, float] = {
    RequirementStatus.COVERED: 1.0,
    RequirementStatus.PARTIAL: 0.5,
    RequirementStatus.GAP: 0.0,
    RequirementStatus.NOT_APPLICABLE: 1.0,
}


CATEGORY_WEIGHTS: dict[RequirementCategory, float] = {
    RequirementCategory.TECHNICAL: 0.35,
    RequirementCategory.COMPLIANCE: 0.30,
    RequirementCategory.QUALIFICATION: 0.20,
    RequirementCategory.ADMINISTRATIVE: 0.15,
}


GO_THRESHOLD = 75
CONDITIONAL_GO_THRESHOLD = 50
BLOCKING_GAP_SCORE_CAP = 40