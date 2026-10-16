"""Conservative proof checks for explicit numeric physical conditions.

This is a necessary numeric-coherence guard, not proof of semantic or legal grounding.
Independent semantic review is still required. It supports digit
quantities, basic physical units and one-sided comparisons. Ranges, uncertain facts,
ambiguous grouping and ambiguous unit capitalization cannot prove a condition. It does
not establish applicability of exceptions, disjunctions or unrecognized unit families.
Attribution rejects obvious differing physical attributes or measurement subjects;
it does not resolve unrestricted noun phrases, references or component relationships.
"""

import re
import unicodedata
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

_OPERATORS = (
    (
        "<=",
        r"(?:<=|≤|at\s+most|no\s+more\s+than|not\s+more\s+than|not\s+exceeding|"
        r"không\s+(?:vượt\s+)?quá|khong\s+(?:vuot\s+)?qua|không\s+lớn\s+hơn|"
        r"khong\s+lon\s+hon|tối\s+đa|toi\s+da|nhỏ\s+hơn\s+hoặc\s+bằng|nho\s+hon\s+hoac\s+bang)",
    ),
    (
        ">=",
        r"(?:>=|≥|at\s+least|no\s+less\s+than|not\s+less\s+than|not\s+under|"
        r"ít\s+nhất|it\s+nhat|không\s+dưới|khong\s+duoi|không\s+nhỏ\s+hơn|"
        r"khong\s+nho\s+hon|tối\s+thiểu|toi\s+thieu|lớn\s+hơn\s+hoặc\s+bằng|lon\s+hon\s+hoac\s+bang)",
    ),
    ("<", r"(?:<|less\s+than|under|below|nhỏ\s+hơn|nho\s+hon|dưới|duoi)"),
    (">", r"(?:>|more\s+than|over|above|lớn\s+hơn|lon\s+hon|trên|tren|vượt\s+quá|vuot\s+qua)"),
    ("=", r"(?:=|exactly|equal\s+to|bằng|bang)"),
)
_BASE_UNITS = {
    "chỗ": ("seats", "1"),
    "cho": ("seats", "1"),
    "người": ("seats", "1"),
    "nguoi": ("seats", "1"),
    "seat": ("seats", "1"),
    "seats": ("seats", "1"),
    "persons": ("seats", "1"),
    "people": ("seats", "1"),
    "kg": ("mass", "1000"),
    "g": ("mass", "1"),
    "mg": ("mass", "0.001"),
    "t": ("mass", "1000000"),
    "tấn": ("mass", "1000000"),
    "tan": ("mass", "1000000"),
    "w": ("power", "1"),
    "kw": ("power", "1000"),
    "mm": ("length", "0.001"),
    "cm": ("length", "0.01"),
    "m": ("length", "1"),
    "km": ("length", "1000"),
    "ml": ("volume", "0.001"),
    "l": ("volume", "1"),
    "cm3": ("volume", "0.001"),
    "cm³": ("volume", "0.001"),
    "m3": ("volume", "1000"),
    "m³": ("volume", "1000"),
    "v": ("voltage", "1"),
    "kv": ("voltage", "1000"),
    "a": ("current", "1"),
    "hz": ("frequency", "1"),
    "khz": ("frequency", "1000"),
    "ghz": ("frequency", "1000000000"),
}
_CASE_UNITS = {
    "mW": ("power", "0.001"),
    "MW": ("power", "1000000"),
    "mA": ("current", "0.001"),
    "MA": ("current", "1000000"),
    "mHz": ("frequency", "0.001"),
    "MHz": ("frequency", "1000000"),
    "Mm": ("length", "1000000"),
    "mL": ("volume", "0.001"),
    "ML": ("volume", "1000000"),
}
_AMBIGUOUS_UNITS = {"mw": "power", "ma": "current", "mhz": "frequency"}
_NAMES = {
    "seats": "số chỗ ngồi",
    "mass": "khối lượng",
    "power": "công suất",
    "length": "kích thước",
    "volume": "thể tích",
    "voltage": "điện áp",
    "current": "cường độ dòng điện",
    "frequency": "tần số",
}
_UNITS = "|".join(
    re.escape(unit) for unit in sorted({*_BASE_UNITS, *_CASE_UNITS}, key=len, reverse=True)
)
_QUANTITY = re.compile(
    r"(?:(?P<operator>(?<!\w)(?:"
    + "|".join(pattern for _, pattern in _OPERATORS)
    + r")|[<>]=?|[≤≥=])\s*|(?<![\w.,]))(?P<number>[+-]?\d(?:[\d.,\u00a0 –-]*\d)?)\s*(?P<unit>"
    + _UNITS
    + r")(?!\w)",
    re.IGNORECASE,
)
_UNCERTAIN = re.compile(
    r"\b(?:khong\s+(?:biet|ro|chac)|chua\s+(?:biet|ro|xac\s+nhan)|co\s+the|"
    r"gia\s+su|neu|khoang|uoc\s+chung|not\s+sure|unknown|uncertain|maybe|might|"
    r"approximately|about|assuming|if|hoac|or)\b|"
    r"\b(?:between|from|tu)\s*[+-]?\d|[?？]|\d\s*[-–]\s*\d"
)
_NEGATED_ASSERTION = re.compile(
    r"\b(?:khong\s+(?:phai|bang)|not\s+equal|is\s+not|was\s+not|does\s+not|isn't|wasn't)\b"
)
_ATTRIBUTES = {
    "mass": (("mass", r"khoi luong|trong luong|mass|weight"),),
    "power": (("power", r"cong suat|power"),),
    "length": (
        ("length", r"chieu dai|length"),
        ("width", r"chieu rong|be rong|width"),
        ("height", r"chieu cao|height"),
        ("depth", r"chieu sau|depth"),
        ("thickness", r"do day|be day|thickness"),
        ("diameter", r"duong kinh|diameter"),
        ("radius", r"ban kinh|radius"),
    ),
}
_TARGET_STOPWORDS = {
    "cua",
    "co",
    "la",
    "voi",
    "the",
    "a",
    "an",
    "has",
    "have",
    "is",
    "its",
    "of",
    "rated",
    "nominal",
    "danh",
    "dinh",
}


