"""Parameterized hybrid retrieval with separate tariff and evidence results."""

import re
import time
import unicodedata
from datetime import date
from typing import Any

import psycopg
from pgvector.psycopg import register_vector
from psycopg import sql as pgsql

from rag.data import ROOT, config, normalize_code, read
from rag.embedding import CrossEncoder, Embedder, colbert_scores


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
            entry["rrf_score"] += (weights.get(branch, 0.0) if weights is not None else 1.0) / (
                rrf_k + rank
            )
            entry["branches"][branch] = {"rank": rank, "score": float(row["score"])}
    return sorted(by_id.values(), key=lambda x: (-x["rrf_score"], x["id"]))


def code_mention_plan(query: str) -> dict:
    """Mask uncertain code mentions only for Exact; keep the semantic query intact."""
    pattern = r"(?<![\w.])(?:\d{4}\.\d{2}(?:\.\d{2})?|\d{2}\.\d{2}|\d{8}|\d{6}|\d{4})(?![\w.])"
    mentions = []
    masked = list(query)
    for match in re.finditer(pattern, query):
        before = query[max(0, match.start() - 110) : match.start()].lower()
        after = query[match.end() : match.end() + 40].lower()
        short_before = before[-55:]
        negated = bool(
            re.search(
                r"(?:không|khong|not)\s+(?:thuộc|thuoc|ở|o|vào|vao|phân loại(?: tại| vào)?|phan loai(?: tai| vao)?|in|under)\s+(?:(?:nhóm|nhom|mã|ma|heading)\s+)?$",
                short_before,
            )
        )
        disputed = bool(
            re.search(r"(?:có|co|phải|phai|thuộc|thuoc|được|duoc)", before)
            and re.search(r"^\s*[\"”’']?\s*(?:không|khong)(?:\b|[?,])", after)
        )
        status = "NEGATED" if negated else "QUESTIONED" if disputed else "MENTIONED"
        if status in ("NEGATED", "QUESTIONED"):
            masked[match.start() : match.end()] = " " * (match.end() - match.start())
        mentions.append({"code": normalize_code(match[0]), "surface": match[0], "status": status})
    return {
        "semantic_query": query,
        "exact_query": "".join(masked),
        "code_mentions": mentions,
        "exclusion_status": "NO_LEGAL_EXCLUSION_DECISION",
    }


def qa_candidate_pool(
    direct: list[dict], parents: list[dict], notes: list[dict], limit: int,
    direct_fraction: float = 0.7,
) -> list[dict]:
    """Reserve room for cited graph neighbors before scoring a fixed rerank pool."""
    if limit < 1 or not 0 < direct_fraction <= 1:
        raise ValueError("Invalid QA candidate-pool budget")
    direct_quota = max(1, min(limit, int(limit * direct_fraction)))
    selected = list(direct[:direct_quota])
    seen = {row["id"] for row in selected}
    neighbors = []
    for index in range(max(len(parents), len(notes))):
        for group in (parents, notes):
            if index >= len(group):
                continue
            row = group[index]
            if row["id"] not in seen and row.get("source_text") and row.get("locator"):
                neighbors.append({**row, "score": row.get("score", 0.0)})
                seen.add(row["id"])
    selected.extend(neighbors[: limit - len(selected)])
    seen = {row["id"] for row in selected}
    selected.extend(row for row in direct if row["id"] not in seen and len(selected) < limit)
    return selected


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


def candidate_paths(
    leaf_branches: dict[str, list[dict]],
    sections: list[dict],
    section_policies: dict[str, dict],
    params: dict,
) -> dict:
    """Keep direct candidates while following ancestor prefixes supported by tariff leaves."""
    beam = params.get("beam_size", 10)
    pool = params.get("candidate_pool", 100)
    section_rankings = {}
    traces = []
    hierarchy_rankings = {}
    for section in sections:
        key = section["section"]
        policy = section_policies[key]
        ranked = unique_codes(
            fuse(
                {b: rows[:pool] for b, rows in leaf_branches.items() if b in policy["weights"]},
                policy["k"],
                policy["weights"],
            ),
            1000,
        )
        ranked = [r for r in ranked if r.get("section") == key and r.get("level") == 8]
        section_rankings[key] = ranked
        stages = {}
        descendants = ranked
        for length, name in ((2, "chapter"), (4, "heading"), (6, "hs6")):
            parents = list(dict.fromkeys(r["code"][:length] for r in descendants))[:beam]
            stages[name] = parents
            descendants = [r for r in descendants if r["code"][:length] in parents]
        stages["ahtn8"] = [r["code"] for r in descendants[:30]]
        traces.append(
            {
                "section": key,
                "stages": stages,
                "parent_scoring": "DESCENDANT_RANK_SUPPORT; not synthetic legal text",
            }
        )
        hierarchy_rankings[key] = descendants
    section_weights = {
        s["section"]: (s["score"] if params.get("section_mix", "router") == "router" else 1.0)
        for s in sections
    }
    total = sum(section_weights.values())
    section_weights = {k: v / total for k, v in section_weights.items()} if total else {}
    k = params.get("k", 20)
    direct = unique_codes(fuse(section_rankings, k, section_weights), 100)
    hierarchy = unique_codes(fuse(hierarchy_rankings, k, section_weights), 100)
    strategy = params.get("strategy", "dual")
    if strategy == "direct":
        candidates = direct
    elif strategy == "hierarchy":
        candidates = hierarchy
    else:
        ratio = params.get("direct_weight", 0.5)
        candidates = unique_codes(
            fuse(
                {"direct": direct, "hierarchy": hierarchy},
                k,
                {"direct": ratio, "hierarchy": 1 - ratio},
            ),
            100,
        )
    return {
        "candidates": candidates,
        "direct_candidates": direct,
        "hierarchy_candidates": hierarchy,
        "hierarchy": traces,
    }


