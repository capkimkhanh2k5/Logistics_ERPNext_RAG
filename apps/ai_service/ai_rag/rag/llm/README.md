Cập nhật 22/10/2026: đã triển khai semantic-v1 nhưng chưa nghiệm thu đủ bộ 17 lượt HS.
Xem artifacts/obligation-flow-20261022/report.md để đối chiếu test local và provider thật;
không dùng schema hợp lệ hoặc safe abstention làm bằng chứng hệ thống đã khôi phục chất lượng.

# Contract goals sau điều tra 22/10/2026

Đường goals-v1 hiện dùng semantic-v1. Xem `contracts/obligations.py` cho schema gọn,
phân biệt assertion và câu hỏi/giả định, kiểm tra hiệu lực áp dụng và nghĩa vụ immutable.
Draft không cần universal proof graph. `analysis_jobs` gồm cả claims của CLASSIFY;
review quyết định mã và review claims phải đều hợp lệ trước phát hành. Các ràng buộc
trích dẫn chính xác, item, ancestor, coverage và định lượng vẫn chạy.

`validation.valid`/`output_contract_valid` mô tả public envelope, không phải chất lượng
pháp lý. Báo riêng task_completion, review_execution_status, semantic_grounding,
questions, legal gaps và technical failures. Thiếu dữ kiện/luật hợp lệ không đồng nghĩa
đã chốt mã. Các phần mô tả proof bên dưới dành cho compatibility/evaluator/replay;
chúng không còn là yêu cầu Draft chung của goals-v1.

# Các module LLM

Package này xử lý ngữ cảnh, generation, review và kiểm chứng. Retrieval nằm trong
`rag/retrieval`; việc tổ chức thư mục không đổi thuật toán hoặc cấu hình truy xuất.

## Tìm module theo trách nhiệm

- `providers/`: [client.py](providers/client.py) giữ chính sách model/fallback của phiên;
  [cliproxy_client.py](providers/cliproxy_client.py), [groq_client.py](providers/groq_client.py)
  gọi provider; [budget.py](providers/budget.py) tính ngân sách và lưu effective schema.
- `context/`: [builder.py](context/builder.py) đóng gói nguồn, registry và messages;
  [task_context.py](context/task_context.py) tạo phạm vi theo mục tiêu;
  [conversation.py](context/conversation.py) xử lý quan hệ hội thoại có provenance;
  [normalization.py](context/normalization.py) chuẩn hóa caller legacy trước model wire.
- `generation/`: [answering.py](generation/answering.py) là entrypoint chung;
  [task_generation.py](generation/task_generation.py) điều phối goals-v1 và ngân sách;
  [shortlist.py](generation/shortlist.py) mở/gộp ứng viên đã review;
  [recovery.py](generation/recovery.py) điều phối tìm lại chứng cứ trong giới hạn hiện có.
- `review/`: [review_packet.py](review/review_packet.py) đóng gói ma trận dùng chung;
  [review_slots.py](review/review_slots.py) giải mã khóa backend cấp;
  [prerequisites.py](review/prerequisites.py) dựng review cha trước mã con;
  [disambiguation.py](review/disambiguation.py) kiểm tra đối chứng;
  [analysis_review.py](review/analysis_review.py) kiểm tra claims;
  [decision_review.py](review/decision_review.py) kiểm tra quyết định chưa kết luận;
  [review_coverage.py](review/review_coverage.py) mô tả phạm vi đã review;
  [candidate_ranking.py](review/candidate_ranking.py) xếp ứng viên theo bằng chứng.
- `evidence/`: [evidence.py](evidence/evidence.py) dựng citation, claim và câu hỏi;
  [conditions.py](evidence/conditions.py) quản lý span/condition registry;
  [ledger.py](evidence/ledger.py) quản lý dữ kiện và supersedes;
  [catalogue.py](evidence/catalogue.py) giải mã proof dùng chung;
  [proof_contract.py](evidence/proof_contract.py) gắn fact quote và vai trò chứng minh.
- `validation/`: [answer.py](validation/answer.py) kiểm tra đầu ra chung;
  [task_validation.py](validation/task_validation.py) kiểm tra mục tiêu/mặt hàng/cấp mã;
  [proof.py](validation/proof.py) kiểm tra proof graph chung;
  [quantitative.py](validation/quantitative.py),
  [application_rules.py](validation/application_rules.py) giữ các guard hiện có.
- `contracts/`: [errors.py](contracts/errors.py) định nghĩa lỗi an toàn;
  [diagnostics.py](contracts/diagnostics.py) gắn code/cause/owner/safe_action cho feedback;
  [repair_dispatch.py](contracts/repair_dispatch.py) canonicalize và chọn repair/withhold.
  [proof_resolution.py](review/proof_resolution.py) hạ assessment từ proof hợp lệ trước repair.

Prompt và schema thuộc [rag/prompts](../prompts/README.md). Không đặt system prompt
hoặc chỉ dẫn repair mới vào module xử lý.

## Entry point và luồng

```python
from rag.llm.context.builder import prepare_context
from rag.llm.generation.answering import generate_answer
from rag.llm.providers.client import RAGClient
```

`goals-v1`: prepare_context → Draft gọn → kiểm tra envelope/ID/scope → Review batch
các job tổ tiên, mã và claim → chốt thời điểm/số đo/phụ thuộc → render.
`registry-v2`/replay proof: draft/ledger → bind catalogue → review → tổng hợp graph → validators.

