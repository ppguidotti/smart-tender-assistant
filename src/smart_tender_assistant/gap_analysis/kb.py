"""Company knowledge base for B4 — ``local`` and ``postgres`` backends.

Both expose the same retrieval surface used by the gap-analysis engine:
  * ``structured_company_kg()``  — structured evidence dict for the LLM
  * ``semantic_search(text, k)`` — Qdrant vector search (competenze + referenze)
  * ``token_search(text, k)``    — keyword overlap over the KB corpus

``local``   : reads the profile JSON and builds an in-memory Qdrant (zero infra).
``postgres``: reads the profile from PostgreSQL (system of record) and queries a
              Qdrant server whose collections were filled by ``load_company_kb.py``.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from smart_tender_assistant.config import Settings, get_settings
from smart_tender_assistant.gap_analysis import kb_data


@runtime_checkable
class CompanyKB(Protocol):
    def structured_company_kg(self) -> dict: ...
    def semantic_search(self, requirement_text: str, top_k: int = 2) -> list[dict]: ...
    def token_search(self, requirement_text: str, top_k: int = 3) -> list[dict]: ...


def build_qdrant_collections(qclient, sections: dict, settings: Settings, *, recreate: bool = True) -> None:
    """(Re)build the two portfolio collections from the parsed profile sections."""
    from qdrant_client import models

    from smart_tender_assistant.gap_analysis.embedding import embed_batch

    plan = [
        (settings.qdrant_collection_competenze, kb_data.competenze_points(sections)),
        (settings.qdrant_collection_referenze, kb_data.referenze_points(sections)),
    ]
    for coll, points in plan:
        if not points:
            continue
        vectors = embed_batch([p["text"] for p in points], settings.gap_embedding_model)
        dim = len(vectors[0])
        if qclient.collection_exists(coll):
            if not recreate:
                continue
            qclient.delete_collection(coll)
        qclient.create_collection(
            coll, vectors_config=models.VectorParams(size=dim, distance=models.Distance.COSINE)
        )
        qclient.upsert(
            coll,
            points=[
                models.PointStruct(id=i, vector=vectors[i], payload=points[i]["payload"])
                for i in range(len(points))
            ],
        )


class _BaseKB:
    """Shared retrieval logic given parsed ``sections`` and a Qdrant client."""

    def __init__(self, sections: dict, qclient, settings: Settings) -> None:
        self._sections = sections
        self._structured = kb_data.build_structured_kg(sections)
        self._corpus = kb_data.build_corpus(sections)
        self._q = qclient
        self._settings = settings
        self._collections = [
            settings.qdrant_collection_competenze,
            settings.qdrant_collection_referenze,
        ]

    def structured_company_kg(self) -> dict:
        return self._structured

    def token_search(self, requirement_text: str, top_k: int = 3) -> list[dict]:
        return kb_data.token_search(requirement_text, self._corpus, top_k)

    def semantic_search(self, requirement_text: str, top_k: int = 2) -> list[dict]:
        from smart_tender_assistant.gap_analysis.embedding import embed

        vector = embed(requirement_text, self._settings.gap_embedding_model)
        results: list[dict] = []
        for coll in self._collections:
            try:
                points = self._q.query_points(
                    collection_name=coll, query=vector, limit=top_k, with_payload=True
                ).points
            except Exception:  # collection missing / qdrant down → skip, fail soft
                continue
            for p in points:
                pl = p.payload or {}
                results.append(
                    {
                        "item_type": "qdrant_result",
                        "collection": coll,
                        "id": str(p.id),
                        "title": pl.get("nome_competenza") or pl.get("oggetto_progetto") or "",
                        "text": (pl.get("testo_vettorializzato") or "")[:700],
                        "score": p.score,
                        "payload": pl,
                    }
                )
        return sorted(results, key=lambda x: x["score"], reverse=True)[:top_k]


class LocalCompanyKB(_BaseKB):
    """KB from JSON files + in-memory Qdrant. No external services required."""

    def __init__(self, settings: Settings | None = None) -> None:
        settings = settings or get_settings()
        sections = kb_data.read_profile(settings.company_kb_dir)
        if not sections:
            raise RuntimeError(
                f"Company KB not found under {settings.company_kb_dir!r}. "
                "Set COMPANY_KB_DIR to the profilo_aziendale folder."
            )
        from qdrant_client import QdrantClient

        qclient = QdrantClient(location=":memory:")
        build_qdrant_collections(qclient, sections, settings, recreate=True)
        super().__init__(sections, qclient, settings)


class PostgresCompanyKB(_BaseKB):
    """KB from PostgreSQL (system of record) + Qdrant server (derived index)."""

    def __init__(self, settings: Settings | None = None) -> None:
        settings = settings or get_settings()
        sections = load_sections_from_pg(settings.pg_dsn)
        from qdrant_client import QdrantClient

        qclient = QdrantClient(url=settings.qdrant_url)
        super().__init__(sections, qclient, settings)


def load_sections_from_pg(dsn: str) -> dict:
    """Read the profile sections from the ``company_profile_kb`` table."""
    import psycopg

    sections: dict[str, object] = {}
    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        cur.execute("SELECT section, data FROM company_profile_kb")
        for section, data in cur.fetchall():
            sections[section] = data
    if not sections:
        raise RuntimeError(
            "Table company_profile_kb is empty — run scripts/load_company_kb.py first."
        )
    return sections


def get_company_kb(settings: Settings | None = None) -> CompanyKB:
    """Factory: pick the KB backend from ``KB_BACKEND`` (``local`` | ``postgres``)."""
    settings = settings or get_settings()
    if settings.kb_backend.lower() == "postgres":
        return PostgresCompanyKB(settings)
    return LocalCompanyKB(settings)
