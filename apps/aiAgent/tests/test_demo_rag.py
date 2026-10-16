"""Terminal conversations exercise the runtime context/validation without network calls."""

import json
import os
from collections import deque
from contextlib import nullcontext
from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from config.settings import DEFAULT_MODEL_PRESET, MODEL_PRESETS, GroqConfig, RAGGenerationConfig
from rag.api import cli as demoRAG
from rag.graph.context import GraphContext
from rag.llm.groq_client import GroqError
from rag.prompts.schemas import ANSWER_SCHEMA, PRODUCT_REVIEW_SCHEMA


def response(status="ANSWERED"):
    missing = status == "MISSING_PRODUCT_INFO"
    return {
        "status": status,
        "answer": "Bạn cần làm rõ loại hồ sơ."
        if missing
        else "Chỉ dẫn của AI [S1] [S2] [S3]."
        if status == "RECOMMENDATION"
        else "Chỉ dẫn của AI [S1].",
        "suggested_hs_code": "71131990" if status == "RECOMMENDATION" else "",
        "alternatives": [],
        "citations": []
        if missing
        else [
            {"label": label, "quote": "Nội dung nguồn"}
            for label in (["S1", "S2", "S3"] if status == "RECOMMENDATION" else ["S1"])
        ],
        "missing_information": ["Loại hồ sơ hoặc vật liệu hàng hóa?"] if missing else [],
        "missing_legal_evidence": [],
    }


def conversation(
    inputs,
    answers,
    *,
    max_chars=8000,
    advisory_intent="qa",
    debug=False,
    retrieval_timings=None,
    review_answers=None,
    selectable=False,
    model_selections=None,
    token_limits=False,
):
    inputs, answers = iter(inputs), deque(answers)
    review_answers = deque(review_answers) if review_answers is not None else None
    queries, payloads = [], []
    output: list[str] = []
    source = {
        "id": "test-source",
        "source_text": "Nội dung nguồn",
        "code": "71131990",
        "locator": {"document": "TT31.pdf", "physical_page": 7, "printed_page": "5"},
    }
    heading = {**source, "id": "heading", "code": "7113"}
    subheading = {**source, "id": "subheading", "code": "711319"}
    graph = GraphContext(
        [source, heading, subheading],
        [],
        [
            {"source": "heading", "target": "subheading", "relation": "CONTAINS"},
            {"source": "subheading", "target": source["id"], "relation": "CONTAINS"},
        ],
    )

    def search(query, *, intent):
        queries.append((query, intent))
        return {
            "matches": [source],
            "hs_candidates": [source],
            "semantic_intent": {"status": "ADVISORY", "intent": advisory_intent},
            "timings": retrieval_timings,
        }

    def complete(messages, schema, **kwargs):
        if schema is PRODUCT_REVIEW_SCHEMA:
            if review_answers is not None:
                return {
                    "content": json.dumps(review_answers.popleft()),
                    "finish_reason": "stop",
                    "model": "fallback-model",
                }
            payload = json.loads(messages[1]["content"])
            question = payload["question"]
            return {
                "content": json.dumps(
                    {
                        "status": "SUPPORTED",
                        "reason": "Dữ kiện người dùng đáp ứng các điều kiện trong nguồn được cấp.",
                        "product_facts": [{"fact": "User facts", "user_quote": question}],
                        "condition_checks": [
                            {
                                "source_label": source["label"],
                                "source_quote": source["text"],
                                "assessment": "SATISFIED",
                                "product_fact_indices": [0],
                            }
                            for source in payload["sources"]
                        ],
                        "missing_information": [],
                        "missing_legal_evidence": [],
                    }
                ),
                "finish_reason": "stop",
                "model": "fallback-model",
            }
        payloads.append(json.loads(messages[1]["content"]))
        item = answers.popleft()
        if isinstance(item, Exception):
            raise item
        return {
            "content": json.dumps(item),
            "finish_reason": "stop",
            "model": "fallback-model",
            "fallback_used": True,
        }

    def read(_):
        try:
            item = next(inputs)
        except StopIteration:
            raise EOFError from None
        if isinstance(item, BaseException):
            raise item
        return item

    client = SimpleNamespace(
        config=GroqConfig(keys=("fixture",), max_input_chars=max_chars), complete=complete
    )
    if token_limits:
        client.config = RAGGenerationConfig(
            model=MODEL_PRESETS[DEFAULT_MODEL_PRESET].model,
            fallback_model="gpt-oss-120b-medium",
            max_input_chars=None,
            max_context_chars=None,
            use_model_token_limits=True,
        )
    if selectable:
        client.model_preset = DEFAULT_MODEL_PRESET
        client.config = replace(client.config, model=MODEL_PRESETS[DEFAULT_MODEL_PRESET].model)

        def select_model(key):
            if model_selections is not None:
                model_selections.append(key)
            client.model_preset = key
            client.config = replace(client.config, model=MODEL_PRESETS[key].model)

        client.select_model = select_model

    def keep_fixture_decision(_context, answer, _client, **kwargs):
        return answer, {
            "valid": True,
            "review": {"reason": "Giữ phản hồi giả lập để kiểm tra giao diện terminal."},
            "model": "fixture-decision-review-model",
            "errors": [],
        }

    with patch("rag.llm.answering.review_decision", side_effect=keep_fixture_decision):
        demoRAG.run_console(
            SimpleNamespace(routed_search=search),
            client,
            graph,
            read=read,
            write=output.append,
            debug=debug,
        )
    return queries, payloads, "\n".join(output)


