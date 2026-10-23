"""A retrieved evidence gap does not establish absence from the complete corpus."""

import pytest

from rag.llm.validation.answer import validate_answer


def response(**changes):
    return {
        "status": "INSUFFICIENT_LEGAL_EVIDENCE",
        "answer": "Ngữ cảnh truy xuất lượt này chưa có nguồn pháp lý phù hợp.",
        "suggested_hs_code": "",
        "alternatives": [],
        "citations": [],
        "missing_information": [],
        "missing_legal_evidence": ["Chưa được cấp mô tả pháp lý của nhóm hàng liên quan."],
        **changes,
    }


CONTEXT = {"task": "auto", "sources": [], "allowed_hs_codes": [], "candidate_evidence": []}


@pytest.mark.parametrize("field", ["answer", "missing_legal_evidence"])
@pytest.mark.parametrize(
    "claim",
    [
        "Cơ sở dữ liệu không có quy định nhóm 84.71.",
        "Cơ sở dữ liệu hiện tại chưa có biểu thuế phù hợp.",
        "Kho dữ liệu còn thiếu mô tả pháp lý của mã này.",
        "Kho tri thức không chứa Chú giải Chương 84.",
        "Cơ sở dữ liệu không có thông tin về nhóm 84.71.",
        "Database lacks any relevant tariff entries.",
        "Corpus lacks applicable Chapter 84 notes.",
        "The database has no legal evidence for this classification.",
        "The knowledge base does not contain any tariff entries.",
        "Our corpus is missing the relevant legal sources.",
        "Không có quy định nhóm 84.71 trong cơ sở dữ liệu.",
        "There are no tariff entries in the database.",
        "Không thể kết luận về hiệu lực; database has no legal sources.",
        "We cannot conclude the database lacks notes, but the corpus lacks tariff data.",
    ],
)
def test_whole_corpus_absence_claims_require_separate_trusted_evidence(field, claim):
    changes = {field: [claim] if field == "missing_legal_evidence" else claim}
    result = validate_answer(response(**changes), CONTEXT)
    assert not result["valid"]
    assert any("toàn kho" in error for error in result["boundary_errors"])


@pytest.mark.parametrize("field", ["answer", "missing_legal_evidence"])
@pytest.mark.parametrize(
    "diagnostic",
    [
        "Ngữ cảnh truy xuất lượt này chưa có mô tả nhóm 84.71.",
        "Hệ thống chưa truy xuất được Chú giải Chương 84.",
        "Các nguồn được cấp chưa chứa biểu thuế phù hợp.",
        "The retrieved context lacks the relevant legal evidence.",
        "No relevant tariff entries were retrieved from the database in this turn.",
        "Không thể kết luận kho dữ liệu không có quy định nhóm 84.71.",
        "Chưa thể khẳng định cơ sở dữ liệu thiếu Chú giải.",
        "Không thể kết luận rằng toàn bộ kho dữ liệu không có quy định này.",
        "Không nhận được nguồn không có nghĩa là corpus không có mô tả pháp lý.",
        "Thiếu nguồn truy xuất không đồng nghĩa là corpus không có mô tả pháp lý.",
        "Không phải database không có luật; hệ thống chưa truy xuất được nguồn.",
        "We cannot conclude that the database has no legal evidence.",
        "We cannot conclude that the entire database has no legal evidence.",
        "There is no evidence that the database has no applicable notes.",
        "Missing retrieved evidence does not mean the corpus lacks applicable notes.",
        "The retrieved sources from the database lack the relevant legal evidence.",
        "Corpus evidence is missing.",
    ],
)
def test_scoped_evidence_gaps_and_negated_corpus_claims_remain_valid(field, diagnostic):
    changes = {field: [diagnostic] if field == "missing_legal_evidence" else diagnostic}
    assert validate_answer(response(**changes), CONTEXT)["valid"]


@pytest.mark.parametrize(
    "question",
    [
        "Sản phẩm thực tế là loại hàng gì và dùng để làm gì?",
        "Máy chủ cơ sở dữ liệu này không có màn hình; vui lòng cho biết công dụng thực tế.",
        "Does the database server have a keyboard or display?",
    ],
)
def test_product_clarification_is_not_a_corpus_absence_claim(question):
    value = response(
        status="MISSING_PRODUCT_INFO",
        answer=question,
        missing_information=["Loại hàng và công dụng thực tế"],
        missing_legal_evidence=[],
    )
    assert validate_answer(value, CONTEXT)["valid"]
