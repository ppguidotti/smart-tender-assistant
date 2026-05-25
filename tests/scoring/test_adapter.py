from scoring.adapter import gap_analysis_to_scoring
from scoring.models import RequirementStatus, RequirementType


def test_gap_analysis_unknown_maps_to_blocking_gap():
    gap_analysis = {
        "requirement_gap_analysis": [
            {
                "requirement_id": "REQ_001",
                "coverage_status": "unknown",
                "gap_description": "Evidence not found",
            }
        ]
    }

    requirements = gap_analysis_to_scoring(gap_analysis)

    assert len(requirements) == 1
    assert requirements[0].id == "REQ_001"
    assert requirements[0].status == RequirementStatus.GAP
    assert requirements[0].type == RequirementType.BLOCKING
    assert requirements[0].note == "Evidence not found"