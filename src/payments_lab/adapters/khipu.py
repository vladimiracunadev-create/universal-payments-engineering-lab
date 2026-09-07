import os
from .base import PaymentProvider
from ..core.http import JsonHTTPClient

class KhipuProvider(PaymentProvider):
    """Khipu Instant Payments API v3 client. Requires user's official API key."""
    def __init__(self, api_key=None, base_url=None, http=None):
        self.api_key = api_key or os.getenv("KHIPU_API_KEY")
        self.base_url = (base_url or os.getenv("KHIPU_BASE_URL") or "https://payment-api.khipu.com").rstrip("/")
        self.http = http or JsonHTTPClient()
        if not self.api_key:
            raise RuntimeError("KHIPU_API_KEY is required")

    @property
    def headers(self):
        return {"x-api-key": self.api_key}

    def create(self, payload: dict, **kwargs):
        return self.http.request("POST", f"{self.base_url}/v3/payments", headers=self.headers, payload=payload)

    def get(self, payment_id: str):
        return self.http.request("GET", f"{self.base_url}/v3/payments/{payment_id}", headers=self.headers)

    def delete(self, payment_id: str):
        return self.http.request("DELETE", f"{self.base_url}/v3/payments/{payment_id}", headers=self.headers)

    def void(self, payment_id: str):
        return self.http.request("POST", f"{self.base_url}/v3/payments/{payment_id}/void", headers=self.headers, payload={})

    def refund(self, payment_id: str, payload=None):
        return self.http.request("POST", f"{self.base_url}/v3/payments/{payment_id}/refund", headers=self.headers, payload=payload or {})
