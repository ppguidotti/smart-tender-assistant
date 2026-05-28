"""Repository documenti — render-as-HTML 1:1 con `viewRepository()` del prototipo.

Sezioni:
- topbar (HTML)
- upload zone (file_uploader stilizzato come uzone HTML)
- pending files (conditional) — bottoni "Avvia analisi" + "Rimuovi"
- agent bar — 2 bottoni
- "Da avviare" — card EDR con bottone Avvia analisi AI
- notifiche — 2 card con Ignora/Scarica

Tutta la pagina è dentro un singolo `@st.fragment` per evitare reload globale.
"""

from __future__ import annotations

import streamlit as st

from smart_tender_assistant.frontend.ui.stca_helpers import get_bando
from smart_tender_assistant.frontend.ui.theme import inject_custom_css

inject_custom_css()

# ---------------------------------------------------------------------------
# Topbar (statico HTML)
# ---------------------------------------------------------------------------

st.markdown(
    """
    <div class="stca-topbar">
      <h2 style="font-size:15px;font-weight:600;margin:0">Repository documenti</h2>
      <div class="sub" style="font-size:11.5px;color:#8A8AA4;margin-top:3px">
        Caricamento e gestione documenti di gara · Agente di monitoraggio
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Fragment: tutta la pagina (scoped reruns)
# ---------------------------------------------------------------------------


@st.fragment
def _repository() -> None:
    # ===== Upload zone (puramente decorativa, mirror del .uzone HTML) =====
    st.markdown(
        """
        <div class="stca-uzone">
          <div class="cloud">☁</div>
          <div class="title">Trascina i documenti del bando qui</div>
          <div class="sub">Capitolato, allegati tecnici, FAQ ente appaltante · PDF, DOCX, HTML, XML</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    pending = st.session_state.get("pending_files", [])

    # ===== Pending files card =====
    if pending:
        with st.container(key="rep_pending"):
            chips = "".join(f'<span class="stca-file-chip">📄 {n}</span>' for n in pending)
            st.markdown(
                f"""
                <div style="font-size:11.5px;font-weight:600;margin-bottom:7px">
                  File selezionati ({len(pending)})
                </div>
                <div style="display:flex;flex-wrap:wrap;gap:4px;margin-bottom:10px">{chips}</div>
                """,
                unsafe_allow_html=True,
            )
            c_start, c_clear, _ = st.columns([1.5, 1, 4])
            with c_start:
                if st.button("▶ Avvia analisi AI", type="primary", key="rep_start_pending"):
                    st.session_state["start_analysis_bid"] = "edr-001"
                    st.session_state["start_analysis_file"] = pending[0]
                    st.session_state["pending_files"] = []
                    st.switch_page("pages/tender_detail.py")
            with c_clear:
                if st.button("Rimuovi", key="rep_clear_pending"):
                    st.session_state["pending_files"] = []
                    st.rerun(scope="fragment")

    # ===== Agent bar =====
    with st.container(key="rep_agent"):
        c_icon, c_text, c_cfg, c_attiva = st.columns([0.4, 6, 1.6, 1.4])
        with c_icon:
            st.markdown(
                '<div style="font-size:22px;line-height:1;color:#8A8AA4">🤖</div>',
                unsafe_allow_html=True,
            )
        with c_text:
            st.markdown(
                """
                <div style="font-size:12.5px;font-weight:500">
                  Agente monitoraggio bandi automatico<span class="stca-beta-tag">Beta</span>
                </div>
                <div style="font-size:11px;color:#8A8AA4;margin-top:1px">
                  Verifica periodica su [portale appalti], MePA, portali PA configurati ·
                  Notifica nuovi bandi con AI summary e match stimato
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c_cfg:
            if st.button("Configura sorgenti", key="rep_cfg_agent"):
                st.toast("Configurazione sorgenti in arrivo.")
        with c_attiva:
            if st.button("Attiva agente", type="primary", key="rep_attiva_agent"):
                st.toast("Agente di monitoraggio attivato.", icon="✅")

    # ===== Sezione "Da avviare" =====
    st.markdown(
        '<div class="stca-sec-hd">Da avviare — 1 bando in attesa di analisi</div>',
        unsafe_allow_html=True,
    )

    edr = get_bando("edr-001")
    if edr:
        with st.container(key="rep_edr"):
            c_info, c_btn = st.columns([5, 1.4])
            with c_info:
                chips = "".join(
                    f'<span class="stca-file-chip">📄 {f}</span>' for f in edr.files
                )
                st.markdown(
                    f"""
                    <div style="font-size:13px;font-weight:600;margin-bottom:3px">
                      {edr.nome}
                    </div>
                    <div style="font-size:11px;color:#8A8AA4;margin-bottom:9px">
                      Caricato il {edr.uploaded_at} · {len(edr.files)} file · 9 pagine totali · {edr.ente}
                    </div>
                    <div style="display:flex;gap:5px;flex-wrap:wrap">{chips}</div>
                    """,
                    unsafe_allow_html=True,
                )
            with c_btn:
                if st.button(
                    "▶ Avvia analisi AI",
                    type="primary",
                    key="rep_start_edr",
                    width="stretch",
                ):
                    st.session_state["start_analysis_bid"] = "edr-001"
                    st.session_state["start_analysis_file"] = (
                        edr.files[0] if edr.files else "Capitolato.pdf"
                    )
                    st.switch_page("pages/tender_detail.py")

    # ===== Sezione "Notifiche agente" =====
    st.markdown(
        '<div class="stca-sec-hd">Notifiche agente — 2 nuovi bandi rilevati</div>',
        unsafe_allow_html=True,
    )

    notifs = [
        {
            "id": "cloud-x",
            "nome": "Servizi cloud ibrido e migrazione — [Ente regionale X]",
            "meta": "MePA · CPV 72220000-3 · Valore stimato ~€800K · Scadenza 30/06/2026",
            "ai": "AI: cloud migration [vendor cloud], IAM, [vendor cloud] 365. Match profilo stimato ~83%.",
        },
        {
            "id": "soc-y",
            "nome": "Cybersecurity + SOC managed H24 — [Comune Y]",
            "meta": "[Ente vigilanza] · CPV 79710000-4 · Valore stimato ~€450K · Scadenza 15/07/2026",
            "ai": "AI: SOC as a Service, SIEM, incident response NIS2-compliant. Match stimato ~71%.",
        },
    ]

    for n in notifs:
        with st.container(key=f"rep_notif_{n['id']}"):
            c_text, c_skip, c_dl = st.columns([5, 1, 1])
            with c_text:
                st.markdown(
                    f"""
                    <div style="font-size:12.5px;font-weight:500">{n["nome"]}</div>
                    <div style="font-size:10.5px;color:#8A8AA4;margin-top:2px">{n["meta"]}</div>
                    <div style="font-size:11px;color:#4A4A62;margin-top:3px;font-style:italic">{n["ai"]}</div>
                    """,
                    unsafe_allow_html=True,
                )
            with c_skip:
                if st.button("Ignora", key=f"rep_ign_{n['id']}"):
                    st.toast(f"Notifica ignorata: {n['nome'][:30]}…")
            with c_dl:
                if st.button(
                    "↓ Scarica",
                    type="primary",
                    key=f"rep_dl_{n['id']}",
                ):
                    st.toast(f"Bando scaricato: {n['nome'][:30]}…", icon="✅")


_repository()
