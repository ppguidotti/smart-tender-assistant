"""Dashboard bandi — render-as-HTML 1:1 con `viewDashboard()` del prototipo.

Layout:
- Topbar (key="dash_topbar"): title sx + search + bottone Nuovo bando in 3 colonne
- Stat grid: 5 stat-card HTML
- Chip filtri (key="dash_chips"): bottoni Streamlit stilizzati come pill
- Tabella: anchor `.stca-brow` HTML (click → switch_page tender_detail)

Tutto wrappato in `@st.fragment` → search e chip non causano reload del browser.
"""

from __future__ import annotations

import streamlit as st

from smart_tender_assistant.frontend.models.schemas import BandoHTML
from smart_tender_assistant.frontend.ui.stca_helpers import load_bandi
from smart_tender_assistant.frontend.ui.theme import (
    DASH_FILTER_LABELS,
    bando_status_badge,
    fmt_val,
    inject_custom_css,
)

inject_custom_css()

# ---------------------------------------------------------------------------
# Cross-page actions
# ---------------------------------------------------------------------------

qp = st.query_params

if "open" in qp:
    st.session_state["selected_bando_id"] = qp["open"]
    st.query_params.clear()
    st.switch_page("pages/tender_detail.py")

st.session_state.setdefault("dash_filter", "all")
st.session_state.setdefault("dash_search", "")

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

bandi = load_bandi()
totale = len(bandi)
n_analisi = sum(1 for b in bandi if b.status == "analisi")
n_go = sum(1 for b in bandi if b.status == "go")
n_nogo = sum(1 for b in bandi if b.status == "no-go")
n_vinte = sum(1 for b in bandi if b.status == "vinta")
n_perse = sum(1 for b in bandi if b.status == "persa")
n_chiuse = n_vinte + n_perse
win_rate = f"{round(n_vinte / n_chiuse * 100)}%" if n_chiuse > 0 else "—"


def _stat_card(label: str, value: str | int, tone: str = "") -> str:
    cls = f"stca-stat-val{' ' + tone if tone else ''}"
    return (
        f'<div class="stca-stat-card">'
        f'<div class="stca-stat-lbl">{label}</div>'
        f'<div class="{cls}">{value}</div>'
        f"</div>"
    )


def _brow(b: BandoHTML) -> str:
    urgent_cls = "stca-brow-urgent" if 0 < b.giorni_mancanti <= 14 else ""
    urgent_suffix = (
        f" · {b.giorni_mancanti}gg" if 0 < b.giorni_mancanti <= 14 else ""
    )
    return (
        f'<a class="stca-brow" href="?open={b.id}" target="_self">'
        f"<div>"
        f'<div class="stca-brow-name">{b.nome}</div>'
        f'<div class="stca-brow-cpv">CPV {b.cpv}</div>'
        f"</div>"
        f'<div class="stca-brow-ente">{b.ente}</div>'
        f'<div class="stca-brow-val">{fmt_val(b.valore)}</div>'
        f'<div class="{urgent_cls}" style="font-size:11.5px">{b.scadenza}{urgent_suffix}</div>'
        f'<div class="stca-brow-channel">{b.canale}</div>'
        f"<div>{bando_status_badge(b.status)}</div>"
        f"</a>"
    )


def _on_search_change() -> None:
    """Callback search: sincronizza widget → session_state."""
    st.session_state["dash_search"] = st.session_state.get("dash_search_input", "")


# ---------------------------------------------------------------------------
# Fragment: tutta la dashboard (scoped reruns)
# ---------------------------------------------------------------------------


@st.fragment
def _dashboard() -> None:
    # ===== Topbar =====
    with st.container(key="dash_topbar"):
        col_title, col_search, col_btn = st.columns([3.5, 2, 1.2])
        with col_title:
            st.markdown(
                f"<h2>Dashboard bandi</h2>"
                f'<div class="sub">{totale} bandi in gestione · Anno 2026</div>',
                unsafe_allow_html=True,
            )
        with col_search:
            st.text_input(
                "search",
                value=st.session_state["dash_search"],
                placeholder="Cerca bando…",
                label_visibility="collapsed",
                key="dash_search_input",
                on_change=_on_search_change,
            )
        with col_btn:
            if st.button("＋ Nuovo bando", key="new_bando", width="stretch"):
                st.switch_page("pages/repository.py")

    # ===== Stat grid =====
    stats_html = (
        _stat_card("TOTALE", totale)
        + _stat_card("IN ANALISI", n_analisi, "c-bl")
        + _stat_card("GO CONFERMATI", n_go, "c-gn")
        + _stat_card("NO-GO", n_nogo, "c-rd")
        + _stat_card("WIN RATE", win_rate, "c-am")
    )
    st.markdown(
        f'<div class="stca-stat-grid">{stats_html}</div>',
        unsafe_allow_html=True,
    )

    # ===== Chip filtri =====
    filters = ["all", "analisi", "go", "no-go", "vinta", "persa", "pending"]
    with st.container(key="dash_chips"):
        cols = st.columns(len(filters) + 1)
        for i, f in enumerate(filters):
            label = DASH_FILTER_LABELS[f] + (f" ({totale})" if f == "all" else "")
            with cols[i]:
                is_on = st.session_state["dash_filter"] == f
                if st.button(
                    label,
                    key=f"chip_{f}",
                    type="primary" if is_on else "secondary",
                ):
                    st.session_state["dash_filter"] = f
                    st.rerun(scope="fragment")

    # ===== Filtro effettivo =====
    active = st.session_state["dash_filter"]
    filtered = bandi if active == "all" else [b for b in bandi if b.status == active]
    q = st.session_state["dash_search"].strip().lower()
    if q:
        filtered = [
            b
            for b in filtered
            if q in b.nome.lower()
            or q in b.ente.lower()
            or q in b.cpv.lower()
            or (b.short_nome and q in b.short_nome.lower())
        ]

    # ===== Tabella =====
    rows_html = (
        "".join(_brow(b) for b in filtered)
        if filtered
        else '<div class="stca-card" style="text-align:center;color:#8A8AA4">'
        "Nessun bando corrisponde ai filtri selezionati.</div>"
    )
    st.markdown(
        f'<div class="stca-tbl-hd" style="margin-top:10px">'
        "<span>BANDO</span><span>ENTE</span><span>VALORE</span>"
        "<span>SCADENZA</span><span>CANALE</span><span>STATO</span>"
        f"</div>{rows_html}",
        unsafe_allow_html=True,
    )


_dashboard()
