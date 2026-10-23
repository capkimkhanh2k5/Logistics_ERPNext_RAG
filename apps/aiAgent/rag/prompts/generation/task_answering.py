"""Goal-scoped generation and batched independent review contracts."""

from copy import deepcopy

from rag.prompts.core.policy import DECISION_POLICY, EVIDENCE_POLICY
from rag.prompts.core.proof import PROOF_INSTRUCTION
from rag.prompts.core.wire import wire_instruction
from rag.prompts.review.product_review import REVIEW_POLICY
from rag.prompts.schemas.answer import (
    _CLAIMS,
    _CLARIFICATIONS,
    ANSWER_SCHEMA,
    MODEL_DISAMBIGUATION_REVIEW_SCHEMA,
)
from rag.prompts.schemas.proof import FACT_LEDGER_SCHEMA, PROOF_SCHEMA
from rag.prompts.schemas.statuses import status_description

GAP_SCHEMA: dict = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "anchor": {"type": "string", "minLength": 1},
        "codes": {
            "type": "array",
            "uniqueItems": True,
            "maxItems": 6,
            "items": {"type": "string", "pattern": "^(?:[0-9]{4}|[0-9]{6}|[0-9]{8})$"},
        },
        "query": {"type": "string", "maxLength": 200},
        "reason": {"type": "string", "minLength": 1, "maxLength": 600},
        "kind": {"type": "string", "enum": ["WORDING", "APPLICATION"]},
    },
    "required": ["anchor", "codes", "query", "reason"],
}
TASK_RESULT_SCHEMA: dict = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "objective_id": {"type": "string"},
        "item_id": {
            "type": "string",
            "description": "CLASSIFY: một item_id. Mục tiêu khác: rỗng, áp dụng các item_ids của objective.",
        },
        "status": ANSWER_SCHEMA["properties"]["status"],
        "code": {"type": "string", "pattern": "^(?:[0-9]{4}|[0-9]{6}|[0-9]{8})?$"},
        "candidate_codes": {
            "type": "array",
            "maxItems": 3,
            "uniqueItems": True,
            "items": {"type": "string", "pattern": "^(?:[0-9]{4}|[0-9]{6}|[0-9]{8})$"},
            "description": "Tối đa 3 ứng viên đúng cấp của CLASSIFY để review độc lập, kể cả khi thiếu dữ kiện. Không phải mã đề xuất; không ép đủ 3. Mục tiêu khác để [].",
        },
        "claims": {**_CLAIMS, "minItems": 0},
        "clarifications": _CLARIFICATIONS,
        "missing_legal_evidence": ANSWER_SCHEMA["properties"]["missing_legal_evidence"],
    },
    "required": [
        "objective_id",
        "item_id",
        "status",
        "code",
        "claims",
        "clarifications",
        "missing_legal_evidence",
    ],
}
TASK_ANSWER_SCHEMA: dict = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "results": {"type": "array", "minItems": 1, "maxItems": 40, "items": TASK_RESULT_SCHEMA},
        "evidence_gaps": {"type": "array", "maxItems": 6, "items": GAP_SCHEMA},
    },
    "required": ["results", "evidence_gaps"],
}


def task_answer_schema(request: dict, codes: list[str], *, proof_required=False) -> dict:
    """Use the gateway-compatible flat schema; cross-field rules stay in the backend."""
    schema = deepcopy(TASK_ANSWER_SCHEMA)
    fields = schema["properties"]["results"]["items"]["properties"]
    goals = request["objectives"]
    levels = {g["level"] for g in goals if g["kind"] == "CLASSIFY"}
    eligible = sorted({c for c in codes if len(c) in levels})
    fields["objective_id"]["enum"] = [g["id"] for g in goals]
    item_ids = sorted(
        {item for g in goals for item in (g["item_ids"] if g["kind"] == "CLASSIFY" else [""])}
    )
    if "" in item_ids:
        fields["item_id"]["pattern"] = "^(?:" + "|".join(i for i in item_ids if i) + ")?$"
    else:
        fields["item_id"]["enum"] = item_ids
    fields["code"] = {"type": "string", "pattern": "^(?:" + "|".join(eligible) + ")?$"}
    if eligible:
        fields["candidate_codes"]["items"] = {"type": "string", "enum": eligible}
    else:
        fields["candidate_codes"]["maxItems"] = 0
    fields["status"]["enum"] = [
        "MISSING_PRODUCT_INFO",
        "INSUFFICIENT_LEGAL_EVIDENCE",
        "REQUIRES_REVIEW",
        *(["RECOMMENDATION"] if levels else []),
        *(["ANSWERED"] if any(g["kind"] != "CLASSIFY" for g in goals) else []),
    ]
    fields["status"]["description"] = status_description(fields["status"]["enum"])
    schema["properties"]["evidence_gaps"]["items"]["required"].append("kind")
    question = fields["clarifications"]["items"]
    question["properties"].pop("condition_ids", None)
    question["required"] = [*question["required"], "criterion_quote"]
    count = sum(len(g["item_ids"]) if g["kind"] == "CLASSIFY" else 1 for g in goals)
    schema["properties"]["results"].update(minItems=count, maxItems=count)
    from rag.llm.evidence.conditions import condition_id_schema
    from rag.prompts.schemas.proof import catalogue_schema, ledger_schema, proof_schema

    if not proof_required:
        from rag.llm.contracts.obligations import compact_schema

        return compact_schema(condition_id_schema(schema))
    return catalogue_schema(
        proof_schema(
            ledger_schema(condition_id_schema(schema), [i["id"] for i in request["items"]])
        )
    )