def test_common_flow_answers_qa_and_hs_without_user_mode_selection():
    queries, payloads, output = conversation(
        ["Hồ sơ nào cần nộp?", "Hồ sơ phân tích hàng hóa", "/new", "Nhẫn bằng vàng", "/exit"],
        [response("MISSING_PRODUCT_INFO"), response(), response("RECOMMENDATION")],
    )
    assert [intent for _, intent in queries] == ["auto", "auto", "auto"]
    assert [payload["task"] for payload in payloads] == ["auto", "auto", "auto"]
    # A QA classifier hint does not prevent a supported HS recommendation.
    assert payloads[2]["intent_advice"]["intent"] == "qa"
    assert (
        queries[1][0]
        == "Hồ sơ nào cần nộp?\n\nThông tin người dùng bổ sung ở lượt 2: Hồ sơ phân tích hàng hóa"
    )
    assert queries[2][0] == "Nhẫn bằng vàng"
    assert "Chỉ dẫn của AI" not in payloads[2]["question"]
    assert "Hồ sơ" not in payloads[2]["question"]
    assert "Thông tin bạn cần bổ sung:" in output
    assert "Mã HS đề xuất: 71131990" in output
    assert "TT31.pdf | trang PDF 7 | trang in 5" in output
    assert "/sources để xem trích đoạn" in output
    assert "Nội dung nguồn" not in output
    assert "ID: test-source" not in output
    assert "fallback-model" not in output


def test_citation_display_preserves_all_pdf_pages():
    output: list[str] = []
    context = {
        "sources": [
            {
                "label": "S1",
                "id": "source",
                "locator": {
                    "document": "TT31.pdf",
                    "physical_page": 75,
                    "physical_pages": [75, 76],
                },
            }
        ]
    }
    generated = {
        "generation": {"model": "fixture"},
        "validation": {"valid": True},
        "answer": response(),
    }
    demoRAG.show_answer(context, generated, 0, write=output.append)
    assert "TT31.pdf | trang PDF 75, 76" in "\n".join(output)


def test_new_question_discards_previous_supplements():
    queries, _, _ = conversation(
        ["Phiên A", "Dữ kiện chỉ thuộc A", "/new", "Phiên B"],
        [response(), response(), response()],
    )
    assert queries[-1][0] == "Phiên B"


def test_provider_failure_preserves_question_and_context_for_retry():
    queries, _, output = conversation(
        ["Câu hỏi gốc", "Thông tin bổ sung", "/details", "/retry"],
        [response("MISSING_PRODUCT_INFO"), GroqError(429, "fixture-model", 12), response()],
    )
    assert queries[1] == queries[2]
    assert "Thông tin bổ sung" in queries[2][0]
    assert "HTTP: 429" in output and "12s" in output
    assert "Thông tin đã được giữ lại" in output


def test_invalid_input_never_reaches_retrieval_and_does_not_poison_retry():
    queries, _, output = conversation(
        [" ", "/retry", "/unknown", "Câu hỏi", "x" * 8001, "/retry"],
        [response(), response()],
    )
    assert queries == [("Câu hỏi", "auto"), ("Câu hỏi", "auto")]
    assert "vượt giới hạn 8000" in output


def test_invalid_llm_answer_is_not_presented_as_a_result():
    invalid = {
        **response(),
        "answer": "Nội dung không được xác thực [S1]",
        "citations": [{"label": "S1", "quote": "Trích dẫn bịa"}],
    }
    queries, _, output = conversation(["Hỏi một câu", "/retry"], [invalid, invalid, response()])
    assert len(queries) == 2
    assert "Trạng thái: Cần thẩm định thêm" in output
    assert "Trích đoạn không khớp nguyên văn nguồn" in output
    assert "Nội dung không được xác thực" not in output
    assert "Trích dẫn bịa" not in output
    assert "AI: Chỉ dẫn của AI [S1]." in output


@pytest.mark.parametrize("end", [EOFError(), KeyboardInterrupt()])
def test_end_of_input_and_interrupt_exit_cleanly(end):
    queries, _, _ = conversation([end], [])
    assert queries == []


