"""Helpers UI riusabili per il prototipo STCA.

Mirror del JavaScript di `docs/STCA_Platform_v2.html`:
- `calc_score()` — calcolo deterministico Go/No-Go (M2/M3/Qual)
- `gap_count()` — conteggi gap escludenti/preferenziali/parziali
- `chk_stats()` — progresso checklist
- `aggregate_gaps()` — gap aggregati cross-bandi per la Roadmap
"""

from __future__ import annotations

from dataclasses import dataclass

from smart_tender_assistant.frontend.models.schemas import (
    BandoHTML,
    ChecklistItemHTML,
    RequisitoBando,
)


@dataclass(frozen=True)
class ScoreResult:
    """Risultato del calcolo score (mirror di calcScore() in HTML)."""

    score: int
    ra: str  # "GO" | "GO_CONDIZIONALE" | "NO_GO"
    m2: int
    m3c: int
    m3q: int
    gap_esc: int
    gap_pref: int
    override: bool = False


def calc_score(reqs: list[RequisitoBando]) -> ScoreResult:
    """Calcola lo score composito M2*0.30 + M3c*0.40 + M3q*0.30 — mirror dell'HTML."""
    if not reqs:
        return ScoreResult(score=0, ra="NO_GO", m2=0, m3c=0, m3q=100, gap_esc=0, gap_pref=0)

    # M2 — copertura normativa
    norm = [r for r in reqs if r.cat == "NORMATIVA"]
    cov = sum(1 for r in norm if r.status in ("coperto", "automatico"))
    m2 = round(cov / len(norm) * 100) if norm else 100

    # M3 — gap analysis (escl. amministrative)
    all_reqs = [r for r in reqs if r.cat != "AMMINISTRATIVA"]
    gap_esc = sum(1 for r in all_reqs if r.status == "gap-esc")
    gap_pref = sum(1 for r in all_reqs if r.status == "gap-pref")
    m3c = max(0, 100 - gap_esc * 20 - gap_pref * 5)

    # M3 — qualificazione economica (fixed demo)
    m3q = 100

    score = round(m2 * 0.30 + m3c * 0.40 + m3q * 0.30)

    if gap_esc > 0:
        return ScoreResult(
            score=0, ra="NO_GO", m2=m2, m3c=m3c, m3q=m3q,
            gap_esc=gap_esc, gap_pref=gap_pref, override=True,
        )
    ra = "GO" if score >= 75 else "GO_CONDIZIONALE" if score >= 55 else "NO_GO"
    return ScoreResult(
        score=score, ra=ra, m2=m2, m3c=m3c, m3q=m3q,
        gap_esc=gap_esc, gap_pref=gap_pref,
    )


@dataclass(frozen=True)
class GapCount:
    esc: int
    pref: int
    parc: int


def gap_count(reqs: list[RequisitoBando]) -> GapCount:
    """Conteggio gap escludenti/preferenziali/parziali."""
    return GapCount(
        esc=sum(1 for r in reqs if r.status == "gap-esc"),
        pref=sum(1 for r in reqs if r.status == "gap-pref"),
        parc=sum(1 for r in reqs if r.status == "parziale"),
    )


@dataclass(frozen=True)
class ChecklistStats:
    done: int
    total: int
    pct: int


def chk_stats(items: list[ChecklistItemHTML]) -> ChecklistStats:
    """Statistiche progresso checklist."""
    done = sum(1 for x in items if x.done)
    total = len(items)
    pct = round(done / total * 100) if total else 0
    return ChecklistStats(done=done, total=total, pct=pct)


@dataclass(frozen=True)
class AggregatedGap:
    testo: str
    tipo: str
    status: str
    count: int
    bandi: list[str]


def aggregate_gaps(bandi: list[BandoHTML]) -> list[AggregatedGap]:
    """Aggregazione gap cross-bandi (mirror di getAggregatedGaps())."""
    grouped: dict[str, dict] = {}
    for b in bandi:
        for r in b.requisiti:
            if r.status in ("gap-pref", "gap-esc", "parziale"):
                key = r.txt[:40]
                if key not in grouped:
                    grouped[key] = {
                        "testo": r.txt, "tipo": r.tipo, "status": r.status,
                        "count": 0, "bandi": [],
                    }
                grouped[key]["count"] += 1
                if b.id not in grouped[key]["bandi"]:
                    grouped[key]["bandi"].append(b.id)
    return sorted(
        [AggregatedGap(**v) for v in grouped.values()],
        key=lambda g: g.count, reverse=True,
    )


# ---------------------------------------------------------------------------
# Helpers session-state per bandi (carica + modifica in memoria)
# ---------------------------------------------------------------------------

import streamlit as st

from smart_tender_assistant.frontend.services.api_client import get_api_client

_BANDI_KEY = "stca_bandi"


def load_bandi() -> list[BandoHTML]:
    """Carica i bandi in session_state, completi di requisiti+checklist per quello di analisi.

    Solo il bando con `analisi_completa=True` ha i sub-dettagli caricati per default.
    """
    if _BANDI_KEY not in st.session_state:
        client = get_api_client()
        bandi = client.list_bandi_html()
        for b in bandi:
            if b.analisi_completa:
                b.requisiti = client.get_bando_requisiti(b.id)
                b.checklist = client.get_bando_checklist(b.id)
        st.session_state[_BANDI_KEY] = bandi
    return st.session_state[_BANDI_KEY]


def get_bando(bid: str) -> BandoHTML | None:
    return next((b for b in load_bandi() if b.id == bid), None)


def save_bandi(bandi: list[BandoHTML]) -> None:
    st.session_state[_BANDI_KEY] = bandi
