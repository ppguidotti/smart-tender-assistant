"""Map the engine's ``coverage_status`` onto the project contracts.

``coverage_status`` (covered / partially_covered / not_covered / unknown) →
  * ``GapAnalysisResult`` (match_status + Gap severity per §B4 business rule)
  * dashboard ``RequisitoBando`` status tuple (coperto / parziale / gap-*).
"""

from __future__ import annotations

from smart_tender_assistant.models.schemas import Gap, GapAnalysisResult, MatchStatus, Requirement

_STATUS_TO_MATCH: dict[str, MatchStatus] = {
    "covered": "FULL",
    "partially_covered": "PARTIAL",
    "not_covered": "NONE",
    "unknown": "UNKNOWN",
}
_MATCH_CONFIDENCE = {"FULL": 0.9, "PARTIAL": 0.6, "NONE": 0.55, "UNKNOWN": 0.3}


def requirement_to_engine_dict(req: Requirement) -> dict:
    """Adapt a contract ``Requirement`` to the engine's input dict."""
    return {
        "id": req.requirement_id,
        "text": req.text_normalized or req.text_original,
        "categoria": req.category,
        "tipo": req.type,
        "obbligatorio": req.type == "ESCLUDENTE",
    }


def _severity(req_type: str, match_status: MatchStatus) -> str | None:
    """Business rule from docs/block_architecture.md §B4."""
    if req_type == "INFORMATIVO" or match_status == "FULL":
        return None
    if req_type == "ESCLUDENTE":
        return "CRITICAL" if match_status == "NONE" else "MAJOR"
    return "MINOR"  # PREFERENZIALE


def coverage_to_result(req: Requirement, coverage: dict) -> GapAnalysisResult:
    status = coverage.get("coverage_status", "unknown")
    match_status: MatchStatus = _STATUS_TO_MATCH.get(status, "UNKNOWN")
    description = coverage.get("gap_description", "") or ""
    severity = _severity(req.type, match_status)

    gap = None
    if severity is not None:
        gap = Gap(
            severity=severity,
            description=description or "Evidenza non sufficiente nella knowledge base.",
            remediation_suggestion="",
            remediation_effort="MEDIUM",
        )

    needs_review = match_status == "UNKNOWN" or (req.type == "ESCLUDENTE" and match_status != "FULL")
    return GapAnalysisResult(
        requirement_id=req.requirement_id,
        match_status=match_status,
        match_confidence=_MATCH_CONFIDENCE[match_status],
        gap=gap,
        needs_human_review=needs_review,
        reasoning=description,
    )


def coverage_to_requisito_status(req_type: str, coverage_status: str) -> tuple[str, str, str]:
    """Return ``(status, mt, ml)`` for the dashboard ``RequisitoBando`` view."""
    if req_type == "INFORMATIVO":
        return "info", "gr", "Informativo"
    if coverage_status == "covered":
        return "coperto", "gn", "Coperto da profilo aziendale ✓"
    if coverage_status == "partially_covered":
        return "parziale", "am", "Parzialmente coperto — verifica"
    if coverage_status == "not_covered":
        if req_type == "ESCLUDENTE":
            return "gap-esc", "rd", "Gap escludente — evidenza assente"
        return "gap-pref", "rd", "Gap preferenziale — evidenza assente"
    return "parziale", "am", "Evidenza non trovata — da verificare"  # unknown