def test_missing_sources_skip_main_generation_and_only_review_decision():
    output: list[str] = []
    inputs = iter(["Một câu hỏi", "/exit"])
    calls = []

    def unavailable_review(_messages, schema, **kwargs):
        calls.append(schema)
        assert schema is not ANSWER_SCHEMA
        assert schema is not PRODUCT_REVIEW_SCHEMA
        raise GroqError(503, "fixture-review-model")

    demoRAG.run_console(
        SimpleNamespace(routed_search=lambda *args, **kwargs: {"matches": []}),
        SimpleNamespace(config=GroqConfig(keys=("fixture",)), complete=unavailable_review),
        None,
        read=lambda _: next(inputs),
        write=output.append,
    )
    assert len(calls) == 1
    assert not any("Mã HS đề xuất:" in line for line in output)
    assert not any("Thông tin bạn cần bổ sung" in line for line in output)
    assert not any("Không gọi LLM" in line for line in output)


def test_help_does_not_initialize_runtime_or_ask_for_mode(monkeypatch, capsys):
    monkeypatch.setattr(demoRAG, "connect", lambda: pytest.fail("Must not connect for help"))
    with pytest.raises(SystemExit) as exc:
        demoRAG.main(["--help"])
    assert exc.value.code == 0
    output = capsys.readouterr().out
    assert "--task" not in output
    assert "--model" in output
    assert DEFAULT_MODEL_PRESET in output


@pytest.mark.parametrize("choice", [None, "3.8-high", "3.5-lite-high", "120b"])
def test_startup_selects_default_or_explicit_model_without_interactive_menu(monkeypatch, choice):
    selected: list[str] = []

    def client_factory(*, model_preset):
        selected.append(model_preset)
        return SimpleNamespace(
            config=SimpleNamespace(model=MODEL_PRESETS[model_preset].model, fallback_models=()),
            model_preset=model_preset,
        )

    conn = SimpleNamespace(execute=lambda _: None)
    retriever = SimpleNamespace(unified_policy={"active": True})
    conversations = []
    monkeypatch.setattr(demoRAG, "RAGClient", client_factory)
    monkeypatch.setattr(demoRAG, "connect", lambda: nullcontext(conn))
    monkeypatch.setattr(demoRAG, "Embedder", lambda: object())
    monkeypatch.setattr(demoRAG, "Retriever", lambda *_: retriever)
    monkeypatch.setattr(demoRAG, "load_generation_graph", lambda _: None)
    monkeypatch.setattr(
        demoRAG,
        "run_console",
        lambda _retriever, client, _graph, **kwargs: conversations.append(client.model_preset),
    )
    assert demoRAG.main([] if choice is None else ["--model", choice]) == 0
    expected = choice or DEFAULT_MODEL_PRESET
    assert selected == conversations == [expected]


def test_invalid_startup_model_is_rejected_before_initializing_runtime(monkeypatch, capsys):
    monkeypatch.setattr(demoRAG, "RAGClient", lambda **_: pytest.fail("Unexpected client"))
    monkeypatch.setattr(demoRAG, "connect", lambda: pytest.fail("Unexpected DB connection"))
    with pytest.raises(SystemExit) as raised:
        demoRAG.main(["--model", "unknown"])
    assert raised.value.code == 2
    assert "invalid choice" in capsys.readouterr().err


def test_model_commands_list_and_switch_without_retrieval_or_generation():
    selected: list[str] = []
    queries, payloads, output = conversation(
        ["/model", "/model 1", "/model 120b", "/model 2", "/model"],
        [],
        selectable=True,
        model_selections=selected,
    )
    assert queries == payloads == []
    assert selected == ["3.8-high", "120b", "3.5-lite-high"]
    assert "Model: " + MODEL_PRESETS[DEFAULT_MODEL_PRESET].label in output
    assert "Model hiện tại: " + MODEL_PRESETS[DEFAULT_MODEL_PRESET].label in output
    assert "1. " + MODEL_PRESETS["3.8-high"].label in output
    assert "2. " + MODEL_PRESETS["3.5-lite-high"].label in output
    assert "3. " + MODEL_PRESETS["120b"].label in output
    assert "đang dùng, mặc định" in output


def test_model_switch_preserves_user_facts_and_clears_previous_result():
    selected: list[str] = []
    queries, payloads, output = conversation(
        ["Câu hỏi gốc", "Dữ kiện đã xác nhận", "/model 1", "/sources", "/details", "/retry"],
        [response("MISSING_PRODUCT_INFO"), response(), response()],
        selectable=True,
        model_selections=selected,
    )
    assert selected == ["3.8-high"]
    assert queries[1] == queries[2]
    assert "Dữ kiện đã xác nhận" in queries[2][0]
    assert payloads[1]["question"] == payloads[2]["question"]
    assert output.count("Chưa có kết quả.") == 2
    assert "Nội dung nguồn" not in output
    assert "Thông tin kỹ thuật" not in output


