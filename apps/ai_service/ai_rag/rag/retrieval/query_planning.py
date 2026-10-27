"""Optional model-assisted query expansion without a product or attribute catalogue."""

import json
import re
import time
from collections import OrderedDict
from copy import deepcopy

from jsonschema import ValidationError, validate

from rag.llm.context.builder import compose_query
from rag.llm.context.conversation import (
    MAX_ROUTING_CHARS,
    explicit_turn,
    turn_context,
    validate_turn,
)
from rag.llm.contracts.errors import LLMError
from rag.prompts.planning.query_planning import (
    QUERY_PLAN_SCHEMA,
    QUERY_PLANNING_PROMPT,
    SEARCH_HINT_TEMPLATE,
    SEARCH_TERMS_SCHEMA,
    TURN_PLAN_SCHEMA,
    TURN_PLANNING_PROMPT,
)
from rag.retrieval.request_plan import canonical_anchor, validate_request
from rag.utils.files import digest

QUERY_FLOW_VERSION = "conversation-goals-and-search-hints-v5"


def raw_query_plan(query: str) -> dict:
    return {
        "status": "RAW_ONLY",
        "queries": [query],
        "ranking_query": query,
        "terms": [],
        "used_as_product_facts": False,
        "cache_hit": False,
        "query_hash": digest(query),
        "request": None,
    }


