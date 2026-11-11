# TradeRAG: Hierarchical Hybrid RAG & Knowledge Graph for Customs Classification

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17%20%2B%20pgvector%20%2B%20Apache%20AGE-336791.svg)](https://www.postgresql.org/)
[![Embedding](https://img.shields.io/badge/Embedding-BGE--M3%20(Dense%20%2B%20Sparse)-red.svg)](https://huggingface.co/BAAI/bge-m3)
[![Reranker](https://img.shields.io/badge/Reranker-BGE--v2--M3%20%E2%86%92%20Qwen3--0.6B-purple.svg)](https://huggingface.co/BAAI/bge-reranker-v2-m3)
[![Benchmark](https://img.shields.io/badge/HS%20Recall%4010-97.3%25-success.svg)](#-empirical-benchmarks)
[![License](https://img.shields.io/badge/License-Proprietary%20%2F%20GPLv3-green.svg)](#-license)

> **TradeRAG** is a domain-specialized, enterprise-grade Retrieval-Augmented Generation (RAG) system engineered for **statutory customs law and 8-digit Harmonized System (HS) Code classification**. It couples 5-channel hybrid search, a graph-modeled legal hierarchy (Apache AGE), two-stage cascade reranking, and an epistemic product-review protocol to eliminate hallucinations in mission-critical trade compliance.

---

## ⚡ The Challenge: Why Standard RAG Fails in Customs

Zero-shot LLMs and flat vector search fail catastrophically in statutory classification:

- **Strict Hierarchical Constraints**: HS codes are non-flat taxonomies: $\text{Section} \to \text{Chapter (2)} \to \text{Heading (4)} \to \text{Subheading (6)} \to \text{Tariff Line (8)}$. A valid code requires satisfying every parent level's legal scope.
- **Statutory Exclusion Precedence**: Legal notes (Section/Chapter Notes) enforce strict exclusions (e.g., *"Automobile seats are excluded from Ch.94 and governed by Ch.87"*). Flat cosine similarity misses these governing conditions.
- **Rule Hierarchy (GIR 1–6)**: Classification must legally adhere to 6 General Interpretative Rules (GIR) in strict sequence.
- **Premature Assumptions vs. Abstention**: When technical specifications are missing (e.g., voltage, cylinder capacity, vehicle weight), standard LLMs hallucinate digits rather than clarifying.

---

## 🏛️ System Architecture

TradeRAG combines dense/sparse lexical retrieval, multi-level graph traversal, cascade neural reranking, and dual-agent verification:

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                            USER QUERY & SPECIFICATION                            │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│      QueryPlanner: Single-pass Intent Classification & Keyword Expansion         │
└──────┬────────────────────────────────────────────────────────────────────┬──────┘
       │ Direct Source Search                                               │ Graph Expansion
       ▼                                                                    ▼
┌──────────────────────────────────────┐   ┌───────────────────────────────────────┐
│     5-CHANNEL HYBRID RETRIEVAL       │   │       KNOWLEDGE GRAPH TRAVERSAL       │
│  - Dense: BGE-M3 1024d       (0.35)  │   │  - PostgreSQL 17 + Apache AGE (Cypher)│
│  - Context BM25Okapi         (0.35)  │   │  - Ancestor Chain (Depth <= 12)       │
│  - Learned Sparse: BGE-M3    (0.15)  │   │  - Edges: CONTAINS, CONTEXT_FOR       │
│  - Exact Match: Code/Spec    (0.10)  │   │  - Exclusions: APPLIES_TO, GOVERNS    │
│  - PostgreSQL FTS unaccent   (0.05)  │   │  - Sibling Expansion (160 Peer Codes) │
└──────────────────┬───────────────────┘   └───────────────────┬───────────────────┘
                   │                                           │
                   └─────────────────────┬─────────────────────┘
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│     MULTI-CHANNEL FUSION (RRF k=60) ➔ Top 160 Candidate Pool                     │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│     TWO-STAGE CASCADE RERANKING                                                  │
│     - Stage 1: BGE-reranker-v2-m3 (Top 100, rank weight 0.85)                    │
│     - Stage 2: Qwen3-Reranker-0.6B (Top 40 deep cross-attention, weight 0.50)   │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│     GENERATION, PRODUCT REVIEW & EPISTEMIC ABSTENTION                            │
│     - Candidate Drafting (HS4 / HS6 / HS8 level resolution)                      │
│     - Independent Batch Review: Spec grounding vs. 160 Sibling Branch Codes      │
│     - Bounded Evidence Recovery: Max 1 retrieval retry cycle for missing law     │
│     - Epistemic States: SUPPORTED | MISSING_PRODUCT_INFO | INSUFFICIENT_EVIDENCE │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔬 Core Innovations

### 1. Deterministic Ingestion & Content-Hash Embedding Cache
- **Canonical ID Schema**: Every segment receives a deterministic legal address (e.g., `tariff:tt31:hs8:85171300`, `legal:tt85_2026:art_3_clause_1`, `legal:gir:rule_3b`).
- **Zero-Waste Re-Ingestion**: Ingestion computes $\text{SHA-256}(\text{source\_text} + \text{embedding\_text})$. Re-uploaded or amended legal DOCX files achieve **100% vector reuse** on unchanged sections via `embedding_cache`, eliminating redundant embedding inference and preventing chunk duplication.

### 2. Hierarchical Hybrid Retrieval Pipeline (v5)

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             USER QUERY (Product / Legal)                         │
└────────┬────────────────────────────────────────┬────────────────────────────────┘
         │                                        │
         ▼                                        ▼
┌─────────────────────────────────┐      ┌─────────────────────────────────┐
│     DIRECT SOURCE CHANNELS      │      │     GRAPH CONTEXT EXPANSION     │
│  - Dense (BGE-M3 1024d)  : 0.35 │      │  - Hierarchical Path Traversal  │
│  - BM25Okapi (Tariff)    : 0.35 │      │  - Context Dense Embedding      │
│  - Sparse (BGE-M3 Tokens): 0.15 │      │  - Context BM25 Matching        │
│  - Exact Match (Regex)   : 0.10 │      │  - Relational Notes & Exclusions│
│  - Postgres FTS (unacc.) : 0.05 │      └────────────────┬────────────────┘
└────────────────┬────────────────┘                       │
                 │                                        │
                 └──────────────────┬─────────────────────┘
                                    ▼
       ┌──────────────────────────────────────────────────────────┐
       │   MULTI-CHANNEL FUSION: Reciprocal Rank Fusion (k=60)    │
       │   Deduplicated Candidate Pool (Cap: 160 Source Items)    │
       └────────────────────────────┬─────────────────────────────┘
                                    ▼
       ┌──────────────────────────────────────────────────────────┐
       │   STAGE 1 RERANKING: BGE-reranker-v2-m3                  │
       │   - Scores Top 100 candidates from pool                  │
       │   - RRF Fusion: 0.15 Pool Rank + 0.85 Model Rank         │
       └────────────────────────────┬─────────────────────────────┘
                                    ▼
       ┌──────────────────────────────────────────────────────────┐
       │   STAGE 2 RERANKING: Qwen3-Reranker-0.6B                 │
       │   - Deep cross-attention on Top 40 candidates            │
       │   - RRF Fusion: 0.50 Stage 1 Rank + 0.50 Qwen Rank       │
       └────────────────────────────┬─────────────────────────────┘
                                    ▼
       ┌──────────────────────────────────────────────────────────┐
       │   FINAL RETRIEVAL PACKAGE                                │
       │   - Top-10 Primary Statutory Matches                     │
       │   - Ranked HS8 Candidate Shortlist                       │
       │   - Context-bound Graph Evidence & Provenance            │
       └──────────────────────────────────────────────────────────┘
```

- Five channels fused via Reciprocal Rank Fusion ($RRF, k=60$):
  $$\text{RRF Score}(d) = \sum_{c \in \text{Channels}} w_c \cdot \frac{1}{60 + \text{Rank}_c(d)}$$
- Combines semantic understanding (`Dense`), technical term matching (`BM25Okapi`), domain vocabulary (`Learned Sparse`), regex code identifiers (`Exact`), and full-text database indexing (`FTS`).

### 3. Knowledge Graph Engine (PostgreSQL 17 + Apache AGE)
- **Hierarchy Representation**: Nodes represent Sections, Chapters, Headings, Subheadings, Tariff Lines, and Legal Notes.
- **Relational Edges**: `CONTAINS` (ancestor path), `CONTEXT_FOR` (un-coded classification headers), `APPLIES_TO` / `GOVERNS` (scope of notes), and `CONSTRAINED_BY` (exclusions).
- **Depth-12 Ancestor Traversal**: Enables dynamic retrieval of the entire statutory path and mandatory chapter exclusions to ground the LLM prompt.

### 4. Two-Stage Cascade Reranker
- **Stage 1 (High-Throughput Filter)**: `BGE-reranker-v2-m3` evaluates the top 100 candidates from the 160-item pool.
- **Stage 2 (Deep Attention Cross-Encoder)**: `Qwen3-Reranker-0.6B` re-scores the top 40 items.
- **Rank Combination via RRF**: Avoids uncalibrated cross-model logit distortion by combining rank orders rather than raw prediction scores.

### 5. Generation, Product Review & Epistemic Abstention

```text
                        ┌──────────────────────────────┐
                        │      User Query / Input      │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │     QueryPlanner Request     │
                        │  (Intent, Specs, Keywords)   │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │  Hybrid Retrieval & Graph    │
                        │   (Top Statutory Evidence)   │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │      Drafting Candidate      │
                        │ (HS4 / HS6 / HS8 Resolution) │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │   Structural & Graph Check   │
                        │ (ASCII 8-digit, CONTAINS,    │
                        │  verbatim PDF wording match) │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │     Batch Product Review     │
                        │  (Independent Spec Match vs  │
                        │   160 Peer Branch Codes)     │
                        └──────────────┬───────────────┘
                                       │
             ┌─────────────────────────┼─────────────────────────┐
             │                         │                         │
             ▼                         ▼                         ▼
   [ Fully Grounded ]       [ Incomplete Specs ]      [ Missing Legal Basis ]
             │                         │                         │
             ▼                         ▼                         ▼
   ┌───────────────────┐     ┌───────────────────┐     ┌───────────────────┐
   │    SUPPORTED      │     │  MISSING_PRODUCT_ │     │   Bounded Legal   │
   │  - Final HS Code  │     │       INFO        │     │  Recovery Loop?   │
   │  - 6 GIR Rules    │     │ - Prompt user for │     └─────────┬─────────┘
   │  - Legal Citations│     │   missing params  │               │
   └───────────────────┘     │ - NO legal jargon │        ┌──────┴──────┐
                             └───────────────────┘        ▼             ▼
                                                        [Yes]          [No]
                                                          │             │
                                                (1 Retrial Cycle)       ▼
                                                          │    ┌─────────────────┐
                                                          │    │  INSUFFICIENT_  │
                                                          │    │ EVIDENCE REPORT │
                                                          │    │ - Corpus Gap    │
                                                          │    │ - Zero guess    │
                                                          │    └─────────────────┘
```

- **Independent Reviewer (Confirmation Bias Defense)**: The reviewer LLM evaluates candidate conditions against verbatim user statements without seeing the drafter's proposed code.
- **Branch Disambiguation**: Evaluates up to **160 sibling branch codes** to verify that alternative subheadings are demonstrably inapplicable before approving a classification.
- **Three Strict Epistemic States**:
  - `SUPPORTED`: 100% of branch conditions verified with verbatim citations.
  - `MISSING_PRODUCT_INFO`: Insufficient technical parameters; generates clarifying questions for the user.
  - `INSUFFICIENT_LEGAL_EVIDENCE`: Corpus gap; abstains and logs diagnostic gaps without asking the user for legal advice.

---

## 📊 Empirical Benchmarks

Evaluated on **1,272 Dev queries** and **318 independent Test queries** spanning the most legally intricate tariff sections: **Section XIV** (Ch.71: Jewelry/Precious Metals), **Section XVI** (Ch.84–85: Machinery/Electronics), and **Section XVII** (Ch.87: Vehicles).

### HS Code Shortlist Performance (188 Independent Test Queries)

| Tariff Domain | Queries | Hit@1 | Recall@5 | Recall@10 | MRR@10 |
|---|:---:|:---:|:---:|:---:|:---:|
| **Section XIV** (Ch. 71) | 49 | 51.0% | 91.8% | 98.0% | 0.6938 |
| **Section XVI** (Ch. 84, 85) | 85 | **81.2%** | **94.1%** | **98.8%** | **0.8696** |
| **Section XVII** (Ch. 87) | 54 | 63.0% | 83.3% | 94.4% | 0.7286 |
| **Total Test Benchmark** | **188** | **68.1%** | **90.4%** | **97.3%** | **0.7833** |

### Legal Statutory QA Performance (130 Independent Test Queries)

| Metric | Score | Target |
|---|:---:|:---:|
| **Top-10 Primary Statutory Coverage** | **93.1%** (121 / 130) | $\ge 90.0\%$ |
| **Legal MRR@10** | **0.7675** | $\ge 0.7500$ |
| **Extended Package Evidence Coverage** | **94.6%** (123 / 130) | $\ge 92.0\%$ |

---

## 🛠️ Tech Stack

| Component | Technology | Role |
|---|---|---|
| **Vector DB & Graph** | PostgreSQL 17 + `pgvector` + `Apache AGE` | Dense/Sparse vector index & Cypher property graph |
| **Embeddings** | `BAAI/bge-m3` | 1024-dim dense vectors & learned sparse token weights |
| **Lexical Index** | `BM25Okapi` + PostgreSQL `tsvector` | Hierarchical context BM25 & unaccented full-text search |
| **Rerankers** | `BGE-reranker-v2-m3` $\to$ `Qwen3-Reranker-0.6B` | Two-stage cascade cross-encoder |
| **LLM Gateway** | `CLIProxyAPI` | Model pooling, token budgeting, and fallback |
| **Host ERP** | `Frappe Framework` / `ERPNext v15` | Business logic, customs documents, and desk copilot |

---
