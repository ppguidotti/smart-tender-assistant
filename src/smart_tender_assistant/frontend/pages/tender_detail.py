"""Pagina Dettaglio gara — stub, verrà implementata nella prossima iterazione."""

from __future__ import annotations

import streamlit as st

tender_id = st.session_state.get("selected_tender_id")

if not tender_id:
    st.warning("Nessuna gara selezionata. Torna alla lista gare.")
    st.stop()

st.title("Dettaglio gara")
st.caption(f"Tender ID: {tender_id}")
st.info(
    "Questa pagina sarà implementata nella prossima iterazione con tab per requisiti, gap analysis, rischi, checklist e audit trail."
)
