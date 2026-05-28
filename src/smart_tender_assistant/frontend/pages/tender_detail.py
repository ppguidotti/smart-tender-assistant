"""Dettaglio gara — render-as-HTML 1:1 con `viewDetail()` del prototipo.

Topbar (breadcrumb + meta) + 3 tab:
- Requisiti & Gap — chip filtri + sezioni categoria + popover Revisiona
- Checklist — progress + sezioni + checkbox per item + Mark all + Add item
- Go/No-Go — gauge SVG + score breakdown + KPI + contesto + decisione

Dialog "Analisi AI in corso" si apre se `session_state["start_analysis_bid"]` è set.
"""

from __future__ import annotations

import time
from math import pi
from typing import Iterable

import streamlit as st

from smart_tender_assistant.frontend.models.schemas import (
    ChecklistItemHTML,
    RequisitoBando,
)
from smart_tender_assistant.frontend.ui.stca_helpers import (
    calc_score,
    chk_stats,
    gap_count,
    get_bando,
)
from smart_tender_assistant.frontend.ui.theme import (
    COLOR_AM,
    COLOR_BD,
    COLOR_GN,
    COLOR_RD,
    COLOR_T1,
    COLOR_T2,
    COLOR_T3,
    bando_status_badge,
    fmt_val,
    inject_custom_css,
)

inject_custom_css()


# ───────────────────────────────────────────────────────────────
# Dialog analisi AI (mirror startAnalysis() nell'HTML)
# ───────────────────────────────────────────────────────────────


