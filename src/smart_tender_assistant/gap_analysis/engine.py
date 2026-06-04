"""B4 retrieval+reasoning engine.

For one requirement: gather semantic (Qdrant) and structured (KB) evidence, then
ask the LLM whether the knowledge base covers it. The prompt and the
``coverage_status`` vocabulary are carried over verbatim from the validated
prototype; only the plumbing (no file I/O, no fixed sleep, KB injected) changed.
"""

from __future__ import annotations

import json

from smart_tender_assistant.config import Settings, get_settings
from smart_tender_assistant.gap_analysis.kb import CompanyKB

COVERAGE_PROMPT = """
Sei un assistente per la gap analysis di un singolo requisito di gara.

Riceverai un JSON con:
- requirement: il requisito da valutare
- retrieved_company_evidence.qdrant: evidenze semantiche recuperate da Qdrant
- retrieved_company_evidence.knowledge_graph: evidenze strutturate dalla knowledge base

Obiettivo: valutare se la knowledge base contiene evidenze sufficienti per coprire il requisito.
Non devi decidere GO/NO-GO. Devi solo valutare se le evidenze disponibili sono sufficienti.

Valori ammessi per coverage_status: covered | partially_covered | not_covered | unknown

Regole obbligatorie:
- Usa solo il JSON ricevuto. Non inventare certificazioni, albi, autorizzazioni, partnership, esperienze, documenti o competenze non presenti nelle evidenze.
- Le evidenze strutturate (certificazioni, albi, gare storiche) sono più forti quando contengono dati espliciti.
- Usa covered solo se le evidenze coprono chiaramente e direttamente il requisito.
- Usa partially_covered se le evidenze riguardano lo stesso tema ma mancano dettagli specifici.
- Usa not_covered solo se le evidenze dimostrano esplicitamente che il requisito non è soddisfatto, è assente, scaduto o revocato. La semplice mancanza di evidenze è unknown, mai not_covered.
- Usa unknown se non ci sono evidenze pertinenti o se sono generiche/deboli/su un tema diverso.
- Un requisito amministrativo o documentale (sopralluogo, PEC, polizza, CCNL, DURC, DGUE, firma digitale, garanzia) non è coperto da evidenze tecniche ICT generiche.
- Per requisiti con status diverso da covered, descrivi il gap in modo sintetico.

Restituisci solo JSON valido, senza markdown, nel formato:
{"requirement_id": "string", "coverage_status": "covered | partially_covered | not_covered | unknown", "gap_description": "string"}
""".strip()

_WEAK_PHRASES = (
    "non specificano", "non specifica", "non dimostrano", "non dimostra",
    "non forniscono", "non fornisce", "non sono presenti evidenze sufficienti",
    "non chiaramente",
)


def build_requirement_context(req: dict, kb: CompanyKB) -> dict:
    """Assemble the evidence JSON for one requirement (semantic + structured)."""
    return {
        "requirement": req,
        "retrieved_company_evidence": {
            "qdrant": kb.semantic_search(req["text"], top_k=2),
            "knowledge_graph": {
                "structured_company_data": kb.structured_company_kg(),
                "token_matches": kb.token_search(req["text"], top_k=3),
            },
        },
    }


def _client(settings: Settings):
    from openai import OpenAI

    base_url, api_key, model = settings.resolve_llm()
    return OpenAI(base_url=base_url, api_key=api_key, timeout=settings.llm_timeout_seconds), model


def _extract_json(raw: str) -> dict:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start, end = raw.find("{"), raw.rfind("}")
        if start == -1 or end <= start:
            raise
        return json.loads(raw[start : end + 1])


def coverage_for_requirement(req: dict, kb: CompanyKB, *, settings: Settings | None = None) -> dict:
    """Run retrieval + LLM and return ``{requirement_id, coverage_status, gap_description}``."""
    settings = settings or get_settings()
    context = build_requirement_context(req, kb)
    client, model = _client(settings)

    completion = client.chat.completions.create(
        model=model,
        temperature=0,
        max_tokens=500,
        messages=[
            {"role": "system", "content": COVERAGE_PROMPT},
            {"role": "user", "content": json.dumps(context, ensure_ascii=False)},
        ],
    )
    result = _extract_json(completion.choices[0].message.content or "")
    result.setdefault("requirement_id", req["id"])
    result.setdefault("coverage_status", "unknown")
    result.setdefault("gap_description", "")
    return _downgrade_weak(result)


def _downgrade_weak(result: dict) -> dict:
    """Mirror the prototype: weak 'partially_covered' justifications become 'unknown'."""
    desc = (result.get("gap_description") or "").lower()
    if result.get("coverage_status") == "partially_covered" and any(p in desc for p in _WEAK_PHRASES):
        result["coverage_status"] = "unknown"
    return result
