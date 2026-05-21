"""Badge components per decisioni, severity, categorie e stati.

Usano la palette da ui/theme.py — mai colori inline.
"""

from __future__ import annotations

import streamlit as st

from smart_tender_assistant.frontend.ui.theme import (
    CATEGORY_COLORS,
    DECISION_COLORS,
    DECISION_ICONS,
    DECISION_LABELS,
    MATCH_STATUS_COLORS,
    MATCH_STATUS_LABELS,
    SEVERITY_COLORS,
    STATUS_COLORS,
    STATUS_LABELS,
)


def decision_badge(decision: str, large: bool = False) -> None:
    """Renderizza un badge colorato per la decisione GO/NO-GO.

    Args:
        decision: Uno di "GO", "GO_WITH_RESERVATIONS", "NO_GO".
        large: Se True, usa font più grande (per header pagina).
    """
    color = DECISION_COLORS.get(decision, "#888")
    label = DECISION_LABELS.get(decision, decision)
    icon = DECISION_ICONS.get(decision, "")
    size = "1.1rem" if large else "0.8rem"
    padding = "0.3rem 0.8rem" if large else "0.15rem 0.55rem"
    st.markdown(
        f'<span class="sta-badge" style="background:{color};color:#fff;'
        f'font-size:{size};padding:{padding}">'
        f"{icon} {label}</span>",
        unsafe_allow_html=True,
    )


def severity_badge(severity: str) -> None:
    """Badge per gap severity (CRITICAL/MAJOR/MINOR)."""
    color = SEVERITY_COLORS.get(severity, "#888")
    st.markdown(
        f'<span class="sta-badge" style="background:{color};color:#fff">{severity}</span>',
        unsafe_allow_html=True,
    )


def match_status_badge(status: str) -> None:
    """Badge per match status (FULL/PARTIAL/NONE/UNKNOWN)."""
    color = MATCH_STATUS_COLORS.get(status, "#888")
    label = MATCH_STATUS_LABELS.get(status, status)
    st.markdown(
        f'<span class="sta-badge" style="background:{color};color:#fff">{label}</span>',
        unsafe_allow_html=True,
    )


def category_badge(category: str) -> None:
    """Badge per categoria requisito."""
    color = CATEGORY_COLORS.get(category, "#64748B")
    label = category.capitalize()
    st.markdown(
        f'<span class="sta-badge" style="background:{color};color:#fff">{label}</span>',
        unsafe_allow_html=True,
    )


def status_badge(status: str) -> None:
    """Badge per stato analisi gara."""
    color = STATUS_COLORS.get(status, "#888")
    label = STATUS_LABELS.get(status, status)
    st.markdown(
        f'<span class="sta-badge" style="background:{color};color:#fff">{label}</span>',
        unsafe_allow_html=True,
    )


def decision_badge_html(decision: str) -> str:
    """Restituisce HTML inline per un badge decisione (per uso in dataframe)."""
    color = DECISION_COLORS.get(decision, "#888")
    label = DECISION_LABELS.get(decision, decision)
    icon = DECISION_ICONS.get(decision, "")
    return (
        f'<span style="background:{color};color:#fff;padding:0.15rem 0.55rem;'
        f'border-radius:4px;font-size:0.8rem;font-weight:600">'
        f"{icon} {label}</span>"
    )
