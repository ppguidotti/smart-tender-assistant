"""Pagina dettaglio gara — header, tab Requisiti, tab Gap Analysis, tab Rischi."""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import timezone

import plotly.graph_objects as go
import streamlit as st

from smart_tender_assistant.frontend.models.schemas import (
    AdminChecklist,
    AuditEntry,
    DocumentTodo,
    GapAnalysisResult,
    RiskAssessment,
    RiskFactor,
    Requirement,
    TenderDecision,
    TenderListItem,
)
from smart_tender_assistant.frontend.services.api_client import get_api_client
from smart_tender_assistant.frontend.ui.components.badges import (
    decision_badge,
    effort_badge,
    match_status_badge_html,
    requirement_type_badge,
    risk_severity_badge,
    severity_badge_html,
)
from smart_tender_assistant.frontend.ui.components.cards import evidence_card
from smart_tender_assistant.frontend.ui.components.citations import source_citation
from smart_tender_assistant.frontend.ui.theme import (
    CATEGORY_COLORS,
    COLOR_BG_SECONDARY,
    COLOR_BORDER,
    COLOR_GO,
    COLOR_GO_RESERVATIONS,
    COLOR_NO_GO,
    COLOR_PARTIAL,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    inject_custom_css,
)

# ---------------------------------------------------------------------------
# Mesi italiani (fallback senza locale di sistema)
# ---------------------------------------------------------------------------

_MESI_IT = {
    1: "gennaio",
    2: "febbraio",
    3: "marzo",
    4: "aprile",
    5: "maggio",
    6: "giugno",
    7: "luglio",
    8: "agosto",
    9: "settembre",
    10: "ottobre",
    11: "novembre",
    12: "dicembre",
}

_TYPE_FILTER_LABELS: dict[str, str] = {
    "ESCLUDENTE": "Escludente",
    "PREFERENZIALE": "Preferenziale",
    "INFORMATIVO": "Informativo",
}

_CATEGORY_LABELS: dict[str, str] = {
    "QUALIFICAZIONE": "Qualificazione",
    "NORMATIVA": "Normativa",
    "TECNICA": "Tecnica",
    "AMMINISTRATIVA": "Amministrativa",
}

# Ordine canonico delle categorie
_CATEGORY_ORDER = ["QUALIFICAZIONE", "NORMATIVA", "TECNICA", "AMMINISTRATIVA"]


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


def _find_tender_metadata(tender_id: str) -> TenderListItem | None:
    """Cerca i metadati della gara nella lista gare."""
    client = get_api_client()
    tenders = client.list_tenders()
    for t in tenders:
        if str(t.tender_id) == tender_id:
            return t
    return None


def _load_requirements(tender_id: str) -> list[Requirement]:
    """Carica i requisiti della gara."""
    client = get_api_client()
    return client.get_requirements(tender_id)


def _load_decision(tender_id: str) -> TenderDecision | None:
    """Carica la decisione della gara, None se non disponibile."""
    client = get_api_client()
    try:
        return client.get_decision(tender_id)
    except (FileNotFoundError, Exception):
        return None


def _load_admin_checklist(tender_id: str) -> AdminChecklist | None:
    """Carica la checklist amministrativa, None se B6 non ancora girato."""
    client = get_api_client()
    try:
        return client.get_admin_checklist(tender_id)
    except Exception:
        return None


def _load_audit_trail(tender_id: str) -> list[AuditEntry]:
    """Carica l'audit trail della gara, lista vuota se non disponibile."""
    client = get_api_client()
    try:
        return client.get_audit_trail(tender_id)
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------


