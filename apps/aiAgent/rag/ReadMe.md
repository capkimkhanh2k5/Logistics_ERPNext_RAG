# Package RAG

Luồng theo mục tiêu dùng thêm `retrieval/request_plan.py`, `retrieval/evidence_recovery.py` và các module `llm/context/task_context.py`, `llm/validation/task_validation.py`, `llm/generation/task_generation.py`, `llm/generation/recovery.py`. Prompt/schema nằm tại `prompts/generation/task_answering.py`. [Contract và giới hạn](../docs/GenerationFlow/GenerationFlow.md) mô tả quan hệ với `registry-v2` và đường tương thích giao thức.

Code được nhóm theo chức năng. Các thư mục ở đây là Python package; import từ module cụ thể để thấy rõ phụ thuộc. Cấu hình nằm ngoài runtime package tại `config/`; dữ liệu và kết quả thực nghiệm giữ nguyên vị trí.

```text
rag/
├── __init__.py
├── __main__.py                 # python -m rag
├── ingestion/
│   ├── sources.py              # Manifest, adapters và chuẩn hóa records/NODE/EDGE
│   ├── audit.py                # Kiểm tra nguồn, PDF, wording và provenance
│   ├── pdf_graph.py            # Trích cấu trúc bảng từ hình học PDF
│   ├── pdf_wording.py          # Bản chép đã đối chiếu ảnh và lớp chữ PDF gốc
│   ├── provenance.py           # Kiểm tra tương thích fingerprint khi chuyển package
│   └── provenance_relocations.json
├── chunking/
│   └── corpus.py               # Ghép ngữ cảnh nguồn, build/load corpus và snapshot
├── embedding/
│   ├── bge_m3.py               # Dense/sparse/ColBERT vectors và cache
│   └── validation.py           # Kích thước, giá trị và chuẩn hóa vector
├── vectordb/
│   └── postgres.py             # Kết nối, migration, nạp snapshot và pgvector
├── retrieval/
│   ├── retriever.py            # Hybrid retrieval, RRF và các API tìm kiếm
│   ├── unified.py              # Pool nguồn chung, cascade và source package
│   └── rerankers.py            # CrossEncoder M3/Qwen/Gemma và ColBERT scoring
├── graph/
│   ├── context.py              # Hierarchy, Notes và graph context có nguồn
│   └── legal_evidence.py       # Binding wording pháp lý và các cấp HS
├── prompts/                   # Xem prompts/README.md
│   ├── core/                  # Policy, system, wire, repair và provider format
│   ├── generation/            # Chỉ dẫn sinh kết quả theo tác vụ/mục tiêu
│   ├── review/                # Product và decision review
│   ├── schemas/               # Contract, trạng thái và slot động
│   ├── planning/              # Query/turn planning và hội thoại
│   └── retrieval/             # Instruction/template reranking
├── llm/                       # Xem llm/README.md
│   ├── providers/             # Client, gateway, Groq, budget và schema trace
│   ├── context/               # Đóng gói nguồn, mục tiêu và hội thoại
│   ├── generation/            # Generation, shortlist và recovery
│   ├── review/                # Ma trận, slot, tổ tiên, đối chứng và claims
│   ├── evidence/              # Registry, spans, citation và proof binding
│   ├── validation/            # Guard đầu ra, scope, grounding và định lượng
│   └── contracts/             # Lỗi và metadata diagnostic
├── api/
│   └── cli.py                  # Giao diện terminal HS/QA; chưa có HTTP API
└── utils/
    ├── files.py                # Hash nội dung, JSON/JSONL và ghi JSON atomic
    └── codes.py                # Chuẩn hóa định dạng mã HS
```

`chunking/corpus.py` giữ chiến lược ghép các đơn vị nguồn hiện tại, gồm GIR, điều/khoản TT85 và biểu thuế. Nó không bổ sung một thuật toán cắt văn bản mới.

Bản đồ module: [LLM](llm/README.md) và [prompt/schema](prompts/README.md).

## Luồng và ranh giới

Build knowledge base: `ingestion` → `chunking` → `embedding` → `vectordb`.

