"""B4 orchestration — requirements → GapAnalysisResponse.

Loads the company KB once, runs coverage on each requirement, maps to the
``GapAnalysisResult`` contract and assembles the summary.
"""

from __future__ import annotations

from collections.abc import Callable
from uuid import UUID

from smart_tender_assistant.config import Settings, get_settings
from smart_tender_assistant.gap_analysis.engine import coverage_for_requirement
from smart_tender_assistant.gap_analysis.kb import CompanyKB, get_company_kb
from smart_tender_assistant.gap_analysis.mapping import (
    coverage_to_result,
    requirement_to_engine_dict,
)
from smart_tender_assistant.models.schemas import (
    GapAnalysisResponse,
    GapAnalysisResult,
    GapAnalysisSummary,
    Requirement,
)


def analyze_requirements(
    requirements: list[Requirement],
    tender_id: UUID,
    *,
    kb: CompanyKB | None = None,
    settings: Settings | None = None,
    progress: Callable[[str], None] | None = None,
) -> GapAnalysisResponse:
    """Run gap analysis for all requirements of a tender against the company KB."""
    settings = settings or get_settings()
    kb = kb or get_company_kb(settings)

    results: list[GapAnalysisResult] = []
    total = len(requirements)
    for i, req in enumerate(requirements, start=1):
        if progress is not None:
            progress(f"B4 — copertura {i}/{total}: {req.requirement_id}")
        engine_req = requirement_to_engine_dict(req)
        try:
            coverage = coverage_for_requirement(engine_req, kb, settings=settings)
        except Exception as exc:  # fail soft per-requirement, never abort the batch
            coverage = {
                "requirement_id": req.requirement_id,
                "coverage_status": "unknown",
                "gap_description": f"Analisi non riuscita: {exc}",
            }
        results.append(coverage_to_result(req, coverage))

    return GapAnalysisResponse(
        tender_id=tender_id, results=results, summary=_summary(results)
    )


def _summary(results: list[GapAnalysisResult]) -> GapAnalysisSummary:
    full = sum(1 for r in results if r.match_status == "FULL")
    partial = sum(1 for r in results if r.match_status == "PARTIAL")
    none = sum(1 for r in results if r.match_status == "NONE")
    unknown = sum(1 for r in results if r.match_status == "UNKNOWN")
    critical = sum(1 for r in results if r.gap is not None and r.gap.severity == "CRITICAL")
    review = sum(1 for r in results if r.needs_human_review)
    total = len(results)

    if total == 0 or critical > 0 or unknown >= total * 0.5:
        level = "HIGH"
    elif partial > 0 or unknown > 0:
        level = "MEDIUM"
    else:
        level = "LOW"

    return GapAnalysisSummary(
        total_analyzed=total,
        full_match=full,
        partial_match=partial,
        no_match=none,
        unknown=unknown,
        critical_gaps=critical,
        sent_to_review_queue=review,
        overall_gap_level=level,
    )
