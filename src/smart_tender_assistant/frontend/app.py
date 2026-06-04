"""Entry point dell'applicazione Streamlit Smart Tender Assistant.

Configura la navigazione multipage e il layout globale.
Allineato al prototipo `docs/STCA_Platform_v2.html` (sezioni GARE / ANALISI / SISTEMA).
Lanciare con: streamlit run src/smart_tender_assistant/frontend/app.py
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from smart_tender_assistant.frontend.services.api_client import get_api_client
from smart_tender_assistant.frontend.ui.theme import inject_custom_css


def _configure_page() -> None:
    """Configurazione globale della pagina Streamlit."""
    st.set_page_config(
        page_title="STCA — Smart Tender Compliance Assistant",
        page_icon="📋",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_custom_css()


def _build_navigation() -> None:
    """Costruisce la navigazione multipage via `st.navigation()`.

    Le icone usano la sintassi `:material/...:` di Streamlit (font interno
    garantito su tutti i browser/OS).
    """
    pages_dir = Path(__file__).parent / "pages"

    dashboard = st.Page(
        str(pages_dir / "home.py"),
        title="Dashboard",
        icon="📊",
        default=True,
    )
    repository = st.Page(
        str(pages_dir / "repository.py"),
        title="Repository",
        icon="📂",
    )
    detail = st.Page(
        str(pages_dir / "tender_detail.py"),
        title="Dettaglio gara",
        icon="📋",
    )
    roadmap = st.Page(
        str(pages_dir / "roadmap.py"),
        title="Roadmap aziendale",
        icon="🗺",
    )
    alerts = st.Page(
        str(pages_dir / "alerts.py"),
        title="Alert",
        icon="🔔",
    )
    storico = st.Page(
        str(pages_dir / "storico.py"),
        title="Storico gare",
        icon="🕐",
    )
    settings = st.Page(
        str(pages_dir / "profile.py"),
        title="Impostazioni",
        icon="⚙",
    )

    nav = st.navigation(
        [dashboard, repository, detail, roadmap, alerts, storico, settings],
        position="hidden",
    )

    _render_sidebar(dashboard, repository, roadmap, alerts, storico, settings)

    nav.run()


def _render_sidebar(
    dashboard: st.Page,
    repository: st.Page,
    roadmap: st.Page,
    alerts: st.Page,
    storico: st.Page,
    settings: st.Page,
) -> None:
    """Sidebar che ricalca quella del prototipo HTML (sezioni + badge + utente)."""
    client = get_api_client()
    try:
        bandi = client.list_bandi_html()
    except Exception:
        bandi = []
    n_bandi = len(bandi)
    n_pending = sum(1 for b in bandi if b.status == "pending")
    n_alerts = 2  # da HTML: badge alerts = 2

    bdg_bandi = f"  ·  {n_bandi}"
    bdg_pending = f"  ·  {n_pending}" if n_pending else ""
    bdg_alerts = f"  ·  {n_alerts}" if n_alerts else ""

    with st.sidebar:
        # Logo / brand
        st.markdown(
            '<div class="stca-sb-logo">'
            '<div class="mark">STCA</div>'
            '<div class="sub">Smart Tender Compliance Assistant</div>'
            "</div>",
            unsafe_allow_html=True,
        )

        # GARE
        st.markdown(
            '<div class="stca-sb-section">GARE</div>',
            unsafe_allow_html=True,
        )
        st.page_link(dashboard, label=f"Dashboard{bdg_bandi}")
        st.page_link(repository, label=f"Repository{bdg_pending}")

        # ANALISI
        st.markdown(
            '<div class="stca-sb-section">ANALISI</div>',
            unsafe_allow_html=True,
        )
        st.page_link(roadmap, label="Roadmap aziendale")
        st.page_link(alerts, label=f"Alert{bdg_alerts}")
        st.page_link(storico, label="Storico gare")

        # SISTEMA
        st.markdown(
            '<div class="stca-sb-section">SISTEMA</div>',
            unsafe_allow_html=True,
        )
        st.page_link(settings, label="Impostazioni")

        # Utente (pushato in fondo via margin-top:auto su .stca-sb-user)
        st.markdown(
            '<div class="stca-sb-user">'
            '<div class="av">AB</div>'
            "<div>"
            '<div class="name">A. Boschetti</div>'
            '<div class="role">Admin</div>'
            "</div></div>",
            unsafe_allow_html=True,
        )


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
