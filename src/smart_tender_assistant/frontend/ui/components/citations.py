"""Componente source_citation — pillola cliccabile con popover per traceability.

Mostra la sezione di origine del requisito e, al click, il testo originale
completo con eventuali riferimenti normativi. È il differenziatore chiave
del sistema: ogni dato mostrato è tracciabile alla fonte.
"""

from __future__ import annotations

import streamlit as st

from smart_tender_assistant.frontend.models.schemas import Reference, SourceLocation
from smart_tender_assistant.frontend.ui.theme import COLOR_BG_SECONDARY, COLOR_TEXT_SECONDARY


def _format_section_label(source: SourceLocation) -> str:
    """Genera l'etichetta breve della sezione (es. 'Art. 5 — Req. partecipazione')."""
    if source.section_title:
        label = source.section_title
        # Tronca a 35 char per la pillola
        if len(label) > 35:
            label = label[:32] + "…"
        return label
    return f"p. {source.page}"


def source_citation(
    source: SourceLocation,
    text_original: str = "",
    normative_refs: list[Reference] | None = None,
    *,
    key: str = "",
) -> None:
    """Renderizza una pillola cliccabile che apre un popover con il testo originale.

    Args:
        source: Posizione nel documento sorgente.
        text_original: Testo originale completo dal bando (opzionale).
        normative_refs: Lista di riferimenti normativi opzionali.
        key: Chiave univoca per il popover Streamlit.
    """
    label = _format_section_label(source)

    with st.popover(f"📄 {label}", width="content"):
        st.markdown(
            f'<p style="font-size:0.75rem;color:{COLOR_TEXT_SECONDARY};'
            f'margin-bottom:0.3rem">Fonte: <b>{source.document_name}</b>, '
            f"pagina {source.page}</p>",
            unsafe_allow_html=True,
        )

        if text_original:
            st.markdown(
                f'<div style="background:{COLOR_BG_SECONDARY};padding:0.8rem;'
                f"border-radius:6px;font-size:0.85rem;line-height:1.5;"
                f'border-left:3px solid {COLOR_TEXT_SECONDARY}">'
                f"{text_original}</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<p style="font-size:0.8rem;color:{COLOR_TEXT_SECONDARY};'
                f'font-style:italic">Testo originale non disponibile.</p>',
                unsafe_allow_html=True,
            )

        if normative_refs:
            refs_text = ", ".join(
                f"{r.law}" + (f" {r.article}" if r.article else "") for r in normative_refs
            )
            st.markdown(
                f'<p style="font-size:0.75rem;color:{COLOR_TEXT_SECONDARY};'
                f'margin-top:0.5rem">📚 Riferimenti: {refs_text}</p>',
                unsafe_allow_html=True,
            )
