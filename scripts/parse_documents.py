"""B1 CLI — parse a folder (or files) of tender documents with Tika.

Usage (from the repo root):
    python scripts/parse_documents.py <folder-or-files...> [--tender-id UUID] [--out PATH]

Writes a JSON list of ``ParsedDocument`` to ``--out`` (default:
``data/parsed/<tender_id>.json``) and prints that path to stdout for chaining
into ``extract_requirements.py``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from uuid import UUID, uuid4

import _bootstrap  # noqa: F401  (sys.path side-effect)

from smart_tender_assistant.ingestion import parse_files

_SUPPORTED_HINT = {".pdf", ".docx", ".doc", ".xlsx", ".csv", ".txt", ".html", ".eml", ".odt", ".rtf"}


def _collect(paths: list[str]) -> list[Path]:
    files: list[Path] = []
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            files.extend(sorted(f for f in p.rglob("*") if f.is_file()))
        elif p.is_file():
            files.append(p)
        else:
            print(f"warning: skipping missing path {p}", file=sys.stderr)
    return files


def main() -> int:
    ap = argparse.ArgumentParser(description="Parse tender documents with Tika (B1).")
    ap.add_argument("paths", nargs="+", help="Folder(s) or file(s) to parse")
    ap.add_argument("--tender-id", type=UUID, default=None, help="Tender UUID (default: random)")
    ap.add_argument("--out", type=Path, default=None, help="Output JSON path")
    args = ap.parse_args()

    tender_id = args.tender_id or uuid4()
    files = _collect(args.paths)
    if not files:
        print("error: no files to parse", file=sys.stderr)
        return 1

    print(f"Parsing {len(files)} file(s) for tender {tender_id} ...", file=sys.stderr)
    documents = parse_files(files, tender_id)

    out = args.out or Path("data/parsed") / f"{tender_id}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps([d.model_dump(mode="json") for d in documents], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Parsed {len(documents)} document(s).", file=sys.stderr)
    print(out)  # stdout: the path, for chaining
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
