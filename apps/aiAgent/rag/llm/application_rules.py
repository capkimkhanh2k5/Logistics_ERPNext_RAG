"""Retrieve source rules from explicit presentation wording, not product/model names."""

import re

from rag.llm.validation import _folded


def assembly_hypothesis(question: str) -> bool:
    # This only requests evidence. The review still determines applicability.
    turns = re.split(r"\n\nThông tin người dùng bổ sung ở lượt \d+: ", question)
    for turn in reversed(turns):
        turn = re.split(
            r"\b(?:hãy|có thể phân loại|nên phân loại|mã HS|áp dụng GIR)\b",
            turn,
            maxsplit=1,
            flags=re.I,
        )[0]
        text = _folded(turn)
        mentions = list(
            re.finditer(
                r"\b(?:ckd|chua lap rap|thao roi|unassembled|disassembled|cbu|nguyen chiec)\b", text
            )
        )
        if mentions:
            last = mentions[-1]
            return last[0] not in {"cbu", "nguyen chiec"} and not re.search(
                r"(?:khong|not)\s+(?:phai\s+|la\s+|dang\s+){0,3}$",
                text[max(0, last.start() - 30) : last.start()],
            )
    return False


def assembly_rule_rows(question: str, graph) -> list[dict]:
    if graph is None or not assembly_hypothesis(question):
        return []
    return [
        row
        for row in graph.records.values()
        if row.get("chunk_type") == "gir_rule"
        and "chua lap rap hoac thao roi" in _folded(row.get("source_text", ""))
        and "dac trung co ban" in _folded(row.get("source_text", ""))
        and graph.citation(row["id"])
    ]


def rule_name(source: dict) -> str:
    if source.get("chunk_type") != "gir_rule":
        return ""
    match = re.search(r"(?:^|:)GIR_(\d+)([A-C]?)$", source["id"])
    return (f"GIR {match[1]}" + (f"({match[2].lower()})" if match[2] else "")) if match else ""
