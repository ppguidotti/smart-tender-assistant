"""B1 — Document Ingestor (Tika-based, ``tika_raw`` strategy)."""

from smart_tender_assistant.ingestion.service import parse_file, parse_files

__all__ = ["parse_file", "parse_files"]
