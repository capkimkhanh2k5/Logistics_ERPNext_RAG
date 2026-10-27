"""Goal-scoped answers with one batched review and a shared bounded call budget."""

import json
import re
from copy import deepcopy
from time import perf_counter

from rag.llm.contracts.diagnostics import diagnostic
from rag.llm.contracts.errors import ContractIssue, LLMError, scoped_issue
from rag.llm.contracts.obligations import review_obligations
from rag.llm.evidence.evidence import model_candidate, source_registry, unique_clarifications
from rag.llm.evidence.proof_contract import (
    bind_fact_quotes,
    candidate_outcome,
    product_fact_ids,
    proof_roles,
)
from rag.llm.providers.budget import schema_contract
from rag.llm.review.disambiguation import review_scope
from rag.llm.review.review_packet import expand_comparisons, review_packet
from rag.llm.review.review_slots import expand_review_slots
from rag.llm.validation.answer import match_user_quote, schema_errors, validate_answer
from rag.llm.validation.task_validation import (
    code_claim_errors,
    decode_task_answer,
    item_context,
    item_quote_errors,
    render_task_answer,
)
from rag.prompts.core.repair import format_task_repair_prompt
from rag.prompts.generation.task_answering import (
    ANALYSIS_REVIEW_SCHEMA,
    TASK_REVIEW_SCHEMA,
    task_answer_schema,
    task_review_prompt,
)
from rag.prompts.schemas.answer import bind_registry_schema
from rag.retrieval.request_plan import referenced_codes

MAX_ANSWER_CALLS = 8  # Shared by draft/review repairs and the optional recovery round.


def _schema_codes(schema: dict) -> set[str]:
    codes = set()

    def visit(node):
        if isinstance(node, dict):
            for key, value in node.get("properties", {}).items():
                if key in {"code", "selected_code", "suggested_hs_code"}:
                    codes.update(value.get("enum", []))
            for value in node.values():
                visit(value)
        elif isinstance(node, list):
            for value in node:
                visit(value)

    visit(schema)
    return codes


class TaskRun:
    def __init__(self, client, model, allow_fallback, remaining):
        self.client, self.model, self.allow_fallback = client, model, allow_fallback
        self.remaining = remaining
        self.calls: list[dict] = []
        self.validation_ms = 0.0

    def request(
        self,
        messages,
        schema,
        checker,
        phase,
        *,
        reserve=0,
        repair_contract=None,
        max_attempts=2,
        repair_request=None,
        on_withhold=None,
    ):
        messages = list(messages)
        decoded, errors = None, ["Ngân sách gọi model đã hết."]
        payload: dict = {}
        terminal_errors: list[str] = []
        total_attempts = min(max_attempts, max(0, self.remaining - reserve))
        for attempt in range(total_attempts):
            self.remaining -= 1
            tick = perf_counter()
            try:
                generation = self.client.complete(
                    messages,
                    schema,
                    model=self.model,
                    allow_fallback=self.allow_fallback if not attempt else False,
                )
            except LLMError as exc:
                self.calls.append(
                    {
                        "phase": phase,
                        "elapsed_ms": (perf_counter() - tick) * 1000,
                        "error_code": exc.error_code,
                        "http_status": exc.status,
                        "transport_attempts": exc.transport_attempts,
                        "request_contract": schema_contract(schema, "provider_request_failed"),
                    }
                )
                if attempt < total_attempts - 1 and self.remaining > reserve:
                    from time import sleep
                    sleep(2)
                    continue
                return {}, None, [*terminal_errors, "Dịch vụ model chưa hoàn thành kiểm tra."]
            self.model = generation.get("model", self.model)
            entry = {**generation, "phase": phase, "elapsed_ms": (perf_counter() - tick) * 1000}
            entry.setdefault("request_contract", schema_contract(schema, "client_contract"))
            self.calls.append(entry)
            validation_started = perf_counter()
            try:
                from rag.llm.contracts.repair_dispatch import canonicalize

                payload, changes = canonicalize(
                    json.loads(generation["content"]), _schema_codes(schema)
                )
                entry["canonicalizations"] = changes
                if generation.get("finish_reason") == "stop":
                    decoded, errors = checker(payload)
                else:
                    decoded, errors = None, ["Phản hồi model chưa hoàn tất bình thường."]
            except (ValueError, KeyError, TypeError):
                decoded, errors = None, ["Phản hồi không đúng JSON bắt buộc."]
            self.validation_ms += (perf_counter() - validation_started) * 1000
            entry["validation_errors"] = errors
            entry["validation_issues"] = [diagnostic(e, phase) for e in errors]
            from rag.llm.contracts.repair_dispatch import dispatch

            disposition = dispatch(errors, phase, allow_rebind=True)
            entry["repair_disposition"] = disposition
            terminal_errors = list(disposition["withhold"])
            if on_withhold and disposition["withhold"]:
                on_withhold(disposition["withhold"])
            errors = disposition["repair"]
            if not errors:
                break
            messages.extend(
                [
                    {"role": "assistant", "content": generation["content"]},
                    {
                        "role": "user",
                        "content": format_task_repair_prompt(
                            errors,
                            phase=phase,
                            contract=repair_contract() if repair_contract else None,
                        ),
                    },
                ]
            )
            if repair_request is not None:
                messages, schema = repair_request(messages[-1])
        return payload, decoded, list(dict.fromkeys([*terminal_errors, *errors]))


def blocked(row: dict, reason: str) -> dict:
    return {
        **row,
        "status": "REQUIRES_REVIEW",
        "suggested_hs_code": "",
        "answer": reason,
        "citations": [],
        "missing_information": [],
        "missing_legal_evidence": [],
        "review_valid": False,
        "hs_candidates": [],
        "failure_kind": "TECHNICAL",
        "claims": row.get("claims", []),
    }


def _unreviewed_fallback(row: dict, scoped: dict, reason: str) -> dict:

    labels = {c["label"] for c in row.get("citations", [])}
    sources = [source for source in scoped["sources"] if source["label"] in labels]
    result = blocked(row, reason)
    if row.get("valid") and sources:
        result["answer"] += " Nguồn tham khảo, chưa xác nhận áp dụng cho hàng hóa: " + " ".join(
            f"[{source['label']}]" for source in sources
        )
        result["citations"] = [
            {"label": source["label"], "quote": source["text"]} for source in sources
        ]
    return result


def review_jobs(rows: list[dict], context: dict) -> tuple[list[dict], dict]:
    from rag.llm.context.builder import _model_candidate_evidence
    from rag.llm.evidence.conditions import review_conditions

    jobs, scopes = [], {}
    goals = {g["id"]: g for g in context["request"]["objectives"]}
    items = {i["id"]: i for i in context["request"]["items"]}
    for row in rows:
        if row["status"] != "RECOMMENDATION":
            continue
        original = row["suggested_hs_code"]
        scoped_context = context.get("review_contexts", {}).get(row["result_id"], context)
        scoped = item_context(scoped_context, row["item_id"], row["level"], original)
        selection = [
            c["code"]
            for c in scoped["candidate_evidence"]
            if c["code"] in scoped["allowed_hs_codes"]
            and (row["level"] != 8 or c["code"][:6] == original[:6])
        ]
        if row.get("candidate_only"):
            peers = {
                c["code"]: c
                for c in [
                    *scoped["candidate_evidence"],
                    *context["candidate_evidence"],
                    *context.get("comparison_candidates", []),
                ]
                if c["code"] in row["shortlist_codes"] or c in scoped["candidate_evidence"]
            }
            scoped["candidate_evidence"] = list(peers.values())
            scoped["candidate_comparison"] = [
                {
                    "parent_code": "",
                    "codes": list(peers),
                    "missing_codes": [],
                    "branch_options": [],
                },
                *[g for g in scoped["candidate_comparison"] if g["parent_code"]],
            ]
        groups = review_scope(scoped, original)
        scoped["review_conditions"] = review_conditions(scoped, groups, original)
        sources = {s["label"]: s for s in context["sources"]}
        selected = next(c for c in scoped["candidate_evidence"] if c["code"] == original)
        prerequisites = [
            {
                "code": node["code"],
                "level": node["level"],
                "evidence_ids": [
                    sources[label]["evidence_id"]
                    for label in node.get("evidence_labels", [])
                    if label in sources
                ],
            }
            for node in selected["hierarchy"]["chain"]
            if node["level"] < row["level"]
        ]
        scopes[row["result_id"]] = (scoped, row, selection)
        comparison_pool = {
            c["code"]: c
            for c in [
                *scoped["candidate_evidence"],
                *context.get("candidate_evidence", []),
                *context.get("comparison_candidates", []),
            ]
            if any(c["code"] in g["codes"] for g in groups)
            or c["code"] in selection
            or c["code"] == original
        }
        jobs.append(
            {
                "result_id": row["result_id"],
                "shortlist_member": row.get("candidate_only", False),
                "objective": {**goals[row["objective_id"]], "level": row["level"]},
                "item": items[row["item_id"]],
                "proposed_answer": {
                    "code": original,
                    "claims": row["claims"],
                    "clarifications": row.get("draft_clarifications", []),
                },
                "selection_codes": selection,
                "candidate_evidence": [
                    model_candidate(c, context["sources"])
                    for c in _model_candidate_evidence(list(comparison_pool.values()))
                ],
                "review_scope": groups,
                "required_comparison_codes": sorted(
                    {code for group in groups for code in group["codes"]}
                ),
                "required_branch_groups": [g for g in groups if g["branch_options"]],
                "allowed_fact_ids": [s["id"] for s in scoped["user_context"]["statements"]],
                "prerequisites": prerequisites,
                "note_scope_evidence_ids": [
                    sources[label]["evidence_id"]
                    for label in selected.get("related_note_labels", [])
                    if label in sources
                ]
                if selected.get("note_scope_required")
                else [],
            }
        )
    return jobs, scopes