def _render_header(
    tender: TenderListItem,
    decision: TenderDecision | None,
) -> None:
    """Renderizza l'header della pagina con titolo, badge, score e azioni."""
    col_header, col_actions = st.columns([4, 1])

    with col_header:
        st.title(tender.name)

        cols = st.columns([1.5, 1, 1, 2.5])

        with cols[0]:
            if decision:
                decision_badge(decision.decision, large=True)
            elif tender.decision:
                decision_badge(tender.decision, large=True)
            else:
                st.markdown(
                    f'<span style="color:{COLOR_TEXT_SECONDARY}">In analisi…</span>',
                    unsafe_allow_html=True,
                )

        with cols[1]:
            if tender.score is not None:
                st.markdown(f"### {tender.score:.0f}/100")
            else:
                st.markdown(
                    f'<span style="color:{COLOR_TEXT_SECONDARY};font-size:1.2rem">—</span>',
                    unsafe_allow_html=True,
                )

        with cols[2]:
            short_id = str(tender.tender_id).split("-")[0]
            st.code(short_id, language=None)

        with cols[3]:
            ts = decision.decision_timestamp if decision else tender.created_at
            mese = _MESI_IT.get(ts.month, str(ts.month))
            st.markdown(
                f'<span style="color:{COLOR_TEXT_SECONDARY};font-size:0.9rem">'
                f"{ts.day} {mese} {ts.year}, {ts.strftime('%H:%M')}</span>",
                unsafe_allow_html=True,
            )

    with col_actions:
        if st.button("📄 Scarica report PDF", width="stretch"):
            st.info("Funzionalità in arrivo — generazione report PDF con B6.")


# ---------------------------------------------------------------------------
# Tab Requisiti
# ---------------------------------------------------------------------------


def _render_requirement_row(req: Requirement, idx: int) -> None:
    """Renderizza una singola riga di requisito dentro un expander."""
    col_id, col_type, col_text, col_cite, col_conf = st.columns([0.8, 1.2, 4, 2, 1.2])

    with col_id:
        st.markdown(
            f'<code style="font-size:0.75rem;color:{COLOR_TEXT_SECONDARY}">'
            f"{req.requirement_id}</code>",
            unsafe_allow_html=True,
        )

    with col_type:
        requirement_type_badge(req.type)

    with col_text:
        text = req.text_normalized
        if len(text) > 80:
            text = text[:77] + "…"
        st.markdown(f'<span style="font-size:0.85rem">{text}</span>', unsafe_allow_html=True)

    with col_cite:
        source_citation(
            source=req.source,
            text_original=req.text_original,
            normative_refs=req.normative_references or None,
            key=f"cite_{req.requirement_id}_{idx}",
        )

    with col_conf:
        pct = int(req.confidence * 100)
        warning = " ⚠" if req.confidence < 0.7 else ""
        st.progress(req.confidence, text=f"{pct}%{warning}")


def _render_tab_requisiti(requirements: list[Requirement]) -> None:
    """Renderizza il contenuto del tab Requisiti con filtri e expander per categoria."""
    # Filtro per tipo
    type_options = ["ESCLUDENTE", "PREFERENZIALE", "INFORMATIVO"]
    selected_types: list[str] = st.multiselect(
        "Filtra per tipo",
        options=type_options,
        format_func=lambda x: _TYPE_FILTER_LABELS.get(x, x),
        default=[],
        help="Lascia vuoto per mostrare tutti i tipi.",
    )

    # Filtra
    filtered = requirements
    if selected_types:
        filtered = [r for r in filtered if r.type in selected_types]

    if not filtered:
        st.info("Nessun requisito corrisponde ai filtri selezionati.")
        return

    # Raggruppa per categoria
    grouped: dict[str, list[Requirement]] = defaultdict(list)
    for req in filtered:
        grouped[req.category].append(req)

    # Render expander per ogni categoria (in ordine canonico)
    idx = 0
    for cat_key in _CATEGORY_ORDER:
        reqs = grouped.get(cat_key, [])
        if not reqs:
            continue

        cat_label = _CATEGORY_LABELS.get(cat_key, cat_key)
        cat_color = CATEGORY_COLORS.get(cat_key, "#64748B")

        with st.expander(
            f"**{cat_label}** ({len(reqs)})",
            expanded=True,
        ):
            # Header sottile per l'expander
            st.markdown(
                f'<div style="display:flex;padding:0.2rem 0;'
                f"border-bottom:2px solid {cat_color};"
                f"margin-bottom:0.4rem;font-size:0.7rem;"
                f'color:{COLOR_TEXT_SECONDARY};font-weight:600">'
                f'<div style="flex:0.8">ID</div>'
                f'<div style="flex:1.2">TIPO</div>'
                f'<div style="flex:4">TESTO</div>'
                f'<div style="flex:2">FONTE</div>'
                f'<div style="flex:1.2">CONFIDENZA</div>'
                f"</div>",
                unsafe_allow_html=True,
            )

            for req in reqs:
                _render_requirement_row(req, idx)
                idx += 1