Phục vụ câu hỏi: `api/cli.py` → `QueryPlanner.plan_turn` (nhận diện + từ khóa trong cùng request) → `retrieval` + `graph` → `llm/context/builder.py` + `prompts` → `llm/generation/answering.py` → `llm/validation/answer.py`.

Terminal dùng `QueryPlanner.plan_turn(...)`: lệnh `/new <câu hỏi>`/`/add <dữ kiện>` và tiền tố chỉ định được backend ưu tiên; lượt đầu không cần model nhận diện. Các lượt cần suy luận dùng `TURN_PLANNING_PROMPT`/`TURN_PLAN_SCHEMA` để trả `NEW_QUESTION`, `FOLLOW_UP` hoặc `CLARIFY` cùng `terms` trong một request, giữ nguyên client và chính sách model của phiên. Input chỉ gồm câu hỏi đang hoạt động, bổ sung nguyên văn, câu hỏi làm rõ đã qua validation và tin nhắn mới; không nhận câu trả lời, mã ứng viên hay nguồn cũ làm dữ kiện. `llm/context/conversation.py` chỉ xử lý chỉ định rõ ràng, kiểm tra schema/anchor và chọn lời người dùng theo action; không gọi LLM. Anchor chỉ kiểm tra nguồn gốc trích đoạn, chưa chứng minh ngữ nghĩa đúng.

`NEW_QUESTION` xóa dữ kiện và kết quả cũ trước retrieval; từ khóa phải neo vào tin nhắn mới. Lỗi xử lý câu hỏi mới không khôi phục câu hỏi cũ; `/retry` dùng câu hỏi mới. `FOLLOW_UP` ghép thêm lời người dùng qua `compose_query`, giữ các lượt đính chính để model đọc theo thứ tự. `CLARIFY`, lỗi provider/JSON/quyết định/anchor hoặc JSON đầu vào định tuyến vượt 16.000 ký tự giữ nguyên câu hỏi/kết quả đang hoạt động và yêu cầu chỉ định bằng lệnh; không cắt ngữ cảnh để suy đoán. Quyết định hợp lệ nhưng `terms` lỗi/thiếu thì dùng câu hỏi gốc đã chọn đúng phạm vi, không gọi model lần hai. `/retry` không nhận diện lại, dùng cache plan khi cùng câu hỏi và cấu hình; `/sources`, `/details` và `/model` không gọi LLM. Chẩn đoán `conversation_routing` không đi vào registry dữ kiện hoặc gói nguồn. Ngữ cảnh chỉ lưu trong phiên terminal; chưa có HTTP API, lưu hội thoại qua restart hoặc bộ nhớ liên phiên. Notebook kịch bản có bổ sung khai báo sẵn giữ đường replay xác định.

Terminal hiển thị Hội thoại, Retrieval, Reranking, LLM và Validation. Thời gian request nhận diện + từ khóa nằm một lần trong `query_planning_ms` thuộc Retrieval; `conversation_routing.elapsed_ms` bằng 0 cho lượt dùng chung request. `/details` giải thích rõ việc dùng chung, không in lặp usage. LLM gồm sinh, sửa lỗi, Product Review và Decision Review, kể cả thời gian provider lỗi trước fallback; đóng gói context được đo riêng. Khi chưa kết luận được, mã ứng viên và nguồn chẩn đoán lấy từ context có thể hiển thị cùng lý do; đây chưa phải đề xuất HS. `/sources` mở nguồn hiện tại để đối chiếu mà không gọi model lại.

Model đã có trong [registry giới hạn](../config/model_limits.py) dùng token budget riêng. `context.py` giữ nguyên bộ nguồn/ứng viên; `budget.py` kiểm tra system + user + schema + wrapper trước từng request main, review, repair và fallback. Không tự cắt hay đóng gói lại nguồn cho fallback nhỏ hơn. `MAX_OUTPUT_TOKENS=model` dùng mức output của model; số nguyên vẫn được hỗ trợ. Context dùng chung như GPT-OSS 120B giảm output theo phần còn lại. Alias chưa biết và caller legacy giữ đường cấu hình tương thích cũ; xem [cấu hình](../config/README.md).