def _canonical_quotes(raw: dict, scoped: dict) -> dict:
    """Replace model quotes by the authentic user slices they refer to, when one exists."""
    statements = {s["id"]: s["text"] for s in scoped["user_context"]["statements"]}
    from rag.llm.contracts.obligations import statement_role
    from rag.llm.validation.answer import LEGAL_INFORMATION, _folded

    asserted_ids = [
        sid
        for sid, text in statements.items()
        if statement_role(text) == "ASSERTED" and not LEGAL_INFORMATION.search(_folded(text))
    ]
    sources = {}
    for s in scoped.get("sources", []):
        if "evidence_id" in s:
            sources[s["evidence_id"]] = s
        if "label" in s:
            sources[s["label"]] = s

    from rag.llm.validation.quantitative import _quantities, _proves

    req_labels = {
        label
        for cand in scoped.get("candidate_evidence", [])
        for label in cand.get("required_citation_labels", [])
    }

    review = deepcopy(raw)
    for key in ["condition_checks", "candidate_assessments", "branch_checks"]:
        for check in review.get(key, []):
            if "evidence_ids" in check:
                check["evidence_ids"] = [eid for eid in check["evidence_ids"] if not (isinstance(eid, str) and eid.startswith("U"))]
            if "decisive_evidence_ids" in check:
                check["decisive_evidence_ids"] = [eid for eid in check["decisive_evidence_ids"] if not (isinstance(eid, str) and eid.startswith("U"))]
            eid = check.get("evidence_id")
            source = sources.get(eid) or sources.get(check.get("source_label"))
            if source and check.get("assessment") == "SATISFIED":
                thresholds = _quantities(source.get("text", ""))
                if thresholds:
                    matching_facts = []
                    has_proof = True
                    for thresh in thresholds:
                        proved_by = []
                        candidates_to_check = check.get("fact_ids", []) or asserted_ids
                        for sid in candidates_to_check:
                            stext = statements.get(sid, "")
                            fact_quantities = _quantities(stext, facts=True)
                            for fq in fact_quantities:
                                if fq.dimension == thresh.dimension and _proves(fq, thresh):
                                    proved_by.append(sid)
                        if not proved_by:
                            has_proof = False
                            break
                        matching_facts.extend(proved_by)
                    if not has_proof:
                        source_label = source.get("label", "")
                        if source_label not in req_labels:
                            check["assessment"] = "NOT_APPLICABLE"
                            check["fact_ids"] = []
                            check["user_quotes"] = []
                        else:
                            check["assessment"] = "MISSING_PRODUCT_INFO"
                    elif not check.get("fact_ids") and matching_facts:
                        check["fact_ids"] = list(dict.fromkeys(matching_facts))

            # Exclude legal quotes/statements from product facts
            if check.get("fact_ids"):
                check["fact_ids"] = [
                    sid
                    for sid in check["fact_ids"]
                    if sid in statements and not LEGAL_INFORMATION.search(_folded(statements[sid]))
                ]
            if (
                check.get("assessment") in {"SATISFIED", "RULED_OUT", "CONTRADICTED"}
                and not check.get("fact_ids")
                and asserted_ids
            ):
                check["fact_ids"] = [asserted_ids[0]]
            if not check.get("evidence_ids") and check.get("code"):
                cand_code = check["code"]
                matched_eids = [
                    s["evidence_id"]
                    for s in scoped.get("sources", [])
                    if s.get("code") == cand_code
                    or (s.get("code") and cand_code.startswith(s["code"]))
                ]
                if matched_eids:
                    check["evidence_ids"] = [matched_eids[0]]
            texts = [statements[sid] for sid in check.get("fact_ids", []) if sid in statements]
            if check.get("user_quotes"):
                cleaned_quotes = [
                    q for q in check["user_quotes"] if not LEGAL_INFORMATION.search(_folded(q))
                ]
                check["user_quotes"] = [
                    match_user_quote(quote, texts) or quote for quote in cleaned_quotes
                ] if cleaned_quotes else list(texts)
            else:
                check["user_quotes"] = list(texts)
    return review


def _confirmed_analysis(proposed: dict, code: str, scoped: dict) -> tuple[str, list[dict]]:
    """Keep the draft's cited legal analysis only when review confirmed the same code."""
    from rag.llm.evidence.evidence import render_claims

    if code != proposed["suggested_hs_code"] or not proposed.get("valid"):
        return "", []
    claims = [c for c in proposed.get("claims", []) if c["kind"] == "LEGAL_ANALYSIS"]
    if scoped.get("proof_required"):
        from rag.llm.validation.proof import proof_errors

        if any(
            proof_errors(
                {**claim, "assessment": "APPLICATION" if claim.get("fact_ids") else "REFERENCE"},
                scoped,
                target=claim["text"],
                product=bool(claim.get("fact_ids")),
                evidence_ids=claim["evidence_ids"],
                fact_ids=claim["fact_ids"],
            )
            for claim in claims
        ):
            return "", []
    if not claims or code_claim_errors(claims, code, scoped):
        return "", []
    text, citations, errors = render_claims(claims, scoped)
    return ("", []) if errors or not text else (text, citations)


