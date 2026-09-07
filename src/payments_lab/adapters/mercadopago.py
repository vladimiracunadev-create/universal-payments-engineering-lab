"""Mercado Pago Payments API adapter."""

from __future__ import annotations

import os

from ..core.http import JsonHTTPClient, require_https_base_url
from ..core.validation import positive_amount, require_fields, safe_identifier
from ..core.webhooks import verify_mercadopago_signature
from .base import PaymentProvider


class MercadoPagoProvider(PaymentProvider):
    """Direct Payments API client with mandatory idempotency for mutations."""

    def __init__(self, access_token=None, base_url=None, http=None, webhook_secret=None):
        self.token = access_token or os.getenv("MERCADOPAGO_ACCESS_TOKEN")
        self.webhook_secret = webhook_secret or os.getenv("MERCADOPAGO_WEBHOOK_SECRET")
        self.base_url = require_https_base_url(
            base_url or os.getenv("MERCADOPAGO_BASE_URL") or "https://api.mercadopago.com"
        )
        self.http = http or JsonHTTPClient()
        if not self.token:
            raise RuntimeError("MERCADOPAGO_ACCESS_TOKEN is required")

    def _headers(self, idempotency_key=None):
        headers = {"Authorization": f"Bearer {self.token}"}
        if idempotency_key:
            headers["X-Idempotency-Key"] = safe_identifier(idempotency_key, name="idempotency_key")
        return headers

    def create(self, payload: dict, **kwargs):
        key = kwargs.get("idempotency_key")
        if not key:
            raise ValueError("idempotency_key is required for monetary create operations")
        require_fields(payload, "transaction_amount", "payment_method_id", "payer")
        outbound = dict(payload)
        outbound["transaction_amount"] = positive_amount(outbound["transaction_amount"], name="transaction_amount")
        return self.http.request("POST", f"{self.base_url}/v1/payments", headers=self._headers(key), payload=outbound)

    def get(self, payment_id: str):
        payment_id = safe_identifier(payment_id, name="payment_id")
        return self.http.request("GET", f"{self.base_url}/v1/payments/{payment_id}", headers=self._headers())

    def refund(self, payment_id: str, *, amount=None, idempotency_key: str):
        payment_id = safe_identifier(payment_id, name="payment_id")
        payload = {} if amount is None else {"amount": positive_amount(amount)}
        return self.http.request(
            "POST",
            f"{self.base_url}/v1/payments/{payment_id}/refunds",
            headers=self._headers(idempotency_key),
            payload=payload,
        )

    def verify_webhook(self, *, data_id: str, request_id: str, signature_header: str, now=None):
        if not self.webhook_secret:
            raise RuntimeError("MERCADOPAGO_WEBHOOK_SECRET is required to authenticate webhooks")
        verify_mercadopago_signature(
            data_id=data_id,
            request_id=request_id,
            signature_header=signature_header,
            secret=self.webhook_secret,
            now=now,
        )