`CONSERVATIVE_UTF8_BOUND` là ước lượng bảo thủ bằng byte UTF-8, không phải tokenizer chính xác. `/details` hiển thị budget toàn request và usage provider riêng để tránh nhầm ước lượng với tiêu thụ thực tế.

Luồng v5 vẫn dùng một policy chung: hybrid toàn nguồn → graph context → pool theo ID → M3 → Qwen. `intent="auto"`, `"product"`, `"qa"` chỉ là hint; không thay candidate pool/ranking. `matches` trả Top-10 nguồn, `hs_candidates` chiếu tối đa 10 mã HS8 từ ranked pool; `package` giữ các nguồn sơ cấp có citation. Retrieval không tự chốt mã HS.

Terminal và notebook generation dùng `QueryPlanner(client)` để diễn giải từ khóa tìm nguồn từ toàn bộ câu hỏi và các lượt bổ sung. Prompt/schema nằm ở [prompts/planning/query_planning.py](prompts/planning/query_planning.py), không tra danh sách hãng, loại hàng hoặc thuộc tính viết sẵn. Mỗi từ khóa phải có anchor nguyên văn trong câu hỏi; schema và code chặn mã số, điều kiện số học, nhãn citation hoặc đầu ra lỗi. Loại hàng diễn giải vẫn là giả thuyết của model, chưa phải dữ kiện được xác minh.

Luồng mới: câu hỏi gốc + một truy vấn có từ khóa bổ sung → chạy cả hai trên cùng các kênh retrieval → hợp nhất theo source ID, chia cơ hội giữa truy vấn gốc và truy vấn mở rộng trong từng kênh → pool chung → M3 → Qwen. Xếp hạng dùng câu hỏi gốc kèm các từ khóa; semantic intent vẫn chỉ là advisory dựa trên câu hỏi gốc. Trọng số, ngân sách nguồn, model và instruction reranker trong policy đã khóa giữ nguyên. Đây là thay đổi luồng truy vấn, không phải kết quả đánh giá lại policy cũ. Câu hỏi/phủ định/mã do người dùng cung cấp không bị thay bằng bản diễn giải.

Từ khóa tìm kiếm chỉ nằm trong chẩn đoán `query_plan`; không đi vào `user_context`, messages trả lời, citation hoặc bằng chứng pháp lý. Model diễn giải dùng chung chính sách model của client; mặc định chỉ gọi model đang chọn. Với `plan(query)` stateless hoặc lượt đã được backend chỉ định, lỗi provider/schema/anchor/đầu ra bị cắt vẫn tìm bằng câu hỏi gốc; với lượt chưa rõ quan hệ, lỗi quyết định phải dừng trước retrieval. Không cache lỗi tạm thời. `/retry` dùng lại plan hợp lệ trong bộ nhớ; thêm dữ kiện, đổi model hoặc sửa prompt/schema làm đổi khóa cache. Quyết định hội thoại không lấy từ cache theo riêng tin nhắn mới: luôn xét cả ngữ cảnh và câu hỏi làm rõ hiện tại. `/details` hiển thị từ khóa, model, usage và thời gian request chung **nằm trong Retrieval**; LLM ở dòng đo các bước là các cuộc gọi tạo/kiểm tra câu trả lời. Nhánh đề xuất HS thông thường còn 3 request (chuẩn bị, trả lời, Product Review), trước repair/fallback.

API cấp thấp `Retriever(conn, embedder)` và `unified_search(query)` giữ tìm kiếm gốc để chạy offline/replay policy. Notebook/script tiếp tục khởi tạo `Retriever(conn, embedder, query_planner=QueryPlanner(client))` và gọi `routed_search(query)` để tự lập plan stateless. Terminal gọi `plan_turn` trước rồi truyền `routed_search(query, query_plan=plan)`; retrieval kiểm tra hash câu hỏi, fingerprint cấu hình và nội dung truy vấn/từ khóa trước khi dùng, không lập plan lần hai. Plan khác câu hỏi hoặc cấu hình bị từ chối trước retrieval. Cache generation đánh dấu riêng hash prompt/schema/cấu hình model của planner, gồm prompt/schema hội thoại mới. Chạy đối chiếu retrieval trên corpus chỉ đọc bằng `python scripts/diagnose_retrieval_flow.py --queries <queries.json> --out <report.json>`; file truy vấn là danh sách `{id, query}`. Đây là chẩn đoán ứng viên/nguồn, không tự chốt tính đúng pháp lý hoặc đo chất lượng trên holdout.