@st.dialog("🤖 Analisi AI in corso", width="large")
def _run_analysis_dialog(bando_id: str, filename: str) -> None:
    st.markdown(
        f'<div style="font-size:13px;color:{COLOR_T3};margin-bottom:14px">'
        f"File: <strong style='color:#E87722'>{filename}</strong></div>",
        unsafe_allow_html=True,
    )

    with st.status("M1 — Estrazione e classificazione requisiti", expanded=True) as s1:
        st.write("Caricamento e parsing documento in corso…")
        time.sleep(0.4)
        st.write("Identificazione sezioni: Capitolato, Allegati, FAQ…")
        time.sleep(0.4)
        st.write("Classificazione requisiti per categoria…")
        time.sleep(0.35)
        st.success("✓ 30 requisiti estratti: 5 qualificazione, 9 normativa, 8 tecnica, 8 amm.")
        s1.update(label="M1 — Estrazione completata ✓", state="complete")

    with st.status("M2+M3 — Analisi normativa + Gap certificazioni", expanded=True) as s2:
        st.write("[M2] Caricamento KB normativo: GDPR, D.lgs.36/2023, CAD…")
        time.sleep(0.35)
        st.write("[M2] Analisi conformità normativa: 9 requisiti…")
        time.sleep(0.35)
        st.write("[M3] Confronto certificazioni con registry aziendale…")
        time.sleep(0.35)
        st.write("[M3] Fuzzy matching: ISO/IEC 27001 ✓, ISO 9001 ✓, [Vendor EDR] Elite ✓…")
        time.sleep(0.35)
        st.warning("⚠ Gap rilevato: ISO/IEC 20000-1 — IN_SCADENZA 31/05/2026")
        time.sleep(0.3)
        st.success("✓ M2: copertura normativa 87% · M3: 1 gap preferenziale, 0 escludenti")
        s2.update(label="M2+M3 — Analisi completata ✓", state="complete")

    with st.status("Output — Score e raccomandazione Go/No-Go", expanded=True) as s3:
        st.write("Calcolo score composito: M2×0.30 + M3×0.40 + Qual×0.30…")
        time.sleep(0.35)
        bb = get_bando(bando_id)
        if bb is not None:
            bb.status = "analisi"
            bb.analisi_completa = True
            sc = calc_score(bb.requisiti)
        else:
            sc = type("R", (), {"score": 76, "ra": "GO"})()
        st.success(f"Score: {sc.score}/100 — {sc.ra}")
        s3.update(label="Output — Score calcolato ✓", state="complete")

    snum_color = "#4ADE80" if sc.ra == "GO" else "#F87171"
    slabel = "✓ GO — Presentare offerta" if sc.ra == "GO" else f"⊘ {sc.ra}"
    st.markdown(
        f"""
        <div style="background:#16162B;border-radius:12px;padding:24px;
             margin-top:14px;text-align:center">
          <div style="font-size:48px;font-weight:700;font-family:'JetBrains Mono',monospace;
               color:{snum_color};line-height:1">{sc.score}</div>
          <div style="font-size:14px;font-weight:600;color:{snum_color};margin-top:6px">
            {slabel}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Apri analisi →", type="primary", key="open_after_analysis", width="stretch"):
        st.session_state["selected_bando_id"] = bando_id
        st.session_state.pop("start_analysis_bid", None)
        st.session_state.pop("start_analysis_file", None)
        st.rerun()


if "start_analysis_bid" in st.session_state:
    _run_analysis_dialog(
        st.session_state["start_analysis_bid"],
        st.session_state.get("start_analysis_file", "Capitolato.pdf"),
    )


# ───────────────────────────────────────────────────────────────
# Resolve bando
# ───────────────────────────────────────────────────────────────


bid = st.session_state.get("selected_bando_id", "edr-001")
b = get_bando(bid)

if b is None:
    st.warning("Nessuna gara selezionata.")
    if st.button("← Torna alla Dashboard"):
        st.switch_page("pages/home.py")
    st.stop()


# ───────────────────────────────────────────────────────────────
# Back button + topbar
# ───────────────────────────────────────────────────────────────


with st.container(key="tdet_back"):
    if st.button("← Dashboard", key="back_to_dash"):
        st.switch_page("pages/home.py")

status_html = bando_status_badge(b.status)
meta_urgent = (
    f'<span class="stca-urgency">⏱ {b.giorni_mancanti} giorni alla scadenza</span>'
    f'<span class="sep">·</span>'
    if b.giorni_mancanti > 0
    else ""
)

st.markdown(
    f'<div class="stca-topbar">'
    f'<div class="stca-breadcrumb"><span class="cur">{b.short_nome or b.nome}</span>&nbsp; {status_html}</div>'
    f'<div class="stca-meta">'
    f"<span>🏛 {b.ente}</span><span class=\"sep\">·</span>"
    f'<span>💶 {fmt_val(b.valore)}</span><span class="sep">·</span>'
    f'<span>🗓 Scad. {b.scadenza}</span><span class="sep">·</span>'
    f"{meta_urgent}"
    f"<span>{b.canale} · CPV {b.cpv}</span>"
    f"</div></div>",
    unsafe_allow_html=True,
)


# ───────────────────────────────────────────────────────────────
# Tabs
# ───────────────────────────────────────────────────────────────


tab_req, tab_chk, tab_gng = st.tabs(
    ["📋 Requisiti & Gap", "☑ Checklist", "🎯 Go / No-Go"]
)


# ============================================================
# TAB 1 — REQUISITI & GAP
# ============================================================


_CATS = ["TECNICA", "NORMATIVA", "QUALIFICAZIONE", "AMMINISTRATIVA"]
_CAT_LABELS = {
    "TECNICA": "Tecnica",
    "NORMATIVA": "Normativa",
    "QUALIFICAZIONE": "Qualificazione",
    "AMMINISTRATIVA": "Amministrativa",
}


def _req_dot_class(r: RequisitoBando) -> str:
    if r.status in ("coperto", "automatico"):
        return "stca-d-gn"
    if r.status == "parziale":
        return "stca-d-am"
    if r.status in ("gap-esc", "gap-pref"):
        return "stca-d-rd"
    return "stca-d-gr"


def _nota_class(r: RequisitoBando) -> str:
    if r.status in ("gap-esc", "gap-pref"):
        return "rn"
    if r.status == "parziale":
        return "wn"
    return ""


def _tipo_tag(tipo: str) -> str:
    cls = "esc" if tipo == "ESCLUDENTE" else "pref" if tipo == "PREFERENZIALE" else "info"
    return f'<span class="stca-tag stca-tag-{cls}">{tipo}</span>'


def _render_req_row(r: RequisitoBando) -> None:
    """Riga requisito = 6 colonne (dot, txt+nota, fonte, tipo, match, action button).

    L'azione apre un pannello di revisione inline sotto la riga (tramite
    `session_state["rev_open"]`). Pattern coerente col prototipo HTML originale.
    """
    needs_action = r.status in ("parziale", "gap-pref", "gap-esc")
    nota_html = (
        f'<div class="stca-req-note {_nota_class(r)}">{r.nota}</div>' if r.nota else ""
    )
    rev_open = st.session_state.get("rev_open") == r.id

    with st.container(key=f"tdet_req_row_{r.id}"):
        c1, c2, c3, c4, c5, c6 = st.columns([0.3, 4.5, 0.9, 1.4, 2.4, 1.6])
        with c1:
            st.markdown(
                f'<div class="stca-req-dot {_req_dot_class(r)}" style="margin-top:6px"></div>',
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f'<div class="stca-req-txt">{r.txt}</div>{nota_html}',
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                f'<div class="stca-req-fonte" style="margin-top:2px">{r.fonte}</div>',
                unsafe_allow_html=True,
            )
        with c4:
            st.markdown(
                f'<div style="margin-top:1px">{_tipo_tag(r.tipo)}</div>',
                unsafe_allow_html=True,
            )
        with c5:
            st.markdown(
                f'<div style="margin-top:1px"><span class="stca-mp stca-mp-{r.mt}">{r.ml}</span></div>',
                unsafe_allow_html=True,
            )
        with c6:
            if needs_action:
                if rev_open:
                    label = "Chiudi"
                    btn_type = "secondary"
                elif r.status in ("gap-esc", "gap-pref"):
                    label = "⚠ Gestisci"
                    btn_type = "primary"
                else:
                    label = "Revisiona"
                    btn_type = "secondary"
                if st.button(
                    label,
                    key=f"rev_btn_{r.id}",
                    type=btn_type,
                    width="stretch",
                ):
                    st.session_state["rev_open"] = None if rev_open else r.id
                    st.rerun(scope="fragment")

    # Pannello revisione inline sotto la riga
    if needs_action and rev_open:
        with st.container(key=f"tdet_req_rev_{r.id}"):
            _render_revision_form(r)


def _render_revision_form(r: RequisitoBando) -> None:
    """Form inline di revisione (mirror del rev-panel)."""
    is_gap = r.status in ("gap-esc", "gap-pref")
    st.markdown(
        f'<div style="font-size:12px;font-weight:600;margin-bottom:4px">'
        f"Revisione umana — {r.txt[:55]}{'...' if len(r.txt) > 55 else ''}</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div style="font-size:11px;color:{COLOR_T2};margin-bottom:8px">'
        + (
            "Questo requisito ha un gap attivo. Aggiorna lo stato se hai trovato "
            "un'evidenza nel profilo aziendale non riconosciuta dall'AI."
            if is_gap
            else f"L'AI ha classificato questo come <em>{r.status}</em>. "
            "Se hai un'evidenza che lo copre, aggiorna lo stato e inserisci una nota."
        )
        + "</div>",
        unsafe_allow_html=True,
    )

    if is_gap:
        opts = {
            "": "Seleziona azione…",
            "coperto": "✓ Match trovato — coperto",
            "gap-pref": "Gap preferenziale — accetta perdita punti",
            "gap-esc": "Gap escludente — impossibile partecipare",
        }
    else:
        opts = {
            "": "Seleziona stato aggiornato…",
            "coperto": "✓ Coperto — evidenza confermata",
            "parziale": "Parziale — verifica ancora in corso",
            "gap-pref": "Gap preferenziale",
        }

    new_status = st.selectbox(
        "Nuovo stato",
        options=list(opts.keys()),
        format_func=lambda k: opts[k],
        key=f"sel_{r.id}",
        label_visibility="collapsed",
    )
    note = st.text_area(
        "Note",
        value=r.rev_nota or "",
        placeholder="Note (es. numero referenza, documento disponibile…)",
        key=f"note_{r.id}",
        label_visibility="collapsed",
        height=70,
    )
    if st.button("Salva", type="primary", key=f"save_{r.id}", width="stretch"):
        if not new_status:
            st.toast("Seleziona uno stato prima di salvare.", icon="⚠️")
        else:
            r.status = new_status  # type: ignore[assignment]
            r.rev_nota = note
            if new_status == "coperto":
                r.ml = "✓ Coperto — revisione umana"
                r.mt = "gn"
            elif new_status in ("gap-pref", "gap-esc"):
                r.ml = (
                    "Gap preferenziale confermato"
                    if new_status == "gap-pref"
                    else "Gap escludente — azione richiesta"
                )
                r.mt = "rd"
            else:
                r.mt = "am"
            if note:
                r.nota = note
            st.toast("Revisione salvata — Score aggiornato", icon="✅")
            st.rerun()


with tab_req:

    @st.fragment
    def _tab_requisiti() -> None:
        reqs = b.requisiti
        gaps_n = sum(1 for r in reqs if r.status in ("gap-esc", "gap-pref"))
        parc_n = sum(1 for r in reqs if r.status == "parziale")

        # Chip filtri + legenda
        st.session_state.setdefault("req_filter", "all")
        filters: list[tuple[str, str]] = [("all", f"Tutti ({len(reqs)})")] + [
            (c.lower(), f"{_CAT_LABELS[c]} ({sum(1 for r in reqs if r.cat == c)})")
            for c in _CATS
        ] + [("gap", f"⚠ Gap ({gaps_n + parc_n})")]

        col_chips, col_legend = st.columns([3, 1])
        with col_chips:
            with st.container(key="tdet_req_chips"):
                cols = st.columns(len(filters))
                for i, (k, lbl) in enumerate(filters):
                    is_on = st.session_state["req_filter"] == k
                    with cols[i]:
                        if st.button(
                            lbl,
                            key=f"req_chip_{k}",
                            type="primary" if is_on else "secondary",
                        ):
                            st.session_state["req_filter"] = k
                            st.rerun(scope="fragment")
        with col_legend:
            st.markdown(
                """
                <div class="stca-legend" style="justify-content:flex-end;padding-top:6px">
                  <div class="stca-leg-i"><div class="stca-leg-dot stca-d-gn"></div>Coperto</div>
                  <div class="stca-leg-i"><div class="stca-leg-dot stca-d-am"></div>Parziale</div>
                  <div class="stca-leg-i"><div class="stca-leg-dot stca-d-rd"></div>Gap</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Applica filtro (gap = include anche parziali per matchare il conteggio della chip)
        f = st.session_state["req_filter"]
        if f == "all":
            filtered: list[RequisitoBando] = reqs
        elif f == "gap":
            filtered = [
                r for r in reqs if r.status in ("gap-esc", "gap-pref", "parziale")
            ]
        else:
            filtered = [r for r in reqs if r.cat.lower() == f]

        # Sezioni per categoria
        for cat in _CATS:
            cat_reqs = [r for r in filtered if r.cat == cat]
            if not cat_reqs:
                continue
            n_cat = sum(1 for r in reqs if r.cat == cat)
            cov = sum(1 for r in cat_reqs if r.status in ("coperto", "automatico", "info"))
            par = sum(1 for r in cat_reqs if r.status == "parziale")
            gap = sum(1 for r in cat_reqs if r.status in ("gap-esc", "gap-pref"))

            bits = []
            if cov:
                bits.append(
                    f'<span style="font-size:10.5px;color:{COLOR_GN};font-weight:500">✓ {cov} coperti</span>'
                )
            if par:
                bits.append(
                    f'<span style="font-size:10.5px;color:{COLOR_AM};font-weight:500">~ {par} parziali</span>'
                )
            if gap:
                bits.append(
                    f'<span style="font-size:10.5px;color:{COLOR_RD};font-weight:500">⚠ {gap} gap</span>'
                )

            st.markdown(
                f"""
                <div class="stca-req-sec-hd" style="margin-top:14px">
                  <span>{_CAT_LABELS[cat].upper()} — {n_cat} REQUISITI</span>
                  <div style="display:flex;gap:10px">{' '.join(bits)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            for r in cat_reqs:
                _render_req_row(r)

    _tab_requisiti()


# ============================================================
# TAB 2 — CHECKLIST
# ============================================================


@st.dialog("Aggiungi item alla checklist")
def _add_item_dialog() -> None:
    st.caption("Inserisci manualmente un adempimento non estratto automaticamente")
    txt = st.text_input("Descrizione", placeholder="Es. Comunicare nominativo referente tecnico…")
    cat = st.selectbox(
        "Categoria",
        [
            "Privacy & GDPR",
            "Sicurezza & Certificazioni",
            "Fatturazione & Tracciabilità",
            "Delivery & Contratto",
            "Altro",
        ],
    )
    prio = st.selectbox("Priorità", ["Standard", "Attenzione", "Urgente"])
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Annulla", width="stretch"):
            st.rerun()
    with c2:
        if st.button("Aggiungi item", type="primary", width="stretch"):
            if not txt.strip():
                st.toast("Inserisci una descrizione.", icon="⚠️")
            else:
                b.checklist.append(
                    ChecklistItemHTML(
                        id=f"usr-{len(b.checklist) + 1}",
                        cat=cat,
                        txt=txt.strip(),
                        sub="Aggiunto manualmente",
                        done=False,
                        urgente=(prio == "Urgente"),
                        warn=(prio == "Attenzione"),
                    )
                )
                st.toast("Item aggiunto alla checklist", icon="✅")
                st.rerun()


def _render_chk_item(it: ChecklistItemHTML) -> None:
    """Item checklist = checkbox + testo + status pill."""
    with st.container(key=f"tdet_chk_item_{it.id}"):
        c_box, c_text, c_pill = st.columns([0.3, 5, 1.2])
        with c_box:
            if it.urgente:
                # Item urgente: niente checkbox (azione manuale)
                st.markdown(
                    '<div class="stca-chk-box" style="margin-top:1px"></div>',
                    unsafe_allow_html=True,
                )
            else:
                new_val = st.checkbox(
                    " ",
                    value=it.done,
                    key=f"chk_{b.id}_{it.id}",
                    label_visibility="collapsed",
                )
                if new_val != it.done:
                    it.done = new_val
                    st.rerun(scope="fragment")
        with c_text:
            done_cls = "done" if it.done else ""
            urgent_cls = "urgent" if it.urgente else ""
            st.markdown(
                f"""
                <div class="stca-chk-item {done_cls}" style="margin:0">
                  <div style="flex:1">
                    <div class="stca-chk-lbl">{it.txt}</div>
                    <div class="stca-chk-sub {urgent_cls}">{it.sub}</div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c_pill:
            if it.urgente:
                lbl_html = (
                    f'<span style="font-size:10px;padding:3px 8px;border-radius:100px;'
                    f'background:{COLOR_RD};color:#fff;font-weight:600">Azione richiesta</span>'
                )
            elif it.done:
                lbl_html = (
                    f'<span style="font-size:10px;padding:3px 8px;border-radius:100px;'
                    f'background:#F0FDF4;color:{COLOR_GN};font-weight:500">Completato</span>'
                )
            elif it.warn:
                lbl_html = (
                    f'<span style="font-size:10px;padding:3px 8px;border-radius:100px;'
                    f'background:#FEFCE8;color:{COLOR_AM};font-weight:500">In corso</span>'
                )
            else:
                lbl_html = (
                    f'<span style="font-size:10px;padding:3px 8px;border-radius:100px;'
                    f'background:#F8F7F5;color:{COLOR_T3};font-weight:500">Da fare</span>'
                )
            st.markdown(
                f'<div style="margin-top:2px;text-align:right">{lbl_html}</div>',
                unsafe_allow_html=True,
            )


with tab_chk:

    @st.fragment
    def _tab_checklist() -> None:
        st_chk = chk_stats(b.checklist)
        cats = list(dict.fromkeys([c.cat for c in b.checklist]))

        # Toolbar: title/progress sx + bottoni dx
        with st.container(key="tdet_chk_toolbar"):
            col_l, col_r = st.columns([3, 2])
            with col_l:
                st.markdown(
                    f"""
                    <div style="font-size:13px;font-weight:600">Checklist conformità</div>
                    <div style="font-size:11px;color:{COLOR_T3};margin-top:1px">
                      {st_chk.done} / {st_chk.total} completati · {st_chk.pct}%
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with col_r:
                ca, cb = st.columns(2)
                with ca:
                    if st.button("＋ Aggiungi item", key="add_item_btn", width="stretch"):
                        _add_item_dialog()
                with cb:
                    if st.button("↓ Esporta PDF", key="export_pdf", width="stretch"):
                        st.toast("Export PDF in arrivo — B6 ReportGenerator non ancora attivo.")

        st.markdown(
            f"""
            <div class="stca-pb-wrap" style="margin:10px 0 14px">
              <div class="stca-pb-fill" style="width:{st_chk.pct}%"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Sezioni per categoria
        for cat in cats:
            items = [i for i in b.checklist if i.cat == cat]
            done_n = sum(1 for i in items if i.done)
            color = COLOR_GN if done_n == len(items) else COLOR_T3
            st.markdown(
                f"""
                <div style="font-size:9.5px;font-weight:700;color:{COLOR_T3};
                     letter-spacing:.07em;padding:8px 0 6px;
                     border-bottom:1px solid {COLOR_BD};margin-bottom:6px;
                     display:flex;justify-content:space-between">
                  <span>{cat.upper()}</span>
                  <span style="color:{color}">{done_n}/{len(items)}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            for it in items:
                _render_chk_item(it)

        # Mark all done
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        with st.container(key="tdet_chk_mark_all"):
            col_info, col_btn = st.columns([3, 1.4])
            with col_info:
                st.markdown(
                    f'<div style="padding-top:6px;font-size:11.5px;color:{COLOR_T3}">'
                    f"Completamento: <strong style='color:{COLOR_T1}'>"
                    f"{st_chk.done}/{st_chk.total}</strong></div>",
                    unsafe_allow_html=True,
                )
            with col_btn:
                if st.button("Segna tutti completati ✓", key="mark_all", width="stretch"):
                    for it in b.checklist:
                        if not it.urgente:
                            it.done = True
                    st.toast("Tutti gli item non urgenti segnati come completati", icon="✅")
                    st.rerun(scope="fragment")

    _tab_checklist()


# ============================================================
# TAB 3 — GO / NO-GO
# ============================================================


def _gauge_svg(score: int, ra: str, color: str) -> str:
    """Gauge SVG mirror dell'HTML — single-line per evitare interpretazione code block."""
    circ = 2 * pi * 58
    arc = circ * (score / 100) if score > 0 else 0
    offset = -circ * 0.25
    return (
        f'<svg width="170" height="170" viewBox="0 0 158 158">'
        f'<circle cx="79" cy="79" r="58" fill="none" stroke="#E5E7EB" stroke-width="13"/>'
        f'<circle cx="79" cy="79" r="58" fill="none" stroke="{color}" stroke-width="13" '
        f'stroke-dasharray="{arc} {circ}" stroke-dashoffset="{offset}" stroke-linecap="round" '
        f'style="transform:rotate(-90deg);transform-origin:79px 79px"/>'
        f'<text x="79" y="68" text-anchor="middle" font-family="JetBrains Mono,monospace" '
        f'font-size="30" font-weight="600" fill="{color}">{score}</text>'
        f'<text x="79" y="85" text-anchor="middle" font-family="Plus Jakarta Sans,sans-serif" '
        f'font-size="11" fill="#8A8AA4">/100 punti</text>'
        f'<text x="79" y="104" text-anchor="middle" font-family="Plus Jakarta Sans,sans-serif" '
        f'font-size="12" font-weight="600" fill="{color}">{ra}</text>'
        f"</svg>"
    )


with tab_gng:

    @st.fragment
    def _tab_gng() -> None:
        sc = calc_score(b.requisiti)
        gaps = gap_count(b.requisiti)
        cs = chk_stats(b.checklist)

        gauge_color = (
            "#DC2626"
            if sc.override
            else "#16A34A"
            if sc.ra == "GO"
            else "#D97706"
            if sc.ra == "GO_CONDIZIONALE"
            else "#DC2626"
        )

        motiv = (
            "Presenza di gap escludenti: la partecipazione alla gara non è possibile "
            "nelle condizioni attuali. Risolvere i gap prima di procedere."
            if sc.override
            else (
                "Profilo aziendale fortemente allineato su tutti i requisiti escludenti. "
                "Il vendor lock-in è favorevole (livello Elite Partner). Gap preferenziale "
                "ISO/IEC 20000-1 in scadenza incide sulla componente M3. Gara MePA sotto "
                "soglia: concorrenza limitata. Strategicamente conveniente."
                if sc.ra == "GO"
                else "Score borderline. Risolvere i gap preferenziali identificati per "
                "rafforzare la posizione competitiva prima della presentazione."
            )
        )

        # Gauge + score breakdown (single-line HTML per evitare code-block parsing)
        col_gauge, col_score = st.columns([1, 2.5])
        with col_gauge:
            override_html = (
                f'<div style="margin-top:8px;font-size:10.5px;padding:5px 9px;'
                f'background:#FEF2F2;color:{COLOR_RD};border-radius:8px;text-align:center">'
                f"⚠ Override: gap escludente</div>"
                if sc.override
                else ""
            )
            st.markdown(
                f'<div class="stca-card" style="text-align:center;padding:14px">'
                f"{_gauge_svg(sc.score, sc.ra, gauge_color)}"
                f'<div style="font-size:11px;color:{COLOR_T3};margin-top:4px">Score complessivo</div>'
                f'<div style="font-size:10px;color:{COLOR_T3};margin-top:2px">Soglia Go ≥ 75</div>'
                f"{override_html}"
                f"</div>",
                unsafe_allow_html=True,
            )

        with col_score:
            def _bar(label: str, pct: int, weight: float) -> str:
                color = "#16A34A" if pct >= 80 else "#D97706" if pct >= 50 else "#DC2626"
                text_color = COLOR_GN if pct >= 80 else COLOR_AM
                return (
                    f'<div style="margin-bottom:10px">'
                    f'<div style="display:flex;justify-content:space-between;font-size:11px;margin-bottom:4px">'
                    f'<span style="color:{COLOR_T2}">{label}</span>'
                    f'<span style="font-weight:600;font-family:\'JetBrains Mono\',monospace">'
                    f'{pct}% → <span style="color:{text_color}">+{pct * weight:.1f}pt</span>'
                    f"</span></div>"
                    f'<div class="stca-score-bar">'
                    f'<div class="stca-score-fill" style="width:{pct}%;background:{color}"></div>'
                    f"</div></div>"
                )

            st.markdown(
                f'<div class="stca-card">'
                f'<div style="font-size:12px;font-weight:600;margin-bottom:11px">'
                f"Scomposizione score per modulo</div>"
                f'{_bar("M2 — Copertura normativa (30%)", sc.m2, 0.30)}'
                f'{_bar("M3 — Gap certificazioni (40%)", sc.m3c, 0.40)}'
                f'{_bar("M3 — Qualificazione economica (30%)", sc.m3q, 0.30)}'
                f'<div class="stca-ai-box">'
                f'<div style="font-size:10px;font-weight:600;color:{COLOR_AM};margin-bottom:2px">'
                f"🤖 Motivazione AI</div>"
                f'<div style="font-size:11px;color:{COLOR_T2};line-height:1.5">{motiv}</div>'
                f"</div></div>",
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

        # KPI grid (4 card)
        kpis = [
            ("Valore contratto", fmt_val(b.valore), COLOR_T1, "36 mesi"),
            ("Gap escludenti", str(gaps.esc), COLOR_RD if gaps.esc else COLOR_GN, ""),
            ("Gap preferenziali", str(gaps.pref), COLOR_AM if gaps.pref else COLOR_GN, ""),
            ("Checklist", f"{cs.done}/{cs.total}", COLOR_GN if cs.pct >= 80 else COLOR_AM, ""),
        ]
        cards_html = "".join(
            f'<div class="stca-kpi-card">'
            f'<div class="stca-kpi-lbl">{lbl}</div>'
            f'<div class="stca-kpi-val" style="color:{color}">{val}</div>'
            + (
                f'<div style="font-size:10px;color:{COLOR_T3};margin-top:2px">{sub}</div>'
                if sub
                else ""
            )
            + "</div>"
            for (lbl, val, color, sub) in kpis
        )
        st.markdown(
            f'<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;'
            f'margin-bottom:14px">{cards_html}</div>',
            unsafe_allow_html=True,
        )

        # 2 cols: gap pendenti + contesto strategico (single-line per safe rendering)
        gap_pref_items = [r for r in b.requisiti if r.status == "gap-pref"]
        parz_items = [r for r in b.requisiti if r.status == "parziale"]

        gap_inner = ""
        if gap_pref_items:
            for r in gap_pref_items:
                txt_short = r.txt[:50] + ("..." if len(r.txt) > 50 else "")
                nota_block = (
                    f'<div style="font-size:10px;color:{COLOR_T3}">{r.nota}</div>'
                    if r.nota
                    else ""
                )
                gap_inner += (
                    f'<div style="display:flex;gap:7px;padding:6px 0;border-bottom:1px solid {COLOR_BD}">'
                    f'<span class="stca-tag stca-tag-pref" style="flex-shrink:0;margin-top:1px">PREF.</span>'
                    f"<div>"
                    f'<div style="font-size:11.5px;font-weight:500">{txt_short}</div>'
                    f"{nota_block}"
                    f"</div></div>"
                )
        elif not parz_items:
            gap_inner = f'<div style="font-size:11.5px;color:{COLOR_GN}">✓ Nessun gap attivo</div>'

        for r in parz_items:
            txt_short = r.txt[:50] + ("..." if len(r.txt) > 50 else "")
            gap_inner += (
                f'<div style="display:flex;gap:7px;padding:6px 0;border-bottom:1px solid {COLOR_BD}">'
                f'<span class="stca-tag" style="background:#FEFCE8;color:{COLOR_AM};'
                f'border:1px solid #FDE68A;flex-shrink:0;margin-top:1px">VERIFICA</span>'
                f'<div style="font-size:11.5px">{txt_short}</div>'
                f"</div>"
            )

        rischio_color = COLOR_RD if b.giorni_mancanti <= 14 else COLOR_AM
        rischio_v = (
            f"{b.giorni_mancanti} giorni alla scadenza"
            if b.giorni_mancanti > 0
            else "Chiuso"
        )

        st.markdown(
            f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:14px">'
            f'<div class="stca-card-sm">'
            f'<div class="stca-info-card-t">⚠ Gap e azioni pendenti</div>'
            f"{gap_inner}"
            f"</div>"
            f'<div class="stca-card-sm">'
            f'<div class="stca-info-card-t">🎯 Contesto strategico</div>'
            f'<div class="stca-irow"><span class="k">Canale acquisto</span>'
            f'<span class="v">MePA — concorrenza limitata</span></div>'
            f'<div class="stca-irow"><span class="k">Vendor lock-in</span>'
            f'<span class="v" style="color:{COLOR_GN}">Favorevole — Livello Elite</span></div>'
            f'<div class="stca-irow"><span class="k">Gare simili vinte</span>'
            f'<span class="v">2 su 3 (67%)</span></div>'
            f'<div class="stca-irow"><span class="k">Marginalità stimata</span>'
            f'<span class="v">Buona — licenze rinnovo</span></div>'
            f'<div class="stca-irow"><span class="k">Rischio penali</span>'
            f'<span class="v" style="color:{rischio_color}">{rischio_v}</span></div>'
            f"</div></div>",
            unsafe_allow_html=True,
        )

        # Decision bar
        dec_color_esc = COLOR_RD if gaps.esc else COLOR_GN
        dec_color_pref = COLOR_AM if gaps.pref else COLOR_T1
        confermato_html = (
            f' · <strong style="color:{COLOR_GN}">✓ Decisione confermata</strong>'
            if b.gng_confermato
            else ""
        )
        with st.container(key="tdet_gng_dec"):
            if not b.gng_confermato:
                col_info, col_no, col_yes = st.columns([3, 1.2, 1.8])
                with col_info:
                    st.markdown(
                        f'<div style="font-size:11.5px;color:{COLOR_T3};padding-top:6px">'
                        f'Checklist: <strong style="color:{COLOR_T1}">{cs.done}/{cs.total}</strong> · '
                        f'Gap escludenti: <strong style="color:{dec_color_esc}">{gaps.esc}</strong> · '
                        f'Gap pref.: <strong style="color:{dec_color_pref}">{gaps.pref}</strong>'
                        f"{confermato_html}</div>",
                        unsafe_allow_html=True,
                    )
                with col_no:
                    if st.button("⊘ Segna No-Go", key="no_go", width="stretch"):
                        b.status = "no-go"
                        b.gng_confermato = True
                        st.toast("⊘ No-Go registrato.", icon="⚠️")
                        st.rerun(scope="fragment")
                with col_yes:
                    yes_lbl = (
                        "✓ Conferma Go — Vai alla gara"
                        if sc.ra == "GO"
                        else "~ Conferma Go condizionale"
                        if sc.ra == "GO_CONDIZIONALE"
                        else "⊘ Conferma No-Go"
                    )
                    yes_type = (
                        "primary" if sc.ra in ("GO", "GO_CONDIZIONALE") else "secondary"
                    )
                    if st.button(yes_lbl, type=yes_type, key="conferma_gng", width="stretch"):
                        b.status = (
                            "go" if sc.ra in ("GO", "GO_CONDIZIONALE") else "no-go"
                        )
                        b.gng_confermato = True
                        st.toast(
                            f"✓ GO confermato! Score: {sc.score}/100"
                            if b.status == "go"
                            else "⊘ No-Go registrato",
                            icon="✅" if b.status == "go" else "⚠️",
                        )
                        st.rerun(scope="fragment")
            else:
                col_info, col_btn = st.columns([4, 1.3])
                with col_info:
                    st.markdown(
                        f'<div style="font-size:11.5px;color:{COLOR_T3};padding-top:6px">'
                        f'Checklist: <strong style="color:{COLOR_T1}">{cs.done}/{cs.total}</strong> · '
                        f'Gap escludenti: <strong style="color:{dec_color_esc}">{gaps.esc}</strong> · '
                        f'Gap pref.: <strong style="color:{dec_color_pref}">{gaps.pref}</strong>'
                        f"{confermato_html}</div>",
                        unsafe_allow_html=True,
                    )
                with col_btn:
                    if st.button("Modifica decisione", key="reset_gng", width="stretch"):
                        b.gng_confermato = False
                        b.status = "analisi"
                        st.rerun(scope="fragment")

    _tab_gng()