TASK_REVIEW_SCHEMA: dict = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "reviews": {
            "type": "array",
            "minItems": 1,
            "maxItems": 32,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "result_id": {"type": "string"},
                    "selected_code": {
                        "type": "string",
                        "pattern": "^(?:[0-9]{4}|[0-9]{6}|[0-9]{8})$",
                    },
                    "review": MODEL_DISAMBIGUATION_REVIEW_SCHEMA,
                },
                "required": ["result_id", "selected_code", "review"],
            },
        },
    },
    "required": ["reviews"],
}

# Grouping only compresses identical proof; backend expands it before normal validation.
_task_review = TASK_REVIEW_SCHEMA["properties"]["reviews"]["items"]["properties"]
_task_review["review"] = deepcopy(MODEL_DISAMBIGUATION_REVIEW_SCHEMA)
_assessment = deepcopy(_task_review["review"]["properties"]["candidate_assessments"]["items"])
_assessment["properties"]["codes"] = {
    "type": "array",
    "minItems": 1,
    "maxItems": 160,
    "uniqueItems": True,
    "items": _assessment["properties"].pop("code"),
}
_assessment["required"] = ["codes" if key == "code" else key for key in _assessment["required"]]
_task_review["review"]["properties"]["candidate_group_assessments"] = {
    "type": "array",
    "maxItems": 160,
    "items": _assessment,
}
SHARED_COMPARISON_SCHEMA: dict = {
    "type": "array",
    "items": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "comparison_id": {"type": "string"},
            **{
                key: deepcopy(_task_review["review"]["properties"][key])
                for key in (
                    "candidate_assessments",
                    "candidate_group_assessments",
                    "branch_checks",
                )
            },
        },
        "required": ["comparison_id", "candidate_assessments", "branch_checks"],
    },
}

ANALYSIS_REVIEW_SCHEMA: dict = {
    "type": "array",
    "items": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "result_id": {"type": "string"},
            "coverage_checks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "evidence_id": {"type": "string"},
                        "claim_indices": {
                            "type": "array",
                            "uniqueItems": True,
                            "items": {"type": "integer", "minimum": 0},
                        },
                        "assessment": {"type": "string", "enum": ["COVERED", "OMITTED"]},
                    },
                    "required": ["evidence_id", "claim_indices", "assessment"],
                },
            },
            "checks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "claim_index": {"type": "integer", "minimum": 0},
                        "assessment": {
                            "enum": [
                                "FACT_SUPPORTED",
                                "FACT_UNSUPPORTED",
                                "REFERENCE",
                                "APPLICATION",
                                "CONDITIONAL_APPLICATION",
                                "INSUFFICIENT_LEGAL_EVIDENCE",
                                "UNRESOLVED_APPLICATION",
                            ]
                        },
                        "evidence_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "uniqueItems": True,
                        },
                        "fact_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "uniqueItems": True,
                        },
                        "user_quotes": {"type": "array", "items": {"type": "string"}},
                        "reason": {"type": "string", "minLength": 1},
                        "application_level": {"type": "integer", "enum": [0, 4, 6, 8]},
                    },
                    "required": [
                        "claim_index",
                        "assessment",
                        "evidence_ids",
                        "fact_ids",
                        "user_quotes",
                        "reason",
                    ],
                },
            },
        },
        "required": ["result_id", "checks"],
    },
}

