from scoring.models import RequirementType, ScoringRequirement


def build_rationale(
    blocking_gaps: list[ScoringRequirement],
    partial_requirements: list[ScoringRequirement],
    preferential_gaps: list[ScoringRequirement] | None = None,
) -> list[str]:
    preferential_gaps = preferential_gaps or []
    rationale: list[str] = []

    if blocking_gaps:
        rationale.append(
            f"{len(blocking_gaps)} requisito/i bloccante/i risultano non soddisfatti."
        )

    if partial_requirements:
        rationale.append(
            f"{len(partial_requirements)} requisito/i risultano parzialmente coperti e richiedono verifica."
        )

    if preferential_gaps:
        rationale.append(
            f"{len(preferential_gaps)} requisito/i preferenziale/i non risultano coperti e riducono il punteggio tecnico."
        )

    if not blocking_gaps and not partial_requirements and not preferential_gaps:
        rationale.append("Non emergono gap bloccanti o requisiti parziali rilevanti.")

    return rationale


def build_recommended_actions(
    blocking_gaps: list[ScoringRequirement],
    partial_requirements: list[ScoringRequirement],
    preferential_gaps: list[ScoringRequirement] | None = None,
) -> list[str]:
    preferential_gaps = preferential_gaps or []
    actions: list[str] = []

    for requirement in blocking_gaps:
        actions.append(f"Risolvi gap bloccante: {requirement.title}")

    for requirement in partial_requirements:
        actions.append(f"Verifica copertura parziale: {requirement.title}")

    for requirement in preferential_gaps:
        actions.append(f"Valuta impatto del gap preferenziale: {requirement.title}")

    if not actions:
        actions.append("Procedere con la preparazione dell’offerta.")

    return actions