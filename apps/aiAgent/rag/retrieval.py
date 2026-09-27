"""Parameterized hybrid retrieval with separate tariff and evidence results."""

import re
import time
from datetime import date
from typing import Any

import psycopg
from pgvector.psycopg import register_vector
from psycopg import sql as pgsql

from rag.data import ROOT, config, normalize_code, read
from rag.embedding import Embedder


def fuse(
    branches: dict[str, list[dict]], rrf_k: int = 60, weights: dict | None = None
) -> list[dict]:
    by_id: dict[str, dict] = {}
    for branch, rows in branches.items():
        seen = set()
        for rank, row in enumerate(rows, 1):
            if row["id"] in seen:
                continue
            seen.add(row["id"])
            entry = by_id.setdefault(row["id"], {**row, "rrf_score": 0.0, "branches": {}})
            entry["rrf_score"] += (weights or {}).get(branch, 1.0) / (rrf_k + rank)
            entry["branches"][branch] = {"rank": rank, "score": float(row["score"])}
    return sorted(by_id.values(), key=lambda x: (-x["rrf_score"], x["id"]))


def unique_codes(rows: list[dict], limit: int) -> list[dict]:
    output = []
    seen = set()
    for row in rows:
        if row.get("code") and row["code"] not in seen:
            seen.add(row["code"])
            output.append(row)
        if len(output) == limit:
            break
    return output


