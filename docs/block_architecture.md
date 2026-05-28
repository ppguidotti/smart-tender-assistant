# Smart Tender Assistant — Block Architecture & Interface Contracts

> **Documento di riferimento tecnico** per lo sviluppo modulare del sistema.
> Ogni blocco è definito con interfacce **input/output esplicite**: chi sviluppa un blocco sa esattamente cosa riceve e cosa deve produrre, senza dipendere dall'implementazione degli altri blocchi.
>
> **Principio guida**: interfacce stabili, implementazioni intercambiabili. Ogni blocco può essere sviluppato, testato e sostituito indipendentemente.

---

## Indice

1. [Diagramma a blocchi del sistema](#1-diagramma-a-blocchi-del-sistema)
2. [Convenzioni e principi](#2-convenzioni-e-principi)
3. [Shared data contracts (tipi condivisi)](#3-shared-data-contracts-tipi-condivisi)
4. [Blocchi del sistema](#4-blocchi-del-sistema)
   - [B1 — Document Ingestor](#b1--document-ingestor)
   - [B2 — Requirement Extractor](#b2--requirement-extractor)
   - [B3 — Company Profile KB](#b3--company-profile-kb)
   - [B4 — Gap Analyzer](#b4--gap-analyzer)
   - [B5 — Scoring Engine](#b5--scoring-engine)
   - [B6 — Report Generator](#b6--report-generator)
   - [B7 — Human-in-the-Loop Review Queue](#b7--human-in-the-loop-review-queue)
   - [B8 — Orchestrator / API Gateway](#b8--orchestrator--api-gateway)
   - [B9 — Storage Layer](#b9--storage-layer)
   - [B10 — Frontend / Dashboard](#b10--frontend--dashboard)
5. [Sequenza di sviluppo e parallelizzazione](#5-sequenza-di-sviluppo-e-parallelizzazione)
6. [Strategia di mock per sviluppo parallelo](#6-strategia-di-mock-per-sviluppo-parallelo)
7. [Testing strategy per blocco](#7-testing-strategy-per-blocco)

---

## 1. Diagramma a blocchi del sistema

```mermaid
flowchart LR
    U([Utente]) -->|upload bando| B10[B10<br/>Frontend]
    B10 -->|REST API| B8[B8<br/>Orchestrator]

    B8 -->|file| B1[B1<br/>Document<br/>Ingestor]
    B1 -->|ParsedDocument| B8
    B8 -->|ParsedDocument| B2[B2<br/>Requirement<br/>Extractor]
    B2 -->|Requirements[]| B8
    B8 -->|Requirements[]| B4[B4<br/>Gap<br/>Analyzer]
    B4 <-->|query/evidence| B3[B3<br/>Company<br/>Profile KB]
    B4 -->|GapAnalysis[]| B8
    B8 -->|GapAnalysis[]| B5[B5<br/>Scoring<br/>Engine]
    B5 -->|TenderDecision| B8
    B8 -->|tutti gli artefatti| B6[B6<br/>Report<br/>Generator]
    B6 -->|PDF + dashboard data| B8

    B4 -.ambigui.-> B7[B7<br/>HITL<br/>Review Queue]
    B7 -.aggiorna.-> B3

    B8 <-->|persistenza| B9[B9<br/>Storage Layer]
    B3 <-->|persistenza| B9
    B9 -->|dato strutturato| PG[(PostgreSQL<br/>system of record)]
    B9 -.indice vettoriale.-> QD[(Qdrant<br/>ricerca semantica)]
    B9 -.path ref.-> FS[/Filesystem locale<br/>PDF + report/]

    style B1 fill:#e1f5ff
    style B2 fill:#e1f5ff
    style B3 fill:#fff4e1
    style B4 fill:#e1f5ff
    style B5 fill:#e1f5ff
    style B6 fill:#e1f5ff
    style B7 fill:#ffe1e1
    style B8 fill:#f0e1ff
    style B9 fill:#fff4e1
    style B10 fill:#e1ffe1
    style PG fill:#e8f0fb
    style QD fill:#f0e8fb,stroke-dasharray: 4 3
    style FS fill:#f5f5f0,stroke-dasharray: 4 3
```

**Legenda colori:**
- 🟦 Blocchi di processamento (B1, B2, B4, B5, B6)
- 🟨 Blocchi di persistenza/knowledge (B3, B9)
- 🟧 Blocco human-in-the-loop (B7)
- 🟪 Orchestrazione (B8)
- 🟩 Frontend (B10)

---

## 2. Convenzioni e principi

### Formato dei contratti
- Tutti gli schemi sono definiti come **JSON Schema** (rappresentati qui in Python/Pydantic syntax per leggibilità)
- Tutti gli ID sono **UUID v4** salvo dove diversamente specificato
- Tutte le date/ora sono **ISO 8601** in UTC (`2026-05-15T14:30:00Z`)
- Tutti i confidence score sono **float in [0, 1]**
- Tutte le enum sono **stringhe maiuscole** con underscore (`NO_GO`, non `noGo` o `no-go`)

### Principi di interfaccia
1. **Idempotenza**: chiamare un blocco due volte con lo stesso input deve produrre lo stesso output (a meno di timestamp)
2. **Stateless dove possibile**: i blocchi non mantengono stato; lo stato vive in B9 (Storage)
3. **Fail loud**: errori espliciti con codice + messaggio, no fallback silenziosi
4. **Versionamento**: ogni schema ha campo `schema_version` per evoluzioni future

### Comunicazione tra blocchi
- **In-process MVP**: chiamate Python dirette (un singolo processo FastAPI)
- **Produzione**: REST API tra blocchi separabili (ogni blocco diventa un microservizio se necessario)
- **L'interfaccia di codice non cambia** tra i due scenari grazie a Pydantic + dependency injection

---

## 3. Shared data contracts (tipi condivisi)

Tipi riusati da più blocchi. **Modificare uno di questi impatta tutti i blocchi che lo usano** — discutere in team prima.

### `Reference` — riferimento normativo o documentale
```python
class Reference:
    law: str              # "D.lgs. 36/2023" | "GDPR" | "L. 136/2010"
    article: str | None   # "Art. 11 c.2" | "Art. 28"
    url: str | None       # link a Normattiva/EUR-Lex se disponibile
```

### `SourceLocation` — puntatore alla fonte (per citation/traceability)
```python
class SourceLocation:
    document_id: UUID
    document_name: str       # "Capitolato.pdf"
    section_id: str | None   # "art-8"
    section_title: str | None  # "Art. 8 - Obblighi dell'Appaltatore"
    page: int
    char_start: int | None
    char_end: int | None
```

### `Money` — valori monetari
```python
class Money:
    amount: float
    currency: str = "EUR"
    is_net: bool             # true = al netto IVA
```

### `Evidence` — singola prova/evidenza dal profilo aziendale
```python
class Evidence:
    evidence_id: str
    type: Literal["CERTIFICATION", "REFERENCE", "COMPETENCY", "FINANCIAL", "DOCUMENT", "PARTNERSHIP"]
    title: str
    description: str
    valid_from: date | None
    valid_until: date | None
    proof_attachments: list[str]  # paths/URLs ai documenti di prova
    metadata: dict
```

### `Penalty` — penale contrattuale
```python
class Penalty:
    type: Literal["FIXED", "PERCENTAGE", "PER_DAY", "PER_MILLE"]
    value: float                # 1.5 per "1.5 per mille"
    base: str                   # "netto contrattuale" | "valore licenza"
    cap_pct: float | None       # tetto cumulativo (es. 10.0)
    triggers: list[str]         # cosa la fa scattare
```

### `SchemaVersion` — versionamento
```python
class SchemaVersion:
    major: int = 1
    minor: int = 0
```

---

## 4. Blocchi del sistema

---

### B1 — Document Ingestor

**Owner suggerito:** Developer con esperienza parsing/document AI
**Priorità sviluppo:** 🔴 ALTA (blocca B2)

#### Scopo
Trasforma documenti binari di **qualsiasi formato** in una rappresentazione strutturata navigabile (`ParsedDocument`), preservando articoli, tabelle, riferimenti incrociati e numerazione delle pagine. Il blocco è progettato per essere format-agnostic verso i blocchi a valle: B2 non sa né deve sapere se il documento d'origine fosse PDF, DOCX, email o archivio ZIP.

#### Architettura interna: Tika come router universale + strategie specializzate

```
Input file (qualunque formato)
    │
    ▼
┌──────────────────────────────────────────┐
│  Apache Tika                              │
│  - Detect MIME type (no fiducia in estensione) │
│  - Estrae metadati                        │
│  - Estrazione testo "grezza" come baseline │
└─────────┬────────────────────────────────┘
          │
          ▼
┌──────────────────────────────────────────┐
│  Strategy Selector                        │
│  Sceglie l'estrattore specializzato       │
│  in base al MIME type                     │
└─────────┬────────────────────────────────┘
          │
    ┌─────┼──────────┬──────────┬──────────┬──────────┐
    ▼     ▼          ▼          ▼          ▼          ▼
PDF nativo  PDF scan  DOCX    XLSX/CSV  EML/MSG   ZIP/7z   Altri (HTML/RTF/ODT/…)
italiano                                                    fallback: Tika raw
    │     │          │          │          │          │
    │     │          │          │          │          ▼ (ricorsivo)
    │     │          │          │          │      Re-invoca B1
    │     │          │          │          │      per ogni file estratto
    │     │          │          │          │
    └─────┴──────────┴──────────┴──────────┴──────────┐
                                                       ▼
                                            ┌──────────────────┐
                                            │ Normalizer        │
                                            │ → ParsedDocument │
                                            └──────────────────┘
```

**Perché questa architettura:**
- **Tika** sa identificare 1400+ formati e funge da MIME detector affidabile (non ci fidiamo dell'estensione file)
- Per i formati **critici** (PDF italiani, DOCX, tabelle) entrano in gioco estrattori dedicati che producono output più strutturato di Tika "raw"
- Per formati **esotici o legacy** (ODT, RTF, eml, html, doc legacy), Tika "raw" è già abbastanza
- Gli **archivi e gli embedded** sono gestiti ricorsivamente, in modo trasparente

#### Input

```python
class IngestionRequest:
    schema_version: SchemaVersion
    file_path: str                       # path locale o URL
    mime_type_hint: str | None = None    # opzionale; Tika ricava da contenuto se assente
    expected_language: str = "it"
    document_type_hint: Literal["CAPITOLATO", "ALLEGATO", "BANDO_ONERI", "FAQ", "ALTRO"] | None
    tender_id: UUID                       # gara di appartenenza
    extraction_options: IngestionOptions

class IngestionOptions:
    extract_tables: bool = True           # disattiva se non servono (es. email)
    extract_embedded: bool = True         # processa file embedded ricorsivamente
    ocr_fallback: bool = True             # se PDF senza layer testo, attiva OCR
    ocr_languages: list[str] = ["ita", "eng"]
    max_recursion_depth: int = 5          # per archivi annidati
```

#### Output (invariato — il contratto con B2 non cambia col formato di input)

```python
class ParsedDocument:
    schema_version: SchemaVersion
    document_id: UUID
    tender_id: UUID
    source: SourceMetadata
    sections: list[Section]
    raw_text: str                   # fallback full-text
    warnings: list[str]             # es. "OCR fallback used on page 3"
    processing_stats: ProcessingStats
    embedded_documents: list[UUID]  # document_id dei file estratti ricorsivamente (se presenti)

class SourceMetadata:
    filename: str
    mime_type: str                  # rilevato da Tika, non dall'estensione
    detected_format: str            # "PDF 1.7 native" | "PDF scanned" | "DOCX (Office Open XML)" | ...
    pages: int | None               # null per formati senza pagine (es. email, HTML)
    language: str                   # detected language (Tika language detection)
    hash_sha256: str
    extracted_at: datetime
    extraction_strategy: str        # "tika_raw" | "pdf_italian_tender" | "docx_native" | "spreadsheet" | "email" | ...
    tika_metadata: dict             # metadati completi restituiti da Tika (autore, creation_date, ecc.)
    is_embedded: bool               # true se estratto da un archivio o documento padre
    parent_document_id: UUID | None # se is_embedded=true

class Section:
    section_id: str                 # "art-1", "preamble", "annex-a", "sheet-1", "email-body", ...
    type: Literal["ARTICLE", "PREAMBLE", "ANNEX", "TABLE_BLOCK", "EMAIL_HEADER", "EMAIL_BODY", "SPREADSHEET_SHEET", "OTHER"]
    title: str | None
    order: int                      # ordine nel documento
    page_start: int | None          # null per formati senza pagine
    page_end: int | None
    text_raw: str
    text_clean: str                 # normalizzato (whitespace, smart quotes, ecc.)
    subsections: list[Section]
    tables: list[Table]
    metadata: dict                  # campo libero per dati format-specific

class Table:
    table_id: str
    caption: str | None
    headers: list[str]
    rows: list[list[str]]
    page: int | None
    source_format: Literal["NATIVE_TABLE", "EXTRACTED_FROM_PDF", "SPREADSHEET_SHEET"]

class ProcessingStats:
    duration_ms: int
    strategy_used: str
    ocr_used: bool
    ocr_pages: list[int]
    tables_extracted: int
    embedded_files_count: int
    warnings_count: int
```

#### Strategie di estrazione (implementazione)

| Strategia | MIME types gestiti | Tecnologia | Output specifico |
|---|---|---|---|
| **`pdf_italian_tender`** | `application/pdf` (con layer testo) | PyMuPDF + Camelot + regex articoli | Sezioni `ARTICLE` con `section_id="art-N"`, tabelle strutturate |
| **`pdf_ocr`** | `application/pdf` (scansionato) | Tesseract via Tika + preprocessing OpenCV | `text_raw` + warning OCR usato, no sezionatura semantica |
| **`docx_native`** | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` | python-docx | Sezioni da Heading 1/2/3 nativi, tabelle preservate |
| **`spreadsheet`** | `application/vnd.openxmlformats-…spreadsheetml.sheet`, `text/csv` | openpyxl, pandas | Una `Section` per sheet/foglio, contenuto come `Table` |
| **`email`** | `message/rfc822`, `application/vnd.ms-outlook` | Tika + email standard library | `EMAIL_HEADER` + `EMAIL_BODY` separati, allegati processati ricorsivamente |
| **`archive`** | `application/zip`, `application/x-7z-compressed`, `application/x-tar` | Tika ricorsivo | Crea un `ParsedDocument` per ogni file estratto, link tramite `parent_document_id` |
| **`tika_raw`** | tutto il resto: HTML, RTF, ODT, .doc legacy, PPT, immagini standalone, ecc. | Apache Tika | `raw_text` + sezione unica `OTHER`, metadati Tika |

#### Failure modes
| Codice | Quando | Comportamento |
|---|---|---|
| `UNSUPPORTED_FORMAT` | Tika non riconosce affatto il formato | Solleva eccezione, log |
| `OCR_FAILED` | OCR non riesce su pagina scansionata | Warning + best-effort su altre pagine |
| `EMPTY_DOCUMENT` | nessun testo estratto | Solleva eccezione |
| `STRUCTURE_NOT_DETECTED` | nessun articolo riconosciuto (per `pdf_italian_tender`) | Warning, fallback a sezione unica con `raw_text` |
| `ARCHIVE_TOO_DEEP` | Archivio annidato oltre `max_recursion_depth` | Warning, processamento parziale |
| `TIKA_SERVER_UNREACHABLE` | Tika server Docker non raggiungibile | Errore, retry con backoff |
| `CORRUPT_FILE` | File binario corrotto | Errore con suggerimento di re-upload |

#### Dipendenze
- Apache Tika server (Docker container `apache/tika:latest-full`)
- Tesseract OCR (incluso nell'immagine Tika `-full`, con language packs `ita`+`eng`)
- Nessun blocco a monte (è il primo del workflow)
- Storage B9 per salvare il documento originale + il `ParsedDocument`

#### Stack suggerito

**Core**
- **Apache Tika** via tika-python (`pip install tika`) oppure REST API diretta a Tika server
- Tika server in Docker: `apache/tika:latest-full` (include Tesseract + language packs)

**Strategie specializzate**
- **PyMuPDF** (fitz) per estrazione PDF nativi italiani con layout preservato
- **pdfplumber** come alternativa per PDF con layout complessi
- **Camelot** o **Tabula-py** per tabelle PDF
- **OpenCV + Pillow** per preprocessing OCR (deskew, denoise, binarization) prima di Tesseract
- **python-docx** per estrazione semantica DOCX (preserva headings nativi)
- **openpyxl** + **pandas** per spreadsheet
- **email** (stdlib) + **extract-msg** per .msg Outlook

**Strutturazione semantica**
- Regex per riconoscimento articoli italiani: `r"^Art(?:icolo|\.)\s*(\d+)(?:\s*[-–]\s*(.+))?"`
- Language detection: Tika ha già `Content-Language`; fallback `langdetect`

#### Note
- Il `section_id` deve essere stabile tra esecuzioni (idempotenza)
- Tika gira come servizio separato (porta 9998 default) → architettura cloud-portable: stesso codice in dev locale, staging, on-prem produzione
- Tika gestisce nativamente l'**estrazione ricorsiva da archivi**: un ZIP con dentro PDF+DOCX viene esploso e ogni file genera il suo `ParsedDocument`, con `parent_document_id` che li collega
- Per la demo W3: focalizzarsi su `pdf_italian_tender` come strategia di punta (è ciò che si vede sui capitolati di esempio), ma avere il fallback `tika_raw` operativo per gli altri formati garantisce robustezza nella demo
- **Variante "Tika-only"**: per il PoC iniziale di W1 è legittimo partire con sola strategia `tika_raw` su tutto, e solo dopo introdurre le strategie specializzate. Lo schema `ParsedDocument` è già pensato per supportare entrambi i casi.

---

### B2 — Requirement Extractor

**Owner suggerito:** Developer con esperienza LLM/prompt engineering
**Priorità sviluppo:** 🔴 ALTA (cuore del sistema)

#### Scopo
Riceve un `ParsedDocument` ed estrae la lista strutturata di requisiti, classificandoli per categoria (Qualificazione/Normativa/Tecnica/Amministrativa) e tipo (Escludente/Preferenziale/Informativo).

#### Input

```python
class ExtractionRequest:
    schema_version: SchemaVersion
    documents: list[ParsedDocument]   # tutti i documenti della stessa gara
    tender_id: UUID
    extraction_options: ExtractionOptions

class ExtractionOptions:
    classify_normative_refs: bool = True   # risolve e espande riferimenti a leggi
    extract_penalties: bool = True
    extract_deadlines: bool = True
    min_confidence: float = 0.7             # soglia sotto cui il requisito va in review
    llm_model: str = "claude-3-5-sonnet"
```

#### Output

```python
class ExtractionResult:
    schema_version: SchemaVersion
    tender_id: UUID
    requirements: list[Requirement]
    extraction_summary: ExtractionSummary
    needs_review: list[str]                # requirement_id che necessitano review umana

class Requirement:
    requirement_id: str                     # "REQ-001"
    tender_id: UUID
    source: SourceLocation                  # da dove proviene
    text_original: str                      # citazione fedele dal documento
    text_normalized: str                    # versione pulita per processing
    category: Literal["QUALIFICAZIONE", "NORMATIVA", "TECNICA", "AMMINISTRATIVA"]
    type: Literal["ESCLUDENTE", "PREFERENZIALE", "INFORMATIVO"]
    subcategory: str | None                 # tassonomia fine: "iscrizione_albo", "certificazione_iso", ...
    normative_references: list[Reference]
    required_evidences: list[EvidenceRequest]
    deadline: date | str | None             # date o placeholder "01/01/AAAA"
    penalty: Penalty | None
    confidence: float                       # 0-1, fiducia dell'estrattore
    extraction_notes: str                   # spiegabilità: perché è stato classificato così

class EvidenceRequest:
    evidence_type: str                      # "iscrizione_mepa", "certificazione_iso_27001", ...
    description: str                        # cosa serve dimostrare
    mandatory: bool

class ExtractionSummary:
    total_requirements: int
    by_category: dict[str, int]             # {"QUALIFICAZIONE": 5, "NORMATIVA": 9, ...}
    by_type: dict[str, int]
    avg_confidence: float
    processing_duration_ms: int
```

#### Failure modes
| Codice | Quando | Comportamento |
|---|---|---|
| `LLM_TIMEOUT` | LLM API non risponde | Retry con backoff, max 3 tentativi |
| `LLM_RATE_LIMIT` | Rate limit raggiunto | Coda + retry |
| `INVALID_LLM_OUTPUT` | Output LLM non parsabile in `Requirement` | Re-prompt con esempio strutturato, max 2 tentativi |
| `NO_REQUIREMENTS_FOUND` | Estrattore non trova requisiti | Warning, requirements vuoto |

#### Dipendenze
- B1 (Document Ingestor) — riceve `ParsedDocument`
- B3 opzionalmente — per arricchimento con KB normativa
- Provider LLM (Anthropic API / OpenAI API)

#### Stack suggerito
- **Anthropic SDK** o **OpenAI SDK** per chiamate LLM
- **LangChain** o orchestrazione custom (preferenza per custom: meno magia, più controllo)
- **Pydantic** per validazione output LLM
- **Tenacity** per retry logic
- Prompt engineering: few-shot con esempi dal Modulo 1 VEM come gold standard

#### Note
- Il prompt deve essere versionato (es. `prompts/extraction_v1.2.md`) per riproducibilità
- L'estrazione è il blocco più "magico" del sistema → tracing dettagliato per debug essenziale
- Validare empiricamente sul capitolato EDR: il sistema deve riprodurre i 30 requisiti del Modulo 1

---

### B3 — Company Profile KB

**Owner suggerito:** Developer con esperienza database/RAG
**Priorità sviluppo:** 🟡 MEDIA (può iniziare con stub)

#### Scopo
Knowledge base interrogabile del profilo aziendale di VEM (certificazioni, referenze, competenze, partnership, dati finanziari). Esposta come API CRUD + semantica per il Gap Analyzer.

#### Input (interfaccia di query — uso principale da B4)

```python
class ProfileQuery:
    schema_version: SchemaVersion
    requirement: Requirement                # cosa stiamo cercando di soddisfare
    top_k: int = 5                          # n. di evidenze candidate
    min_relevance: float = 0.6
    evidence_types_filter: list[str] | None # opzionale: filtra per tipo

class ProfileQueryResult:
    schema_version: SchemaVersion
    requirement_id: str
    candidates: list[EvidenceCandidate]
    query_metadata: dict

class EvidenceCandidate:
    evidence: Evidence                      # vedi shared contracts
    relevance_score: float                  # 0-1
    reasoning: str                          # perché l'embedding ha matchato
```

#### Input (interfaccia di update — uso da B7 HITL)

```python
class ProfileUpdateRequest:
    schema_version: SchemaVersion
    operation: Literal["CREATE", "UPDATE", "DEACTIVATE"]
    evidence: Evidence
    source: Literal["MANUAL", "HITL_REVIEW", "TENDER_FEEDBACK", "BULK_IMPORT"]
    triggered_by_user: str
    related_requirement_id: str | None      # se l'update nasce da un gap risolto

class ProfileUpdateResponse:
    success: bool
    evidence_id: str
    message: str
```

#### Storage interno (modello dati)
```python
class CompanyProfile:
    profile_id: UUID
    company_name: str
    last_updated: datetime
    evidences: list[Evidence]               # tutte le evidenze attive
    revision_history: list[Revision]
```

#### Failure modes
| Codice | Quando | Comportamento |
|---|---|---|
| `EMBEDDING_FAILED` | Embedding model non disponibile | Fallback a keyword search |
| `EVIDENCE_NOT_FOUND` | Update su evidence_id inesistente | 404 + log |
| `DUPLICATE_EVIDENCE` | Tentativo di creare evidence già esistente | 409 + suggerimento di update |

#### Dipendenze
- B9 Storage (PostgreSQL: tabelle `profile_evidences` e `profile_revisions` come record canonici + audit; Qdrant: collection `profile_evidences_idx` con gli embedding delle descrizioni per il RAG di B4)
- Embedding model (locale o cloud)

#### Stack suggerito
- **PostgreSQL** (record di profilo + revisioni) e **Qdrant** (indice vettoriale per il RAG) — vedi B9
- Embedding: **multilingual-e5-large** (locale, gratis) o **OpenAI text-embedding-3-small** (cloud, multilingue, costo basso)

#### Note importanti
- **Per la demo W3**: profilo aziendale fittizio in JSON statico è accettabile. Il valore dimostrativo è nell'interfaccia, non nei dati.
- Il vector DB deve indicizzare **descrizioni dettagliate**, non solo titoli, per migliore recall
- Storia delle revisioni indispensabile per audit

---

### B4 — Gap Analyzer

**Owner suggerito:** Developer con buona conoscenza domain + LLM
**Priorità sviluppo:** 🟡 MEDIA

#### Scopo
Per ogni requisito estratto, determina se il profilo aziendale lo soddisfa, parzialmente lo soddisfa, o non lo soddisfa. Produce un `GapAnalysisResult` per requisito con evidenze, severità del gap e suggerimenti di rimedio.

#### Input

```python
class GapAnalysisRequest:
    schema_version: SchemaVersion
    tender_id: UUID
    requirements: list[Requirement]         # output di B2
    analysis_options: GapAnalysisOptions

class GapAnalysisOptions:
    deep_reasoning: bool = True             # usa LLM per match ambigui
    auto_queue_ambiguous: bool = True       # invia automaticamente i casi UNKNOWN a B7
    confidence_threshold_human_review: float = 0.7
```

#### Output

```python
class GapAnalysisResponse:
    schema_version: SchemaVersion
    tender_id: UUID
    results: list[GapAnalysisResult]
    summary: GapAnalysisSummary

class GapAnalysisResult:
    requirement_id: str
    match_status: Literal["FULL", "PARTIAL", "NONE", "UNKNOWN"]
    match_confidence: float
    matching_evidences: list[Evidence]      # evidenze che soddisfano il requisito
    gap: Gap | None                         # null se match=FULL
    needs_human_review: bool
    reasoning: str                          # spiegazione human-readable

class Gap:
    severity: Literal["CRITICAL", "MAJOR", "MINOR"]
    description: str
    remediation_suggestion: str
    remediation_effort: Literal["LOW", "MEDIUM", "HIGH"]
    remediation_time_estimate: str | None   # "30 giorni"

class GapAnalysisSummary:
    total_analyzed: int
    full_match: int
    partial_match: int
    no_match: int
    unknown: int
    critical_gaps: int                      # i CRITICAL = NO-GO automatico
    sent_to_review_queue: int
```

#### Logica di severità (regola di business)
- Requirement `type == ESCLUDENTE` AND `match_status == NONE` → **CRITICAL**
- Requirement `type == ESCLUDENTE` AND `match_status == PARTIAL` → **MAJOR** (potenzialmente critico, va revisionato)
- Requirement `type == PREFERENZIALE` AND `match_status == NONE` → **MINOR**
- Requirement `type == INFORMATIVO` → mai un gap

#### Failure modes
| Codice | Quando | Comportamento |
|---|---|---|
| `KB_UNAVAILABLE` | B3 non risponde | Errore, retry |
| `LOW_CONFIDENCE_BATCH` | >50% requisiti con confidence < soglia | Warning, raccomanda revisione manuale completa |

#### Dipendenze
- B2 (riceve `Requirement[]`)
- B3 (Company Profile KB — query intensiva)
- LLM per il deep reasoning sui match ambigui

#### Stack suggerito
- Pipeline a due passi:
  1. **Retrieval rapido** via B3 (top-k evidenze candidate per ogni requisito)
  2. **Reasoning LLM** per validare ogni match candidato (`Questa evidenza soddisfa davvero questo requisito? Perché?`)
- **Tenacity** per resilienza
- **asyncio** per parallelizzare l'analisi di N requisiti

#### Note
- Il reasoning LLM è il bottleneck di costo del sistema — considerare caching dei pattern già visti
- I "ragionamenti" prodotti dall'LLM sono parte dell'output utente, non solo logging: vanno mostrati in dashboard

---

### B5 — Scoring Engine

**Owner suggerito:** Developer (logica deterministica, no LLM)
**Priorità sviluppo:** 🟢 BASSA (può venire dopo B4)

#### Scopo
Prende l'output del Gap Analyzer e produce una decisione GO / GO_WITH_RESERVATIONS / NO_GO con score, motivazione e raccomandazioni. Logica deterministica e configurabile.

#### Input

```python
class ScoringRequest:
    schema_version: SchemaVersion
    tender_id: UUID
    requirements: list[Requirement]
    gap_results: list[GapAnalysisResult]
    tender_metadata: TenderMetadata
    scoring_config: ScoringConfig

class TenderMetadata:
    estimated_value: Money
    duration_months: int
    has_technical_score: bool               # true = gara con graduatoria
    cpv_codes: list[str]
    procedure_type: str                     # "MEPA_SOTTO_SOGLIA" | "APERTA" | ...

class ScoringConfig:
    risk_weights: dict[str, float]          # configurabile: { "penalties": 0.3, "vendor_lockin": 0.2, ... }
    soft_score_weights: dict[str, float]
```

#### Output

```python
class TenderDecision:
    schema_version: SchemaVersion
    tender_id: UUID
    decision: Literal["GO", "GO_WITH_RESERVATIONS", "NO_GO"]
    decision_timestamp: datetime

    hard_gate: HardGateResult
    soft_score: SoftScoreResult | None      # null se gara senza graduatoria
    risk_assessment: RiskAssessment

    summary: DecisionSummary
    rationale: str                           # spiegazione human-readable
    recommendations: list[Recommendation]
    next_actions: list[NextAction]

class HardGateResult:
    passed: bool
    blocking_requirements: list[str]         # requirement_id dei gap CRITICAL
    blocking_reasons: list[str]

class SoftScoreResult:
    technical_score_estimate: float | None   # 0-100, stima del punteggio in graduatoria
    max_score_available: float | None
    competitiveness: Literal["HIGH", "MEDIUM", "LOW"]

class RiskAssessment:
    overall_risk: Literal["LOW", "MEDIUM", "HIGH"]
    max_penalty_exposure_pct: float
    auto_termination_clauses: list[str]
    vendor_lock_in_detected: bool
    sla_complexity: Literal["LOW", "MEDIUM", "HIGH"]
    risk_factors: list[RiskFactor]

class RiskFactor:
    type: str
    severity: Literal["LOW", "MEDIUM", "HIGH"]
    description: str
    source: SourceLocation

class DecisionSummary:
    total_requirements: int
    met_full: int
    met_partial: int
    unmet: int
    critical_gaps: int
    avg_confidence: float

class Recommendation:
    priority: Literal["HIGH", "MEDIUM", "LOW"]
    text: str
    targets_requirement_id: str | None

class NextAction:
    action: str
    deadline: date | None
    owner_role: str                          # "PRESALES" | "LEGAL" | "TECH_LEAD" | ...
```

#### Algoritmo (riassunto)
```
1. HARD GATE
   if any(g.severity == "CRITICAL" for g in gap_results):
       decision = "NO_GO"
       hard_gate.passed = False
       return

2. RISK ASSESSMENT (sempre eseguito)
   - Calcola max penalty exposure
   - Identifica clausole di risoluzione automatica
   - Vendor lock-in: rileva citazioni esplicite SKU vendor
   - SLA complexity: complessità scadenze e tempi attivazione

3. SOFT SCORING (solo se tender_metadata.has_technical_score)
   - Calcola punteggio tecnico atteso dai PREFERENZIALI soddisfatti
   - Confronta con max disponibile → competitiveness

4. DECISIONE FINALE
   if risk_assessment.overall_risk == "HIGH" or gaps MAJOR > soglia:
       decision = "GO_WITH_RESERVATIONS"
   else:
       decision = "GO"
```

#### Failure modes
| Codice | Quando | Comportamento |
|---|---|---|
| `INVALID_CONFIG` | Pesi non sommano a 1 | Errore, suggerisce config valida |
| `MISSING_GAP_RESULTS` | Gap analysis incompleta | Errore, non procede |

#### Dipendenze
- B4 (riceve `GapAnalysisResult[]`)
- B2 (riceve `Requirement[]` originali per contesto)

#### Stack suggerito
- Logica pura Python — **niente LLM** qui (decisione deterministica e riproducibile)
- **Pydantic** per validazione
- Config esterno (YAML/JSON) per pesi e soglie

#### Note
- È il blocco che il **giurato del pitch capirà meglio**: tenere la logica chiara e mostrabile
- I pesi devono essere **calibrabili con VEM** dopo qualche gara reale analizzata

---

### B6 — Report Generator

**Owner suggerito:** Developer + design sensibility
**Priorità sviluppo:** 🟢 BASSA (può essere ultimo)

#### Scopo
Produce gli output finali destinati all'utente: report PDF in formato simile al Modulo 1 VEM, dati strutturati per la dashboard, checklist amministrativa.

#### Input

```python
class ReportRequest:
    schema_version: SchemaVersion
    tender_id: UUID
    parsed_documents: list[ParsedDocument]
    requirements: list[Requirement]
    gap_results: list[GapAnalysisResult]
    decision: TenderDecision
    output_formats: list[Literal["PDF", "DASHBOARD_JSON", "ADMIN_CHECKLIST"]]
```

#### Output

```python
class ReportResponse:
    schema_version: SchemaVersion
    tender_id: UUID
    artifacts: list[ReportArtifact]
    generated_at: datetime

class ReportArtifact:
    artifact_type: Literal["PDF_REPORT", "DASHBOARD_JSON", "ADMIN_CHECKLIST_PDF", "ADMIN_CHECKLIST_JSON"]
    file_path: str | None                   # per artefatti binari
    content: dict | None                    # per artefatti JSON
    size_bytes: int
```

#### Strutture dei singoli output

**`DASHBOARD_JSON`** — alimenta il frontend
```python
class DashboardData:
    header: DashboardHeader                 # gara, decisione, score
    requirements_by_category: dict          # per la vista tabellare
    gaps_summary: GapSummary                # visualizzazione gap
    risk_radar: dict                        # dati per radar chart
    timeline: list[TimelineEvent]           # scadenze e milestone
    audit_trail: list[AuditEntry]
```

**`ADMIN_CHECKLIST_JSON`** — lista documenti da preparare
```python
class AdminChecklist:
    tender_id: UUID
    documents_required: list[DocumentTodo]

class DocumentTodo:
    document_type: str                      # "DURC", "PassOE", "DPA", ...
    description: str
    template_available: bool
    template_path: str | None
    source_requirement_id: str
    deadline: date | None
    owner_role: str
```

#### Failure modes
| Codice | Quando | Comportamento |
|---|---|---|
| `PDF_GENERATION_FAILED` | Errore in template/rendering | Errore, JSON sempre disponibile come fallback |
| `MISSING_INPUTS` | Manca uno degli input | Errore esplicito |

#### Dipendenze
- Output di B1, B2, B4, B5
- Storage B9 per persistere gli artefatti

#### Stack suggerito
- **WeasyPrint** (HTML→PDF) o **ReportLab** per il PDF
- Template Jinja2 ispirato al layout del Modulo 1 VEM
- Logo VEM + identità grafica per il pitch finale

#### Note
- Il PDF deve essere **identico nello spirito al Modulo 1**: stessa struttura tabellare, stessa traceability articolo-requisito
- Il `DASHBOARD_JSON` è il contratto tra backend e frontend B10 → vale la pena progettarlo con cura

---

### B7 — Human-in-the-Loop Review Queue

**Owner suggerito:** Developer fullstack
**Priorità sviluppo:** 🟢 BASSA (raccontato nel pitch, MVP minimale)

#### Scopo
Coda asincrona di item che richiedono revisione umana. Un revisore (responsabile gare in VEM) può approvarli, modificarli, rifiutarli. Le approvazioni alimentano automaticamente B3 (KB profilo).

#### Input (push da B4 o altri blocchi)

```python
class ReviewItem:
    schema_version: SchemaVersion
    item_id: UUID
    item_type: Literal["AMBIGUOUS_REQUIREMENT", "UNKNOWN_EVIDENCE_MATCH", "NEW_REQUIREMENT_PATTERN"]
    tender_id: UUID
    payload: dict                            # contenuto specifico per tipo
    created_at: datetime
    priority: Literal["HIGH", "MEDIUM", "LOW"]
    deadline: datetime | None
    context: ReviewContext

class ReviewContext:
    requirement: Requirement | None
    candidate_evidences: list[Evidence]
    auto_suggestion: str | None              # cosa il sistema farebbe in autonomia
```

#### Output (azione del revisore)

```python
class ReviewDecision:
    item_id: UUID
    decided_by: str                          # user id
    decided_at: datetime
    action: Literal["APPROVE_AS_SUGGESTED", "MODIFY", "REJECT", "ADD_NEW_EVIDENCE"]
    modified_payload: dict | None
    reviewer_notes: str
    propagate_to_profile: bool               # se true → invia a B3
```

#### API esposte
```
POST   /review-queue/items              # B4 pusha un nuovo item
GET    /review-queue/items?status=pending&priority=HIGH
GET    /review-queue/items/{item_id}
POST   /review-queue/items/{item_id}/decide
GET    /review-queue/stats
```

#### Failure modes
| Codice | Quando | Comportamento |
|---|---|---|
| `ITEM_ALREADY_DECIDED` | Tentativo di decidere item già chiuso | 409 |
| `INVALID_PROPAGATION` | propagate_to_profile=true ma payload incompatibile | Errore |

#### Dipendenze
- Riceve da B4 (gap ambigui)
- Aggiorna B3 (Profile KB)
- Storage B9

#### Stack suggerito
- Tabella PostgreSQL `review_queue_items` in B9 (stato HITL transazionale, nessun vettore)
- Per la demo: UI Streamlit con tab "Review Queue"
- Notifiche email/Slack via webhook (post-MVP)

#### Note
- Per la demo W3: implementazione minimale ma **funzionante end-to-end** è più importante di una UI raffinata
- Posizionamento nel pitch: "questo è il meccanismo con cui il sistema migliora nel tempo"

---

### B8 — Orchestrator / API Gateway

**Owner suggerito:** Senior dev / tech lead del team
**Priorità sviluppo:** 🔴 ALTA (collante del sistema)

#### Scopo
Espone l'API pubblica del sistema e orchestra il workflow di analisi di una gara, chiamando i blocchi nell'ordine corretto, gestendo errori e persistendo gli stati intermedi.

#### Input (API esposte al frontend e CLI)

Endpoint principali:
```
POST   /tenders                          # crea nuova gara
POST   /tenders/{tender_id}/documents    # upload documenti
POST   /tenders/{tender_id}/analyze      # avvia pipeline completa
GET    /tenders/{tender_id}              # stato + risultati
GET    /tenders/{tender_id}/report.pdf   # download report
GET    /tenders                          # lista gare con filtri

GET    /profile                          # legge profilo aziendale
PATCH  /profile/evidences/{id}           # aggiorna evidence

GET    /review-queue                     # delega a B7
```

#### Modello di workflow

```python
class AnalysisJob:
    job_id: UUID
    tender_id: UUID
    status: Literal["QUEUED", "PARSING", "EXTRACTING", "ANALYZING", "SCORING", "REPORTING", "COMPLETED", "FAILED"]
    progress_pct: int
    started_at: datetime
    completed_at: datetime | None
    error: str | None
    artifacts: dict                          # riferimenti agli output dei blocchi
```

#### Output (esempio risposta `GET /tenders/{id}`)
```python
class TenderView:
    tender_id: UUID
    name: str
    status: AnalysisJob.status
    progress: int
    created_at: datetime
    documents: list[DocumentRef]
    decision: TenderDecision | None
    report_url: str | None
```

#### Dipendenze
- **Tutti** gli altri blocchi
- Storage B9 per stato persistente

#### Stack suggerito
- **FastAPI** (async, OpenAPI auto-generato)
- **Celery** o **arq** per task asincroni (l'analisi richiede minuti)
- **Pydantic** per i modelli API
- **SQLAlchemy** (+ `qdrant-client` per l'indice semantico) + repository pattern per accesso a B9

#### Note
- Il workflow deve essere **ripristinabile**: se la pipeline fallisce a metà, deve poter ripartire dal punto giusto
- Tutti gli step logged in audit trail
- Per MVP: pipeline sincrona con feedback "loading" sul frontend è accettabile

---

### B9 — Storage Layer

**Owner suggerito:** Senior dev (configura, non sviluppa molto)
**Priorità sviluppo:** 🔴 ALTA (infrastruttura abilitante)

#### Scopo
Persistenza di tutti i dati del sistema. Espone API CRUD ai blocchi che ne hanno bisogno. Architettura **ibrida PostgreSQL + Qdrant**: PostgreSQL è il *system of record* per tutto il dato strutturato; Qdrant è usato **solo per ciò per cui nasce** — indicizzazione e ricerca vettoriale (semantica). Il filesystem locale ospita i file binari, referenziati per path.

#### Principio guida
- **PostgreSQL = verità.** Ogni entità (gare, documenti, requisiti, gap, decisioni, audit, job, profilo) è una riga relazionale con vincoli FK, transazioni ACID e query aggregate native.
- **Qdrant = indice derivato.** Contiene solo il vettore + un payload minimo (id di join verso PG + 1-2 campi di filtro). Non è uno store di verità: può essere **ricostruito interamente da PostgreSQL** con un reindex job. Questo elimina sia il rischio di disallineamento permanente sia l'hack del "vettore dummy" per dati non semantici.
- **Lettura RAG**: Qdrant restituisce gli id più simili (con filtri payload) → PostgreSQL idrata le righe canoniche complete.
- **Scrittura**: write su PG (transazione, committata per prima) → upsert del vettore su Qdrant (best-effort). Se l'upsert vettoriale fallisce, `reindex_from_source` recupera dallo stato PG: nessun dato perso.

#### Componenti

**PostgreSQL** — system of record relazionale

Ogni "tipo" di dato è una **tabella**. Tutto ciò che è strutturato, transazionale o auditabile vive qui — niente più vettori finti.

| Tabella | Colonne chiave | Note |
|---|---|---|
| `tenders` | tender_id (PK), nome, stato, cpv, valore, date | metadata gara; abilita aggregati per CPV/stato/periodo |
| `documents` | document_id (PK), tender_id (FK), filename, mime_type, hash, fs_path | una riga per file ingerito; `fs_path` → filesystem |
| `requirements` | requirement_id (PK), tender_id (FK), categoria, tipo, fonte (`SourceLocation`), testo | record canonico; l'embedding del testo vive in Qdrant |
| `gap_results` | gap_id (PK), requirement_id (FK), match_status, evidenze (jsonb), reasoning | join relazionale con `requirements` |
| `decisions` | decision_id (PK), tender_id (FK), decisione, score, motivazione, created_at | una per gara; abilita aggregati GO/NO-GO |
| `analysis_jobs` | job_id (PK), tender_id (FK), status, progress_pct, timestamps, error | stato workflow transazionale/ripristinabile |
| `audit_log` | event_id (PK), actor, action, target, ts, payload (jsonb) | append-only; vero audit trail con WAL |
| `profile_evidences` | evidence_id (PK), tipo, titolo, descrizione, validità | record canonico; l'embedding della descrizione vive in Qdrant |
| `profile_revisions` | revision_id (PK), evidence_id (FK), operation, source, ts | storia modifiche profilo (audit) |
| `review_queue_items` | item_id (PK), tipo, payload (jsonb), priorità, status | coda HITL; stato transazionale |

**Qdrant** — indice semantico (solo dove serve la ricerca vettoriale)

Esistono **solo le 2 collection** che alimentano un RAG. Ogni punto è derivato da una riga PostgreSQL e porta nel payload l'id di join per idratare la verità da PG.

| Collection | Vettore | Payload (minimo) | Sorgente |
|---|---|---|---|
| `requirements_idx` | embedding del testo requisito | requirement_id, tender_id, categoria | PG `requirements` |
| `profile_evidences_idx` | embedding della descrizione | evidence_id, tipo | PG `profile_evidences` |

**Filesystem locale** — file binari

I file binari (PDF originali, report generati, allegati di evidenze) non vivono nel database ma sul filesystem del server. Il path è referenziato nella colonna `fs_path` della tabella PostgreSQL corrispondente.

```
/data/files/
├── tenders/
│   └── {tender_id}/
│       ├── documents/           # PDF originali del bando
│       │   └── {document_id}.pdf
│       └── reports/             # Report PDF generati da B6
│           └── {decision_id}.pdf
└── evidences/
    └── {evidence_id}/
        └── attachments/         # Documenti di prova del profilo
            └── *.pdf
```

In produzione, il path stringato nella colonna `fs_path` di PostgreSQL può essere sostituito senza modifiche di codice applicativo da una URL `s3://` o equivalente — la migrazione a object storage è una decisione operativa, non architetturale.

#### Interfacce
Esposte come **repository pattern** Python (no API HTTP interna). L'interfaccia pubblica è identica a quella del vecchio single-store: cambia solo l'implementazione sottostante.

```python
class TenderRepository:                 # PostgreSQL
    def create(self, tender: TenderCreate) -> Tender: ...
    def get(self, tender_id: UUID) -> Tender | None: ...
    def list(self, filters: TenderFilters) -> list[Tender]: ...
    def update_status(self, tender_id: UUID, status: str) -> None: ...

class RequirementRepository:            # PG (canonico) + Qdrant (indice)
    def upsert(self, req: Requirement, embedding: list[float]) -> Requirement: ...
    def semantic_search(self, query_vec: list[float], filters) -> list[Requirement]: ...
    # semantic_search: Qdrant → ids → idratazione righe da PostgreSQL

class GapResultRepository: ...          # PostgreSQL
class DecisionRepository: ...           # PostgreSQL (+ aggregati GO/NO-GO)
class AnalysisJobRepository: ...        # PostgreSQL
class AuditLogRepository: ...           # PostgreSQL, append-only
class ProfileRepository: ...            # PG (canonico) + Qdrant (indice)
class ReviewQueueRepository: ...        # PostgreSQL

class VectorIndex:                      # wrapper Qdrant — indice derivato, ricostruibile
    def upsert(self, collection: str, id: UUID, vector: list[float], payload: dict) -> None: ...
    def search(self, collection: str, vector: list[float], filters, k: int) -> list[UUID]: ...
    def reindex_from_source(self, collection: str) -> None: ...   # rigenera da PG

class FileStore:                        # invariato — filesystem, domani S3
    def save(self, path: str, content: bytes) -> str: ...
    def load(self, path: str) -> bytes: ...
    def delete(self, path: str) -> None: ...
```

Tutti i repository condividono una `Session`/engine SQLAlchemy iniettata via dependency injection; quelli con ricerca semantica ricevono **anche** la `VectorIndex` (client Qdrant). Il `FileStore` resta separato e oggi punta al filesystem; domani può essere sostituito con un'implementazione S3-compatible senza toccare i repository.

#### Stack suggerito
- **PostgreSQL 16** (Docker `postgres:16`) — porta 5432
- **SQLAlchemy 2.0** (Core/ORM) + **Alembic** per le migrazioni di schema
- **psycopg 3** come driver
- **Qdrant** (Docker `qdrant/qdrant:latest`) — porta 6333 + **qdrant-client**
- **Pydantic v2** per i modelli/contratti
- Filesystem standard Python (`pathlib`) per il `FileStore`

#### Decisione aggiornata (29 mag 2026): da single-store a ibrido
Superato il **single-store Qdrant** originario. Quel design costringeva a un vettore *dummy* su 8 collection su 10 (dato non semantico forzato dentro un vector DB) e rinunciava ad ACID, audit con WAL e query aggregate — proprio i requisiti di credibilità verso la PA. L'ibrido mette ogni dato dove rende: **PostgreSQL** per relazionale/transazionale/auditabile, **Qdrant** solo per la ricerca vettoriale.

**Alternativa scartata: Postgres + `pgvector`** (un solo motore). Scartata deliberatamente: Qdrant offre filtri su payload e prestazioni ANN superiori su scala, e il costo di un container in più è marginale; restiamo coerenti col principio "ogni tecnologia per il suo mestiere". `pgvector` resta un fallback valido se in produzione si volesse collassare a un solo motore.

#### Trade-off di questa scelta (espliciti per onestà intellettuale)

| Cosa costa l'ibrido | Impatto MVP | Mitigazione |
|---|---|---|
| Un container in più (postgres) | Bassa | `docker-compose`: 4 servizi (app, tika, postgres, qdrant); niente MinIO, i binari restano su filesystem |
| Doppia scrittura su `requirements` / `profile_evidences` | Bassa | PG committato per primo; Qdrant è derivato e reindicizzabile (`reindex_from_source`) |
| Migrazioni di schema da gestire | Bassa | Alembic versiona lo schema; serviva comunque per il versionamento dei contratti |
| Sync PG ↔ Qdrant | Bassa | Qdrant non è mai sorgente di verità: se diverge non si perde nulla, basta un reindex |

Posizionamento nel pitch: l'ibrido **è** la slide "**Architettura production-ready**" — ACID, audit trail reale e aggregati nativi, con la ricerca semantica dove serve davvero.

#### Note
- Schema versionato via **Alembic** (più il campo `schema_version` sui contratti Pydantic) abilita migration future
- Audit log = obbligatorio per credibilità PA: chi ha fatto cosa quando — ora con garanzie WAL native
- Backup: `pg_dump` schedulato per PostgreSQL (verità); le collection Qdrant non vanno backuppate, si rigenerano da PG con `reindex_from_source`

---

### B10 — Frontend / Dashboard

**Owner suggerito:** Developer con sensibilità UX
**Priorità sviluppo:** 🟡 MEDIA (per la demo serve qualcosa di mostrabile)

#### Scopo
Interfaccia utente per: caricare gare, visualizzare l'analisi, esplorare gap, gestire profilo, gestire review queue.

#### Input
Consuma l'API di B8.

#### Output
Interazione utente.

#### Schermate principali

1. **Home / Lista gare** — tabella con filtri (stato, decisione, data)
2. **Nuova gara** — upload documenti, avvio analisi
3. **Dettaglio gara** — vista principale con:
   - Header: decisione GO/NO-GO con badge colorato, score, timestamp
   - Tab "Requisiti" — tabella drill-down per categoria
   - Tab "Gap Analysis" — gap per severità con evidenze e raccomandazioni
   - Tab "Rischi" — radar chart + lista risk factors
   - Tab "Checklist amministrativa" — documenti da preparare
   - Tab "Audit Trail" — log delle decisioni del sistema
4. **Profilo Aziendale** — vista CRUD su evidenze
5. **Review Queue** — coda HITL con interfaccia di approvazione

#### Stack suggerito
- **MVP / Demo W3**: **Streamlit** — sviluppo rapidissimo, perfetto per data app
- **Produzione**: **Next.js** + Tailwind + shadcn/ui
- **Charts**: Plotly (Streamlit) o Recharts (Next.js)

#### Note
- Per la demo W3 lo stile non deve essere perfetto, ma il **flusso utente** sì
- Mostrare visivamente la **traceability**: cliccando su un requisito si apre il PDF originale evidenziato all'articolo giusto = effetto wow

---

## 5. Sequenza di sviluppo e parallelizzazione

### Settimana 1 (14-22 maggio)

**In parallelo:**
- **Track A — Pipeline core**: B1 (Document Ingestor) → B2 (Requirement Extractor)
- **Track B — Infrastruttura**: B9 (Storage) + B8 (Orchestrator scheletro)
- **Track C — KB & dati**: B3 (Profile KB) con profilo fittizio VEM in JSON

**Output W1**: estrazione funzionante su capitolato EDR, output simile al Modulo 1 VEM.

### Settimana 2 (22-29 maggio)

**In parallelo:**
- **Track A**: B4 (Gap Analyzer)
- **Track B**: B5 (Scoring Engine), B10 (Frontend MVP con Streamlit)
- **Track C**: B6 (Report Generator) — PDF base

**Output W2**: pipeline end-to-end funzionante, demo navigabile via Streamlit.

### Settimana 3 (29 maggio - 3 giugno)

**Tutti convergono su:**
- Hardening, gestione errori, edge case
- B7 (Review Queue) — implementazione minimale
- Polish demo, preparazione pitch deck

---

## 6. Strategia di mock per sviluppo parallelo

Ogni blocco può essere sviluppato in parallelo grazie a **fixture di mock** che rispettano i contratti.

**Esempio: chi sviluppa B4 (Gap Analyzer) non aspetta B2.**

Crea un file `mocks/requirements_capitolato_edr.json` con i 30 requisiti del Modulo 1 già strutturati secondo lo schema `Requirement`. B4 lo legge come input → può iniziare a sviluppare immediatamente. Quando B2 sarà pronto, sostituire la fixture con la chiamata reale è **una linea di codice**.

**Mock prioritari da creare in W1:**

| Mock | Per sbloccare | Contenuto |
|---|---|---|
| `parsed_document_edr.json` | B2, B4 | ParsedDocument del capitolato EDR |
| `requirements_modulo1.json` | B4, B5, B6 | 30 requirements dal Modulo 1 VEM |
| `company_profile_vem_fake.json` | B4 | Profilo VEM fittizio con ~20 evidenze realistiche |
| `gap_results_sample.json` | B5, B6 | Output GapAnalysisResult coerente |
| `tender_decision_sample.json` | B6, B10 | Decision di esempio |

**Convenzione team**: i file mock vivono in `tests/fixtures/` e sono **parte del repo**.

---

## 7. Testing strategy per blocco

| Blocco | Test minimo |
|---|---|
| B1 | Test multi-formato: parsing capitolato EDR (PDF) → ≥23 articoli + tabella SKU; DOCX di test → struttura preservata; ZIP con PDF+DOCX → 2 `ParsedDocument` collegati via `parent_document_id`; immagine scansionata → OCR attivato; formato esotico (ODT/RTF) → fallback Tika non rompe la pipeline |
| B2 | Test golden: estrazione sul capitolato EDR → verifica match con i 30 requirements del Modulo 1 (tolleranza 80%+) |
| B3 | Unit test: query con requirement noto → recupera evidenze attese; update + retrieve roundtrip |
| B4 | Test integrazione: dato `requirements_modulo1.json` + profilo VEM fake → produce N gap noti |
| B5 | Unit test puro: input gap con un CRITICAL → output `NO_GO`; senza critical + risk medio → `GO_WITH_RESERVATIONS` |
| B6 | Test visivo: il PDF generato sul capitolato EDR è confrontabile col Modulo 1 di VEM |
| B7 | Test API: push item → GET item → POST decisione → verify update propagato a B3 |
| B8 | Test E2E: POST gara → upload documento → POST analyze → GET decision (timeout 5 min) |
| B9 | Setup test: PostgreSQL raggiungibile su 5432 con migrazioni Alembic applicate + Qdrant su 6333; roundtrip CRUD su ogni repository; `semantic_search` Qdrant→PG hydrate; `reindex_from_source` rigenera l'indice da PG; `FileStore` save+load file di test |
| B10 | Test manuale di flusso utente (per MVP) |

**Test golden della demo**: la pipeline end-to-end deve riprodurre il Modulo 1 VEM dal capitolato EDR con > 90% di precisione. Questo è **il test di accettazione del pitch**.

---

## Appendice — Quick reference contratti

| Blocco | Input principale | Output principale |
|---|---|---|
| B1 | File path (qualunque formato: PDF/DOCX/XLSX/EML/ZIP/…) | `ParsedDocument` (schema unico, format-agnostic) |
| B2 | `list[ParsedDocument]` | `list[Requirement]` |
| B3 (query) | `Requirement` | `list[EvidenceCandidate]` |
| B3 (update) | `Evidence` + operation | `ProfileUpdateResponse` |
| B4 | `list[Requirement]` + access B3 | `list[GapAnalysisResult]` |
| B5 | `list[Requirement]` + `list[GapAnalysisResult]` + `TenderMetadata` | `TenderDecision` |
| B6 | Tutti gli artefatti precedenti | `list[ReportArtifact]` (PDF + JSON) |
| B7 | `ReviewItem` (push) | `ReviewDecision` (pull) |
| B8 | Richieste HTTP | Risposte HTTP + orchestrazione |
| B9 | Comandi repository | Dati persistiti |
| B10 | Interazione utente | API calls a B8 |

---

*Documento tecnico di riferimento — vive con il repo, va aggiornato a ogni modifica di interfaccia. Convenzione: tag PR `[interface]` per modifiche ai contratti, richiedono review da owner di tutti i blocchi consumatori.*
