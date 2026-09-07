"""Validation at the outbound provider trust boundary."""

from __future__ import annotations

import re
from collections.abc import Mapping
from decimal import Decimal, InvalidOperation
from urllib.parse import urlsplit

SAFE_IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")


def require_fields(payload: Mapping[str, object], *fields: str) -> None:
    missing = [field for field in fields if payload.get(field) in (None, "")]
    if missing:
        raise ValueError(f"missing required fields: {', '.join(missing)}")


def safe_identifier(value: object, *, name: str = "identifier", max_length: int = 128) -> str:
    text = str(value)
    if len(text) > max_length or not SAFE_IDENTIFIER.fullmatch(text):
        raise ValueError(f"{name} contains unsafe characters or has invalid length")
    return text


def positive_amount(value: object, *, name: str = "amount") -> int | str:
    if isinstance(value, bool) or isinstance(value, float):
        raise ValueError(f"{name} must be an integer or decimal string, never float")
    try:
        decimal = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{name} is not a valid decimal amount") from exc
    if not decimal.is_finite() or decimal <= 0:
        raise ValueError(f"{name} must be positive and finite")
    return value if isinstance(value, int) else format(decimal, "f")


def https_url(value: object, *, name: str) -> str:
    text = str(value)
    parsed = urlsplit(text)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError(f"{name} must be an absolute HTTPS URL without embedded credentials")
    return text
