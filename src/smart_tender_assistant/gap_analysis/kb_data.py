"""Pure parsing of the company knowledge base JSON files.

These functions turn the ``profilo_aziendale`` JSON (certificazioni, competenze,
referenze, core, storico_gare) into:
  * a trimmed *structured KG* dict fed to the LLM as evidence;
  * a flat *corpus* for keyword/token retrieval;
  * the *texts + payloads* to embed into the two Qdrant portfolio collections.

No external dependencies — shared by both the ``local`` and ``postgres`` KB
backends and by the loader script that populates PostgreSQL/Qdrant.
"""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path

PROFILE_SECTIONS = ["core", "certificazioni", "competenze", "referenze", "coda_revisione"]


def load_loose_json(path: str | Path) -> object:
    """Load JSON, falling back to a Python literal (the KB files use single quotes)."""
    text = Path(path).read_text(encoding="utf-8").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return ast.literal_eval(text)


def read_profile(kb_dir: str | Path) -> dict[str, object]:
    """Read all profile sections (+ storico_gare) into ``{section: data}``."""
    base = Path(kb_dir)
    sections: dict[str, object] = {}
    for name in PROFILE_SECTIONS:
        f = base / f"{name}.json"
        if f.is_file():
            sections[name] = load_loose_json(f)
    storico_dir = base / "storico_gare"
    if storico_dir.is_dir():
        sections["storico_gare"] = [
            load_loose_json(p) for p in sorted(storico_dir.glob("*.json"))
        ]
    return sections


def _strip_notes(d: dict) -> dict:
    return {k: v for k, v in d.items() if not k.startswith("_")}


def build_structured_kg(sections: dict) -> dict:
    """Trimmed structured company evidence passed to the LLM (token-budget aware)."""
    certs = (sections.get("certificazioni") or {}).get("certificazioni", [])
    refs = (sections.get("referenze") or {}).get("referenze", [])
    comp = sections.get("competenze") or {}
    indip = comp.get("certificazioni_aziendali_indipendenti", {})
    indip_certs = [c for soc, lst in indip.items() if isinstance(lst, list) for c in lst]
    storico = sections.get("storico_gare") or []

    return {
        "azienda": _strip_notes(sections.get("core") or {}),
        "certificazioni": [
            {
                "nome": c.get("nome"),
                "nome_normalizzato": c.get("nome_normalizzato"),
                "stato": c.get("stato"),
                "data_scadenza": c.get("data_scadenza"),
                "scope": c.get("scope"),
            }
            for c in certs
        ],
        "competenze_certificate": [
            {"nome": c.get("nome") or c.get("skill"), "livello": c.get("livello")}
            for c in indip_certs
        ],
        "referenze": [
            {
                "id": r.get("id"),
                "cliente": r.get("cliente"),
                "oggetto": r.get("oggetto"),
                "cpv": r.get("cpv"),
                "valore_contratto_eur": r.get("valore_contratto_eur"),
                "requisiti_dimostrati": r.get("requisiti_dimostrati", []),
            }
            for r in refs
        ],
        "storico_gare": [
            {
                "id": g.get("id"),
                "oggetto": g.get("oggetto"),
                "cpv": g.get("cpv"),
                "esito": g.get("esito_reale") or g.get("decisione_aziendale"),
                "nuove_evidenze_emerse": g.get("nuove_evidenze_emerse"),
            }
            for g in storico
            if isinstance(g, dict)
        ],
    }


def competenze_points(sections: dict) -> list[dict]:
    """Texts + payloads to index in ``portfolio_competenze``."""
    comp = sections.get("competenze") or {}
    out: list[dict] = []
    for area in comp.get("aree_tecniche", []):
        area_name = area.get("area", "")
        for c in area.get("competenze", []):
            skill = c.get("skill") or c.get("nome") or ""
            spec = ", ".join(c.get("specializzazioni", []))
            tags = ", ".join(c.get("tag_gara", []))
            text = f"{area_name} — {skill}. Specializzazioni: {spec}. Tag: {tags}. {c.get('note', '')}".strip()
            out.append(
                {
                    "id": f"comp-{len(out) + 1}",
                    "text": text,
                    "payload": {
                        "nome_competenza": skill,
                        "fonte_dati": area_name,
                        "livello": c.get("livello"),
                        "tag_gara": c.get("tag_gara", []),
                        "testo_vettorializzato": text,
                    },
                }
            )
    indip = comp.get("certificazioni_aziendali_indipendenti", {})
    for soc, lst in indip.items():
        if not isinstance(lst, list):
            continue
        for c in lst:
            text = f"Certificazione {c.get('nome')} (livello {c.get('livello')}). {c.get('note', '')}".strip()
            out.append(
                {
                    "id": f"cert-{len(out) + 1}",
                    "text": text,
                    "payload": {
                        "nome_competenza": c.get("nome"),
                        "fonte_dati": soc,
                        "livello": c.get("livello"),
                        "testo_vettorializzato": text,
                    },
                }
            )
    return out