def test_invalid_model_choice_preserves_current_model_and_sources():
    selected: list[str] = []
    queries, payloads, output = conversation(
        ["Câu hỏi", "/model unknown", "/sources", "/model"],
        [response()],
        selectable=True,
        model_selections=selected,
    )
    assert len(queries) == len(payloads) == 1
    assert selected == []
    assert "Model không hợp lệ" in output
    assert "Model hiện tại: " + MODEL_PRESETS[DEFAULT_MODEL_PRESET].label in output
    assert "Nội dung nguồn" in output


def test_model_commands_handle_clients_without_selector_gracefully():
    queries, payloads, output = conversation(["/model", "/model 1"], [])
    assert queries == payloads == []
    assert "Model hiện tại:" in output
    assert "Phiên này chưa hỗ trợ đổi model" in output


@pytest.mark.parametrize("hint", ["product", "mixed_or_uncertain", None])
def test_qa_answers_remain_possible_when_intent_is_wrong_or_unclear(hint):
    _, payloads, output = conversation(
        ["Hệ thống HS gồm những gì?"], [response()], advisory_intent=hint
    )
    assert payloads[0]["task"] == "auto"
    assert "AI: Chỉ dẫn của AI [S1]." in output
    assert "Trạng thái: Đã trả lời" in output


def test_source_and_detail_commands_reveal_evidence_without_a_new_request():
    queries, payloads, output = conversation(["Câu hỏi", "/sources", "/details"], [response()])
    assert len(queries) == len(payloads) == 1
    assert "Trích dẫn nguồn" in output
    assert "Nội dung nguồn" in output
    assert "ID: test-source" in output
    assert "Model: fallback-model — đã dùng model dự phòng" in output
    assert "Nguồn gửi LLM:" in output
    assert "Ngữ cảnh gửi LLM:" in output
    assert "Ứng viên HS trong ngữ cảnh:" in output


def test_new_question_clears_evidence_and_diagnostics():
    queries, _, output = conversation(["Phiên A", "/new", "/sources", "/details"], [response()])
    assert len(queries) == 1
    assert output.count("Chưa có kết quả.") == 2
    assert "Nội dung nguồn" not in output
    assert "Thông tin kỹ thuật" not in output


def test_failed_new_request_does_not_reveal_previous_sources():
    queries, _, output = conversation(
        ["Câu hỏi", "Bổ sung", "/sources", "/details"],
        [response(), GroqError(503, "unavailable-model")],
    )
    assert len(queries) == 2
    assert "Chưa có câu trả lời hợp lệ để hiển thị nguồn" in output
    assert "Nội dung nguồn" not in output
    assert "HTTP: 503" in output


def test_invalid_answer_stays_hidden_when_source_and_detail_commands_are_used():
    invalid = {
        **response(),
        "answer": "Kết luận chưa xác thực [S1]",
        "citations": [{"label": "S1", "quote": "Trích đoạn bịa"}],
    }
    queries, _, output = conversation(["Câu hỏi", "/sources", "/details"], [invalid, invalid])
    assert len(queries) == 1
    assert "Kết luận chưa xác thực" not in output
    assert "Trích đoạn bịa" not in output
    assert "Trạng thái: Cần thẩm định thêm" in output
    assert "Nội dung nguồn" in output
    assert "ID: test-source" in output
    assert "Bước cần kiểm tra: generation_validation" in output
    assert "Mã chẩn đoán: ANSWER_VALIDATION_FAILED" in output
    assert "Trích đoạn không khớp nguyên văn nguồn" in output


def test_clarification_and_legal_gaps_are_not_repeated_in_the_same_response():
    question = "Vật liệu hàng hóa là gì?"
    gap = "Chưa có mô tả pháp lý của nhánh được xét."
    _, _, output = conversation(
        ["Câu hỏi", "Vật liệu đã xác nhận"],
        [
            {
                **response("MISSING_PRODUCT_INFO"),
                "answer": question,
                "missing_information": [question],
            },
            {
                **response(),
                "status": "INSUFFICIENT_LEGAL_EVIDENCE",
                "answer": gap,
                "citations": [],
                "missing_legal_evidence": [gap],
            },
        ],
    )
    assert output.count(question) == 1
    assert output.count(gap) == 1


