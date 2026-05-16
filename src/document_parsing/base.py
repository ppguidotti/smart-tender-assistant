from abc import ABC, abstractmethod
from pathlib import Path
from pydantic import BaseModel


class ParsedDocument(BaseModel):
    source_path: str
    parser: str
    text: str
    metadata: dict = {}


class DocumentParser(ABC):
    @abstractmethod
    def parse(self, path: Path) -> ParsedDocument:
        pass