def _review_payload(value: dict, context: dict, scopes: dict) -> tuple[dict, list[str]]:
    from rag.llm.evidence.conditions import (
        bind_condition_refs,
        defer_descendant_comparison,
        predicate_bindings,
    )
    from rag.llm.generation.answering import check_product_review

    if (
        not isinstance(value, dict)
        or set(value) != {"reviews"}
        or not isinstance(value.get("reviews"), list)
    ):
        return {}, schema_errors(value, TASK_REVIEW_SCHEMA)
    errors: list[str] = []
    reviews = value["reviews"]
    ids = [
        r["result_id"]
        for r in reviews
        if isinstance(r, dict) and isinstance(r.get("result_id"), str)
    ]
    if len(ids) != len(reviews):
        errors.append(
            ContractIssue(
                "Review có slot không định danh được.", code="SCHEMA_VIOLATION", path="reviews"
            )
        )
    reviews = [r for r in reviews if isinstance(r, dict) and isinstance(r.get("result_id"), str)]
    missing = set(scopes) - set(ids)
    errors.extend(
        ContractIssue(
            f"{rid}: Thiếu review được cấp.", code="REVIEW_SLOT_MISSING", path=f"{rid}/review"
        )
        for rid in sorted(missing)
    )
    duplicate = {rid for rid in ids if ids.count(rid) > 1}
    errors.extend(
        ContractIssue(
            f"{rid}: Review lặp hoặc ngoài phạm vi.",
            code="REVIEW_SLOT_UNKNOWN",
            path=f"{rid}/review",
        )
        for rid in set(ids) - set(scopes) | duplicate
    )
    checked = {}
    for value_row in reviews:
        if value_row.get("result_id") not in scopes or value_row.get("result_id") in duplicate:
            continue
        value_row = deepcopy(value_row)
        raw_review = value_row.get("review")
        grouped = (
            raw_review.get("candidate_group_assessments", [])
            if isinstance(raw_review, dict)
            else []
        )
        for group in grouped if isinstance(grouped, list) else []:
            codes = group.get("codes") if isinstance(group, dict) else None
            if isinstance(codes, list) and all(isinstance(code, str) for code in codes):
                # Repeated codes within ONE identical proof carry no extra assertion.
                group["codes"] = list(dict.fromkeys(codes))
        row_errors = schema_errors(value_row, TASK_REVIEW_SCHEMA["properties"]["reviews"]["items"])
        if row_errors:
            errors.extend(f"{value_row['result_id']}: {e}" for e in row_errors)
            continue
        rid, code = value_row["result_id"], value_row["selected_code"]
        scoped, proposed, selection = scopes[rid]
        if code not in selection:
            errors.append(f"{rid}: Mã chọn lại không có trong selection_codes đã xác minh.")
            continue
        raw = deepcopy(value_row["review"])
        grouped = raw.pop("candidate_group_assessments", [])
        survivors = [
            c
            for g in grouped
            if g.get("assessment") == "POSSIBLE"
            for c in g.get("codes", [])
            if c in selection
        ]
        ruled_out = {
            c
            for g in grouped
            if g.get("assessment") == "RULED_OUT"
            for c in g.get("codes", [])
        }
        if raw.get("status") == "REJECTED" and len(survivors) == 1 and code in ruled_out:
            winner = survivors[0]
            code = winner
            value_row["selected_code"] = winner
            raw["status"] = "SUPPORTED"
        candidate = next(c for c in scoped["candidate_evidence"] if c["code"] == code)
        raw["candidate_assessments"].extend(
            {**{k: v for k, v in group.items() if k != "codes"}, "code": peer}
            for group in grouped
            for peer in group["codes"]
        )
        bcs = raw.get("branch_checks", [])
        known_parents = {
            b["parent_code"]
            for b in bcs
            if b.get("assessment") == "KNOWN" and b.get("fact_ids")
        }
        if known_parents:
            raw["branch_checks"] = [
                b
                for b in bcs
                if not (
                    b.get("parent_code") in known_parents
                    and b.get("assessment") == "KNOWN"
                    and not b.get("fact_ids")
                )
            ]
        sources = {s["label"]: s for s in scoped.get("sources", context.get("sources", []))}
        rule_labels = [
            l
            for l in candidate.get("required_citation_labels", [])
            if l in context.get("application_rule_labels", []) and l in sources
        ]
        present_eids = {c.get("evidence_id") for c in raw.get("condition_checks", [])}
        for rlabel in rule_labels:
            reid = sources[rlabel]["evidence_id"]
            if reid not in present_eids:
                branch_facts = [
                    fid
                    for b in raw.get("branch_checks", [])
                    if b.get("assessment") == "KNOWN"
                    for fid in b.get("fact_ids", [])
                ]
                if branch_facts:
                    raw.setdefault("condition_checks", []).append(
                        {
                            "evidence_id": reid,
                            "assessment": "SATISFIED",
                            "fact_ids": branch_facts,
                            "user_quotes": [],
                        }
                    )
        from rag.llm.review.proof_resolution import resolve_review

        raw = resolve_review(raw, scoped)
        raw, deferred_eids = defer_descendant_comparison(raw, scoped, code)
        if deferred_eids:
            scoped["comparison_deferred_for"] = deferred_eids
        raw = _canonical_quotes(bind_condition_refs(raw, scoped), scoped)
        raw = proof_roles(raw, scoped, code)
        # An unavailable peer is a source gap, never a model-proven exclusion.
        missing_peers = {
            code for group in review_scope(scoped, code) for code in group["missing_codes"]
        }
        if missing_peers:
            raw.update(
                status="INSUFFICIENT_LEGAL_EVIDENCE",
                reason="Chưa đủ nguồn của các nhánh đối chứng để phân định ứng viên.",
                clarifications=[],
                missing_legal_evidence=[
                    "Thiếu nguồn đối chứng trong ngữ cảnh: " + ", ".join(sorted(missing_peers))
                ],
            )
            raw["candidate_assessments"] = [
                {
                    **assessment,
                    "assessment": "INSUFFICIENT_LEGAL_EVIDENCE",
                    "evidence_ids": [],
                    "fact_ids": [],
                    "user_quotes": [],
                }
                if assessment["code"] in missing_peers
                else assessment
                for assessment in raw["candidate_assessments"]
            ]
        if raw["status"] != "SUPPORTED":
            # The selected code belongs in the structured candidate field. Its
            # occurrence in a review's explanation is a reference, not a new proposal.
            references = {code} | {
                peer for group in review_scope(scoped, code) for peer in group["codes"]
            }
            references.update(node["code"] for node in candidate["hierarchy"]["chain"])
            forms = {}
            for ref in references:
                for form in {
                    ref,
                    ".".join([ref[:4], *[ref[i : i + 2] for i in range(4, len(ref), 2)]]),
                } | ({ref[:2] + "." + ref[2:]} if len(ref) == 4 else set()):
                    forms[form] = "ứng viên đang xét" if ref == code else "nhánh đối chứng"
            raw["reason"] = re.sub(
                r"(?<!\d)(?:"
                + "|".join(re.escape(form) for form in sorted(forms, key=len, reverse=True))
                + r")(?!\d|\.\d)",
                lambda match: forms[match[0]],
                raw["reason"],
            )
        if code != proposed["suggested_hs_code"] and raw["status"] != "SUPPORTED":
            errors.append(
                ContractIssue(
                    f"{rid}: Chỉ được đổi selected_code sang ứng viên khác khi ứng viên mới đạt SUPPORTED.",
                    code="RESELECTION_UNSUPPORTED",
                    path=f"{rid}/selected_code",
                    expected=proposed["suggested_hs_code"],
                    actual=code,
                )
            )
            continue
        foreign = item_quote_errors(
            [
                q
                for key in ["condition_checks", "candidate_assessments", "branch_checks"]
                for check in raw[key]
                for q in check["user_quotes"]
            ],
            scoped,
        )
        if foreign:
            errors.extend(f"{rid}: {e}" for e in foreign)
            continue
        candidate_answer = {**proposed, "suggested_hs_code": code}
        public_raw = deepcopy(raw)
        if context.get("reasoning_contract") == "semantic-v1" and raw.get("reason", "").strip():
            public_raw["reason"] = {
                "SUPPORTED": "Đề xuất phân loại theo mã đã được kiểm tra từ dữ kiện và nguồn.",
                "MISSING_PRODUCT_INFO": "Chưa đủ dữ kiện để xác nhận điều kiện quyết định.",
                "INSUFFICIENT_LEGAL_EVIDENCE": "Nguồn hiện có chưa chứng minh đầy đủ điều kiện áp dụng.",
                "REJECTED": "Ứng viên có điều kiện cần bị bác bỏ; các nhánh khác cần được kiểm tra.",
            }.get(raw["status"], "Chưa phân định được cách áp dụng điều kiện nguồn.")
            if raw["status"] == "INSUFFICIENT_LEGAL_EVIDENCE" and raw.get("missing_legal_evidence"):
                public_raw["missing_legal_evidence"] = [public_raw["reason"]]
        answer, decoded, row_errors = check_product_review(
            public_raw,
            scoped,
            candidate,
            candidate_answer,
            {s["label"] for s in context["sources"]},
        )
        if decoded and raw["status"] == "SUPPORTED":
            labels = {c["source_label"] for c in decoded["condition_checks"]}
            reason = (
                decoded["reason"]
                + " "
                + " ".join(f"[{s['label']}]" for s in context["sources"] if s["label"] in labels)
            )
            analysis, analysis_citations = _confirmed_analysis(proposed, code, scoped)
            labels.update(c["label"] for c in analysis_citations)
            citations = [
                {"label": s["label"], "quote": s["text"]}
                for s in context["sources"]
                if s["label"] in labels
            ]
            text = f"{analysis} {reason}" if analysis else reason
            answer = {
                **candidate_answer,
                "status": "RECOMMENDATION",
                "answer": text,
                "citations": citations,
                "missing_information": [],
                "missing_legal_evidence": [],
            }
            row_errors.extend(
                validate_answer(
                    {
                        k: answer[k]
                        for k in [
                            "status",
                            "answer",
                            "suggested_hs_code",
                            "alternatives",
                            "citations",
                            "missing_information",
                            "missing_legal_evidence",
                        ]
                    },
                    {
                        **scoped,
                        "structured_code_claims": [
                            {"kind": "CONCLUSION", "text": decoded["reason"]}
                        ],
                    },
                )["errors"]
            )
            row_errors.extend(
                code_claim_errors(
                    [{"kind": "CONCLUSION", "text": decoded["reason"]}], code, context
                )
            )
        if (
            decoded
            and proposed.get("candidate_only")
            and raw["status"] != "REJECTED"
            and not deferred_eids
        ):
            covered = {c["source_label"] for c in decoded["condition_checks"]}
            if not set(candidate["required_citation_labels"]) <= covered:
                row_errors.append(
                    "Mỗi ứng viên phải kiểm tra mọi điều kiện bắt buộc, kể cả khi thiếu dữ kiện."
                )
        if decoded:
            row_errors.extend(
                code_claim_errors(
                    [{"kind": "CONCLUSION", "text": decoded["reason"]}],
                    code if raw["status"] == "SUPPORTED" else "",
                    context,
                )
            )
        if row_errors:
            errors.extend(scoped_issue(e, rid) for e in row_errors)
        else:
            checked[rid] = {
                **proposed,
                **answer,
                "review_valid": True,
                "failure_kind": "",
                "condition_bindings": [
                    binding
                    for key in ("condition_checks", "branch_checks", "clarifications")
                    for check in raw[key]
                    for binding in predicate_bindings(check, scoped)
                ],
                "reselected_from": proposed["suggested_hs_code"]
                if code != proposed["suggested_hs_code"]
                else "",
                "review": decoded,
                "candidate_outcome": candidate_outcome(decoded),
                "review_clarifications": [
                    {
                        **q,
                        "source_ids": [
                            source_registry(context)[eid]["id"] for eid in q["evidence_ids"]
                        ],
                    }
                    for q in unique_clarifications(raw["clarifications"])
                ],
                "reviewed_code": code,
                "candidate_assessments": raw.get("candidate_assessments", []),
                "verified_path": [
                    {"code": n["code"], "level": n["level"]}
                    for n in candidate["hierarchy"]["chain"]
                ],
                "selected_source": {
                    "snapshot": context.get("snapshot"),
                    "source_id": next(
                        s["id"]
                        for s in context["sources"]
                        if s["label"] == candidate["wording_label"]
                    ),
                },
            }
        if rid in checked and deferred_eids:
            checked[rid]["comparison_deferred_for"] = deferred_eids
    return checked, list(dict.fromkeys(errors))


