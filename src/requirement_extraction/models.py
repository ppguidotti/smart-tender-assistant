from pydantic import BaseModel


class ExtractedRequirement(BaseModel):
    category: str
    requirement: str
    source_document: str
    evidence: str
    priority: str


class ExtractionResult(BaseModel):
    tender_id: str
    requirements: list[ExtractedRequirement]
