"""B2 CLI — extract requirements from parsed documents with the LLM.

Usage (from the repo root):
    python scripts/extract_requirements.py <parsed.json> [--out PATH] [--min-confidence F]

``<parsed.json>`` is the output of ``parse_documents.py``. Writes an
``ExtractionResult`` JSON and prints a short summary. Requires the LLM
credentials in ``.env`` (see env.example).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import _bootstrap  # noqa: F401  (sys.path side-effect)

from smart_tender_assistant.extraction import extract_requirements
from smart_tender_assistant.models.schemas import ParsedDocument


def main() -> int:
    ap = argparse.ArgumentParser(description="Extract requirements with the LLM (B2).")
    ap.add_argument("parsed", type=Path, help="Parsed-documents JSON (from parse_documents.py)")
    ap.add_argument("--out", type=Path, default=None, help="Output JSON path")
    ap.add_argument("--min-confidence", type=float, default=0.7, help="Review threshold")
    args = ap.parse_args()

    if not args.parsed.is_file():
        print(f"error: parsed file not found: {args.parsed}", file=sys.stderr)
        return 1

    raw = json.loads(args.parsed.read_text(encoding="utf-8"))
    documents = [ParsedDocument.model_validate(d) for d in raw]
    if not documents:
        print("error: no documents in parsed file", file=sys.stderr)
        return 1

    tender_id = documents[0].tender_id
    print(f"Extracting requirements for tender {tender_id} ...", file=sys.stderr)
    result = extract_requirements(documents, tender_id, min_confidence=args.min_confidence)

    out = args.out or Path("data/requirements") / f"{tender_id}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(result.model_dump_json(indent=2), encoding="utf-8")

    s = result.extraction_summary
    print(f"  total requirements : {s.total_requirements}", file=sys.stderr)
    print(f"  by category        : {s.by_category}", file=sys.stderr)
    print(f"  by type            : {s.by_type}", file=sys.stderr)
    print(f"  avg confidence     : {s.avg_confidence}", file=sys.stderr)
    print(f"  needs review       : {len(result.needs_review)}", file=sys.stderr)
    print(out)  # stdout: the path
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
