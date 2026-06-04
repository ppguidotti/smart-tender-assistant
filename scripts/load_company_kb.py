"""Load the company knowledge base into PostgreSQL + Qdrant (B4 setup).

Reads the ``profilo_aziendale`` JSON files and:
  1. upserts each section into PostgreSQL ``company_profile_kb`` (system of record);
  2. (re)builds the two Qdrant portfolio collections (derived index).

Run once after the postgres + qdrant containers are up (docker compose up -d
postgres qdrant) and the schema is applied (db/schema.sql).

Usage (from the repo root):
    python scripts/load_company_kb.py [--kb-dir PATH] [--skip-qdrant] [--skip-pg]
"""

from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401  (sys.path side-effect)

from smart_tender_assistant.config import get_settings
from smart_tender_assistant.gap_analysis import kb_data
from smart_tender_assistant.gap_analysis.kb import build_qdrant_collections


def _load_pg(sections: dict, dsn: str) -> None:
    import psycopg
    from psycopg.types.json import Jsonb

    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        for section, data in sections.items():
            cur.execute(
                """
                INSERT INTO company_profile_kb (section, data, updated_at)
                VALUES (%s, %s, now())
                ON CONFLICT (section)
                DO UPDATE SET data = EXCLUDED.data, updated_at = now()
                """,
                (section, Jsonb(data)),
            )
        conn.commit()
    print(f"PostgreSQL: {len(sections)} sezioni upsertate in company_profile_kb")


def _build_qdrant(sections: dict, settings) -> None:
    from qdrant_client import QdrantClient

    qclient = QdrantClient(url=settings.qdrant_url)
    build_qdrant_collections(qclient, sections, settings, recreate=True)
    for coll in (settings.qdrant_collection_competenze, settings.qdrant_collection_referenze):
        info = qclient.get_collection(coll)
        print(f"Qdrant: '{coll}' → {info.points_count} punti")


def main() -> int:
    ap = argparse.ArgumentParser(description="Carica la KB aziendale in PG + Qdrant (B4).")
    ap.add_argument("--kb-dir", default=None, help="Cartella profilo_aziendale (default: config)")
    ap.add_argument("--skip-pg", action="store_true", help="Non scrivere su PostgreSQL")
    ap.add_argument("--skip-qdrant", action="store_true", help="Non ricostruire Qdrant")
    args = ap.parse_args()

    settings = get_settings()
    kb_dir = args.kb_dir or settings.company_kb_dir
    sections = kb_data.read_profile(kb_dir)
    if not sections:
        print(f"error: nessun JSON di profilo trovato in {kb_dir}", file=sys.stderr)
        return 1
    print(f"Sezioni lette da {kb_dir}: {', '.join(sections)}")

    if not args.skip_pg:
        try:
            _load_pg(sections, settings.pg_dsn)
        except Exception as exc:  # psycopg mancante o PG giù
            print(f"warning: load PostgreSQL saltato: {exc}", file=sys.stderr)

    if not args.skip_qdrant:
        try:
            _build_qdrant(sections, settings)
        except Exception as exc:
            print(f"warning: build Qdrant saltato: {exc}", file=sys.stderr)

    comp = len(kb_data.competenze_points(sections))
    ref = len(kb_data.referenze_points(sections))
    print(f"\nKB pronta — competenze indicizzabili: {comp}, referenze: {ref}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
