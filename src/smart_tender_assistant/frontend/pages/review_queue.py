"""Pagina Review Queue — coda di revisione umana (HITL)."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from datetime import datetime, timedelta, timezone

from smart_tender_assistant.frontend.models.schemas import (
    Evidence,
    ReviewDecision,
    ReviewItem,
)
from smart_tender_assistant.frontend.services.api_client import get_api_client
from smart_tender_assistant.frontend.ui.components.badges import (
    requirement_type_badge,
    risk_severity_badge_html,
)
from smart_tender_assistant.frontend.ui.components.cards import evidence_card
from smart_tender_assistant.frontend.ui.components.citations import source_citation
from smart_tender_assistant.frontend.ui.theme import (
    COLOR_BG_SECONDARY,
    COLOR_BORDER,
    COLOR_GO,
    COLOR_GO_RESERVATIONS,
    COLOR_INFO,
    COLOR_NO_GO,
    COLOR_PARTIAL,
    COLOR_TEXT_SECONDARY,
    EVIDENCE_TYPE_LABELS,
    inject_custom_css,
)

# ---------------------------------------------------------------------------
# Costanti
# ---------------------------------------------------------------------------

_ITEM_TYPE_LABELS = {
    "AMBIGUOUS_REQUIREMENT": "Requisito ambiguo",
    "UNKNOWN_EVIDENCE_MATCH": "Match incerto",
    "NEW_REQUIREMENT_PATTERN": "Nuovo pattern",
}

_ACTION_LABELS = {
    "APPROVE_AS_SUGGESTED": "Approva come suggerito",
    "MODIFY": "Modifica payload",
    "REJECT": "Rifiuta",
    "ADD_NEW_EVIDENCE": "Aggiungi nuova evidenza",
}

_DECISION_COLORS = {
    "APPROVE_AS_SUGGESTED": COLOR_GO,
    "MODIFY": COLOR_GO_RESERVATIONS,
    "REJECT": COLOR_NO_GO,
    "ADD_NEW_EVIDENCE": COLOR_INFO,
}

_DECISION_LABELS = {
    "APPROVE_AS_SUGGESTED": "Approvato",
    "MODIFY": "Modificato",
    "REJECT": "Rifiutato",
    "ADD_NEW_EVIDENCE": "Nuova evid.",
}

_TABLE_COLS = [0.55, 1.7, 3.2, 1.4, 1.4, 1.7, 1.4]
_PRIORITY_ORDER = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
_EV_TYPES = ["CERTIFICATION", "REFERENCE", "COMPETENCY", "FINANCIAL", "DOCUMENT", "PARTNERSHIP"]

# ---------------------------------------------------------------------------
# State helpers
# ---------------------------------------------------------------------------


def _init_state() -> None:
    if "review_queue_items" not in st.session_state:
        st.session_state["review_queue_items"] = get_api_client().list_review_queue()
    st.session_state.setdefault("review_decisions", {})


def _items() -> list[ReviewItem]:
    return st.session_state["review_queue_items"]


def _decisions() -> dict[str, ReviewDecision]:
    return st.session_state["review_decisions"]


def _pending() -> list[ReviewItem]:
    d = _decisions()
    return [i for i in _items() if str(i.item_id) not in d]


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------


def _render_stats() -> None:
    pending = _pending()
    high = [i for i in pending if i.priority == "HIGH"]
    now = datetime.now(timezone.utc)
    cutoff = now + timedelta(hours=24)

    def _aware(dt: datetime) -> datetime:
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)

    soon = [i for i in pending if i.deadline and _aware(i.deadline) < cutoff]

    c1, c2, c3, _ = st.columns([1, 1, 1, 2])
    with c1:
        st.metric("In attesa", len(pending))
    with c2:
        st.metric("Alta priorità", len(high))
    with c3:
        label = "Scade < 24h"
        if soon:
            st.markdown(
                f'<div style="background:{COLOR_NO_GO};color:#fff;padding:0.5rem 1rem;'
                f'border-radius:8px;text-align:center">'
                f'<p style="font-size:0.8rem;margin:0;opacity:0.85">{label}</p>'
                f'<p style="font-size:1.8rem;font-weight:700;margin:0">{len(soon)}</p>'
                f"</div>",
                unsafe_allow_html=True,
            )
        else:
            st.metric(label, 0)


# ---------------------------------------------------------------------------
# Table
# ---------------------------------------------------------------------------


def _table_header() -> None:
    cols = st.columns(_TABLE_COLS)
    labels = ["PRI", "TIPO", "REQUISITO", "GARA", "CREATO", "SCADENZA", "STATO"]
    for col, lbl in zip(cols, labels):
        with col:
            st.markdown(
                f'<span style="font-size:0.7rem;font-weight:700;'
                f'color:{COLOR_TEXT_SECONDARY};letter-spacing:0.04em">{lbl}</span>',
                unsafe_allow_html=True,
            )
    st.markdown(
        f'<div style="border-bottom:1px solid {COLOR_BORDER};margin:0.2rem 0 0.4rem"></div>',
        unsafe_allow_html=True,
    )


def _relative_time(dt: datetime) -> str:
    now = datetime.now(timezone.utc)
    aware = dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    s = int((now - aware).total_seconds())
    if s < 3600:
        return f"{s // 60} min fa"
    if s < 86400:
        return f"{s // 3600} ore fa"
    if s < 172800:
        return f"ieri"
    return f"{s // 86400} giorni fa"


def _render_queue() -> ReviewItem | None:
    """Renderizza tabella e ritorna l'item da aprire in dialog (se bottone cliccato)."""
    all_items = _items()
    if not all_items:
        st.info("Nessun item in coda di revisione.")
        return None

    sorted_items = sorted(
        all_items,
        key=lambda i: (_PRIORITY_ORDER.get(i.priority, 9), i.created_at),
    )
    decisions = _decisions()
    now = datetime.now(timezone.utc)
    cutoff = now + timedelta(hours=24)

    def _aware(dt: datetime) -> datetime:
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)

    _table_header()
    to_open: ReviewItem | None = None

    for item in sorted_items:
        decision = decisions.get(str(item.item_id))
        req = item.context.requirement
        req_text = ""
        if req:
            t = req.text_normalized
            req_text = t if len(t) <= 45 else t[:42] + "…"

        short_tender = str(item.tender_id).split("-")[0]
        deadline_str = "—"
        deadline_warn = False
        if item.deadline:
            aware_dl = _aware(item.deadline)
            deadline_str = aware_dl.strftime("%d/%m %H:%M")
            deadline_warn = aware_dl < cutoff

        with st.container(border=True):
            cols = st.columns(_TABLE_COLS)

            with cols[0]:
                st.markdown(risk_severity_badge_html(item.priority), unsafe_allow_html=True)

            with cols[1]:
                st.markdown(
                    f'<span style="font-size:0.82rem">'
                    f'{_ITEM_TYPE_LABELS.get(item.item_type, item.item_type)}</span>',
                    unsafe_allow_html=True,
                )

            with cols[2]:
                st.markdown(
                    f'<span style="font-size:0.82rem">{req_text}</span>',
                    unsafe_allow_html=True,
                )

            with cols[3]:
                st.code(short_tender, language=None)

            with cols[4]:
                st.markdown(
                    f'<span style="font-size:0.8rem;color:{COLOR_TEXT_SECONDARY}">'
                    f"{_relative_time(item.created_at)}</span>",
                    unsafe_allow_html=True,
                )

            with cols[5]:
                color = COLOR_NO_GO if deadline_warn else COLOR_TEXT_SECONDARY
                warn = " ⚠" if deadline_warn else ""
                st.markdown(
                    f'<span style="font-size:0.8rem;color:{color}">'
                    f"{deadline_str}{warn}</span>",
                    unsafe_allow_html=True,
                )

            with cols[6]:
                if decision:
                    dc = _DECISION_COLORS[decision.action]
                    dl = _DECISION_LABELS[decision.action]
                    st.markdown(
                        f'<span style="background:{dc};color:#fff;padding:0.1rem 0.4rem;'
                        f'border-radius:4px;font-size:0.75rem;font-weight:600">{dl}</span>',
                        unsafe_allow_html=True,
                    )
                    if st.button("Modifica", key=f"mod_{item.item_id}", type="secondary"):
                        to_open = item
                else:
                    if st.button("Rivedi", key=f"btn_{item.item_id}", type="primary"):
                        to_open = item

    return to_open


