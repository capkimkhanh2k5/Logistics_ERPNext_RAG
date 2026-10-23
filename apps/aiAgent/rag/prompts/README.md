# Quản lý prompt và schema

Các chỉ dẫn tác vụ và schema do ứng dụng định nghĩa nằm trong package này.
Module LLM chỉ ghép payload, gọi provider và thực thi kiểm chứng.

## Sửa nội dung ở đâu

- `core/`: [policy.py](core/policy.py) giữ EVIDENCE_POLICY/DECISION_POLICY dùng chung;
  [system.py](core/system.py) thêm contract đơn kết quả;
  [wire.py](core/wire.py) chọn biểu diễn theo protocol/phase/job;
  [repair.py](core/repair.py) ghép chỉ dẫn sửa đúng quyền hạn;
  [provider_format.py](core/provider_format.py) tạo JSON wrapper cho provider cần nó;
  [proof.py](core/proof.py) giữ hướng dẫn ledger và proof graph chung.
- `generation/`: [task_answering.py](generation/task_answering.py) giữ prompt/schema
  goals-v1, builder schema động và batch review;
  [tasks.py](generation/tasks.py) giữ chỉ dẫn HS/QA/Auto và template dữ kiện bổ sung.
- `review/`: [product_review.py](review/product_review.py) giữ REVIEW_POLICY và prompt
  kiểm tra sản phẩm dùng chung/đơn; [decision_review.py](review/decision_review.py)
  kiểm tra quyết định chưa kết luận trong đường tương thích.
- `schemas/`: [answer.py](schemas/answer.py) giữ contract công khai, contract nội bộ và
  MODEL_*_SCHEMA; [review_slots.py](schemas/review_slots.py) dựng slot/miền evidence theo
  từng job; [statuses.py](schemas/statuses.py) mô tả thống nhất trạng thái và outcome;
  [proof.py](schemas/proof.py) dựng ledger, graph và catalogue wire.
- `planning/`: [query_planning.py](planning/query_planning.py) giữ query/turn planner;
  [conversation.py](planning/conversation.py) giữ fragment nhận diện lượt hội thoại.
- `retrieval/`: [reranking.py](retrieval/reranking.py) giữ instruction/template Qwen
  và version cache. Nội dung reranking không đổi trong lần tổ chức package này.

## Luồng goals hiện hành: semantic-v1 (22/10/2026)

`goals-v1` dùng `reasoning_contract=semantic-v1`: Draft chỉ chọn claim/fact/source/span,
không phát sinh ledger hay proof graph bắt buộc. Backend cấp objective/item, review slots,
claim_index và `review_obligations`; ID không chứng minh entailment. Mọi claim trong
CLASSIFY đề xuất cũng được semantic review trong batch, ngoài review quyết định mã.
Backend chỉ phát hành phần đã qua review và các chốt source/scope/ancestry/định lượng.

Prompt Task dùng SEMANTIC_INSTRUCTION. Graph contract dưới đây tiếp tục dành cho
`registry-v2`, các primitive evaluator và canonical proof đã lưu; không phải chốt Draft
giữa goals-v1 và Review. Không thêm call verifier hoặc đổi model/fallback.

Review kiểm tra câu hỏi/giả định/đính chính và toàn bộ điều kiện, phủ định, ngoại lệ;
backend từ chối non-assertion làm fact và nguồn được đánh dấu hết hiệu lực/UNVERIFIED
cho áp dụng hiện tại. SOURCE_SNAPSHOT mô tả wording lịch sử, có cảnh báo công khai về hiệu lực;
REFERENCE không chứng nhận luật hiện hành. Ngày áp dụng
có cấu trúc `as_of`, nếu được cung cấp, phải do caller có provenance xác định; không suy
hiệu lực hiện hành từ một trích dẫn. Metadata rỗng vẫn là chưa biết, không phải chứng nhận hiệu lực.

Repair goals cho phép chọn lại ID/slot trong registry với tối đa một lần sửa, không đoán
ID ngoài nguồn. Lỗi hiện hành thay bằng kết quả validate lần mới, lịch sử vẫn trong attempts.
Recovery chỉ vượt lỗi kỹ thuật của sibling khi gap độc lập đã review; không biến graph/ID
hỏng thành thiếu luật. COMPARE/EXPLAIN áp mã phải thỏa các phụ thuộc phân loại từng item;
giữ riêng phần REFERENCE/CONDITIONAL_APPLICATION đã được review.

Draft packet giữ mọi mã đối chứng và nguồn, bỏ phần metadata phân cấp lặp của danh mục
đối chứng; review packet giữ điều kiện/nguồn đầy đủ theo job. Không loại nhánh bằng Top-K.

## Contract proof và đường tương thích

