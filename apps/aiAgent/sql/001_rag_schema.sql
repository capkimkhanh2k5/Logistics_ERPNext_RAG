CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS unaccent;
CREATE SCHEMA IF NOT EXISTS rag;
CREATE TABLE IF NOT EXISTS rag.snapshots (
  id text PRIMARY KEY, manifest jsonb NOT NULL, created_at timestamptz DEFAULT now()
);
CREATE TABLE IF NOT EXISTS rag.chunks (
  snapshot text REFERENCES rag.snapshots(id), id text, dataset text NOT NULL,
  role text NOT NULL, code text, level integer, chapter text, heading text,
  source_text text NOT NULL, embedding_text text NOT NULL, metadata jsonb NOT NULL,
  locator jsonb NOT NULL, effective_from date, effective_to date,
  lexical tsvector NOT NULL, PRIMARY KEY(snapshot,id)
);
CREATE INDEX IF NOT EXISTS chunks_code ON rag.chunks(snapshot,code);
CREATE INDEX IF NOT EXISTS chunks_filter ON rag.chunks(snapshot,role,dataset,level);
CREATE INDEX IF NOT EXISTS chunks_lexical ON rag.chunks USING gin(lexical);
CREATE TABLE IF NOT EXISTS rag.profiles (
  id text PRIMARY KEY, config jsonb NOT NULL
);
CREATE TABLE IF NOT EXISTS rag.embeddings (
  snapshot text, chunk_id text, profile text REFERENCES rag.profiles(id),
  embedding vector(1024) NOT NULL,
  PRIMARY KEY(snapshot,chunk_id,profile),
  FOREIGN KEY(snapshot,chunk_id) REFERENCES rag.chunks(snapshot,id)
);
CREATE TABLE IF NOT EXISTS rag.sparse_postings (
  snapshot text, chunk_id text, profile text, token integer, weight real NOT NULL,
  PRIMARY KEY(snapshot,chunk_id,profile,token),
  FOREIGN KEY(snapshot,chunk_id,profile) REFERENCES rag.embeddings(snapshot,chunk_id,profile)
);
CREATE INDEX IF NOT EXISTS sparse_token ON rag.sparse_postings(snapshot,profile,token);
CREATE TABLE IF NOT EXISTS rag.graph_nodes (
  snapshot text REFERENCES rag.snapshots(id), id text, metadata jsonb NOT NULL,
  PRIMARY KEY(snapshot,id)
);
CREATE TABLE IF NOT EXISTS rag.graph_edges (
  snapshot text, id text, source text NOT NULL, target text NOT NULL,
  relation text NOT NULL, metadata jsonb NOT NULL, PRIMARY KEY(snapshot,id),
  FOREIGN KEY(snapshot,source) REFERENCES rag.graph_nodes(snapshot,id),
  FOREIGN KEY(snapshot,target) REFERENCES rag.graph_nodes(snapshot,id)
);
CREATE INDEX IF NOT EXISTS edges_source ON rag.graph_edges(snapshot,source);
CREATE INDEX IF NOT EXISTS edges_target ON rag.graph_edges(snapshot,target);
CREATE TABLE IF NOT EXISTS rag.active (
  singleton boolean PRIMARY KEY DEFAULT true CHECK(singleton),
  snapshot text REFERENCES rag.snapshots(id), profile text REFERENCES rag.profiles(id)
);
CREATE TABLE IF NOT EXISTS rag.evaluation_runs (
  id text PRIMARY KEY, snapshot text REFERENCES rag.snapshots(id),
  config jsonb NOT NULL, metrics jsonb NOT NULL, created_at timestamptz DEFAULT now()
);
CREATE TABLE IF NOT EXISTS rag.retrieval_results (
  run_id text REFERENCES rag.evaluation_runs(id), test_id text, variant text,
  result jsonb NOT NULL, PRIMARY KEY(run_id,test_id,variant)
);