def _fold(text: str) -> str:
    return "".join(
        char
        for char in unicodedata.normalize("NFD", text.lower().replace("đ", "d"))
        if not unicodedata.combining(char)
    )


def _attribution(prefix: str, dimension: str) -> tuple[str | None, str | None]:
    """Read only a nearby explicit physical attribute and simple measurement subject."""
    prefix = re.split(r"[.;,:!?()\n]|\b(?:va|and)\b", _fold(prefix[-160:]))[-1]
    matches = [
        (match, attribute)
        for attribute, pattern in _ATTRIBUTES.get(dimension, ())
        for match in re.finditer(r"\b(?:" + pattern + r")\b", prefix)
    ]
    if not matches:
        return None, None
    match, attribute = max(matches, key=lambda item: item[0].end())
    before, after = prefix[: match.start()].strip(), prefix[match.end() :].strip()
    subject = after or before
    if re.match(r"^(?:may|thiet bi|san pham|hang hoa|product|device|equipment|machine)\b", subject):
        if not re.search(r"\b(?:gom|contains|includes|component|part|with|of)\b", subject):
            return attribute, "WHOLE"
    words = [word for word in re.findall(r"\w+", subject) if word not in _TARGET_STOPWORDS]
    if not words or " ".join(words) in {
        "toan bo",
        "whole",
        "whole unit",
        "whole product",
        "whole device",
    }:
        return attribute, "WHOLE"
    return attribute, " ".join(words)


@dataclass(frozen=True)
class _Quantity:
    dimension: str
    operator: str
    value: Decimal | None
    text: str
    attribute: str | None
    subject: str | None


def _number(text: str) -> Decimal | None:
    text = text.replace("\u00a0", " ").strip()
    if " " in text:
        if not re.fullmatch(r"[+-]?\d{1,3}(?: \d{3})+", text):
            return None
        text = text.replace(" ", "")
    if re.fullmatch(r"[+-]?[1-9]\d{0,2}[.,]\d{3}", text):
        return None
    try:
        value = Decimal(text.replace(",", "."))
    except InvalidOperation:
        return None
    return value if value.is_finite() and value >= 0 else None