def _partition_review_batches(rows: list[dict], max_batch_size: int = 3) -> list[list[dict]]:
    """Partition review rows so that each batch does not exceed Gemini schema limits.

    Rows belonging to the same item are kept together so comparison matrices remain cohesive.
    """
    if len(rows) <= max_batch_size:
        return [rows]

    by_item: dict[str, list[dict]] = {}
    for r in rows:
        key = r.get("item_id") or r.get("result_id", "").split(".")[0]
        by_item.setdefault(key, []).append(r)

    batches: list[list[dict]] = []
    current_batch: list[dict] = []

    for item_rows in by_item.values():
        for i in range(0, len(item_rows), max_batch_size):
            chunk = item_rows[i : i + max_batch_size]
            if len(current_batch) + len(chunk) <= max_batch_size:
                current_batch.extend(chunk)
            else:
                if current_batch:
                    batches.append(current_batch)
                current_batch = list(chunk)
    if current_batch:
        batches.append(current_batch)
    return batches


def _execute_review_batch(rows: list[dict], context: dict, run: TaskRun) -> tuple[list[dict], dict]:
    from rag.llm.review.analysis_review import (
        analysis_jobs,
        check_analyses,
    )

    jobs, scopes = review_jobs(rows, context)
    analyses = analysis_jobs(rows, context)
    if not jobs and not analyses:
        return rows, {}
    schema = deepcopy(TASK_REVIEW_SCHEMA)
    if jobs:
        props = schema["properties"]["reviews"]["items"]["properties"]
        props["result_id"]["enum"] = [j["result_id"] for j in jobs]
        props["selected_code"]["enum"] = sorted(
            {code for j in jobs for code in j["selection_codes"]}
        )
    if analyses:
        schema["properties"]["analysis_reviews"] = ANALYSIS_REVIEW_SCHEMA
        schema["required"].append("analysis_reviews")
    schema["properties"]["reviews"]["minItems"] = 1 if jobs else 0
    schema["properties"]["reviews"]["maxItems"] = len(jobs)
    branch_schema = schema["properties"]["reviews"]["items"]["properties"]["review"]["properties"][
        "branch_checks"
    ]
    # The wire carries source IDs only. Stable condition bindings are assigned by
    # the backend after decoding; the model need not copy a second ID namespace.
    branch_schema["items"]["properties"].pop("condition_ids", None)
    schema["properties"]["reviews"]["items"]["properties"]["review"]["properties"][
        "clarifications"
    ]["items"]["properties"].pop("condition_ids", None)
    question_wire = schema["properties"]["reviews"]["items"]["properties"]["review"]["properties"][
        "clarifications"
    ]["items"]
    question_wire["required"] = [*question_wire["required"], "criterion_quote"]
    branch_schema["items"]["required"] = [*branch_schema["items"]["required"], "criterion_quote"]
    condition_wire = schema["properties"]["reviews"]["items"]["properties"]["review"]["properties"][
        "condition_checks"
    ]["items"]
    condition_wire["required"] = [*condition_wire["required"], "criterion_quote"]
    parents = sorted({g["parent_code"] for job in jobs for g in job["required_branch_groups"]})
    if parents:
        branch_schema["items"]["properties"]["parent_code"]["enum"] = parents
    else:
        branch_schema["maxItems"] = 0
    labels = {
        label
        for scoped, row, _ in scopes.values()
        for candidate in scoped["candidate_evidence"]
        for label in [*candidate["required_citation_labels"], *candidate["related_note_labels"]]
    }
    labels.update(c["label"] for _, row, _ in scopes.values() for c in row["citations"])
    labels.update(
        label for _, row, _ in scopes.values() for label in row.get("review_evidence_labels", [])
    )
    analysis_evidence = {
        eid for job in analyses for claim in job["claims"] for eid in claim["evidence_ids"]
    }
    analysis_evidence.update(eid for job in analyses for eid in job["coverage_evidence_ids"])
    labels.update(s["label"] for s in context["sources"] if s["evidence_id"] in analysis_evidence)
    payload = {
        "jobs": jobs,
        "analysis_jobs": analyses,
        "reasoning_contract": context.get("reasoning_contract"),
        "legal_scope": context.get("legal_scope"),
        "as_of": context.get("as_of"),
        "review_obligations": review_obligations(jobs, analyses),
        "user_context": context["user_context"],
        "sources": [
            {
                k: s[k]
                for k in [
                    "evidence_id",
                    "code",
                    "chunk_type",
                    "text",
                    "document",
                    "locator",
                    "effective_from",
                    "effective_to",
                    "legal_status",
                ]
                if k in s
            }
            for s in context["sources"]
            if s["label"] in labels
        ],
    }
    schema = bind_registry_schema(
        schema,
        [s["evidence_id"] for s in payload["sources"]],
        product_fact_ids(context["user_context"]),
    )
    from rag.llm.evidence.conditions import bind_registered_conditions, condition_span_registry

    span_registry = condition_span_registry(payload["sources"])
    packet, wire_schema, bindings = review_packet(payload, schema)
    active_bindings = dict(bindings)
    active_layout = dict(packet["review_slots"])
    application_claims = {
        job["result_id"]: set(job.get("application_claim_indices", [])) for job in analyses
    }
    retained: dict[str, dict] = {}
    withheld: set[str] = set()
    superseded_errors: list[str] = []

    def check(value):
        obsolete: set[str] = set()
        # Validate the dynamic batch schema, then use the original classification decoder.
        if not isinstance(value, dict):
            return retained, ["Batch review phải là JSON object."]
        from rag.llm.evidence.catalogue import expand_proofs

        value, proof_ref_errors = expand_proofs(value)
        if proof_ref_errors:
            return retained, proof_ref_errors
        value, slot_errors = expand_review_slots(value, active_layout)
        slot_errors.extend(proof_ref_errors)
        bad_slots = {
            rid
            for error in slot_errors
            if getattr(error, "diagnostic", {}).get("code") == "SCHEMA_VIOLATION"
            for rid in [*scopes, *(j["result_id"] for j in analyses)]
            if rid in getattr(error, "diagnostic", {}).get("path", "").split("/")
        }
        for field in ("reviews", "analysis_reviews"):
            if field in value and isinstance(value[field], list):
                value[field] = [
                    row
                    for row in value[field]
                    if not isinstance(row, dict) or row.get("result_id") not in bad_slots
                ]
        value = bind_fact_quotes(value, context)
        span_errors: list[str] = []
        for field in ("reviews", "analysis_reviews", "comparison_reviews"):
            good = []
            for unit in value.get(field, []):
                if not isinstance(unit, dict):
                    span_errors.append(
                        ContractIssue(
                            "Slot không đúng cấu trúc object.", code="SCHEMA_VIOLATION", path=field
                        )
                    )
                    continue
                bound, failures = bind_registered_conditions(unit, span_registry)
                if failures:
                    identity = (
                        unit.get("comparison_id")
                        if field == "comparison_reviews"
                        else unit.get("result_id")
                    )
                    owners = (
                        [rid for rid, gid in active_bindings.items() if gid == identity]
                        if field == "comparison_reviews"
                        else [identity]
                    )
                    span_errors.extend(
                        scoped_issue(error, rid) for rid in owners if rid for error in failures
                    )
                else:
                    good.append(bound)
            if field in value:
                value[field] = good
        value, matrix_errors = expand_comparisons(value, active_bindings)
        active_scopes = {
            rid: scope
            for rid, scope in scopes.items()
            if rid not in retained and rid not in withheld
        }
        if active_scopes and "reviews" not in value:
            return retained, ["Batch review thiếu trường reviews bắt buộc."]
        if set(value) - set(schema["properties"]):
            return retained, ["Batch review chứa trường ngoài schema được cấp."]
        active_reviews = [
            r
            for r in value.get("reviews", [])
            if not isinstance(r, dict)
            or r.get("result_id") not in retained
            and r.get("result_id") not in withheld
        ]
        checked, errors = (
            _review_payload({"reviews": active_reviews}, context, active_scopes)
            if active_scopes
            else (
                {},
                ["Không được tự tạo job phân loại khi chỉ có analysis_jobs."]
                if active_reviews
                else [],
            )
        )
        if analyses:
            for analysis in value.get("analysis_reviews", []):
                if (
                    not isinstance(analysis, dict)
                    or analysis.get("result_id") not in application_claims
                ):
                    continue
                rid = analysis["result_id"]
                for check_row in analysis.get("checks", []):
                    if isinstance(check_row, dict) and check_row.get("assessment") in {
                        "APPLICATION",
                        "CONDITIONAL_APPLICATION",
                    }:
                        index = check_row.get("claim_index")
                        if isinstance(index, int) and next(
                            j["item_ids"] for j in analyses if j["result_id"] == rid
                        ):
                            application_claims[rid].add(index)
            for job in analyses:
                job["application_claim_indices"] = sorted(application_claims[job["result_id"]])
            reviewed_analyses, analysis_errors = check_analyses(
                [
                    r
                    for r in value.get("analysis_reviews", [])
                    if not isinstance(r, dict)
                    or r.get("result_id") not in retained
                    and r.get("result_id") not in withheld
                ],
                [
                    j
                    for j in analyses
                    if j["result_id"] not in retained and j["result_id"] not in withheld
                ],
                rows,
                context,
            )
            for rid, analysis in reviewed_analyses.items():
                if rid in scopes:
                    classified = checked.get(rid)
                    if classified is not None:
                        if (
                            analysis["status"]
                            != rows[
                                next(i for i, row in enumerate(rows) if row["result_id"] == rid)
                            ]["status"]
                        ):
                            checked[rid] = {
                                **analysis,
                                "suggested_hs_code": "",
                                "review_valid": False,
                            }
                        else:
                            checked[rid] = {
                                **classified,
                                "analysis_review_valid": True,
                                "analysis_checks": analysis["analysis_checks"],
                            }
                else:
                    checked[rid] = analysis
            if context.get("reasoning_contract") == "semantic-v1":
                for job in analyses:
                    rid = job["result_id"]
                    if rid in scopes and rid not in reviewed_analyses and rid not in retained:
                        checked.pop(rid, None)
            errors.extend(analysis_errors)
            obsolete = {
                rid
                for rid, (_, row, _) in scopes.items()
                if any(
                    analysis.get("application_evidence_gap")
                    and row["item_id"]
                    in next(j["item_ids"] for j in analyses if j["result_id"] == aid)
                    and row["level"] >= analysis.get("application_gap_level", 0)
                    for aid, analysis in reviewed_analyses.items()
                )
            }
            superseded_errors.extend(
                error for error in errors if any(error.startswith(f"{rid}:") for rid in obsolete)
            )
            errors = [
                error
                for error in errors
                if not any(error.startswith(f"{rid}:") for rid in obsolete)
            ]
        for rid, row in checked.items():
            retained.setdefault(rid, row)
        errors = [e for e in errors if not any(e.startswith(f"{rid}:") for rid in retained)]
        # Bind slot diagnostics to their real dependent owners before deciding repair.
        owned_errors = [*span_errors, *matrix_errors, *errors]
        for error in slot_errors:
            path = getattr(error, "diagnostic", {}).get("path", "")
            owners = [rid for rid, gid in active_bindings.items() if gid in path.split("/")]
            owners.extend(
                rid
                for rid in [*scopes, *(j["result_id"] for j in analyses)]
                if rid in path.split("/")
            )
            for rid in set(owners):
                if not isinstance(rid, str) or rid in retained:
                    continue
                issue = scoped_issue(error, rid)
                if rid in obsolete:
                    superseded_errors.append(issue)
                else:
                    owned_errors.append(issue)
        return dict(retained), [
            e for e in owned_errors if not any(str(e).startswith(f"{rid}:") for rid in retained)
        ]

    def on_withhold(errors):
        for error in errors:
            path = getattr(error, "diagnostic", {}).get("path", "")
            for rid in [*scopes, *(job["result_id"] for job in analyses)]:
                if str(error).startswith(f"{rid}:") or path.startswith(f"{rid}/"):
                    withheld.add(rid)

    def retry_request(feedback):
        pending = {
            **payload,
            "jobs": [
                job
                for job in jobs
                if job["result_id"] not in retained and job["result_id"] not in withheld
            ],
            "analysis_jobs": [
                job
                for job in analyses
                if job["result_id"] not in retained and job["result_id"] not in withheld
            ],
        }
        pending_schema = deepcopy(schema)
        if not pending["jobs"]:
            pending_schema["properties"].pop("reviews", None)
            pending_schema["required"] = [
                k for k in pending_schema["required"] if k != "reviews"
            ]
        else:
            pending_schema["properties"]["reviews"]["maxItems"] = len(pending["jobs"])
            pending_schema["properties"]["reviews"]["minItems"] = 1
            pending_schema["properties"]["reviews"]["items"]["properties"]["result_id"]["enum"] = [
                j["result_id"] for j in pending["jobs"]
            ]
        if not pending["analysis_jobs"]:
            pending_schema["properties"].pop("analysis_reviews", None)
            pending_schema["required"] = [
                k for k in pending_schema["required"] if k != "analysis_reviews"
            ]
        pending_packet, pending_wire, pending_bindings = review_packet(pending, pending_schema)
        active_layout.clear()
        active_layout.update(pending_packet["review_slots"])
        active_bindings.clear()
        active_bindings.update(pending_bindings)
        return [
            {
                "role": "system",
                "content": task_review_prompt(
                    classification=bool(pending["jobs"]), analysis=bool(pending["analysis_jobs"])
                ),
            },
            {"role": "user", "content": json.dumps(pending_packet, ensure_ascii=False)},
            feedback,
        ], pending_wire

    _, checked, errors = run.request(
        [
            {
                "role": "system",
                "content": task_review_prompt(classification=bool(jobs), analysis=bool(analyses)),
            },
            {"role": "user", "content": json.dumps(packet, ensure_ascii=False)},
        ],
        wire_schema,
        check,
        "product_review",
        repair_contract=lambda: {
            "read_only_claims": True,
            "job_types": [
                kind
                for kind, pending in [
                    ("classification", any(rid not in retained for rid in scopes)),
                    ("analysis", any(j["result_id"] not in retained for j in analyses)),
                ]
                if pending
            ],
            "application_claim_indices": {
                rid: sorted(indices) for rid, indices in application_claims.items()
            },
            "locked_results": list(retained),
        },
        repair_request=retry_request,
        on_withhold=on_withhold,
    )
    checked = checked or retained
    updated = [
        checked.get(
            r["result_id"],
            _unreviewed_fallback(
                r,
                scopes[r["result_id"]][0] if r["result_id"] in scopes else context,
                "Kiểm tra kết luận chưa hoàn tất hợp lệ; xem diagnostic lỗi hệ thống.",
            )
            if r["result_id"] in scopes or any(j["result_id"] == r["result_id"] for j in analyses)
            else r,
        )
        for r in rows
    ]
    for row in updated:
        coverage: list[str] = next(
            (j["coverage_evidence_ids"] for j in analyses if j["result_id"] == row["result_id"]),
            [],
        )
        if coverage and any(
            e.startswith(f"{row['result_id']}:") and "REQUIREMENTS_COVERAGE_MISSING" in e
            for e in errors
        ):
            row["answer_coverage_gap"] = coverage
            row["coverage_failure_kind"] = "UNVERIFIED"
    return updated, {
        "valid": not errors,
        "errors": errors,
        "checked_results": list(checked),
        "slot_coverage": {
            rid: "VALIDATED" if rid in checked else "UNREVIEWED"
            for rid in [*scopes, *(job["result_id"] for job in analyses)]
        },
        "superseded_errors": list(dict.fromkeys(superseded_errors)),
    }


