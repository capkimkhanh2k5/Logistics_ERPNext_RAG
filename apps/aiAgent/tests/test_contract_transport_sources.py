"""Current wire, failure boundaries and source ingestion; no network in these tests."""

import copy
import json
from dataclasses import replace
from types import SimpleNamespace

import pytest

from config.settings import ROOT, CLIProxyConfig
from rag.llm.context.builder import prepare_context
from rag.llm.contracts.errors import ContractIssue, LLMError
from rag.llm.evidence.catalogue import expand_proofs
from rag.llm.evidence.ledger import bind_ledger, build_ledger
from rag.llm.generation.answering import generate_answer
from rag.llm.providers.cliproxy_client import CLIProxyClient
from rag.llm.validation.answer import schema_errors
from rag.llm.validation.proof import evaluate_proof
from rag.prompts.schemas.proof import WIRE_LEDGER_SCHEMA, WIRE_PROOF_SCHEMA
from rag.utils.files import digest
from tests.test_generic_proof_engine import context, entry, prepared, proof


def wire_proof(canonical):
    graph = copy.deepcopy(canonical)
    root = next(n for n in graph["nodes"] if n["key"] == graph["root"])
    graph["nodes"].remove(root)
    graph.pop("root")
    graph.pop("target")
    graph["root_node"] = {k: v for k, v in root.items() if k not in {"key", "text"}}
    return graph


def selected_entry(ctx, *, modality="ASSERTED", fact_id="U1"):
    value = entry(modality=modality, fact_id=fact_id)
    return {
        **{k: v for k, v in value.items() if k not in {"quote", "value", "correction_quote"}},
        "source_mode": "STATEMENT",
    }


def test_backend_materializes_ledger_from_selected_statement_only():
    ctx = context()
    selection = selected_entry(ctx)
    assert not schema_errors([selection], WIRE_LEDGER_SCHEMA)
    value = {"fact_ledger": [selection]}
    bound, errors = bind_ledger(value, ctx)
    assert not errors
    row = bound["user_context"]["fact_ledger"][0]
    assert row["quote"] == row["value"] == ctx["user_context"]["statements"][0]["text"]
    assert "source_mode" not in value["fact_ledger"][0]


@pytest.mark.parametrize("fact_id", ["invented", "U2"])
def test_selection_cannot_cross_registry_or_item(fact_id):
    ctx = context()
    ctx["request"]["items"].append({"id": "I2", "anchor": "Mặt hàng B"})
    ctx["question"] = "Mặt hàng A có x. Mặt hàng B có y."
    ctx["user_context"]["statements"][1]["text"] = "Mặt hàng B có y"
    assert build_ledger([selected_entry(ctx, fact_id=fact_id)], ctx)[1]


def test_legacy_fuzzy_quote_cannot_invent_or_reverse_a_fact():
    ctx = context()
    bad = {**entry(), "value": "không có thuộc tính x", "quote": "Mặt hàng A có thuộc tính x."}
    assert build_ledger([bad], ctx)[1]
    bad["quote"] = "not specified"
    assert build_ledger([bad], ctx)[1]


def test_unknown_selection_has_no_fabricated_value():
    ctx = context()
    rows, errors = build_ledger([selected_entry(ctx, modality="UNKNOWN", fact_id="")], ctx)
    assert not errors and rows[0]["state"] == "UNKNOWN" and rows[0]["value"] == ""


def test_consumer_root_binds_without_echo_and_keeps_premise_validation():
    ctx = prepared()
    graph = wire_proof(proof(ctx))
    assert not schema_errors(graph, WIRE_PROOF_SCHEMA)
    payload, errors = expand_proofs(
        {"claims": [{"proof_key": "p"}], "proof_catalogue": [{"key": "p", "proof": graph}]}
    )
    assert not errors
    result, errors = evaluate_proof(
        payload["claims"][0]["proof"], ctx, target="Điều kiện đang kiểm tra", product=True
    )
    assert not errors and result["state"] == "PROVEN"
    malformed = copy.deepcopy(payload["claims"][0]["proof"])
    malformed["nodes"][0]["evidence_ids"] = ["invented"]
    assert evaluate_proof(malformed, ctx, target="Điều kiện đang kiểm tra", product=True)[1]