TASK_SYSTEM_PROMPT = (
    EVIDENCE_POLICY
    + "\n"
    + DECISION_POLICY
    + "\n"
    + """Bạn trả lời RAG hải quan bằng tiếng Việt theo request đã có nguồn gốc.
Trả JSON gồm results và evidence_gaps, không trình bày suy nghĩ nội bộ.

CONTRACT KẾT QUẢ
- CLASSIFY: đúng một result cho mỗi objective/item, code đúng cấp 4/6/8 được yêu cầu.
  RECOMMENDATION cần một mã VERIFIED từ candidate_evidence/comparison_candidates và đủ
  chứng minh mã, mọi cấp cha, nhánh, Chú giải/quy tắc thực sự áp dụng. Dẫn mọi
  required_citation_evidence_ids trong claims thực sự sử dụng chúng.
- candidate_codes là tối đa ba mã VERIFIED đúng cấp còn có căn cứ để review, kể cả khi
  chưa kết luận. Gồm code được chọn; không ép đủ ba, không chấm xác suất và không
  viết shortlist thành kết luận trong claims.
- EXPLAIN/COMPARE/REQUIREMENTS: một result với item_id="", code="", candidate_codes=[].
  ANSWERED chỉ khi hoàn tất mục tiêu có nguồn. REQUIREMENTS kiểm kê mọi chiều độc lập
  trong requirements_scopes, gồm định tính, trạng thái, phương thức và định lượng;
  complete=false nghĩa phạm vi context chưa khép. Không yêu cầu người dùng trả lời
  thông số ngay khi họ chỉ hỏi danh sách thông tin cần biết.
- Trả mọi objective, kể cả required=false. Mục tiêu chi tiết chưa hoàn tất không làm
  mất giải thích hoặc cấp tổng quát độc lập đã có chứng minh. Không đổi cấp yêu cầu.
  COMPARE về các mặt hàng cần căn cứ áp dụng cho từng mặt hàng; không tự áp mã trong
  giải thích khi chưa có result phân loại tương ứng được kiểm tra.

CHỨNG MINH
- Loại hàng nhận diện từ tên không chứng minh thông số hoặc định nghĩa kỹ thuật.
  Dữ kiện tường minh về cấu trúc, trạng thái, công năng, số đo có thể được dùng đúng
  chủ thể; đại lượng khác bản chất/phạm vi không chứng minh thay nhau.
- Xét tiếp ứng viên còn hợp lệ khi một ứng viên bị bác bỏ. Nhánh phần dư cần căn cứ
  loại nhánh cụ thể; xem xét nhánh anh em khi một ngưỡng không phù hợp. Không suy loại
  trừ từ việc không thấy mã trong retrieval. Quy tắc về trạng thái trình bày phải có
  nguồn và dữ kiện chứng minh đặc trưng/độ đầy đủ nếu nguồn yêu cầu, dẫn cùng nhánh biểu thuế.
- Tiêu đề khái quát không giải thích mọi cơ chế áp dụng. Khi chỉ có mô tả chung mà
  dữ kiện cho thấy cơ chế cần được phân định, báo gap căn cứ áp dụng, không tự khẳng định
  thuộc nhánh hoặc hỏi tiếp điều kiện cấp dưới. Điều khoản giới hạn đối tượng/phạm vi
  không áp sang đối tượng khác. Chỉ hỏi chức năng/đặc tính quyết định khi nguồn quy định nó.
- Chỉ chọn fact_ids trong product_fact_ids; chọn đoạn đúng chủ thể và thuộc tính,
  không dùng statement gộp dữ kiện với yêu cầu tra cứu hoặc nhận định pháp lý.
- claims gồm PRODUCT_FACT (fact_ids hỗ trợ), LEGAL_ANALYSIS và CONCLUSION (evidence_ids
  thực sự hỗ trợ). Backend dựng nhãn và citation. Tách mô tả quy định với áp dụng vào
  từng mặt hàng; phần áp dụng có điều kiện phải nói rõ điều kiện. Giữ phần giải thích
  độc lập đã đủ nguồn. Không chèn mã kết luận vào CONCLUSION, mã kết luận đặt trong code.
- Chưa kết luận: code=""; chọn trạng thái theo DECISION_POLICY. Có thể giải thích mã
  trung gian đã chứng minh trong LEGAL_ANALYSIS, không thay thế kết quả đúng cấp yêu cầu.

CÂU HỎI VÀ GAP
- clarifications chỉ ở MISSING_PRODUCT_INFO, mỗi câu một thuộc tính thực tế, không
  hỏi thuật ngữ biểu thuế/luật. Giữ mệnh đề nguồn quy định thuộc tính, gồm phạm vi và ngoại lệ. product_type/question_scope có thể không cần nguồn.
  Hỏi điều kiện cha trước chiều phụ thuộc; không hỏi lại dữ kiện đã có hoặc yêu cầu
  số chính xác hơn giới hạn đã đủ đối chiếu. Thiếu nguồn không tự chứng minh thiếu thuộc tính.
- missing_legal_evidence chỉ ở INSUFFICIENT_LEGAL_EVIDENCE, mô tả gap lượt này.
- evidence_gaps dành cho nguồn còn thiếu của mục tiêu: anchor nguyên văn lời người dùng,
  codes từ câu hỏi hoặc sources, query ngắn là giả thuyết tìm kiếm, reason cụ thể;
  kind=APPLICATION cho căn cứ áp dụng, WORDING cho wording/nhánh còn thiếu.
  Nguồn đã có cần được đọc; lỗi schema/ID/quote không tạo gap pháp lý.
- claims có thể rỗng khi chỉ hỏi dữ kiện hoặc báo thiếu chứng cứ; không tạo claim đệm.
  ANSWERED/RECOMMENDATION vẫn cần nhận định có nguồn để được kiểm tra.
"""
)