def review_results(rows: list[dict], context: dict, run: TaskRun) -> tuple[list[dict], dict]:
    """Execute review jobs in batches of at most 3 to respect model schema complexity limits."""
    batches = _partition_review_batches(rows, max_batch_size=3)
    if len(batches) <= 1:
        return _execute_review_batch(rows, context, run)

    all_updated: list[dict] = []
    combined_errors: list[str] = []
    checked_results: list[str] = []
    slot_coverage: dict[str, str] = {}
    superseded_errors: list[str] = []

    for batch in batches:
        b_updated, b_report = _execute_review_batch(batch, context, run)
        all_updated.extend(b_updated)
        if b_report:
            combined_errors.extend(b_report.get("errors", []))
            checked_results.extend(b_report.get("checked_results", []))
            slot_coverage.update(b_report.get("slot_coverage", {}))
            superseded_errors.extend(b_report.get("superseded_errors", []))

    row_map = {r["result_id"]: r for r in all_updated}
    return [row_map.get(r["result_id"], r) for r in rows], {
        "valid": not combined_errors,
        "errors": combined_errors,
        "checked_results": checked_results,
        "slot_coverage": slot_coverage,
        "superseded_errors": list(dict.fromkeys(superseded_errors)),
    }


def _fill_missing(rows: list[dict], context: dict) -> list[dict]:
    goals = {g["id"]: g for g in context["request"]["objectives"]}
    for r in rows:
        g = goals.get(r.get("objective_id"))
        if g and g.get("kind") != "CLASSIFY" and r.get("item_id") in set(g.get("item_ids", [])):
            r["item_id"] = ""
    rows = list({(r["objective_id"], r["item_id"]): r for r in rows}.values())
    actual = {(r["objective_id"], r["item_id"]) for r in rows}
    next_id = (
        max(
            (int(r["result_id"][1:]) for r in rows if re.fullmatch(r"R\d+", r["result_id"])),
            default=0,
        )
        + 1
    )
    for goal in context["request"]["objectives"]:
        for item in goal["item_ids"] if goal["kind"] == "CLASSIFY" else [""]:
            if (goal["id"], item) not in actual:
                rows.append(
                    blocked(
                        {
                            "result_id": f"R{next_id}",
                            "objective_id": goal["id"],
                            "item_id": item,
                            "level": goal["level"],
                            "kind": goal["kind"],
                            "required": goal["required"],
                        },
                        "Mục tiêu này chưa có phản hồi hợp lệ.",
                    )
                )
                next_id += 1
    return rows


