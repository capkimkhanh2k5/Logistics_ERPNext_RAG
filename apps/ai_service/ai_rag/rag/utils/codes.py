"""HS code format normalization without classification inference."""

import re


def normalize_code(value: str) -> str:
    if not re.fullmatch(
        r"(?:\d{2}|\d{4}|\d{6}|\d{8}|\d{2}\.\d{2}|\d{4}\.\d{2}(?:\.\d{2})?)", value
    ):
        raise ValueError(f"Invalid HS code: {value}")
    return value.replace(".", "")
