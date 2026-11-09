-- 004_staging_schema.sql
-- Comprehensive schema for Staging Area, Immutable Snapshots, and Ingestion Jobs

CREATE SCHEMA IF NOT EXISTS rag;

-- 1. Staged Documents
CREATE TABLE IF NOT EXISTS rag.staged_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    logical_document_id UUID NULL,
    filename TEXT NOT NULL,
    document_no TEXT,
    document_type TEXT NOT NULL,
    file_sha256 CHAR(64) NOT NULL,
    file_path TEXT NOT NULL,
    parser_version TEXT NOT NULL DEFAULT '3.0.0',
    status TEXT NOT NULL DEFAULT 'PARSED',
    total_nodes INT DEFAULT 0,
    total_chunks INT DEFAULT 0,
    approved_chunks INT DEFAULT 0,
    excluded_chunks INT DEFAULT 0,
    effective_from DATE,
    effective_to DATE,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_by TEXT DEFAULT 'system',
    created_at TIMESTAMPTZ DEFAULT clock_timestamp(),
    reviewed_by TEXT,
    reviewed_at TIMESTAMPTZ,
    committed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_staged_docs_status ON rag.staged_documents(status);
CREATE INDEX IF NOT EXISTS idx_staged_docs_created ON rag.staged_documents(created_at DESC);

-- 2. Staged Structural Hierarchy Nodes
CREATE TABLE IF NOT EXISTS rag.staged_nodes (
    id TEXT PRIMARY KEY,
    document_id UUID NOT NULL REFERENCES rag.staged_documents(id) ON DELETE CASCADE,
    parent_node_id TEXT REFERENCES rag.staged_nodes(id) ON DELETE CASCADE,
    node_type TEXT NOT NULL,
    node_level INT NOT NULL,
    node_order INT NOT NULL,
    canonical_anchor TEXT,
    code TEXT,
    title TEXT,
    source_text TEXT,
    source_location JSONB DEFAULT '{}'::jsonb,
    breadcrumb TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_staged_nodes_doc ON rag.staged_nodes(document_id);
CREATE INDEX IF NOT EXISTS idx_staged_nodes_parent ON rag.staged_nodes(parent_node_id);
CREATE INDEX IF NOT EXISTS idx_staged_nodes_code ON rag.staged_nodes(code);

-- 3. Staged Atomic Chunks
CREATE TABLE IF NOT EXISTS rag.staged_chunks (
    id TEXT PRIMARY KEY,
    document_id UUID NOT NULL REFERENCES rag.staged_documents(id) ON DELETE CASCADE,
    node_id TEXT REFERENCES rag.staged_nodes(id) ON DELETE CASCADE,
    chunk_index INT NOT NULL,
    chunk_type TEXT NOT NULL,
    canonical_anchor TEXT,
    code TEXT,
    level INT,
    role TEXT NOT NULL DEFAULT 'candidate',
    namespace TEXT NOT NULL DEFAULT 'hs_classification',
    source_text TEXT NOT NULL,
    edited_text TEXT,
    embedding_text TEXT NOT NULL,
    embedding_hash CHAR(64),
    breadcrumb TEXT NOT NULL,
    source_location JSONB DEFAULT '{}'::jsonb,
    review_status TEXT NOT NULL DEFAULT 'PENDING_REVIEW',
    revision INT NOT NULL DEFAULT 1,
    confidence_score NUMERIC DEFAULT 1.0,
    validation_issues JSONB DEFAULT '[]'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,
    reviewed_by TEXT,
    reviewed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ DEFAULT clock_timestamp()
);

CREATE INDEX IF NOT EXISTS idx_staged_chunks_doc ON rag.staged_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_staged_chunks_status ON rag.staged_chunks(document_id, review_status);
CREATE INDEX IF NOT EXISTS idx_staged_chunks_code ON rag.staged_chunks(code);

-- 4. Staged Chunk Revisions (Audit log of all edits)
CREATE TABLE IF NOT EXISTS rag.staged_chunk_revisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chunk_id TEXT NOT NULL REFERENCES rag.staged_chunks(id) ON DELETE CASCADE,
    revision_no INT NOT NULL,
    old_value JSONB NOT NULL,
    new_value JSONB NOT NULL,
    change_reason TEXT,
    changed_by TEXT DEFAULT 'system',
    changed_at TIMESTAMPTZ DEFAULT clock_timestamp()
);

CREATE INDEX IF NOT EXISTS idx_chunk_revisions_chunk ON rag.staged_chunk_revisions(chunk_id);

-- 5. Approved Snapshots (Immutable artifact ready for background ingestion)
CREATE TABLE IF NOT EXISTS rag.approved_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    staged_document_id UUID NOT NULL REFERENCES rag.staged_documents(id) ON DELETE CASCADE,
    snapshot_hash CHAR(64) NOT NULL,
    total_records INT NOT NULL,
    snapshot_data JSONB NOT NULL,
    approved_by TEXT NOT NULL DEFAULT 'system',
    approved_at TIMESTAMPTZ DEFAULT clock_timestamp()
);

CREATE INDEX IF NOT EXISTS idx_approved_snapshots_doc ON rag.approved_snapshots(staged_document_id);

-- 6. Ingestion Jobs
CREATE TABLE IF NOT EXISTS rag.ingestion_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    staged_document_id UUID NOT NULL REFERENCES rag.staged_documents(id) ON DELETE CASCADE,
    snapshot_id UUID NOT NULL REFERENCES rag.approved_snapshots(id) ON DELETE CASCADE,
    idempotency_key TEXT UNIQUE NOT NULL,
    status TEXT NOT NULL DEFAULT 'QUEUED',
    stage TEXT NOT NULL DEFAULT 'INIT',
    total_chunks INT NOT NULL,
    processed_chunks INT DEFAULT 0,
    failed_chunks INT DEFAULT 0,
    retry_count INT DEFAULT 0,
    error_code TEXT,
    error_message TEXT,
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_ingestion_jobs_status ON rag.ingestion_jobs(status);

-- 7. Transactional Outbox
CREATE TABLE IF NOT EXISTS rag.ingestion_outbox (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES rag.ingestion_jobs(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    payload JSONB NOT NULL,
    status TEXT NOT NULL DEFAULT 'PENDING',
    attempt_count INT DEFAULT 0,
    next_attempt_at TIMESTAMPTZ DEFAULT clock_timestamp(),
    created_at TIMESTAMPTZ DEFAULT clock_timestamp(),
    dispatched_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_outbox_status ON rag.ingestion_outbox(status, next_attempt_at);
