from pathlib import Path
from tika import parser

from .base import DocumentParser, ParsedDocument


class TikaParser(DocumentParser):
    """
    Parser documentale basato su Apache Tika.
    """

    def parse(self, path: Path) -> ParsedDocument:
        parsed = parser.from_file(str(path))

        return ParsedDocument(
            source_path=str(path),
            parser="tika",
            text=parsed.get("content", "") or "",
            metadata=parsed.get("metadata", {}) or {},
        )