"""Ponte frontend → pipeline backend (B1 ingestion + B2 extraction).

Esegue la pipeline reale sui file caricati dall'utente e produce un
``BandoHTML`` (dominio del prototipo) pronto da mostrare nel dettaglio gara.

MVP in-process: il frontend chiama direttamente i moduli backend (stesso
processo Python). Quando esistera' B8, questo modulo verra' sostituito da una
chiamata HTTP senza toccare le pagine.

Gli import backend sono lazy (dentro le funzioni) cosi' la semplice navigazione
del frontend non paga il costo di openai/tika/numpy.
"""

from __future__ import annotations

import tempfile
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from uuid import uuid4

from smart_tender_assistant.frontend.models.schemas import BandoHTML, RequisitoBando


@dataclass(frozen=True)
class UploadedDoc:
    """File caricato, indipendente dal tipo Streamlit (testabile)."""

    name: str
    data: bytes


@dataclass(frozen=True)
class BandoMeta:
    nome: str
    ente: str
    valore: float
    scadenza: str
    giorni_mancanti: int
    canale: str
    cpv: str


def _requirement_to_requisito(req: object) -> RequisitoBando:
    """Requirement (contratto B2) → RequisitoBando (dominio HTML del frontend).

    B4 (gap analysis) non e' ancora girato: lo stato e' "parziale" ("estratto,
    da analizzare"), tranne gli INFORMATIVO. La nota riporta la citazione
    originale — e' la traceability che vogliamo mostrare.
    """
    tipo = req.type  # type: ignore[attr-defined]
    is_info = tipo == "INFORMATIVO"
    citation = (req.text_original or "").strip()  # type: ignore[attr-defined]
    nota = (
        f'Fonte: "{citation[:140]}{"…" if len(citation) > 140 else ""}"' if citation else None
    )
    return RequisitoBando(
        id=req.requirement_id,  # type: ignore[attr-defined]
        cat=req.category,  # type: ignore[attr-defined]
        txt=req.text_normalized,  # type: ignore[attr-defined]
        fonte=Path(req.source.document_name).stem[:24],  # type: ignore[attr-defined]
        tipo=tipo,
        status="info" if is_info else "parziale",
        ml="Estratto da B2 — gap analysis non eseguita",
        mt="gr" if is_info else "am",
        nota=nota,
    )


_MATCH_TO_COVERAGE = {
    "FULL": "covered",
    "PARTIAL": "partially_covered",
    "NONE": "not_covered",
    "UNKNOWN": "unknown",
}


def _apply_gap_analysis(requisiti, result, tender_id, say) -> None:
    """Run B4 and overwrite each RequisitoBando status with the real coverage."""
    from smart_tender_assistant.gap_analysis import analyze_requirements
    from smart_tender_assistant.gap_analysis.mapping import coverage_to_requisito_status

    say("B4 — gap analysis contro il profilo aziendale…")
    response = analyze_requirements(result.requirements, tender_id, progress=say)

    type_by_id = {r.requirement_id: r.type for r in result.requirements}
    rq_by_id = {rq.id: rq for rq in requisiti}
    for gr in response.results:
        rq = rq_by_id.get(gr.requirement_id)
        if rq is None:
            continue
        coverage = _MATCH_TO_COVERAGE.get(gr.match_status, "unknown")
        status, mt, ml = coverage_to_requisito_status(
            type_by_id.get(gr.requirement_id, "ESCLUDENTE"), coverage
        )
        rq.status, rq.mt, rq.ml = status, mt, ml
        if gr.reasoning:
            rq.nota = gr.reasoning

    s = response.summary
    say(
        f"B4 completato: {s.full_match} coperti · {s.partial_match} parziali · "
        f"{s.no_match} gap · {s.unknown} da verificare (livello {s.overall_gap_level})."
    )


def analyze_uploads(
    docs: list[UploadedDoc],
    meta: BandoMeta,
    *,
    progress=None,
) -> BandoHTML:
    """Esegue B1+B2 sui file caricati e costruisce il ``BandoHTML`` risultante.

    Args:
        docs: file caricati (nome + bytes).
        meta: metadati del bando inseriti dall'utente.
        progress: callback opzionale ``(str) -> None`` per messaggi di avanzamento.

    Returns:
        Un ``BandoHTML`` con ``requisiti`` popolati e ``analisi_completa=True``.

    Raises:
        ValueError: se non viene passato alcun file.
        Exception: errori B1 (Tika non raggiungibile, file vuoto) o B2 (LLM).
    """
    if not docs:
        raise ValueError("Nessun file da analizzare.")

    # Import lazy: pesanti e necessari solo quando si lancia davvero l'analisi.
    from smart_tender_assistant.extraction import extract_requirements
    from smart_tender_assistant.ingestion import parse_files

    def _say(msg: str) -> None:
        if progress is not None:
            progress(msg)

    tender_id = uuid4()
    tmpdir = Path(tempfile.mkdtemp(prefix="sta_upload_"))
    paths: list[Path] = []
    for d in docs:
        p = tmpdir / d.name
        p.write_bytes(d.data)
        paths.append(p)

    _say(f"B1 — parsing di {len(paths)} documento/i con Tika…")
    parsed = parse_files(paths, tender_id)

    _say("B2 — estrazione requisiti con LLM…")
    result = extract_requirements(parsed, tender_id)

    requisiti = [_requirement_to_requisito(r) for r in result.requirements]
    _say(f"B2 completato: {len(requisiti)} requisiti estratti.")

    # B4 — gap analysis contro il profilo aziendale (best-effort: se fallisce,
    # i requisiti restano nello stato 'parziale/da analizzare' di B2).
    try:
        _apply_gap_analysis(requisiti, result, tender_id, _say)
    except Exception as exc:  # KB assente, LLM giù… non bloccare l'upload
        _say(f"B4 saltata ({exc}) — requisiti senza copertura")

    return BandoHTML(
        id=f"live-{tender_id.hex[:8]}",
        nome=meta.nome,
        short_nome=meta.nome[:24],
        ente=meta.ente,
        valore=meta.valore,
        scadenza=meta.scadenza,
        giorni_mancanti=meta.giorni_mancanti,
        canale=meta.canale,
        cpv=meta.cpv,
        status="analisi",
        uploaded_at=date.today().strftime("%d/%m/%Y"),
        files=[d.name for d in docs],
        analisi_completa=True,
        gng_confermato=False,
        requisiti=requisiti,
        checklist=[],
    )
