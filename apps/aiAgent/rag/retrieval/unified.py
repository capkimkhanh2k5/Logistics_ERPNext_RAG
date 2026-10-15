"""One source retrieval and ranking algorithm for product and legal questions."""

import time
from pathlib import Path

import numpy as np
from rank_bm25 import BM25Okapi

from config.retrieval import INSTRUCTION, MODELS, WEIGHTS
from config.settings import ROOT
from rag.graph.context import GraphContext, fit_rerank_context
from rag.ingestion.sources import SOURCE_TYPES
from rag.retrieval.rerankers import CrossEncoder
from rag.utils.files import digest, read


def id_pool(channels: dict, weights: dict, limit: int, k: int = 60) -> list[dict]:
    """Reserve channel opportunity in every prefix; distinct cited IDs never collapse."""
    from rag.retrieval.retriever import fuse

    if (
        limit < 1
        or set(channels) != set(weights)
        or min(weights.values()) < 0
        or sum(weights.values()) <= 0
    ):
        raise ValueError("Invalid unified channel budget")
    weights = {n: v / sum(weights.values()) for n, v in weights.items()}
    fused = {r["id"]: r for r in fuse(channels, k, weights)}
    positions, served = dict.fromkeys(channels, 0), dict.fromkeys(channels, 0)
    seen: set[str] = set()
    result: list[dict] = []
    while len(result) < limit:
        available = []
        for name, rows in channels.items():
            while positions[name] < len(rows) and rows[positions[name]]["id"] in seen:
                positions[name] += 1
            if positions[name] < len(rows) and weights[name] > 0:
                available.append(name)
        if not available:
            break
        name = max(available, key=lambda n: weights[n] * (len(result) + 1) - served[n])
        row = channels[name][positions[name]]
        positions[name] += 1
        served[name] += 1
        seen.add(row["id"])
        result.append({**fused[row["id"]], "selection_channel": name})
    return result


def rank_scores(
    rows: list[dict], scores: list[float], weight: float = 1.0, k: int = 60
) -> list[dict]:
    from rag.retrieval.retriever import fuse

    ordered = sorted(
        [
            {**r, "rerank_score": float(s), "score": float(s)}
            for r, s in zip(rows, scores, strict=True)
        ],
        key=lambda r: (-r["rerank_score"], r["id"]),
    )
    if weight == 1:
        return ordered
    blended = fuse(
        {"retrieval": rows, "rerank": ordered}, k, {"retrieval": 1 - weight, "rerank": weight}
    )
    values = {r["id"]: r["rerank_score"] for r in ordered}
    return [{**r, "rerank_score": values[r["id"]]} for r in blended]


def hs_projection(rows: list[dict], limit: int = 10) -> list[dict]:
    seen, result = set(), []
    for row in rows:
        if (
            row.get("level") == 8
            and row.get("chunk_type") == "tariff_entry"
            and row.get("code") not in seen
        ):
            seen.add(row["code"])
            result.append(row)
            if len(result) == limit:
                break
    return result


def make_encoder(name: str) -> CrossEncoder:
    import torch

    return CrossEncoder(
        **MODELS[name],
        device="mps" if torch.backends.mps.is_available() else "cpu",
        max_length=2048,
        instruction=INSTRUCTION if name == "qwen" else None,
    )


def fit_inputs(query: str, rows: list[dict], encoder: CrossEncoder) -> list[dict]:
    # Leave room for the Qwen chat template. No atomic text is silently truncated.
    return fit_rerank_context(
        query, rows, encoder.model.tokenizer, 1840 if encoder.backend == "qwen" else 2048
    )


