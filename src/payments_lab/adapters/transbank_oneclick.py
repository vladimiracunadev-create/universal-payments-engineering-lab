"""Transbank Oneclick Mall enrollment and transaction REST adapter."""

from __future__ import annotations

import os

from ..core.http import JsonHTTPClient, require_https_base_url
from ..core.validation import https_url, positive_amount, require_fields, safe_identifier


class OneclickMallProvider:
    def __init__(self, commerce_code=None, api_key=None, base_url=None, http=None):
        self.commerce_code = commerce_code or os.getenv("TRANSBANK_ONECLICK_COMMERCE_CODE")
        self.api_key = api_key or os.getenv("TRANSBANK_ONECLICK_API_KEY")
        url = base_url or os.getenv("TRANSBANK_ONECLICK_BASE_URL")
        if not (self.commerce_code and self.api_key and url):
            raise RuntimeError("Oneclick commerce code, API key and base URL are required")
        self.base_url = require_https_base_url(url)
        self.http = http or JsonHTTPClient()

    @property
    def headers(self):
        return {"Tbk-Api-Key-Id": self.commerce_code, "Tbk-Api-Key-Secret": self.api_key}

    def start_enrollment(self, *, username: str, email: str, response_url: str):
        username = safe_identifier(username, name="username", max_length=40)
        if len(email) > 100 or "@" not in email:
            raise ValueError("email is invalid or exceeds 100 characters")
        payload = {"username": username, "email": email, "response_url": https_url(response_url, name="response_url")}
        return self.http.request("POST", f"{self.base_url}/inscriptions", headers=self.headers, payload=payload)

    def finish_enrollment(self, token: str):
        token = safe_identifier(token, name="token")
        return self.http.request("PUT", f"{self.base_url}/inscriptions/{token}", headers=self.headers, payload={})

    def delete_enrollment(self, *, tbk_user: str, username: str):
        payload = {
            "tbk_user": safe_identifier(tbk_user, name="tbk_user"),
            "username": safe_identifier(username, name="username", max_length=40),
        }
        return self.http.request("DELETE", f"{self.base_url}/inscriptions", headers=self.headers, payload=payload)

    def authorize(self, payload: dict):
        require_fields(payload, "username", "tbk_user", "buy_order", "details")
        if not isinstance(payload["details"], list) or not payload["details"]:
            raise ValueError("details must contain at least one child transaction")
        outbound = dict(payload)
        outbound["username"] = safe_identifier(outbound["username"], name="username", max_length=40)
        outbound["tbk_user"] = safe_identifier(outbound["tbk_user"], name="tbk_user")
        outbound["buy_order"] = safe_identifier(outbound["buy_order"], name="buy_order")
        outbound["details"] = [self._detail(item) for item in outbound["details"]]
        return self.http.request("POST", f"{self.base_url}/transactions", headers=self.headers, payload=outbound)

    def status(self, buy_order: str):
        buy_order = safe_identifier(buy_order, name="buy_order")
        return self.http.request("GET", f"{self.base_url}/transactions/{buy_order}", headers=self.headers)

    def refund(self, buy_order: str, *, commerce_code: str, detail_buy_order: str, amount):
        buy_order = safe_identifier(buy_order, name="buy_order")
        payload = {
            "commerce_code": safe_identifier(commerce_code, name="commerce_code"),
            "detail_buy_order": safe_identifier(detail_buy_order, name="detail_buy_order"),
            "amount": positive_amount(amount),
        }
        return self.http.request(
            "POST", f"{self.base_url}/transactions/{buy_order}/refunds", headers=self.headers, payload=payload
        )

    @staticmethod
    def _detail(item: dict) -> dict:
        require_fields(item, "commerce_code", "buy_order", "amount")
        return {
            **item,
            "commerce_code": safe_identifier(item["commerce_code"], name="commerce_code"),
            "buy_order": safe_identifier(item["buy_order"], name="detail_buy_order"),
            "amount": positive_amount(item["amount"]),
        }