def review_by_level(rows: list[dict], context: dict, run: TaskRun) -> tuple[list[dict], dict]:
    """Review parents before leaves, retaining completed results within the same budget."""
    from rag.llm.generation.shortlist import collapse_rows, expand_rows
    from rag.llm.review.prerequisites import defer_leaf, leaf_review, parent_review

    pending = list(rows)
    completed: list[dict] = []
    reports: list[dict] = []
    while pending:
        ready = [
            row
            for row in pending
            if row["kind"] != "CLASSIFY"
            or not any(
                p["kind"] == "CLASSIFY"
                and p["required"]
                and p["item_id"] == row["item_id"]
                and 0 < p["level"] < row["level"]
                for p in pending
            )
        ]
        deferred_ids = {row["result_id"] for row in pending} - {row["result_id"] for row in ready}
        pending = [row for row in pending if row["result_id"] in deferred_ids]
        eligible = []
        for row in ready:
            parents = [
                p
                for p in completed
                if p["kind"] == "CLASSIFY"
                and p["required"]
                and p["item_id"] == row["item_id"]
                and 0 < p["level"] < row["level"]
            ]
            if any(p["status"] != "RECOMMENDATION" or not p.get("review_valid") for p in parents):
                completed.append(
                    {**row, "candidate_codes": [], "hs_candidates": []}
                    if row.get("clarifications_inherited")
                    and row["status"] == "MISSING_PRODUCT_INFO"
                    else blocked(
                        row,
                        "Chưa xét mã chi tiết khi nhóm cha chưa được xác định; cần xử lý điều kiện phân biệt ở nhóm cha trước.",
                    )
                )
            else:
                eligible.append(row)
        states = {}
        for row in eligible:
            leaf, leaf_context = row, context
            parents = [
                p
                for p in completed
                if p["kind"] == "CLASSIFY"
                and p["item_id"] == row["item_id"]
                and p.get("review_valid")
                and p["status"] == "RECOMMENDATION"
                and 0 < p["level"] < row["level"]
            ]
            if parents:
                leaf, leaf_context = leaf_review(
                    leaf, leaf_context, max(parents, key=lambda p: p["level"])
                )
            states[row["result_id"]] = (leaf, leaf_context)
        while states:
            prerequisites = {
                rid: probe
                for rid, (leaf, scoped) in states.items()
                if (probe := parent_review(leaf, scoped)) is not None
            }
            if not prerequisites:
                break
            parent_rows = [probe[0] for probe in prerequisites.values()]
            parent_scopes = {probe[0]["result_id"]: probe[1] for probe in prerequisites.values()}
            reviewed, report = review_results(
                parent_rows, {**context, "review_contexts": parent_scopes}, run
            )
            if report:
                reports.append({**report, "stage": "prerequisite"})
            by_parent = {parent["result_id"]: parent for parent in reviewed}
            for rid, (proposed, _) in prerequisites.items():
                leaf, scoped = states[rid]
                parent = by_parent[proposed["result_id"]]
                if parent["status"] != "RECOMMENDATION" or not parent.get("review_valid"):
                    completed.append(defer_leaf(leaf, parent))
                    del states[rid]
                else:
                    states[rid] = leaf_review(leaf, scoped, parent)
        expanded_all, scoped_all, groups_by_row = [], {}, {}
        for rid, (leaf, scoped) in list(states.items()):
            if (
                leaf["kind"] == "CLASSIFY"
                and leaf["status"] == "RECOMMENDATION"
                and not leaf["suggested_hs_code"]
            ):
                completed.append(blocked(leaf, "Chưa có nguồn mã con thuộc nhóm cha đã kiểm tra."))
                del states[rid]
                continue
            expanded, groups = expand_rows([leaf], scoped)
            expanded_all.extend(expanded)
            scoped_all.update({row["result_id"]: scoped for row in expanded})
            groups_by_row[rid] = groups
        if expanded_all:
            reviewed, report = review_results(
                expanded_all, {**context, "review_contexts": scoped_all}, run
            )
            for rid, (leaf, scoped) in states.items():
                ids = set(groups_by_row[rid].get(rid, [rid]))
                completed.extend(
                    collapse_rows(
                        [leaf],
                        [row for row in reviewed if row["result_id"] in ids],
                        groups_by_row[rid],
                        scoped,
                    )
                )
            if report:
                reports.append(report)
    by_id = {row["result_id"]: row for row in completed}
    return [by_id[row["result_id"]] for row in rows], {
        "valid": bool(reports) and all(report["valid"] for report in reports),
        "errors": [error for report in reports for error in report["errors"]],
        "checked_results": [rid for report in reports for rid in report["checked_results"]],
        "superseded_errors": [
            error for report in reports for error in report.get("superseded_errors", [])
        ],
        "waves": len(reports),
    }


def _resolve_levels(rows: list[dict]) -> list[dict]:
    for index, row in enumerate(rows):
        if row["kind"] != "CLASSIFY":
            continue
        lower = [
            r
            for r in rows
            if r["kind"] == "CLASSIFY"
            and r["item_id"] == row["item_id"]
            and 0 < r["level"] < row["level"]
        ]
        if any(
            r["required"] and (r["status"] != "RECOMMENDATION" or not r.get("review_valid"))
            for r in lower
        ):
            if (
                row.get("required")
                and row.get("valid")
                and row["status"] in {"MISSING_PRODUCT_INFO", "INSUFFICIENT_LEGAL_EVIDENCE"}
                and all(r["status"] == row["status"] for r in lower if r["required"])
            ):
                continue
            parent_unresolved = next(
                (
                    r
                    for r in lower
                    if r["required"]
                    and r["status"] in {"INSUFFICIENT_LEGAL_EVIDENCE", "MISSING_PRODUCT_INFO"}
                ),
                None,
            )
            if parent_unresolved:
                p_status = parent_unresolved["status"]
                rows[index] = {
                    **row,
                    "status": p_status,
                    "suggested_hs_code": "",
                    "answer": parent_unresolved.get(
                        "answer",
                        "Chưa xét mã chi tiết khi nhóm hoặc phân nhóm chưa được xác định.",
                    ),
                    "citations": parent_unresolved.get("citations", []),
                    "missing_information": parent_unresolved.get("missing_information", []),
                    "missing_legal_evidence": parent_unresolved.get("missing_legal_evidence", []),
                    "review_valid": True,
                    "hs_candidates": [],
                    "failure_kind": "",
                }
                continue
            rows[index] = blocked(
                row,
                "Chưa xét mã chi tiết khi nhóm hoặc phân nhóm bắt buộc của cùng mặt hàng chưa được xác định.",
            )
            continue
        path = {n["level"]: n["code"] for n in row.get("verified_path", [])}
        if row["status"] == "RECOMMENDATION" and any(
            r.get("review_valid")
            and r["status"] == "RECOMMENDATION"
            and path.get(r["level"]) != r["suggested_hs_code"]
            for r in lower
        ):
            rows[index] = blocked(
                row, "Kết quả mã chi tiết mâu thuẫn với nhóm đã được kiểm tra của cùng mặt hàng."
            )
    return rows


def _withhold_application(row: dict, context: dict, reason: str) -> dict:
    result = blocked(row, reason)
    if row.get("analysis_review_valid"):
        from rag.llm.evidence.evidence import render_claims

        independent = {
            check["claim_index"]
            for check in row.get("analysis_checks", [])
            if check["assessment"] in {"REFERENCE", "CONDITIONAL_APPLICATION"}
        }
        claims = [claim for i, claim in enumerate(row.get("claims", [])) if i in independent]
        if claims:
            text, citations, errors = render_claims(claims, context)
            if not errors:
                result.update(
                    claims=claims,
                    answer=text + " " + reason,
                    citations=citations,
                    independent_explanation_retained=True,
                )
    return result


