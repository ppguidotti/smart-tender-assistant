"""Layer di astrazione dati per il frontend.

Definisce il Protocol `TenderApiClient` e la factory `get_api_client()`.
Oggi restituisce `MockApiClient` (fixture JSON), domani `HttpApiClient` (B8).
Il resto dell'app non si accorge del cambio.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol, runtime_checkable

import streamlit as st

from smart_tender_assistant.frontend.config import get_settings
from smart_tender_assistant.frontend.models.schemas import (
    AdminChecklist,
    AuditEntry,
    Evidence,
    GapAnalysisResult,
    GapAnalysisSummary,
    Requirement,
    ReviewItem,
    TenderDecision,
    TenderListItem,
)

# ---------------------------------------------------------------------------
# Protocol — interfaccia astratta
# ---------------------------------------------------------------------------


@runtime_checkable
class TenderApiClient(Protocol):
    """Interfaccia per accesso dati. Mock oggi, HTTP domani."""

    def list_tenders(self) -> list[TenderListItem]: ...

    def get_requirements(self, tender_id: str) -> list[Requirement]: ...

    def get_gap_results(self, tender_id: str) -> list[GapAnalysisResult]: ...

    def get_gap_summary(self, tender_id: str) -> GapAnalysisSummary: ...

    def get_decision(self, tender_id: str) -> TenderDecision: ...

    def get_company_profile(self) -> list[Evidence]: ...

    def list_review_queue(self) -> list[ReviewItem]: ...

    def get_admin_checklist(self, tender_id: str) -> AdminChecklist | None: ...

    def get_audit_trail(self, tender_id: str) -> list[AuditEntry]: ...


# ---------------------------------------------------------------------------
# Mock implementation — legge da fixture JSON
# ---------------------------------------------------------------------------


def _load_json(path: Path) -> dict | list:
    """Carica un file JSON da disco."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


class MockApiClient:
    """Client che legge dati dalle fixture in tests/fixtures/.

    Le modifiche (es. profilo, review) sono persistite in session_state
    per la durata della sessione Streamlit.
    """

    def __init__(self, fixtures_path: Path) -> None:
        self._fixtures = fixtures_path

    def list_tenders(self) -> list[TenderListItem]:
        """Restituisce la lista gare dalla fixture."""
        data = _load_json(self._fixtures / "tender_list.json")
        return [TenderListItem.model_validate(item) for item in data]

    def get_requirements(self, tender_id: str) -> list[Requirement]:
        """Restituisce i requisiti di una gara."""
        short_id = tender_id.split("-")[0]
        path = self._fixtures / f"tender_{short_id}_requirements.json"
        if not path.exists():
            return []
        data = _load_json(path)
        return [Requirement.model_validate(item) for item in data]

    def get_gap_results(self, tender_id: str) -> list[GapAnalysisResult]:
        """Restituisce i risultati gap analysis."""
        short_id = tender_id.split("-")[0]
        path = self._fixtures / f"tender_{short_id}_gaps.json"
        if not path.exists():
            return []
        data = _load_json(path)
        return [GapAnalysisResult.model_validate(item) for item in data["results"]]

    def get_gap_summary(self, tender_id: str) -> GapAnalysisSummary:
        """Restituisce il summary della gap analysis."""
        short_id = tender_id.split("-")[0]
        path = self._fixtures / f"tender_{short_id}_gaps.json"
        data = _load_json(path)
        return GapAnalysisSummary.model_validate(data["summary"])

    def get_decision(self, tender_id: str) -> TenderDecision:
        """Restituisce la decisione GO/NO-GO."""
        short_id = tender_id.split("-")[0]
        path = self._fixtures / f"tender_{short_id}_decision.json"
        data = _load_json(path)
        return TenderDecision.model_validate(data)

    def get_company_profile(self) -> list[Evidence]:
        """Restituisce le evidenze del profilo aziendale."""
        path = self._fixtures / "company_profile.json"
        if not path.exists():
            return []
        data = _load_json(path)
        return [Evidence.model_validate(item) for item in data]

    def list_review_queue(self) -> list[ReviewItem]:
        """Restituisce la coda di review HITL."""
        path = self._fixtures / "review_queue.json"
        if not path.exists():
            return []
        data = _load_json(path)
        return [ReviewItem.model_validate(item) for item in data]

    def get_admin_checklist(self, tender_id: str) -> AdminChecklist | None:
        """Restituisce la checklist amministrativa. None se B6 non ancora girato."""
        short_id = tender_id.split("-")[0]
        path = self._fixtures / f"tender_{short_id}_checklist.json"
        if not path.exists():
            return None
        data = _load_json(path)
        return AdminChecklist.model_validate(data)

    def get_audit_trail(self, tender_id: str) -> list[AuditEntry]:
        """Restituisce l'audit trail della gara, lista vuota se non disponibile."""
        short_id = tender_id.split("-")[0]
        path = self._fixtures / f"tender_{short_id}_audit.json"
        if not path.exists():
            return []
        data = _load_json(path)
        return [AuditEntry.model_validate(item) for item in data]


# ---------------------------------------------------------------------------
# HTTP implementation — stub per quando B8 esisterà
# ---------------------------------------------------------------------------


class HttpApiClient:
    """Client HTTP verso il backend FastAPI (B8).

    Stub: tutte le chiamate sollevano NotImplementedError.
    Verrà implementato quando B8 sarà disponibile.
    """

    def __init__(self, base_url: str) -> None:
        self._base_url = base_url

    def list_tenders(self) -> list[TenderListItem]:
        raise NotImplementedError("HTTP client non ancora implementato — usa STA_API_MODE=mock")

    def get_requirements(self, tender_id: str) -> list[Requirement]:
        raise NotImplementedError("HTTP client non ancora implementato")

    def get_gap_results(self, tender_id: str) -> list[GapAnalysisResult]:
        raise NotImplementedError("HTTP client non ancora implementato")

    def get_gap_summary(self, tender_id: str) -> GapAnalysisSummary:
        raise NotImplementedError("HTTP client non ancora implementato")

    def get_decision(self, tender_id: str) -> TenderDecision:
        raise NotImplementedError("HTTP client non ancora implementato")

    def get_company_profile(self) -> list[Evidence]:
        raise NotImplementedError("HTTP client non ancora implementato")

    def list_review_queue(self) -> list[ReviewItem]:
        raise NotImplementedError("HTTP client non ancora implementato")

    def get_admin_checklist(self, tender_id: str) -> AdminChecklist | None:
        raise NotImplementedError("HTTP client non ancora implementato")

    def get_audit_trail(self, tender_id: str) -> list[AuditEntry]:
        raise NotImplementedError("HTTP client non ancora implementato")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


@st.cache_resource
def get_api_client() -> TenderApiClient:
    """Factory: restituisce il client appropriato in base a STA_API_MODE.

    Returns:
        MockApiClient se mode=mock, HttpApiClient se mode=http.
    """
    settings = get_settings()
    if settings.sta_api_mode == "mock":
        return MockApiClient(fixtures_path=settings.sta_fixtures_path)
    return HttpApiClient(base_url=settings.sta_api_base_url)
