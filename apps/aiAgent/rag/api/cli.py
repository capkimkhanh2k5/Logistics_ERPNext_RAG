"""Interactive terminal demo for HS/QA retrieval and grounded LLM answers."""

import argparse
import math
import os
import shutil
import sys
import textwrap
import time
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from config.settings import DEFAULT_MODEL_PRESET, MODEL_PRESETS  # noqa: E402
from rag.embedding.bge_m3 import Embedder  # noqa: E402
from rag.llm.answering import generate_answer
from rag.llm.budget import ContextBudgetError
from rag.llm.client import RAGClient
from rag.llm.context import compose_query, load_generation_graph, prepare_context
from rag.llm.conversation import turn_context
from rag.llm.errors import LLMError
from rag.llm.recovery import recover_answer
from rag.retrieval.query_planning import QueryPlanner
from rag.retrieval.retriever import Retriever  # noqa: E402
from rag.vectordb.postgres import connect  # noqa: E402

INTRO = """RAG Demo
Nhập câu hỏi để bắt đầu. Dùng /help để xem các lệnh."""

HELP = """Tự nhận diện câu hỏi mới hoặc thông tin bổ sung cho câu hỏi đang xét.
/new      Bắt đầu câu hỏi mới; /new <câu hỏi> để hỏi ngay
/add <dữ kiện>  Bổ sung hoặc đính chính cho câu hỏi đang xét
/retry    Thử lại với dữ kiện hiện tại
/sources  Xem trích đoạn và vị trí nguồn của câu trả lời vừa rồi
/details  Xem model, thời gian và thông tin kiểm tra
/model    Xem model hiện tại và các lựa chọn; /model <mã hoặc số> để đổi
/help     Xem hướng dẫn
/exit     Thoát (hoặc Ctrl+C / Ctrl+D)"""

STATUSES = {
    "ANSWERED": "Đã trả lời",
    "RECOMMENDATION": "Đề xuất mã HS",
    "MISSING_PRODUCT_INFO": "Cần bổ sung thông tin",
    "INSUFFICIENT_LEGAL_EVIDENCE": "Chưa đủ chứng cứ pháp lý",
    "REQUIRES_REVIEW": "Cần thẩm định thêm",
}
MODEL_SHORTCUTS = {"1": "3.8-high", "2": "3.5-lite-high", "3": "120b"}


def _write_text(text: str, write=print, *, prefix: str = "") -> None:
    width = max(20, min(shutil.get_terminal_size((90, 24)).columns - 2, 88))
    for i, line in enumerate(text.splitlines() or [""]):
        write(
            textwrap.fill(
                line,
                width=width,
                initial_indent=prefix if i == 0 else " " * len(prefix),
                subsequent_indent=" " * len(prefix),
                break_on_hyphens=False,
            )
        )


def _source_location(source: dict) -> str:
    locator = source.get("locator", {})
    details = [str(locator.get("document") or source.get("label") or "Nguồn")]
    if locator.get("physical_pages"):
        details.append("trang PDF " + ", ".join(map(str, locator["physical_pages"])))
    elif locator.get("physical_page") is not None:
        details.append(f"trang PDF {locator['physical_page']}")
    if locator.get("printed_page") is not None:
        details.append(f"trang in {locator['printed_page']}")
    return " | ".join(details)


def _additional_items(answer: str, items: list[str]) -> list[str]:
    normalized = " ".join(answer.casefold().split())
    return [
        item
        for item in dict.fromkeys(items)
        if " ".join(item.casefold().split()).rstrip(".?!;:") not in normalized
    ]


def _current_model_label(client) -> str:
    key = getattr(client, "model_preset", None)
    preset = MODEL_PRESETS.get(key) if isinstance(key, str) else None
    return preset.label if preset is not None else getattr(client.config, "model", "Chưa xác định")


