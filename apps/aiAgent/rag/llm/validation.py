"""Validate answer schema, exact citations, HS ancestry and information ownership."""

import re
import unicodedata

import jsonschema

from rag.prompts.schemas import ANSWER_SCHEMA


def _normalized(text: str) -> str:
    return " ".join(text.split())


def _folded(text: str) -> str:
    return "".join(
        c
        for c in unicodedata.normalize("NFD", text.lower().replace("đ", "d"))
        if not unicodedata.combining(c)
    )


LEGAL_INFORMATION = re.compile(
    r"\b(?:hs|ahtn|gir|gri|chu giai|phan nhom|nhom [0-9]{4}|mo ta phap ly|"
    r"quy tac (?:tong quat|phan loai)|phap ly|phap luat|quy dinh|dieu kien phan loai|noi dung luat|"
    r"dieu (?:luat|khoan)|thong tu|nghi dinh|bieu thue|heading|subheading|"
    r"(?:chapter|section) (?:[0-9]+|notes?)|legal (?:text|wording|evidence|provisions?)|"
    r"classification (?:rules|conditions)|rules of interpretation|tariff (?:code|wording|description)|legislation|regulations?|law)\b"
)


USER_REQUEST = re.compile(
    r"^(?:can )?(?:hay|bo sung|cung cap|cho biet|xac nhan|provide|supply|submit)\b|"
    r"\b(?:vui long|ban (?:can|nen|co the|hay)|nguoi dung (?:can|phai)|"
    r"please|(?:can|could|would) you|you (?:must|should|need))\b"
)


def _ownership_errors(answer: dict) -> list[str]:
    errors = []
    missing = answer["missing_information"]
    legal = answer["missing_legal_evidence"]
    if answer["status"] == "MISSING_PRODUCT_INFO":
        if not missing or any(not item.strip() for item in missing):
            errors.append("Missing product information status requires specific user facts")
        if any(LEGAL_INFORMATION.search(_folded(item)) for item in missing):
            errors.append(
                "Legal evidence belongs to retrieval/corpus, never to missing product information"
            )
    elif missing:
        errors.append("Only MISSING_PRODUCT_INFO may request user information")
    if answer["status"] == "INSUFFICIENT_LEGAL_EVIDENCE":
        if not legal or any(not item.strip() for item in legal):
            errors.append("Insufficient legal evidence status requires a retrieval/corpus gap")
    elif legal:
        errors.append("Legal evidence gaps require INSUFFICIENT_LEGAL_EVIDENCE")
    if any(
        USER_REQUEST.search(_folded(item).strip()) or "?" in item or "？" in item for item in legal
    ):
        errors.append("Legal evidence gaps are system diagnostics, not user requests")
    for sentence in re.split(r"(?<=[.!?])\s+|\n", answer["answer"]):
        folded = _folded(sentence)
        request = USER_REQUEST.search(folded)
        # A corpus diagnostic may describe work for the system without asking the user.
        diagnostic = re.match(r"(?:corpus|retrieval|he thong|nguon truy xuat)\b", folded.strip())
        if re.search(r"\b(?:ban|nguoi dung|vui long|please|you)\b", folded):
            diagnostic = None
        if request and not diagnostic and LEGAL_INFORMATION.search(folded):
            errors.append(
                "Do not ask the user to supply legal evidence; report a retrieval/corpus gap"
            )
        if answer["status"] != "MISSING_PRODUCT_INFO" and (
            (request and not diagnostic) or "?" in sentence or "？" in sentence
        ):
            errors.append("Only MISSING_PRODUCT_INFO may ask the user a question")
    return errors


def validate_answer(answer: dict, context: dict) -> dict:
    errors = [e.message for e in jsonschema.Draft202012Validator(ANSWER_SCHEMA).iter_errors(answer)]
    if errors:
        return {"valid": False, "errors": errors, "semantic_grounding": "NOT_EVALUATED"}
    sources = {s["label"]: s for s in context["sources"]}
    cited = set()
    for citation in answer["citations"]:
        label, quote = citation["label"], _normalized(citation["quote"])
        if label in cited:
            errors.append(f"Duplicate citation: {label}")
        cited.add(label)
        if label not in sources:
            errors.append(f"Unknown citation: {label}")
        elif not quote or quote not in _normalized(sources[label]["text"]):
            errors.append(f"Quote does not occur in source: {label}")
    markers = set(re.findall(r"\[(S\d+)\]", answer["answer"]))
    if markers != cited:
        errors.append("Inline citations and citation records differ")
    if answer["status"] in {"ANSWERED", "RECOMMENDATION"} and not cited:
        errors.append("A substantive answer requires citations")
    codes = [c for c in [answer["suggested_hs_code"], *answer["alternatives"]] if c]
    if any(not re.fullmatch(r"[0-9]{8}", c) for c in codes):
        errors.append("Proposed HS codes must have exactly eight ASCII digits")
    if any(c not in context["allowed_hs_codes"] for c in codes):
        errors.append("HS code is outside the supplied candidates")
    if context["task"] == "qa" and (codes or answer["status"] == "RECOMMENDATION"):
        errors.append("QA must not produce an HS recommendation")
    if context["task"] == "auto" and answer["status"] == "ANSWERED" and codes:
        errors.append("An answered QA response must not include proposed HS codes")
    if context["task"] == "hs" and answer["status"] == "ANSWERED":
        errors.append("HS must use a recommendation or abstention status")
    if answer["status"] == "RECOMMENDATION" and not answer["suggested_hs_code"]:
        errors.append("HS recommendation requires a code")
    if answer["status"] != "RECOMMENDATION" and answer["suggested_hs_code"]:
        errors.append("Abstention must not include a selected HS code")
    if answer["status"] != "RECOMMENDATION" and answer["alternatives"]:
        errors.append("Abstention must not include alternative HS proposals")
    boundary_errors = _ownership_errors(answer)
    if answer["status"] == "RECOMMENDATION":
        evidence = {e["code"]: e for e in context.get("candidate_evidence", [])}
        for code in codes:
            path = evidence.get(code, {}).get("hierarchy", {})
            if path.get("status") != "VERIFIED":
                boundary_errors.append(
                    f"HS hierarchy is not verified for {code}: {path.get('errors', [])}"
                )
            elif code == answer["suggested_hs_code"]:
                required = set(evidence[code]["required_citation_labels"])
                if not required <= cited:
                    boundary_errors.append(
                        f"HS recommendation is missing citations for its leaf, printed parents or source branch conditions: {sorted(required - cited)}. Use these exact labels in answer and citation records."
                    )
    errors.extend(boundary_errors)
    return {
        "valid": not errors,
        "errors": errors,
        "cited_labels": sorted(cited),
        "cited_source_ids": [sources[label]["id"] for label in sorted(cited) if label in sources],
        "semantic_grounding": "NOT_EVALUATED",
        "boundary_errors": boundary_errors,
    }
