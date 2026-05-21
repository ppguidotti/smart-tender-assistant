"""Palette colori semantici e token tipografici.

Fonte: skill smart-tender-design-system.
Importa sempre da qui — mai colori inline nel codice UI.
"""

from __future__ import annotations

import streamlit as st

# ---------------------------------------------------------------------------
# Colori semantici — decisione / gap / match
# ---------------------------------------------------------------------------

COLOR_GO = "#1D9E75"
COLOR_GO_RESERVATIONS = "#BA7517"
COLOR_NO_GO = "#A32D2D"
COLOR_INFO = "#185FA5"
COLOR_PARTIAL = "#888780"

# ---------------------------------------------------------------------------
# Colori di base — sfondo, bordi, testo
# ---------------------------------------------------------------------------

COLOR_BG_PRIMARY = "#FFFFFF"
COLOR_BG_SECONDARY = "#F5F4EF"
COLOR_BORDER = "#D3D1C7"
COLOR_TEXT_PRIMARY = "#2C2C2A"
COLOR_TEXT_SECONDARY = "#5F5E5A"

# ---------------------------------------------------------------------------
# VEM Sistemi brand (header/footer demo)
# ---------------------------------------------------------------------------

COLOR_VEM_NAVY = "#1B2440"
COLOR_VEM_ORANGE = "#E97825"

# ---------------------------------------------------------------------------
# Mapping semantici — usare questi, non i colori direttamente
# ---------------------------------------------------------------------------

DECISION_COLORS: dict[str, str] = {
    "GO": COLOR_GO,
    "GO_WITH_RESERVATIONS": COLOR_GO_RESERVATIONS,
    "NO_GO": COLOR_NO_GO,
}

DECISION_LABELS: dict[str, str] = {
    "GO": "GO",
    "GO_WITH_RESERVATIONS": "GO con riserve",
    "NO_GO": "NO GO",
}

DECISION_ICONS: dict[str, str] = {
    "GO": "✅",
    "GO_WITH_RESERVATIONS": "⚠️",
    "NO_GO": "❌",
}

SEVERITY_COLORS: dict[str, str] = {
    "CRITICAL": COLOR_NO_GO,
    "MAJOR": COLOR_GO_RESERVATIONS,
    "MINOR": COLOR_PARTIAL,
}

MATCH_STATUS_COLORS: dict[str, str] = {
    "FULL": COLOR_GO,
    "PARTIAL": COLOR_GO_RESERVATIONS,
    "NONE": COLOR_NO_GO,
    "UNKNOWN": COLOR_PARTIAL,
}

MATCH_STATUS_LABELS: dict[str, str] = {
    "FULL": "Completo",
    "PARTIAL": "Parziale",
    "NONE": "Assente",
    "UNKNOWN": "Da verificare",
}

CATEGORY_COLORS: dict[str, str] = {
    "QUALIFICAZIONE": "#6366F1",
    "NORMATIVA": "#0EA5E9",
    "TECNICA": "#8B5CF6",
    "AMMINISTRATIVA": "#64748B",
}

EVIDENCE_TYPE_COLORS: dict[str, str] = {
    "CERTIFICATION": "#6366F1",
    "REFERENCE": "#0EA5E9",
    "COMPETENCY": "#8B5CF6",
    "FINANCIAL": "#10B981",
    "DOCUMENT": "#64748B",
    "PARTNERSHIP": "#F59E0B",
}

EVIDENCE_TYPE_LABELS: dict[str, str] = {
    "CERTIFICATION": "Certificazioni",
    "REFERENCE": "Referenze",
    "COMPETENCY": "Competenze",
    "FINANCIAL": "Finanziario",
    "DOCUMENT": "Documenti",
    "PARTNERSHIP": "Partnership",
}

STATUS_COLORS: dict[str, str] = {
    "COMPLETED": COLOR_GO,
    "FAILED": COLOR_NO_GO,
    "QUEUED": COLOR_PARTIAL,
    "PARSING": COLOR_INFO,
    "EXTRACTING": COLOR_INFO,
    "ANALYZING": COLOR_INFO,
    "SCORING": COLOR_INFO,
    "REPORTING": COLOR_INFO,
}

