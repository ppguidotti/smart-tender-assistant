"""Bridge B2 → dashboard Streamlit.

Converte un ``ExtractionResult`` (output di ``extract_requirements.py``) nelle
fixture che il ``MockApiClient`` del frontend gia' legge:
  * ``tests/fixtures/bando_<bid>_requisiti.json``  (list[RequisitoBando])
  * ``tests/fixtures/bando_<bid>_checklist.json``  (list[ChecklistItemHTML], vuota)
  * upsert di una riga in ``tests/fixtures/bandi_html.json``

Cosi' i requisiti estratti dal vero compaiono nel tab "Requisiti & Gap" del
dettaglio gara, senza toccare il codice del frontend.

NB: B4 (gap analysis) non e' ancora girato, quindi lo stato dei requisiti e'
"parziale" ("estratto, da analizzare") — non "coperto". La nota riporta la
citazione originale: e' la traceability che vogliamo mostrare.

Uso (dalla root):
    python scripts/export_to_dashboard.py data/requirements/<tid>.json \\
        --bando-id live-edr --nome "Capitolato EDR (estrazione reale)" \\
        --ente "[PA locale]" --valore 52500 --scadenza 30/05/2026 --cpv 48730000-4
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

_FIXTURES = Path("tests/fixtures")


def _req_to_requisito(req: dict) -> dict:
    """Requirement (contratto B2) → RequisitoBando (dominio HTML del frontend)."""
    tipo = req["type"]
    is_info = tipo == "INFORMATIVO"
    citation = (req.get("text_original") or "").strip()
    nota = f'Fonte: "{citation[:140]}{"…" if len(citation) > 140 else ""}"' if citation else None
    return {
        "id": req["requirement_id"],
        "cat": req["category"],
        "txt": req["text_normalized"],
        "fonte": Path(req["source"]["document_name"]).stem[:24],
        "tipo": tipo,
        # Nessuna gap analysis ancora: INFORMATIVO→info, gli altri→parziale (da verificare).
        "status": "info" if is_info else "parziale",
        "ml": "Estratto da B2 — gap analysis non eseguita",
        "mt": "gr" if is_info else "am",
        "nota": nota,
    }


def _upsert_bando(bid: str, meta: dict, files: list[str]) -> None:
    path = _FIXTURES / "bandi_html.json"
    bandi: list[dict] = json.loads(path.read_text(encoding="utf-8"))
    entry = {
        "id": bid,
        "nome": meta["nome"],
        "short_nome": meta.get("short_nome") or meta["nome"][:24],
        "ente": meta["ente"],
        "valore": meta["valore"],
        "scadenza": meta["scadenza"],
        "giorni_mancanti": meta["giorni_mancanti"],
        "canale": meta["canale"],
        "cpv": meta["cpv"],
        "status": "analisi",
        "uploaded_at": meta.get("uploaded_at"),
        "files": files,
        "analisi_completa": True,
        "gng_confermato": False,
    }
    bandi = [b for b in bandi if b["id"] != bid]  # idempotente: rimpiazza
    bandi.insert(0, entry)
    path.write_text(json.dumps(bandi, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Esporta i requisiti B2 nella dashboard.")
    ap.add_argument("result", type=Path, help="ExtractionResult JSON (da extract_requirements.py)")
    ap.add_argument("--bando-id", default="live-edr")
    ap.add_argument("--nome", default="Capitolato EDR — estrazione B2 reale")
    ap.add_argument("--short-nome", default="EDR — estrazione reale")
    ap.add_argument("--ente", default="[PA locale]")
    ap.add_argument("--valore", type=float, default=52500)
    ap.add_argument("--scadenza", default="30/05/2026")
    ap.add_argument("--giorni-mancanti", type=int, default=8)
    ap.add_argument("--canale", default="MePA")
    ap.add_argument("--cpv", default="48730000-4")
    args = ap.parse_args()

    result = json.loads(args.result.read_text(encoding="utf-8"))
    requirements: list[dict] = result["requirements"]
    if not requirements:
        print("error: nessun requisito nell'ExtractionResult", flush=True)
        return 1

    requisiti = [_req_to_requisito(r) for r in requirements]
    files = sorted({r["source"]["document_name"] for r in requirements})

    bid = args.bando_id
    (_FIXTURES / f"bando_{bid}_requisiti.json").write_text(
        json.dumps(requisiti, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (_FIXTURES / f"bando_{bid}_checklist.json").write_text("[]\n", encoding="utf-8")
    _upsert_bando(
        bid,
        {
            "nome": args.nome,
            "short_nome": args.short_nome,
            "ente": args.ente,
            "valore": args.valore,
            "scadenza": args.scadenza,
            "giorni_mancanti": args.giorni_mancanti,
            "canale": args.canale,
            "cpv": args.cpv,
        },
        files,
    )

    by_cat: dict[str, int] = {}
    for r in requisiti:
        by_cat[r["cat"]] = by_cat.get(r["cat"], 0) + 1
    print(f"Esportato bando '{bid}': {len(requisiti)} requisiti {by_cat}")
    print(f"  → tests/fixtures/bando_{bid}_requisiti.json")
    print(f"  → riga aggiunta in tests/fixtures/bandi_html.json (in cima alla lista)")
    print("Apri la dashboard: il bando compare in Dashboard bandi (stato 'In analisi').")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