def _resolve_comparisons(rows: list[dict], context: dict) -> list[dict]:
    goals = {g["id"]: g for g in context["request"]["objectives"]}
    checked = {
        (r["objective_id"], r["item_id"]): r
        for r in rows
        if r["kind"] == "CLASSIFY" and r["status"] == "RECOMMENDATION" and r.get("review_valid")
    }
    for index, row in enumerate(rows):
        if row["kind"] == "CLASSIFY":
            continue
        goal = goals[row["objective_id"]]
        application = any(
            check.get("assessment") == "APPLICATION" for check in row.get("analysis_checks", [])
        )
        if application:
            bindings = {}
            for check in row.get("analysis_checks", []):
                if check.get("assessment") != "APPLICATION":
                    continue
                if check["claim_index"] not in range(len(row.get("claims", []))):
                    rows[index] = _withhold_application(
                        row, context, "Thiếu nhận định áp dụng đã kiểm tra."
                    )
                    break
                claim = row["claims"][check["claim_index"]]
                refs = set(check.get("fact_ids", []))
                owners = [
                    item
                    for item in goal["item_ids"]
                    if refs
                    and refs
                    <= {
                        fact["id"]
                        for fact in item_context(context, item, 0)["user_context"]["statements"]
                    }
                ] or goal["item_ids"]
                domains = [
                    {
                        code
                        for result in checked.values()
                        if result["item_id"] == item
                        for code in [
                            result["suggested_hs_code"],
                            *(node["code"] for node in result.get("verified_path", [])),
                        ]
                    }
                    for item in owners
                ]
                registered = set.union(*domains) if domains else set()
                if row.get("kind") in {"EXPLAIN", "COMPARE"} or len(goal.get("item_ids", [])) > 1:
                    goal_domains = [
                        {
                            code
                            for result in checked.values()
                            if result["item_id"] == item
                            for code in [
                                result["suggested_hs_code"],
                                *(node["code"] for node in result.get("verified_path", [])),
                            ]
                        }
                        for item in goal.get("item_ids", [])
                    ]
                    if goal_domains:
                        registered = set.union(*goal_domains)
                if not any(r["kind"] == "CLASSIFY" for r in rows):
                    registered = {s.get("code") for s in context.get("sources", []) if s.get("code")}
                # The reviewed APPLICATION role owns this gate, including named-item prose.
                failures = code_claim_errors(
                    [{**claim, "kind": "CONCLUSION"}], "", context, registered, application=True
                )
                if not failures and len(owners) > 1 and len(domains) > 1:
                    items_by_id = {i["id"]: i for i in context.get("request", {}).get("items", [])}
                    for item, item_domain in zip(owners, domains):
                        anchor = items_by_id.get(item, {}).get("anchor", "")
                        if anchor and anchor in claim.get("text", ""):
                            clauses = [part for part in re.split(r"[;.\n]", claim.get("text", "")) if anchor in part]
                            other_domains = set.union(*(d for other_item, d in zip(owners, domains) if other_item != item))
                            for clause in clauses:
                                clause_codes = referenced_codes(clause)
                                foreign_codes = (clause_codes & other_domains) - item_domain
                                if foreign_codes:
                                    failures = [f"Mặt hàng {anchor} bị gán sai mã của mặt hàng khác: {foreign_codes}"]
                                    break
                            if failures:
                                break
                if failures:
                    rows[index] = _withhold_application(
                        row,
                        context,
                        "Nhận định áp mã chưa được gắn với kết quả đã xác nhận của đúng mặt hàng.",
                    )
                    break
                bindings[str(check["claim_index"])] = owners
            else:
                row["application_item_bindings"] = bindings
            if rows[index] is not row:
                continue
        required_items = {
            item
            for g in goals.values()
            if g["kind"] == "CLASSIFY"
            for item in g["item_ids"]
            if item in goal["item_ids"]
        }
        if (
            application
            and required_items
            and not all(
                any(r["item_id"] == item and r["level"] >= goal["level"] for r in checked.values())
                for item in required_items
            )
        ):
            rows[index] = _withhold_application(
                row,
                context,
                "Phần áp dụng phụ thuộc kết quả phân loại chưa hoàn tất của từng mặt hàng.",
            )
            continue
        if row.get("depends_on") and not all(tuple(key) in checked for key in row["depends_on"]):
            rows[index] = blocked(
                row, "Phần kết luận này phụ thuộc kết quả phân loại chưa hoàn tất."
            )
            if row["kind"] == "EXPLAIN" and row.get("analysis_review_valid"):
                from rag.llm.evidence.evidence import render_claims

                independent = {
                    c["claim_index"]
                    for c in row["analysis_checks"]
                    if c["assessment"] in {"REFERENCE", "CONDITIONAL_APPLICATION"}
                }
                claims = [c for i, c in enumerate(row["claims"]) if i in independent]
                if claims:
                    text, citations, _ = render_claims(claims, context)
                    rows[index].update(
                        claims=claims,
                        answer=text
                        + " Chưa xác nhận áp dụng cho hàng hóa khi kết quả phân loại còn chờ bổ sung.",
                        citations=citations,
                        independent_explanation_retained=True,
                    )
        binary_code_question = bool(
            re.search(r"(?:cùng|chung|khác)\s+(?:mã|nhóm|phân\s+nhóm)", goal["anchor"], re.I)
            or re.search(
                r"(?:mã(?:\s+HS[468])?|nhóm|phân\s+nhóm)\s+(?:có\s+)?(?:cùng|chung|khác)",
                goal["anchor"],
                re.I,
            )
            or re.search(r"cả\s+hai|tất\s+cả", goal["anchor"], re.I)
            and referenced_codes(goal["anchor"])
            and re.search(r"có\s+(?:được\s+)?phân\s+loại.+không", goal["anchor"], re.I)
        )
        if (
            goal["kind"] != "COMPARE"
            or not goal["level"]
            or not binary_code_question
            or len(goal["item_ids"]) < 2
        ):
            continue
        items = [
            max(
                (r for r in checked.values() if r["item_id"] == item),
                key=lambda r: r["level"],
                default=None,
            )
            for item in goal["item_ids"]
        ]
        if any(r is None for r in items):
            keeps_reference_answer = (
                row.get("valid")
                and row["status"] == "ANSWERED"
                and referenced_codes(goal["anchor"])
                and any(r is not None for r in items)
            )
            if not keeps_reference_answer and any(
                g["kind"] == "CLASSIFY" and set(goal["item_ids"]) & set(g["item_ids"])
                for g in goals.values()
            ):
                rows[index] = blocked(
                    row,
                    "Chưa đủ kết quả phân loại đã kiểm tra của từng mặt hàng để xác nhận so sánh mã.",
                )
            continue
        paths = [{n["level"]: n["code"] for n in r["verified_path"]} for r in items if r]
        levels = set.intersection(*(set(p) for p in paths))
        usable = [level for level in levels if level <= goal["level"]]
        if not usable:
            continue
        level = max(usable)
        codes = [p[level] for p in paths]
        same = len(set(codes)) == 1
        if same and level < goal["level"]:
            rows[index] = blocked(
                row,
                "Cùng nhóm ở cấp tổng quát chưa đủ để khẳng định cùng mã ở cấp chi tiết được hỏi.",
            )
            continue
        comparison_citations = {c["label"]: c for r in items if r for c in r["citations"]}
        text = (
            ("Các mặt hàng có cùng" if same else "Các mặt hàng có khác")
            + f" mã ở cấp {level} số: "
            + "; ".join(
                f"{item}: {code}" for item, code in zip(goal["item_ids"], codes, strict=True)
            )
            + "."
        )
        if level < goal["level"]:
            text += (
                f" Vì đã khác cấp {level} số, chúng không thể dùng chung mã cấp {goal['level']} số."
            )
        text += " " + " ".join(f"[{label}]" for label in comparison_citations)
        rows[index] = {
            **row,
            "status": "ANSWERED",
            "answer": text,
            "claims": [],
            "analysis_checks": [],
            "analysis_review_valid": False,
            "review_valid": False,
            "failure_kind": "",
            "suggested_hs_code": "",
            "citations": list(comparison_citations.values()),
            "missing_information": [],
            "missing_legal_evidence": [],
            "derived_from_reviewed_results": [r["result_id"] for r in items if r],
        }
    return rows


