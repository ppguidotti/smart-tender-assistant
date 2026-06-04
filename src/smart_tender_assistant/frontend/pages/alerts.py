"""Alert e notifiche — render-as-HTML 1:1 con `viewAlerts()` del prototipo.

3 sezioni:
- Urgente (cert in scadenza / scadute) — bottoni "Avvia rinnovo"
- Prossime scadenze entro 6 mesi — tabella cert
- Scadenza bandi prossimi 60 giorni — bottoni "Apri" → switch_page
"""

from __future__ import annotations

import streamlit as st

from smart_tender_assistant.frontend.services.api_client import get_api_client
from smart_tender_assistant.frontend.ui.stca_helpers import load_bandi
from smart_tender_assistant.frontend.ui.theme import (
    COLOR_AM,
    COLOR_GN,
    COLOR_RD,
    COLOR_T3,
    bando_status_badge,
    inject_custom_css,
)

inject_custom_css()

client = get_api_client()
certs = client.list_cert_expiry()
bandi = load_bandi()

urgent_certs = [c for c in certs if c.stato in ("urgent", "scaduta")]
normal_certs = [c for c in certs if c.stato in ("warn", "ok")]
upcoming_bandi = [b for b in bandi if 0 < b.giorni_mancanti <= 60]

# ---------------------------------------------------------------------------
# Topbar
# ---------------------------------------------------------------------------

st.markdown(
    '<div class="st-key-alr_topbar">'
    "<h2>Alert e notifiche</h2>"
    '<div class="sub">Certificazioni in scadenza, bandi urgenti, azioni richieste</div>'
    "</div>",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sezione URGENTI
# ---------------------------------------------------------------------------

st.markdown(
    f'<div class="stca-alrt-hd" style="background:#FEF2F2;color:{COLOR_RD};'
    f"border:1px solid #FECACA;border-bottom:none;border-radius:8px 8px 0 0\">"
    "⚠ Urgente — azione richiesta</div>",
    unsafe_allow_html=True,
)

for c in urgent_certs:
    gg_lbl = "SCAD." if c.stato == "scaduta" else f"{c.giorni} gg"
    scaduta_html = (
        f' · <strong style="color:{COLOR_RD}">SCADUTA</strong>'
        if c.stato == "scaduta"
        else ""
    )
    with st.container(key=f"alr_urgent_{c.nome[:20].replace(' ', '_')}"):
        c_info, c_pill, c_btn = st.columns([5, 0.9, 1.4])
        with c_info:
            st.markdown(
                f'<div style="font-size:12.5px;font-weight:500">{c.nome}</div>'
                f'<div style="font-size:10.5px;color:{COLOR_T3};margin-top:2px">'
                f"Ente: {c.ente} · Scadenza: {c.scad}{scaduta_html}</div>"
                f'<div style="font-size:10.5px;color:{COLOR_RD};margin-top:2px">'
                f"Impatta {c.bandi} bandi attivi</div>",
                unsafe_allow_html=True,
            )
        with c_pill:
            st.markdown(
                f'<span class="stca-days-pill" style="background:#FEF2F2;color:{COLOR_RD};'
                f'border:1px solid #FECACA">{gg_lbl}</span>',
                unsafe_allow_html=True,
            )
        with c_btn:
            if st.button("Avvia rinnovo", key=f"alr_renew_{c.nome[:20]}", width="stretch"):
                st.toast(f"Procedura rinnovo avviata per: {c.nome[:40]}", icon="✅")

# ---------------------------------------------------------------------------
# Sezione PROSSIME SCADENZE (tabella)
# ---------------------------------------------------------------------------

st.markdown(
    '<div class="stca-alrt-hd" style="background:#F8F7F5;color:#4A4A62;'
    "border:1px solid rgba(0,0,0,0.07);border-bottom:none;border-radius:8px 8px 0 0\">"
    "🔔 Prossime scadenze — entro 6 mesi</div>",
    unsafe_allow_html=True,
)

rows = "".join(
    f"<tr>"
    f'<td style="font-weight:500">{c.nome}</td>'
    f'<td style="color:{COLOR_T3}">{c.ente}</td>'
    f"<td>{c.scad}</td>"
    f'<td style="font-family:\'JetBrains Mono\',monospace;font-weight:600;'
    f'color:{COLOR_AM if c.giorni < 90 else COLOR_GN}">{c.giorni} gg</td>'
    f'<td style="color:{COLOR_T3}">{f"{c.bandi} bandi" if c.bandi else "—"}</td>'
    f"</tr>"
    for c in normal_certs
)

st.markdown(
    '<div style="border:1px solid rgba(0,0,0,0.07);border-top:none;'
    'border-radius:0 0 8px 8px;background:#fff;margin-bottom:14px">'
    '<table class="stca-cert-tbl">'
    "<thead><tr>"
    "<th>CERTIFICAZIONE</th><th>ENTE</th><th>SCADENZA</th>"
    "<th>GIORNI</th><th>BANDI</th>"
    "</tr></thead>"
    f"<tbody>{rows}</tbody>"
    "</table></div>",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sezione SCADENZA BANDI 60GG
# ---------------------------------------------------------------------------

st.markdown(
    '<div class="stca-alrt-hd" style="background:#F8F7F5;color:#4A4A62;'
    "border:1px solid rgba(0,0,0,0.07);border-bottom:none;border-radius:8px 8px 0 0\">"
    "📋 Scadenza bandi — prossimi 60 giorni</div>",
    unsafe_allow_html=True,
)

for bb in upcoming_bandi:
    is_urgent = bb.giorni_mancanti <= 14
    pill_bg = "#FEF2F2" if is_urgent else "#FEFCE8"
    pill_color = COLOR_RD if is_urgent else COLOR_AM
    pill_bd = "#FECACA" if is_urgent else "#FDE68A"

    with st.container(key=f"alr_bando_{bb.id}"):
        c_info, c_pill, c_btn = st.columns([5, 0.9, 1.0])
        with c_info:
            st.markdown(
                f'<div style="font-size:12.5px;font-weight:500">{bb.nome}</div>'
                f'<div style="font-size:10.5px;color:{COLOR_T3};margin-top:2px">'
                f"{bb.ente} · Scadenza: {bb.scadenza} · {bando_status_badge(bb.status)}</div>",
                unsafe_allow_html=True,
            )
        with c_pill:
            st.markdown(
                f'<span class="stca-days-pill" style="background:{pill_bg};color:{pill_color};'
                f'border:1px solid {pill_bd}">{bb.giorni_mancanti} gg</span>',
                unsafe_allow_html=True,
            )
        with c_btn:
            if st.button("Apri", key=f"alr_open_{bb.id}", width="stretch"):
                st.session_state["selected_bando_id"] = bb.id
                st.switch_page("pages/tender_detail.py")
