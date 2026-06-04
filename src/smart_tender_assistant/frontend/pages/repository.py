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

from datetime import date
from pathlib import Path

import streamlit as st

from smart_tender_assistant.frontend.services.pipeline import (
    BandoMeta,
    UploadedDoc,
    analyze_uploads,
)
from smart_tender_assistant.frontend.ui.stca_helpers import get_bando, load_bandi, save_bandi
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
    # ===== Upload zone (file_uploader reale → pipeline B1+B2) =====
    st.markdown(
        """
        <div class="stca-uzone" style="padding-bottom:8px">
          <div class="cloud">☁</div>
          <div class="title">Carica i documenti del bando</div>
          <div class="sub">Capitolato, allegati tecnici, FAQ ente appaltante · PDF, DOCX, HTML, XML, TXT</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded = st.file_uploader(
        "Documenti del bando",
        type=["pdf", "docx", "doc", "html", "xml", "txt", "csv", "eml", "odt", "rtf", "xlsx"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        key="rep_uploader",
    )

    if uploaded:
        with st.container(key="rep_meta"):
            st.markdown(
                f'<div style="font-size:11.5px;font-weight:600;margin:4px 0 6px">'
                f"Metadati gara · {len(uploaded)} file selezionato/i</div>",
                unsafe_allow_html=True,
            )
            c1, c2 = st.columns([3, 2])
            nome = c1.text_input("Nome bando", value=Path(uploaded[0].name).stem, key="rep_nome")
            ente = c2.text_input("Ente appaltante", value="[PA locale]", key="rep_ente")
            c3, c4, c5 = st.columns(3)
            valore = c3.number_input(
                "Valore (€)", min_value=0.0, value=50000.0, step=1000.0, key="rep_valore"
            )
            scad = c4.date_input("Scadenza", key="rep_scad")
            cpv = c5.text_input("CPV", value="48730000-4", key="rep_cpv")

            run = st.button(
                "▶ Carica e analizza", type="primary", key="rep_run", width="stretch"
            )

        if run:
            docs = [UploadedDoc(name=f.name, data=f.getvalue()) for f in uploaded]
            meta = BandoMeta(
                nome=nome.strip() or "Bando senza nome",
                ente=ente.strip() or "[PA]",
                valore=float(valore),
                scadenza=scad.strftime("%d/%m/%Y"),
                giorni_mancanti=(scad - date.today()).days,
                canale="MePA",
                cpv=cpv.strip() or "—",
            )
            bando = None
            with st.status("Analisi AI in corso…", expanded=True) as status:
                try:
                    bando = analyze_uploads(docs, meta, progress=status.write)
                    status.update(label="Analisi completata ✓", state="complete")
                except Exception as exc:
                    status.update(label="Analisi fallita", state="error")
                    st.error(
                        f"**Analisi fallita:** {exc}\n\n"
                        "Verifica che Tika sia attivo (`docker compose up -d tika`) "
                        "e che `LLM_API_KEY` sia nel `.env`."
                    )
            if bando is not None:
                bandi = load_bandi()
                bandi.insert(0, bando)
                save_bandi(bandi)
                st.session_state["selected_bando_id"] = bando.id
                st.success(
                    f"✓ {len(bando.requisiti)} requisiti estratti — apro il dettaglio…"
                )
                st.switch_page("pages/tender_detail.py")

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
