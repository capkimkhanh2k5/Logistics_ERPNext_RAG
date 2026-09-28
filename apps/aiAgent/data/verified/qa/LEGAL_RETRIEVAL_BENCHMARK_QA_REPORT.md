# Legal Retrieval Benchmark V5 — Final QA Report

## 1. Scope correction

Both benchmark subsets are treated as **Legal Retrieval**:

- `expanded_200`: 200 legal-retrieval queries.
- `original_50`: the earlier 50 queries, also evaluated strictly as retrieval of legal/tariff evidence.

Some queries are phrased as “thuộc nhóm/mã nào?”, but the scored output in this benchmark is the retrieved legal/tariff evidence chunk, not the generated final HS answer.

All 250 records therefore use `benchmark_family = legal_retrieval`, `task_family = legal_retrieval`, and `evaluation_target = legal_evidence_rag_chunk`.

## 2. Validation of the three supplied Section RAG_INGEST files

### Section XIV
- MASTER_NORMALIZED records: **190**
- RAG_INGEST chunks: **190**
- MASTER `id` → RAG `source_record_id`: **190/190 exact**
- Missing: **0**
- Duplicate RAG source IDs: **0**
- Retrieval enabled: **190/190**
- Canonical chunk mapping: `MASTER.id -> RAG.document_id`

### Section XVI
- MASTER_NORMALIZED records: **3421**
- RAG_INGEST chunks: **3421**
- MASTER `record_id` → RAG `id`: **3421/3421 exact**
- Missing: **0**
- Duplicate RAG IDs: **0**
- `READY_FOR_INGEST`: **3421/3421**
- Canonical chunk mapping: `MASTER.record_id -> RAG.id`

### Section XVII
- MASTER_NORMALIZED nodes: **1456**
- RAG_INGEST chunks: **1433**
- MASTER nodes represented in RAG: **1433**
- Not represented in RAG: **23**
- All **23** omitted nodes are `external_reference` records with `is_external=true`.
- **No benchmark gold target uses any omitted external-reference node.**
- Duplicate RAG source-node IDs: **0**
- Canonical chunk mapping: `MASTER.id/source_node_id -> RAG.document_id`

Omitted Section XVII external-reference nodes:
- `EXT_CHAPTER_39`
- `EXT_CHAPTER_82`
- `EXT_CHAPTER_85`
- `EXT_CHAPTER_90`
- `EXT_CHAPTER_91`
- `EXT_CHAPTER_93`
- `EXT_HEADING_40_16`
- `EXT_HEADING_44_06`
- `EXT_HEADING_68_10`
- `EXT_HEADING_73_02`
- `EXT_HEADING_83_06`
- `EXT_HEADING_84_81`
- `EXT_HEADING_84_82`
- `EXT_HEADING_84_83`
- `EXT_HEADING_84_84`
- `EXT_HEADING_85_30`
- `EXT_HEADING_94_05`
- `EXT_HEADING_95_03`
- `EXT_HEADING_95_06`
- `EXT_HEADING_95_08`
- `EXT_HEADING_96_03`
- `EXT_HEADING_RANGE_84_01_TO_84_79`
- `EXT_SECTION_XV`

## 3. GIR and TT85

- GIR canonical RAG records: **115**; unique IDs: **115**.
- TT85 canonical RAG chunks: **100**; unique chunk IDs: **100**.
- For GIR and TT85, the stable record ID is already the canonical retrieval chunk ID.

## 4. Benchmark QA

- Expanded Legal Retrieval set: **200/200**
- Original Legal Retrieval set: **50/50**
- Combined master: **250/250**
- Unique question IDs: **250/250**
- Questions with exact RAG chunk gold mapping: **250/250**
- Questions missing a gold chunk: **0**
- Unique source-record gold IDs: **146**
- Unique canonical RAG gold chunk IDs: **146**
- Missing gold record IDs in supplied RAG sources: **0**
- Missing gold chunk IDs in supplied RAG sources: **0**
- Primary/secondary overlap inside a question: **0**
- Exact duplicate query texts across all 250: **0**

Unique gold-record distribution by source:
- GIR: **16**
- TT31_SECTION_XIV: **23**
- TT31_SECTION_XVI: **33**
- TT31_SECTION_XVII: **24**
- TT85: **50**

## 5. Recheck of the original 50 questions

All earlier 50 questions are now explicitly classified as **Legal Retrieval**, not as a separate HS-classification benchmark.

For the **45** original questions whose human-reference target contains a numeric HS code, the code was programmatically checked against the mapped primary RAG evidence: **45/45 passed**.

The remaining five are rule/exclusion questions and are validated by exact GIR/legal-note/TT85 chunk mapping.

`expected_target` is kept only for human readability and marked `expected_target_role = HUMAN_REFERENCE_ONLY_NOT_RETRIEVAL_SCORE`.

## 6. Cross-subset overlap

- Original-50 questions with at least one exact-gold-set overlap with the 200-set: **8**.
- Pairwise cross-subset overlap relationships: **17**.
- This is not a mapping error: the query texts are different, while the correct evidence set can be identical.

- `LQ010` ↔ `Q132` — `XIV_CH71_NOTE_02`
- `LQ010` ↔ `Q133` — `XIV_CH71_NOTE_02`
- `LQ027` ↔ `Q191` — `SXVI-T-8501, SXVII_NOTE_2`
- `LQ028` ↔ `Q192` — `SXVI-T-8482, SXVII_NOTE_2`
- `LQ029` ↔ `Q157` — `SXVI-N-SXVI_NOTE_3`
- `LQ029` ↔ `Q158` — `SXVI-N-SXVI_NOTE_3`
- `LQ046` ↔ `Q041` — `GIR_1`
- `LQ046` ↔ `Q042` — `GIR_1`
- `LQ046` ↔ `Q043` — `GIR_1`
- `LQ046` ↔ `Q044` — `GIR_1`
- `LQ046` ↔ `Q045` — `GIR_1`
- `LQ046` ↔ `Q090` — `GIR_1`
- `LQ047` ↔ `Q100` — `GIR_2A, TT85-A8-p1`
- `LQ047` ↔ `Q101` — `GIR_2A, TT85-A8-p1`
- `LQ049` ↔ `Q066` — `GIR_5A`
- `LQ049` ↔ `Q068` — `GIR_5A`
- `LQ050` ↔ `Q070` — `GIR_6`

## 7. Canonical scoring fields

- `gold_primary_chunk_ids`: primary required legal evidence.
- `gold_secondary_chunk_ids`: supporting legal evidence.
- `gold_chunk_ids`: union of primary + secondary.
- `gold_retrieval_ids`: canonical alias of `gold_chunk_ids`.
- `gold_record_ids`: stable source-record IDs retained for traceability/audit.

Do not score retrieval against `expected_target`; that field is only a human-readable reference.

## 8. Final status

**PASS — ready for Legal Retrieval evaluation.**

The three supplied Section `RAG_INGEST` files are the correct files needed to complete exact chunk-level mapping. The benchmark no longer has Section XIV/XVI/XVII record-only placeholders.