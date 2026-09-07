"""Provider webhook authentication using published signature schemes."""

from __future__ import annotations

import base64
import hashlib
import hmac
import time


class InvalidWebhookSignature(ValueError):
    pass


def _parts(header: str) -> dict[str, str]:
    return dict(part.strip().split("=", 1) for part in header.split(",") if "=" in part)


def _fresh(timestamp_ms: int, *, now: float | None, tolerance_seconds: int) -> None:
    current = time.time() if now is None else now
    if abs(current - timestamp_ms / 1000) > tolerance_seconds:
        raise InvalidWebhookSignature("webhook timestamp is outside the replay window")


def verify_khipu_signature(
    raw_body: bytes, signature_header: str, secret: str, *, now=None, tolerance_seconds=300
) -> None:
    """Verify `t=<ms>,s=<base64>` over `<timestamp>.<raw JSON bytes>`."""
    values = _parts(signature_header)
    try:
        timestamp, supplied = int(values["t"]), values["s"]
    except (KeyError, ValueError) as exc:
        raise InvalidWebhookSignature("Khipu signature requires numeric t and s") from exc
    _fresh(timestamp, now=now, tolerance_seconds=tolerance_seconds)
    message = str(timestamp).encode("ascii") + b"." + raw_body
    expected = base64.b64encode(hmac.new(secret.encode(), message, hashlib.sha256).digest()).decode()
    if not hmac.compare_digest(expected, supplied):
        raise InvalidWebhookSignature("invalid Khipu webhook signature")


def verify_mercadopago_signature(
    *, data_id: str, request_id: str, signature_header: str, secret: str, now=None, tolerance_seconds=300
) -> None:
    """Verify Mercado Pago's `id:...;request-id:...;ts:...;` manifest."""
    values = _parts(signature_header)
    try:
        timestamp, supplied = int(values["ts"]), values["v1"]
    except (KeyError, ValueError) as exc:
        raise InvalidWebhookSignature("Mercado Pago signature requires numeric ts and v1") from exc
    _fresh(timestamp, now=now, tolerance_seconds=tolerance_seconds)
    manifest = f"id:{data_id.lower()};request-id:{request_id};ts:{timestamp};"
    expected = hmac.new(secret.encode(), manifest.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, supplied):
        raise InvalidWebhookSignature("invalid Mercado Pago webhook signature")
