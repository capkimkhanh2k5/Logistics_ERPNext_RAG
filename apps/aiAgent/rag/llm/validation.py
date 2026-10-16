"""Validate answer schema, exact citations, HS ancestry and information ownership."""

import re
import unicodedata

import jsonschema

from rag.prompts.schemas import ANSWER_SCHEMA


def schema_errors(value: object, schema: dict) -> list[str]:
    errors = []
    for error in jsonschema.Draft202012Validator(schema).iter_errors(value):
        path = "/" + "/".join(map(str, error.absolute_path))
        if error.validator == "required":
            missing = [key for key in error.validator_value if key not in error.instance]
            detail = "Thiếu trường bắt buộc: " + ", ".join(missing)
        elif error.validator == "additionalProperties":
            extra = sorted(set(error.instance) - set(error.schema.get("properties", {})))
            detail = "Có trường ngoài cấu trúc cho phép: " + ", ".join(extra)
        elif error.validator == "type":
            detail = f"Sai kiểu dữ liệu; kiểu JSON yêu cầu: {error.validator_value}"
        elif error.validator == "enum":
            detail = "Giá trị phải thuộc danh sách: " + ", ".join(error.validator_value)
        elif error.validator == "minLength":
            detail = f"Chuỗi phải có ít nhất {error.validator_value} ký tự"
        else:
            detail = f"Không đáp ứng ràng buộc JSON {error.validator}: {error.validator_value}"
        errors.append(f"{path}: {detail}")
    return list(dict.fromkeys(errors))


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


_CORPUS_NAME = r"(?:co so du lieu|kho du lieu|kho tri thuc|database|corpus|knowledge base)"
_CORPUS_OBJECT = (
    r"(?:(?:du|bat ky|bat cu|cac|nhung|any|relevant|applicable|sufficient|the|enough)\s+){0,5}"
    r"(?:quy dinh|mo ta|chu giai|gir|gri|ma hs|nhom|phan nhom|bieu thue|chung cu|"
    r"can cu|nguon|tai lieu|du lieu|noi dung|ban ghi|thong tin|danh muc|ma ung vien|legal|evidence|"
    r"sources?|documents?|data|records?|tariff|headings?|subheadings?|chapter|section|"
    r"rules?|regulations?|legislation|law|notes?|[0-9]{4,8})\b"
)
_CORPUS_ABSENCE = re.compile(
    rf"\b{_CORPUS_NAME}\s+"
    r"(?:(?:hien tai|hien|dang|van|con|nay|cua he thong|currently|still|itself)\s+){0,3}"
    r"(?:khong co|chua co|khong chua|chua chua|thieu|lacks?|is missing|is lacking|"
    r"(?:has|have|contains?) (?:no|insufficient)|does not (?:contain|have)|doesn't (?:contain|have))"
    rf"\s+{_CORPUS_OBJECT}"
    rf"|\b(?:khong co|chua co|there (?:are|is) no)\s+{_CORPUS_OBJECT}"
    rf"(?:(?!\.(?:\s|$))[^;!?\n]){{0,180}}?\s+(?:trong|in|from)\s+(?:the\s+)?{_CORPUS_NAME}\b"
)
_CORPUS_DISCLAIMER = re.compile(
    r"\b(?:(?:khong|chua)(?: the)?\s+(?:ket luan|khang dinh|xac nhan|chung minh|suy ra|"
    r"co nghia|dong nghia|phai)(?:\s+(?:rang|la|duoc|toan bo))*|"
    r"(?:cannot|can not|can't|could not|do not|does not|don't|doesn't)\s+"
    r"(?:conclude|assert|establish|confirm|prove|mean|imply|show|indicate)"
    r"(?:\s+that)?(?:\s+(?:the|our|entire|whole|full)){0,3}|"
    r"(?:there is )?(?:no|insufficient) (?:evidence|basis|proof)"
    r"(?: to (?:conclude|assert|confirm))?(?: that)?(?: the)?)\s*$"
)
_RETRIEVED_CORPUS_PREFIX = re.compile(
    r"\b(?:ngu canh(?: truy xuat)?|nguon truy xuat|cac ket qua truy xuat|"
    r"retrieved (?:context|sources?|records?)|retrieval context)"
    r"[^,;.!?\n]{0,80}\b(?:tu|trong|from|of|in)\s+(?:the\s+)?$"
)