def _model_command(client, choice: str, write) -> bool:
    if not choice:
        _write_text("Model hiện tại: " + _current_model_label(client), write)
        for number, key in MODEL_SHORTCUTS.items():
            flags = []
            if key == getattr(client, "model_preset", None):
                flags.append("đang dùng")
            if key == DEFAULT_MODEL_PRESET:
                flags.append("mặc định")
            suffix = " (" + ", ".join(flags) + ")" if flags else ""
            _write_text(f"{number}. {MODEL_PRESETS[key].label} · {key}{suffix}", write, prefix="  ")
        write("Dùng /model <mã hoặc số> để đổi; dữ kiện câu hỏi được giữ lại.")
        return False
    selected = MODEL_SHORTCUTS.get(choice, choice)
    if selected not in MODEL_PRESETS:
        write("Model không hợp lệ. Dùng /model để xem các lựa chọn.")
        return False
    selector = getattr(client, "select_model", None)
    if not callable(selector):
        write("Phiên này chưa hỗ trợ đổi model. Khởi động lại với --model " + selected + ".")
        return False
    try:
        selector(selected)
    except ValueError:
        write("Chưa đổi được model. Dùng /model để xem các lựa chọn.")
        return False
    _write_text("Đã chọn model: " + _current_model_label(client), write)
    write("Dữ kiện câu hỏi được giữ lại. Dùng /retry để chạy với model vừa chọn.")
    return True


def _write_errors(errors: list[str], write) -> None:
    safe = (
        "Phản hồi không đúng cấu trúc JSON bắt buộc." if error.startswith("/") else error
        for error in errors
    )
    for error in dict.fromkeys(safe):
        _write_text(error, write, prefix="  - ")


def _diagnostics(context: dict, generated: dict) -> dict:
    if not generated["validation"]["valid"] or generated["answer"]["status"] not in {
        "REQUIRES_REVIEW",
        "MISSING_PRODUCT_INFO",
        "INSUFFICIENT_LEGAL_EVIDENCE",
    }:
        return {}
    diagnostics = generated.get("diagnostics") or {}
    candidate = diagnostics.get("candidate_hs_code", "")
    return {
        **diagnostics,
        "candidate_hs_code": candidate
        if isinstance(candidate, str)
        and len(candidate) == 8
        and candidate.isdigit()
        and candidate in context.get("allowed_hs_codes", [])
        else "",
    }


def _visible_sources(context: dict, generated: dict) -> list[dict]:
    labels = [citation["label"] for citation in generated["answer"]["citations"]]
    labels.extend(_diagnostics(context, generated).get("source_labels", []))
    sources = {source["label"]: source for source in context["sources"]}
    return [sources[label] for label in dict.fromkeys(labels) if label in sources]


def _duration(milliseconds) -> str:
    if (
        not isinstance(milliseconds, (int, float))
        or isinstance(milliseconds, bool)
        or not math.isfinite(milliseconds)
        or milliseconds < 0
    ):
        return "chưa đo"
    return f"{milliseconds:.1f}ms" if milliseconds < 1000 else f"{milliseconds / 1000:.2f}s"


def _show_stage_timings(context: dict, generated: dict, write) -> None:
    retrieval = context.get("retrieval_timings") or {}
    generation = generated.get("timings") or {}
    stages = [
        ("Retrieval", retrieval.get("retrieval_ms")),
        ("Reranking", retrieval.get("reranking_ms")),
        ("LLM", generation.get("llm_ms")),
        ("Validation", generation.get("validation_ms")),
    ]
    if context.get("conversation_routing"):
        stages.insert(0, ("Hội thoại", context["conversation_routing"].get("elapsed_ms")))
    _write_text(
        "Đo từng bước: " + " · ".join(f"{label} {_duration(value)}" for label, value in stages),
        write,
    )


