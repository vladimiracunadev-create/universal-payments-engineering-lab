"""Transbank Webpay Plus REST transport."""

from __future__ import annotations

import os

from ..core.http import JsonHTTPClient, require_https_base_url
from ..core.validation import https_url, positive_amount, require_fields, safe_identifier
from .base import PaymentProvider


class WebpayPlusProvider(PaymentProvider):
    def __init__(self, commerce_code=None, api_key=None, base_url=None, http=None):
        self.commerce_code = commerce_code or os.getenv("TRANSBANK_COMMERCE_CODE")
        self.api_key = api_key or os.getenv("TRANSBANK_API_KEY")
        url = base_url or os.getenv("TRANSBANK_BASE_URL")
        if not (self.commerce_code and self.api_key and url):
            raise RuntimeError("TRANSBANK_COMMERCE_CODE, TRANSBANK_API_KEY and TRANSBANK_BASE_URL are required")
        self.base_url = require_https_base_url(url)
        self.http = http or JsonHTTPClient()

    @property
    def headers(self):
        return {"Tbk-Api-Key-Id": self.commerce_code, "Tbk-Api-Key-Secret": self.api_key}

    def create(self, payload: dict, **kwargs):
        require_fields(payload, "buy_order", "session_id", "amount", "return_url")
        outbound = dict(payload)
        outbound["buy_order"] = safe_identifier(outbound["buy_order"], name="buy_order", max_length=26)
        outbound["session_id"] = safe_identifier(outbound["session_id"], name="session_id", max_length=61)
        outbound["amount"] = positive_amount(outbound["amount"])
        outbound["return_url"] = https_url(outbound["return_url"], name="return_url")
        return self.http.request("POST", f"{self.base_url}/transactions", headers=self.headers, payload=outbound)

    def commit(self, token: str):
        token = safe_identifier(token, name="token")
        return self.http.request("PUT", f"{self.base_url}/transactions/{token}", headers=self.headers, payload={})

    def get(self, payment_id: str):
        token = safe_identifier(payment_id, name="token")
        return self.http.request("GET", f"{self.base_url}/transactions/{token}", headers=self.headers)

    def refund(self, token: str, amount):
        token = safe_identifier(token, name="token")
        return self.http.request(
            "POST",
            f"{self.base_url}/transactions/{token}/refunds",
            headers=self.headers,
            payload={"amount": positive_amount(amount)},
        )
