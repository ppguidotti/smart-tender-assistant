"""Entry point dell'applicazione Streamlit Smart Tender Assistant.

Configura la navigazione multipage e il layout globale.
Lanciare con: streamlit run src/smart_tender_assistant/frontend/app.py
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from smart_tender_assistant.frontend.ui.theme import (
    COLOR_VEM_NAVY,
    inject_custom_css,
)


def _configure_page() -> None:
    """Configurazione globale della pagina Streamlit."""
    st.set_page_config(
        page_title="Smart Tender Assistant",
        page_icon="📋",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_custom_css()


def _build_navigation() -> None:
    """Costruisce la navigazione multipage via st.navigation()."""
    pages_dir = Path(__file__).parent / "pages"

    home = st.Page(str(pages_dir / "home.py"), title="Lista gare", icon="🏠", default=True)
    detail = st.Page(str(pages_dir / "tender_detail.py"), title="Dettaglio gara", icon="📋")
    profile = st.Page(str(pages_dir / "profile.py"), title="Profilo aziendale", icon="👤")
    review = st.Page(str(pages_dir / "review_queue.py"), title="Review Queue", icon="🔍")

    nav = st.navigation(
        [home, detail, profile, review],
        position="hidden",
    )

    # Header sidebar
    with st.sidebar:
        st.markdown(
            f'<div style="padding:0.5rem 0 1rem 0">'
            f'<span style="color:{COLOR_VEM_NAVY};font-weight:700;font-size:1.1rem">'
            f"Smart Tender Assistant</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
        st.page_link(home, label="Lista gare", icon="🏠")
        st.page_link(profile, label="Profilo aziendale", icon="👤")
        st.page_link(review, label="Review Queue", icon="🔍")

    nav.run()


def main() -> None:
    """Entry point principale."""
    _configure_page()
    _build_navigation()


def run() -> None:
    """Entry point per il comando `sta-frontend` (pyproject.toml script)."""
    import sys

    from streamlit.web.cli import main as st_main

    sys.argv = ["streamlit", "run", str(Path(__file__).resolve()), "--server.headless=true"]
    st_main()


if __name__ == "__main__":
    main()