def _render_tab_gap_analysis(
    gaps: list[GapAnalysisResult], requirements: list[Requirement]
) -> None:
    """Renderizza la tab Gap Analysis."""
    if not gaps:
        st.info("Nessun risultato di gap analysis trovato.")
        return

    # Map requisiti per join veloce
    req_by_id = {r.requirement_id: r for r in requirements}

    # Filtro Categoria
    all_categories = list(_CATEGORY_ORDER)
    selected_categories = st.multiselect(
        "Filtra per categoria del requisito",
        options=all_categories,
        format_func=lambda x: _CATEGORY_LABELS.get(x, x),
        default=all_categories,
        key="gap_category_filter",
    )

    # Filtra gap in base alla categoria del requisito
    filtered_gaps = []
    for g in gaps:
        req = req_by_id.get(g.requirement_id)
        if req and req.category in selected_categories:
            filtered_gaps.append((g, req))

    if not filtered_gaps:
        st.info("Nessun gap corrisponde ai filtri selezionati.")
        return

    # Raggruppa per severity o FULL MATCH
    grouped = {
        "CRITICAL": [],
        "MAJOR": [],
        "MINOR": [],
        "FULL_MATCH": [],
    }

    for g, req in filtered_gaps:
        if g.match_status == "FULL" or g.gap is None:
            grouped["FULL_MATCH"].append((g, req))
        else:
            grouped[g.gap.severity].append((g, req))

    # Render sezioni
    _render_gap_section("CRITICAL", "Gap CRITICI", grouped["CRITICAL"], default_expanded=True)
    _render_gap_section("MAJOR", "Gap MAJOR", grouped["MAJOR"], default_expanded=True)
    _render_gap_section("MINOR", "Gap MINOR", grouped["MINOR"], default_expanded=True)
    
    # Sezione Full Match nascosta di default
    if grouped["FULL_MATCH"]:
        _render_gap_section(
            "FULL_MATCH",
            "Requisiti Soddisfatti (Nessun Gap)",
            grouped["FULL_MATCH"],
            default_expanded=False,
        )


