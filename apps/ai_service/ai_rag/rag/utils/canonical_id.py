"""Unified Canonical Identifier and Semantic Role Utilities.
Standardizes chunk IDs, document slugs, and boilerplate classification
across all legal documents, tariff nomenclature, and staging pipelines.
"""

import re
import unicodedata
from typing import Any, Optional


def remove_vietnamese_accents(text: str) -> str:
    """Removes diacritics/accents from Vietnamese string."""
    if not text:
        return ""
    text = unicodedata.normalize("NFD", text)
    text = re.sub(r"[\u0300-\u036f]", "", text)
    text = text.replace("đ", "d").replace("Đ", "D")
    return text


def normalize_document_key(document_no: Optional[str], default_fallback: str = "doc") -> str:
    """Transforms raw legal / customs document numbers into a unified canonical slug.

    Examples:
        'Thông tư 85/2026/TT-BTC' -> 'tt85_2026'
        '85/2026/TT-BTC'          -> 'tt85_2026'
        'Thông tư 31/2022/TT-BTC' -> 'tt31_2022'
        'Nghị định 08/2015/NĐ-CP' -> 'nd08_2015'
        'Nghị định 26/2015/NĐ-CP' -> 'nd26_2015'
        '02/2024/TT-BTTTT'        -> 'tt02_2024'
        '12/2022/TT-BGTVT'        -> 'tt12_2022'
        'VBHN 05/VBHN-BGTVT'      -> 'vbhn05_bgtvt'
        'GIR' / 'Quy tắc phân loại' -> 'gir'
    """
    if not document_no:
        return default_fallback.lower().strip()

    raw = document_no.strip()
    unaccented = remove_vietnamese_accents(raw).lower()

    if "gir" in unaccented or "quy tac" in unaccented:
        return "gir"

    # Match common Vietnamese legal document patterns: (TT|ND|QD|VBHN|LUAT) ... (number)/(year)
    match_legal = re.search(
        r"(tt|nd|qd|vbhn|luat|nghi dinh|thong tu|quyet dinh)[\s\-_]*([0-9]+)[\s/_]+([0-9]{4})",
        unaccented,
    )
    if match_legal:
        doc_type_raw = match_legal.group(1)
        doc_num = match_legal.group(2).zfill(2)
        doc_year = match_legal.group(3)

        prefix = "doc"
        if "tt" in doc_type_raw or "thong tu" in doc_type_raw:
            prefix = "tt"
        elif "nd" in doc_type_raw or "nghi dinh" in doc_type_raw:
            prefix = "nd"
        elif "qd" in doc_type_raw or "quyet dinh" in doc_type_raw:
            prefix = "qd"
        elif "vbhn" in doc_type_raw:
            prefix = "vbhn"
        elif "luat" in doc_type_raw:
            prefix = "luat"

        return f"{prefix}{doc_num}_{doc_year}"

    # Match simple (number)/(year)
    match_num_year = re.search(r"([0-9]+)/([0-9]{4})", unaccented)
    if match_num_year:
        num = match_num_year.group(1).zfill(2)
        year = match_num_year.group(2)
        prefix = "doc"
        if "tt" in unaccented or "thong tu" in unaccented:
            prefix = "tt"
        elif "nd" in unaccented or "nghi dinh" in unaccented:
            prefix = "nd"
        elif "qd" in unaccented or "quyet dinh" in unaccented:
            prefix = "qd"
        return f"{prefix}{num}_{year}"

    # Sanitize general string to snake_case
    clean = re.sub(r"[^a-z0-9]+", "_", unaccented).strip("_")
    return clean if clean else default_fallback


def is_boilerplate_content(title: Optional[str] = None, text: Optional[str] = None) -> bool:
    """Detects administrative boilerplate provisions (enforcement, transitional, standard formulas)
    as opposed to substantive legal/tariff rules.
    """
    combined = f"{title or ''} {text or ''}".lower()
    combined_clean = remove_vietnamese_accents(combined)

    boilerplate_phrases = [
        "hieu luc thi hanh",
        "hieu luc ap dung",
        "to chuc thuc hien",
        "trach nhiem thuc hien",
        "trach nhiem thi hanh",
        "dieu khoan chuyen tiep",
        "dieu khoan thi hanh",
        "noi nhan:",
        "noi nhan :",
        "chuc nang nhiem vu thi hanh",
        "thay the thong tu",
        "thay the nghi dinh",
        "bai bo quy dinh",
    ]

    for phrase in boilerplate_phrases:
        if phrase in combined_clean:
            return True

    # Biểu thuế / HS non-informative catch-all descriptions
    if text:
        t_clean = remove_vietnamese_accents(text).strip().lower()
        if t_clean in ("- loai khac", "-- loai khac", "--- loai khac", "---- loai khac", "loai khac"):
            return True

    return False


