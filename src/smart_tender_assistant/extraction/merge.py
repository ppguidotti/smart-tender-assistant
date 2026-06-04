"""Cross-document deduplication / merging of raw requirements (B2, stage 2).

Ports the Colab merging logic: normalise → embed → cosine-similarity →
connected-components grouping → merge each group into one record keeping the
fullest description and the union of source documents/citations.

Embeddings use a local sentence-transformers model. If that optional dependency
is unavailable, we fall back to grouping by normalised-text equality so the
pipeline still runs (degraded dedup, never a crash).
"""

from __future__ import annotations

import re

import numpy as np

from smart_tender_assistant.config import Settings, get_settings

_model_cache: dict[str, object] = {}


def clean_text(text: str) -> str:
    """Lowercase, drop punctuation, collapse whitespace — for similarity only."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def flatten_requirements(per_document: list[dict]) -> list[dict]:
    """Flatten ``[{document, requirements:[...]}, ...]`` into tagged requirement dicts."""
    flat: list[dict] = []
    for entry in per_document:
        document_name = entry["document"]
        for req in entry["requirements"]:
            flat.append(
                {
                    **req,
                    "document": document_name,
                    "normalized_description": clean_text(req.get("descrizione", "")),
                }
            )
    return flat


def _embeddings(requirements: list[dict], settings: Settings) -> np.ndarray | None:
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        return None

    model = _model_cache.get(settings.embedding_model_local)
    if model is None:
        model = SentenceTransformer(settings.embedding_model_local)
        _model_cache[settings.embedding_model_local] = model

    texts = [
        f"categoria: {r.get('categoria', '')}\n"
        f"tipo: {r.get('tipo', '')}\n"
        f"descrizione: {r.get('normalized_description', '')}"
        for r in requirements
    ]
    return np.asarray(model.encode(texts, normalize_embeddings=True))  # type: ignore[union-attr]


def _groups_from_similarity(sim: np.ndarray, threshold: float) -> list[list[int]]:
    """Connected components over the similarity graph (>= threshold = same node)."""
    n = sim.shape[0]
    visited: set[int] = set()
    groups: list[list[int]] = []
    for i in range(n):
        if i in visited:
            continue
        stack, group = [i], []
        while stack:
            cur = stack.pop()
            if cur in visited:
                continue
            visited.add(cur)
            group.append(cur)
            neighbours = np.where(sim[cur] >= threshold)[0]
            stack.extend(int(j) for j in neighbours if j != cur and j not in visited)
        groups.append(group)
    return groups


def _groups_by_text(requirements: list[dict]) -> list[list[int]]:
    """Fallback grouping: identical normalised description = duplicate."""
    by_text: dict[str, list[int]] = {}
    for idx, req in enumerate(requirements):
        by_text.setdefault(req["normalized_description"], []).append(idx)
    return list(by_text.values())


def merge_group(reqs: list[dict]) -> dict:
    """Merge duplicates: keep the longest description, union docs and citations."""
    best = max(reqs, key=lambda r: len(r.get("descrizione", "")))
    return {
        "categoria": best["categoria"],
        "tipo": best["tipo"],
        "descrizione": best["descrizione"],
        "valore": best.get("valore"),
        "unita": best.get("unita"),
        "confidenza": _max_confidence(reqs),
        "obbligatorio": any(r.get("obbligatorio", False) for r in reqs),
        "documenti": sorted({r["document"] for r in reqs}),
        "fonti_testuali": sorted({r.get("fonte_testuale", "") for r in reqs if r.get("fonte_testuale")}),
        "fonte_testuale": best.get("fonte_testuale", ""),
        "occorrenze": len(reqs),
    }


def consolidate(per_document: list[dict], *, settings: Settings | None = None) -> list[dict]:
    """Flatten, dedup and merge requirements coming from several documents."""
    settings = settings or get_settings()
    requirements = flatten_requirements(per_document)
    if not requirements:
        return []

    embeddings = _embeddings(requirements, settings)
    if embeddings is not None:
        sim = embeddings @ embeddings.T  # normalised vectors → cosine similarity
        groups = _groups_from_similarity(sim, settings.merge_similarity_threshold)
    else:
        groups = _groups_by_text(requirements)

    return [merge_group([requirements[i] for i in group]) for group in groups]


_CONFIDENCE_RANK = {"alta": 3, "media": 2, "bassa": 1}


def _max_confidence(reqs: list[dict]) -> str:
    return max(
        (r.get("confidenza", "bassa") for r in reqs),
        key=lambda c: _CONFIDENCE_RANK.get(c, 0),
    )
