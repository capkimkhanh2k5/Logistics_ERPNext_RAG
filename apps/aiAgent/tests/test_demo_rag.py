"""Terminal conversations exercise the runtime context/validation without network calls."""

import json
from collections import deque
from types import SimpleNamespace

import pytest

from config.settings import GroqConfig
from rag import demoRAG
from rag.answering import PRODUCT_REVIEW_SCHEMA
from rag.context import GraphContext
from rag.groq_client import GroqError


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


def conversation(inputs, answers, *, max_chars=8000, advisory_intent="qa"):
    inputs, answers = iter(inputs), deque(answers)
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
        }

    def complete(messages, schema, **kwargs):
        if schema is PRODUCT_REVIEW_SCHEMA:
            question = json.loads(messages[1]["content"])["question"]
            return {
                "content": json.dumps(
                    {
                        "status": "SUPPORTED",
                        "product_facts": [{"fact": "User facts", "user_quote": question}],
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
    demoRAG.run_console(
        SimpleNamespace(routed_search=search), client, graph, read=read, write=output.append
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
    assert "Trích: Nội dung nguồn" in output
    assert "fallback-model — đã dùng model dự phòng" in output


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
        ["Câu hỏi gốc", "Thông tin bổ sung", "/retry"],
        [response("MISSING_PRODUCT_INFO"), GroqError(429, "fixture-model", 12), response()],
    )
    assert queries[1] == queries[2]
    assert "Thông tin bổ sung" in queries[2][0]
    assert "HTTP 429" in output and "12s" in output
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
    assert "Phản hồi chưa vượt qua kiểm tra" in output
    assert "Nội dung không được xác thực" not in output
    assert "Trích dẫn bịa" not in output
    assert "AI: Chỉ dẫn của AI [S1]." in output


@pytest.mark.parametrize("end", [EOFError(), KeyboardInterrupt()])
def test_end_of_input_and_interrupt_exit_cleanly(end):
    queries, _, _ = conversation([end], [])
    assert queries == []


def test_missing_sources_skip_llm_and_show_insufficient_evidence():
    output: list[str] = []
    inputs = iter(["Một câu hỏi", "/exit"])

    def never_complete(*args, **kwargs):
        pytest.fail("No API call is allowed without sources")

    demoRAG.run_console(
        SimpleNamespace(routed_search=lambda *args, **kwargs: {"matches": []}),
        SimpleNamespace(config=GroqConfig(keys=("fixture",)), complete=never_complete),
        None,
        read=lambda _: next(inputs),
        write=output.append,
    )
    assert any("Chưa đủ chứng cứ pháp lý trong retrieval/corpus" in line for line in output)
    assert not any("Thông tin bạn cần bổ sung" in line for line in output)
    assert any("Không gọi LLM" in line for line in output)


def test_help_does_not_initialize_runtime_or_ask_for_mode(monkeypatch, capsys):
    monkeypatch.setattr(demoRAG, "connect", lambda: pytest.fail("Must not connect for help"))
    with pytest.raises(SystemExit) as exc:
        demoRAG.main(["--help"])
    assert exc.value.code == 0
    assert "--task" not in capsys.readouterr().out


@pytest.mark.parametrize("hint", ["product", "mixed_or_uncertain", None])
def test_qa_answers_remain_possible_when_intent_is_wrong_or_unclear(hint):
    _, payloads, output = conversation(
        ["Hệ thống HS gồm những gì?"], [response()], advisory_intent=hint
    )
    assert payloads[0]["task"] == "auto"
    assert "AI: Chỉ dẫn của AI [S1]." in output
    assert "Trạng thái: Đã trả lời" in output
