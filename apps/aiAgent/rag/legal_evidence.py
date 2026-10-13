"""Bind logical HS levels to complete printed passages, without inventing parent text."""

import hashlib
import json
import re
import unicodedata
from collections import defaultdict

BINDING_VERSION = 1
CONSOLIDATED_ROW = "CONSOLIDATED_UNDIVIDED_ROW"


def evidence_digest(value) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()


def normalized_wording(text: str) -> str:
    # Fold PDF accent/OCR variants only; retain every word, negation and numeric condition.
    text = unicodedata.normalize("NFKD", text.lower().replace("đ", "d"))
    return " ".join(
        re.findall(r"[a-z0-9]+", "".join(c for c in text if not unicodedata.combining(c)))
    )


def consolidated_bindings(rows: list[dict], records: list[dict], extraction: dict) -> list[dict]:
    """Require an undivided printed block, complete code inventory and exact normalized wording."""
    inventory = extraction["code_inventory"]
    by_heading: dict[str, set[str]] = defaultdict(set)
    occurrences: dict[str, int] = defaultdict(int)
    for item in inventory:
        by_heading[item["code"][:4]].add(item["code"])
        occurrences[item["code"]] += 1
    by_code = {r["code"]: r for r in records if r.get("code")}
    bindings = []
    for index, row in enumerate(rows):
        code = row.get("code") or ""
        # Zero padding is eligibility, never the evidence of an undivided legal scope.
        if not re.fullmatch(r"[0-9]{4}0000", code) or code not in by_code:
            continue
        if row.get("depth") is not None or row.get("depth_vi") is not None:
            continue
        if row.get("depth_en") is not None or not row.get("text_en", "").strip():
            continue
        if by_heading[code[:4]] != {code} or occurrences[code] != 1:
            continue
        block = []
        for following in rows[index + 1 :]:
            if following.get("code") and following["code"][:4] != code[:4]:
                break
            block.append(following)
        if any(r.get("code") or r.get("depth") is not None for r in block):
            continue
        record = by_code[code]
        if not normalized_wording(row["text_vi"]):
            raise ValueError(f"Empty consolidated source wording: {code}")
        if normalized_wording(record["source_text"]) != normalized_wording(row["text_vi"]):
            raise ValueError(f"Incomplete or different consolidated source wording: {code}")
        bindings.append(
            {
                "version": BINDING_VERSION,
                "kind": CONSOLIDATED_ROW,
                "status": "VERIFIED",
                "source_id": record["id"],
                "source_code": code,
                "source_text_hash": evidence_digest(record["source_text"]),
                "locator": row["locator"],
                "covered_codes": [code[:4], code[:6], code],
                "printed_codes": sorted(by_heading[code[:4]]),
                "wording_status": "NORMALIZED_COMPLETE_MATCH",
                "scope_basis": "FULL_PDF_CODE_COLUMN_AND_UNDIVIDED_BILINGUAL_ROW",
                "extraction": extraction["extractor"],
            }
        )
    return bindings


def attach_bindings(records: list[dict], nodes: list[dict], bindings: list[dict]) -> None:
    """Attach audited bindings to graph metadata; preserve original text and source flags."""
    by_id = {r["id"]: r for r in records}
    by_code: dict[str, list[dict]] = defaultdict(list)
    for node in nodes:
        md = node["metadata"]
        code = md.get("code") or md.get("code_compact") or md.get("hs", {}).get("code_compact")
        if code:
            by_code[code].append(node)
    for binding in bindings:
        code = binding["source_code"]
        source = by_id.get(binding["source_id"])
        if source is None or source.get("code") != code:
            raise ValueError(f"Consolidated evidence has no registered source: {code}")
        locator = source["locator"]
        if any(locator.get(k) != v for k, v in binding["locator"].items()):
            raise ValueError(f"Consolidated evidence locator drifted: {code}")
        if binding["source_text_hash"] != evidence_digest(source["source_text"]):
            raise ValueError(f"Consolidated evidence text drifted: {code}")
        targets = {}
        for covered in binding["covered_codes"]:
            if len(by_code[covered]) != 1:
                raise ValueError(f"Ambiguous consolidated evidence target: {covered}")
            targets[covered] = by_code[covered][0]["id"]
        proof = {
            **binding,
            "covered_node_ids": targets,
            "source_locator_hash": evidence_digest(locator),
        }
        for covered in binding["covered_codes"]:
            by_code[covered][0]["metadata"]["legal_evidence_binding"] = proof