Phần graph/ledger bên dưới chỉ áp dụng khi `proof_required=true` (registry/replay),
không phải hợp đồng Draft của goals semantic-v1. Cơ chế repair goals nằm ở mục trên.

`goals-v1` giữ mục tiêu/mặt hàng từ planner; `registry-v2` phục vụ đường đơn.
Context legacy không khai báo protocol được chuẩn hóa trước generation; model luôn
nhận MODEL_* hoặc task wire. ANSWER_SCHEMA chỉ còn là contract renderer/validator.
Decoder còn đọc định dạng canonical cũ để replay, không gửi schema công khai cho model.

Draft trả `fact_ledger`: chọn `fact_id` cùng `source_mode=STATEMENT`, subject/item, modality, polarity,
nguồn lời khai và supersedes. Backend gán L ID và trạng thái ACTIVE/UNKNOWN/CONFLICT/
SUPERSEDED. Draft dùng ledger key cục bộ trong proof; backend đổi sang L ID trước
kiểm tra. Review nhận ledger chỉ đọc và phải đối chiếu với toàn bộ statements.

`proof_catalogue` chứa `{key, proof}` một lần cho mỗi graph; các claim/check dẫn
`proof_key`, review dẫn `reason_proof_key`. Schema graph chỉ xuất hiện một lần trong
wire. Graph dùng predicate/quan hệ/phạm vi/ngoại lệ lấy từ nguồn và lời người dùng,
không có taxonomy theo tên sản phẩm hoặc đáp án bộ test. Backend gán N/G ID sau bind.

Wire proof-v2 có `root_node` không cần chép target và nodes phụ; backend gán root/target
từ đúng consumer. Mỗi graph chỉ được tham chiếu một lần. Canonical/replay vẫn có
root/target chỉ đọc và xác nhận phân rã/ledger. ALL/ANY/NOT/SCOPE/
EXCEPT/COMPARE được code tổng hợp; node nguyên tử còn cần model xác nhận hỗ trợ
ngữ nghĩa. Đúng ID/quote không đủ chứng minh entailment hay tính đầy đủ của phân rã.
Các trạng thái UNKNOWN giữ nguyên nhân riêng, không tự chuyển thành thiếu luật/fact.

`task_review_prompt` và repair chỉ ghép loại job đang có. `reviews`/`analysis_reviews`
giữ khóa backend cấp. `candidate_group_assessments` phủ mỗi mã đúng một lần, có thể
dùng chung assessment/proof khi cùng điều kiện quyết định. Chứng cứ quyết định loại
phải thuộc miền bắt buộc của mọi mã thành viên; trường hợp khác tách nhóm một mã.
Backend mở về slot từng mã và chạy lại kiểm tra nguồn, scope và độ phủ.

Lỗi từng job/group/claim được giữ đúng owner. Binding/coverage còn lỗi được withhold;
không gọi model để điền assessment giả. Nhận định thiếu chứng minh chỉ được hạ cấp
khi graph hợp lệ xác định trạng thái; proof hỏng không đủ để tự hỏi người dùng.
Câu hỏi thuộc tính có nguồn cần proof UNKNOWN cùng thuộc tính/ledger/span. Câu hỏi
nhận diện/phạm vi không có nguồn vẫn theo contract giới hạn riêng.

Provider ghi effective schema/hash/mode trong request_contract. Native và JSON wrapper
đều dùng wire mới. Không thêm call verifier, không đổi model/fallback, retrieval hoặc
ngân sách năm request goals sau planner. Trong nhiều trường hợp schema/output mới
lớn hơn; hiệu quả và gateway compatibility được ghi theo từng run trong
`artifacts/obligation-flow-20261022/report.md`; chưa nghiệm thu đủ 17 lượt HS.

`tests/test_generic_proof_engine.py` kiểm tra thuần backend; không phải đánh giá
phân loại HS. Fixture response giả/trace cũ không có ledger/proof cần chuyển sang
wire proof-v2 nếu dùng giả lập cả generation; decoder replay canonical vẫn giữ.
Xem [báo cáo triển khai](../../artifacts/general-proof-implementation-20261021/report.md).

Review semantic dùng mảng condition_checks với số lượng cố định; backend kiểm tra đúng tập
evidence_id, không thiếu/lặp/thay nguồn. Tránh schema lặp object cho từng nguồn vì native Gemini
đã từ chối 23 object với HTTP400; thử cùng 23 nghĩa vụ ở dạng mảng được chấp nhận.
SOURCE_SNAPSHOT không nâng UNVERIFIED thành CURRENT; CURRENT_APPLICABILITY/as_of cần
metadata hiệu lực đầy đủ. Các job tổ tiên cùng đợt được batch nhưng giữ scope riêng từng result.