Review cha đi theo các mức tổ tiên VERIFIED thực sự phân kỳ trong context, kể cả
qua nhiều HS4. Nghĩa vụ wording/Chú giải/phạm vi không bị xóa để giảm ma trận. Cha
chưa được xác nhận thì chỉ hoãn descendants phụ thuộc; mã tổ tiên không thay mục tiêu.

### Đường proof tương thích (không áp dụng cho goals semantic-v1)

Model định nghĩa graph một lần trong `proof_catalogue`, dùng `proof_key` và
`reason_proof_key`. Wire proof-v2 dùng `root_node` không có target/text/key; backend
gán kết luận từ consumer đang kiểm tra. Mỗi graph v2 chỉ được một consumer tham chiếu;
không đổi target của graph v1 lưu trong replay. `candidate_group_assessments` chia sẻ đánh giá giữa các mã chỉ khi
có cùng điều kiện quyết định; backend mở về từng slot và kiểm tra decisive domain
của mọi thành viên. Không cắt mã đối chứng rồi coi là đã loại.

Wire ledger chọn `fact_id` đã đăng ký với `source_mode=STATEMENT`; backend lấy nguyên
statement để điền quote/value. Model không phải chép lại lời người dùng. Ledger giữ
giá trị nguyên văn, item, polarity, modality, turn, position và quan hệ
supersedes. UNKNOWN không trở thành False. Đính chính phải cùng thuộc tính/chủ thể,
có nguồn và ở vị trí sau; không có quy tắc tự chọn lời khai cuối cùng khi còn xung đột.

Proof graph có ATOM, ALL, ANY, NOT, SCOPE, EXCEPT, COMPARE. Backend kiểm tra chu trình,
root, nguồn, span, ledger và scope rồi tính trạng thái. UNKNOWN hợp lệ có thể hạ
assessment trước repair; chỉ sinh câu hỏi khi có entry UNKNOWN đúng thuộc tính và
điều kiện nguồn. Proof thiếu/sai không tự thành câu hỏi hoặc gap pháp lý.

Các guard thuộc tính/cơ chế chuyên biệt cũ đã chuyển sang
[fixture lịch sử](../../tests/support/legacy_grounding.py), không còn import trong runtime.
`application_rules.py` vẫn giữ cách lấy nguồn quy tắc hiện có theo yêu cầu đóng băng
retrieval/context source selection; nó không xác nhận thuộc tính thay proof graph.

Slot/ma trận/span lỗi được cô lập theo owner. Nhóm lỗi binding/coverage còn lại bị
withhold; repair chỉ xem xét phần ngữ nghĩa còn lỗi và còn ngân sách. Canonicalize
chỉ bỏ reference lặp hoặc chuẩn hóa định dạng mã vào đúng miền đã đăng ký.
Tham chiếu proof cục bộ sai được trả lại model sửa trước khi decode consumer;
placeholder rỗng không tạo lỗi coverage phụ. Việc sửa dùng ngân sách hiện có,
không tự clone graph để chứng minh một mệnh đề khác.

## Trace và giới hạn

- `request_contract`: schema thực gửi, hash và native-schema/JSON-wrapper mode.
- `validation_issues`: code, path, cause, owner, safe_action và phase.
- `slot_coverage`: VALIDATED hoặc UNREVIEWED; không đồng nghĩa đúng pháp lý.
- `prerequisite_reviews`: chuỗi đánh giá cha nội bộ trong generation trace.
- Goals: `reasoning_contract=semantic-v1`, `proof_contract_version=null`, scope hiệu lực và review coverage.
- Đường proof tương thích: `proof_contract_version=proof-v2`, `fact_ledger`, `proof_catalogue`, `proof_adjustments`.
- `repair_disposition`: phần bị giữ lại và phần cần model xem xét lại.
- `transport_timeout`/`transport_connection_error`: phân biệt lỗi kết nối với HTTP 503.
- `transport_attempts`/`transport_retries`: tối đa hai lần thử lại cùng payload/model,
  chờ 2 và 5 giây cho 503/timeout/kết nối; không sửa JSON hay chuyển model trong retry.
  `CLIPROXYAPI_TRANSPORT_RETRIES` nhận 0–2, mặc định 2. Mỗi lần vẫn có timeout riêng;
  ba lần với timeout 60 giây có thể mất khoảng 187 giây, chưa có deadline tổng.

Ngân sách goals-v1 vẫn tối đa năm request sau planner, gồm review cha/repair/recovery.
Model vẫn chịu trách nhiệm phân rã ngữ nghĩa và kiểm tra entailment/độ đầy đủ. Graph
hợp lệ không chứng minh mọi cách diễn giải pháp lý đều đúng. COMPARE hỗ trợ Decimal
và đơn vị tường minh giống nhau; các phép đổi đơn vị không nhận diện được không được
tự suy. Guard định lượng cũ vẫn kiểm tra những nhóm đơn vị đã hỗ trợ.
Chưa tự nâng model hoặc thêm verifier call. Nhiều proof có thể làm tăng output hoặc
hết ngân sách; thiếu kiểm tra thì chưa phát hành kết luận phụ thuộc.

Bản đồ di chuyển và báo cáo triển khai nằm trong
[artifact triển khai](../../artifacts/wire-contract-implementation-20261021/report.md).

Bản triển khai proof-v1: [báo cáo](../../artifacts/general-proof-implementation-20261021/report.md).