def _render_gap_section(
    severity: str,
    title: str,
    items: list[tuple[GapAnalysisResult, Requirement]],
    default_expanded: bool = True,
) -> None:
    """Renderizza una sezione espandibile di gap."""
    if not items:
        return

    with st.expander(f"**{title}** ({len(items)})", expanded=default_expanded):
        for g, req in items:
            with st.container(border=True):
                # Header card
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{req.requirement_id}** — {req.text_normalized}")
                with col2:
                    st.markdown("<div style='text-align:right'>", unsafe_allow_html=True)
                    st.markdown(match_status_badge_html(g.match_status), unsafe_allow_html=True)
                    if g.gap:
                        st.markdown("<span style='margin-left:5px;'></span>", unsafe_allow_html=True)
                        st.markdown(severity_badge_html(g.gap.severity), unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                # Evidenze proposte
                with st.expander(f"Evidenze proposte ({len(g.matching_evidences)})"):
                    if g.matching_evidences:
                        for ev in g.matching_evidences:
                            evidence_card(ev)
                    else:
                        st.write("Nessuna evidenza proposta.")

                # Spiegazione del sistema
                with st.expander("Spiegazione del sistema"):
                    st.write(g.reasoning)
                
                # Remediation se presente
                if g.gap:
                    st.info(f"**🛠 Suggerimento:** {g.gap.remediation_suggestion}")
                    
                    c1, c2, _c3 = st.columns([1, 1, 2])
                    with c1:
                        st.write("Effort:")
                        effort_badge(g.gap.remediation_effort)
                    with c2:
                        if g.gap.remediation_time_estimate:
                            st.write(f"⏱ **{g.gap.remediation_time_estimate}**")
                
                # Badge In Revisione
                if g.needs_human_review:
                    st.markdown("<div style='margin-top:0.5rem'></div>", unsafe_allow_html=True)
                    if st.button("⚠ In revisione (HITL)", key=f"review_{req.requirement_id}", help="Vai alla coda di revisione"):
                        st.success("Navigazione alla Review Queue (in arrivo)")


# ---------------------------------------------------------------------------
# Tab Rischi
# ---------------------------------------------------------------------------

_RISK_COLORS: dict[str, str] = {
    "LOW": COLOR_GO,
    "MEDIUM": COLOR_GO_RESERVATIONS,
    "HIGH": COLOR_NO_GO,
}

_RISK_LEVEL_LABELS: dict[str, str] = {
    "LOW": "BASSO",
    "MEDIUM": "MEDIO",
    "HIGH": "ALTO",
}

_SLA_LABELS: dict[str, str] = {
    "LOW": "Bassa",
    "MEDIUM": "Media",
    "HIGH": "Alta",
}

_SEV_SCORE: dict[str, float] = {"LOW": 33.0, "MEDIUM": 66.0, "HIGH": 100.0}
_SEV_ORDER: dict[str, int] = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}


def _hex_to_rgb(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    return f"{int(h[0:2], 16)}, {int(h[2:4], 16)}, {int(h[4:6], 16)}"


def _build_radar_data(risk: RiskAssessment) -> tuple[list[str], list[float]]:
    """Restituisce (labels, values) normalizzati 0-100 per il radar chart."""
    labels: list[str] = [
        "Penali esposte",
        "Clausole auto-ris.",
        "Vendor lock-in",
        "Complessità SLA",
    ]
    values: list[float] = [
        min(risk.max_penalty_exposure_pct / 30.0 * 100.0, 100.0),
        min(len(risk.auto_termination_clauses) / 3.0 * 100.0, 100.0),
        100.0 if risk.vendor_lock_in_detected else 0.0,
        _SEV_SCORE.get(risk.sla_complexity, 0.0),
    ]

    # Assi dinamici: un asse per tipo unico, max severity per tipo
    type_score: dict[str, float] = {}
    for rf in risk.risk_factors:
        v = _SEV_SCORE.get(rf.severity, 0.0)
        type_score[rf.type] = max(type_score.get(rf.type, 0.0), v)

    sorted_types = sorted(type_score.items(), key=lambda x: x[1], reverse=True)

    # Cap a 5 assi dinamici — i restanti collassano in "Altri rischi"
    if len(sorted_types) > 5:
        top5 = sorted_types[:5]
        others_val = max(v for _, v in sorted_types[5:])
        top5.append(("altri_rischi", others_val))
        sorted_types = top5

    for rf_type, val in sorted_types:
        labels.append(rf_type.replace("_", " ").capitalize())
        values.append(val)

    return labels, values


def _render_radar_chart(risk: RiskAssessment) -> None:
    labels, values = _build_radar_data(risk)
    color = _RISK_COLORS.get(risk.overall_risk, COLOR_PARTIAL)

    fig = go.Figure(
        data=go.Scatterpolar(
            r=values,
            theta=labels,
            fill="toself",
            fillcolor=f"rgba({_hex_to_rgb(color)}, 0.18)",
            line=dict(color=color, width=2),
            marker=dict(size=5, color=color),
            name="Rischio",
        )
    )
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                range=[0, 100],
                visible=True,
                tickvals=[25, 50, 75, 100],
                tickfont=dict(size=8, color=COLOR_TEXT_SECONDARY),
                gridcolor="#D3D1C7",
                linecolor="#D3D1C7",
            ),
            angularaxis=dict(
                tickfont=dict(size=11, color=COLOR_TEXT_PRIMARY),
                gridcolor="#D3D1C7",
                linecolor="#D3D1C7",
            ),
            bgcolor="#FFFFFF",
        ),
        paper_bgcolor="#FFFFFF",
        margin=dict(l=50, r=50, t=20, b=20),
        height=370,
        showlegend=False,
        font=dict(color=COLOR_TEXT_PRIMARY),
    )
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


