"""Conservative negative checks; these do not establish semantic entailment."""

import re

from rag.llm.validation import _folded


def _explicit_values(quotes: list[str], pattern: str) -> set[tuple[str, bool]]:
    values = set()
    for quote in quotes:
        # Questions/conditions do not assert the presentation/capability being asked about.
        quote = re.split(
            r"\b(?:hãy|có thể phân loại|nên phân loại|mã HS|áp dụng GIR)\b",
            quote,
            maxsplit=1,
            flags=re.I,
        )[0]
        for clause in re.split(r"[.;!?]|\b(?:nhung|ma)\b", _folded(quote)):
            if re.search(r"chua (?:biet|ro|xac dinh)|neu |gia su", clause):
                continue
            for match in re.finditer(pattern, clause):
                before = clause[: match.start()]
                negative = bool(re.search(r"\b(?:khong|chua|not)\b[^,;.!?]{0,60}$", before))
                values.add((match[0], not negative))
    return values


_PRESENTATION = r"\b(?:ckd|cbu|nguyen chiec|chua lap rap|thao roi|unassembled|disassembled)\b"
_CHARGING = r"\b(?:phev|hev|plug.in|(?:sac|nap(?: dien)?)[^.;!?]{0,70}ngoai|cam sac)\b"


def unsupported_qualifier_errors(texts: list[str], quotes: list[str]) -> list[str]:
    """Integrated equipment does not, by itself, prove permanent integration."""
    permanence = r"\b(?:vinh vien|permanently|permanent)\b"
    if any(value for _, value in _explicit_values(quotes, permanence)):
        return []
    for text in texts:
        for sentence in re.split(r"[.;!?]", _folded(text)):
            if not re.search(permanence, sentence):
                continue
            if re.match(r"\s*(?:neu|khi|nguon|quy dinh|chu giai)\b", sentence) or re.search(
                r"\b(?:chua (?:xac nhan|biet|ro)|khong (?:co|du) (?:du kien|can cu))\b",
                sentence,
            ):
                continue
            if re.search(r"\b(?:thiet bi|hang hoa|san pham|phuong tien|camera)\b", sentence):
                return [
                    "Không có dữ kiện xác nhận tính vĩnh viễn của bộ phận tích hợp. Bỏ thuộc tính tự thêm trong diễn giải, giữ nguyên mô tả người dùng; chỉ hỏi nếu thuộc tính thực sự quyết định mã."
                ]
    return []


def discriminating_fact_errors(
    texts: list[str], quotes: list[str], *, satisfied=False, context=None
) -> list[str]:
    """Reject two observed name/capacity-to-attribute substitutions, not classify goods."""
    sources = [_folded(text) for text in texts]
    errors = []
    if satisfied and any(re.search(r"\bchi su dung dong co dot trong\b", text) for text in sources):
        only_fuel = any(
            value
            for _, value in _explicit_values(
                quotes,
                r"\b(?:chi(?: (?:su dung|dung|co))?|duy nhat)[^.;!?]{0,35}dong co[^.;!?]{0,30}(?:diesel|xang|dot trong|nhien lieu)\b",
            )
        )
        no_electric = any(
            re.search(r"\bkhong (?:co |su dung |dung )?(?:bat ky )?dong co dien\b", _folded(q))
            and not re.search(r"\b(?:neu|gia su|chua ro)\b", _folded(q))
            for q in quotes
        )
        if not only_fuel and not no_electric:
            errors.append(
                "Nguồn yêu cầu CHỈ sử dụng động cơ đốt trong; chữ diesel/xăng không chứng minh không có động cơ điện cùng tạo lực kéo. Không xác nhận SATISFIED. Nếu chưa rõ, hỏi có động cơ điện cùng tạo lực kéo hay chỉ động cơ nhiên liệu, trước khi hỏi sạc ngoài; nếu đã có động cơ điện cùng tạo lực kéo, dùng CONTRADICTED."
            )
    forms = _explicit_values(quotes, _PRESENTATION)
    if any(re.search(r"\bckd\b|(?:loai|dang) nguyen chiec", text) for text in sources):
        if not forms:
            errors.append(
                "Dạng nhập khẩu chưa có dữ kiện tường minh; tên/model hoặc cụm 'nhập khẩu xe' không chứng minh CKD/nguyên chiếc. Dùng MISSING_PRODUCT_INFO và hỏi dạng nhập khẩu."
            )
        elif satisfied:
            if any(
                re.fullmatch(r"[\W_]*(?:dang )?ckd[\W_]*", text) for text in sources
            ) and not any(
                value and form in {"ckd", "chua lap rap", "thao roi", "unassembled", "disassembled"}
                for form, value in forms
            ):
                errors.append(
                    "Điều kiện CKD chưa được chứng minh bằng dữ kiện về dạng tháo rời/CKD."
                )
            if any(
                re.fullmatch(r"[\W_]*(?:loai|dang) nguyen chiec[\W_]*", text) for text in sources
            ) and not any(value and form in {"cbu", "nguyen chiec"} for form, value in forms):
                errors.append(
                    "Điều kiện nguyên chiếc chưa có dữ kiện khẳng định, không dùng câu phủ định/đính chính để chứng minh SATISFIED."
                )
        if context and len(context.get("request", {}).get("items", [])) == 1:
            statements = context["user_context"]["statements"]
            explicit = [s for s in statements if _explicit_values([s["text"]], _PRESENTATION)]
            if explicit:
                latest = max(s.get("turn", 1) for s in explicit)
                declaration = max(
                    (s for s in statements if s.get("turn", 1) == latest),
                    key=lambda s: len(s["text"]),
                )
                current = _explicit_values([declaration["text"]], _PRESENTATION)

                def state(form):
                    return "WHOLE" if form in {"cbu", "nguyen chiec"} else "DISASSEMBLED"

                known = {state(form) for form, value in current if value}
                cited = {state(form) for form, value in forms if value}
                if latest > 1 and known and cited - known:
                    errors.append(
                        "Trích đoạn dạng nhập khẩu mâu thuẫn với đính chính mới nhất; không dùng trạng thái cũ hoặc cắt mất phủ định để chứng minh điều kiện."
                    )
    external = [
        text
        for text in sources
        if re.search(r"nap dien[^.;]{0,80}nguon dien[^.;]{0,25}ben ngoai", text)
    ]
    if external:
        mentions = _explicit_values(quotes, _CHARGING)
        charging = {
            False if form == "hev" else value
            for form, value in mentions
            if form not in {"hev", "phev"} or value
        }
        if not charging:
            errors.append(
                "Khả năng sạc từ nguồn điện bên ngoài chưa được người dùng xác nhận; dung lượng pin hoặc tên xe không chứng minh thuộc tính này. Dùng MISSING_PRODUCT_INFO và hỏi khả năng sạc ngoài."
            )
        elif satisfied and any(
            (not bool(re.search(r"\btru loai\b", text))) not in charging for text in external
        ):
            errors.append(
                "Dữ kiện sạc ngoài không chứng minh chiều điều kiện của nguồn; giữ đúng phủ định và nhánh có/trừ loại nạp điện ngoài."
            )
    return errors


