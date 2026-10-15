"""Pack user facts, cited source text and verified HS evidence for the LLM."""

import json
import re

from rag.graph.context import GraphContext
from rag.ingestion.sources import SOURCE_TYPES
from rag.prompts.schemas import ANSWER_SCHEMA
from rag.prompts.system import SYSTEM_PROMPT
from rag.utils.files import digest


def compose_query(question: str, supplements: list[str], max_chars: int) -> str:
    """Combine user facts for a fresh retrieval, without carrying assistant claims."""
    if not question.strip():
        raise ValueError("Question must not be empty")
    if any(not text.strip() for text in supplements):
        raise ValueError("Additional context must not be empty")
    sections = [question.strip()]
    sections.extend(
        f"Thông tin người dùng bổ sung ở lượt {i + 2}: {text.strip()}"
        for i, text in enumerate(supplements)
    )
    combined = "\n\n".join(sections)
    if len(combined) > max_chars:
        raise ValueError("Combined question exceeds GROQ_MAX_INPUT_CHARS")
    return combined


def load_generation_graph(retriever) -> GraphContext:
    records = retriever.documents("knowledge", chunk_types=SOURCE_TYPES)
    nodes = retriever.conn.execute(
        "SELECT * FROM rag.graph_nodes WHERE snapshot=%s", (retriever.snapshot,)
    ).fetchall()
    edges = retriever.conn.execute(
        "SELECT * FROM rag.graph_edges WHERE snapshot=%s ORDER BY id", (retriever.snapshot,)
    ).fetchall()
    return GraphContext(records, nodes, edges)


def source_rows(
    result: dict, task: str, graph=None, candidate_limit: int = 10
) -> tuple[list, list]:
    candidates = result.get("hs_candidates", [])[:candidate_limit] if task in {"hs", "auto"} else []
    advice = result.get("semantic_intent", {})
    # Advisory intent affects packing priority, never filters the common retrieval results.
    rows = (
        list(result.get("matches", []))
        if task == "auto" and advice.get("intent") != "product"
        else []
    )
    notes: list[dict] = []
    for row in candidates:
        rows.append(row)
        if graph is not None:
            view = graph.source_view(row)
            for nid in [*view["ancestor_ids"], *view["context_ids"], *view["note_ids"]]:
                evidence = (
                    graph.legal_evidence(nid)
                    if hasattr(graph, "legal_evidence")
                    else [graph.citation(nid)]
                )
                for citation in evidence:
                    if not citation:
                        continue
                    sid = citation.get("id", nid)
                    target = notes if nid in view["note_ids"] else rows
                    target.append(
                        {
                            **graph.records.get(sid, {}),
                            "id": sid,
                            "source_text": citation["text"],
                            "locator": citation["locator"],
                        }
                    )
    rows.extend([*result.get("matches", []), *result.get("package", []), *notes])
    unique = {}
    for row in rows:
        if graph is not None and graph.citation(row["id"]) is None:
            continue
        if row.get("source_text") and row["id"] not in unique:
            unique[row["id"]] = row
    return list(unique.values()), candidates


def _candidate_evidence(candidates: list[dict], sources: list[dict], graph) -> list[dict]:
    labels = {s["id"]: s["label"] for s in sources}
    evidence = []
    for row in candidates:
        if row["id"] not in labels:
            continue
        view = graph.source_view(row) if graph is not None else {}
        hierarchy: dict = (
            graph.hs_hierarchy(row)
            if graph is not None and hasattr(graph, "hs_hierarchy")
            else {"status": "INVALID", "chain": [], "errors": ["HS source graph is unavailable"]}
        )
        chain = []
        for node in hierarchy["chain"]:
            source_ids = node.get(
                "legal_evidence_ids", [node["id"]] if node["has_legal_wording"] else []
            )
            evidence_labels = [labels[sid] for sid in source_ids if sid in labels]
            chain.append(
                {
                    **node,
                    "label": evidence_labels[0] if evidence_labels else None,
                    "evidence_labels": evidence_labels,
                }
            )
            for sid in source_ids:
                if sid not in labels:
                    hierarchy["errors"].append(
                        f"HS{node['level']} wording omitted from generation context: {node['code']} ({sid})"
                    )
        hierarchy = {
            **hierarchy,
            "chain": chain,
            "errors": list(hierarchy["errors"]),
        }
        for sid in view.get("context_ids", []):
            if sid not in labels:
                hierarchy["errors"].append(
                    f"Source branch condition omitted from generation context: {sid}"
                )
        if hierarchy["errors"]:
            hierarchy["status"] = "INVALID"
            if hierarchy.get("structure_status") == "VERIFIED":
                hierarchy["legal_evidence_status"] = "INSUFFICIENT"
        context_labels = [labels[sid] for sid in view.get("context_ids", []) if sid in labels]
        required = {label for node in hierarchy["chain"] for label in node["evidence_labels"]}
        required.update(context_labels)
        evidence.append(
            {
                "code": row["code"],
                "wording_label": labels[row["id"]],
                "ancestor_labels": [
                    labels[sid] for sid in view.get("ancestor_ids", []) if sid in labels
                ],
                "context_labels": context_labels,
                "required_citation_labels": sorted(required, key=lambda label: int(label[1:])),
                "related_note_labels": [
                    labels[sid] for sid in view.get("note_ids", []) if sid in labels
                ],
                "hierarchy": hierarchy,
                "note_applicability": "REQUIRES_SOURCE_REASONING",
            }
        )
    return evidence