STATUS_LABELS: dict[str, str] = {
    "QUEUED": "In coda",
    "PARSING": "Parsing documento",
    "EXTRACTING": "Estrazione requisiti",
    "ANALYZING": "Analisi gap",
    "SCORING": "Scoring",
    "REPORTING": "Generazione report",
    "COMPLETED": "Completata",
    "FAILED": "Errore",
}


def inject_custom_css() -> None:
    """Inietta CSS custom per sovrascrivere gli stili default di Streamlit."""
    st.markdown(
        f"""
        <style>
        /* Font e colori base */
        .stApp {{
            color: {COLOR_TEXT_PRIMARY};
        }}

        /* Badge inline */
        .sta-badge {{
            display: inline-block;
            padding: 0.15rem 0.55rem;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 600;
            letter-spacing: 0.02em;
        }}

        /* Source citation pill */
        .sta-citation {{
            display: inline-block;
            padding: 0.1rem 0.45rem;
            border-radius: 3px;
            font-size: 0.7rem;
            font-weight: 500;
            background: {COLOR_BG_SECONDARY};
            border: 1px solid {COLOR_BORDER};
            color: {COLOR_TEXT_SECONDARY};
        }}

        /* Card container */
        .sta-card {{
            padding: 1rem;
            border: 1px solid {COLOR_BORDER};
            border-radius: 8px;
            background: {COLOR_BG_PRIMARY};
            margin-bottom: 0.5rem;
        }}

        /* Tabella home — riga cliccabile */
        .sta-tender-row {{
            cursor: pointer;
            transition: background 0.15s ease;
        }}
        .sta-tender-row:hover {{
            background: {COLOR_BG_SECONDARY};
        }}

        /* Allinea a sinistra il testo dei bottoni terziari (nomi delle gare) e lo rende selezionabile */
        button[data-testid="stBaseButton-tertiary"],
        button[kind="tertiary"],
        div[class*="st-key-tender_"] button {{
            justify-content: flex-start !important;
            text-align: left !important;
            padding-left: 0px !important;
            width: 100% !important;
            -webkit-user-select: text !important;
            -moz-user-select: text !important;
            -ms-user-select: text !important;
            user-select: text !important;
        }}
        button[data-testid="stBaseButton-tertiary"] div,
        button[data-testid="stBaseButton-tertiary"] p,
        button[data-testid="stBaseButton-tertiary"] span,
        div[class*="st-key-tender_"] button div,
        div[class*="st-key-tender_"] button p,
        div[class*="st-key-tender_"] button span {{
            text-align: left !important;
            justify-content: flex-start !important;
            margin: 0 !important;
            -webkit-user-select: text !important;
            -moz-user-select: text !important;
            -ms-user-select: text !important;
            user-select: text !important;
        }}

        /* Nasconde la voce 'Dettaglio gara' dalla sidebar */
        a[data-testid="stSidebarNavLink"][href*="tender_detail"] {{
            display: none !important;
        }}

        /* Nasconde solo gli elementi di deploy e menu a destra (mantiene il pulsante per la sidebar a sinistra) */
        .stAppDeployButton, .stDeployButton, [data-testid="stHeaderActionElements"], div[data-testid="stDeployButton"] {{
            display: none !important;
        }}
        #MainMenu {{
            display: none !important;
        }}

        /* Nasconde la linea decorativa colorata in cima alla pagina */
        div[data-testid="stDecoration"] {{
            display: none !important;
        }}

        /* Rende l'header trasparente per non coprire il layout ma mantiene visibile il pulsante sidebar */
        header {{
            background-color: transparent !important;
        }}

        /* Regola il padding superiore */
        .stMainBlockContainer {{
            padding-top: 2rem !important;
        }}

        /* Sidebar styling */
        section[data-testid="stSidebar"] {{
            background: {COLOR_BG_SECONDARY};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