def test_consumer_graph_cannot_be_reused_to_relabel_distinct_claims():
    ctx = prepared()
    payload, errors = expand_proofs(
        {
            "claims": [{"text": "A", "proof_key": "p"}, {"text": "B", "proof_key": "p"}],
            "proof_catalogue": [{"key": "p", "proof": wire_proof(proof(ctx))}],
        }
    )
    assert len(errors) == 2 and all(c["proof"] is None for c in payload["claims"])


def test_legacy_target_mismatch_remains_rejected():
    ctx = prepared()
    assert evaluate_proof(proof(ctx), ctx, target="Một mệnh đề mạnh hơn")[1]


def test_diagnostic_survives_copy_with_structured_metadata():
    issue = ContractIssue(
        "invalid", code="LEDGER_INVALID", path="fact_ledger/0", expected=["U1"], actual="U2"
    )
    cloned = copy.deepcopy(issue)
    assert cloned.diagnostic == issue.diagnostic and cloned is not issue
    cloned.diagnostic["expected"].append("U3")
    assert issue.diagnostic["expected"] == ["U1"]


@pytest.mark.parametrize(
    "error_code",
    [
        None,
        "transport_timeout",
        "transport_connection_error",
        "RESOURCE_EXHAUSTED",
        "rate_limit_exceeded",
    ],
)
def test_transport_retries_twice_then_succeeds_same_payload(monkeypatch, error_code):
    client = CLIProxyClient(CLIProxyConfig(api_key="fixture"))
    calls, sleeps = [], []

    def request(path, payload):
        calls.append((path, copy.deepcopy(payload)))
        if len(calls) < 3:
            raise LLMError(503, payload["model"], error_code=error_code, provider="cliproxyapi")
        return {"choices": [{"message": {"content": "{}"}, "finish_reason": "stop"}]}

    monkeypatch.setattr(client, "_request_once", request)
    monkeypatch.setattr("rag.llm.providers.cliproxy_client.time.sleep", sleeps.append)
    result = client.complete([], {})
    assert len(calls) == 3 and sleeps == [2, 5] and calls[0] == calls[1] == calls[2]
    assert result["transport_retries"] == 2 and not result["fallback_used"]


@pytest.mark.parametrize("status", [400, 401, 403, 429, 500, 502])
def test_transport_does_not_retry_nontransient_or_other_http_errors(monkeypatch, status):
    client = CLIProxyClient(CLIProxyConfig(api_key="fixture"))
    calls = []

    def request(path, payload):
        calls.append(payload)
        raise LLMError(status, payload["model"], provider="cliproxyapi")

    monkeypatch.setattr(client, "_request_once", request)
    monkeypatch.setattr(
        "rag.llm.providers.cliproxy_client.time.sleep", lambda _: pytest.fail("unexpected wait")
    )
    with pytest.raises(LLMError):
        client.complete([], {})
    assert len(calls) == 1


def test_retry_exhaustion_retains_all_transport_failures(monkeypatch):
    client = CLIProxyClient(CLIProxyConfig(api_key="fixture"))

    def fail(path, payload):
        raise LLMError(
            503, payload["model"], error_code="transport_timeout", provider="cliproxyapi"
        )

    monkeypatch.setattr(client, "_request_once", fail)
    monkeypatch.setattr("rag.llm.providers.cliproxy_client.time.sleep", lambda _: None)
    with pytest.raises(LLMError) as error:
        client.complete([], {})
    assert len(error.value.transport_attempts) == 3
    assert error.value.transport_attempts[-1]["retry_delay_seconds"] == 0


