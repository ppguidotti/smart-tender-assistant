"""Componenti card per la visualizzazione di evidenze e altri blocchi informativi."""

from __future__ import annotations

import streamlit as st

from smart_tender_assistant.frontend.models.schemas import Evidence
from smart_tender_assistant.frontend.ui.theme import COLOR_BG_SECONDARY, COLOR_TEXT_SECONDARY


def evidence_card(evidence: Evidence) -> None:
    """Renderizza una card per una Evidence del profilo aziendale."""
    # Icone base per type
    icons = {
        "CERTIFICATION": "📜",
        "REFERENCE": "🏢",
        "COMPETENCY": "🧠",
        "FINANCIAL": "💰",
        "DOCUMENT": "📄",
        "PARTNERSHIP": "🤝",
    }
    icon = icons.get(evidence.type, "📌")

    # Costruzione del contenuto HTML
    html = f"""
    <div style="
        background: {COLOR_BG_SECONDARY};
        padding: 0.8rem;
        border-radius: 6px;
        margin-bottom: 0.5rem;
        border-left: 3px solid {COLOR_TEXT_SECONDARY};
    ">
        <div style="font-weight: 600; font-size: 0.9rem; margin-bottom: 0.3rem;">
            {icon} {evidence.title}
        </div>
        <div style="font-size: 0.85rem; line-height: 1.4;">
            {evidence.description}
        </div>
    """

    # Aggiunta di metadata se presenti (validità o altre info)
    meta_parts = []
    if evidence.valid_from or evidence.valid_until:
        v_from = evidence.valid_from.strftime("%Y-%m-%d") if evidence.valid_from else "N/A"
        v_until = evidence.valid_until.strftime("%Y-%m-%d") if evidence.valid_until else "N/A"
        meta_parts.append(f"Validità: {v_from} - {v_until}")

    if evidence.metadata:
        for k, v in evidence.metadata.items():
            meta_parts.append(f"{k.capitalize()}: {v}")

    if meta_parts:
        meta_str = " | ".join(meta_parts)
        html += f"""
        <div style="
            margin-top: 0.5rem;
            font-size: 0.75rem;
            color: {COLOR_TEXT_SECONDARY};
        ">
            {meta_str}
        </div>
        """

    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)
