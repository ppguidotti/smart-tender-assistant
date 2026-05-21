"""Configurazione frontend Smart Tender Assistant.

Legge da variabili d'ambiente (con fallback a .env) via pydantic-settings.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings

# Root del progetto (3 livelli su da questo file)
_PROJECT_ROOT = Path(__file__).resolve().parents[3]


class FrontendSettings(BaseSettings):
    """Impostazioni per il frontend Streamlit."""

    sta_api_mode: Literal["mock", "http"] = "mock"
    sta_api_base_url: str = "http://localhost:8000"
    sta_fixtures_path: Path = _PROJECT_ROOT / "tests" / "fixtures"
    log_level: str = "INFO"

    model_config = {"env_file": str(_PROJECT_ROOT / ".env"), "extra": "ignore"}


def get_settings() -> FrontendSettings:
    """Restituisce le impostazioni cached (singleton di fatto)."""
    return FrontendSettings()