def _corpus_scope_errors(answer: dict) -> list[str]:
    for text in [answer["answer"], *answer["missing_legal_evidence"]]:
        folded = _folded(text)
        for claim in _CORPUS_ABSENCE.finditer(folded):
            prefix = re.split(
                r"[,;:\n]|\.(?:\s|$)|\b(?:nhung|tuy nhien|but|however|yet)\b",
                folded[: claim.start()],
            )[-1]
            if _CORPUS_DISCLAIMER.search(prefix) or _RETRIEVED_CORPUS_PREFIX.search(prefix):
                continue
            return [
                "Chưa có kiểm tra toàn kho dữ liệu đáng tin cậy: chỉ mô tả chứng cứ chưa được "
                "cấp trong ngữ cảnh truy xuất lượt này, không kết luận database/corpus thiếu dữ liệu."
            ]
    return []


def _requests_legal_information(sentence: str) -> bool:
    for request in USER_REQUEST.finditer(sentence):
        requested = re.split(
            r"\b(?:de|nham|in order to|so as to|so that|for (?=(?:hs|ahtn|tariff|classification)\b))\b",
            sentence[request.end() :],
            maxsplit=1,
        )[0]
        if LEGAL_INFORMATION.search(requested):
            return True
        prefix = sentence[: request.start()].strip()
        if LEGAL_INFORMATION.search(prefix) and not re.match(
            r"^(?:de|nham|in order to|to|for)\b", prefix
        ):
            return True
    return False


def _ownership_errors(answer: dict) -> list[str]:
    errors = _corpus_scope_errors(answer)
    missing = answer["missing_information"]
    legal = answer["missing_legal_evidence"]
    if answer["status"] == "MISSING_PRODUCT_INFO":
        if not missing or any(not item.strip() for item in missing):
            errors.append("MISSING_PRODUCT_INFO yêu cầu nêu rõ dữ kiện người dùng cần bổ sung")
        if any(LEGAL_INFORMATION.search(_folded(item)) for item in missing):
            errors.append(
                "Chứng cứ pháp lý thuộc trách nhiệm truy xuất/kho dữ liệu, không phải dữ kiện người dùng cần bổ sung"
            )
    elif missing:
        errors.append("Chỉ MISSING_PRODUCT_INFO được yêu cầu người dùng bổ sung dữ kiện")
    if answer["status"] == "INSUFFICIENT_LEGAL_EVIDENCE":
        if not legal or any(not item.strip() for item in legal):
            errors.append(
                "INSUFFICIENT_LEGAL_EVIDENCE yêu cầu nêu rõ khoảng trống truy xuất/kho dữ liệu"
            )
    elif legal:
        errors.append("Thiếu chứng cứ pháp lý phải dùng INSUFFICIENT_LEGAL_EVIDENCE")
    if any(
        USER_REQUEST.search(_folded(item).strip()) or "?" in item or "？" in item for item in legal
    ):
        errors.append(
            "Khoảng trống chứng cứ pháp lý là chẩn đoán hệ thống, không được hỏi người dùng"
        )
    for sentence in re.split(r"(?<=[.!?])\s+|\n", answer["answer"]):
        folded = _folded(sentence)
        request = USER_REQUEST.search(folded)
        # A corpus diagnostic may describe work for the system without asking the user.
        diagnostic = re.match(r"(?:corpus|retrieval|he thong|nguon truy xuat)\b", folded.strip())
        if re.search(r"\b(?:ban|nguoi dung|vui long|please|you)\b", folded):
            diagnostic = None
        if request and not diagnostic and _requests_legal_information(folded):
            errors.append(
                "Không yêu cầu người dùng cung cấp chứng cứ pháp lý; hãy báo khoảng trống truy xuất/kho dữ liệu"
            )
        if answer["status"] != "MISSING_PRODUCT_INFO" and (
            (request and not diagnostic) or "?" in sentence or "？" in sentence
        ):
            errors.append("Chỉ MISSING_PRODUCT_INFO được hỏi người dùng bổ sung thông tin")
    return errors


