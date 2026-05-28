"""Roadmap aziendale gap — render-as-HTML 1:1 con `viewRoadmap()` del prototipo.

Aggregazione gap cross-bandi + righe statiche + piano azioni prioritarie.
"""

from __future__ import annotations

import streamlit as st

from smart_tender_assistant.frontend.ui.stca_helpers import aggregate_gaps, load_bandi
from smart_tender_assistant.frontend.ui.theme import (
    COLOR_AM,
    COLOR_GN,
    COLOR_RD,
    COLOR_T2,
    inject_custom_css,
)

inject_custom_css()

bandi = load_bandi()
dyn_gaps = aggregate_gaps(bandi)

# Righe statiche mirror dell'HTML
_STATIC_ROWS: list[dict] = [
    {
        "testo": "ISO/IEC 20000-1:2018 — IT Service Management certificato",
        "stato": "IN_SCADENZA",
        "tone": "analisi",
        "freq": 4,
        "imp": "Critico · 4 gare",
        "azione": "Rinnovo urgente · [Ente cert. C] · ~€4.000 · Q2 2026",
        "cls": "crit",
    },
    {
        "testo": "ISO/IEC 27017:2015 — Cloud Security Controls specifica",
        "stato": "ASSENTE",
        "tone": "nogo",
        "freq": 3,
        "imp": "Critico · 3 gare",
        "azione": "Iter certificazione · ~6 mesi · ~€8.000 · Q3 2026",
        "cls": "crit",
    },
    {
        "testo": "ISO 45001:2018 — Salute e Sicurezza",
        "stato": "SCADUTA",
        "tone": "persa",
        "freq": 3,
        "imp": "Medio · 3 gare pref.",
        "azione": "Valutare rinnovo · ~€3.500 · Q3 2026",
        "cls": "warn",
    },
    {
        "testo": "Partnership SIEM — competenza vendor certificata",
        "stato": "DICHIARATO",
        "tone": "pending",
        "freq": 2,
        "imp": "Medio · 2 gare",
        "azione": "Formalizzare partnership · coda revisione · Q3 2026",
        "cls": "warn",
    },
    {
        "testo": "[Vendor Networking] Gold Partner o superiore",
        "stato": "COPERTO",
        "tone": "go",
        "freq": 5,
        "imp": "Risolto",
        "azione": "Partnership [Vendor Networking] Preferred attiva ✓",
        "cls": "",
    },
    {
        "testo": "Esperienza PA ente >500.000 abitanti verificabile",
        "stato": "COPERTO",
        "tone": "go",
        "freq": 5,
        "imp": "Risolto",
        "azione": "REF001 — [Comune capoluogo] ✓",
        "cls": "",
    },
    {
        "testo": "[Vendor EDR] Partner livello Elite o superiore",
        "stato": "COPERTO",
        "tone": "go",
        "freq": 2,
        "imp": "Risolto",
        "azione": "Livello Elite attivo ✓",
        "cls": "",
    },
]

all_rows: list[dict] = [
    {
        "testo": g.testo,
        "stato": "GAP ESC." if g.status == "gap-esc" else "GAP PREF.",
        "tone": "nogo" if g.status == "gap-esc" else "cond",
        "freq": g.count,
        "imp": f"{g.count} gare",
        "azione": "Da risolvere — coda revisione",
        "cls": "crit" if g.status == "gap-esc" else "warn",
    }
    for g in dyn_gaps
] + _STATIC_ROWS


# ---------------------------------------------------------------------------
# Topbar (con bottoni Streamlit)
# ---------------------------------------------------------------------------


with st.container(key="rmp_topbar"):
    col_title, col_xls, col_add = st.columns([4, 1.2, 1.4])
    with col_title:
        st.markdown(
            f'<h2>Roadmap aziendale gap</h2>'
            f'<div class="sub">Requisiti trasversali · {len(bandi)} bandi analizzati · '
            f"Impatto sul win rate</div>",
            unsafe_allow_html=True,
        )
    with col_xls:
        if st.button("↓ Esporta Excel", key="rmp_xls", width="stretch"):
            st.toast("Export Excel in arrivo.")
    with col_add:
        if st.button("＋ Aggiungi azione", type="primary", key="rmp_add", width="stretch"):
            st.toast("Modulo nuova azione in arrivo.")

# ---------------------------------------------------------------------------
# Info banner
# ---------------------------------------------------------------------------

st.markdown(
    '<div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:8px;'
    'padding:9px 13px;margin-bottom:14px;font-size:12px;color:#1D4ED8">'
    "ℹ I requisiti con gap attivi (in rosso/arancio) sono aggiornati in tempo reale "
    "dalle revisioni effettuate nella tab Requisiti &amp; Gap."
    "</div>",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Tabella header + righe (single-line HTML)
# ---------------------------------------------------------------------------

st.markdown(
    '<div class="stca-road-hd">'
    "<span>REQUISITO / CATEGORIA</span>"
    "<span>FREQ.</span>"
    "<span>STATO</span>"
    "<span>IMPATTO</span>"
    "<span>AZIONE CONSIGLIATA</span>"
    "</div>",
    unsafe_allow_html=True,
)


def _row(r: dict) -> str:
    cls = r["cls"]
    freq_color = COLOR_RD if cls == "crit" else COLOR_AM if cls == "warn" else COLOR_GN
    imp_color = freq_color
    fill_pct = min(r["freq"] / 5 * 100, 100)
    testo_short = r["testo"][:70] + ("..." if len(r["testo"]) > 70 else "")
    return (
        f'<div class="stca-road-row {cls}">'
        f'<div><div style="font-size:12px;font-weight:500">{testo_short}</div></div>'
        f"<div>"
        f'<div style="font-size:16px;font-weight:700;'
        f'font-family:\'JetBrains Mono\',monospace;color:{freq_color}">{r["freq"]}</div>'
        f'<div class="stca-freq-bar">'
        f'<div class="stca-freq-fill" style="width:{fill_pct}%;background:{freq_color}"></div>'
        f"</div></div>"
        f'<span class="stca-badge stca-b-{r["tone"]}">{r["stato"]}</span>'
        f'<div style="font-size:11.5px;font-weight:500;color:{imp_color}">{r["imp"]}</div>'
        f'<div style="font-size:11px;color:{COLOR_T2}">{r["azione"]}</div>'
        f"</div>"
    )


rows_html = "".join(_row(r) for r in all_rows)
st.markdown(rows_html, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Piano azioni prioritarie
# ---------------------------------------------------------------------------

st.markdown(
    f'<div style="margin-top:14px">'
    f'<div style="font-size:11.5px;font-weight:600;color:{COLOR_T2};margin-bottom:8px">'
    f"Piano azioni prioritarie — impatto stimato:</div>"
    f'<span class="stca-prio-pill" style="background:#FEF2F2;color:{COLOR_RD};'
    f'border:1px solid #FECACA">1. Rinnovo ISO 20000-1 → +4 gare</span>'
    f'<span class="stca-prio-pill" style="background:#FEF2F2;color:{COLOR_RD};'
    f'border:1px solid #FECACA">2. ISO 27017 cloud → +3 gare PA sanitaria</span>'
    f'<span class="stca-prio-pill" style="background:#FEFCE8;color:{COLOR_AM};'
    f'border:1px solid #FDE68A">3. ISO 45001 rinnovo → +3 punti tecnici</span>'
    f'<span class="stca-prio-pill" style="background:#F0FDF4;color:{COLOR_GN};'
    f'border:1px solid #BBF7D0">Win rate atteso post azioni: 67% → 85%+</span>'
    f"</div>",
    unsafe_allow_html=True,
)
