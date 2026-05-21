"""Pagina Profilo aziendale — CRUD evidenze."""

from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from uuid import uuid4

import pandas as pd
import streamlit as st

from smart_tender_assistant.frontend.models.schemas import Evidence
from smart_tender_assistant.frontend.services.api_client import get_api_client
from smart_tender_assistant.frontend.ui.theme import (
    COLOR_BG_SECONDARY,
    COLOR_BORDER,
    COLOR_INFO,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    EVIDENCE_TYPE_COLORS,
    EVIDENCE_TYPE_LABELS,
    inject_custom_css,
)

# Ordine canonico dei tipi di evidenza
_TYPE_ORDER = ["CERTIFICATION", "REFERENCE", "COMPETENCY", "FINANCIAL", "DOCUMENT", "PARTNERSHIP"]
_NEW_ID = "__new__"


# ---------------------------------------------------------------------------
# Session-state helpers
# ---------------------------------------------------------------------------


def _init_state() -> None:
    if "profile_evidences" not in st.session_state:
        st.session_state["profile_evidences"] = get_api_client().get_company_profile()
    if "selected_evidence_id" not in st.session_state:
        st.session_state["selected_evidence_id"] = None
    if "profile_last_updated" not in st.session_state:
        dates = [e.valid_from for e in st.session_state["profile_evidences"] if e.valid_from]
        st.session_state["profile_last_updated"] = max(dates) if dates else None
    st.session_state.setdefault("profile_show_inactive", False)


def _all_evidences() -> list[Evidence]:
    return st.session_state["profile_evidences"]


def _upsert(ev: Evidence) -> None:
    evs: list[Evidence] = st.session_state["profile_evidences"]
    idx = next((i for i, e in enumerate(evs) if e.evidence_id == ev.evidence_id), None)
    if idx is not None:
        evs[idx] = ev
    else:
        evs.append(ev)
    st.session_state["profile_last_updated"] = datetime.now()


def _deactivate(evidence_id: str) -> None:
    evs: list[Evidence] = st.session_state["profile_evidences"]
    idx = next((i for i, e in enumerate(evs) if e.evidence_id == evidence_id), None)
    if idx is not None:
        evs[idx] = evs[idx].model_copy(update={"active": False})
    st.session_state["profile_last_updated"] = datetime.now()


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------


def _render_header() -> None:
    col_title, col_m1, col_m2, col_btn = st.columns([2.5, 1.2, 1.8, 1.2])

    active_count = sum(1 for e in _all_evidences() if e.active)
    lu = st.session_state.get("profile_last_updated")
    if isinstance(lu, datetime):
        lu_str = lu.strftime("%d/%m/%Y %H:%M")
    elif isinstance(lu, date):
        lu_str = lu.strftime("%d/%m/%Y")
    else:
        lu_str = "—"

    with col_title:
        st.title("Profilo aziendale")
    with col_m1:
        st.metric("Evidenze attive", active_count)
    with col_m2:
        st.metric("Aggiornato il", lu_str)
    with col_btn:
        st.markdown("<div style='margin-top:1.4rem'></div>", unsafe_allow_html=True)
        if st.button("+ Nuova evidenza", type="primary", width="stretch"):
            st.session_state["selected_evidence_id"] = _NEW_ID


# ---------------------------------------------------------------------------
# Left panel — evidence list
# ---------------------------------------------------------------------------


