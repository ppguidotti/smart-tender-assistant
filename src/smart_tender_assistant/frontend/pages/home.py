"""Pagina Home — Lista gare con filtri e navigazione al dettaglio."""

from __future__ import annotations

from datetime import date, timedelta

import streamlit as st

from smart_tender_assistant.frontend.models.schemas import TenderListItem
from smart_tender_assistant.frontend.services.api_client import get_api_client
from smart_tender_assistant.frontend.ui.theme import (
    COLOR_TEXT_SECONDARY,
    COLOR_VEM_NAVY,
    DECISION_COLORS,
    DECISION_LABELS,
    STATUS_COLORS,
    STATUS_LABELS,
    inject_custom_css,
)


def _load_tenders() -> list[TenderListItem]:
    """Carica la lista gare dal client API."""
    client = get_api_client()
    return client.list_tenders()


def _apply_filters(
    tenders: list[TenderListItem],
    decision_filter: list[str],
    status_filter: list[str],
    date_range: tuple[date, date],
) -> list[TenderListItem]:
    """Applica i filtri selezionati dall'utente."""
    filtered = tenders

    if decision_filter:
        filtered = [t for t in filtered if t.decision in decision_filter]

    if status_filter:
        filtered = [t for t in filtered if t.status in status_filter]

    start, end = date_range
    filtered = [t for t in filtered if start <= t.created_at.date() <= end]
    return filtered


def _render_sidebar_filters(
    tenders: list[TenderListItem],
) -> tuple[list[str], list[str], tuple[date, date]]:
    """Renderizza i filtri nella sidebar e restituisce i valori selezionati."""
    st.sidebar.markdown("### Filtri")

    # Filtro per decisione
    decision_options = ["GO", "GO_WITH_RESERVATIONS", "NO_GO"]
    decision_labels = {k: DECISION_LABELS[k] for k in decision_options}
    selected_decisions: list[str] = st.sidebar.multiselect(
        "Decisione",
        options=decision_options,
        format_func=lambda x: decision_labels[x],
        default=[],
        help="Filtra per tipo di decisione. Lascia vuoto per mostrare tutte.",
    )

    # Filtro per stato
    status_options = [
        "QUEUED",
        "PARSING",
        "EXTRACTING",
        "ANALYZING",
        "SCORING",
        "REPORTING",
        "COMPLETED",
        "FAILED",
    ]
    status_labels = {k: STATUS_LABELS[k] for k in status_options}
    selected_statuses: list[str] = st.sidebar.multiselect(
        "Stato dell'analisi",
        options=status_options,
        format_func=lambda x: status_labels[x],
        default=[],
        help="Filtra per stato dell'analisi. Lascia vuoto per mostrare tutti.",
    )

    # Filtro per data
    if tenders:
        min_date = min(t.created_at.date() for t in tenders)
        max_date = max(t.created_at.date() for t in tenders)
    else:
        min_date = date.today() - timedelta(days=30)
        max_date = date.today()

    date_range = st.sidebar.date_input(
        "Intervallo date",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        help="Filtra per data di creazione della gara.",
    )

    # Gestisci il caso in cui l'utente seleziona una sola data
    if isinstance(date_range, tuple) and len(date_range) == 2:
        date_start, date_end = date_range
    else:
        date_start = date_range if isinstance(date_range, date) else min_date
        date_end = max_date

    return selected_decisions, selected_statuses, (date_start, date_end)


def _format_decision_html(decision: str | None) -> str:
    """Formatta la decisione come badge HTML per la tabella."""
    if decision is None:
        return '<span style="color:#888">—</span>'
    color = DECISION_COLORS.get(decision, "#888")
    label = DECISION_LABELS.get(decision, decision)
    return (
        f'<span style="background:{color};color:#fff;padding:2px 8px;'
        f'border-radius:4px;font-size:0.8rem;font-weight:600">{label}</span>'
    )