def definition_passages(records: list[dict], nodes: list[dict], edges: list[dict]) -> dict:
    """Derive cited search views through positive graph edges, never through exclusions."""
    by_id = {r["id"]: r for r in records}
    metadata = {n["id"]: n.get("metadata", {}) for n in nodes}
    children: dict[str, set[str]] = {}
    references: dict[str, set[str]] = {}
    for edge in edges:
        if edge["relation"] == "CONTAINS":
            children.setdefault(edge["source"], set()).add(edge["target"])
        elif edge["relation"] == "REFERS_TO":
            references.setdefault(edge["source"], set()).add(edge["target"])

    def excerpts(note_id):
        note = by_id[note_id]
        result = [
            {
                "id": note_id,
                "text": " ".join(note["source_text"].split()),
                "locator": note["locator"],
            }
        ]
        for reference in sorted(references.get(note_id, set())):
            info = metadata.get(reference, {})
            parent = note_id.split(":", 1)[0] + ":" + str(info.get("parent_note_id", ""))
            label = re.search(r"\(([a-z])\)", info.get("label", ""))
            if parent not in by_id or not label:
                continue
            # A placeholder resolves to an exact excerpt of its source parent, not invented text.
            text = " ".join(by_id[parent]["source_text"].split())
            part = re.search(r"\(" + label[1] + r"\)(.*?)(?=\([a-z]\)|$)", text)
            if part:
                result.append(
                    {
                        "id": parent,
                        "fragment_id": reference,
                        "text": part[0].strip(),
                        "locator": by_id[parent]["locator"],
                    }
                )
        return result

    views: dict[str, dict] = {}
    for edge in edges:
        if edge["relation"] not in ("DEFINES_FOR", "DEFINITION_APPLIES_TO", "INCLUDES_IN_SCOPE"):
            continue
        note = by_id.get(edge["source"])
        if (
            not note
            or note.get("namespace") != "hs_classification"
            or note.get("role") != "evidence"
        ):
            continue
        # A target outside the ingested graph has no fabricated descendants.
        frontier, visited = [edge["target"]], set()
        while frontier:
            node_id = frontier.pop()
            if node_id in visited:
                continue
            visited.add(node_id)
            row = by_id.get(node_id)
            if row and row.get("chunk_type") == "tariff_entry" and row.get("level") == 8:
                view = views.setdefault(node_id, {"record": row, "citations": {}, "paths": []})
                for excerpt in excerpts(edge["source"]):
                    view["citations"][excerpt.get("fragment_id", excerpt["id"])] = excerpt
                path = {
                    "note_id": edge["source"],
                    "relation": edge["relation"],
                    "target_id": edge["target"],
                    "candidate_id": node_id,
                }
                if path not in view["paths"]:
                    view["paths"].append(path)
            frontier.extend(sorted(children.get(node_id, set())))
    for view in views.values():
        view["citations"] = list(view["citations"].values())
        view["text"] = (
            view["record"]["embedding_text"]
            + "\nDefinition evidence:\n"
            + "\n".join(x["text"] for x in view["citations"])
        )
    return views


def definition_fusion(
    rows: list[dict], definitions: list[dict], weight: float, k: int
) -> list[dict]:
    """Add graph-derived candidates while retaining the direct retrieval path."""
    if not 0 <= weight <= 1:
        raise ValueError("Definition weight must be in [0, 1]")
    if weight == 0 or not definitions:
        return rows
    branches = {"retrieval": rows, "definition": definitions}
    if weight == 1:
        branches = {"definition": definitions}
    return unique_codes(fuse(branches, k, {"retrieval": 1 - weight, "definition": weight}), 100)