LLM chỉ hỏi người dùng về dữ kiện hàng hóa/hồ sơ còn thiếu qua `MISSING_PRODUCT_INFO`. Thiếu wording, GIR, Notes hoặc quan hệ HS phải trả `INSUFFICIENT_LEGAL_EVIDENCE`; không yêu cầu người dùng bổ sung luật. Đề xuất HS vẫn cần hierarchy `CONTAINS` đã xác minh và đủ nhãn citation bắt buộc. Các kiểm tra này nằm trong code, ngoài system prompt.

`llm/review/disambiguation.py` lấy các mã đối chứng HS8 từ subtree HS6 đã được graph xác minh, tối đa thêm 160 mã. `context.py` đóng gói nguồn/điều kiện nhánh và ghi `candidate_comparison` cùng `missing_codes`. `comparison_candidates` giữ mã đối chứng ngoài Top-10; chúng không được thêm vào `allowed_hs_codes`. Phần model xem chỉ giữ code/wording/điều kiện nhánh của mã đối chứng để giảm metadata lặp; backend vẫn giữ hierarchy đầy đủ. Độ đầy đủ là trong subtree được kiểm tra, không đại diện toàn database hay các quy tắc pháp lý khác.

Khi có phạm vi so sánh, Product Review dùng `MODEL_DISAMBIGUATION_REVIEW_SCHEMA` trong cùng request hiện có. Bảng đánh giá phải phủ đủ shortlist retrieval (kể cả khác phân nhóm) và mã cùng cấp của ứng viên đề xuất, loại mã bằng dữ kiện có trích đoạn và điều kiện của nhánh đó. Nhóm `parent_code=""` ghi shortlist chung; nhóm HS6 ghi đối chứng từ graph. Các kiểm tra thuộc tính mở phải bao phủ điều kiện nhánh đối chứng; `MISSING` không được giả có dữ kiện xác nhận, và phải gắn câu hỏi đúng thuộc tính/nguồn. `SUPPORTED` chỉ được giữ khi còn duy nhất mã đề xuất, các chiều phân nhánh đã biết và coverage đầy đủ. Phản hồi bỏ sót hoặc sai tham chiếu được repair một lần rồi chặn an toàn nếu vẫn sai. Decision Review cũng nhận phạm vi so sánh để phân biệt thiếu thuộc tính với thiếu nguồn.

Không có bước LLM riêng cho Missing Attribute Detection/Candidate Disambiguation. Context có thể lớn hơn và phát sinh thêm token hoặc repair; các kiểm tra cấu trúc/provenance không thay thế đánh giá ngữ nghĩa. Ca kiểm chứng và giới hạn nằm ở [docs/GenerationFlow/GenerationFlow.md](../docs/GenerationFlow/GenerationFlow.md).

Context mới dùng `registry-v2`: `user_context.statements` lưu lời người dùng theo thứ tự lượt và các trích đoạn nguyên văn có ID. Không tự gán loại hàng, thuộc tính, trạng thái đúng/sai hoặc tài liệu nhà sản xuất. Main, Product Review và Decision Review dùng chung ngữ cảnh này. Model chịu trách nhiệm đọc ý nghĩa, chủ thể, phủ định, mức độ chắc chắn, mâu thuẫn và đính chính; ID chỉ xác nhận nguồn gốc lời nói.

Các nhận định dùng `evidence_ids` và `fact_ids` (ID lời người dùng); backend dựng `[S#]`, trích đoạn nguồn và citations. Product Review kiểm tra cả câu trả lời nháp và từng điều kiện của ứng viên, dùng `user_quotes` lấy đúng từ các ID lời người dùng đã tham chiếu. Backend chặn trích đoạn không có trong nguồn gốc đó, kiểm tra cấu trúc, nguồn/citation và ancestry. Kiểm tra định lượng giữ các phép so sánh số đo/đơn vị dùng chung; không nhận diện hãng, bộ phận hoặc thuộc tính theo một danh mục sản phẩm. Đối chiếu ngữ nghĩa vẫn là đánh giá của model, không phải chứng minh pháp lý tự động.