def _render_evidence_list() -> None:
    evs = _all_evidences()
    show_inactive = st.session_state.get("profile_show_inactive", False)

    for ev_type in _TYPE_ORDER:
        active_of_type = [e for e in evs if e.type == ev_type and e.active]
        inactive_of_type = [e for e in evs if e.type == ev_type and not e.active]
        visible = active_of_type + (inactive_of_type if show_inactive else [])

        type_color = EVIDENCE_TYPE_COLORS.get(ev_type, "#888")
        type_label = EVIDENCE_TYPE_LABELS.get(ev_type, ev_type)
        count = len(active_of_type)

        st.markdown(
            f'<p style="font-size:0.72rem;font-weight:700;letter-spacing:0.06em;'
            f"color:{type_color};margin:0.6rem 0 0.1rem 0;"
            f'text-transform:uppercase">{type_label} ({count})</p>',
            unsafe_allow_html=True,
        )

        if not visible:
            st.markdown(
                f'<p style="font-size:0.78rem;color:{COLOR_TEXT_SECONDARY};'
                f'padding-left:0.4rem;margin:0">(nessuna evidenza)</p>',
                unsafe_allow_html=True,
            )
            continue

        for ev in visible:
            label = ev.title if len(ev.title) <= 34 else ev.title[:31] + "…"
            if not ev.active:
                label = f"{label} (disattivata)"

            if st.button(
                label,
                key=f"ev_{ev.evidence_id}",
                type="tertiary",
                width="stretch",
            ):
                st.session_state["selected_evidence_id"] = ev.evidence_id

    # Toggle "Mostra disattivate"
    inactive_total = sum(1 for e in evs if not e.active)
    if inactive_total:
        st.markdown("<div style='margin-top:0.8rem'></div>", unsafe_allow_html=True)
        st.toggle(
            f"Mostra disattivate ({inactive_total})",
            key="profile_show_inactive",
        )

    # CSS highlight iniettato DOPO i bottoni: a questo punto session_state riflette
    # già il click appena avvenuto (se c'è stato), quindi la selezione è corretta.
    selected_id = st.session_state.get("selected_evidence_id")
    if selected_id and selected_id != _NEW_ID:
        st.markdown(
            f"<style>"
            f'div[class*="st-key-ev_{selected_id}"] button {{'
            f"  background-color: {COLOR_BG_SECONDARY} !important;"
            f"  border-left: 3px solid {COLOR_INFO} !important;"
            f"  padding-left: 0.55rem !important;"
            f"}}"
            f"</style>",
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------------
# Right panel — form + attachments
# ---------------------------------------------------------------------------


def _render_placeholder() -> None:
    st.markdown(
        f'<div style="display:flex;align-items:center;justify-content:center;'
        f'height:260px;border:1px dashed {COLOR_BORDER};border-radius:8px">'
        f'<p style="color:{COLOR_TEXT_SECONDARY};font-size:0.95rem;text-align:center">'
        f"Seleziona un'evidenza dalla lista,<br>oppure crea una nuova.</p></div>",
        unsafe_allow_html=True,
    )


def _render_attachments(ev: Evidence) -> None:
    st.markdown("---")
    st.subheader(f"Allegati ({len(ev.proof_attachments)})")

    if ev.proof_attachments:
        for path_str in ev.proof_attachments:
            fname = Path(path_str).name
            col_name, col_dl = st.columns([5, 1])
            with col_name:
                st.markdown(
                    f'<code style="font-size:0.82rem">{fname}</code>',
                    unsafe_allow_html=True,
                )
            with col_dl:
                if st.button("↓", key=f"dl_{ev.evidence_id}_{fname}", help=f"Scarica {fname}"):
                    st.toast("Download non disponibile in MVP — connetti B9 storage.")
    else:
        st.markdown(
            f'<span style="font-size:0.85rem;color:{COLOR_TEXT_SECONDARY}">Nessun allegato.</span>',
            unsafe_allow_html=True,
        )

    if st.button("+ Aggiungi allegato", key=f"add_att_{ev.evidence_id}"):
        st.info("Upload allegati disponibile con B9 storage layer.")


def _render_form(selected_id: str | None) -> None:
    evs = _all_evidences()
    is_new = selected_id == _NEW_ID
    ev: Evidence | None = None

    if not is_new and selected_id:
        ev = next((e for e in evs if e.evidence_id == selected_id), None)

    # Badge tipo corrente (solo per evidenza esistente)
    if ev:
        color = EVIDENCE_TYPE_COLORS.get(ev.type, "#888")
        label = EVIDENCE_TYPE_LABELS.get(ev.type, ev.type)
        st.markdown(
            f'<span style="background:{color};color:#fff;padding:0.15rem 0.55rem;'
            f'border-radius:4px;font-size:0.8rem;font-weight:600">{label}</span>',
            unsafe_allow_html=True,
        )
        st.markdown("<div style='margin-bottom:0.4rem'></div>", unsafe_allow_html=True)

    form_key = f"ev_form_{selected_id}"
    with st.form(form_key):
        col_type, col_title = st.columns([1.2, 3])
        with col_type:
            type_idx = _TYPE_ORDER.index(ev.type) if ev and ev.type in _TYPE_ORDER else 0
            new_type = st.selectbox("Tipo *", options=_TYPE_ORDER, index=type_idx,
                                    format_func=lambda x: EVIDENCE_TYPE_LABELS.get(x, x))
        with col_title:
            new_title = st.text_input("Titolo *", value=ev.title if ev else "")

        new_desc = st.text_area("Descrizione", value=ev.description if ev else "", height=90)

        col_vf, col_vu = st.columns(2)
        with col_vf:
            new_vf = st.date_input("Valido dal", value=ev.valid_from if ev else None)
        with col_vu:
            new_vu = st.date_input("Valido fino al", value=ev.valid_until if ev else None)

        # Metadata editor
        st.markdown(
            f'<p style="font-size:0.85rem;font-weight:600;margin:0.4rem 0 0.2rem 0">Metadati</p>',
            unsafe_allow_html=True,
        )
        meta_rows = [{"Chiave": k, "Valore": v} for k, v in (ev.metadata if ev else {}).items()]
        meta_df = pd.DataFrame(meta_rows if meta_rows else [], columns=["Chiave", "Valore"])
        edited_meta = st.data_editor(
            meta_df,
            num_rows="dynamic",
            key=f"meta_{selected_id}",
            width="stretch",
            column_config={
                "Chiave": st.column_config.TextColumn("Chiave", width="medium"),
                "Valore": st.column_config.TextColumn("Valore", width="large"),
            },
            hide_index=True,
        )

        submit_label = "Crea evidenza" if is_new else "Salva modifiche"
        submitted = st.form_submit_button(submit_label, type="primary")

        if submitted:
            if not new_title.strip():
                st.error("Il titolo è obbligatorio.")
            else:
                new_meta: dict[str, str] = {}
                for _, row in edited_meta.iterrows():
                    k = str(row["Chiave"]).strip() if pd.notna(row["Chiave"]) else ""
                    v = str(row["Valore"]).strip() if pd.notna(row["Valore"]) else ""
                    if k:
                        new_meta[k] = v

                ev_id = str(uuid4()) if is_new else (ev.evidence_id if ev else str(uuid4()))
                saved = Evidence(
                    evidence_id=ev_id,
                    type=new_type,
                    title=new_title.strip(),
                    description=new_desc.strip(),
                    valid_from=new_vf if isinstance(new_vf, date) else None,
                    valid_until=new_vu if isinstance(new_vu, date) else None,
                    proof_attachments=ev.proof_attachments if ev else [],
                    metadata=new_meta,
                    active=ev.active if ev else True,
                )
                _upsert(saved)
                st.session_state["selected_evidence_id"] = ev_id
                st.success("Evidenza salvata." if not is_new else "Evidenza creata.")
                st.rerun()

    # Attiva/Disattiva — fuori dal form, solo per evidenze esistenti
    if not is_new and ev:
        st.markdown("<div style='margin-top:0.4rem'></div>", unsafe_allow_html=True)
        if ev.active:
            if st.button(
                "Disattiva evidenza",
                key=f"deact_{ev.evidence_id}",
                type="secondary",
                help="Segna come non più valida. Reversibile con 'Riattiva'.",
            ):
                _deactivate(ev.evidence_id)
                st.session_state["selected_evidence_id"] = None
                st.rerun()
        else:
            if st.button(
                "Riattiva evidenza",
                key=f"react_{ev.evidence_id}",
                type="secondary",
                help="Segna di nuovo come attiva.",
            ):
                _upsert(ev.model_copy(update={"active": True}))
                st.rerun()

    # Allegati — solo per evidenze esistenti
    if not is_new and ev:
        _render_attachments(ev)


# ---------------------------------------------------------------------------
# Main page
# ---------------------------------------------------------------------------

inject_custom_css()
_init_state()

_render_header()
st.divider()

col_list, col_detail = st.columns([1, 2])

with col_list:
    _render_evidence_list()

with col_detail:
    sid = st.session_state.get("selected_evidence_id")
    if sid is None:
        _render_placeholder()
    else:
        _render_form(sid)