@pytest.mark.parametrize("retries", [-1, 3, True, 1.5])
def test_retry_configuration_is_bounded(retries):
    with pytest.raises(ValueError):
        replace(CLIProxyConfig(api_key="fixture"), transport_retries=retries)


@pytest.mark.parametrize("invalid_first", [False, True])
def test_explain_wire_reaches_review_and_repairs_invalid_fact_without_target_copying(invalid_first):
    question = "Giải thích quy định hồ sơ."
    request = {
        "items": [],
        "objectives": [
            {
                "id": "G1",
                "kind": "EXPLAIN",
                "level": 0,
                "item_ids": [],
                "anchor": question,
                "required": True,
            }
        ],
    }
    cfg = SimpleNamespace(
        max_input_chars=None,
        max_context_chars=None,
        use_model_token_limits=True,
        model="gemini-3.5-flash-lite",
    )
    ctx = prepare_context(
        question,
        {
            "matches": [
                {
                    "id": "rule",
                    "source_text": "Hồ sơ gồm tài liệu kỹ thuật.",
                    "chunk_type": "legal_clause",
                }
            ],
            "query_plan": {"request": request, "query_hash": digest(question)},
        },
        "auto",
        cfg,
    )
    eid = ctx["sources"][0]["evidence_id"]
    from rag.llm.evidence.conditions import condition_span_registry

    pid = next(iter(condition_span_registry(ctx["sources"])))
    root = {
        "operator": "ATOM",
        "kind": "LEGAL_RULE",
        "attribute": "",
        "item_ids": [],
        "children": [],
        "evidence_ids": [eid],
        "condition_ids": [pid],
        "ledger_ids": [],
        "assessment": "PROVEN",
        "cause": "NONE",
        "comparison": {
            "left": "",
            "right": "",
            "left_unit": "",
            "right_unit": "",
            "operator": "NONE",
        },
    }
    graph = {
        "root_node": root,
        "nodes": [],
        "decomposition_review": "FAITHFUL_COMPLETE",
        "ledger_review": "CONSISTENT",
    }
    draft = {
        "results": [
            {
                "objective_id": "G1",
                "item_id": "",
                "status": "ANSWERED",
                "code": "",
                "candidate_codes": [],
                "claims": [
                    {
                        "kind": "LEGAL_ANALYSIS",
                        "text": "Hồ sơ gồm tài liệu kỹ thuật.",
                        "evidence_ids": [eid],
                        "fact_ids": [],
                        "proof_key": "p1",
                    }
                ],
                "clarifications": [],
                "missing_legal_evidence": [],
            }
        ],
        "fact_ledger": [],
        "evidence_gaps": [],
        "proof_catalogue": [{"key": "p1", "proof": graph}],
    }
    review = {
        "reviews": [],
        "analysis_reviews": {
            "R1": {
                "checks": {
                    "0": {
                        "assessment": "REFERENCE",
                        "evidence_ids": [eid],
                        "fact_ids": [],
                        "reason": "Nguồn mô tả đúng hồ sơ.",
                        "proof_key": "p2",
                    }
                }
            }
        },
        "proof_catalogue": [{"key": "p2", "proof": graph}],
    }
    def semantic_value(value):
        if isinstance(value, list):
            return [semantic_value(child) for child in value]
        if isinstance(value, dict):
            return {key: semantic_value(child) for key, child in value.items()
                    if key not in {"fact_ledger", "proof_catalogue", "proof_key", "reason_proof_key"}}
        return value

    draft, review = semantic_value(draft), semantic_value(review)
    calls = []
    responses = [draft, review]
    if invalid_first:
        broken = copy.deepcopy(draft)
        claim = copy.deepcopy(broken["results"][0]["claims"][0])
        claim["kind"] = "PRODUCT_FACT"  # schema-valid, but no asserted fact supports it
        broken["results"][0]["claims"].append(claim)
        responses.insert(0, broken)

    class Client:
        config = cfg

        def complete(self, messages, schema, **kwargs):
            result = responses[len(calls)]
            calls.append(schema)
            assert not schema_errors(result, schema)
            return {
                "content": json.dumps(result, ensure_ascii=False),
                "finish_reason": "stop",
                "model": cfg.model,
                "usage": {},
                "provider": "fixture",
                "elapsed_ms": 0,
            }

    result = generate_answer(ctx, Client())
    assert len(calls) == len(responses), result
    assert (
        result["validation"]["task_completion"]
        and result["validation"]["review_execution_status"] == "COMPLETED"
    ), result