def _show_request_budget(budget: dict, label: str, write) -> None:
    if not budget:
        return
    input_tokens = budget.get("input_tokens")
    input_limit = budget.get("input_limit")
    measured = str(input_tokens) if input_tokens is not None else "chưa đo"
    capacity = f"/{input_limit}" if input_limit is not None else " (chưa biết giới hạn)"
    _write_text(
        f"{label}: {measured}{capacity} token ước tính · {budget.get('mode', 'chưa xác định')}",
        write,
    )
    output = budget.get("output_tokens")
    maximum = budget.get("max_output_tokens")
    if output is not None:
        maximum_text = f"/{maximum}" if maximum is not None else ""
        _write_text(f"Ngân sách output: {output}{maximum_text} token", write)
    if budget.get("shared_context"):
        context_limit = budget.get("context_limit")
        remaining = budget.get("remaining_context_tokens")
        _write_text(
            "Context dùng chung input/output: "
            + (str(context_limit) if context_limit is not None else "chưa xác định")
            + " token · Còn sau input: "
            + (str(remaining) if remaining is not None else "chưa đo"),
            write,
        )


def show_sources(context: dict, generated: dict, write=print) -> None:
    if not generated["validation"]["valid"]:
        write("Chưa có câu trả lời hợp lệ để hiển thị nguồn.")
        return
    citations = {citation["label"]: citation for citation in generated["answer"]["citations"]}
    sources = _visible_sources(context, generated)
    if not sources:
        write("Câu trả lời này chưa có nguồn trích dẫn.")
        return
    write("\nTrích dẫn nguồn")
    for source in sources:
        label = source["label"]
        _write_text(_source_location(source), write, prefix=f"[{label}] ")
        if label in citations:
            _write_text(citations[label]["quote"], write, prefix="  ")
        else:
            _write_text("Nguồn dùng để kiểm tra ứng viên; chưa phải kết luận phân loại.", write)
            _write_text(source["text"], write, prefix="  ")
        _write_text(f"ID: {source['id']}", write, prefix="  ")
        write("")


def _show_decision_review(review: dict, write) -> None:
    write(
        "Kiểm tra trạng thái phân loại: " + ("Hợp lệ" if review.get("valid") else "Cần thẩm định")
    )
    if review.get("model"):
        _write_text("Model kiểm tra trạng thái: " + review["model"], write)
    result = review.get("review")
    reason = review.get("reason") or (result.get("reason") if isinstance(result, dict) else None)
    if review.get("valid") and isinstance(reason, str) and reason.strip():
        _write_text(reason, write, prefix="  ")
    _write_errors(review.get("errors", []), write)
    if review.get("request_budget"):
        _show_request_budget(review["request_budget"], "Yêu cầu kiểm tra trạng thái", write)
    if review.get("usage"):
        _write_text(
            "Token kiểm tra trạng thái theo provider: "
            + ", ".join(f"{key}={value}" for key, value in review["usage"].items()),
            write,
        )