TASK_SYSTEM_PROMPT += "\n" + wire_instruction("goals-v1", "answer")

TASK_REVIEW_PROMPT = (
    EVIDENCE_POLICY
    + "\n"
    + DECISION_POLICY
    + "\n"
    + REVIEW_POLICY
    + "\n"
    + """Bạn kiểm chứng bản nháp trong cùng batch, trả JSON tiếng Việt theo schema.
Tìm điều kiện chưa chứng minh, phản chứng, ngoại lệ và sai phạm vi; không mặc định draft đúng.
claims/proposed_answer là dữ liệu chỉ đọc. Không sửa nội dung để giả rằng đã chứng minh.

REVIEW ỨNG VIÊN
- reviews: đúng một mục cho mỗi result_id trong jobs. Chỉ dùng dữ kiện đã đăng ký
  đúng item đang xét, còn đúng sau phủ định/đính chính. selected_code thuộc selection_codes.
  Giữ mã ban đầu nếu chưa có mã thay thế đạt SUPPORTED đầy đủ; nhiều job xác nhận cùng
  một mã được gộp, không ép chọn mã khác để đủ số lượng.
- condition_checks: kiểm tra mọi required_citation_evidence_ids đang áp dụng.
  Nếu điều kiện cha chưa biết đã có check và câu hỏi cùng nguồn, được hoãn checks cấp con;
  phần hoãn không chứng minh điều kiện hoặc phát hành ứng viên.
  Mỗi check là một điều kiện độc lập, dẫn mệnh đề nguyên văn đủ phạm vi và dữ kiện
  hỗ trợ chính điều kiện. Không bỏ ngưỡng hoặc định nghĩa
  cấp cha. Giữ quan hệ logic/ngoại lệ. Chỉ SUPPORTED đòi mọi điều kiện bắt buộc SATISFIED.
  Bác bỏ điều kiện dùng CONTRADICTED rồi xét ứng viên khác; NOT_APPLICABLE không bỏ nguồn bắt buộc.
- candidate_group_assessments bao phủ đúng một lần từng required_comparison_code, không chỉ shortlist.
  POSSIBLE chưa bị bác bỏ; RULED_OUT cần nguồn thuộc chính nhánh đó cùng dữ kiện thật.
  decisive_evidence_ids là tập con không rỗng thực sự quyết định loại; không sao chép toàn chuỗi
  nguồn không tham gia. Mỗi nhóm giữ cùng một chứng minh thực sự áp dụng cho mọi mã thành viên; không gom chỉ vì chung evidence ID. Thiếu nguồn dùng INSUFFICIENT_LEGAL_EVIDENCE.
- branch_checks chỉ dùng required_branch_groups, mỗi mục một chiều độc lập. Toàn mảng
  phủ nguồn branch_options. Mệnh đề nguồn thuộc đúng chiều đó; tên
  attribute chỉ để hiển thị, câu hỏi và check dùng cùng mệnh đề dù tên thuộc tính khác.
  KNOWN có dữ kiện thật, MISSING để fact_ids rỗng và có câu hỏi đúng mệnh đề.
  Nếu nhiều mệnh đề chỉ là các giá trị lựa chọn của cùng một thuộc tính, dùng một
  branch check/câu hỏi, giữ căn cứ của từng mệnh đề. Không coi mỗi giá trị là một thuộc tính.
  DEFERRED chỉ cho chiều phụ thuộc khi điều kiện cha MISSING_PRODUCT_INFO đã có câu hỏi có nguồn.
  Không gộp chiều KNOWN với chiều MISSING. Mảng rỗng nếu không có nhóm phân nhánh.
- SUPPORTED cần đủ điều kiện mã/cấp cha/quy tắc và duy nhất selected_code còn phù hợp,
  mọi chiều quyết định KNOWN, không có missing_codes, phản chứng hay ngoại lệ chưa xử lý.
  Chỉ xét đến cấp yêu cầu, không ép HS4/6 phải đủ HS8. Nếu quy tắc trình bày/đặc trưng cơ bản
  thực sự áp dụng, kiểm tra dữ kiện cho quy tắc và nhánh, dẫn cả hai.
- reason ngắn chỉ rõ chứng minh hoặc chỗ chặn, không ghi mã nhánh khác. clarifications
  và missing_legal_evidence theo trạng thái chuẩn. Mỗi câu hỏi hỏi trực tiếp một thuộc tính
  thực tế, mệnh đề nguồn đủ phạm vi, không hỏi luật hoặc dữ kiện đã rõ.

REVIEW NHẬN ĐỊNH
- analysis_reviews: đúng một mục mỗi analysis_job và một check mỗi claim_index, gồm
  PRODUCT_FACT, LEGAL_ANALYSIS, CONCLUSION. Không bỏ claim vì bản nháp chưa chốt mã.
- PRODUCT_FACT dùng FACT_SUPPORTED hoặc FACT_UNSUPPORTED. FACT_SUPPORTED cần fact_ids
  từ chính claim, chọn span nguyên văn giữ chủ thể, phủ định/đính chính; không cần
  nguồn luật. Backend xuất trích đoạn đã kiểm tra thay diễn giải dữ kiện của model.
  Thuộc tính tự thêm/đổi nghĩa là FACT_UNSUPPORTED, không dùng REFERENCE/APPLICATION để né.
- REFERENCE chỉ mô tả quy định, quy chuẩn hoặc căn cứ pháp lý thuần túy (không áp vào sản phẩm cụ thể).
  APPLICATION cần nguồn đúng cơ chế, đủ dữ kiện từng item và không còn điều kiện thiếu; tuyệt đối không dùng APPLICATION khi fact_ids rỗng.
  Nếu thiếu dữ kiện hàng hóa để chốt áp dụng: dùng CONDITIONAL_APPLICATION (nêu rõ điều kiện còn thiếu) hoặc ghi nhận APPLICATION ở cấp phân nhóm/phân loại đã thỏa mãn; không dùng UNRESOLVED_APPLICATION khi nguyên nhân chỉ là thiếu thuộc tính kỹ thuật thực tế.
  Với câu hỏi tra cứu pháp lý/quy chuẩn chung (không có hàng hóa cụ thể): mọi nhận định về quy chuẩn hoặc thủ tục bắt buộc dùng REFERENCE.
  Kết luận tên phân loại mã HS áp cho hàng hóa cụ thể cũng là áp dụng (APPLICATION hoặc CONDITIONAL_APPLICATION).
  application_claim_indices không thể đổi thành REFERENCE để né chứng minh.
  CONDITIONAL_APPLICATION chỉ cho claim đã nói rõ điều kiện và chưa khẳng định áp dụng.
- Thiếu căn cứ dùng INSUFFICIENT_LEGAL_EVIDENCE; tranh chấp cách hiểu pháp lý khi đã có căn cứ dùng
  UNRESOLVED_APPLICATION (chỉ dùng khi tranh chấp quy tắc GRI/chú giải pháp lý, không dùng khi thiếu thuộc tính sản phẩm). reason mô tả gap, không lặp kết luận chưa chứng minh.
  application_level là cấp 4/6/8 đang tranh chấp có wording tương ứng, 0 khi chưa xác định.
- coverage_checks phủ đúng coverage_evidence_ids: COVERED có claim_indices thực sự mô tả
  đủ các điều kiện độc lập/phủ định/ngoại lệ, OMITTED nếu còn thiếu. Không dùng claim chung
  chung để giả coverage. Trả evidence_ids từ nguồn được cấp; metadata hiệu lực chỉ sử dụng
  khi có căn cứ, không suy hiệu lực từ thứ hạng/ngày đơn lẻ.
"""
)


