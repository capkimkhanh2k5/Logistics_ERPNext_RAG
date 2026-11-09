-- 005_legal_versioning.sql
-- Table for tracking legal normative effects (Amendments, Replacements, Repeals) at provision level

CREATE SCHEMA IF NOT EXISTS rag;

CREATE TABLE IF NOT EXISTS rag.legal_effects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_document_id UUID,
    source_document_no TEXT,
    source_provision_anchor TEXT,
    target_document_id UUID,
    target_document_no TEXT,
    target_provision_anchor TEXT,
    effect_type TEXT NOT NULL, -- 'AMENDS', 'REPLACES', 'REPEALS', 'SUSPENDS', 'REFERENCES'
    effective_from DATE,
    effective_to DATE,
    verification_status TEXT DEFAULT 'VERIFIED', -- 'VERIFIED', 'PROPOSED', 'UNVERIFIED'
    verified_by TEXT DEFAULT 'system',
    source_reference TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT clock_timestamp()
);

CREATE INDEX IF NOT EXISTS idx_legal_effects_target ON rag.legal_effects(target_document_no, target_provision_anchor);
CREATE INDEX IF NOT EXISTS idx_legal_effects_type ON rag.legal_effects(effect_type);
CREATE INDEX IF NOT EXISTS idx_legal_effects_dates ON rag.legal_effects(effective_from, effective_to);