def generate_canonical_chunk_id(
    namespace: str,
    document_no: Optional[str],
    node_type: Any = None,
    code: Optional[str] = None,
    canonical_anchor: Optional[str] = None,
    node_order: int = 1,
    parent_anchor: Optional[str] = None,
) -> str:
    """Generates a deterministic, collision-resistant canonical Chunk ID conforming to:
    {namespace_prefix}:{doc_slug}:{entity_type}_{canonical_code}

    Examples:
        'legal:tt85_2026:clause_1_2'
        'legal:tt85_2026:art_3'
        'hs:tt31_2022:hs8_87037066'
        'hs:tt31_2022:chap_note_87_2'
        'hs:gir:rule_3_b'
    """
    ns_prefix = "hs" if "hs" in namespace.lower() else "legal"
    doc_slug = normalize_document_key(document_no, default_fallback="doc")
    nt_name = str(getattr(node_type, "name", getattr(node_type, "value", node_type))).upper()

    # 1. HS Nomenclature / Tariff Schedule
    if ns_prefix == "hs":
        if code:
            clean_code = re.sub(r"[^0-9a-zA-Z]+", "", code)
            if len(clean_code) == 8:
                return f"hs:{doc_slug}:hs8_{clean_code}"
            if len(clean_code) == 6:
                return f"hs:{doc_slug}:hs6_{clean_code}"
            if len(clean_code) == 4:
                return f"hs:{doc_slug}:hs4_{clean_code}"
            if len(clean_code) == 2:
                return f"hs:{doc_slug}:chap_{clean_code}"

        if "SECTION_NOTE" in nt_name and canonical_anchor:
            clean_anchor = re.sub(r"[^0-9a-zA-Z]+", "_", canonical_anchor).strip("_")
            return f"hs:{doc_slug}:sec_note_{clean_anchor}"

        if "CHAPTER_NOTE" in nt_name and canonical_anchor:
            clean_anchor = re.sub(r"[^0-9a-zA-Z]+", "_", canonical_anchor).strip("_")
            return f"hs:{doc_slug}:chap_note_{clean_anchor}"

        if doc_slug == "gir":
            clean_anchor = re.sub(r"[^0-9a-zA-Z]+", "_", canonical_anchor or str(node_order)).strip("_")
            return f"hs:gir:rule_{clean_anchor}"

        clean_anchor = re.sub(r"[^0-9a-zA-Z]+", "_", canonical_anchor or f"node_{node_order}").strip("_")
        return f"hs:{doc_slug}:entry_{clean_anchor}"

    # 2. Legal Documents (Law, Decree, Circular, Decision)
    if canonical_anchor:
        clean_anchor = remove_vietnamese_accents(canonical_anchor).lower()
        clean_anchor = re.sub(r"[^0-9a-z]+", "_", clean_anchor).strip("_")

        # Normalize common Vietnamese anchor formats
        # e.g., 'dieu_1_khoan_2' -> 'clause_1_2'
        # e.g., 'dieu_1' -> 'art_1'
        m_point = re.match(r"dieu_([0-9]+)_khoan_([0-9]+)_diem_([a-z0-9]+)", clean_anchor)
        if m_point:
            return f"legal:{doc_slug}:point_{m_point.group(1)}_{m_point.group(2)}_{m_point.group(3)}"

        m_clause = re.match(r"dieu_([0-9]+)_khoan_([0-9]+)", clean_anchor)
        if m_clause:
            return f"legal:{doc_slug}:clause_{m_clause.group(1)}_{m_clause.group(2)}"

        m_art = re.match(r"dieu_([0-9]+)", clean_anchor)
        if m_art:
            return f"legal:{doc_slug}:art_{m_art.group(1)}"

        return f"legal:{doc_slug}:{clean_anchor}"

    if "ARTICLE" in nt_name:
        return f"legal:{doc_slug}:art_{node_order}"
    if "CLAUSE" in nt_name:
        return f"legal:{doc_slug}:clause_{node_order}"
    if "DATA_ROW" in nt_name:
        return f"legal:{doc_slug}:item_{node_order}"

    return f"legal:{doc_slug}:chunk_{node_order}"
