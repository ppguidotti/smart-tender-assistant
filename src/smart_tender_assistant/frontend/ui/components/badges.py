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
    st.markdown(severity_badge_html(severity), unsafe_allow_html=True)

def severity_badge_html(severity: str) -> str:
    color = SEVERITY_COLORS.get(severity, "#888")
    return f'<span class="sta-badge" style="background:{color};color:#fff">{severity}</span>'


def match_status_badge(status: str) -> None:
    """Badge per match status (FULL/PARTIAL/NONE/UNKNOWN)."""
    st.markdown(match_status_badge_html(status), unsafe_allow_html=True)

def match_status_badge_html(status: str) -> str:
    color = MATCH_STATUS_COLORS.get(status, "#888")
    label = MATCH_STATUS_LABELS.get(status, status)
    return f'<span class="sta-badge" style="background:{color};color:#fff">{label}</span>'


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


# ---------------------------------------------------------------------------
# Colori e labels per tipo requisito
# ---------------------------------------------------------------------------

_TYPE_COLORS: dict[str, str] = {
    "ESCLUDENTE": SEVERITY_COLORS.get("CRITICAL", "#A32D2D"),
    "PREFERENZIALE": DECISION_COLORS.get("GO_WITH_RESERVATIONS", "#BA7517"),
    "INFORMATIVO": "#888780",
}

_TYPE_LABELS: dict[str, str] = {
    "ESCLUDENTE": "Escludente",
    "PREFERENZIALE": "Preferenziale",
    "INFORMATIVO": "Informativo",
}


def requirement_type_badge(req_type: str) -> None:
    """Badge per tipo requisito (ESCLUDENTE/PREFERENZIALE/INFORMATIVO)."""
    color = _TYPE_COLORS.get(req_type, "#888")
    label = _TYPE_LABELS.get(req_type, req_type.capitalize())
    st.markdown(
        f'<span class="sta-badge" style="background:{color};color:#fff">{label}</span>',
        unsafe_allow_html=True,
    )


def requirement_type_badge_html(req_type: str) -> str:
    """Restituisce HTML inline per un badge tipo requisito."""
    color = _TYPE_COLORS.get(req_type, "#888")
    label = _TYPE_LABELS.get(req_type, req_type.capitalize())
    return (
        f'<span style="background:{color};color:#fff;padding:0.15rem 0.55rem;'
        f'border-radius:4px;font-size:0.8rem;font-weight:600">{label}</span>'
    )


# ---------------------------------------------------------------------------
# Altri badge
# ---------------------------------------------------------------------------

_EFFORT_COLORS: dict[str, str] = {
    "LOW": "#2E7D32",     # Verde
    "MEDIUM": "#F57C00",  # Arancione
    "HIGH": "#D32F2F",    # Rosso
}

def effort_badge(effort: str) -> None:
    """Badge per l'effort di remediation."""
    color = _EFFORT_COLORS.get(effort, "#888")
    st.markdown(
        f'<span class="sta-badge" style="background:{color};color:#fff">{effort}</span>',
        unsafe_allow_html=True,
    )

def review_badge_html() -> str:
    """Restituisce HTML inline per il badge In Revisione."""
    return (
        '<span style="background:#FBC02D;color:#000;padding:0.2rem 0.6rem;'
        'border-radius:4px;font-size:0.8rem;font-weight:600">'
        '⚠ In revisione (HITL)</span>'
    )


# ---------------------------------------------------------------------------
# Risk severity badge (LOW / MEDIUM / HIGH) — usato nella tab Rischi
# ---------------------------------------------------------------------------

_RISK_SEV_COLORS: dict[str, str] = {
    "LOW": DECISION_COLORS["GO"],
    "MEDIUM": DECISION_COLORS["GO_WITH_RESERVATIONS"],
    "HIGH": DECISION_COLORS["NO_GO"],
}

_RISK_SEV_LABELS: dict[str, str] = {
    "LOW": "Basso",
    "MEDIUM": "Medio",
    "HIGH": "Alto",
}


def risk_severity_badge_html(severity: str) -> str:
    """HTML badge per severity rischio (LOW/MEDIUM/HIGH)."""
    color = _RISK_SEV_COLORS.get(severity, "#888")
    label = _RISK_SEV_LABELS.get(severity, severity)
    return f'<span class="sta-badge" style="background:{color};color:#fff">{label}</span>'


def risk_severity_badge(severity: str) -> None:
    """Badge per severity rischio (LOW/MEDIUM/HIGH)."""
    st.markdown(risk_severity_badge_html(severity), unsafe_allow_html=True)
