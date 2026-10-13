"""Interactive terminal demo for HS/QA retrieval and grounded Groq answers."""

import argparse
import sys
import time
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config.settings import GroqConfig  # noqa: E402
from rag.answering import (  # noqa: E402
    compose_query,
    generate_answer,
    load_generation_graph,
    prepare_context,
)
from rag.db import connect  # noqa: E402
from rag.embedding import Embedder  # noqa: E402
from rag.groq_client import GroqClient, GroqError  # noqa: E402
from rag.retrieval import Retriever  # noqa: E402

HELP = """Nhập câu hỏi trên một dòng và nhấn Enter.
Sau khi AI trả lời, nhập thêm thông tin để làm rõ cùng câu hỏi.
/new   Bắt đầu câu hỏi mới và xóa thông tin bổ sung của câu hỏi trước
/retry Truy xuất và trả lời lại với các thông tin hiện tại
/help  Xem hướng dẫn
/exit  Thoát (hoặc Ctrl+C / Ctrl+D)"""

STATUSES = {
    "ANSWERED": "Đã trả lời",
    "RECOMMENDATION": "Đề xuất mã HS",
    "MISSING_PRODUCT_INFO": "Thiếu thông tin hàng hóa/hồ sơ từ người dùng",
    "INSUFFICIENT_LEGAL_EVIDENCE": "Chưa đủ chứng cứ pháp lý trong retrieval/corpus",
    "REQUIRES_REVIEW": "Cần thẩm định thêm",
}


def show_answer(context: dict, generated: dict, elapsed: float, write=print) -> None:
    generation = generated["generation"]
    model = generation.get("model") or "Không gọi LLM (không có nguồn)"
    fallback = " — đã dùng model dự phòng" if generation.get("fallback_used") else ""
    write(f"\nModel: {model}{fallback} | Tổng thời gian: {elapsed:.1f}s")
    if not generated["validation"]["valid"]:
        write("Phản hồi chưa vượt qua kiểm tra cấu trúc/mã HS/trích dẫn. Dùng /retry để thử lại.")
        for error in generated["validation"]["errors"][:3]:
            write(f"- {error}")
        return
    answer = generated["answer"]
    write(f"Trạng thái: {STATUSES[answer['status']]}")
    write(f"\nAI: {answer['answer']}")
    if answer["suggested_hs_code"]:
        write(f"Mã HS đề xuất: {answer['suggested_hs_code']} (cần chuyên môn xác nhận)")
    if answer["alternatives"]:
        write("Mã cần cân nhắc thêm: " + ", ".join(answer["alternatives"]))
    if answer["status"] == "MISSING_PRODUCT_INFO" and answer["missing_information"]:
        write("\nThông tin bạn cần bổ sung:")
        for item in answer["missing_information"]:
            write(f"- {item}")
    if answer["missing_legal_evidence"]:
        write("\nKhoảng trống chứng cứ của hệ thống (retrieval/corpus):")
        for item in answer["missing_legal_evidence"]:
            write(f"- {item}")
    if answer["citations"]:
        write("\nNguồn trích dẫn:")
        sources = {source["label"]: source for source in context["sources"]}
        for citation in answer["citations"]:
            source = sources[citation["label"]]
            locator = source["locator"]
            details = [str(locator.get("document") or source["id"])]
            if locator.get("physical_pages"):
                details.append("trang PDF " + ", ".join(map(str, locator["physical_pages"])))
            elif locator.get("physical_page") is not None:
                details.append(f"trang PDF {locator['physical_page']}")
            if locator.get("printed_page") is not None:
                details.append(f"trang in {locator['printed_page']}")
            write(f"[{citation['label']}] " + " | ".join(details))
            write(f"  ID: {source['id']}")
            write(f"  Trích: {citation['quote']}")


def run_console(retriever, client, graph, *, read=input, write=print) -> None:
    question = ""
    supplements: list[str] = []
    needs_product_info = False
    write(HELP)
    while True:
        prompt = (
            "\nThông tin hàng hóa/hồ sơ hoặc lệnh: "
            if needs_product_info
            else "\nLệnh hoặc nội dung tiếp theo (/new để hỏi câu mới): "
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
        if command == "/new":
            question, supplements = "", []
            needs_product_info = False
            write("Đã bắt đầu câu hỏi mới.")
            continue
        if text.startswith("/") and command != "/retry":
            write("Lệnh không hợp lệ. Dùng /help để xem hướng dẫn.")
            continue
        if command == "/retry" and not question:
            write("Chưa có câu hỏi để thử lại.")
            continue

        previous_question, previous_supplements = question, supplements
        if command != "/retry":
            if question:
                supplements = [*supplements, text]
            else:
                question = text
        try:
            query = compose_query(question, supplements, client.config.max_input_chars)
        except ValueError:
            question, supplements = previous_question, previous_supplements
            write(
                f"Tổng câu hỏi và thông tin bổ sung vượt giới hạn "
                f"{client.config.max_input_chars} ký tự. Hãy rút gọn hoặc dùng /new."
            )
            continue

        started = time.perf_counter()
        try:
            write("Đang truy xuất nguồn… (lượt đầu cần tải embedding/reranker vào bộ nhớ)")
            result = retriever.routed_search(query, intent="auto")
            context = prepare_context(query, result, "auto", client.config, graph)
            write(f"Đã đóng gói {len(context['sources'])} nguồn. Đang tạo câu trả lời…")
            generated = generate_answer(context, client)
            needs_product_info = (
                generated["validation"]["valid"]
                and generated["answer"].get("status") == "MISSING_PRODUCT_INFO"
            )
            show_answer(context, generated, time.perf_counter() - started, write)
        except GroqError as exc:
            details = f"HTTP {exc.status}, model={exc.model}"
            if exc.error_code:
                details += f", {exc.error_code}"
            write(f"Groq chưa trả lời được ({details}).")
            if exc.retry_after:
                write(f"Thời gian chờ nhà cung cấp báo: {exc.retry_after:.0f}s.")
            write("Thông tin đã được giữ lại. Dùng /retry hoặc bổ sung thêm thông tin.")
        except ValueError:
            question, supplements = previous_question, previous_supplements
            write(
                "Không thể xử lý lượt này: kiểm tra giới hạn context/token hoặc policy retrieval. "
                "Hãy rút gọn thông tin vừa nhập hoặc dùng /new; thông tin trước đó được giữ lại."
            )
        except KeyboardInterrupt:
            return
        except Exception as exc:
            write(
                f"Luồng RAG gặp lỗi {type(exc).__name__}. Kiểm tra DB/model; dùng /retry để thử lại."
            )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Tự nhập câu hỏi HS/QA và bổ sung ngữ cảnh trong terminal."
    )
    parser.parse_args(argv)
    try:
        config = GroqConfig.from_env()
        print(f"\nModel chính: {config.model} | Dự phòng: {config.fallback_model}")
        print("Đang kết nối DB và khởi tạo RAG từ cấu hình hiện tại…")
        with connect() as conn:
            conn.execute("SET default_transaction_read_only = on")
            retriever = Retriever(conn, Embedder())
            if not getattr(retriever, "unified_policy", None):
                raise ValueError("No active unified retrieval policy")
            graph = load_generation_graph(retriever)
            print(f"Snapshot: {retriever.snapshot} | Profile: {retriever.profile}")
            run_console(retriever, GroqClient(config), graph)
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