def _build_synthesis(risk: RiskAssessment) -> str:
    sentences: list[str] = []

    high_count = sum(1 for rf in risk.risk_factors if rf.severity == "HIGH")
    if high_count:
        sentences.append(
            f"{high_count} fattori di rischio HIGH richiedono verifica prima della presentazione"
        )

    n_clauses = len(risk.auto_termination_clauses)
    if n_clauses:
        sentences.append(
            f"Presenti {n_clauses} clausole di auto-risoluzione contrattuale"
        )

    if risk.vendor_lock_in_detected:
        sentences.append("Rilevato rischio vendor lock-in")

    if not sentences:
        return "Nessun fattore critico rilevato."

    sentences[0] = sentences[0][0].upper() + sentences[0][1:]
    return ". ".join(sentences) + "."


def _render_overall_risk_card(risk: RiskAssessment) -> None:
    color = _RISK_COLORS.get(risk.overall_risk, COLOR_PARTIAL)
    label = _RISK_LEVEL_LABELS.get(risk.overall_risk, risk.overall_risk)

    st.markdown(
        f'<div style="background:{color};color:#fff;padding:1.2rem 1.4rem;'
        f'border-radius:8px;text-align:center;margin-bottom:0.9rem">'
        f'<div style="font-size:0.8rem;font-weight:600;letter-spacing:0.06em;'
        f'opacity:0.85;margin-bottom:0.2rem">RISCHIO COMPLESSIVO</div>'
        f'<div style="font-size:2.4rem;font-weight:800;line-height:1.1">{label}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<p style="font-size:0.9rem;line-height:1.55;margin-bottom:0.8rem">'
        f"{_build_synthesis(risk)}</p>",
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.markdown(
            f'<div style="font-size:0.82rem;color:{COLOR_TEXT_SECONDARY};line-height:1.8">'
            f"<b>Esposizione penali</b>&nbsp;&nbsp;{risk.max_penalty_exposure_pct:.1f}%<br>"
            f"<b>Clausole auto-ris.</b>&nbsp;&nbsp;{len(risk.auto_termination_clauses)}<br>"
            f"<b>Complessità SLA</b>&nbsp;&nbsp;"
            f"{_SLA_LABELS.get(risk.sla_complexity, risk.sla_complexity)}<br>"
            f"<b>Vendor lock-in</b>&nbsp;&nbsp;"
            f"{'Sì' if risk.vendor_lock_in_detected else 'No'}"
            f"</div>",
            unsafe_allow_html=True,
        )


def _render_risk_factor_card(rf: RiskFactor, idx: int) -> None:
    with st.container(border=True):
        col_badge, col_type, col_cite = st.columns([1, 3, 2])

        with col_badge:
            risk_severity_badge(rf.severity)

        with col_type:
            type_label = rf.type.replace("_", " ").capitalize()
            st.markdown(
                f'<span style="font-weight:600;font-size:0.9rem">{type_label}</span>',
                unsafe_allow_html=True,
            )

        with col_cite:
            source_citation(source=rf.source, key=f"risk_cite_{idx}")

        st.markdown(
            f'<p style="font-size:0.88rem;line-height:1.5;'
            f'margin-top:0.35rem;margin-bottom:0">{rf.description}</p>',
            unsafe_allow_html=True,
        )


def _render_tab_rischi(decision: TenderDecision | None) -> None:
    if decision is None:
        st.info(
            "Analisi dei rischi non ancora disponibile. "
            "Avvia l'analisi completa per ottenere la valutazione."
        )
        return

    risk = decision.risk_assessment

    col_radar, col_card = st.columns([55, 45])
    with col_radar:
        _render_radar_chart(risk)
    with col_card:
        _render_overall_risk_card(risk)

    st.divider()

    sorted_factors = sorted(
        risk.risk_factors, key=lambda rf: _SEV_ORDER.get(rf.severity, 99)
    )
    st.subheader(f"Fattori di rischio ({len(sorted_factors)})")

    if not sorted_factors:
        st.markdown(
            f'<span style="color:{COLOR_TEXT_SECONDARY};font-size:0.9rem">'
            "Nessun fattore di rischio specifico rilevato.</span>",
            unsafe_allow_html=True,
        )
        return

    for idx, rf in enumerate(sorted_factors):
        _render_risk_factor_card(rf, idx)


# ---------------------------------------------------------------------------
# Tab Checklist amministrativa
# ---------------------------------------------------------------------------

_CL_COLS = [0.45, 1.7, 3.6, 1.5, 1.6, 1.5]
_CL_KEY_PREFIX = "cl"


def _cl_key(tender_id: str, doc: DocumentTodo) -> str:
    """Chiave session_state stabile e unica per il checkbox di un documento."""
    safe_type = doc.document_type.replace(" ", "_").replace(".", "")
    return f"{_CL_KEY_PREFIX}_{tender_id}_{doc.source_requirement_id}_{safe_type}"


def _init_checklist_state(tender_id: str, docs: list[DocumentTodo]) -> None:
    """Inizializza le chiavi session_state a False solo se non già presenti."""
    for doc in docs:
        key = _cl_key(tender_id, doc)
        if key not in st.session_state:
            st.session_state[key] = False


def _render_checklist_header_row() -> None:
    cols = st.columns(_CL_COLS)
    labels = ["✓", "DOCUMENTO", "DESCRIZIONE", "SCADENZA", "RESPONSABILE", "TEMPLATE"]
    for col, label in zip(cols, labels):
        with col:
            st.markdown(
                f'<span style="font-size:0.7rem;font-weight:700;'
                f'color:{COLOR_TEXT_SECONDARY};letter-spacing:0.04em">{label}</span>',
                unsafe_allow_html=True,
            )
    st.markdown(
        f'<div style="border-bottom:1px solid {COLOR_BORDER};margin:0.2rem 0 0.4rem 0"></div>',
        unsafe_allow_html=True,
    )


def _render_checklist_row(doc: DocumentTodo, tender_id: str, idx: int) -> None:
    key = _cl_key(tender_id, doc)
    is_done = st.session_state.get(key, False)

    with st.container(border=True):
        cols = st.columns(_CL_COLS)

        with cols[0]:
            st.checkbox(
                label=doc.document_type,
                key=key,
                label_visibility="collapsed",
            )

        with cols[1]:
            style = f"font-weight:600;font-size:0.85rem"
            if is_done:
                style += f";color:{COLOR_TEXT_SECONDARY};text-decoration:line-through"
            st.markdown(f'<span style="{style}">{doc.document_type}</span>', unsafe_allow_html=True)

        with cols[2]:
            text = doc.description
            if len(text) > 90:
                text = text[:87] + "…"
            st.markdown(f'<span style="font-size:0.82rem">{text}</span>', unsafe_allow_html=True)

        with cols[3]:
            if doc.deadline:
                deadline_str = doc.deadline.strftime("%d/%m/%Y")
                # Evidenzia in rosso se scadenza passata
                from datetime import date as _date
                color = COLOR_NO_GO if doc.deadline < _date.today() else COLOR_TEXT_PRIMARY
                st.markdown(
                    f'<span style="font-size:0.85rem;color:{color}">{deadline_str}</span>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<span style="color:{COLOR_TEXT_SECONDARY}">—</span>',
                    unsafe_allow_html=True,
                )

        with cols[4]:
            st.markdown(
                f'<span style="font-size:0.82rem;color:{COLOR_TEXT_SECONDARY}">'
                f"{doc.owner_role}</span>",
                unsafe_allow_html=True,
            )

        with cols[5]:
            if doc.template_available:
                if st.button(
                    "↓ Scarica",
                    key=f"tmpl_{tender_id}_{doc.source_requirement_id}",
                    type="secondary",
                    width="stretch",
                ):
                    st.toast("Template in arrivo — B6 ReportGenerator non ancora attivo.")
            else:
                st.markdown(
                    f'<span style="color:{COLOR_TEXT_SECONDARY}">—</span>',
                    unsafe_allow_html=True,
                )


def _render_tab_checklist(
    checklist: AdminChecklist | None,
    tender_id: str,
    selected_roles: list[str],
) -> None:
    if checklist is None:
        st.info(
            "Checklist non disponibile. "
            "Avvia l'analisi completa (B6) per generare la lista dei documenti da preparare."
        )
        return

    docs = checklist.documents_required
    if not docs:
        st.info("Nessun documento richiesto per questa gara.")
        return

    _init_checklist_state(tender_id, docs)

    # Conteggio su TUTTI i documenti (non filtrati) — il progresso è della gara, non della vista
    done_count = sum(1 for doc in docs if st.session_state.get(_cl_key(tender_id, doc), False))
    total_count = len(docs)

    col_prog, col_spacer = st.columns([2, 3])
    with col_prog:
        st.markdown(
            f'<p style="font-size:1rem;font-weight:600;margin-bottom:0.2rem">'
            f"{done_count} di {total_count} documenti pronti</p>",
            unsafe_allow_html=True,
        )
        st.progress(done_count / total_count)

    st.markdown("<div style='margin-top:0.8rem'></div>", unsafe_allow_html=True)

    # Filtro applicato alla vista
    visible_docs = docs if not selected_roles else [d for d in docs if d.owner_role in selected_roles]

    if not visible_docs:
        st.info("Nessun documento corrisponde al filtro selezionato.")
        return

    _render_checklist_header_row()

    for idx, doc in enumerate(visible_docs):
        _render_checklist_row(doc, tender_id, idx)


# ---------------------------------------------------------------------------
# Tab Audit trail
# ---------------------------------------------------------------------------

_NOW = None  # lazily set at render time to keep relative timestamps consistent


def _relative_time(ts: datetime) -> str:  # noqa: F821 — datetime imported via schemas
    """Converte un timestamp in stringa relativa (es. '5 minuti fa')."""
    from datetime import datetime as _dt

    now = _dt.now(timezone.utc)
    aware = ts.replace(tzinfo=timezone.utc) if ts.tzinfo is None else ts
    delta_s = int((now - aware).total_seconds())

    if delta_s < 60:
        return f"{delta_s} secondi fa"
    if delta_s < 3600:
        m = delta_s // 60
        return f"{m} {'minuto' if m == 1 else 'minuti'} fa"
    if delta_s < 86400:
        h = delta_s // 3600
        return f"{h} {'ora' if h == 1 else 'ore'} fa"
    if delta_s < 172800:
        return f"ieri, {aware.strftime('%H:%M')}"
    return aware.strftime("%d/%m/%Y")


def _render_audit_entry(entry: AuditEntry, idx: int, is_last: bool) -> None:
    col_line, col_content = st.columns([0.03, 0.97])

    with col_line:
        line_html = (
            f'<div style="display:flex;flex-direction:column;align-items:center;height:100%">'
            f'<span style="font-size:0.65rem;color:{COLOR_TEXT_SECONDARY};line-height:1">●</span>'
        )
        if not is_last:
            line_html += (
                f'<div style="width:1px;background:{COLOR_BORDER};'
                f'flex:1;min-height:32px;margin-top:2px"></div>'
            )
        line_html += "</div>"
        st.markdown(line_html, unsafe_allow_html=True)

    with col_content:
        # Timestamp con tooltip e actor
        aware = entry.timestamp.replace(tzinfo=timezone.utc) if entry.timestamp.tzinfo is None else entry.timestamp
        exact = aware.strftime("%d/%m/%Y %H:%M:%S UTC")
        rel = _relative_time(entry.timestamp)
        actor_label = "SISTEMA" if entry.actor == "SYSTEM" else entry.actor

        st.markdown(
            f'<p style="font-size:0.78rem;color:{COLOR_TEXT_SECONDARY};margin:0 0 0.15rem 0">'
            f'<span title="{exact}" style="cursor:help">{rel}</span>'
            f" &nbsp;·&nbsp; {actor_label}"
            f"</p>",
            unsafe_allow_html=True,
        )

        # Descrizione azione
        st.markdown(
            f'<p style="font-size:0.9rem;margin:0 0 0.15rem 0">{entry.detail}</p>',
            unsafe_allow_html=True,
        )

        # Target (monospace inline)
        if entry.target:
            st.markdown(
                f'<p style="font-size:0.78rem;color:{COLOR_TEXT_SECONDARY};'
                f'font-family:monospace;margin:0 0 0.3rem 0">{entry.target}</p>',
                unsafe_allow_html=True,
            )

        # Payload espandibile
        if entry.payload:
            with st.expander("Payload", expanded=False):
                st.code(
                    json.dumps(entry.payload, indent=2, ensure_ascii=False),
                    language="json",
                )

        if not is_last:
            st.markdown(
                f'<div style="margin-bottom:0.6rem"></div>',
                unsafe_allow_html=True,
            )


def _render_tab_audit(entries: list[AuditEntry]) -> None:
    if not entries:
        st.info("Nessun evento registrato per questa gara.")
        return

    # Più recenti prima
    sorted_entries = sorted(entries, key=lambda e: e.timestamp, reverse=True)

    for idx, entry in enumerate(sorted_entries):
        _render_audit_entry(entry, idx, is_last=(idx == len(sorted_entries) - 1))


# ---------------------------------------------------------------------------
# Main page
# ---------------------------------------------------------------------------

inject_custom_css()

if st.button("← Torna alla lista", type="secondary"):
    st.switch_page("pages/home.py")

tender_id = st.session_state.get("selected_tender_id")

if not tender_id:
    st.warning("Nessuna gara selezionata. Torna alla lista gare.")
    st.stop()

# Carica dati
tender = _find_tender_metadata(tender_id)
if not tender:
    st.error(f"Gara non trovata: {tender_id}")
    st.stop()

decision = _load_decision(tender_id)
requirements = _load_requirements(tender_id)

client = get_api_client()
gap_results = client.get_gap_results(tender_id)
checklist = _load_admin_checklist(tender_id)
audit_entries = _load_audit_trail(tender_id)

# Sidebar — filtro checklist (visibile quando la checklist è disponibile)
if checklist and checklist.documents_required:
    _all_roles = sorted({doc.owner_role for doc in checklist.documents_required})
    selected_roles: list[str] = st.sidebar.multiselect(
        "Responsabile",
        options=_all_roles,
        default=[],
        help="Filtra i documenti della checklist per responsabile. Vuoto = mostra tutti.",
        key="checklist_role_filter",
    )
else:
    selected_roles = []

# Header
_render_header(tender, decision)

st.divider()

# Tab
tab_req, tab_gap, tab_risk, tab_check, tab_audit = st.tabs(
    ["Requisiti", "Gap analysis", "Rischi", "Checklist", "Audit trail"]
)

with tab_req:
    if requirements:
        _render_tab_requisiti(requirements)
    else:
        st.info("Nessun requisito estratto per questa gara.")

with tab_gap:
    if gap_results:
        _render_tab_gap_analysis(gap_results, requirements)
    else:
        st.info("Nessun risultato di gap analysis disponibile per questa gara.")

with tab_risk:
    _render_tab_rischi(decision)

with tab_check:
    _render_tab_checklist(checklist, tender_id, selected_roles)

with tab_audit:
    _render_tab_audit(audit_entries)
