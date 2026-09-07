"""Hardened JSON transport for payment-provider adapters.

The client deliberately does not retry: after a monetary mutation times out,
the result is unknown and the provider must be queried before another attempt.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlsplit

RETRYABLE_HTTP_STATUSES = {408, 425, 429, 500, 502, 503, 504}


class InvalidProviderResponse(RuntimeError):
    """The provider returned a response outside the JSON contract."""


class ProviderTransportError(RuntimeError):
    def __init__(self, message: str, *, outcome_unknown: bool):
        super().__init__(message)
        self.outcome_unknown = outcome_unknown


class ProviderHTTPError(RuntimeError):
    def __init__(self, status: int, body: str, *, request_id: str | None = None):
        super().__init__(f"Provider HTTP {status}: {body[:500]}")
        self.status = status
        self.body = body
        self.request_id = request_id
        self.retryable = status in RETRYABLE_HTTP_STATUSES


def require_https_base_url(url: str, *, allow_localhost_http: bool = False) -> str:
    parsed = urlsplit(url)
    local = parsed.hostname in {"localhost", "127.0.0.1", "::1"}
    if not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("base_url must be an absolute provider URL without credentials, query or fragment")
    if parsed.scheme != "https" and not (allow_localhost_http and parsed.scheme == "http" and local):
        raise ValueError("base_url must use HTTPS")
    return url.rstrip("/")


@dataclass(frozen=True)
class JsonHTTPClient:
    timeout: float = 15.0
    max_response_bytes: int = 1_048_576
    user_agent: str = "universal-payments-engineering-lab/0.1"

    def request(self, method: str, url: str, *, headers=None, payload=None, timeout=None) -> dict[str, Any]:
        require_https_base_url(url)
        method = method.upper()
        body = None
        request_headers = {"Accept": "application/json", "User-Agent": self.user_agent, **(headers or {})}
        if payload is not None:
            body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
            request_headers.setdefault("Content-Type", "application/json")
        request = urllib.request.Request(url, data=body, headers=request_headers, method=method)
        try:
            with urllib.request.urlopen(  # nosec B310
                request, timeout=timeout or self.timeout
            ) as response:
                raw = response.read(self.max_response_bytes + 1)
                if len(raw) > self.max_response_bytes:
                    raise InvalidProviderResponse("provider response exceeds configured size limit")
                return self._decode(raw)
        except urllib.error.HTTPError as exc:
            raw = exc.read(self.max_response_bytes).decode("utf-8", errors="replace")
            request_id = exc.headers.get("x-request-id") if exc.headers else None
            raise ProviderHTTPError(exc.code, raw, request_id=request_id) from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            detail = exc.reason if isinstance(exc, urllib.error.URLError) else exc
            raise ProviderTransportError(
                f"provider transport failed: {detail}",
                outcome_unknown=method not in {"GET", "HEAD", "OPTIONS"},
            ) from exc

    @staticmethod
    def _decode(raw: bytes) -> dict[str, Any]:
        if not raw:
            return {}
        try:
            decoded = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise InvalidProviderResponse("provider returned invalid UTF-8 JSON") from exc
        if not isinstance(decoded, dict):
            raise InvalidProviderResponse("provider JSON root must be an object")
        return decoded
