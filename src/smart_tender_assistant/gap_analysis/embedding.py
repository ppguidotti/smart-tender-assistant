"""Local sentence-transformers embeddings for B4 retrieval.

Same model family as the original prototype
(``paraphrase-multilingual-MiniLM-L12-v2``). The model is loaded lazily and
cached per process.
"""

from __future__ import annotations

from functools import lru_cache


@lru_cache(maxsize=2)
def _model(name: str):
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(name)


def embed(text: str, model_name: str) -> list[float]:
    return _model(model_name).encode(text, normalize_embeddings=True).tolist()


def embed_batch(texts: list[str], model_name: str) -> list[list[float]]:
    vectors = _model(model_name).encode(list(texts), normalize_embeddings=True)
    return [v.tolist() for v in vectors]