class QueryPlanner:
    """Plan a scoped query; uncertain conversation routing never reaches retrieval."""

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
                "turn_prompt": TURN_PLANNING_PROMPT,
                "turn_schema": TURN_PLAN_SCHEMA,
                "template": SEARCH_HINT_TEMPLATE,
                "model": self.client.config.model,
                "fallback_models": getattr(self.client.config, "fallback_models", ())
                or (self.client.config.fallback_model,),
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
                **deepcopy(self._cache[key]),
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
            if not isinstance(generation, dict):
                raise ValueError("invalid_query_response")
            result["generation"] = {
                k: generation[k]
                for k in ("model", "provider", "fallback_used", "usage", "failures", "elapsed_ms")
                if k in generation
            }
            if generation.get("finish_reason") not in (None, "stop"):
                raise ValueError("incomplete_query_plan")
            payload = json.loads(generation["content"])
            result.update(self._planned_payload(query, payload))
        except LLMError as exc:
            result.update(
                status="FALLBACK_RAW",
                error={"http_status": exc.status, "error_code": exc.error_code},
            )
        except (ValueError, ValidationError, KeyError, TypeError):
            result.update(**raw_query_plan(query), error={"error_code": "invalid_query_plan"})
            result["status"] = "FALLBACK_RAW"
        return self._finish_plan(query, result, tick)

    def plan_turn(
        self,
        question: str,
        supplements: list[str],
        message: str,
        pending_questions: list[str],
        *,
        forced_action: str | None = None,
        max_chars: int | None = None,
    ) -> tuple[dict, dict | None]:
        """Resolve a turn and its search hints in at most one application LLM call."""
        tick = time.perf_counter()
        routing = explicit_turn(question, message, forced_action)
        if routing is not None:
            next_question, next_supplements = turn_context(
                question, supplements, message, routing["action"]
            )
            query = compose_query(next_question, next_supplements, max_chars)
            return routing, self.plan(query)

        routing = {"action": "CLARIFY", "method": "SEMANTIC", "shared_with_query_plan": True}
        content = json.dumps(
            {
                "active_question": question,
                "supplements": supplements,
                "pending_questions": pending_questions,
                "message": message,
            },
            ensure_ascii=False,
        )
        if len(content) > MAX_ROUTING_CHARS:
            routing.update(method="CLARIFY", error_code="routing_context_too_long")
            return self._unresolved(routing, tick)
        try:
            generation = self.client.complete(
                [
                    {"role": "system", "content": TURN_PLANNING_PROMPT},
                    {"role": "user", "content": content},
                ],
                TURN_PLAN_SCHEMA,
            )
            if not isinstance(generation, dict):
                raise ValueError("invalid_turn_response")
            routing["generation"] = {
                key: generation[key]
                for key in ("model", "provider", "fallback_used", "usage", "failures", "elapsed_ms")
                if key in generation
            }
            if generation.get("finish_reason") not in (None, "stop"):
                raise ValueError("incomplete_turn_decision")
            payload = json.loads(generation["content"])
            if not isinstance(payload, dict):
                raise ValueError("invalid_turn_response")
            decision = {
                key: value for key, value in payload.items() if key not in {"terms", "request"}
            }
            validate_turn(decision, question, supplements, message, pending_questions)
            routing.update(decision)
        except LLMError as exc:
            routing.update(
                method="CLARIFY", error_code="routing_provider_error", http_status=exc.status
            )
            return self._unresolved(routing, tick)
        except (ValueError, ValidationError, KeyError, TypeError):
            routing.update(method="CLARIFY", error_code="invalid_turn_decision")
            return self._unresolved(routing, tick)
        if routing["action"] == "CLARIFY":
            return self._unresolved(routing, tick)

        next_question, next_supplements = turn_context(
            question, supplements, message, routing["action"]
        )
        query = compose_query(next_question, next_supplements, max_chars)
        result = {
            **raw_query_plan(query),
            "fingerprint": self.fingerprint(),
            "generation": routing["generation"],
        }
        try:
            content_plan = {key: payload[key] for key in ("terms", "request") if key in payload}
            planned = self._planned_payload(query, content_plan)
            terms = planned["terms"]
            # System-added turn labels and pending questions cannot anchor search hints.
            if any(
                not any(row["anchor"] in text for text in [next_question, *next_supplements])
                for row in terms
            ):
                raise ValueError("invalid_search_hint_anchor")
            result.update(planned)
            if planned.get("request") is not None:
                request = planned["request"]
                if any(
                    not any(row["anchor"] in text for text in [next_question, *next_supplements])
                    for row in [*request["items"], *request["objectives"]]
                ):
                    raise ValueError("invalid_request_anchor")
                result["request"] = request
        except (ValueError, ValidationError, KeyError, TypeError):
            result.update(**raw_query_plan(query), error={"error_code": "invalid_query_plan"})
            result["status"] = "FALLBACK_RAW"
        # The single shared request is accounted for under query planning, inside retrieval.
        routing["elapsed_ms"] = 0.0
        return routing, self._finish_plan(query, result, tick)

    def validate_plan(self, query: str, plan: dict) -> None:
        """Reject stale, mismatched or modified plans without a second model request."""
        if plan.get("fingerprint") != self.fingerprint() or plan.get("query_hash") != digest(query):
            raise ValueError("Precomputed plan does not match the query or planner configuration")
        status = plan.get("status")
        if status not in {"RAW_ONLY", "NO_EXPANSION", "EXPANDED", "FALLBACK_RAW"}:
            raise ValueError("Invalid precomputed plan status")
        terms = self._terms(query, {"terms": plan.get("terms")})
        if plan.get("request") is not None:
            if validate_request(query, plan["request"]) != plan["request"]:
                raise ValueError("Precomputed request plan is not canonical")
        expected = (
            self._expanded_plan(query, terms) if status == "EXPANDED" else raw_query_plan(query)
        )
        if (
            plan.get("used_as_product_facts") is not False
            or any(plan.get(key) != expected[key] for key in ("queries", "ranking_query", "terms"))
            or (status == "EXPANDED" and not terms)
        ):
            raise ValueError("Invalid precomputed search hints")

    @classmethod
    def _planned_payload(cls, query: str, payload: dict) -> dict:
        if not isinstance(payload, dict):
            raise ValueError("invalid_query_plan")
        if "request" not in payload:
            return cls._expanded_plan(query, cls._terms(query, payload))
        if set(payload) - {"terms", "request"}:
            raise ValueError("unexpected_query_plan_field")
        request = validate_request(query, payload["request"])
        try:
            terms = cls._terms(query, {"terms": payload.get("terms")})
        except (ValueError, ValidationError, KeyError, TypeError):
            return {
                **cls._expanded_plan(query, []),
                "request": request,
                "hint_error": {"error_code": "invalid_search_hints_request_preserved"},
            }
        return {**cls._expanded_plan(query, terms), "request": request}

    def _finish_plan(self, query: str, result: dict, tick: float) -> dict:
        result["elapsed_ms"] = (time.perf_counter() - tick) * 1000
        if result["status"] != "FALLBACK_RAW":
            key = digest({"query": query, "fingerprint": result["fingerprint"]})
            self._cache[key] = deepcopy(result)
            self._cache.move_to_end(key)
            if len(self._cache) > 64:
                self._cache.popitem(last=False)
        return result

    @staticmethod
    def _unresolved(routing: dict, tick: float) -> tuple[dict, None]:
        routing["elapsed_ms"] = (time.perf_counter() - tick) * 1000
        return routing, None

    @staticmethod
    def _expanded_plan(query: str, terms: list[dict]) -> dict:
        result = raw_query_plan(query)
        if terms:
            expanded = SEARCH_HINT_TEMPLATE.format(
                query=query, terms="; ".join(t["term"] for t in terms)
            )
            result.update(
                status="EXPANDED", terms=terms, queries=[query, expanded], ranking_query=expanded
            )
        else:
            result["status"] = "NO_EXPANSION"
        return result

    @staticmethod
    def _terms(query: str, payload: dict) -> list[dict]:
        validate(payload, QUERY_PLAN_SCHEMA if "request" in payload else SEARCH_TERMS_SCHEMA)
        result, seen = [], set()
        for row in payload["terms"]:
            row = {**row, "anchor": canonical_anchor(query, row["anchor"])}
            term = " ".join(row["term"].split())
            # Keep numeric conditions, codes and citation/control markup out of hints.
            if row["anchor"] not in query or not re.fullmatch(r"[^\d\[\]{}<>:;\n]+", term):
                raise ValueError("invalid_search_hint")
            if term and term.casefold() not in seen and term.casefold() not in query.casefold():
                seen.add(term.casefold())
                result.append({**row, "term": term})
        return result