def show_details(
    context: dict, generated: dict, elapsed: float, write=print, *, show_timings: bool = True
) -> None:
    generation = generated["generation"]
    model = generation.get("model") or "Không gọi LLM (không có nguồn)"
    fallback = " — đã dùng model dự phòng" if generation.get("fallback_used") else ""
    write("\nThông tin kỹ thuật")
    _write_text(f"Model: {model}{fallback}", write)
    write(f"Thời gian: {elapsed:.1f}s")
    if show_timings:
        _show_stage_timings(context, generated, write)
    routing = context.get("conversation_routing")
    if routing:
        _write_text(f"Nhận diện hội thoại: {routing['action']} · {routing['method']}", write)
        if routing.get("shared_with_query_plan"):
            _write_text(
                "Nhận diện và diễn giải dùng chung một request (nằm trong Retrieval).", write
            )
        elif routing.get("generation"):
            route_generation = routing["generation"]
            _write_text(
                f"Model hội thoại: {route_generation.get('model', 'chưa rõ')} · "
                f"usage: {route_generation.get('usage', {})}",
                write,
            )
    retrieval_timings = context.get("retrieval_timings") or {}
    if retrieval_timings:
        _write_text(
            f"M3: {_duration(retrieval_timings.get('m3_ms'))} · "
            f"Qwen: {_duration(retrieval_timings.get('qwen_ms'))} · "
            f"Tổng truy xuất: {_duration(retrieval_timings.get('total_ms'))}",
            write,
        )
    plan = context.get("query_plan") or {}
    if plan:
        _write_text(
            f"Diễn giải truy vấn: {plan['status']} · "
            f"{_duration(retrieval_timings.get('query_planning_ms'))} · "
            f"cache {'có' if plan.get('cache_hit') else 'không'} (nằm trong Retrieval)",
            write,
        )
        if plan.get("terms"):
            _write_text(
                "Từ khóa tìm nguồn (chưa xác minh dữ kiện): "
                + "; ".join(row["term"] for row in plan["terms"]),
                write,
            )
        if context.get("request"):
            request = context["request"]
            _write_text(
                f"Mục tiêu: {len(request['objectives'])} · Mặt hàng: {len(request['items'])}", write
            )
            for goal in request["objectives"]:
                _write_text(
                    f"{goal['id']}: {goal['kind']} · cấp {goal['level'] or 'không chốt mã'} · {', '.join(goal['item_ids']) or 'hỏi đáp'}",
                    write,
                )
        if plan.get("error"):
            _write_text("Diễn giải không thành công; đã tìm bằng câu hỏi gốc.", write)
        if plan.get("generation"):
            planning_generation = plan["generation"]
            _write_text(
                f"Model diễn giải: {planning_generation.get('model', 'chưa rõ')} · "
                f"usage lần tạo plan: {planning_generation.get('usage', {})}",
                write,
            )
    if "packing_ms" in context:
        _write_text(f"Đóng gói ngữ cảnh: {_duration(context['packing_ms'])}", write)
    generation_timings = generated.get("timings") or {}
    _write_text(
        f"LLM trả lời: {_duration(generation_timings.get('answer_llm_ms'))} · "
        f"LLM kiểm tra dữ kiện: {_duration(generation_timings.get('product_review_llm_ms'))}",
        write,
    )
    if generation.get("decision_review") or generation_timings.get("decision_review_llm_ms"):
        _write_text(
            "LLM kiểm tra trạng thái phân loại: "
            + _duration(generation_timings.get("decision_review_llm_ms")),
            write,
        )
    if generation_timings:
        _write_text(
            "Tổng tạo và kiểm tra câu trả lời: " + _duration(generation_timings.get("total_ms")),
            write,
        )
    for key, label in (("provider", "Provider"), ("http_status", "HTTP"), ("error_code", "Mã lỗi")):
        if key == "http_status" and generation.get("error_code") == "context_length_exceeded":
            continue
        if generation.get(key) is not None:
            _write_text(f"{label}: {generation[key]}", write)
    diagnostics = _diagnostics(context, generated)
    for key, label in (("stage", "Bước cần kiểm tra"), ("code", "Mã chẩn đoán")):
        if diagnostics.get(key):
            _write_text(f"{label}: {diagnostics[key]}", write)
    if "sources" in context:
        _write_text(
            f"Nguồn gửi LLM: {len(context['sources'])} | "
            f"Nguồn bị bỏ: {len(context.get('omitted_source_ids', []))}",
            write,
        )
    if context.get("packing"):
        packing = context["packing"]
        if packing.get("request_budget"):
            _show_request_budget(packing["request_budget"], "Yêu cầu ban đầu", write)
            _write_text(
                f"Ký tự: system {packing['system_chars']} · user {packing['user_chars']} · "
                f"nguồn {packing['source_chars']} · schema {packing['schema_chars']}",
                write,
            )
        else:
            for key, cap, label in (
                ("input_chars", "max_input_chars", "Ngữ cảnh gửi LLM"),
                ("source_chars", "max_context_chars", "Gói nguồn"),
            ):
                capacity = f"/{packing[cap]}" if packing.get(cap) is not None else ""
                _write_text(f"{label}: {packing[key]}{capacity} ký tự", write)
        _write_text(
            "Ứng viên HS trong ngữ cảnh: " + (", ".join(context["allowed_hs_codes"]) or "Không có"),
            write,
        )
        if packing["omitted_candidate_codes"]:
            _write_text(
                "Ứng viên chưa đưa vào gói: " + ", ".join(packing["omitted_candidate_codes"]), write
            )
    for key in ("snapshot", "profile"):
        if context.get(key):
            _write_text(f"{key}: {context[key]}", write)
    if generation.get("request_budget"):
        _show_request_budget(generation["request_budget"], "Yêu cầu model thực tế", write)
    if generation.get("repair_budget_error"):
        _show_request_budget(
            generation["repair_budget_error"], "Yêu cầu sửa phản hồi bị chặn", write
        )
    if generation.get("product_review", {}).get("request_budget"):
        _show_request_budget(
            generation["product_review"]["request_budget"], "Yêu cầu kiểm tra dữ kiện", write
        )
    if generation.get("usage"):
        _write_text(
            "Token theo provider: " + ", ".join(f"{k}={v}" for k, v in generation["usage"].items()),
            write,
        )
    if generation.get("failures"):
        write(f"Số lần lỗi trước khi có phản hồi: {len(generation['failures'])}")
        for index, failure in enumerate(generation["failures"], start=1):
            status = (
                "chặn cục bộ: vượt ngân sách context"
                if failure.get("error_code") == "context_length_exceeded"
                else f"HTTP {failure.get('http_status', 'chưa rõ')}"
            )
            _write_text(
                f"Lần lỗi {index}: {failure.get('model') or 'Không rõ model'} · "
                f"{status} · {_duration(failure.get('elapsed_ms'))}",
                write,
            )
            if failure.get("request_budget"):
                _show_request_budget(failure["request_budget"], f"Ngân sách lần lỗi {index}", write)
    if generation.get("product_review"):
        review = generation["product_review"]
        write("Kiểm tra dữ kiện HS: " + ("Hợp lệ" if review["valid"] else "Cần thẩm định"))
        _write_errors(review.get("errors", []), write)
    if generation.get("task_review"):
        review = generation["task_review"]
        _write_text(
            "Kiểm tra các kết quả phân loại: "
            + ("Hợp lệ" if review.get("valid") else "Chưa hoàn tất"),
            write,
        )
        _write_errors(review.get("errors", []), write)
    if generation.get("recovery"):
        recovery = generation["recovery"]
        _write_text(
            f"Evidence recovery: {recovery.get('rounds', 0)} vòng · {len(recovery.get('new_source_ids', []))} nguồn mới · {recovery.get('reason', 'đã đánh giá lại')}",
            write,
        )
    if "application_calls" in generation:
        _write_text(
            f"Lượt gọi answer/review (gồm recovery): {generation['application_calls']} · còn {generation.get('remaining_calls', 0)} trong ngân sách",
            write,
        )
    if generation.get("decision_review"):
        _show_decision_review(generation["decision_review"], write)
    _write_text(
        "Kiểm tra cấu trúc và nguồn: "
        + ("Hợp lệ" if generated["validation"]["valid"] else "Chưa đạt"),
        write,
    )
    _write_errors(generated["validation"].get("errors", []), write)


