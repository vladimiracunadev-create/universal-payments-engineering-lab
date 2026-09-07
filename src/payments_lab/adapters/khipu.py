"""Khipu Instant Payments API v3 adapter."""

from __future__ import annotations

import os

from ..core.http import JsonHTTPClient, require_https_base_url
from ..core.validation import https_url, positive_amount, require_fields, safe_identifier
from ..core.webhooks import verify_khipu_signature
from .base import PaymentProvider


class KhipuProvider(PaymentProvider):
    """Production transport. Credentials and merchant enablement remain external."""

    def __init__(self, api_key=None, base_url=None, http=None, webhook_secret=None):
        self.api_key = api_key or os.getenv("KHIPU_API_KEY")
        self.webhook_secret = webhook_secret or os.getenv("KHIPU_WEBHOOK_SECRET")
        self.base_url = require_https_base_url(
            base_url or os.getenv("KHIPU_BASE_URL") or "https://payment-api.khipu.com"
        )
        self.http = http or JsonHTTPClient()
        if not self.api_key:
            raise RuntimeError("KHIPU_API_KEY is required")

    @property
    def headers(self):
        return {"x-api-key": self.api_key}

    def list_banks(self):
        return self.http.request("GET", f"{self.base_url}/v3/banks", headers=self.headers)

    def create(self, payload: dict, **kwargs):
        require_fields(payload, "amount", "currency", "subject")
        outbound = dict(payload)
        outbound["amount"] = positive_amount(outbound["amount"])
        for field in ("return_url", "cancel_url", "notify_url"):
            if outbound.get(field):
                outbound[field] = https_url(outbound[field], name=field)
        return self.http.request("POST", f"{self.base_url}/v3/payments", headers=self.headers, payload=outbound)

    def get(self, payment_id: str):
        payment_id = safe_identifier(payment_id, name="payment_id")
        return self.http.request("GET", f"{self.base_url}/v3/payments/{payment_id}", headers=self.headers)

    def delete(self, payment_id: str):
        payment_id = safe_identifier(payment_id, name="payment_id")
        return self.http.request("DELETE", f"{self.base_url}/v3/payments/{payment_id}", headers=self.headers)

    def verify_webhook(self, raw_body: bytes, signature_header: str, *, now=None):
        if not self.webhook_secret:
            raise RuntimeError("KHIPU_WEBHOOK_SECRET is required to authenticate webhooks")
        verify_khipu_signature(raw_body, signature_header, self.webhook_secret, now=now)