class Retriever:
    def __init__(
        self, conn: psycopg.Connection[dict[str, Any]], embedder: Embedder | None = None
    ) -> None:
        register_vector(conn)
        self.conn = conn
        self.embedder = embedder
        self.cfg = config()
        active = conn.execute("SELECT snapshot,profile FROM rag.active").fetchone()
        if not active:
            raise ValueError("No complete active ingestion snapshot")
        self.snapshot, self.profile = active["snapshot"], active["profile"]
        self.default_mode = "dense_sparse"
        self.weights = self.cfg.get("fusion_weights", {})
        selection_path = ROOT / "config/selected_retrieval.json"
        if selection_path.exists():
            selection = read(selection_path)
            if (
                selection["snapshot"] == self.snapshot
                and selection["profile"] == self.profile
                and selection["retrieval"] == self.cfg
            ):
                self.default_mode = selection["selected_mode"]
                self.weights = selection.get("weights", self.weights)
        if embedder and embedder.profile_id != self.profile:
            raise ValueError("Query embedding profile differs from active database profile")

    def _filter(
        self, intent: str, as_of: date | None, chapters: list[str] | None
    ) -> tuple[str, list]:
        clause = "c.snapshot=%s"
        params: list[Any] = [self.snapshot]
        if intent == "product":
            clause += " AND c.role='candidate' AND c.level=8"
        elif intent == "scope":
            clause += " AND c.role='scope'"
        elif intent in ("gir", "tt85"):
            clause += " AND c.dataset=%s"
            params.append(intent)
        else:
            raise ValueError("Intent must be product, scope, gir, or tt85")
        if chapters:
            clause += " AND c.chapter=ANY(%s)"
            params.append(chapters)
        if as_of:
            # Unknown validity is excluded from date-constrained search.
            clause += " AND c.effective_from IS NOT NULL AND c.effective_from<=%s "
            clause += "AND (c.effective_to IS NULL OR c.effective_to>%s)"
            params.extend([as_of, as_of])
        return clause, params

    def lexical(
        self,
        query: str,
        intent: str = "product",
        limit: int = 50,
        as_of: date | None = None,
        chapters: list[str] | None = None,
    ) -> list[dict]:
        clause, params = self._filter(intent, as_of, chapters)
        # OR lexical candidates handle long product specifications without requiring every term.
        sql = pgsql.SQL(
            """WITH terms AS (
          SELECT unnest(tsvector_to_array(to_tsvector('simple',unaccent(%s)))) AS term
        ), useful AS (SELECT term FROM terms WHERE term <> ALL(%s::text[])), q AS (SELECT to_tsquery('simple',string_agg(quote_literal(term),' | ')) AS query FROM useful)
        SELECT c.*, ts_rank_cd(c.lexical,q.query)::float AS score FROM rag.chunks c CROSS JOIN q
        WHERE {where} AND c.lexical @@ q.query
        ORDER BY score DESC,c.id LIMIT %s"""
        ).format(where=pgsql.SQL(clause))
        return self.conn.execute(
            sql,
            [
                query,
                [
                    "va",
                    "cua",
                    "cho",
                    "co",
                    "la",
                    "cac",
                    "nhung",
                    "de",
                    "duoc",
                    "mot",
                    "nhieu",
                    "voi",
                    "theo",
                    "thuoc",
                    "bao",
                    "gom",
                ],
                *params,
                limit,
            ],
        ).fetchall()

    def dense(
        self,
        vector: Any,
        intent: str = "product",
        limit: int = 50,
        as_of: date | None = None,
        chapters: list[str] | None = None,
    ) -> list[dict]:
        clause, params = self._filter(intent, as_of, chapters)
        sql = pgsql.SQL(
            """SELECT c.*, (1-(e.embedding <=> %s))::float AS score
        FROM rag.embeddings e JOIN rag.chunks c ON c.snapshot=e.snapshot AND c.id=e.chunk_id
        WHERE e.profile=%s AND {where}
        ORDER BY e.embedding <=> %s,c.id LIMIT %s"""
        ).format(where=pgsql.SQL(clause))
        return self.conn.execute(sql, [vector, self.profile, *params, vector, limit]).fetchall()

    def sparse(
        self,
        weights: dict,
        intent: str = "product",
        limit: int = 50,
        as_of: date | None = None,
        chapters: list[str] | None = None,
    ) -> list[dict]:
        if not weights:
            return []
        clause, params = self._filter(intent, as_of, chapters)
        sql = pgsql.SQL(
            """WITH q AS (SELECT * FROM unnest(%s::integer[],%s::real[]) AS t(token,weight)),
        scores AS (
          SELECT p.chunk_id, sum(p.weight*q.weight)::float AS score
          FROM rag.sparse_postings p JOIN q USING(token)
          WHERE p.snapshot=%s AND p.profile=%s GROUP BY p.chunk_id
        ) SELECT c.*,s.score FROM scores s JOIN rag.chunks c ON s.chunk_id=c.id
        WHERE {where} ORDER BY s.score DESC,c.id LIMIT %s"""
        ).format(where=pgsql.SQL(clause))
        tokens = [int(k) for k in weights]
        values = [float(v) for v in weights.values()]
        return self.conn.execute(
            sql, [tokens, values, self.snapshot, self.profile, *params, limit]
        ).fetchall()

    def exact(self, code: str) -> list[dict]:
        code = normalize_code(code)
        return self.conn.execute(
            "SELECT *,1.0 AS score FROM rag.chunks WHERE snapshot=%s AND code=%s ORDER BY id",
            (self.snapshot, code),
        ).fetchall()

    def evidence(
        self,
        candidates: list[dict],
        limit: int = 30,
        hops: int = 2,
        max_chars: int = 16000,
        query_vector: Any = None,
    ) -> dict:
        if not candidates:
            return {
                "records": [],
                "trace": [],
                "omitted_ids": [],
                "required_ids": [],
                "missing_required_ids": [],
                "character_budget": max_chars,
                "coverage_status": "NO_CANDIDATES",
            }
        ancestors = {r["id"] for r in candidates[:3]}
        frontier = sorted(ancestors)
        trace: list[dict] = []
        # Follow only upward CONTAINS edges, never all descendants of a chapter.
        for _ in range(4):
            edges = self.conn.execute(
                """SELECT * FROM rag.graph_edges WHERE snapshot=%s
                AND relation='CONTAINS' AND target=ANY(%s) ORDER BY id""",
                (self.snapshot, frontier),
            ).fetchall()
            next_ids = {e["source"] for e in edges} - ancestors
            trace.extend(
                {"edge": e["id"], "relation": e["relation"], "from": e["source"], "to": e["target"]}
                for e in edges
            )
            ancestors |= next_ids
            frontier = sorted(next_ids)
            if not frontier:
                break
        ancestors |= {"tt31:SXVI-S-XVI"}
        ancestors |= {"tt31:SXVI-CH-" + r["chapter"] for r in candidates[:3] if r.get("chapter")}
        visited = set(ancestors)
        frontier = sorted(ancestors)
        required = set()
        for _ in range(hops):
            edges = self.conn.execute(
                """SELECT * FROM rag.graph_edges WHERE snapshot=%s AND
                ((source=ANY(%s) AND relation=ANY(%s)) OR
                 (target=ANY(%s) AND relation=ANY(%s))) ORDER BY relation,id""",
                (
                    self.snapshot,
                    frontier,
                    ["CONSTRAINED_BY", "NORMALIZED_REFERENCE_TO", "REFERENCES_CODE"],
                    frontier,
                    ["APPLIES_WITHIN", "CONTEXT_WITHIN", "ANNOTATES", "ANNOTATES_SCOPE"],
                ),
            ).fetchall()
            next_ids = set()
            for edge in edges:
                target = edge["target"] if edge["source"] in frontier else edge["source"]
                trace.append(
                    {
                        "edge": edge["id"],
                        "relation": edge["relation"],
                        "from": edge["source"],
                        "to": edge["target"],
                    }
                )
                if edge["relation"] in ("CONSTRAINED_BY", "NORMALIZED_REFERENCE_TO"):
                    required.add(target)
                if target not in visited:
                    next_ids.add(target)
            visited |= next_ids
            frontier = sorted(next_ids)
            if not frontier:
                break
        records = self.conn.execute(
            """SELECT c.* FROM rag.chunks c
            WHERE snapshot=%s AND id=ANY(%s) AND role='evidence' ORDER BY id""",
            (self.snapshot, sorted(visited)),
        ).fetchall()
        relevance = {}
        if query_vector is not None:
            scored = self.conn.execute(
                """SELECT chunk_id,1-(embedding <=> %s) AS score
                FROM rag.embeddings WHERE snapshot=%s AND profile=%s AND chunk_id=ANY(%s)""",
                (query_vector, self.snapshot, self.profile, [r["id"] for r in records]),
            ).fetchall()
            relevance = {r["chunk_id"]: float(r["score"]) for r in scored}
        records.sort(key=lambda r: (r["id"] not in required, -relevance.get(r["id"], 0), r["id"]))
        evidence_ids = {r["id"] for r in records}
        required &= evidence_ids
        selected: list[dict] = []
        omitted = []
        used = 0
        for row in records:
            length = len(row["source_text"])
            if len(selected) < limit and used + length <= max_chars:
                selected.append(
                    {
                        **row,
                        "required_by_graph": row["id"] in required,
                        "query_similarity": relevance.get(row["id"]),
                    }
                )
                used += length
            else:
                omitted.append(row["id"])
        chosen = {r["id"] for r in selected}
        return {
            "records": selected,
            "trace": trace,
            "omitted_ids": omitted,
            "required_ids": sorted(required),
            "missing_required_ids": sorted(required - chosen),
            "character_budget": max_chars,
            "characters_used": used,
            "coverage_status": "BUDGET_LIMITED" if omitted else "EXPANSION_COMPLETE",
        }

    def search(
        self,
        query: str,
        intent: str = "product",
        mode: str | None = None,
        top_k: int | None = None,
        expand: bool = True,
        as_of: date | None = None,
        chapters: list[str] | None = None,
        weights: dict | None = None,
        use_cache: bool = True,
    ) -> dict:
        mode = mode or self.default_mode
        if not query.strip():
            raise ValueError("Query is empty")
        if mode not in ("fts", "dense", "hybrid", "sparse", "dense_sparse", "hybrid_sparse"):
            raise ValueError("Unknown retrieval mode")
        started = time.perf_counter()
        timings = {}
        branches = {}
        n = top_k or self.cfg["top_k"]
        if n < 1:
            raise ValueError("top_k must be positive")
        pool = max(n, self.cfg["candidate_pool"])
        output: dict = {}
        if mode != "fts":
            if not self.embedder:
                raise ValueError("Dense/sparse retrieval requires a BGE-M3 embedder")
            tick = time.perf_counter()
            output = self.embedder.encode([query], use_cache=use_cache)
            timings["embedding_ms"] = (time.perf_counter() - tick) * 1000
            timings["query_cache_hit"] = output["cache_hit"]
        if mode in ("fts", "hybrid", "hybrid_sparse"):
            tick = time.perf_counter()
            branches["fts"] = self.lexical(query, intent, pool, as_of, chapters)
            timings["fts_ms"] = (time.perf_counter() - tick) * 1000
        if mode in ("dense", "hybrid", "dense_sparse", "hybrid_sparse"):
            tick = time.perf_counter()
            branches["dense"] = self.dense(output["dense"][0], intent, pool, as_of, chapters)
            timings["dense_ms"] = (time.perf_counter() - tick) * 1000
        if mode in ("sparse", "dense_sparse", "hybrid_sparse"):
            if not output["sparse"]:
                raise ValueError("Active profile has no sparse embeddings")
            tick = time.perf_counter()
            branches["sparse"] = self.sparse(output["sparse"][0], intent, pool, as_of, chapters)
            timings["sparse_ms"] = (time.perf_counter() - tick) * 1000
        ranked = fuse(branches, self.cfg["rrf_k"], weights or self.weights)
        results = unique_codes(ranked, n) if intent == "product" else ranked[:n]
        tick = time.perf_counter()
        evidence = (
            self.evidence(
                results,
                self.cfg["evidence_limit"],
                self.cfg["evidence_hops"],
                query_vector=output["dense"][0] if output else None,
            )
            if expand and intent == "product"
            else {"records": [], "trace": [], "omitted_ids": []}
        )
        timings["expansion_ms"] = (time.perf_counter() - tick) * 1000
        timings["total_ms"] = (time.perf_counter() - started) * 1000
        return {
            "query": query,
            "intent": intent,
            "mode": mode,
            "snapshot": self.snapshot,
            "profile": self.profile,
            "fusion_weights": weights or self.weights,
            "candidates" if intent == "product" else "matches": results,
            "evidence": evidence,
            "timings": timings,
            "validity": "DATE_FILTERED_LOCAL_METADATA" if as_of else "NOT_LEGALLY_VERIFIED",
            "scope": "CORPUS_84_85" if intent == "product" else "LEGAL_CORPUS",
        }

    def lookup(self, value: str) -> dict:
        if not re.fullmatch(r"[\d.]+", value):
            raise ValueError("Lookup accepts a code, not a product description")
        records = self.exact(value)
        return {
            "code": normalize_code(value),
            "matches": records,
            "evidence": self.evidence(records),
            "snapshot": self.snapshot,
            "status": "FOUND" if records else "CODE_NOT_IN_CORPUS",
        }

    def route(self, query: str) -> dict:
        text = query.lower().strip()
        if not text:
            raise ValueError("Query is empty")
        if re.fullmatch(r"[\d.]+", text):
            try:
                code = normalize_code(text)
            except ValueError:
                return {
                    "intent": "lookup",
                    "status": "INVALID_CODE",
                    "reason": "INVALID_CODE_PATTERN",
                }
            return {
                "intent": "lookup",
                "status": "IN_SCOPE" if code[:2] in ("84", "85") else "OUT_OF_SCOPE",
                "code": code,
                "reason": "EXPLICIT_CODE_PREFIX",
            }
        if re.search(r"\bgir\b|quy tắc|qui tắc", text):
            return {"intent": "gir", "status": "LEGAL_QUERY", "reason": "RULE_INTENT"}
        if re.search(
            r"hồ sơ|mẫu số|biên bản|niêm phong|lưu mẫu|thông tư|điều \d|trả lại mẫu|phân tích hàng",
            text,
        ):
            return {"intent": "tt85", "status": "LEGAL_QUERY", "reason": "PROCEDURE_INTENT"}
        # Strong product cues only; machinery using these materials remains uncertain/in-scope.
        if not re.search(r"máy|thiết bị|bộ điều khiển", text) and re.search(
            r"thịt bò|gạo|áo thun|quần áo|cam tươi|lốp xe|vàng miếng", text
        ):
            return {
                "intent": "product",
                "status": "OUT_OF_SCOPE",
                "reason": "STRONG_OTHER_CHAPTER_CUE",
            }
        if text in {
            "thiết bị điện tử",
            "linh kiện điện tử",
            "bộ chuyển đổi",
            "pin",
            "màn hình",
            "thiết bị mạng",
        }:
            return {
                "intent": "product",
                "status": "NEED_MORE_INFORMATION",
                "reason": "BROAD_PRODUCT_ONLY",
            }
        return {"intent": "product", "status": "UNCERTAIN", "reason": "SEARCH_BOTH_84_85"}

    def routed_search(self, query: str, mode: str | None = None) -> dict:
        routing = self.route(query)
        if routing["status"] in ("OUT_OF_SCOPE", "INVALID_CODE"):
            return {"routing": routing, "candidates": [], "evidence": {"records": []}}
        if routing["intent"] == "lookup":
            return {"routing": routing, **self.lookup(routing["code"])}
        result = self.search(query, intent=routing["intent"], mode=mode)
        return {"routing": routing, **result}
