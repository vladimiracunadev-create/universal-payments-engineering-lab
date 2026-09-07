import os
from .base import PaymentProvider
from ..core.http import JsonHTTPClient

class WebpayPlusProvider(PaymentProvider):
    """Webpay Plus REST transport. Use only with credentials/environment authorized by Transbank."""
    def __init__(self, commerce_code=None, api_key=None, base_url=None, http=None):
        self.commerce_code = commerce_code or os.getenv("TRANSBANK_COMMERCE_CODE")
        self.api_key = api_key or os.getenv("TRANSBANK_API_KEY")
        self.base_url = (base_url or os.getenv("TRANSBANK_BASE_URL") or "").rstrip("/")
        self.http = http or JsonHTTPClient()
        if not (self.commerce_code and self.api_key and self.base_url):
            raise RuntimeError("TRANSBANK_COMMERCE_CODE, TRANSBANK_API_KEY and TRANSBANK_BASE_URL are required")

    @property
    def headers(self):
        return {"Tbk-Api-Key-Id": self.commerce_code, "Tbk-Api-Key-Secret": self.api_key}

    def create(self, payload: dict, **kwargs):
        return self.http.request("POST", f"{self.base_url}/transactions", headers=self.headers, payload=payload)

    def commit(self, token: str):
        return self.http.request("PUT", f"{self.base_url}/transactions/{token}", headers=self.headers, payload={})

    def get(self, payment_id: str):
        return self.http.request("GET", f"{self.base_url}/transactions/{payment_id}", headers=self.headers)

    def refund(self, token: str, amount):
        return self.http.request("POST", f"{self.base_url}/transactions/{token}/refunds", headers=self.headers, payload={"amount": amount})