def _compact_locator(locator: dict) -> dict:
    origin = locator.get("source", {})
    pages = set(locator.get("physical_pages") or [])
    page = locator.get("physical_page") or origin.get("physical_page")
    if page is not None:
        pages.add(page)
    pages.update(c["physical_page"] for c in locator.get("continuations", []))
    values = {
        "document": locator.get("document") or origin.get("source_filename"),
        "physical_page": locator.get("physical_page") or origin.get("physical_page"),
        "printed_page": locator.get("printed_page") or origin.get("printed_page"),
        "graph_source_node": locator.get("graph_source_node"),
        "sha256": locator.get("sha256"),
        "bbox": locator.get("bbox"),
        "continuations": locator.get("continuations"),
        "physical_pages": sorted(pages)
        if len(pages) > 1 or locator.get("physical_pages")
        else None,
    }
    return {k: v for k, v in values.items() if v is not None}


def prepare_context(question: str, result: dict, task: str, config, graph=None) -> dict:
    if task not in {"hs", "qa", "auto"}:
        raise ValueError("Task must be hs, qa or auto")
    if not question.strip() or len(question) > config.max_input_chars:
        raise ValueError("Question is empty or exceeds GROQ_MAX_INPUT_CHARS")
    rows, candidates = source_rows(result, task, graph)
    packed: list[dict] = []
    omitted: list[str] = []
    for row in rows:
        source = {
            "label": f"S{len(packed) + 1}",
            "id": row["id"],
            "text": row["source_text"],
            "code": row.get("code"),
            "chunk_type": row.get("chunk_type"),
            "locator": _compact_locator(row.get("locator", {})),
            "effective_from": str(row.get("effective_from") or ""),
            "effective_to": str(row.get("effective_to") or ""),
            "legal_status": row.get("legal_status"),
        }
        if (
            len(json.dumps([*packed, source], ensure_ascii=False, default=str))
            > config.max_context_chars
        ):
            omitted.append(row["id"])
        else:
            packed.append(source)
    instructions = {
        "hs": (
            "Trước tiên kiểm tra mâu thuẫn chưa đính chính và thuộc tính còn thiếu: "
            "dùng MISSING_PRODUCT_INFO, mã rỗng khi chưa rõ. Chỉ đối chiếu dữ kiện hiện tại, "
            "bỏ dữ kiện người dùng đã đính chính. Chỉ đề xuất mã HS 8 chữ số khi đủ chứng cứ: status=RECOMMENDATION, "
            "suggested_hs_code=mã đã chọn. Nếu chưa thể kết luận, để trường mã rỗng."
        ),
        "qa": "Trả lời câu hỏi QA có dẫn nguồn; dùng status=ANSWERED khi đủ chứng cứ, không đề xuất mã HS.",
        "auto": (
            "Tự xác định nhu cầu từ câu hỏi gốc và thông tin người dùng bổ sung. "
            "Nếu người dùng yêu cầu phân loại hàng hóa, áp dụng quy tắc HS: chỉ dùng "
            "RECOMMENDATION kèm mã ứng viên 8 chữ số khi đủ thuộc tính và chứng cứ. "
            "Nếu hỏi kiến thức, quy định, hồ sơ hoặc giải thích mã có sẵn, trả lời QA có dẫn nguồn: "
            "ANSWERED, mã đề xuất rỗng và alternatives=[]. Việc nhắc tới HS/GIR không tự đồng nghĩa "
            "với yêu cầu phân loại hàng hóa. Nếu cần cả phân loại và hỏi đáp, trả lời cả hai theo nguồn; "
            "chỉ đề xuất HS khi phần phân loại đủ căn cứ. intent_advice chỉ là gợi ý, có thể sai; "
            "không để gợi ý này quyết định thay câu hỏi. Khi nhu cầu chưa rõ hoặc thiếu thuộc tính, "
            "dùng MISSING_PRODUCT_INFO, hỏi thông tin cụ thể, không yêu cầu người dùng chọn HS/QA. "
            "Khi thiếu nguồn, dùng INSUFFICIENT_LEGAL_EVIDENCE hoặc REQUIRES_REVIEW."
        ),
    }
    payload = {
        "task": task,
        "task_instruction": instructions[task],
        "question": question,
        "sources": packed,
        "omitted_source_ids": omitted,
        "scope": result.get("coverage", {}),
        "legal_validity": "LOCAL_SOURCE_METADATA_NOT_INDEPENDENTLY_VERIFIED",
    }
    if task == "auto":
        payload["intent_advice"] = result.get("semantic_intent", {})
    while True:
        included = {s["id"] for s in packed}
        allowed = [
            r["code"]
            for r in candidates
            if r["id"] in included and re.fullmatch(r"[0-9]{8}", r.get("code") or "")
        ]
        payload["candidate_hs_codes"] = allowed
        if candidates:
            payload["candidate_evidence"] = _candidate_evidence(candidates, packed, graph)
        user_message = json.dumps(payload, ensure_ascii=False, default=str)
        if len(user_message) <= config.max_input_chars:
            break
        if not packed:
            raise ValueError("Question and source metadata exceed GROQ_MAX_INPUT_CHARS")
        omitted.append(packed.pop()["id"])
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]
    return {
        "task": task,
        "question": question,
        "sources": packed,
        "allowed_hs_codes": allowed,
        "retrieved_hs_codes": [r["code"] for r in result.get("hs_candidates", [])],
        "candidate_evidence": payload.get("candidate_evidence", []),
        "source_locators": {
            s["label"]: next(r.get("locator", {}) for r in rows if r["id"] == s["id"])
            for s in packed
        },
        "omitted_source_ids": omitted,
        "context_hash": digest(payload),
        "prompt_hash": digest(SYSTEM_PROMPT),
        "schema_hash": digest(ANSWER_SCHEMA),
        "messages": messages,
        "snapshot": result.get("snapshot"),
        "profile": result.get("profile"),
        "policy_hash": result.get("policy_hash"),
    }
