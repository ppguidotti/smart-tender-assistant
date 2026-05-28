"""Impostazioni piattaforma — render-as-HTML 1:1 con `viewSettings()` del prototipo.

Card "Profilo aziendale" (irow + bottoni Aggiorna/Carica) + card "Modello AI" (irow).
"""

from __future__ import annotations

import streamlit as st

from smart_tender_assistant.frontend.ui.theme import (
    COLOR_GN,
    inject_custom_css,
)

inject_custom_css()

# ---------------------------------------------------------------------------
# Topbar
# ---------------------------------------------------------------------------

st.markdown(
    '<div class="st-key-set_topbar"><h2>Impostazioni piattaforma</h2></div>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Card Profilo aziendale (con bottoni)
# ---------------------------------------------------------------------------

with st.container(key="set_card_profile"):
    st.markdown(
        f'<div style="font-size:13px;font-weight:600;margin-bottom:11px">'
        f"Profilo aziendale</div>"
        f'<div class="stca-irow"><span class="k">Ragione sociale</span>'
        f'<span class="v">[Azienda configurata]</span></div>'
        f'<div class="stca-irow"><span class="k">File competenze</span>'
        f'<span class="v" style="color:{COLOR_GN}">competenze_v2026.json ✓</span></div>'
        f'<div class="stca-irow"><span class="k">Certificazioni</span>'
        f'<span class="v">6 aziendali + 10 [Business unit sicurezza]</span></div>'
        f'<div class="stca-irow"><span class="k">Referenze portfolio</span>'
        f'<span class="v">5 referenze attive</span></div>',
        unsafe_allow_html=True,
    )
    c1, c2, _ = st.columns([1.4, 2, 3])
    with c1:
        if st.button("Aggiorna profilo", key="set_upd_profile", width="stretch"):
            st.toast("Aggiornamento profilo in arrivo.")
    with c2:
        if st.button(
            "Carica nuovo JSON competenze",
            type="primary",
            key="set_upload_comp",
            width="stretch",
        ):
            st.toast("Upload competenze JSON in arrivo.")

# ---------------------------------------------------------------------------
# Card Modello AI
# ---------------------------------------------------------------------------

with st.container(key="set_card_ai"):
    st.markdown(
        f'<div style="font-size:13px;font-weight:600;margin-bottom:11px">'
        f"Modello AI</div>"
        f'<div class="stca-irow"><span class="k">Endpoint</span>'
        f'<span class="v" style="font-family:\'JetBrains Mono\',monospace;font-size:11px">'
        f"https://[endpoint-ai].openai.azure.com/</span></div>"
        f'<div class="stca-irow"><span class="k">Modello LLM</span>'
        f'<span class="v">gpt-4o-mini (Standard)</span></div>'
        f'<div class="stca-irow"><span class="k">Embedding</span>'
        f'<span class="v">text-embedding-3-small</span></div>'
        f'<div class="stca-irow"><span class="k">Stato</span>'
        f'<span class="v" style="color:{COLOR_GN}">● Connesso</span></div>',
        unsafe_allow_html=True,
    )