def validate_answer(answer: dict, context: dict) -> dict:
    errors = schema_errors(answer, ANSWER_SCHEMA)
    if errors:
        return {"valid": False, "errors": errors, "semantic_grounding": "NOT_EVALUATED"}
    sources = {s["label"]: s for s in context["sources"]}
    cited = set()
    for citation in answer["citations"]:
        label, quote = citation["label"], _normalized(citation["quote"])
        if label in cited:
            errors.append(f"Nhãn trích dẫn bị lặp trong citations: {label}")
        cited.add(label)
        if label not in sources:
            errors.append(f"Nhãn trích dẫn không có trong nguồn được cung cấp: {label}")
        elif not quote or quote not in _normalized(sources[label]["text"]):
            errors.append(f"Trích đoạn không khớp nguyên văn nguồn: {label}")
    markers = set(re.findall(r"\[(S\d+)\]", answer["answer"]))
    if markers != cited:
        errors.append("Nhãn dẫn nguồn trong answer không khớp các bản ghi trong citations")
    if answer["status"] in {"ANSWERED", "RECOMMENDATION"} and not cited:
        errors.append("Câu trả lời có kết luận phải có trích dẫn nguồn")
    codes = [c for c in [answer["suggested_hs_code"], *answer["alternatives"]] if c]
    if any(not re.fullmatch(r"[0-9]{8}", c) for c in codes):
        errors.append("Mã HS được đề xuất phải có đúng 8 chữ số ASCII")
    if any(c not in context["allowed_hs_codes"] for c in codes):
        errors.append("Mã HS không thuộc danh sách ứng viên được cung cấp")
    if context["task"] == "qa" and (codes or answer["status"] == "RECOMMENDATION"):
        errors.append("Câu trả lời hỏi đáp không được đề xuất mã HS")
    if context["task"] == "auto" and answer["status"] == "ANSWERED" and codes:
        errors.append("Câu trả lời hỏi đáp dùng ANSWERED không được kèm mã HS đề xuất")
    if context["task"] == "hs" and answer["status"] == "ANSWERED":
        errors.append("Phân loại HS phải dùng trạng thái đề xuất hoặc chưa thể kết luận")
    if answer["status"] == "RECOMMENDATION" and not answer["suggested_hs_code"]:
        errors.append("Đề xuất HS phải điền mã vào suggested_hs_code")
    if answer["status"] != "RECOMMENDATION" and answer["suggested_hs_code"]:
        errors.append("Khi chưa đề xuất HS, suggested_hs_code phải để rỗng")
    if answer["status"] != "RECOMMENDATION" and answer["alternatives"]:
        errors.append("Khi chưa đề xuất HS, alternatives phải để []")
    boundary_errors = _ownership_errors(answer)
    if answer["status"] == "RECOMMENDATION":
        evidence = {e["code"]: e for e in context.get("candidate_evidence", [])}
        for code in codes:
            path = evidence.get(code, {}).get("hierarchy", {})
            if path.get("status") != "VERIFIED":
                boundary_errors.append(
                    f"Chuỗi nhóm 4 số → phân nhóm 6 số → mã 8 số chưa được xác minh cho {code}; xem candidate_evidence.hierarchy.errors"
                )
            elif code == answer["suggested_hs_code"]:
                required = set(evidence[code]["required_citation_labels"])
                if not required <= cited:
                    boundary_errors.append(
                        f"Đề xuất HS thiếu trích dẫn của mã chi tiết, cấp cha có mô tả pháp lý hoặc điều kiện nhánh: {sorted(required - cited)}. Dùng đúng các nhãn này trong answer và citations."
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