def test_narrow_terminal_wraps_answer_and_all_source_pages(monkeypatch):
    monkeypatch.setattr(demoRAG.shutil, "get_terminal_size", lambda _: os.terminal_size((42, 24)))
    context = {
        "sources": [
            {
                "label": "S1",
                "id": "source",
                "locator": {"document": "Tài liệu pháp lý.pdf", "physical_pages": [75, 76, 77]},
            }
        ]
    }
    text = "Câu trả lời có căn cứ từ tài liệu pháp lý được cung cấp và giữ đúng vị trí nguồn [S1]."
    generated = {
        "generation": {"model": "fixture"},
        "validation": {"valid": True},
        "answer": {**response(), "answer": text},
    }
    output: list[str] = []
    demoRAG.show_answer(context, generated, 0.1, write=output.append)
    lines = "\n".join(output).splitlines()
    assert max(map(len, lines)) <= 40
    assert "75, 76, 77" in " ".join(line.strip() for line in lines)
    assert text in " ".join(line.strip() for line in lines)


@pytest.mark.parametrize("debug", [False, True])
def test_runtime_logs_are_hidden_by_default_and_available_in_debug(debug, capsys):
    output: list[str] = []
    inputs = iter(["Câu hỏi", "/exit"])

    def search(*args, **kwargs):
        print("Reranker diagnostic log")
        return {"matches": []}

    def unavailable_review(*args, **kwargs):
        raise GroqError(503, "fixture-review-model")

    demoRAG.run_console(
        SimpleNamespace(routed_search=search),
        SimpleNamespace(config=GroqConfig(keys=("fixture",)), complete=unavailable_review),
        None,
        read=lambda _: next(inputs),
        write=output.append,
        debug=debug,
    )
    assert ("Reranker diagnostic log" in capsys.readouterr().out) is debug
    assert ("Thông tin kỹ thuật" in "\n".join(output)) is debug


def test_debug_mode_keeps_quotes_and_model_information_accessible():
    _, _, output = conversation(["Câu hỏi"], [response()], debug=True)
    assert "Nội dung nguồn" in output
    assert "fallback-model" in output
    assert "Thông tin kỹ thuật" in output


def blocked_result():
    context = {
        "allowed_hs_codes": ["85171300"],
        "sources": [
            {
                "label": "S1",
                "id": "smartphone-source",
                "text": "Điện thoại thông minh (smartphones)",
                "locator": {"document": "TT31.pdf", "physical_pages": [7, 8]},
            }
        ],
        "retrieval_timings": {"retrieval_ms": 1234, "reranking_ms": 250},
    }
    generated = {
        "answer": {
            **response("REQUIRES_REVIEW"),
            "answer": "Ứng viên cần kiểm tra thêm trước khi kết luận.",
            "citations": [],
        },
        "generation": {
            "model": "fixture",
            "product_review": {"valid": False, "review": {"quote": "Trích đoạn bịa"}},
        },
        "validation": {"valid": True},
        "diagnostics": {
            "stage": "product_review",
            "code": "PRODUCT_FACTS_NOT_ESTABLISHED",
            "reasons": ["Chưa xác nhận loại hàng thực tế và chức năng liên lạc."],
            "candidate_hs_code": "85171300",
            "source_labels": ["S1", "unknown-source"],
        },
        "timings": {"llm_ms": 4200, "validation_ms": 2},
    }
    return context, generated


def test_blocked_candidate_exposes_reason_and_real_sources_without_recommending():
    context, generated = blocked_result()
    output: list[str] = []
    demoRAG.show_answer(context, generated, 5.686, write=output.append)
    text = "\n".join(output)
    assert "Ứng viên đang kiểm tra (chưa kết luận): 85171300" in text
    assert "Chưa xác nhận loại hàng thực tế và chức năng liên lạc." in text
    assert "TT31.pdf | trang PDF 7, 8" in text
    assert "Nguồn (1)" in text
    assert "Mã HS đề xuất:" not in text
    assert "Điện thoại thông minh" not in text
    demoRAG.show_sources(context, generated, write=output.append)
    text = "\n".join(output)
    assert "Điện thoại thông minh (smartphones)" in text
    assert "ID: smartphone-source" in text
    assert "Trích đoạn bịa" not in text
    assert "unknown-source" not in text
    demoRAG.show_details(context, generated, 5.686, write=output.append)
    text = "\n".join(output)
    assert "Bước cần kiểm tra: product_review" in text
    assert "Mã chẩn đoán: PRODUCT_FACTS_NOT_ESTABLISHED" in text
    assert "Trích đoạn bịa" not in text


@pytest.mark.parametrize("invalid", [True, False])
def test_diagnostics_cannot_expose_invalid_answers_or_absent_candidates(invalid):
    context, generated = blocked_result()
    if invalid:
        generated["validation"] = {"valid": False, "errors": ["Không đạt"]}
    else:
        generated["diagnostics"]["candidate_hs_code"] = "99999999"
        generated["diagnostics"]["source_labels"] = ["unknown-source"]
    output: list[str] = []
    demoRAG.show_answer(context, generated, 5, write=output.append)
    demoRAG.show_sources(context, generated, write=output.append)
    text = "\n".join(output)
    assert "Ứng viên đang kiểm tra" not in text
    assert "smartphone-source" not in text
    assert "Điện thoại thông minh" not in text
    if invalid:
        assert "Chưa xác nhận loại hàng thực tế" not in text


