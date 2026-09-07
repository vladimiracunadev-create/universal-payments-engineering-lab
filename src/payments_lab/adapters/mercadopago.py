import os
from .base import PaymentProvider
from ..core.http import JsonHTTPClient

class MercadoPagoProvider(PaymentProvider):
    """Direct Payments API client. Payload intentionally remains explicit because fields differ by payment method."""
    def __init__(self, access_token=None, base_url=None, http=None):
        self.token = access_token or os.getenv("MERCADOPAGO_ACCESS_TOKEN")
        self.base_url = (base_url or os.getenv("MERCADOPAGO_BASE_URL") or "https://api.mercadopago.com").rstrip("/")
        self.http = http or JsonHTTPClient()
        if not self.token:
            raise RuntimeError("MERCADOPAGO_ACCESS_TOKEN is required")

    def _headers(self, idempotency_key=None):
        h = {"Authorization": f"Bearer {self.token}"}
        if idempotency_key:
            h["X-Idempotency-Key"] = idempotency_key
        return h

    def create(self, payload: dict, **kwargs):
        key = kwargs.get("idempotency_key")
        if not key:
            raise ValueError("idempotency_key is required for monetary create operations")
        return self.http.request("POST", f"{self.base_url}/v1/payments", headers=self._headers(key), payload=payload)

    def get(self, payment_id: str):
        return self.http.request("GET", f"{self.base_url}/v1/payments/{payment_id}", headers=self._headers())

    def refund(self, payment_id: str, *, amount=None, idempotency_key: str):
        payload = {} if amount is None else {"amount": amount}
        return self.http.request("POST", f"{self.base_url}/v1/payments/{payment_id}/refunds", headers=self._headers(idempotency_key), payload=payload)