def rerank_candidates(
    query: str,
    rows: list[dict],
    kind: str,
    embedder: Embedder,
    reranker: CrossEncoder | None = None,
    pool: int = 30,
    rank_weight: float = 1.0,
    k: int = 20,
    use_cache: bool = True,
) -> list[dict]:
    if kind == "none":
        return rows
    texts = [r.get("rerank_text", r["embedding_text"]) for r in rows[:pool]]
    if kind == "cross_encoder":
        if reranker is None:
            raise ValueError("Cross-encoder required")
        scores = reranker.score(query, texts, use_cache=use_cache)
    elif kind == "colbert":
        scores = colbert_scores(embedder, query, texts, use_cache=use_cache)
    else:
        raise ValueError("Unknown reranker")
    ordered = sorted(
        [{**r, "rerank_score": score} for r, score in zip(rows[:pool], scores, strict=True)],
        key=lambda r: (-r["rerank_score"], r["id"]),
    )
    if rank_weight == 1:
        return ordered
    return unique_codes(
        fuse(
            {"retrieval": rows[:pool], "rerank": ordered},
            k,
            {"retrieval": 1 - rank_weight, "rerank": rank_weight},
        ),
        pool,
    )


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
                self.default_mode = selection.get("selected_mode", "full_hybrid")
                self.router_policy = selection.get("router", {})
                self.legal_policy = selection.get("legal", {})
                self.qa_policy = selection.get("qa", {})
                self.pipeline_policies = selection.get("pipeline_policies", {})
                self.definition_policies = selection.get("definition_policies", {})
                self.weights = selection.get(
                    "weights", self.router_policy.get("weights", self.weights)
                )
                modes = {
                    "C1": "dense",
                    "C2": "sparse",
                    "C3": "bm25",
                    "C4": "fts",
                    "C5": "dense_sparse",
                    "C6": "dense_bm25",
                    "C7": "hybrid_sparse",
                    "C8": "dense_sparse_exact",
                    "C9": "dense_bm25_exact",
                    "C10": "full_hybrid",
                    "C11": "full_hybrid",
                    "C12": "dense_sparse",
                    "C13": "full_hybrid",
                    "C14": "full_hybrid",
                    "C15": "full_hybrid",
                }
                self.section_policies = {
                    section: {**policy, "mode": modes[policy["configuration"]]}
                    for section, policy in selection.get("section_policies", {}).items()
                }
        if embedder and embedder.profile_id != self.profile:
            raise ValueError("Query embedding profile differs from active database profile")

    def _filter(
        self,
        intent: str,
        as_of: date | None,
        chapters: list[str] | None,
        namespace: str | None = None,
        chunk_types: list[str] | None = None,
        sections: list[str] | None = None,
        levels: list[int] | None = None,
        headings: list[str] | None = None,
        hs6: list[str] | None = None,
        roles: list[str] | None = None,
        legal_status: list[str] | None = None,
    ) -> tuple[str, list]:
        clause = "c.snapshot=%s"
        params: list[Any] = [self.snapshot]
        if intent == "product":
            namespace = namespace or "hs_classification"
            chunk_types = chunk_types if chunk_types is not None else ["tariff_entry"]
        elif intent == "scope":
            roles = roles if roles is not None else ["scope"]
        elif intent in ("gir", "tt85"):
            clause += " AND c.dataset=%s"
            params.append(intent)
            namespace = namespace or (
                "legal_classification" if intent == "tt85" else "hs_classification"
            )
        elif intent == "legal":
            chunk_types = (
                chunk_types
                if chunk_types is not None
                else [
                    "gir_rule",
                    "gir_explanation",
                    "section_note",
                    "chapter_note",
                    "subheading_note",
                    "legal_clause",
                ]
            )
        elif intent != "knowledge":
            raise ValueError("Unknown intent")
        if namespace:
            if namespace not in ("hs_classification", "legal_classification"):
                raise ValueError("Unknown namespace")
            clause += " AND c.namespace=%s"
            params.append(namespace)
        for column, values in [
            ("chapter", chapters),
            ("chunk_type", chunk_types),
            ("section", sections),
            ("level", levels),
            ("heading", headings),
            ("hs6", hs6),
            ("role", roles),
            ("legal_status", legal_status),
        ]:
            if values is not None:
                clause += f" AND c.{column}=ANY(%s)"
                params.append(values)
        if as_of:
            clause += " AND c.effective_from IS NOT NULL AND c.effective_from<=%s AND (c.effective_to IS NULL OR c.effective_to>%s)"
            params.extend([as_of, as_of])
        return clause, params

    def lexical(
        self,
        query: str,
        intent: str = "product",
        limit: int = 50,
        as_of: date | None = None,
        chapters: list[str] | None = None,
        **filters: Any,
    ) -> list[dict]:
        clause, params = self._filter(intent, as_of, chapters, **filters)
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
        **filters: Any,
    ) -> list[dict]:
        clause, params = self._filter(intent, as_of, chapters, **filters)
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
        **filters: Any,
    ) -> list[dict]:
        if not weights:
            return []
        clause, params = self._filter(intent, as_of, chapters, **filters)
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

    @staticmethod
    def tokens(text: str) -> list[str]:
        text = unicodedata.normalize("NFKD", text.lower()).replace("đ", "d")
        text = "".join(c for c in text if not unicodedata.combining(c))
        return re.findall(r"[a-z0-9]+(?:[-.][a-z0-9]+)*", text)

    def documents(
        self,
        intent: str = "product",
        as_of: date | None = None,
        chapters: list[str] | None = None,
        **filters: Any,
    ) -> list[dict]:
        clause, params = self._filter(intent, as_of, chapters, **filters)
        sql = pgsql.SQL("SELECT c.* FROM rag.chunks c WHERE {where} ORDER BY c.id").format(
            where=pgsql.SQL(clause)
        )
        key = str((clause, params))
        if not hasattr(self, "_document_cache"):
            self._document_cache: dict[str, list] = {}
        if key not in self._document_cache:
            self._document_cache[key] = self.conn.execute(sql, params).fetchall()
        return self._document_cache[key]

    def bm25(
        self,
        query: str,
        intent: str = "product",
        limit: int = 50,
        as_of: date | None = None,
        chapters: list[str] | None = None,
        **filters: Any,
    ) -> list[dict]:
        from rank_bm25 import BM25Okapi

        # Official BM25Okapi implementation; preprocessing is shared with query tokens.
        if not hasattr(self, "_bm25_index"):
            all_rows = self.documents("knowledge")
            corpus = [self.tokens(r["embedding_text"]) for r in all_rows]
            self._bm25_index = BM25Okapi(corpus, k1=1.2, b=0.75, epsilon=0.25)
            self._bm25_positions = {r["id"]: i for i, r in enumerate(all_rows)}
        scores = self._bm25_index.get_scores(self.tokens(query))
        result = [
            {**r, "score": float(scores[self._bm25_positions[r["id"]]])}
            for r in self.documents(intent, as_of, chapters, **filters)
            if scores[self._bm25_positions[r["id"]]] > 0
        ]
        return sorted(result, key=lambda r: (-r["score"], r["id"]))[:limit]

    def definition_views(self) -> dict:
        if not hasattr(self, "_definition_views"):
            records = self.documents("knowledge", namespace="hs_classification")
            nodes = self.conn.execute(
                "SELECT * FROM rag.graph_nodes WHERE snapshot=%s", (self.snapshot,)
            ).fetchall()
            edges = self.conn.execute(
                "SELECT * FROM rag.graph_edges WHERE snapshot=%s ORDER BY id", (self.snapshot,)
            ).fetchall()
            self._definition_views = definition_passages(records, nodes, edges)
        return self._definition_views

    def definition_candidates(self, query: str, limit: int = 100, sections=None) -> list[dict]:
        from rank_bm25 import BM25Okapi

        views = self.definition_views()
        if not views:
            return []
        if not hasattr(self, "_definition_index"):
            self._definition_ids = sorted(views)
            self._definition_index = BM25Okapi(
                [self.tokens(views[key]["text"]) for key in self._definition_ids],
                k1=1.2,
                b=0.75,
                epsilon=0.25,
            )
        scores = self._definition_index.get_scores(self.tokens(query))
        rows = []
        for key, score in zip(self._definition_ids, scores, strict=True):
            view = views[key]
            row = view["record"]
            if score <= 0 or (sections is not None and row["section"] not in sections):
                continue
            rows.append(
                {
                    **row,
                    "score": float(score),
                    "definition_paths": view["paths"],
                    "definition_citations": view["citations"],
                }
            )
        return sorted(rows, key=lambda r: (-r["score"], r["id"]))[:limit]

    def definition_context(self, rows: list[dict]) -> list[dict]:
        views = self.definition_views()
        return [
            {
                **r,
                "rerank_text": views[r["id"]]["text"],
                "definition_paths": views[r["id"]]["paths"],
                "definition_citations": views[r["id"]]["citations"],
            }
            if r["id"] in views
            else r
            for r in rows
        ]

    @classmethod
    def exact_features(cls, text: str) -> set[str]:
        normalized = " ".join(cls.tokens(text))
        features = set()
        for value in re.findall(
            r"\b(?:\d{4}\.\d{2}(?:\.\d{2})?|\d{2}\.\d{2}|\d{4}|\d{6}|\d{8})\b", normalized
        ):
            features.add(value.replace(".", ""))
        for value in re.findall(
            r"(?<!\w)\d+(?:\.\d+)?\s*(?:kw|w|v|mah|ah|kg|cc|cm3|ghz|mhz|gb|tb|carat|karat|%)(?!\w)",
            normalized,
        ):
            features.add(re.sub(r"\s+", "", value))
        features.update(re.findall(r"\b(?:usb-c|li-ion|\d+g|802\.11[a-z]+)\b", normalized))
        # Three-digit purity hallmarks are features, never automatic material classifications.
        for match in re.finditer(
            r"\b(?:bac|vang|fineness|ham luong|do tinh khiet)\s+(\d{3})\b", normalized
        ):
            features.add("fineness:" + match.group(1))
        # Token normalization omits punctuation %, so obtain percentage values from raw text.
        features.update(
            re.sub(r"\s+", "", x.lower()).replace(",", ".")
            for x in re.findall(r"\d+(?:[.,]\d+)?\s*%", text)
        )
        return features

    def exact_match(
        self,
        query: str,
        intent: str = "product",
        limit: int = 50,
        as_of: date | None = None,
        chapters: list[str] | None = None,
        **filters: Any,
    ) -> list[dict]:
        wanted = self.exact_features(query)
        if not wanted:
            return []
        result = []
        for r in self.documents(intent, as_of, chapters, **filters):
            features = self.exact_features(r["embedding_text"])
            if r.get("code"):
                features.add(r["code"])
            hits = wanted & features
            if hits:
                result.append({**r, "score": len(hits) / len(wanted), "exact_hits": sorted(hits)})
        return sorted(result, key=lambda r: (-r["score"], r["id"]))[:limit]

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
        for _ in range(8):
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
                    [
                        "CONSTRAINED_BY",
                        "NORMALIZED_REFERENCE_TO",
                        "REFERENCES_CODE",
                        "GOVERNED_BY",
                        "DEFINED_BY",
                        "RESOLVES_TO",
                    ],
                    frontier,
                    [
                        "APPLIES_WITHIN",
                        "CONTEXT_WITHIN",
                        "ANNOTATES",
                        "ANNOTATES_SCOPE",
                        "GOVERNS",
                        "APPLIES_TO",
                        "DEFINITION_APPLIES_TO",
                    ],
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
                if edge["relation"] in ("CONSTRAINED_BY", "NORMALIZED_REFERENCE_TO", "GOVERNED_BY"):
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
        rrf_k: int | None = None,
        exact_query: str | None = None,
        **filters: Any,
    ) -> dict:
        if (
            intent in ("gir", "tt85", "legal")
            and weights is None
            and getattr(self, "legal_policy", None)
        ):
            weights = self.legal_policy["weights"]
            rrf_k = rrf_k or self.legal_policy["k"]
            mode = mode or "full_hybrid"
        mode = mode or self.default_mode
        if not query.strip():
            raise ValueError("Query is empty")
        if mode not in (
            "fts",
            "dense",
            "hybrid",
            "sparse",
            "dense_sparse",
            "hybrid_sparse",
            "bm25",
            "dense_bm25",
            "dense_sparse_exact",
            "dense_bm25_exact",
            "full_hybrid",
        ):
            raise ValueError("Unknown retrieval mode")
        started = time.perf_counter()
        timings = {}
        branches = {}
        n = top_k or self.cfg["top_k"]
        if n < 1:
            raise ValueError("top_k must be positive")
        pool = max(n, self.cfg["candidate_pool"])
        output: dict = {}
        if mode not in ("fts", "bm25"):
            if not self.embedder:
                raise ValueError("Dense/sparse retrieval requires a BGE-M3 embedder")
            tick = time.perf_counter()
            output = self.embedder.encode([query], use_cache=use_cache)
            timings["embedding_ms"] = (time.perf_counter() - tick) * 1000
            timings["query_cache_hit"] = output["cache_hit"]
        if mode in ("fts", "hybrid", "hybrid_sparse", "full_hybrid"):
            tick = time.perf_counter()
            branches["fts"] = self.lexical(query, intent, pool, as_of, chapters, **filters)
            timings["fts_ms"] = (time.perf_counter() - tick) * 1000
        if mode in (
            "dense",
            "hybrid",
            "dense_sparse",
            "hybrid_sparse",
            "dense_bm25",
            "dense_sparse_exact",
            "dense_bm25_exact",
            "full_hybrid",
        ):
            tick = time.perf_counter()
            branches["dense"] = self.dense(
                output["dense"][0], intent, pool, as_of, chapters, **filters
            )
            timings["dense_ms"] = (time.perf_counter() - tick) * 1000
        if mode in ("sparse", "dense_sparse", "hybrid_sparse", "dense_sparse_exact", "full_hybrid"):
            if not output["sparse"]:
                raise ValueError("Active profile has no sparse embeddings")
            tick = time.perf_counter()
            branches["sparse"] = self.sparse(
                output["sparse"][0], intent, pool, as_of, chapters, **filters
            )
            timings["sparse_ms"] = (time.perf_counter() - tick) * 1000
        if mode in ("bm25", "dense_bm25", "dense_bm25_exact", "full_hybrid"):
            tick = time.perf_counter()
            branches["bm25"] = self.bm25(query, intent, pool, as_of, chapters, **filters)
            timings["bm25_ms"] = (time.perf_counter() - tick) * 1000
        if mode in ("dense_sparse_exact", "dense_bm25_exact", "full_hybrid"):
            tick = time.perf_counter()
            branches["exact"] = self.exact_match(
                query if exact_query is None else exact_query,
                intent,
                pool,
                as_of,
                chapters,
                **filters,
            )
            timings["exact_ms"] = (time.perf_counter() - tick) * 1000
        ranked = fuse(branches, rrf_k or self.cfg["rrf_k"], weights or self.weights)
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
            "section_candidates": self.section_candidates(ranked) if intent == "product" else [],
            "evidence": evidence,
            "timings": timings,
            "validity": "DATE_FILTERED_LOCAL_METADATA" if as_of else "NOT_LEGALLY_VERIFIED",
            "scope": "CORPUS_XIV_XVI_XVII" if intent == "product" else "LEGAL_CORPUS",
        }

    def tariff_knowledge_channels(self, query: str, exact_query: str, top_k: int) -> dict:
        """Apply the frozen HS policies to real source records at each tariff level."""
        router = getattr(self, "router_policy", {})
        cross = self.search(
            query,
            intent="product",
            mode="full_hybrid",
            top_k=100,
            expand=False,
            weights=router.get("weights", self.weights),
            rrf_k=router.get("k", self.cfg["rrf_k"]),
            exact_query=exact_query,
        )
        sections = cross["section_candidates"]
        if not sections:
            return {"channels": {}, "sections": [], "policy_trace": []}
        key = sections[0]["section"]
        policies = getattr(self, "section_policies", {})
        params = getattr(self, "pipeline_policies", {}).get(
            key, {"strategy": "direct", "candidate_pool": 100, "section_mix": "router", "k": 20}
        )
        definition_policy = getattr(self, "definition_policies", {}).get(key)
        ranking_policy = definition_policy or params
        reranker = None
        if ranking_policy.get("reranker") == "cross_encoder":
            import torch

            if not hasattr(self, "_reranker"):
                self._reranker = CrossEncoder(
                    self.cfg["reranker_model"],
                    self.cfg["reranker_revision"],
                    device="mps" if torch.backends.mps.is_available() else "cpu",
                )
            reranker = self._reranker
        channels, traces = {}, []
        for level in (4, 6, 8):
            filters: dict[str, Any] = {"levels": [level]}
            if self.embedder is None:
                raise ValueError("Multi-level retrieval requires an embedder")
            encoded = self.embedder.encode([query])
            pool = max(100, top_k)
            branches = {
                "dense": self.dense(encoded["dense"][0], "product", pool, **filters),
                "sparse": self.sparse(encoded["sparse"][0], "product", pool, **filters),
                "bm25": self.bm25(query, "product", pool, **filters),
                "fts": self.lexical(query, "product", pool, **filters),
                "exact": self.exact_match(exact_query, "product", pool, **filters),
            }
            if level == 8 and policies:
                rows = candidate_paths(branches, sections, policies, params)["candidates"]
                if definition_policy:
                    definitions = self.definition_candidates(
                        query, 100, [s["section"] for s in sections]
                    )
                    rows = definition_fusion(
                        rows,
                        definitions,
                        definition_policy["definition_weight"],
                        definition_policy["k"],
                    )
            else:
                per_section = {}
                for section in sections:
                    name = section["section"]
                    policy = policies.get(
                        name,
                        {
                            "weights": router.get("weights", self.weights),
                            "k": router.get("k", self.cfg["rrf_k"]),
                        },
                    )
                    ranked = fuse(
                        {k: v for k, v in branches.items() if k in policy["weights"]},
                        policy["k"],
                        policy["weights"],
                    )
                    per_section[name] = [r for r in ranked if r["section"] == name]
                total = sum(s["score"] for s in sections)
                section_weights = {
                    s["section"]: s["score"] / total if total else 1 / len(sections)
                    for s in sections
                }
                rows = fuse(per_section, params.get("k", 20), section_weights)
            if ranking_policy.get("evidence_rerank"):
                rows = self.definition_context(rows)
            rows = rerank_candidates(
                query,
                rows,
                ranking_policy.get("reranker", "none"),
                self.embedder,
                reranker,
                ranking_policy.get("rerank_pool", 30),
                ranking_policy.get("rank_weight", 1),
                ranking_policy.get("k", 20),
            )
            channels[f"tariff_{level}"] = rows[:top_k]
            traces.append(
                {
                    "level": level,
                    "routed_section": key,
                    "section_policies": {
                        s["section"]: policies.get(s["section"], {}) for s in sections
                    },
                    "ranking_policy": ranking_policy,
                    "transfer_status": "FROZEN_HS_POLICY_TRANSFER_NOT_QA_TRAINED",
                }
            )
        return {"channels": channels, "sections": sections, "policy_trace": traces}

    def tariff_ancestors(self, seeds: list[dict], limit: int = 30) -> dict:
        """Return actual parent documents, never fabricate evidence from a code prefix."""
        visited = {r["id"] for r in seeds}
        frontier = sorted(visited)
        parent_ids = set()
        trace: list[dict] = []
        for _ in range(8):
            if not frontier:
                break
            edges = self.conn.execute(
                """SELECT * FROM rag.graph_edges WHERE snapshot=%s
                AND relation='CONTAINS' AND target=ANY(%s) ORDER BY id""",
                (self.snapshot, frontier),
            ).fetchall()
            next_ids = {e["source"] for e in edges} - visited
            trace.extend(
                {"edge": e["id"], "relation": e["relation"], "from": e["source"], "to": e["target"]}
                for e in edges
            )
            parent_ids |= next_ids
            visited |= next_ids
            frontier = sorted(next_ids)
        records = self.conn.execute(
            """SELECT c.* FROM rag.chunks c WHERE snapshot=%s
            AND id=ANY(%s) AND chunk_type='tariff_entry' ORDER BY level,id LIMIT %s""",
            (self.snapshot, sorted(parent_ids), limit),
        ).fetchall()
        return {"records": records, "trace": trace}

    def rule_family_evidence(self, query: str, matches: list[dict]) -> list[dict]:
        """Expand retrieved atomic GIR families when the query requests a sequence."""
        if not re.search(
            r"trình tự|trinh tu|thứ tự|thu tu|các quy tắc|cac quy tac|sequence", query.lower()
        ):
            return []
        families = set()
        for row in matches[:3]:
            match = re.fullmatch(
                r"GIR_(\d)[A-Z]?", row.get("source_id") or row["id"].split(":", 1)[-1]
            )
            if match:
                families.add(match[1])
        rules = self.documents("gir", chunk_types=["gir_rule"])
        return [
            {**r, "expansion_reason": "RETRIEVED_GIR_FAMILY_SEQUENCE"}
            for r in rules
            if (
                m := re.fullmatch(
                    r"GIR_(\d)[A-Z]?", r.get("source_id") or r["id"].split(":", 1)[-1]
                )
            )
            and m[1] in families
        ][:10]

    def referenced_note_scope(self, plan: dict) -> list[dict]:
        """Keep Notes of a questioned code available without boosting its tariff candidate."""
        scopes = {}
        for mention in plan["code_mentions"]:
            if mention["status"] not in ("QUESTIONED", "NEGATED"):
                continue
            for record in self.exact(mention["code"]):
                if record.get("section") in ("XIV", "XVI", "XVII"):
                    scopes[(mention["code"], record["section"])] = {
                        "code": mention["code"],
                        "status": mention["status"],
                        "section": record["section"],
                        "source_record": record["id"],
                        "purpose": "NOTES_FOR_REFERENCE_VALIDATION_NOT_CANDIDATE_BOOST",
                    }
        return list(scopes.values())

    def legacy_knowledge_search(self, query: str, top_k: int) -> dict:
        """Retain the original fixed-channel baseline for reproducible notebook comparisons."""
        started = time.perf_counter()
        router = getattr(self, "router_policy", {})
        channels = {}
        for level in (4, 6, 8):
            channels[f"tariff_{level}"] = self.search(
                query,
                intent="knowledge",
                mode="full_hybrid",
                top_k=top_k,
                expand=False,
                chunk_types=["tariff_entry"],
                levels=[level],
                weights=router.get("weights", self.weights),
                rrf_k=router.get("k", self.cfg["rrf_k"]),
            )["matches"]
        channels["legal"] = self.search(query, intent="legal", top_k=top_k, expand=False)["matches"]
        routing = self.route(query, sequence_rules=False)
        legal_weight = 0.75 if routing["intent"] in ("gir", "tt85", "legal") else 0.25
        weights = {f"tariff_{level}": (1 - legal_weight) / 3 for level in (4, 6, 8)}
        weights["legal"] = legal_weight
        ranked = fuse(channels, 60, weights)
        evidence = self.evidence(ranked[:3], limit=30, hops=self.cfg["evidence_hops"])
        package = {r["id"]: r for rows in channels.values() for r in rows}
        package.update({r["id"]: r for r in evidence["records"]})
        return {
            "query": query,
            "snapshot": self.snapshot,
            "profile": self.profile,
            "matches": ranked[:top_k],
            "channels": channels,
            "channel_weights": weights,
            "channel_rrf_k": 60,
            "evidence": evidence,
            "package": list(package.values()),
            "routing": routing,
            "elapsed_ms": (time.perf_counter() - started) * 1000,
            "policy_status": "LEGACY_FIXED_MULTILEVEL_BASELINE",
            "validation_status": "RETRIEVAL_ONLY_REQUIRES_LEGAL_REASONING",
        }

    def qa_search(
        self, query: str, top_k: int = 10, policy_override: dict | None = None,
        include_package: bool = True,
    ) -> dict:
        """Explicit evidence-QA task: source chunks at all levels, no gold labels."""
        from rag.evaluation import QA_CHUNK_TYPES

        if top_k < 1:
            raise ValueError("top_k must be positive")
        policy = policy_override or getattr(self, "qa_policy", None)
        if not policy:
            raise ValueError("QA policy has not been selected on the supplied train partition")
        started = time.perf_counter()
        plan = code_mention_plan(query)
        pool = policy["pool"]
        encoded = self.embedder.encode([query]) if self.embedder else None
        if encoded is None:
            raise ValueError("QA retrieval requires an embedder")
        assert self.embedder is not None
        filters: dict[str, Any] = {"chunk_types": QA_CHUNK_TYPES}
        functions = {
            "dense": lambda: self.dense(encoded["dense"][0], "knowledge", pool, **filters),
            "sparse": lambda: self.sparse(encoded["sparse"][0], "knowledge", pool, **filters),
            "bm25": lambda: self.bm25(query, "knowledge", pool, **filters),
            "fts": lambda: self.lexical(query, "knowledge", pool, **filters),
            "exact": lambda: self.exact_match(plan["exact_query"], "knowledge", pool, **filters),
        }
        branches = {name: functions[name]() for name in policy["weights"]}
        ranked = fuse(branches, policy["k"], policy["weights"])
        neutral_query = " ".join(plan["exact_query"].split())
        query_split_used = False
        split_weight = policy.get("query_split_weight", 0.0)
        if split_weight and neutral_query != " ".join(query.split()):
            if not 0 < split_weight < 1:
                raise ValueError("QA query split weight must be between 0 and 1")
            neutral_encoded = self.embedder.encode([neutral_query])
            neutral_filters: dict[str, Any] = {"chunk_types": ["tariff_entry"]}
            neutral_functions = {
                "dense": lambda: self.dense(
                    neutral_encoded["dense"][0], "knowledge", pool, **neutral_filters
                ),
                "sparse": lambda: self.sparse(
                    neutral_encoded["sparse"][0], "knowledge", pool, **neutral_filters
                ),
                "bm25": lambda: self.bm25(neutral_query, "knowledge", pool, **neutral_filters),
                "fts": lambda: self.lexical(neutral_query, "knowledge", pool, **neutral_filters),
                "exact": lambda: self.exact_match(
                    neutral_query, "knowledge", pool, **neutral_filters
                ),
            }
            neutral_branches = {name: neutral_functions[name]() for name in policy["weights"]}
            neutral_ranked = fuse(neutral_branches, policy["k"], policy["weights"])
            ranked = fuse(
                {"original": ranked, "code_neutral": neutral_ranked},
                policy["k"],
                {"original": 1 - split_weight, "code_neutral": split_weight},
            )
            query_split_used = True
        graph_candidates: dict[str, list[Any]] = {"parents": [], "notes": [], "trace": []}
        if policy.get("graph_before_rerank"):
            if policy.get("reranker") != "cross_encoder":
                raise ValueError("Graph-before-rerank requires a cross-encoder policy")
            seeds = ranked[: policy.get("graph_seed_count", 6)]
            tariff_seeds = [r for r in seeds if r["chunk_type"] == "tariff_entry"]
            parents = self.tariff_ancestors(tariff_seeds, limit=30) if tariff_seeds else {
                "records": [], "trace": []
            }
            graph = self.evidence(
                seeds, limit=30, hops=self.cfg["evidence_hops"],
                query_vector=encoded["dense"][0],
            )
            graph_candidates = {
                "parents": [r["id"] for r in parents["records"]],
                "notes": [r["id"] for r in graph["records"]],
                "trace": parents["trace"] + graph["trace"],
            }
            parent_rows = sorted(
                parents["records"], key=lambda row: (-int(row.get("level") or 0), row["id"])
            )
            ranked = qa_candidate_pool(
                ranked, parent_rows, graph["records"],
                policy["rerank_pool"], policy.get("direct_fraction", 0.7),
            )
        pre_rerank_ids = [r["id"] for r in ranked[: policy.get("rerank_pool", pool)]]
        if policy.get("reranker") == "cross_encoder":
            if not hasattr(self, "_reranker"):
                import torch

                self._reranker = CrossEncoder(
                    self.cfg["reranker_model"],
                    self.cfg["reranker_revision"],
                    device="mps" if torch.backends.mps.is_available() else "cpu",
                )
            ranked = rerank_evidence(
                query,
                ranked,
                self._reranker,
                policy["rerank_pool"],
                policy["rank_weight"],
                policy["k"],
            )
        matches = ranked[:top_k]
        if not include_package:
            return {
                "query": query,
                "snapshot": self.snapshot,
                "matches": matches,
                "pre_rerank_ids": pre_rerank_ids,
                "graph_candidates": graph_candidates,
                "query_split_used": query_split_used,
                "policy": policy,
                "elapsed_ms": (time.perf_counter() - started) * 1000,
                "validation_status": "RETRIEVAL_ONLY_REQUIRES_LEGAL_REASONING",
            }
        families = self.rule_family_evidence(query, matches)
        graph = self.evidence(matches[:3], limit=30, hops=self.cfg["evidence_hops"])
        tariff_seeds = [r for r in matches if r["chunk_type"] == "tariff_entry"]
        ancestors = self.tariff_ancestors(tariff_seeds, limit=30)
        reference_scopes = self.referenced_note_scope(plan)
        notes_sections = sorted(
            {r["section"] for r in tariff_seeds if r.get("section")}
            | {s["section"] for s in reference_scopes}
        )
        notes = (
            self.search(
                query,
                intent="knowledge",
                mode="full_hybrid",
                top_k=10,
                expand=False,
                chunk_types=["section_note", "chapter_note", "subheading_note"],
                sections=notes_sections,
                weights=policy["weights"],
                rrf_k=policy["k"],
                exact_query=plan["exact_query"],
            )["matches"]
            if notes_sections
            else []
        )
        package = {
            r["id"]: r for r in matches + families + graph["records"] + ancestors["records"] + notes
        }
        return {
            "query": query,
            "snapshot": self.snapshot,
            "profile": self.profile,
            "matches": matches,
            "package": list(package.values()),
            "query_plan": plan,
            "query_split_used": query_split_used,
            "pre_rerank_ids": pre_rerank_ids,
            "graph_candidates": graph_candidates,
            "routing": self.route(query),
            "policy": policy,
            "evidence": graph,
            "rule_family_evidence": families,
            "ancestors": ancestors,
            "notes": notes,
            "reference_note_scopes": reference_scopes,
            "package_budget": {
                "ranked": top_k,
                "gir_family": 10,
                "graph": 30,
                "ancestors": 30,
                "notes": 10,
            },
            "elapsed_ms": (time.perf_counter() - started) * 1000,
            "validation_status": "RETRIEVAL_ONLY_REQUIRES_LEGAL_REASONING",
        }

    def knowledge_search(self, query: str, top_k: int = 10, policy: str = "auto") -> dict:
        """Use trained QA by default; explicit legacy policies remain reproducible."""
        if top_k < 1:
            raise ValueError("top_k must be positive")
        if policy == "auto":
            policy = "trained_qa" if getattr(self, "qa_policy", None) else "hs_transfer"
        if policy == "trained_qa":
            return self.qa_search(query, top_k)
        if policy == "legacy_fixed":
            return self.legacy_knowledge_search(query, top_k)
        if policy != "hs_transfer":
            raise ValueError("Unknown knowledge retrieval policy")
        started = time.perf_counter()
        plan = code_mention_plan(query)
        routing = self.route(query)
        tariff = self.tariff_knowledge_channels(query, plan["exact_query"], top_k)
        channels = tariff["channels"]
        legal = self.search(
            query, intent="legal", top_k=top_k, expand=False, exact_query=plan["exact_query"]
        )
        rule_matches = []
        if routing["intent"] == "gir":
            rule_matches = self.search(
                query,
                intent="gir",
                top_k=top_k,
                expand=False,
                chunk_types=["gir_rule"],
                exact_query=plan["exact_query"],
            )["matches"]
            channels["legal"] = fuse(
                {"atomic_gir": rule_matches, "legal": legal["matches"]},
                60,
                {"atomic_gir": 0.5, "legal": 0.5},
            )[:top_k]
        else:
            channels["legal"] = legal["matches"]
        legal_weight = 0.75 if routing["intent"] in ("gir", "tt85", "legal") else 0.25
        channel_weights = {f"tariff_{level}": (1 - legal_weight) / 3 for level in (4, 6, 8)}
        channel_weights["legal"] = legal_weight
        ranked = fuse(channels, 60, channel_weights)
        # Expand Notes from tariff seeds rather than unrelated legal results in the fused top3.
        seeds = [rows[0] for name, rows in channels.items() if name.startswith("tariff_") and rows]
        graph = self.evidence(seeds, limit=30, hops=self.cfg["evidence_hops"])
        ancestors = self.tariff_ancestors(seeds, limit=30)
        families = self.rule_family_evidence(query, rule_matches)
        notes = []
        reference_scopes = self.referenced_note_scope(plan)
        notes_sections = sorted(
            {s["section"] for s in tariff["sections"]} | {s["section"] for s in reference_scopes}
        )
        if notes_sections:
            notes = self.search(
                query,
                intent="knowledge",
                mode="full_hybrid",
                top_k=top_k,
                expand=False,
                namespace="hs_classification",
                chunk_types=["section_note", "chapter_note", "subheading_note"],
                sections=notes_sections,
                weights=getattr(self, "legal_policy", {}).get("weights", self.weights),
                rrf_k=getattr(self, "legal_policy", {}).get("k", self.cfg["rrf_k"]),
                exact_query=plan["exact_query"],
            )["matches"]
        package = {r["id"]: r for rows in channels.values() for r in rows}
        for rows in (graph["records"], ancestors["records"], families, notes):
            package.update({r["id"]: r for r in rows})
        return {
            "query": query,
            "snapshot": self.snapshot,
            "profile": self.profile,
            "matches": ranked[:top_k],
            "channels": channels,
            "channel_weights": channel_weights,
            "channel_rrf_k": 60,
            "evidence": graph,
            "ancestors": ancestors,
            "rule_family_evidence": families,
            "notes": notes,
            "reference_note_scopes": reference_scopes,
            "notes_sections": notes_sections,
            "package": list(package.values()),
            "routing": routing,
            "query_plan": plan,
            "section_candidates": tariff["sections"],
            "policy_trace": tariff["policy_trace"],
            "elapsed_ms": (time.perf_counter() - started) * 1000,
            "policy_status": "FROZEN_HS_POLICY_TRANSFER_QA_TRAIN_PENDING",
            "package_budget": {
                "per_channel": top_k,
                "channels": 4,
                "notes": top_k,
                "graph": 30,
                "tariff_ancestors": 30,
                "gir_family": 10,
            },
            "validation_status": "RETRIEVAL_ONLY_REQUIRES_LEGAL_REASONING",
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

    def route(self, query: str, sequence_rules: bool = True) -> dict:
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
                "status": "IN_SCOPE"
                if code[:2] in ("71", "84", "85", "86", "87", "88", "89")
                else "OUT_OF_SCOPE",
                "code": code,
                "reason": "EXPLICIT_CODE_PREFIX",
            }
        if (
            sequence_rules
            and re.search(r"trình tự|trinh tu|thứ tự|thu tu|nhóm thích hợp|nhom thich hop", text)
            and re.search(
                r"hai nhóm|hai nhom|nhiều nhóm|nhieu nhom|sản phẩm hỗn hợp|san pham hon hop", text
            )
            and re.search(
                r"phân loại|phan loai|chọn nhóm|chon nhom|xác định nhóm|xac dinh nhom|nhóm thích hợp|nhom thich hop",
                text,
            )
        ):
            return {
                "intent": "gir",
                "status": "LEGAL_QUERY",
                "reason": "MULTI_HEADING_SEQUENCE_INTENT",
            }
        if re.search(r"\bgir\b|quy tắc|qui tắc", text):
            return {"intent": "gir", "status": "LEGAL_QUERY", "reason": "RULE_INTENT"}
        if "chú giải" in text or "chu giai" in text:
            return {"intent": "legal", "status": "LEGAL_QUERY", "reason": "NOTES_INTENT"}
        if re.search(
            r"hồ sơ|mẫu số|biên bản|niêm phong|lưu mẫu|thông tư|điều \d|trả lại mẫu|phân tích hàng",
            text,
        ):
            return {"intent": "tt85", "status": "LEGAL_QUERY", "reason": "PROCEDURE_INTENT"}
        # Strong product cues only; machinery using these materials remains uncertain/in-scope.
        if not re.search(r"máy|thiết bị|bộ điều khiển", text) and re.search(
            r"thịt bò|gạo|áo thun|quần áo|cam tươi|lốp xe", text
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
        return {"intent": "product", "status": "UNCERTAIN", "reason": "SOFT_CROSS_SECTION"}

    def routed_search(self, query: str, mode: str | None = None) -> dict:
        routing = self.route(query)
        if routing["status"] in ("OUT_OF_SCOPE", "INVALID_CODE"):
            return {"routing": routing, "candidates": [], "evidence": {"records": []}}
        if routing["intent"] == "lookup":
            return {"routing": routing, **self.lookup(routing["code"])}
        if routing["intent"] == "product" and mode is None:
            result = self.adaptive_search(
                query,
                weights=self.weights,
                section_policies=getattr(self, "section_policies", {}),
                rrf_k=getattr(self, "router_policy", {}).get("k", self.cfg["rrf_k"]),
            )
        elif mode is None and getattr(self, "qa_policy", None):
            result = self.qa_search(query)
        else:
            result = self.search(query, intent=routing["intent"], mode=mode)
        return {"routing": routing, **result}

    def adaptive_search(
        self,
        query: str,
        weights: dict | None = None,
        section_policies: dict | None = None,
        rrf_k: int = 20,
    ) -> dict:
        if self.embedder is None:
            raise ValueError("Adaptive retrieval requires an embedder")
        policies = section_policies or getattr(self, "section_policies", {})
        cross = self.search(
            query,
            mode="full_hybrid",
            top_k=100,
            expand=False,
            weights=weights or self.weights,
            rrf_k=rrf_k,
        )
        # Choose Sections before truncating fused candidates to top_k.
        sections = cross["section_candidates"]
        key = sections[0]["section"] if sections else ""
        params = getattr(self, "pipeline_policies", {}).get(
            key,
            {
                "strategy": "dual",
                "beam_size": 10,
                "direct_weight": 0.5,
                "section_mix": "router",
                "candidate_pool": 100,
                "reranker": "none",
            },
        )
        encoded = self.embedder.encode([query])
        pool = 100
        filters: dict[str, Any] = {"levels": [8]}
        branches = {
            "dense": self.dense(encoded["dense"][0], "product", pool, **filters),
            "sparse": self.sparse(encoded["sparse"][0], "product", pool, **filters),
            "bm25": self.bm25(query, "product", pool, **filters),
            "fts": self.lexical(query, "product", pool, **filters),
            "exact": self.exact_match(query, "product", pool, **filters),
        }
        output = candidate_paths(branches, sections, policies, params)
        definition_policy = getattr(self, "definition_policies", {}).get(key)
        ranking_params = definition_policy or params
        definition_rows = []
        candidates = output["candidates"]
        if definition_policy:
            definition_rows = self.definition_candidates(
                query, 100, [s["section"] for s in sections]
            )
            candidates = definition_fusion(
                candidates,
                definition_rows,
                definition_policy["definition_weight"],
                definition_policy["k"],
            )
            if definition_policy.get("evidence_rerank"):
                candidates = self.definition_context(candidates)
        reranker = None
        if ranking_params.get("reranker") == "cross_encoder":
            import torch

            if not hasattr(self, "_reranker"):
                self._reranker = CrossEncoder(
                    self.cfg["reranker_model"],
                    self.cfg["reranker_revision"],
                    device="mps" if torch.backends.mps.is_available() else "cpu",
                )
            reranker = self._reranker
        ranked = rerank_candidates(
            query,
            candidates,
            ranking_params.get("reranker", "none"),
            self.embedder,
            reranker,
            ranking_params.get("rerank_pool", 30),
            ranking_params.get("rank_weight", 1.0),
            ranking_params.get("k", 20),
        )
        notes = self.documents(
            "knowledge",
            namespace="hs_classification",
            sections=[s["section"] for s in sections],
            chunk_types=["section_note", "chapter_note", "subheading_note"],
        )
        gir = self.search(query, intent="gir", mode="full_hybrid", top_k=5, expand=False)
        return {
            **output,
            "query": query,
            "candidates": ranked[:10],
            "section_candidates": sections,
            "pipeline_policy": params,
            "definition_policy": definition_policy,
            "definition_candidates": definition_rows[:10],
            "definition_evidence": list(
                {
                    x.get("fragment_id", x["id"]): x
                    for r in self.definition_context(ranked[:10])
                    for x in r.get("definition_citations", [])
                }.values()
            )
            if definition_policy
            else [],
            "notes": notes,
            "gir": gir["matches"],
            "evidence": self.evidence(ranked[:10]),
            "validation_status": "REQUIRES_GIR_EXCLUSION_REASONING",
        }

    def section_candidates(self, ranked: list[dict], top_n: int = 2) -> list[dict]:
        # Max score avoids favoring Sections with more tariff entries.
        scores: dict[str, float] = {}
        for r in ranked:
            section = r.get("section")
            if section in ("XIV", "XVI", "XVII"):
                scores[section] = max(scores.get(section, 0), r.get("rrf_score", r.get("score", 0)))
        return [
            {"section": s, "score": score}
            for s, score in sorted(scores.items(), key=lambda x: (-x[1], x[0]))[:top_n]
        ]

    def hierarchy_search(
        self,
        query: str,
        weights: dict | None = None,
        section_policies: dict | None = None,
        rrf_k: int = 60,
        mode: str = "full_hybrid",
        beam_size: int = 5,
    ) -> dict:
        # No product semantics, Section or Chapter is discarded before cross-Section retrieval.
        normalized = " ".join(unicodedata.normalize("NFKC", query).split())
        cross = self.search(
            normalized, mode=mode, top_k=50, expand=False, weights=weights, rrf_k=rrf_k
        )
        sections = self.section_candidates(cross["candidates"])
        selected = [s["section"] for s in sections]
        # Legal evidence is gathered before descending the hierarchy. This is retrieval,
        # not a claim that an executable GIR/exclusion reasoner has validated the product.
        notes = self.search(
            normalized,
            intent="knowledge",
            namespace="hs_classification",
            chunk_types=["section_note", "chapter_note", "subheading_note"],
            sections=selected,
            mode=mode,
            top_k=20,
            expand=False,
            weights=weights,
        )
        gir = self.search(
            normalized, intent="gir", mode=mode, top_k=5, expand=False, weights=weights
        )
        mandatory_notes = self.documents(
            "knowledge",
            namespace="hs_classification",
            sections=selected,
            chunk_types=["section_note"],
        )
        notes["matches"] = list(
            {r["id"]: r for r in [*mandatory_notes, *notes["matches"]]}.values()
        )
        core_rules = self.documents("gir", chunk_types=["gir_rule"])
        gir["matches"] = list({r["id"]: r for r in [*core_rules, *gir["matches"]]}.values())
        traces = []
        final = []
        for section in selected:
            policy = (section_policies or {}).get(section, {})
            w = policy.get("weights", weights)
            branch_mode = policy.get("mode", mode)
            # Chapter candidates come from unrestricted, multi-level candidates within this Section.
            chapter_result = self.search(
                normalized,
                intent="knowledge",
                namespace="hs_classification",
                levels=[2],
                sections=[section],
                mode=branch_mode,
                top_k=beam_size,
                expand=False,
                weights=w,
                rrf_k=policy.get("k", rrf_k),
            )
            chapters = [r["code"] for r in unique_codes(chapter_result["matches"], beam_size)]
            stages = {"chapter": chapters}
            parents: dict[str, Any] = {"chapters": chapters}
            last = []
            for level, label, parent_field in [
                (4, "heading", "headings"),
                (6, "hs6", "hs6"),
                (8, "ahtn8", None),
            ]:
                stage = self.search(
                    normalized,
                    mode=branch_mode,
                    sections=[section],
                    levels=[6, 8] if level == 6 else [level],
                    top_k=50 if level == 6 else beam_size if level == 4 else 10,
                    expand=False,
                    weights=w,
                    rrf_k=policy.get("k", rrf_k),
                    **parents,
                )
                last = stage["candidates"]
                if level == 6:
                    stages[label] = list(dict.fromkeys(r["code"][:6] for r in last))[:beam_size]
                    explicit = {r["code"] for r in last if r["level"] == 6}
                    stages["hs6_implicit_prefixes"] = [
                        code for code in stages[label] if code not in explicit
                    ]
                else:
                    stages[label] = [r["code"] for r in last]
                if parent_field:
                    parents = {parent_field: stages[label]}
            final.extend(last)
            traces.append({"section": section, "stages": stages})
        # Different Section policies have different score scales; fuse the per-Section ranks equally.
        branches = {
            t["section"]: [r for r in final if r["section"] == t["section"]] for t in traces
        }
        candidates = unique_codes(fuse(branches, rrf_k), 10)
        graph = self.evidence(candidates, self.cfg["evidence_limit"], self.cfg["evidence_hops"])
        return {
            "query": normalized,
            "section_candidates": sections,
            "hierarchy": traces,
            "candidates": candidates,
            "notes": notes["matches"],
            "gir": gir["matches"],
            "evidence": graph,
            "validation_status": "REQUIRES_GIR_EXCLUSION_REASONING",
            "cross_section_fallback": cross["candidates"],
            "warnings": [
                "Top-2 routing is a candidate beam, not a legal Section decision.",
                "Exclusion targets outside loaded Sections remain external graph stubs.",
            ],
        }


def rerank_evidence(
    query: str, rows: list[dict], reranker: CrossEncoder, pool: int, rank_weight: float, k: int
) -> list[dict]:
    """Rerank by chunk ID; Notes/GIR must not collapse through code=None."""
    candidates = rows[:pool]
    scores = reranker.score(query, [r["embedding_text"] for r in candidates])
    ordered = [
        r
        for _, r in sorted(
            zip(scores, candidates, strict=True), key=lambda pair: (-pair[0], pair[1]["id"])
        )
    ]
    blended = fuse(
        {"base": candidates, "reranker": ordered},
        k,
        {"base": 1 - rank_weight, "reranker": rank_weight},
    )
    return blended + rows[pool:]
