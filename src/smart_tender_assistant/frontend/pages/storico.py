"""Storico gare — render-as-HTML 1:1 con `viewStorico()` del prototipo.

4 KPI + tabella gare chiuse con motivazione + insight box.
"""

from __future__ import annotations

import streamlit as st

from smart_tender_assistant.frontend.ui.stca_helpers import load_bandi
from smart_tender_assistant.frontend.ui.theme import (
    COLOR_AM,
    COLOR_GN,
    COLOR_RD,
    COLOR_T3,
    bando_status_badge,
    fmt_val,
    inject_custom_css,
)

inject_custom_css()

bandi = load_bandi()
closed = [b for b in bandi if b.status in ("vinta", "persa", "no-go")]
vinte = sum(1 for b in closed if b.status == "vinta")
perse = sum(1 for b in closed if b.status == "persa")
nogo = sum(1 for b in closed if b.status == "no-go")
win_rate = f"{round(vinte / (vinte + perse) * 100)}%" if (vinte + perse) else "—"

_SCORES = {"dc-001": 91, "rete-001": 87, "wan-001": 73, "edr-002": 0}
_MOTIVI = {
    "dc-001": "Referenza PA sanitaria, tutte certificazioni coperte, punteggio tecnico massimo",
    "rete-001": "[Vendor Networking] Gold + SOC certificato, prezzo competitivo",
    "wan-001": (
        "Gap ISO 20000-1 (-3pt pref.) · Concorrente più economico · SIEM non certificato"
    ),
    "edr-002": "Gap escludente: ISO/IEC 27017 obbligatoria — assente in portfolio",
}

# ---------------------------------------------------------------------------
# Topbar con bottone Export
# ---------------------------------------------------------------------------

with st.container(key="rmp_topbar"):  # riutilizzo lo stile della topbar Roadmap
    col_title, col_exp = st.columns([4, 1.4])
    with col_title:
        st.markdown(
            f"<h2>Storico gare</h2>"
            f'<div class="sub">Win rate {win_rate} · {len(closed)} gare chiuse</div>',
            unsafe_allow_html=True,
        )
    with col_exp:
        if st.button("↓ Esporta storico", key="sto_exp", width="stretch"):
            st.toast("Export storico in arrivo.")

# ---------------------------------------------------------------------------
# 4 KPI cards
# ---------------------------------------------------------------------------

st.markdown(
    f'<div class="stca-stat-grid cols-4">'
    f'<div class="stca-stat-card"><div class="stca-stat-lbl">VINTE</div>'
    f'<div class="stca-stat-val c-gn">{vinte}</div></div>'
    f'<div class="stca-stat-card"><div class="stca-stat-lbl">PERSE</div>'
    f'<div class="stca-stat-val c-rd">{perse}</div></div>'
    f'<div class="stca-stat-card"><div class="stca-stat-lbl">NO-GO</div>'
    f'<div class="stca-stat-val c-rd">{nogo}</div></div>'
    f'<div class="stca-stat-card"><div class="stca-stat-lbl">WIN RATE</div>'
    f'<div class="stca-stat-val c-am">{win_rate}</div></div>'
    f"</div>",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Tabella header + righe
# ---------------------------------------------------------------------------

st.markdown(
    f'<div style="display:grid;grid-template-columns:2fr 90px 100px 65px 1.5fr;'
    f"gap:8px;padding:5px 12px;font-size:9.5px;font-weight:600;color:{COLOR_T3};"
    f'letter-spacing:.07em;text-transform:uppercase">'
    f"<span>BANDO</span><span>VALORE</span><span>ESITO</span>"
    f"<span>SCORE</span><span>MOTIVAZIONE</span></div>",
    unsafe_allow_html=True,
)

rows_html = ""
for b in closed:
    sc = _SCORES.get(b.id, 0)
    motivo = _MOTIVI.get(b.id, "—")
    score_color = (
        COLOR_GN if b.status == "vinta"
        else COLOR_T3 if b.status == "persa"
        else COLOR_RD
    )
    rows_html += (
        f'<div style="display:grid;grid-template-columns:2fr 90px 100px 65px 1.5fr;'
        f"gap:8px;padding:10px 12px;background:#fff;border:1px solid rgba(0,0,0,0.07);"
        f'border-radius:8px;margin-bottom:3px;align-items:center">'
        f"<div>"
        f'<div style="font-size:12px;font-weight:500">{b.nome}</div>'
        f'<div style="font-size:10px;color:{COLOR_T3};margin-top:1px">'
        f"{b.ente} · {b.canale}</div>"
        f"</div>"
        f'<div style="font-size:12px;font-weight:500;'
        f'font-family:\'JetBrains Mono\',monospace">{fmt_val(b.valore)}</div>'
        f"<div>{bando_status_badge(b.status)}</div>"
        f'<div style="font-size:14px;font-weight:700;'
        f'font-family:\'JetBrains Mono\',monospace;color:{score_color}">{sc}</div>'
        f'<div style="font-size:11px;color:#4A4A62">{motivo}</div>'
        f"</div>"
    )

st.markdown(rows_html, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Insight box
# ---------------------------------------------------------------------------

st.markdown(
    '<div class="stca-insight">'
    "<strong>💡 Insight:</strong> Le gare perse/no-go condividono: ISO 20000-1 (scaduta), "
    "ISO 27017 (assente), SIEM partnership non formalizzata. Questi 3 elementi sono nella "
    "roadmap come priorità 1-3. Risolverli stima +18% win rate."
    "</div>",
    unsafe_allow_html=True,
)
