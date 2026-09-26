# Section XVI — Production RAG Ingest Guide

## Final dataset

```text
dataset_id      TT31_SECTION_XVI_HS2022_AHTN2022
dataset_version 2026-09-26.phase18.final
status          PRODUCTION_RAG_READY_SOURCE_ANOMALIES_RESOLVED
```

## Official data path

```text
TT31 PDF
  ↓
SECTION_XVI_MASTER_AUDITED_RAW.jsonl
  ↓
SECTION_XVI_MASTER_NORMALIZED.jsonl
  ↓
SECTION_XVI_RAG_INGEST.jsonl
  ↓
Vector DB / BM25 / Graph
```

## Files used by RAG

- `SECTION_XVI_MASTER_AUDITED_RAW.jsonl`: 3,421 audited raw records after Phase 17.
- `SECTION_XVI_MASTER_NORMALIZED.jsonl`: canonical production master.
- `SECTION_XVI_RAG_INGEST.jsonl`: primary Vector/BM25 ingest file.
- `SECTION_XVI_EXACT_CODE_INDEX.csv`: exact HS/AHTN lookup.
- `SECTION_XVI_GRAPH_STRUCTURAL_NODES.jsonl` + `SECTION_XVI_GRAPH_EDGES.jsonl`: graph traversal.

## 54 OCR/text-layer records

The original 54 records remain normalized for retrieval and preserved in the audit trail. They are not unresolved errors.

## 3 source anomalies

```text
SRCWARN_01 RESOLVED_OPERATIONALLY
SRCWARN_02 RESOLVED_OPERATIONALLY
SRCWARN_03 RESOLVED_OPERATIONALLY
```

See `SECTION_XVI_WARNING_RESOLUTIONS.json` and `SECTION_XVI_SOURCE_WARNINGS.csv`.

For these records:

```text
source_text_vi = exact TT31 wording
text_vi        = corrected operational wording
```

`SRCWARN_01` also adds `NORMALIZED_REFERENCE_TO` graph edges from Chapter 84 Note 11(A) to the Chapter 85 Note 12(a)/(b) chunk family.

## Recommended retrieval flow

```text
1. Scope Router
2. Exact-code lookup
3. BM25 / sparse retrieval
4. Dense retrieval
5. Legal-note expansion
6. Graph traversal
7. GIR Rule Engine
8. Critic / HITL
```