def test_diagnostic_reason_is_not_repeated_when_already_in_answer():
    context, generated = blocked_result()
    generated["answer"]["answer"] = generated["diagnostics"]["reasons"][0]
    output: list[str] = []
    demoRAG.show_answer(context, generated, 5, write=output.append)
    assert "\n".join(output).count(generated["diagnostics"]["reasons"][0]) == 1


@pytest.mark.parametrize("debug", [False, True])
def test_stage_measurements_are_independent_and_not_duplicated(debug):
    context, generated = blocked_result()
    output: list[str] = []
    demoRAG.show_answer(context, generated, 5.686, write=output.append, debug=debug)
    text = "\n".join(output)
    for value in ("Retrieval 1.23s", "Reranking 250.0ms", "LLM 4.20s", "Validation 2.0ms"):
        assert text.count(value) == 1
    assert text.count("Đo từng bước:") == 1


def test_unmeasured_stages_are_not_reported_as_zero():
    context, generated = blocked_result()
    context["retrieval_timings"] = {"retrieval_ms": 0, "reranking_ms": float("nan")}
    generated.pop("timings")
    output: list[str] = []
    demoRAG.show_answer(context, generated, 1, write=output.append)
    text = "\n".join(output)
    assert "Retrieval 0.0ms" in text
    for stage in ("Reranking", "LLM", "Validation"):
        assert f"{stage} chưa đo" in text
        assert f"{stage} 0" not in text


def test_details_attribute_llm_time_to_answer_review_and_failed_models():
    context, generated = blocked_result()
    generated["timings"].update(answer_llm_ms=64000, product_review_llm_ms=3839)
    generated["generation"]["failures"] = [
        {"model": "primary-model", "http_status": 503, "elapsed_ms": 60002},
        {"model": "legacy-model", "http_status": 429},
    ]
    output: list[str] = []
    demoRAG.show_answer(context, generated, 68, write=output.append)
    text = "\n".join(output)
    assert "LLM trả lời:" not in text
    assert "LLM kiểm tra dữ kiện:" not in text
    assert "primary-model" not in text
    demoRAG.show_details(context, generated, 68, write=output.append)
    text = "\n".join(output)
    assert "LLM trả lời: 64.00s" in text
    assert "LLM kiểm tra dữ kiện: 3.84s" in text
    assert "Lần lỗi 1: primary-model · HTTP 503 · 60.00s" in text
    assert "Lần lỗi 2: legacy-model · HTTP 429 · chưa đo" in text


def test_legacy_details_leave_unmeasured_llm_phases_unavailable():
    context, generated = blocked_result()
    generated.pop("timings")
    output: list[str] = []
    demoRAG.show_details(context, generated, 1, write=output.append)
    text = "\n".join(output)
    assert "LLM trả lời: chưa đo" in text
    assert "LLM kiểm tra dữ kiện: chưa đo" in text


def test_details_redact_schema_errors_without_changing_saved_metadata():
    context, generated = blocked_result()
    raw_error = "/: Có trường ngoài cấu trúc cho phép: InventedQuestionAndQuote?"
    generated["generation"]["product_review"]["errors"] = [raw_error]
    generated["validation"] = {"valid": False, "errors": [raw_error]}
    output: list[str] = []
    demoRAG.show_details(context, generated, 1, write=output.append)
    text = "\n".join(output)
    assert "InventedQuestionAndQuote?" not in text
    assert "Phản hồi không đúng cấu trúc JSON bắt buộc." in text
    assert generated["generation"]["product_review"]["errors"] == [raw_error]
    assert generated["validation"]["errors"] == [raw_error]


def test_token_budget_details_distinguish_full_request_estimates_and_provider_usage():
    context, generated = blocked_result()
    budget = {
        "mode": "CONSERVATIVE_UTF8_BOUND",
        "input_tokens": 25000,
        "input_limit": 1048576,
        "output_tokens": 65535,
        "max_output_tokens": 65535,
    }
    context["packing"] = {
        "input_chars": 14000,
        "max_input_chars": None,
        "source_chars": 9000,
        "max_context_chars": None,
        "system_chars": 7000,
        "user_chars": 14000,
        "schema_chars": 2000,
        "request_budget": budget,
        "omitted_candidate_codes": [],
    }
    generated["generation"]["request_budget"] = {**budget, "input_tokens": 27000}
    generated["generation"]["usage"] = {"prompt_tokens": 12345, "completion_tokens": 200}
    output: list[str] = []
    demoRAG.show_details(context, generated, 1, write=output.append)
    text = "\n".join(output)
    assert "Yêu cầu ban đầu: 25000/1048576 token ước tính" in text
    assert "Yêu cầu model thực tế: 27000/1048576 token ước tính" in text
    assert "CONSERVATIVE_UTF8_BOUND" in text
    assert "Ký tự: system 7000 · user 14000 · nguồn 9000 · schema 2000" in text
    assert "Token theo provider: prompt_tokens=12345, completion_tokens=200" in text
    assert "/None" not in text
    assert "/8000" not in text
    assert "/6000" not in text