def referenze_points(sections: dict) -> list[dict]:
    """Texts + payloads to index in ``portfolio_referenze``."""
    refs = (sections.get("referenze") or {}).get("referenze", [])
    out: list[dict] = []
    for r in refs:
        req = ", ".join(r.get("requisiti_dimostrati", []))
        text = (
            f"{r.get('oggetto', '')}. Cliente: {r.get('cliente', '')} "
            f"({r.get('tipo_cliente', '')}). CPV {r.get('cpv', '')}. "
            f"Requisiti dimostrati: {req}."
        ).strip()
        out.append(
            {
                "id": r.get("id") or f"ref-{len(out) + 1}",
                "text": text,
                "payload": {
                    "oggetto_progetto": r.get("oggetto"),
                    "nome_cliente": r.get("cliente"),
                    "cpv": r.get("cpv"),
                    "requisiti_dimostrati": r.get("requisiti_dimostrati", []),
                    "testo_vettorializzato": text,
                },
            }
        )
    return out


# --- keyword/token retrieval (replaces the Neo4j token match) ---------------

_STOPWORDS = {
    "deve", "devono", "essere", "avere", "con", "per", "del", "della", "dello",
    "dei", "degli", "delle", "alla", "allo", "alle", "agli", "nel", "nella",
    "nelle", "negli", "un", "una", "uno", "il", "lo", "la", "gli", "le", "di",
    "da", "in", "su", "che", "come", "entro", "relativo", "relativa", "concorrente",
    "fornitore", "appalto", "bando", "gara", "categoria", "informatica", "software",
    "pubblici", "dati", "attività", "tecniche", "conformità", "garantire",
    "contratto", "servizio", "servizi", "pacchetti", "sicurezza",
}


def normalize_text(text: object) -> str:
    s = "" if text is None else str(text)
    s = s.lower().replace("/", " ").replace("-", " ")
    s = re.sub(r"[^\w\sàèéìòù]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def tokenize(text: str) -> set[str]:
    return {w for w in normalize_text(text).split() if len(w) > 3 and w not in _STOPWORDS}


def build_corpus(sections: dict) -> list[dict]:
    """Flat list of evidence items (text + ref) for token search."""
    corpus: list[dict] = []
    for c in (sections.get("certificazioni") or {}).get("certificazioni", []):
        corpus.append(
            {
                "kind": "certificazione",
                "title": c.get("nome"),
                "text": f"{c.get('nome')} {c.get('scope', '')} {c.get('note', '')}",
                "item": {"nome": c.get("nome"), "stato": c.get("stato"), "scadenza": c.get("data_scadenza")},
            }
        )
    for p in competenze_points(sections):
        corpus.append({"kind": "competenza", "title": p["payload"].get("nome_competenza"), "text": p["text"], "item": p["payload"]})
    for p in referenze_points(sections):
        corpus.append({"kind": "referenza", "title": p["payload"].get("oggetto_progetto"), "text": p["text"], "item": p["payload"]})
    return corpus


def token_search(requirement_text: str, corpus: list[dict], top_k: int = 3) -> list[dict]:
    """Score corpus items by token overlap with the requirement; return top_k."""
    req_tokens = tokenize(requirement_text)
    if not req_tokens:
        return []
    scored = []
    for entry in corpus:
        matched = [t for t in req_tokens if t in normalize_text(entry["text"])]
        if matched:
            scored.append(
                {
                    "item_type": "kg_token_match",
                    "kind": entry["kind"],
                    "title": entry["title"],
                    "item": entry["item"],
                    "matched_terms": matched[:10],
                    "score": len(matched),
                }
            )
    return sorted(scored, key=lambda x: x["score"], reverse=True)[:top_k]
