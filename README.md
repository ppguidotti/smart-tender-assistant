# Smart Tender Assistant

> GenAI assistant for automated public-procurement (PA) tender analysis: it reads a
> tender document, extracts the requirements, compares them against the company
> profile, and produces a **traceable, auditable GO / NO-GO decision** — turning
> hours of manual analysis into minutes.

Built for the **VEM Sistemi GenAI Innovation Sprint 2026** hackathon.

---

## Why

A public-sector tender (*bando di gara*) is dozens of pages of articles, technical
specs and mandatory requirements. Deciding whether to bid means manually
cross-checking every requirement against what the company can actually deliver.
Smart Tender Assistant automates that loop while keeping a **citation back to the
exact point in the source document** for every extracted requirement — traceability
is the core differentiator, not an afterthought.

## How it works

Two-stage, format-agnostic pipeline:

```
  PDF / DOCX / XLSX / EML / ZIP …
            │
            ▼
   ┌─────────────────┐   deterministic text extraction (1400+ MIME types)
   │  B1  Apache Tika │
   └─────────────────┘
            │  ParsedDocument
            ▼
   ┌─────────────────┐   structured, JSON-mode requirement extraction
   │  B2  LLM (OpenAI-compatible: Azure Foundry / Azure OpenAI)
   └─────────────────┘
            │  list[Requirement]  (each with a SourceLocation citation)
            ▼
   ┌─────────────────┐   requirement ↔ company-profile matching (RAG)
   │  B4  Gap Analyzer│   PostgreSQL (records) + Qdrant (vector index)
   └─────────────────┘
            │  list[GapAnalysisResult]
            ▼
   ┌─────────────────┐   deterministic rules
   │  B5  Scoring     │ → TenderDecision (GO / NO-GO + rationale)
   └─────────────────┘
            │
            ▼
   B6 Report (PDF)  ·  B10 Streamlit dashboard  ·  B7 HITL review queue
```

### Storage

**Hybrid PostgreSQL + Qdrant.** PostgreSQL is the system of record for all
structured data; Qdrant holds *only* the embeddings for semantic search and is a
**derived index that can be fully rebuilt from PostgreSQL**. Binary files
(original PDFs, generated reports) live on the filesystem under `data/files/` and
are referenced by an `fs_path` column. See `docs/block_architecture.md` §B9.

## Architecture — the 10 blocks

Each block has an explicit Pydantic input/output contract, so implementations are
swappable and blocks can be developed in parallel against JSON fixtures.

| Block | Role | Stack |
|-------|------|-------|
| **B1** Document Ingestor | Multi-format parse → `ParsedDocument` | Apache Tika |
| **B2** Requirement Extractor | Structured extraction → `list[Requirement]` | LLM (OpenAI-compatible) |
| **B3** Company Profile KB | RAG over company evidences | Qdrant + multilingual embeddings |
| **B4** Gap Analyzer | Requirement ↔ profile matching → `list[GapAnalysisResult]` | LLM + Qdrant retrieval |
| **B5** Scoring Engine | GO/NO-GO decision → `TenderDecision` | Pure-Python rules |
| **B6** Report Generator | PDF + dashboard data | WeasyPrint + Jinja2 |
| **B7** HITL Review Queue | Human review of ambiguous cases | Streamlit + Postgres |
| **B8** Orchestrator / API | Gateway + workflow orchestration | FastAPI |
| **B9** Storage Layer | PostgreSQL + Qdrant + filesystem | SQLAlchemy/Alembic + qdrant-client |
| **B10** Frontend | Dashboard (MVP) | Streamlit + Plotly |

Full reference: [`docs/block_architecture.md`](docs/block_architecture.md).

## Repository layout

```
src/smart_tender_assistant/
  models/          # shared Pydantic v2 contracts (schemas.py)
  ingestion/       # B1 — Tika parsing
  extraction/      # B2 — LLM requirement extraction (llm, prompts, merge, mapping)
  gap_analysis/    # B4 — KB + embeddings + gap engine
  frontend/        # B10 — Streamlit app (pages, ui components, services)
  config.py        # pydantic-settings, reads .env
scripts/           # CLI entry points for each pipeline stage
db/schema.sql      # PostgreSQL schema (B9)
docker-compose.yml # tika + postgres + qdrant
tests/fixtures/    # first-class JSON fixtures (mocks for parallel dev)
docs/              # architecture, brainstorm, sample (anonymized) tenders
```

## Quick start

### Prerequisites

- Python **3.11+**
- Docker (for the Tika / PostgreSQL / Qdrant containers)
- LLM credentials — an OpenAI-compatible endpoint (Azure AI Foundry or Azure OpenAI)

### Setup

```bash
git clone git@github.com:ppguidotti/smart-tender-assistant.git
cd smart-tender-assistant

python -m venv .venv && source .venv/bin/activate
pip install -e ".[backend,frontend,dev]"

cp env.example .env        # then fill in your real values — .env is gitignored
```

`env.example` documents every variable. At minimum, set the LLM provider block
(`LLM_PROVIDER` + the matching `AZURE_*` keys, or the generic `LLM_BASE_URL` /
`LLM_API_KEY` / `LLM_MODEL` override).

### Infrastructure

```bash
docker compose up -d tika              # B1 only (Tika)
docker compose up -d                   # tika + postgres + qdrant
```

> Apache Tika can time out on the first call (JVM cold start) — start it a few
> seconds before the first parse, or retry.

### Run

**Frontend dashboard (B10)** — works standalone in mock mode (`STA_API_MODE=mock`,
reads `tests/fixtures/`), no backend required:

```bash
streamlit run src/smart_tender_assistant/frontend/app.py
```

**Pipeline (CLI)** — each stage chains into the next:

```bash
# B1 — parse documents → ParsedDocument JSON
python scripts/parse_documents.py "docs/Capitolato Gara - Anonimizzato.pdf" --out data/parsed/edr.json

# B2 — extract requirements (needs LLM creds in .env)
python scripts/extract_requirements.py data/parsed/edr.json --out data/requirements/edr.json

# Bridge the real extraction into the dashboard fixtures
python scripts/export_to_dashboard.py data/requirements/edr.json --bando-id live-edr --nome "Capitolato EDR"

# B4 setup — load the company KB into PostgreSQL + Qdrant
python scripts/load_company_kb.py
```

Scripts must be run from the repo root (they bootstrap `sys.path` to import from
`src/`).

## Development

```bash
ruff check . && ruff format .
mypy src
pytest
```

Conventions: Python 3.11+, mandatory type hints, Pydantic v2 strict
(`extra="forbid"`), files under ~300 lines, Google-style docstrings on public
functions. Tests mirror `src/` structure; fixtures in `tests/fixtures/` are
first-class artifacts used as mocks for parallel block development.

## Status

Hackathon MVP. B1/B2 (ingestion + extraction) and B10 (dashboard) are the
primary working tracks; B4 gap analysis runs on PostgreSQL + Qdrant; B5–B9 are in
progress against the shared contracts. See `docs/block_architecture.md` for the
authoritative, up-to-date design.

## License

Proprietary — VEM Sistemi GenAI Innovation Sprint 2026.