def test_registered_documents_keep_raw_quotes_and_historical_validity():
    from rag.ingestion.legal_documents import legal_document_bundle
    from rag.ingestion.sources import SOURCE_TYPES, source_manifest

    specs = source_manifest(ROOT)["legal_documents"]
    assert len(specs) == 3 and "technical_standard_item" in SOURCE_TYPES
    for spec in specs:
        rows, nodes, edges = legal_document_bundle(ROOT, spec)
        assert rows and len(rows) == len(nodes)
        assert all(r["code"] is None and r["role"] == "evidence" for r in rows)
        assert all(r["locator"]["sha256"] == spec["sha256"] for r in rows)
        assert all(
            e["source"] in {r["id"] for r in rows} and e["target"] in {r["id"] for r in rows}
            for e in edges
        )
        if spec["dataset"] == "tt02_btttt":
            assert all(
                r["legal_status"] == "EXPIRED" and r["effective_to"] == "2025-12-31" for r in rows
            )


def test_vehicle_standard_group_is_inherited_without_becoming_a_tariff_candidate():
    from rag.graph.context import GraphContext
    from rag.ingestion.legal_documents import legal_document_bundle
    from rag.ingestion.sources import source_manifest

    spec = next(s for s in source_manifest(ROOT)["legal_documents"] if s["key"] == "vbhn05")
    rows, nodes, edges = legal_document_bundle(ROOT, spec)
    tractor = next(r for r in rows if "Ô tô đầu kéo" in r["source_text"])
    view = GraphContext(rows, nodes, edges).source_view(tractor)
    assert tractor["code"] is None
    assert any("QCVN 09:2024/BGTVT" in c["text"] for c in view["citations"])
    assert any("Lĩnh vực phương tiện giao thông đường bộ" in c["text"] for c in view["citations"])


def test_docx_line_breaks_preserve_separate_codes():
    from xml.etree import ElementTree

    from rag.ingestion.legal_documents import paragraph_text

    xml = '<w:p xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:r><w:t>8517.13.00</w:t><w:br/><w:t>8517.14.00</w:t></w:r></w:p>'
    assert paragraph_text(ElementTree.fromstring(xml)) == "8517.13.00\n8517.14.00"


def test_consumer_graph_cannot_be_reused_after_canonical_replay():
    ctx = prepared()
    payload, errors = expand_proofs(
        {
            "claims": [{"proof_key": "p"}],
            "proof_catalogue": [{"key": "p", "proof": wire_proof(proof(ctx))}],
        }
    )
    assert not errors
    canonical = payload["claims"][0]["proof"]
    _, errors = expand_proofs(
        {
            "claims": [{"proof_key": "p"}, {"proof_key": "p"}],
            "proof_catalogue": [{"key": "p", "proof": canonical}],
        }
    )
    assert len(errors) == 2


def test_audit_distinguishes_local_docx_from_reviewed_pdf_provenance():
    from rag.ingestion.audit import audit

    report = audit()
    assert report["legal_verification"] == "MIXED_PDF_REVIEW_AND_HASH_BOUND_LOCAL_DOCX"
    assert report["docx_verification"] == "RAW_DOCX_HASH_BOUND_NOT_PDF_VERIFIED"