def show_answer(
    context: dict, generated: dict, elapsed: float, write=print, *, debug: bool = False
) -> None:
    if not generated["validation"]["valid"]:
        _write_text("\nPhản hồi chưa vượt qua kiểm tra nguồn và cấu trúc.", write)
        _show_stage_timings(context, generated, write)
        _write_text("Dùng /retry để thử lại hoặc /details để xem lỗi kiểm tra.", write)
        if debug:
            show_details(context, generated, elapsed, write, show_timings=False)
        return
    answer = generated["answer"]
    _write_text(f"\nTrạng thái: {STATUSES[answer['status']]} · {elapsed:.1f}s", write)
    _show_stage_timings(context, generated, write)
    write("")
    _write_text(answer["answer"], write, prefix="AI: ")
    if answer["suggested_hs_code"] and answer["suggested_hs_code"] not in answer["answer"]:
        write(f"Mã HS đề xuất: {answer['suggested_hs_code']}")
    if answer["suggested_hs_code"]:
        _write_text("Đề xuất cần người có chuyên môn xác nhận.", write)
    if answer["alternatives"]:
        _write_text("Mã cần cân nhắc thêm: " + ", ".join(answer["alternatives"]), write)
    for heading, items in (
        (
            "Thông tin bạn cần bổ sung:",
            answer["missing_information"] if answer["status"] == "MISSING_PRODUCT_INFO" else [],
        ),
        ("Chứng cứ pháp lý chưa đủ:", answer["missing_legal_evidence"]),
    ):
        additional = _additional_items(answer["answer"], items)
        if additional:
            write("\n" + heading)
            for item in additional:
                _write_text(item, write, prefix="  - ")
    diagnostics = _diagnostics(context, generated)
    if diagnostics.get("candidate_hs_code"):
        _write_text(
            "Ứng viên đang kiểm tra (chưa kết luận): " + diagnostics["candidate_hs_code"], write
        )
    displayed_text = " ".join(
        [answer["answer"], *answer["missing_information"], *answer["missing_legal_evidence"]]
    )
    reasons = _additional_items(displayed_text, diagnostics.get("reasons", []))
    if reasons:
        write("\nLý do cần kiểm tra:")
        for reason in reasons:
            _write_text(reason, write, prefix="  - ")
    sources = _visible_sources(context, generated)
    if sources:
        _write_text(f"\nNguồn ({len(sources)}) · /sources để xem trích đoạn", write)
        for source in sources:
            _write_text(
                _source_location(source),
                write,
                prefix=f"[{source['label']}] ",
            )
    if debug:
        show_sources(context, generated, write)
        show_details(context, generated, elapsed, write, show_timings=False)