`clarifications.attribute` là tên thuộc tính mở do điều kiện trong nguồn xác định. `product_type` và `question_scope` là hai vai trò chung cho nhận diện đối tượng/phạm vi câu hỏi và có thể không cần nguồn; thuộc tính khác phải có `evidence_ids`. Model chỉ hỏi dữ kiện thực sự ảnh hưởng lựa chọn hoặc điều kiện bắt buộc, không hỏi lại điều đã rõ. Đã xóa các cấu hình nhận diện theo danh mục, tham chiếu thông số theo dòng sản phẩm, parser Product Fact và nhãn thuộc tính cố định trong CLI. Mở rộng phạm vi pháp lý vẫn cần corpus phù hợp; chỉ thêm corpus không đảm bảo model đã đối chiếu đúng mọi trường hợp.

Ngữ cảnh `registry-v1` cần được dựng lại; runtime từ chối rõ ràng thay vì tái sử dụng dữ kiện nhận diện/tham chiếu tự động cũ. Contract kết quả công khai `ANSWER_SCHEMA` giữ nguyên; fixture pre-registry vẫn kiểm tra đường replay công khai cũ và các chốt nguồn/số đo. Sơ đồ từ câu hỏi đến câu trả lời: [GenerationFlow.md](../docs/GenerationFlow/GenerationFlow.md), Retrieval được gom thành một khối.

Toàn bộ chỉ dẫn tác vụ, sửa lỗi, định dạng provider và template Qwen do ứng dụng định nghĩa được quản lý tại [prompts/README.md](prompts/README.md). Các module xử lý import template từ đó; policy JSON giữ bản chụp instruction để đối chiếu cấu hình đã khóa.

## Lệnh và import

Chạy từ thư mục `aiAgent`:

```bash
.venv/bin/python -m rag
.venv/bin/python -m rag --model 3.8-high
.venv/bin/python -m rag --model 120b
.venv/bin/python -m rag --help
```

Không chọn thì dùng `3.5-lite-high`. `/model` hiển thị ba lựa chọn trong phiên; `/model 1|2|3` đổi model nhưng giữ dữ kiện, `/retry` chạy lại. Preset và reasoning tương ứng được quản lý tại `config/settings.py`; [cấu hình model](../config/README.md) giải thích fallback và độ ưu tiên so với `.env`.

Import theo vị trí mới:

```python
from rag.chunking.corpus import build_corpus, load_corpus
from rag.embedding.bge_m3 import Embedder
from rag.ingestion.audit import audit
from rag.llm.generation.answering import generate_answer
from rag.llm.context.builder import prepare_context
from rag.prompts.core.system import SYSTEM_PROMPT
from rag.retrieval.retriever import Retriever
from rag.vectordb.postgres import connect
```

Các đường dẫn cũ như `rag.data`, `rag.answering`, `rag.db` và lệnh `python rag/demoRAG.py` đã được thay thế. Scripts, tests và source cells trong cả ba notebook dùng đường dẫn mới.

## Provenance và thực nghiệm

Việc đổi import làm thay đổi SHA-256 của hai processor PDF. `ingestion/provenance_relocations.json` ghi đúng cặp fingerprint trước/sau và hash AST của các hàm xử lý giữ nguyên. `same_processor()` chỉ chấp nhận cặp đã đăng ký; thay code khác, version hoặc thư viện PDF vẫn bị từ chối. Fingerprint hiện tại luôn được tính từ file hiện tại. Các proof nguồn đã lưu không bị sửa.

Cấu hình E0, nguồn chuẩn hóa, corpus snapshot, embeddings và prompt/schema không đổi. Báo cáo/checkpoint cũ giữ nguyên để bảo toàn lịch sử. Các benchmark khóa hash code cần một run ID mới khi chạy với code sau refactor; không trộn checkpoint từ hai phiên bản code.

Gold, metrics, quét trọng số và kịch bản notebook nằm tại [tests/support/](../tests/support/README.md), cấu hình tại [config/](../config/README.md). Runtime không import các module kiểm thử. Xem [README-RAG.md](../README-RAG.md) để cài đặt và vận hành.