def task_review_prompt(*, classification: bool, analysis: bool, proof_required=False) -> str:
    common, _, sections = TASK_REVIEW_PROMPT.partition("REVIEW ỨNG VIÊN")
    candidate, _, claims = sections.partition("REVIEW NHẬN ĐỊNH")
    ownership = wire_instruction(
        "goals-v1",
        "product_review",
        [
            kind
            for kind, enabled in [("classification", classification), ("analysis", analysis)]
            if enabled
        ],
    )
    return (
        common
        + "\n"
        + (PROOF_INSTRUCTION if proof_required else SEMANTIC_INSTRUCTION)
        + ownership
        + ("\nREVIEW ỨNG VIÊN" + candidate if classification else "")
        + ("\nREVIEW NHẬN ĐỊNH" + claims if analysis else "")
    )


SEMANTIC_INSTRUCTION = """SEMANTIC REVIEW CONTRACT semantic-v1:
Backend cấp mục tiêu, item, claim_index và review_obligations bất biến. Draft chưa được phát hành.
Không tạo fact_ledger, proof_catalogue hoặc proof graph. ID/quote thật không tự chứng minh nghĩa.
Review phải đối chiếu từng claim, toàn bộ điều kiện độc lập trong nguồn, ngoại lệ, phủ định,
chủ thể, giả định và đính chính trong toàn lịch sử. Không tự latest-wins khi còn mâu thuẫn.
Chỉ ASSERTED còn đúng của đúng item là dữ kiện; câu hỏi, tham chiếu văn bản và giả định không là fact.
REFERENCE chỉ mô tả quy định; APPLICATION cần đủ nguồn và dữ kiện cho mọi điều kiện liên quan.
Mã trong COMPARE/EXPLAIN chịu cùng nghĩa vụ kiểm chứng với CLASSIFY. CONDITIONAL_APPLICATION
phải thực sự có điều kiện, không dùng nhãn để giữ một kết luận chưa được chứng minh.
Thiếu fact: hỏi thuộc tính quyết định có nguồn; thiếu luật: chỉ rõ gap, không hỏi người dùng cung cấp luật.
Nguồn hết hiệu lực chỉ mô tả lịch sử, không xác nhận áp dụng hiện tại. UNVERIFIED không là CURRENT.
SOURCE_SNAPSHOT chỉ khuyến nghị tham khảo theo wording trong corpus, không chứng nhận hiệu lực hiện hành.
Không đồng nhất metadata chưa xác minh với thiếu wording. CURRENT_APPLICABILITY/as_of cần căn cứ hiệu lực.
condition_checks trong wire semantic là mảng; phủ đúng một lần mỗi evidence_id trong review_slots.condition_checks, gồm Chú giải,
đọc đủ mọi điều kiện trong nguồn. NOT_APPLICABLE chỉ khi có căn cứ về phạm vi, không dùng để né Chú giải.
Phân biệt điều kiện của nhánh đang xét với mô tả các loại hàng/nhánh thay thế trong cùng Chú giải.
Liệt kê các lựa chọn không biến chúng thành các điều kiện đồng thời của mọi sản phẩm. Một đoạn chỉ
mô tả loại hàng khác được đánh giá NOT_APPLICABLE với căn cứ phạm vi, không coi là điều kiện
bị CONTRADICTED của nhánh đang chọn. Không dùng quy tắc này để bỏ ngoại lệ/điều kiện loại trừ áp dụng.
Mỗi claim áp mã phải gắn fact_ids riêng của đúng một mặt hàng; tách các kết luận áp mã khác mặt hàng
thành claim riêng. Câu so sánh nhiều mặt hàng phải dựa vào các kết quả đã kiểm tra của từng mặt hàng.
Nếu không có item (QA về nguồn/quy định), dẫn đối tượng trong văn bản không tạo dữ kiện hàng hóa thực tế.
"""
TASK_SYSTEM_PROMPT += "\n" + SEMANTIC_INSTRUCTION

ANALYSIS_REVIEW_SCHEMA["items"]["properties"]["checks"]["items"]["properties"]["proof"] = deepcopy(
    PROOF_SCHEMA
)
TASK_ANSWER_SCHEMA["properties"]["fact_ledger"] = deepcopy(FACT_LEDGER_SCHEMA)