# ---------------------------------------------------------------------------
# Dialog
# ---------------------------------------------------------------------------


@st.dialog("Revisione item", width="large")
def _review_dialog(item: ReviewItem) -> None:
    decisions = _decisions()
    existing = decisions.get(str(item.item_id))

    # Header
    pri_badge = risk_severity_badge_html(item.priority)
    type_label = _ITEM_TYPE_LABELS.get(item.item_type, item.item_type)
    short_tender = str(item.tender_id).split("-")[0]
    st.markdown(
        f"{pri_badge} &nbsp; **{type_label}** &nbsp;·&nbsp; "
        f'<code style="font-size:0.8rem">{short_tender}</code> &nbsp;·&nbsp; '
        f'<span style="font-size:0.82rem;color:{COLOR_TEXT_SECONDARY}">'
        f"{_relative_time(item.created_at)}</span>",
        unsafe_allow_html=True,
    )
    st.divider()

    # Requisito
    req = item.context.requirement
    if req:
        st.markdown("**Requisito**")
        col_type, col_id = st.columns([1, 3])
        with col_type:
            requirement_type_badge(req.type)
        with col_id:
            st.markdown(f'`{req.requirement_id}`  {req.text_normalized}')
        source_citation(req.source, req.text_original, key=f"rq_cite_{item.item_id}")
        if req.confidence < 0.8:
            st.caption(f"Confidenza: {req.confidence:.0%} ⚠")

    # Evidenze candidate
    evs: list[Evidence] = item.context.candidate_evidences
    if evs:
        st.markdown(f"**Evidenze candidate ({len(evs)})**")
        for ev in evs:
            evidence_card(ev)

    # Suggerimento sistema
    if item.context.auto_suggestion:
        st.info(f"Suggerimento sistema: {item.context.auto_suggestion}")

    st.divider()

    # Selezione azione (fuori dal form — cambia i campi condizionali)
    _ACTIONS = list(_ACTION_LABELS.keys())
    default_idx = _ACTIONS.index(existing.action) if existing else 0
    action = st.radio(
        "Azione *",
        _ACTIONS,
        index=default_idx,
        format_func=lambda x: _ACTION_LABELS[x],
        horizontal=True,
        key=f"action_radio_{item.item_id}",
    )

    # Form condizionale keyed per azione — si resetta quando l'azione cambia
    with st.form(f"rq_form_{item.item_id}_{action}"):
        modified_payload: dict[str, str] | None = None

        if action == "MODIFY":
            st.markdown("**Payload modificato**")
            rows = [{"Chiave": k, "Valore": v} for k, v in item.payload.items()]
            df = pd.DataFrame(rows if rows else [], columns=["Chiave", "Valore"])
            edited = st.data_editor(
                df, num_rows="dynamic", hide_index=True, width="stretch",
                key=f"payload_edit_{item.item_id}",
            )

        elif action == "ADD_NEW_EVIDENCE":
            st.markdown("**Nuova evidenza da aggiungere al profilo**")
            new_title = st.text_input(
                "Titolo evidenza *",
                value=existing.modified_payload.get("new_evidence_title", "") if existing and existing.modified_payload else "",
            )
            new_type = st.selectbox(
                "Tipo *",
                _EV_TYPES,
                format_func=lambda x: EVIDENCE_TYPE_LABELS.get(x, x),
            )

        notes_default = existing.reviewer_notes if existing else ""
        notes = st.text_area("Note revisore", value=notes_default, height=80,
                             placeholder="Motivo della decisione, contesto aggiuntivo…")

        prop_default = (action != "REJECT")
        propagate = st.checkbox("Propaga al profilo aziendale", value=prop_default)

        col_submit, col_cancel = st.columns(2)
        with col_submit:
            submitted = st.form_submit_button("Conferma decisione", type="primary", width="stretch")
        with col_cancel:
            cancelled = st.form_submit_button("Annulla", type="secondary", width="stretch")

        if cancelled:
            st.rerun()

        if submitted:
            if action == "REJECT" and not notes.strip():
                st.error("Le note sono obbligatorie per un rifiuto.")
            elif action == "ADD_NEW_EVIDENCE" and not new_title.strip():  # type: ignore[possibly-undefined]
                st.error("Il titolo dell'evidenza è obbligatorio.")
            else:
                if action == "MODIFY":
                    modified_payload = {
                        str(row["Chiave"]).strip(): str(row["Valore"]).strip()
                        for _, row in edited.iterrows()  # type: ignore[possibly-undefined]
                        if pd.notna(row["Chiave"]) and str(row["Chiave"]).strip()
                    }
                elif action == "ADD_NEW_EVIDENCE":
                    modified_payload = {
                        "new_evidence_title": new_title.strip(),  # type: ignore[possibly-undefined]
                        "new_evidence_type": new_type,  # type: ignore[possibly-undefined]
                    }

                decision = ReviewDecision(
                    item_id=item.item_id,
                    decided_by="ppguidotti",
                    decided_at=datetime.now(timezone.utc),
                    action=action,
                    modified_payload=modified_payload,
                    reviewer_notes=notes.strip(),
                    propagate_to_profile=propagate,
                )
                _decisions()[str(item.item_id)] = decision
                st.rerun()


# ---------------------------------------------------------------------------
# Main page
# ---------------------------------------------------------------------------

inject_custom_css()
_init_state()

st.title("Coda di revisione (HITL)")
st.markdown(
    f'<p style="color:{COLOR_TEXT_SECONDARY};margin-top:-0.5rem">Item che richiedono '
    f"valutazione umana prima di procedere con l'analisi.</p>",
    unsafe_allow_html=True,
)
st.divider()

_render_stats()
st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)

item_to_open = _render_queue()
if item_to_open:
    _review_dialog(item_to_open)