def generate_task_answer(
    context: dict, client, *, model=None, allow_fallback=True, remaining=MAX_ANSWER_CALLS
) -> dict:
    context = {
        **context,
        "proof_required": False,
        "reasoning_contract": "semantic-v1",
        "legal_scope": context.get(
            "legal_scope", "CURRENT_APPLICABILITY" if context.get("as_of") else "SOURCE_SNAPSHOT"
        ),
        "proof_catalogue": {},
        "proof_cache": {},
        "proof_adjustments": [],
    }
    started = perf_counter()
    run = TaskRun(client, model, allow_fallback, remaining)
    retained_drafts: dict[tuple[str, str], dict] = {}

    def check_draft(value):
        from rag.llm.evidence.catalogue import expand_proofs
        from rag.llm.evidence.ledger import (
            bind_ledger,
            bind_ledger_refs,
            ledger_dependencies_changed,
        )

        value, proof_ref_errors = expand_proofs(value)
        if isinstance(value, dict) and context.get("proof_required"):
            bound, ledger_errors = bind_ledger(value, context)
            if ledger_errors and context.get("proof_required"):
                return [], ledger_errors
            before_ledger = context["user_context"].get("fact_ledger", [])
            after_ledger = bound["user_context"].get("fact_ledger", [])
            for key in list(retained_drafts):
                if ledger_dependencies_changed(retained_drafts[key], before_ledger, after_ledger):
                    retained_drafts.pop(key)
            context.update(bound)
            value = bind_ledger_refs(value, context)
        if proof_ref_errors:
            # Null placeholders are not missing objectives or external-source failures.
            # Regenerate local graphs before decoding their consumers, within the same budget.
            return [], proof_ref_errors
        if not isinstance(value, dict) or not isinstance(value.get("results"), list):
            return decode_task_answer(value, context)
        merged = deepcopy(value)
        raw_rows = merged["results"]
        goals = {g["id"]: g for g in context["request"]["objectives"]}
        for key, prior in retained_drafts.items():
            positions = [
                i
                for i, row in enumerate(raw_rows)
                if isinstance(row, dict) and (
                    row.get("objective_id"),
                    "" if (goals.get(row.get("objective_id"), {}).get("kind") != "CLASSIFY" and row.get("item_id") in set(goals.get(row.get("objective_id"), {}).get("item_ids", []))) else row.get("item_id")
                ) == key
            ]
            if len(positions) == 1:
                raw_rows[positions[0]] = deepcopy(prior)
            elif not positions:
                raw_rows.append(deepcopy(prior))
        decoded, errors = decode_task_answer(merged, context)
        errors.extend(proof_ref_errors)
        for row in decoded:
            if row["valid"]:
                raw = raw_rows[int(row["result_id"][1:]) - 1]
                retained_drafts[(row["objective_id"], row["item_id"])] = {
                    **deepcopy(raw),
                    "item_id": row["item_id"],
                }
        return decoded, errors

    def repair_contract():
        return {
            "objectives": context["request"]["objectives"],
            "locked_results": [
                {"objective_id": key[0], "item_id": key[1]} for key in retained_drafts
            ],
        }

    payload, rows, errors = run.request(
        context["messages"],
        bind_registry_schema(
            task_answer_schema(
                context["request"],
                [
                    c["code"]
                    for c in [
                        *context["candidate_evidence"],
                        *context.get("comparison_candidates", []),
                    ]
                    if c["hierarchy"]["status"] == "VERIFIED"
                ],
            ),
            [s["evidence_id"] for s in context["sources"]],
            product_fact_ids(context["user_context"]),
        ),
        check_draft,
        "answer",
        reserve=1,
        repair_contract=repair_contract,
    )
    rows = _fill_missing(rows or [], context)
    if run.calls and run.calls[-1].get("finish_reason") != "stop":
        rows = [blocked(r, "Phản hồi model chưa hoàn tất bình thường.") for r in rows]
    rows = [
        r
        if r.get("valid", True)
        else blocked(r, "Phản hồi mục tiêu chưa qua kiểm tra dữ kiện hoặc nguồn.")
        for r in rows
    ]
    # Do not spend leaf-review jobs while a required parent is already unresolved.
    for index, row in enumerate(rows):
        unresolved = (
            [
                parent
                for parent in rows
                if parent["kind"] == "CLASSIFY"
                and parent["item_id"] == row["item_id"]
                and parent["required"]
                and 0 < parent["level"] < row["level"]
                and parent["status"] != "RECOMMENDATION"
            ]
            if row["kind"] == "CLASSIFY"
            else []
        )
        if unresolved and not row.get("clarifications_inherited"):
            rows[index] = {
                **blocked(
                    row,
                    "Chưa xét mã chi tiết khi nhóm cha còn thiếu căn cứ hoặc dữ kiện phân biệt.",
                ),
                "candidate_codes": [],
            }
    rows, review = review_by_level(rows, context, run)
    revision_targets = {
        (r["objective_id"], r["item_id"]): r
        for r in rows
        if r["kind"] != "CLASSIFY" and r.get("answer_coverage_gap")
    }
    revision = {
        "attempted": False,
        "result_ids": [r["result_id"] for r in revision_targets.values()],
    }
    if revision_targets and run.remaining >= 2:
        revision["attempted"] = True
        for key in revision_targets:
            retained_drafts.pop(key, None)
        feedback: list[str] = [
            ContractIssue(
                "Kiểm tra và bổ sung phạm vi điều kiện của draft; coverage chưa được xác nhận."
                if r.get("coverage_failure_kind") == "UNVERIFIED"
                else "Danh sách điều kiện chưa được trình bày đầy đủ trong draft.",
                code="DRAFT_COVERAGE_UNVERIFIED"
                if r.get("coverage_failure_kind") == "UNVERIFIED"
                else "DRAFT_COVERAGE_OMITTED",
                path=f"{r['result_id']}/claims",
                expected=r["answer_coverage_gap"],
                actual=[],
            )
            for r in revision_targets.values()
        ]
        payload, repaired, revision_errors = run.request(
            [
                *context["messages"],
                {"role": "assistant", "content": json.dumps(payload, ensure_ascii=False)},
                {
                    "role": "user",
                    "content": format_task_repair_prompt(
                        feedback, phase="answer", contract=repair_contract()
                    ),
                },
            ],
            bind_registry_schema(
                task_answer_schema(
                    context["request"],
                    [
                        c["code"]
                        for c in [
                            *context["candidate_evidence"],
                            *context.get("comparison_candidates", []),
                        ]
                        if c["hierarchy"]["status"] == "VERIFIED"
                    ],
                ),
                [s["evidence_id"] for s in context["sources"]],
                product_fact_ids(context["user_context"]),
            ),
            check_draft,
            "answer",
            reserve=1,
            max_attempts=1,
            repair_contract=repair_contract,
        )
        eligible = [
            r
            for r in repaired or []
            if (r["objective_id"], r["item_id"]) in revision_targets and r["valid"]
        ]
        revised, revised_review = (
            review_by_level(eligible, {**context, "draft_rows": rows}, run)
            if eligible
            else ([], {})
        )
        replacements = {(r["objective_id"], r["item_id"]): r for r in revised}
        rows = [replacements.get((r["objective_id"], r["item_id"]), r) for r in rows]
        revision["errors"] = [*revision_errors, *revised_review.get("errors", [])]
        resolved_ids = {
            r["result_id"]
            for r in revised
            if r.get("analysis_review_valid") and not r.get("answer_coverage_gap")
        }
        superseded = [
            error
            for error in review["errors"]
            if any(error.startswith(f"{rid}:") for rid in resolved_ids)
        ]
        review.setdefault("superseded_errors", []).extend(superseded)
        review["errors"] = [e for e in review["errors"] if e not in superseded]
        review["errors"].extend(revision["errors"])
        review["valid"] = not review["errors"]
        review["waves"] += revised_review.get("waves", 0)
    from rag.llm.review.analysis_review import resolve_analysis_gaps
    from rag.llm.review.review_coverage import review_coverage

    rows = resolve_analysis_gaps(rows, context)
    rows = _resolve_levels(rows)
    rows = _resolve_comparisons(rows, context)
    derived = {
        row["result_id"]
        for row in rows
        if row.get("derived_from_reviewed_results")
        and row["status"] == "ANSWERED"
        and not row.get("failure_kind")
    }
    superseded = [
        error
        for error in review.get("errors", [])
        if any(str(error).startswith(f"{rid}:") for rid in derived)
    ]
    review.setdefault("superseded_errors", []).extend(superseded)
    review["errors"] = [error for error in review.get("errors", []) if error not in superseded]
    review["valid"] = not review["errors"]
    if context.get("legal_scope") == "SOURCE_SNAPSHOT":
        for row in rows:
            if (
                row["status"] == "RECOMMENDATION"
                or row["status"] == "ANSWERED"
                and (
                    row.get("derived_from_reviewed_results")
                    or any(
                        check.get("assessment")
                        in {"APPLICATION", "REFERENCE", "CONDITIONAL_APPLICATION"}
                        for check in row.get("analysis_checks", [])
                    )
                )
            ):
                row["answer"] += (
                    " Nội dung tham khảo theo nguồn trong hệ thống; chưa xác minh hiệu lực hiện hành."
                )
    answer = render_task_answer(rows, context)
    coverage = review_coverage(rows)
    cited = {c["label"] for c in answer["citations"]}
    timings = {
        "llm_ms": sum(c["elapsed_ms"] for c in run.calls),
        "answer_llm_ms": sum(c["elapsed_ms"] for c in run.calls if c["phase"] == "answer"),
        "product_review_llm_ms": sum(
            c["elapsed_ms"] for c in run.calls if c["phase"] == "product_review"
        ),
        "decision_review_llm_ms": 0,
        "validation_ms": run.validation_ms,
        "total_ms": (perf_counter() - started) * 1000,
    }
    generation = {
        "model": run.model,
        "provider": next((c.get("provider") for c in run.calls if c.get("provider")), None),
        "elapsed_ms": timings["llm_ms"],
        "application_calls": len(run.calls),
        "remaining_calls": run.remaining,
        "attempts": run.calls,
        "task_review": review,
        "reasoning_contract": "semantic-v1",
        "proof_contract_version": None,
        "fact_ledger": context["user_context"].get("fact_ledger", []),
        "proof_catalogue": context.get("proof_catalogue", {}),
        "proof_adjustments": context.get("proof_adjustments", []),
        "prerequisite_reviews": [
            {
                "result_id": row["result_id"],
                "reviews": row.get("prerequisite_reviews", [row["prerequisite_review"]]),
            }
            for row in rows
            if row.get("prerequisite_review")
        ],
        "draft_revision": revision,
        "discarded_candidate_codes": [
            {"result_id": row["result_id"], "codes": row["discarded_candidate_codes"]}
            for row in rows
            if row.get("discarded_candidate_codes")
        ],
        "fallback_used": any(c.get("fallback_used") for c in run.calls),
        "failures": [f for c in run.calls for f in c.get("failures", [])],
        "usage": {
            k: sum(c.get("usage", {}).get(k, 0) for c in run.calls)
            for k in ["prompt_tokens", "completion_tokens", "total_tokens"]
        },
        "evidence_gaps": payload.get("evidence_gaps", []) if not errors else [],
    }
    reasons = [*errors, *review.get("errors", [])]
    return {
        "answer": answer,
        "generation": generation,
        "timings": timings,
        "validation": {
            "valid": True,
            "output_contract_valid": True,
            "legal_scope": context.get("legal_scope"),
            "current_applicability_verified": False,
            "review_execution_status": "FAILED" if reasons else "COMPLETED",
            "errors": [],
            "cited_labels": sorted(cited),
            "cited_source_ids": [s["id"] for s in context["sources"] if s["label"] in cited],
            "semantic_grounding": coverage["status"],
            "review_coverage": coverage["results"],
            "task_completion": not any(
                r["required"] and r["status"] not in {"ANSWERED", "RECOMMENDATION"} for r in rows
            ),
            "boundary_errors": [],
        },
        "diagnostics": {
            "stage": "task_validation",
            "code": "SYSTEM_VALIDATION_ERROR",
            "reasons": reasons,
            "candidate_hs_code": "",
            "source_labels": sorted(cited),
        }
        if reasons
        else {},
    }