def _format_status_html(status: str) -> str:
    """Formatta lo stato come badge HTML per la tabella."""
    color = STATUS_COLORS.get(status, "#888")
    label = STATUS_LABELS.get(status, status)
    return (
        f'<span style="background:{color};color:#fff;padding:2px 8px;'
        f'border-radius:4px;font-size:0.75rem;font-weight:500">{label}</span>'
    )


def _format_value(value_money: object | None) -> str:
    """Formatta il valore economico."""
    if value_money is None:
        return "—"
    # value_money è un Money object
    amount = getattr(value_money, "amount", 0)
    if amount >= 1_000_000:
        return f"€ {amount / 1_000_000:.1f}M"
    if amount >= 1_000:
        return f"€ {amount / 1_000:.0f}k"
    return f"€ {amount:.0f}"


def _render_tender_table(tenders: list[TenderListItem]) -> None:
    """Renderizza la tabella delle gare con righe cliccabili."""
    if not tenders:
        st.info("Nessuna gara trovata con i filtri selezionati.")
        return

    for tender in tenders:
        col_name, col_status, col_decision, col_score, col_reqs, col_gaps, col_value, col_date = (
            st.columns([3, 1.2, 1.3, 0.8, 0.8, 0.8, 1, 1.2])
        )

        with col_name:
            if st.button(
                tender.name,
                key=f"tender_{tender.tender_id}",
                use_container_width=True,
                type="tertiary",
            ):
                st.session_state["selected_tender_id"] = str(tender.tender_id)
                st.switch_page("pages/tender_detail.py")

        with col_status:
            st.markdown(_format_status_html(tender.status), unsafe_allow_html=True)

        with col_decision:
            st.markdown(_format_decision_html(tender.decision), unsafe_allow_html=True)

        with col_score:
            if tender.score is not None:
                st.markdown(f"**{tender.score:.0f}**/100")
            else:
                st.markdown('<span style="color:#888">—</span>', unsafe_allow_html=True)

        with col_reqs:
            st.markdown(f"{tender.total_requirements}")

        with col_gaps:
            if tender.critical_gaps > 0:
                st.markdown(
                    f'<span style="color:#A32D2D;font-weight:600">{tender.critical_gaps}</span>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(f"{tender.critical_gaps}")

        with col_value:
            st.markdown(_format_value(tender.estimated_value))

        with col_date:
            st.markdown(
                f'<span style="color:{COLOR_TEXT_SECONDARY};font-size:0.85rem">'
                f"{tender.created_at.strftime('%d/%m/%Y')}</span>",
                unsafe_allow_html=True,
            )

    st.divider()
    st.caption(f"{len(tenders)} gare trovate")


# Inietta CSS personalizzato
inject_custom_css()

st.title("Gare d'appalto")

# Carica dati
all_tenders = _load_tenders()

# Sidebar filters
decision_filter, status_filter, date_range = _render_sidebar_filters(all_tenders)

# Azioni principali
col_left, col_right = st.columns([4, 1])
with col_right:
    if st.button("Nuova gara", type="primary", use_container_width=True):
        st.info("Funzionalità in arrivo — upload documento e avvio analisi.")

# Filtro applicato
filtered_tenders = _apply_filters(all_tenders, decision_filter, status_filter, date_range)

# Table header
st.markdown(
    f'<div style="display:flex;padding:0.3rem 0;border-bottom:2px solid {COLOR_VEM_NAVY};'
    f'margin-bottom:0.5rem;font-size:0.75rem;color:{COLOR_TEXT_SECONDARY};font-weight:600">'
    f'<div style="flex:3">NOME GARA</div>'
    f'<div style="flex:1.2">STATO</div>'
    f'<div style="flex:1.3">DECISIONE</div>'
    f'<div style="flex:0.8">SCORE</div>'
    f'<div style="flex:0.8">REQ.</div>'
    f'<div style="flex:0.8">GAP CR.</div>'
    f'<div style="flex:1">VALORE</div>'
    f'<div style="flex:1.2">DATA</div>'
    f"</div>",
    unsafe_allow_html=True,
)

# Table body
_render_tender_table(filtered_tenders)