def test_budget_overflow_preserves_all_user_facts_for_model_switch_and_retry():
    facts = ("Dữ kiện hàng hóa được người dùng xác nhận. " * 5000).strip()
    queries, payloads, output = conversation(
        ["/model 3", "Câu hỏi gốc", facts, "/details", "/model 2", "/retry", "/sources"],
        [response("MISSING_PRODUCT_INFO"), response()],
        selectable=True,
        token_limits=True,
    )
    assert len(queries) == 3
    assert len(payloads) == 2
    assert queries[1] == queries[2]
    assert facts in queries[2][0]
    assert "Câu hỏi gốc" in queries[2][0]
    assert payloads[-1]["question"] == queries[2][0]
    assert "Yêu cầu vượt giới hạn ngữ cảnh đầu vào" in output
    assert "Ngân sách gpt-oss-120b-medium:" in output
    assert "/114000 token ước tính" in output
    assert "context_length_exceeded" in output
    assert "Dịch vụ AI chưa trả lời được" not in output
    assert "Thông tin đã được giữ lại" not in output
    assert "/None" not in output
    assert facts not in output
    assert "ID: test-source" in output


def test_details_show_review_and_repair_budget_guards_without_provider_http_claims():
    context, generated = blocked_result()
    budget = {
        "mode": "CONSERVATIVE_UTF8_BOUND",
        "input_tokens": 120000,
        "input_limit": 114000,
        "shared_context": True,
        "context_limit": 114000,
        "remaining_context_tokens": -6000,
        "output_tokens": 0,
        "max_output_tokens": 32768,
    }
    generated["generation"].update(
        http_status=413,
        error_code="context_length_exceeded",
        repair_budget_error=budget,
        failures=[
            {
                "model": "smaller-fallback",
                "http_status": 413,
                "error_code": "context_length_exceeded",
                "request_budget": budget,
            }
        ],
    )
    generated["generation"]["product_review"]["request_budget"] = budget
    output: list[str] = []
    demoRAG.show_details(context, generated, 1, write=output.append)
    text = "\n".join(output)
    assert "Yêu cầu sửa phản hồi bị chặn: 120000/114000 token ước tính" in text
    assert "Yêu cầu kiểm tra dữ kiện: 120000/114000 token ước tính" in text
    assert "chặn cục bộ: vượt ngân sách context" in text
    assert "Context dùng chung input/output: 114000 token · Còn sau input: -6000" in text
    assert "HTTP: 413" not in text
    assert "HTTP 413" not in text


def test_decision_review_details_show_valid_reason_timing_budget_and_usage_only_on_request():
    context, generated = blocked_result()
    generated["generation"]["decision_review"] = {
        "valid": True,
        "review": {"reason": "Trạng thái thiếu nguồn cần đối chiếu lại với chứng cứ được cấp."},
        "model": "decision-review-model",
        "errors": [],
        "usage": {"prompt_tokens": 1200, "completion_tokens": 200},
        "request_budget": {
            "input_tokens": 8000,
            "input_limit": 1048576,
            "mode": "CONSERVATIVE_UTF8_BOUND",
        },
    }
    generated["timings"]["decision_review_llm_ms"] = 700
    output: list[str] = []
    demoRAG.show_answer(context, generated, 5, write=output.append)
    assert "Kiểm tra trạng thái phân loại:" not in "\n".join(output)
    assert "decision-review-model" not in "\n".join(output)
    demoRAG.show_details(context, generated, 5, write=output.append)
    text = "\n".join(output)
    assert text.count("LLM kiểm tra trạng thái phân loại: 700.0ms") == 1
    assert "Kiểm tra trạng thái phân loại: Hợp lệ" in text
    assert "Trạng thái thiếu nguồn cần đối chiếu lại với chứng cứ được cấp." in text
    assert "Model kiểm tra trạng thái: decision-review-model" in text
    assert "Yêu cầu kiểm tra trạng thái: 8000/1048576 token ước tính" in text
    assert (
        "Token kiểm tra trạng thái theo provider: prompt_tokens=1200, completion_tokens=200" in text
    )


