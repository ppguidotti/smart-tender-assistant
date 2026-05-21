from pydantic import BaseModel


class RequirementSource(BaseModel):
    documento: str
    sezione: str | None = None


class ExtractedRequirement(BaseModel):
    id: str
    testo_originale: str
    requisito_normalizzato: str
    categoria: str
    tipo: str
    fonte: RequirementSource
    riferimenti_normativi: list[str] = []
    evidenze_richieste: list[str] = []
    penale_associata: str | None = None
    scadenza: str | None = None
    impatto_go_no_go: str


class ExtractionResult(BaseModel):
    tender_id: str
    requirements: list[ExtractedRequirement]
