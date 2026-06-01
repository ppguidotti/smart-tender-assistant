-- =============================================================================
-- Smart Tender Assistant — PostgreSQL schema (system of record, B9)
-- =============================================================================
-- Derived 1:1 from what the frontend actually consumes:
--   * src/smart_tender_assistant/frontend/models/schemas.py  (31 Pydantic models)
--   * src/smart_tender_assistant/frontend/services/api_client.py
--       (the 12 read methods on TenderApiClient = the persisted entities)
--   * tests/fixtures/*.json                                   (shape ground truth)
--
-- Design choices (deliberate):
--   * PostgreSQL is the system of record. Qdrant holds ONLY two derived vector
--     indexes (requirements_idx, profile_evidences_idx) and is rebuildable from
--     these tables — not modelled here. See docs/block_architecture.md §B9.
--   * Enums mirror the Pydantic Literals VALUE-FOR-VALUE (Italian where the
--     model is Italian: QUALIFICAZIONE, ESCLUDENTE, coperto, gap-esc, ...).
--   * tender_id / item_id are UUID in the models -> UUID columns. The string
--     business ids (requirement_id "REQ-001", evidence_id, bando id) -> TEXT.
--   * Embedded value objects (Money, SourceLocation, Gap, HardGateResult,
--     SoftScoreResult, RiskAssessment, DecisionSummary) are flattened into
--     their owner table when 1:1; list-valued children become child tables;
--     scalar string lists become TEXT[]; free dicts become JSONB.
--   * Scores/confidence in [0,1] carry CHECK constraints.
--
-- Re-runnable: enum creation guarded, tables IF NOT EXISTS.
-- =============================================================================

BEGIN;

-- -----------------------------------------------------------------------------
-- Enum types — exact mirror of models/schemas.py Literals
-- -----------------------------------------------------------------------------
DO $$ BEGIN
    CREATE TYPE requirement_category AS ENUM
        ('QUALIFICAZIONE','NORMATIVA','TECNICA','AMMINISTRATIVA');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE requirement_type AS ENUM ('ESCLUDENTE','PREFERENZIALE','INFORMATIVO');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE penalty_type AS ENUM ('FIXED','PERCENTAGE','PER_DAY','PER_MILLE');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE evidence_type AS ENUM
        ('CERTIFICATION','REFERENCE','COMPETENCY','FINANCIAL','DOCUMENT','PARTNERSHIP');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE match_status AS ENUM ('FULL','PARTIAL','NONE','UNKNOWN');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE gap_severity AS ENUM ('CRITICAL','MAJOR','MINOR');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- Shared LOW/MEDIUM/HIGH scale: remediation_effort, competitiveness, overall_risk,
-- sla_complexity, RiskFactor.severity, Recommendation.priority, ReviewItem.priority.
DO $$ BEGIN
    CREATE TYPE level_lmh AS ENUM ('LOW','MEDIUM','HIGH');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE decision_type AS ENUM ('GO','GO_WITH_RESERVATIONS','NO_GO');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE analysis_status AS ENUM
        ('QUEUED','PARSING','EXTRACTING','ANALYZING','SCORING','REPORTING','COMPLETED','FAILED');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE review_item_type AS ENUM
        ('AMBIGUOUS_REQUIREMENT','UNKNOWN_EVIDENCE_MATCH','NEW_REQUIREMENT_PATTERN');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE review_action AS ENUM
        ('APPROVE_AS_SUGGESTED','MODIFY','REJECT','ADD_NEW_EVIDENCE');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- HTML-prototype domain (lowercase, as in STCA_Platform_v2.html)
DO $$ BEGIN
    CREATE TYPE bando_status AS ENUM
        ('analisi','go','no-go','vinta','persa','pending','go_cond');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE req_status_html AS ENUM
        ('coperto','automatico','parziale','gap-pref','gap-esc','info');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE req_match_tone AS ENUM ('gn','am','rd','gr');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE cert_status_html AS ENUM ('urgent','scaduta','warn','ok');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- -----------------------------------------------------------------------------
-- updated_at trigger helper
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION set_updated_at() RETURNS trigger AS $$
BEGIN NEW.updated_at := now(); RETURN NEW; END $$ LANGUAGE plpgsql;

-- =============================================================================
-- documents — backs SourceLocation.document_id / document_name (traceability).
-- Not a frontend endpoint, but every Requirement/RiskFactor points here.
-- Binary original lives on disk (fs_path); s3:// in prod.
-- =============================================================================
CREATE TABLE IF NOT EXISTS documents (
    document_id   UUID PRIMARY KEY,
    tender_id     UUID,                          -- FK added after tenders exists
    name          TEXT NOT NULL,
    mime_type     TEXT,
    page_count    INTEGER,
    fs_path       TEXT,
    uploaded_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =============================================================================
-- tenders — TenderListItem (the home table row; flattened Money)
-- =============================================================================
CREATE TABLE IF NOT EXISTS tenders (
    tender_id          UUID PRIMARY KEY,
    name               TEXT NOT NULL,
    status             analysis_status NOT NULL DEFAULT 'QUEUED',
    decision           decision_type,            -- nullable until B5 ran
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at       TIMESTAMPTZ,
    total_requirements INTEGER NOT NULL DEFAULT 0,
    critical_gaps      INTEGER NOT NULL DEFAULT 0,
    score              DOUBLE PRECISION,         -- soft, no 0..1 bound in model
    -- estimated_value: Money (flattened, nullable)
    value_amount       NUMERIC(16,2),
    value_currency     TEXT DEFAULT 'EUR',
    value_is_net       BOOLEAN,
    updated_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_tenders_status ON tenders (status);

DROP TRIGGER IF EXISTS trg_tenders_updated_at ON tenders;
CREATE TRIGGER trg_tenders_updated_at BEFORE UPDATE ON tenders
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

ALTER TABLE documents DROP CONSTRAINT IF EXISTS fk_documents_tender;
ALTER TABLE documents ADD CONSTRAINT fk_documents_tender
    FOREIGN KEY (tender_id) REFERENCES tenders(tender_id) ON DELETE CASCADE;

-- =============================================================================
-- requirements — Requirement (+ flattened SourceLocation + embedded Penalty)
-- =============================================================================
CREATE TABLE IF NOT EXISTS requirements (
    requirement_id        TEXT PRIMARY KEY,
    tender_id             UUID NOT NULL REFERENCES tenders(tender_id) ON DELETE CASCADE,
    text_original         TEXT NOT NULL,
    text_normalized       TEXT NOT NULL,
    category              requirement_category NOT NULL,
    type                  requirement_type NOT NULL,
    subcategory           TEXT,
    deadline              TEXT,                  -- model is date|str|None -> keep raw
    confidence            DOUBLE PRECISION NOT NULL CHECK (confidence BETWEEN 0 AND 1),
    extraction_notes      TEXT NOT NULL DEFAULT '',
    -- SourceLocation (traceability — non negotiable)
    source_document_id    UUID REFERENCES documents(document_id) ON DELETE SET NULL,
    source_document_name  TEXT NOT NULL,
    source_section_id     TEXT,
    source_section_title  TEXT,
    source_page           INTEGER NOT NULL,
    source_char_start     INTEGER,
    source_char_end       INTEGER,
    -- Penalty (embedded 1:1, nullable)
    penalty_type          penalty_type,
    penalty_value         DOUBLE PRECISION,
    penalty_base          TEXT,
    penalty_cap_pct       DOUBLE PRECISION,
    penalty_triggers      TEXT[],
    created_at            TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_requirements_tender   ON requirements (tender_id);
CREATE INDEX IF NOT EXISTS idx_requirements_category ON requirements (category);

-- Requirement.normative_references: list[Reference]
CREATE TABLE IF NOT EXISTS requirement_references (
    id             BIGSERIAL PRIMARY KEY,
    requirement_id TEXT NOT NULL REFERENCES requirements(requirement_id) ON DELETE CASCADE,
    law            TEXT NOT NULL,
    article        TEXT,
    url            TEXT
);
CREATE INDEX IF NOT EXISTS idx_req_refs_req ON requirement_references (requirement_id);

-- Requirement.required_evidences: list[EvidenceRequest]
CREATE TABLE IF NOT EXISTS requirement_evidence_requests (
    id             BIGSERIAL PRIMARY KEY,
    requirement_id TEXT NOT NULL REFERENCES requirements(requirement_id) ON DELETE CASCADE,
    evidence_type  TEXT NOT NULL,
    description    TEXT NOT NULL,
    mandatory      BOOLEAN NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_req_evreq_req ON requirement_evidence_requests (requirement_id);

-- =============================================================================
-- profile_evidences — Evidence (company profile KB; indexed in Qdrant)
-- get_company_profile() returns list[Evidence]
-- =============================================================================
CREATE TABLE IF NOT EXISTS profile_evidences (
    evidence_id       TEXT PRIMARY KEY,
    type              evidence_type NOT NULL,
    title             TEXT NOT NULL,
    description       TEXT NOT NULL,
    valid_from        DATE,
    valid_until       DATE,
    proof_attachments TEXT[] NOT NULL DEFAULT '{}',
    metadata          JSONB NOT NULL DEFAULT '{}'::jsonb,
    active            BOOLEAN NOT NULL DEFAULT true,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_evidences_type   ON profile_evidences (type);
CREATE INDEX IF NOT EXISTS idx_evidences_active ON profile_evidences (active);

-- =============================================================================
-- gap_results — GapAnalysisResult (+ embedded Gap), per (tender, requirement)
-- =============================================================================
CREATE TABLE IF NOT EXISTS gap_results (
    id                            BIGSERIAL PRIMARY KEY,
    tender_id                     UUID NOT NULL REFERENCES tenders(tender_id) ON DELETE CASCADE,
    requirement_id                TEXT NOT NULL REFERENCES requirements(requirement_id) ON DELETE CASCADE,
    match_status                  match_status NOT NULL,
    match_confidence              DOUBLE PRECISION NOT NULL CHECK (match_confidence BETWEEN 0 AND 1),
    needs_human_review            BOOLEAN NOT NULL DEFAULT false,
    reasoning                     TEXT NOT NULL,
    -- Gap (embedded 1:1, nullable)
    gap_severity                  gap_severity,
    gap_description               TEXT,
    gap_remediation_suggestion    TEXT,
    gap_remediation_effort        level_lmh,
    gap_remediation_time_estimate TEXT,
    created_at                    TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (tender_id, requirement_id)
);
CREATE INDEX IF NOT EXISTS idx_gap_results_tender ON gap_results (tender_id);
CREATE INDEX IF NOT EXISTS idx_gap_results_status ON gap_results (match_status);

-- GapAnalysisResult.matching_evidences: list[Evidence] (M:N)
CREATE TABLE IF NOT EXISTS gap_matching_evidences (
    gap_id      BIGINT NOT NULL REFERENCES gap_results(id) ON DELETE CASCADE,
    evidence_id TEXT   NOT NULL REFERENCES profile_evidences(evidence_id) ON DELETE CASCADE,
    PRIMARY KEY (gap_id, evidence_id)
);

-- GapAnalysisSummary — one per tender (gaps fixture has results + summary)
CREATE TABLE IF NOT EXISTS gap_summaries (
    tender_id           UUID PRIMARY KEY REFERENCES tenders(tender_id) ON DELETE CASCADE,
    total_analyzed      INTEGER NOT NULL,
    full_match          INTEGER NOT NULL,
    partial_match       INTEGER NOT NULL,
    no_match            INTEGER NOT NULL,
    unknown             INTEGER NOT NULL,
    critical_gaps       INTEGER NOT NULL,
    sent_to_review_queue INTEGER NOT NULL
);

-- =============================================================================
-- decisions — TenderDecision (flattened HardGate / SoftScore / Risk / Summary)
-- One per tender.
-- =============================================================================
CREATE TABLE IF NOT EXISTS decisions (
    tender_id                  UUID PRIMARY KEY REFERENCES tenders(tender_id) ON DELETE CASCADE,
    schema_version_major       INTEGER NOT NULL DEFAULT 1,
    schema_version_minor       INTEGER NOT NULL DEFAULT 0,
    decision                   decision_type NOT NULL,
    decision_timestamp         TIMESTAMPTZ NOT NULL,
    rationale                  TEXT NOT NULL,
    -- HardGateResult
    hard_gate_passed           BOOLEAN NOT NULL,
    hard_gate_blocking_requirements TEXT[] NOT NULL DEFAULT '{}',
    hard_gate_blocking_reasons      TEXT[] NOT NULL DEFAULT '{}',
    -- SoftScoreResult (nullable block)
    soft_technical_score_estimate DOUBLE PRECISION,
    soft_max_score_available      DOUBLE PRECISION,
    soft_competitiveness          level_lmh,
    -- RiskAssessment
    risk_overall                  level_lmh NOT NULL,
    risk_max_penalty_exposure_pct DOUBLE PRECISION NOT NULL,
    risk_auto_termination_clauses TEXT[] NOT NULL DEFAULT '{}',
    risk_vendor_lock_in_detected  BOOLEAN NOT NULL,
    risk_sla_complexity           level_lmh NOT NULL,
    -- DecisionSummary
    summary_total_requirements    INTEGER NOT NULL,
    summary_met_full              INTEGER NOT NULL,
    summary_met_partial           INTEGER NOT NULL,
    summary_unmet                 INTEGER NOT NULL,
    summary_critical_gaps         INTEGER NOT NULL,
    summary_avg_confidence        DOUBLE PRECISION NOT NULL
);

-- TenderDecision.recommendations: list[Recommendation]
CREATE TABLE IF NOT EXISTS decision_recommendations (
    id                     BIGSERIAL PRIMARY KEY,
    tender_id              UUID NOT NULL REFERENCES decisions(tender_id) ON DELETE CASCADE,
    priority               level_lmh NOT NULL,
    text                   TEXT NOT NULL,
    targets_requirement_id TEXT
);
CREATE INDEX IF NOT EXISTS idx_dec_recs_tender ON decision_recommendations (tender_id);

-- TenderDecision.next_actions: list[NextAction]
CREATE TABLE IF NOT EXISTS decision_next_actions (
    id         BIGSERIAL PRIMARY KEY,
    tender_id  UUID NOT NULL REFERENCES decisions(tender_id) ON DELETE CASCADE,
    action     TEXT NOT NULL,
    deadline   DATE,
    owner_role TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_dec_actions_tender ON decision_next_actions (tender_id);

-- RiskAssessment.risk_factors: list[RiskFactor] (+ flattened SourceLocation)
CREATE TABLE IF NOT EXISTS decision_risk_factors (
    id                    BIGSERIAL PRIMARY KEY,
    tender_id             UUID NOT NULL REFERENCES decisions(tender_id) ON DELETE CASCADE,
    type                  TEXT NOT NULL,
    severity              level_lmh NOT NULL,
    description           TEXT NOT NULL,
    source_document_id    UUID,
    source_document_name  TEXT NOT NULL,
    source_section_id     TEXT,
    source_section_title  TEXT,
    source_page           INTEGER NOT NULL,
    source_char_start     INTEGER,
    source_char_end       INTEGER
);
CREATE INDEX IF NOT EXISTS idx_dec_risk_tender ON decision_risk_factors (tender_id);

-- =============================================================================
-- admin_checklist documents — AdminChecklist.documents_required: list[DocumentTodo]
-- (AdminChecklist itself is just tender_id + the list)
-- =============================================================================
CREATE TABLE IF NOT EXISTS document_todos (
    id                    BIGSERIAL PRIMARY KEY,
    tender_id             UUID NOT NULL REFERENCES tenders(tender_id) ON DELETE CASCADE,
    document_type         TEXT NOT NULL,
    description           TEXT NOT NULL,
    template_available    BOOLEAN NOT NULL,
    template_path         TEXT,
    source_requirement_id TEXT NOT NULL,
    deadline              DATE,
    owner_role            TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_doc_todos_tender ON document_todos (tender_id);

-- =============================================================================
-- audit_log — AuditEntry (append-only; per tender)
-- =============================================================================
CREATE TABLE IF NOT EXISTS audit_log (
    id        BIGSERIAL PRIMARY KEY,
    tender_id UUID NOT NULL REFERENCES tenders(tender_id) ON DELETE CASCADE,
    ts        TIMESTAMPTZ NOT NULL,             -- AuditEntry.timestamp
    actor     TEXT NOT NULL,
    action    TEXT NOT NULL,
    detail    TEXT NOT NULL,
    target    TEXT,
    payload   JSONB
);
CREATE INDEX IF NOT EXISTS idx_audit_tender_ts ON audit_log (tender_id, ts);

-- =============================================================================
-- review_queue_items — ReviewItem (+ flattened ReviewContext) (B7 HITL)
-- =============================================================================
CREATE TABLE IF NOT EXISTS review_queue_items (
    item_id                 UUID PRIMARY KEY,
    item_type               review_item_type NOT NULL,
    tender_id               UUID NOT NULL REFERENCES tenders(tender_id) ON DELETE CASCADE,
    payload                 JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at              TIMESTAMPTZ NOT NULL,
    priority               level_lmh NOT NULL,
    deadline               TIMESTAMPTZ,
    -- ReviewContext
    context_requirement_id  TEXT REFERENCES requirements(requirement_id) ON DELETE SET NULL,
    context_auto_suggestion TEXT
);
CREATE INDEX IF NOT EXISTS idx_review_tender   ON review_queue_items (tender_id);
CREATE INDEX IF NOT EXISTS idx_review_priority ON review_queue_items (priority);

-- ReviewContext.candidate_evidences: list[Evidence] (M:N)
CREATE TABLE IF NOT EXISTS review_candidate_evidences (
    item_id     UUID NOT NULL REFERENCES review_queue_items(item_id) ON DELETE CASCADE,
    evidence_id TEXT NOT NULL REFERENCES profile_evidences(evidence_id) ON DELETE CASCADE,
    PRIMARY KEY (item_id, evidence_id)
);

-- ReviewDecision — outcome of a human review (one per item)
CREATE TABLE IF NOT EXISTS review_decisions (
    item_id              UUID PRIMARY KEY REFERENCES review_queue_items(item_id) ON DELETE CASCADE,
    decided_by           TEXT NOT NULL,
    decided_at           TIMESTAMPTZ NOT NULL,
    action               review_action NOT NULL,
    modified_payload     JSONB,
    reviewer_notes       TEXT NOT NULL,
    propagate_to_profile BOOLEAN NOT NULL
);

-- =============================================================================
-- HTML-prototype domain (mirror of STCA_Platform_v2.html) — repository page
-- =============================================================================
CREATE TABLE IF NOT EXISTS bandi_html (
    id              TEXT PRIMARY KEY,
    nome            TEXT NOT NULL,
    short_nome      TEXT,
    ente            TEXT NOT NULL,
    valore          DOUBLE PRECISION NOT NULL,
    scadenza        TEXT NOT NULL,               -- model is str (display)
    giorni_mancanti INTEGER NOT NULL,
    canale          TEXT NOT NULL,
    cpv             TEXT NOT NULL,
    status          bando_status NOT NULL,
    uploaded_at     TEXT,
    files           TEXT[] NOT NULL DEFAULT '{}',
    analisi_completa BOOLEAN NOT NULL DEFAULT false,
    gng_confermato   BOOLEAN NOT NULL DEFAULT false
);
CREATE INDEX IF NOT EXISTS idx_bandi_status ON bandi_html (status);

-- RequisitoBando — get_bando_requisiti(bando_id)
CREATE TABLE IF NOT EXISTS requisiti_bando (
    id       TEXT PRIMARY KEY,
    bando_id TEXT NOT NULL REFERENCES bandi_html(id) ON DELETE CASCADE,
    cat      requirement_category NOT NULL,
    txt      TEXT NOT NULL,
    fonte    TEXT NOT NULL,
    tipo     requirement_type NOT NULL,
    status   req_status_html NOT NULL,
    ml       TEXT NOT NULL,
    mt       req_match_tone NOT NULL,
    nota     TEXT,
    rev_nota TEXT
);
CREATE INDEX IF NOT EXISTS idx_requisiti_bando ON requisiti_bando (bando_id);

-- ChecklistItemHTML — get_bando_checklist(bando_id)
CREATE TABLE IF NOT EXISTS checklist_html (
    id       TEXT PRIMARY KEY,
    bando_id TEXT NOT NULL REFERENCES bandi_html(id) ON DELETE CASCADE,
    cat      TEXT NOT NULL,
    txt      TEXT NOT NULL,
    sub      TEXT NOT NULL,
    done     BOOLEAN NOT NULL DEFAULT false,
    urgente  BOOLEAN NOT NULL DEFAULT false,
    warn     BOOLEAN NOT NULL DEFAULT false
);
CREATE INDEX IF NOT EXISTS idx_checklist_html_bando ON checklist_html (bando_id);

-- =============================================================================
-- cert_expiry — CertExpiry (alerts page: certifications nearing expiry)
-- =============================================================================
CREATE TABLE IF NOT EXISTS cert_expiry (
    id     BIGSERIAL PRIMARY KEY,
    nome   TEXT NOT NULL,
    ente   TEXT NOT NULL,
    scad   TEXT NOT NULL,                        -- model is str (display)
    giorni INTEGER NOT NULL,
    stato  cert_status_html NOT NULL,
    bandi  INTEGER NOT NULL
);

COMMIT;
