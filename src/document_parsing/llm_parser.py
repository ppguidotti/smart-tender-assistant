from pathlib import Path
from .base import DocumentParser, ParsedDocument


class LLMParser(DocumentParser):
    """
    Parser basato su LLM / Azure OpenAI.

    L'obiettivo non è solo estrarre testo grezzo,
    ma anche comprendere e strutturare le informazioni
    contenute nel bando.
    """

    def parse(self, path: Path) -> ParsedDocument:
        raise NotImplementedError("Parser LLM non ancora implementato.")