def indirect_drive_gap(question: str, texts: list[str]) -> bool:
    """A generic combined-drive heading cannot settle an explicitly indirect mechanism."""
    indirect = re.search(
        r"khong truyen (?:luc|dong luc|luc co hoc)[^.;]{0,50}truc tiep|"
        r"dong co[^.;]{0,55}chi (?:dung de |de )?phat dien",
        _folded(question),
    )
    combined = any(
        "dong co dot trong" in _folded(text)
        and "dong co dien" in _folded(text)
        and "dong luc" in _folded(text)
        for text in texts
    )
    mechanism = any(
        re.search(
            r"may phat dien|truyen luc[^.;]{0,50}gian tiep|hybrid noi tiep|series hybrid",
            _folded(text),
        )
        for text in texts
    )
    return bool(indirect and combined and not mechanism)


def defining_note_errors(review: dict, sources: dict, candidate: dict) -> list[str]:
    """Reject name-only evidence for a definition containing technical requirements.

    Require at least a concrete property clause in the quoted facts. The model review
    still owns semantic coverage, negation and application of that clause to the note.
    This guard never turns an unsupported fact into a supported one.
    """
    errors = []
    facts = review.get("product_facts", [])
    for check in review.get("condition_checks", []):
        label = check["source_label"]
        if check["assessment"] != "SATISFIED" or label not in candidate.get(
            "defining_note_labels", []
        ):
            continue
        quotes = [
            facts[i]["user_quote"] for i in check["product_fact_indices"] if 0 <= i < len(facts)
        ]

        explicit = any(
            re.search(
                r"\b(?:co|gom|su dung|chay|cai dat|tai|ho tro|thuc hien|lam bang|duoc che tao|"
                r"chuc nang|he dieu hanh|bo xu ly|cau tao|thanh phan|cong suat|khoi luong|"
                r"che tac|bang|ma vang|ma bac|ma dien|khong dinh|khong gan|khong chua|"
                r"contains|supports|runs|made of|operating system)\b",
                _folded(q),
            )
            for q in quotes
        )
        if not explicit and sources.get(label):
            errors.append(
                f"Định nghĩa tại [{label}] chưa được chứng minh bằng thuộc tính tường minh; "
                "tên/model và trạng thái nguyên chiếc không đủ xác nhận điều kiện kỹ thuật. "
                "Dùng MISSING_PRODUCT_INFO và hỏi điều kiện của định nghĩa còn thiếu."
            )
    return errors


def presentation_scope_errors(texts: list[str], quotes: list[str]) -> list[str]:
    """A separately-presented exclusion needs evidence of that presentation scope."""
    conditional = any(
        re.search(
            r"khi (?:no )?(?:duoc )?trinh bay rieng|when (?:they are )?presented separately",
            _folded(text),
        )
        for text in texts
    )
    if not conditional:
        return []
    explicit = any(
        re.search(
            r"(?:trinh bay|nhap khau|nhap) rieng|presented separately|imported separately",
            _folded(quote),
        )
        and not re.search(
            r"(?:khong|chua)[^.;]{0,35}(?:trinh bay|nhap khau|nhap) rieng|not presented separately",
            _folded(quote),
        )
        for quote in quotes
    )
    return (
        []
        if explicit
        else [
            "Điều khoản loại trừ được dẫn chỉ áp dụng khi trình bày riêng rẽ; trích đoạn dữ kiện "
            "chưa xác nhận phạm vi này. Không loại một thiết bị tích hợp chỉ từ chức năng của "
            "bộ phận bên trong; phải đối chiếu quy tắc áp dụng cho toàn thiết bị."
        ]
    )