def _quantities(text: str, *, facts: bool = False) -> list[_Quantity]:
    text = unicodedata.normalize("NFC", text)
    folded = _fold(text)
    if facts and (_UNCERTAIN.search(folded) or _NEGATED_ASSERTION.search(folded)):
        return []
    found = []
    for match in _QUANTITY.finditer(text):
        operator_text = match["operator"]
        if not facts and operator_text is None:
            continue
        before = text[: match.start()].strip().lower()
        if facts and re.search(r"(?:không\s+phải|khong\s+phai|not|isn't|wasn't)\s*$", before):
            continue
        operator = next(
            (
                name
                for name, pattern in _OPERATORS
                if operator_text and re.fullmatch(pattern, operator_text, flags=re.IGNORECASE)
            ),
            "=",
        )
        unit = match["unit"]
        if unit in _CASE_UNITS:
            dimension, scale = _CASE_UNITS[unit]
        elif unit.lower() in _AMBIGUOUS_UNITS:
            dimension, scale = _AMBIGUOUS_UNITS[unit.lower()], None
        else:
            dimension, scale = _BASE_UNITS[unit.lower()]
        value = _number(match["number"])
        value = value * Decimal(scale) if value is not None and scale is not None else None
        attribute, subject = _attribution(text[: match.start()], dimension)
        found.append(_Quantity(dimension, operator, value, match[0].strip(), attribute, subject))
    return found


def _proves(fact: _Quantity, threshold: _Quantity) -> bool:
    if fact.dimension != threshold.dimension or fact.value is None or threshold.value is None:
        return False
    if threshold.dimension == "length" and (
        threshold.attribute is None or fact.attribute != threshold.attribute
    ):
        return False
    if (fact.subject or "WHOLE") != (threshold.subject or "WHOLE"):
        return False
    value, bound = fact.value, threshold.value
    if threshold.operator == "<=":
        return fact.operator in {"=", "<=", "<"} and value <= bound
    if threshold.operator == "<":
        return (fact.operator in {"=", "<="} and value < bound) or (
            fact.operator == "<" and value <= bound
        )
    if threshold.operator == ">=":
        return fact.operator in {"=", ">=", ">"} and value >= bound
    if threshold.operator == ">":
        return (fact.operator in {"=", ">="} and value > bound) or (
            fact.operator == ">" and value >= bound
        )
    return fact.operator == "=" and value == bound


def quantitative_grounding_errors(
    review: dict,
    sources: dict[str, dict],
    required_labels: set[str],
) -> list[str]:
    """Require quoted user measurements for numeric conditions claimed SUPPORTED."""
    if review.get("status") != "SUPPORTED":
        return []
    facts = review.get("product_facts", [])
    errors = []
    for label in sorted(required_labels):
        source = sources.get(label)
        if source is None:
            continue
        for threshold in _quantities(source["text"]):
            matching = [
                check
                for check in review.get("condition_checks", [])
                if check["source_label"] == label
                and check["assessment"] == "SATISFIED"
                and any(
                    (item.dimension, item.operator, item.value)
                    == (threshold.dimension, threshold.operator, threshold.value)
                    for item in _quantities(check["source_quote"])
                )
            ]
            proven = bool(matching)
            for check in matching:
                measurements = [
                    quantity
                    for index in check["product_fact_indices"]
                    if isinstance(index, int) and 0 <= index < len(facts)
                    for quantity in _quantities(facts[index]["user_quote"], facts=True)
                    if quantity.dimension == threshold.dimension
                ]
                if not measurements or not all(_proves(item, threshold) for item in measurements):
                    proven = False
                    break
            if not proven:
                errors.append(
                    f"Điều kiện định lượng về {_NAMES[threshold.dimension]} tại [{label}] "
                    f"({threshold.text}) chưa được chứng minh bằng số đo hoặc giới hạn rõ ràng "
                    "trong trích đoạn người dùng được điều kiện tham chiếu. Không suy ra phép đo "
                    "từ tên hàng hoặc diễn giải của model. Nếu thiếu dữ kiện, dùng "
                    "MISSING_PRODUCT_INFO để hỏi thuộc tính này; nếu dữ kiện bác bỏ điều kiện, "
                    "dùng REQUIRES_REVIEW thay vì SUPPORTED."
                )
    return list(dict.fromkeys(errors))