class UnifiedRetrieval:
    def __init__(self, retriever, policy: dict) -> None:
        self.retriever, self.policy = retriever, policy
        if retriever.embedder.profile_id != retriever.profile:
            raise ValueError("Query embedder differs from active source embedding profile")
        if "retrieval_config" in policy and policy["retrieval_config"] != retriever.cfg:
            raise ValueError("Retrieval settings differ from locked Dev configuration")
        if "models" in policy and (
            policy["models"] != MODELS
            or policy["instruction"] != INSTRUCTION
            or policy["max_length"] != 2048
        ):
            raise ValueError("Reranker implementation differs from locked policy")
        records = retriever.documents("knowledge", chunk_types=SOURCE_TYPES)
        nodes = retriever.conn.execute(
            "SELECT * FROM rag.graph_nodes WHERE snapshot=%s", (retriever.snapshot,)
        ).fetchall()
        edges = retriever.conn.execute(
            "SELECT * FROM rag.graph_edges WHERE snapshot=%s ORDER BY id", (retriever.snapshot,)
        ).fetchall()
        self.graph = GraphContext(records, nodes, edges)
        self.views = self.graph.enrich(sorted(records, key=lambda r: r["id"]), include_notes=False)
        self.views = fit_rerank_context(
            "", self.views, retriever.embedder.model.tokenizer, retriever.embedder.cfg["max_length"]
        )
        self.ids = [r["id"] for r in self.views]
        self.positions = {sid: i for i, sid in enumerate(self.ids)}
        self.index = BM25Okapi(
            [retriever.tokens(r["rerank_text"]) for r in self.views], k1=1.2, b=0.75, epsilon=0.25
        )
        self.vectors = retriever.embedder.source_context_vectors(retriever.snapshot, self.views)
        self.encoders: dict[str, CrossEncoder] = {}

    def channels(self, query: str) -> dict:
        from rag.retrieval.retriever import code_mention_plan

        r = self.retriever
        size = self.policy["candidate_pool"]
        out = r.search(
            query,
            intent="knowledge",
            mode="full_hybrid",
            top_k=size,
            expand=False,
            chunk_types=SOURCE_TYPES,
            weights=self.policy.get("weights", WEIGHTS[self.policy["weights_name"]]),
            rrf_k=self.policy["rrf_k"],
            exact_query=code_mention_plan(query)["exact_query"],
        )
        vector = r.embedder.encode([query])["dense"][0]
        dense_scores = self.vectors @ vector
        lex_scores = self.index.get_scores(r.tokens(query))

        def take(scores):
            return [
                {**self.views[i], "score": float(scores[i])}
                for i in np.argsort(-scores, kind="stable")[:size]
            ]

        context_lex, context_dense = take(lex_scores), take(dense_scores)
        seeds = [*out["matches"][:12], *context_dense[:4]]
        neighbors = set()
        for row in seeds:
            view = self.graph.source_view(row)
            neighbors.update(view["ancestor_ids"])
            neighbors.update(view["note_ids"])
        neighbor_rows = sorted(
            [
                {**self.views[self.positions[n]], "score": float(dense_scores[self.positions[n]])}
                for n in neighbors
                if n in self.positions
            ],
            key=lambda row: (-row["score"], row["id"]),
        )[:size]
        return {
            "direct": out["matches"],
            "context_lex": context_lex,
            "context_dense": context_dense,
            "neighbors": neighbor_rows,
        }

    def prepare(self, query: str, channels: dict, policy: dict | None = None) -> list[dict]:
        policy = policy or self.policy
        candidates = id_pool(
            channels, policy["channel_weights"], policy["candidate_pool"], policy["rrf_k"]
        )
        notes = [r["id"] for r in channels["direct"] if self.graph.is_note(r["id"])]
        rows = self.graph.enrich(
            candidates,
            context_budget=5000,
            note_budget=1500,
            relevant_notes=notes,
            include_notes=policy["method"] == "B2",
        )
        return self.graph.format_candidates(rows, policy.get("context_format", "plain"))

    def encoder(self, name: str) -> CrossEncoder:
        if name not in self.encoders:
            self.encoders[name] = make_encoder(name)
        return self.encoders[name]

    def rank(self, query: str, rows: list[dict]) -> list[dict]:
        policy = self.policy
        first = "m3" if policy["model"] == "cascade" else policy["model"]
        encoder = self.encoder(first)
        inputs = fit_inputs(query, rows[: policy["rerank_pool"]], encoder)
        scores = encoder.score(query, [r["rerank_text"] for r in inputs])
        ranked = rank_scores(inputs, scores, policy["rank_weight"], policy["rrf_k"])
        if policy["model"] == "cascade":
            encoder = self.encoder("qwen")
            original = {r["id"]: r for r in rows}
            inputs = fit_inputs(
                query, [original[r["id"]] for r in ranked[: policy["cascade_pool"]]], encoder
            )
            scores = encoder.score(query, [r["rerank_text"] for r in inputs])
            ranked = (
                rank_scores(inputs, scores, policy["cascade_weight"], policy["rrf_k"])
                + ranked[policy["cascade_pool"] :]
            )
        return ranked

    def semantic_intent(self, query: str) -> dict:
        path = self.policy.get("intent_artifact")
        if not path:
            return {"status": "NOT_FITTED", "used_for_retrieval": False}
        artifact = read(ROOT / Path(path))
        if (
            artifact["profile"] != self.retriever.profile
            or digest(artifact) != self.policy["intent_hash"]
        ):
            raise ValueError("Semantic intent artifact differs from locked policy")
        vector = self.retriever.embedder.encode([query])["dense"][0]
        logit = float(vector @ np.asarray(artifact["coef"]) + artifact["intercept"])
        probability = float(1 / (1 + np.exp(-np.clip(logit, -50, 50))))
        return {
            "status": "ADVISORY",
            "p_legal": probability,
            "p_product": 1 - probability,
            "intent": "mixed_or_uncertain"
            if 0.4 <= probability <= 0.6
            else "qa"
            if probability > 0.6
            else "product",
            "used_for_retrieval": False,
            "model": "bge-m3-query-embedding-logistic-regression",
        }

    def source_package(self, matches: list[dict]) -> list[dict]:
        """Materialize cited atomic sources separately from the ranked top ten."""
        package, seen = list(matches), {r["id"] for r in matches}
        for row in matches:
            for citation in [*row.get("hierarchy_citations", []), *row.get("note_citations", [])]:
                source = self.graph.records.get(citation["id"])
                if source and source["id"] not in seen:
                    seen.add(source["id"])
                    package.append({**source, "included_as": "CITED_RERANK_CONTEXT"})
        return package

    def search(self, query: str, intent_hint: str = "auto") -> dict:
        tick = time.perf_counter()
        channels = self.channels(query)
        candidates = self.prepare(query, channels)
        ranked = self.rank(query, candidates)
        hs = hs_projection(ranked)
        matches = ranked[:10]
        package = self.source_package(matches)
        return {
            "query": query,
            "intent": "knowledge",
            "routing": {
                "status": "UNIFIED_SOURCE_RETRIEVAL",
                "intent": "knowledge",
                "hint": intent_hint,
            },
            "semantic_intent": self.semantic_intent(query),
            "snapshot": self.retriever.snapshot,
            "profile": self.retriever.profile,
            "policy_hash": digest(self.policy),
            "matches": matches,
            "candidates": hs,
            "hs_candidates": hs,
            "candidate_pool": candidates,
            "ranked_pool": ranked,
            "evidence": {"records": package},
            "package": package,
            "coverage": self.retriever.coverage,
            "automatic_hs_decision": False,
            "timings": {"total_ms": (time.perf_counter() - tick) * 1000},
        }