@contextmanager
def _runtime_output(debug: bool):
    if debug:
        yield
        return
    with open(os.devnull, "w") as sink, redirect_stdout(sink), redirect_stderr(sink):
        yield


def run_console(retriever, client, graph, *, read=input, write=print, debug: bool = False) -> None:
    question = ""
    supplements: list[str] = []
    needs_product_info = False
    pending_questions: list[str] = []
    planner = getattr(retriever, "query_planner", None)
    if planner is None:
        planner = QueryPlanner(client)
        retriever.query_planner = planner
    last_result: tuple[dict, dict, float] | None = None
    write(INTRO)
    _write_text(f"Model: {_current_model_label(client)} · /model để đổi", write)
    while True:
        prompt = (
            "\nBổ sung thông tin hoặc nhập câu hỏi mới: "
            if needs_product_info
            else "\nCâu hỏi mới hoặc thông tin bổ sung: "
            if question
            else "\nCâu hỏi: "
        )
        try:
            text = read(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            return
        if not text:
            write("Vui lòng nhập nội dung; /exit để thoát.")
            continue
        command = text.lower()
        if command == "/exit":
            return
        if command == "/help":
            write(HELP)
            continue
        if command == "/model" or command.startswith("/model "):
            if _model_command(client, command.removeprefix("/model").strip(), write):
                last_result = None
            continue
        if command in {"/sources", "/details"}:
            if last_result is None:
                write("Chưa có kết quả. Hãy nhập câu hỏi trước.")
            else:
                context, generated, elapsed = last_result
                if command == "/sources":
                    show_sources(context, generated, write)
                else:
                    show_details(context, generated, elapsed, write)
            continue
        if command == "/new":
            question, supplements = "", []
            needs_product_info = False
            pending_questions = []
            last_result = None
            write("Đã bắt đầu câu hỏi mới.")
            continue
        forced_action = None
        verb, *arguments = text.split(maxsplit=1)
        if verb.lower() in {"/new", "/add"}:
            if not arguments:
                write("Dùng /add <dữ kiện> để bổ sung cho câu hỏi đang xét.")
                continue
            if verb.lower() == "/add" and not question:
                write("Chưa có câu hỏi để bổ sung. Hãy nhập câu hỏi trước.")
                continue
            forced_action = "NEW_QUESTION" if verb.lower() == "/new" else "FOLLOW_UP"
            text = arguments[0]
        elif text.startswith("/") and command != "/retry":
            write("Lệnh không hợp lệ. Dùng /help để xem hướng dẫn.")
            continue
        if command == "/retry" and not question:
            write("Chưa có câu hỏi để thử lại.")
            continue

        started = time.perf_counter()
        routing: dict = {"action": "FOLLOW_UP", "method": "RETRY", "elapsed_ms": 0.0}
        next_question, next_supplements = question, supplements
        if (
            command != "/retry"
            and client.config.max_input_chars is not None
            and len(text) > client.config.max_input_chars
        ):
            write(f"Nội dung vượt giới hạn {client.config.max_input_chars} ký tự.")
            continue
        write("Đang chuẩn bị câu hỏi và từ khóa tìm nguồn…")
        try:
            with _runtime_output(debug):
                if command == "/retry":
                    query = compose_query(question, supplements, client.config.max_input_chars)
                    plan = planner.plan(query)
                else:
                    routing, plan = planner.plan_turn(
                        question,
                        supplements,
                        text,
                        pending_questions,
                        forced_action=forced_action,
                        max_chars=client.config.max_input_chars,
                    )
            if routing["action"] == "CLARIFY":
                write(
                    "Chưa xác định được đây là câu hỏi mới hay thông tin bổ sung. "
                    "Ngữ cảnh hiện tại được giữ nguyên. "
                    "Dùng /new <câu hỏi> hoặc /add <dữ kiện> để chỉ định."
                )
                if debug and routing.get("error_code"):
                    write("Nhận diện hội thoại: " + routing["error_code"])
                continue
            if command != "/retry":
                next_question, next_supplements = turn_context(
                    question, supplements, text, routing["action"]
                )
            query = compose_query(next_question, next_supplements, client.config.max_input_chars)
        except KeyboardInterrupt:
            return
        except ValueError:
            write(
                f"Tổng câu hỏi và thông tin bổ sung vượt giới hạn "
                f"{client.config.max_input_chars} ký tự. Hãy rút gọn hoặc dùng /new."
            )
            continue

        if routing["action"] == "NEW_QUESTION":
            if question:
                write("Đã nhận diện câu hỏi mới; bắt đầu với ngữ cảnh riêng.")
            needs_product_info = False
            pending_questions = []
        question, supplements = next_question, next_supplements
        context = {"conversation_routing": routing}
        last_result = None
        try:
            write("Đang tìm nguồn và soạn câu trả lời…")
            with _runtime_output(debug):
                result = retriever.routed_search(query, intent="auto", query_plan=plan)
                context["retrieval_timings"] = dict(result.get("timings") or {})
                packing_started = time.perf_counter()
                context = prepare_context(query, result, "auto", client.config, graph)
                context["conversation_routing"] = routing
                context["packing_ms"] = (time.perf_counter() - packing_started) * 1000
                context["retrieval_timings"] = dict(result.get("timings") or {})
                generated = generate_answer(context, client)
                context, generated = recover_answer(
                    context, generated, result, client, retriever, graph
                )
            elapsed = time.perf_counter() - started
            last_result = context, generated, elapsed
            needs_product_info = (
                generated["validation"]["valid"]
                and generated["answer"].get("status") == "MISSING_PRODUCT_INFO"
            )
            pending_questions = (
                list(generated["answer"].get("missing_information", []))
                if needs_product_info
                else []
            )
            show_answer(context, generated, elapsed, write, debug=debug)
        except ContextBudgetError as exc:
            generated = {
                "generation": {
                    "model": exc.model,
                    "provider": exc.provider,
                    "http_status": exc.status,
                    "error_code": exc.error_code,
                    "request_budget": exc.budget,
                },
                "validation": {"valid": False, "errors": ["Yêu cầu vượt ngân sách ngữ cảnh"]},
                "timings": dict(getattr(exc, "timings", {}) or {}),
            }
            elapsed = time.perf_counter() - started
            last_result = context, generated, elapsed
            write("Yêu cầu vượt giới hạn ngữ cảnh đầu vào của model được gọi.")
            _show_stage_timings(context, generated, write)
            _show_request_budget(exc.budget, f"Ngân sách {exc.model}", write)
            write(
                "Câu hỏi và dữ kiện được giữ lại. Dùng /model rồi /retry, "
                "hoặc /new để nhập câu hỏi ngắn hơn."
            )
            if debug:
                show_details(context, generated, elapsed, write, show_timings=False)
        except LLMError as exc:
            generated = {
                "generation": {
                    "model": exc.model,
                    "provider": exc.provider,
                    "http_status": exc.status,
                    "error_code": exc.error_code,
                },
                "validation": {"valid": False, "errors": ["Dịch vụ AI chưa trả lời được"]},
                "timings": dict(getattr(exc, "timings", {}) or {}),
            }
            elapsed = time.perf_counter() - started
            last_result = context, generated, elapsed
            write("Dịch vụ AI chưa trả lời được.")
            _show_stage_timings(context, generated, write)
            if exc.retry_after:
                write(f"Thử lại sau {exc.retry_after:.0f}s.")
            write("Thông tin đã được giữ lại. Dùng /retry hoặc bổ sung thêm thông tin.")
            write("Dùng /details để xem thông tin lỗi.")
            if debug:
                show_details(context, generated, elapsed, write, show_timings=False)
        except ValueError:
            write(
                "Chưa xử lý được lượt này. Hãy rút gọn thông tin vừa nhập hoặc dùng /new; "
                "câu hỏi và dữ kiện hiện tại được giữ lại để /retry."
            )
        except KeyboardInterrupt:
            return
        except Exception as exc:
            write(
                "Luồng RAG gặp lỗi. Dùng /retry để thử lại; "
                "chạy với --debug nếu cần kiểm tra kỹ thuật."
            )
            if debug:
                write(f"Loại lỗi: {type(exc).__name__}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Tự nhập câu hỏi HS/QA và bổ sung ngữ cảnh trong terminal."
    )
    parser.add_argument("--debug", action="store_true", help="Hiện log, model và chi tiết kỹ thuật")
    parser.add_argument(
        "--model",
        choices=MODEL_PRESETS,
        default=DEFAULT_MODEL_PRESET,
        help="Chọn model; mặc định %(default)s. Dùng /model để đổi trong phiên.",
    )
    args = parser.parse_args(argv)
    try:
        client = RAGClient(model_preset=args.model)
        config = client.config
        if args.debug:
            print(f"\nModel chính: {config.model} | Dự phòng: {' → '.join(config.fallback_models)}")
        print("Đang chuẩn bị RAG… Lần đầu có thể cần thêm thời gian để nạp model.")
        with connect() as conn:
            conn.execute("SET default_transaction_read_only = on")
            with _runtime_output(args.debug):
                retriever = Retriever(conn, Embedder(), query_planner=QueryPlanner(client))
                if not getattr(retriever, "unified_policy", None):
                    raise ValueError("No active unified retrieval policy")
                graph = load_generation_graph(retriever)
            if args.debug:
                print(f"Snapshot: {retriever.snapshot} | Profile: {retriever.profile}")
            run_console(retriever, client, graph, debug=args.debug)
    except (EOFError, KeyboardInterrupt):
        pass
    except Exception as exc:
        print(
            f"Không thể khởi tạo RAG ({type(exc).__name__}). "
            "Kiểm tra .env, PostgreSQL, model và policy tương ứng với snapshot/profile đang active.",
            file=sys.stderr,
        )
        return 1
    finally:
        print("\nĐã thoát demo RAG.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
