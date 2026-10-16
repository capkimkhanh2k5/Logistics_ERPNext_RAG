"""Optional model-assisted query expansion without a product or attribute catalogue."""

import json
import re
import time
from collections import OrderedDict

from jsonschema import ValidationError, validate

from rag.llm.errors import LLMError
from rag.prompts.query_planning import (
    QUERY_PLAN_SCHEMA,
    QUERY_PLANNING_PROMPT,
    SEARCH_HINT_TEMPLATE,
)
from rag.utils.files import digest

QUERY_FLOW_VERSION = "original-plus-search-hints-v1"


def raw_query_plan(query: str) -> dict:
    return {
        "status": "RAW_ONLY",
        "queries": [query],
        "ranking_query": query,
        "terms": [],
        "used_as_product_facts": False,
        "cache_hit": False,
    }


class QueryPlanner:
    """Share the selected RAG client and its fallback policy; fail open to raw retrieval."""

    def __init__(self, client):
        self.client = client
        self._cache: OrderedDict[str, dict] = OrderedDict()

    def fingerprint(self) -> str:
        primary = getattr(getattr(self.client, "primary", None), "config", self.client.config)
        return digest(
            {
                "version": QUERY_FLOW_VERSION,
                "prompt": QUERY_PLANNING_PROMPT,
                "schema": QUERY_PLAN_SCHEMA,
                "template": SEARCH_HINT_TEMPLATE,
                "model": self.client.config.model,
                "fallback_models": self.client.config.fallback_models,
                "endpoint": getattr(primary, "base_url", None),
                "reasoning_effort": getattr(primary, "reasoning_effort", None),
                "fallback_reasoning_effort": getattr(primary, "fallback_reasoning_effort", None),
                "temperature": getattr(primary, "temperature", None),
            }
        )

    def plan(self, query: str) -> dict:
        tick = time.perf_counter()
        fingerprint = self.fingerprint()
        key = digest({"query": query, "fingerprint": fingerprint})
        if key in self._cache:
            self._cache.move_to_end(key)
            return {
                **self._cache[key],
                "cache_hit": True,
                "elapsed_ms": (time.perf_counter() - tick) * 1000,
            }
        result = {**raw_query_plan(query), "fingerprint": fingerprint}
        try:
            generation = self.client.complete(
                [
                    {"role": "system", "content": QUERY_PLANNING_PROMPT},
                    {
                        "role": "user",
                        "content": json.dumps({"question": query}, ensure_ascii=False),
                    },
                ],
                QUERY_PLAN_SCHEMA,
            )
            result["generation"] = {
                k: generation[k]
                for k in ("model", "provider", "fallback_used", "usage", "failures", "elapsed_ms")
                if k in generation
            }
            if generation.get("finish_reason") not in (None, "stop"):
                raise ValueError("incomplete_query_plan")
            payload = json.loads(generation["content"])
            terms = self._terms(query, payload)
            if terms:
                expanded = SEARCH_HINT_TEMPLATE.format(
                    query=query, terms="; ".join(t["term"] for t in terms)
                )
                result.update(
                    status="EXPANDED",
                    terms=terms,
                    queries=[query, expanded],
                    ranking_query=expanded,
                )
            else:
                result["status"] = "NO_EXPANSION"
        except LLMError as exc:
            result.update(
                status="FALLBACK_RAW",
                error={"http_status": exc.status, "error_code": exc.error_code},
            )
        except (ValueError, ValidationError, KeyError, TypeError):
            result.update(status="FALLBACK_RAW", error={"error_code": "invalid_query_plan"})
        result["elapsed_ms"] = (time.perf_counter() - tick) * 1000
        if result["status"] != "FALLBACK_RAW":
            self._cache[key] = result
            if len(self._cache) > 64:
                self._cache.popitem(last=False)
        return result

    @staticmethod
    def _terms(query: str, payload: dict) -> list[dict]:
        validate(payload, QUERY_PLAN_SCHEMA)
        result, seen = [], set()
        for row in payload["terms"]:
            term = " ".join(row["term"].split())
            # Keep numeric conditions, codes and citation/control markup out of hints.
            if row["anchor"] not in query or not re.fullmatch(r"[^\d\[\]{}<>:;\n]+", term):
                raise ValueError("invalid_search_hint")
            if term and term.casefold() not in seen and term.casefold() not in query.casefold():
                seen.add(term.casefold())
                result.append({**row, "term": term})
        return result