@pytest.mark.parametrize("invalid_review", [{"reason": "Invented clarification?"}, [], None])
def test_invalid_decision_review_never_displays_unvalidated_reason_or_schema_keys(invalid_review):
    context, generated = blocked_result()
    generated["generation"]["decision_review"] = {
        "valid": False,
        "review": invalid_review,
        "reason": "Invented top-level clarification?",
        "errors": ["/: Có trường ngoài cấu trúc cho phép: InventedQuestionOrQuote?"],
    }
    output: list[str] = []
    demoRAG.show_answer(context, generated, 1, write=output.append, debug=True)
    text = "\n".join(output)
    assert "Kiểm tra trạng thái phân loại: Cần thẩm định" in text
    assert "LLM kiểm tra trạng thái phân loại: chưa đo" in text
    assert "Phản hồi không đúng cấu trúc JSON bắt buộc." in text
    assert "Invented" not in text


def test_unused_decision_review_does_not_add_a_detail_section():
    context, generated = blocked_result()
    generated["timings"]["decision_review_llm_ms"] = 0
    output: list[str] = []
    demoRAG.show_details(context, generated, 1, write=output.append)
    text = "\n".join(output)
    assert "Kiểm tra trạng thái phân loại:" not in text
    assert "LLM kiểm tra trạng thái phân loại:" not in text


def test_console_transfers_retrieval_measurements_to_details():
    _, _, output = conversation(
        ["Câu hỏi", "/details"],
        [response()],
        retrieval_timings={
            "retrieval_ms": 1000,
            "reranking_ms": 2000,
            "m3_ms": 1250,
            "qwen_ms": 750,
            "total_ms": 3000,
        },
    )
    assert output.count("Retrieval 1.00s") == 2
    assert "Reranking 2.00s" in output
    assert "M3: 1.25s · Qwen: 750.0ms · Tổng truy xuất: 3.00s" in output
    assert "Đóng gói ngữ cảnh:" in output


def test_blocked_diagnostics_are_cleared_by_new_question_and_failed_request(monkeypatch):
    context, generated = blocked_result()
    results = deque([generated, GroqError(503, "unavailable-model")])

    def generate(_context, _client):
        _context["sources"] = context["sources"]
        _context["allowed_hs_codes"] = context["allowed_hs_codes"]
        item = results.popleft()
        if isinstance(item, Exception):
            raise item
        return item

    monkeypatch.setattr(demoRAG, "generate_answer", generate)
    _, _, output = conversation(
        ["Điện thoại", "/new", "/sources", "Câu hỏi khác", "/sources", "/details"], []
    )
    assert output.count("Ứng viên đang kiểm tra (chưa kết luận): 85171300") == 1
    assert output.count("TT31.pdf | trang PDF 7, 8") == 1
    assert "Chưa có kết quả." in output
    assert "Chưa có câu trả lời hợp lệ để hiển thị nguồn." in output
    assert "Điện thoại thông minh" not in output


def test_failed_main_request_preserves_measured_stages_for_output_and_details(monkeypatch):
    error = GroqError(503, "unavailable-model")
    error.timings = {"llm_ms": 1234, "validation_ms": 4.5}

    def generate(*_):
        raise error

    monkeypatch.setattr(demoRAG, "generate_answer", generate)
    _, _, output = conversation(
        ["Câu hỏi", "/details"], [], retrieval_timings={"retrieval_ms": 100, "reranking_ms": 250}
    )
    assert output.count("LLM 1.23s") == 2
    assert output.count("Validation 4.5ms") == 2
    assert "Retrieval 100.0ms" in output
    assert "Reranking 250.0ms" in output
    assert "HTTP: 503" in output


@pytest.mark.parametrize("debug", [False, True])
def test_invalid_review_never_releases_unvalidated_questions_or_quotes(debug):
    invented_question = "VuiLongCungCapDuKienChuaXacThuc?"
    invalid_review = {
        "status": "MISSING_PRODUCT_INFO",
        "reason": "Please provide unsupported product data?",
        "product_facts": [{"fact": "Invented facts", "user_quote": "Invented user quote"}],
        "condition_checks": [
            {
                "source_label": "S99",
                "source_quote": "Invented source quote",
                "assessment": "MISSING_PRODUCT_INFO",
                "product_fact_indices": [],
            }
        ],
        "missing_information": ["Unsupported product attribute?"],
        "missing_legal_evidence": [],
        invented_question: True,
    }
    _, _, output = conversation(
        ["Nhẫn bằng vàng", "/sources", "/details"],
        [response("RECOMMENDATION")],
        review_answers=[invalid_review, invalid_review],
        debug=debug,
    )
    assert "Cần thẩm định thêm" in output
    assert "Ứng viên đang kiểm tra (chưa kết luận): 71131990" in output
    assert "Nội dung nguồn" in output
    assert "ID: test-source" in output
    for unvalidated in (
        invented_question,
        invalid_review["reason"],
        "Invented user quote",
        "Invented source quote",
        "Unsupported product attribute?",
        "S99",
    ):
        assert unvalidated not in output
