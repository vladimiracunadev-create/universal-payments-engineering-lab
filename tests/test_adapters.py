import unittest
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from payments_lab.adapters.khipu import KhipuProvider
from payments_lab.adapters.mercadopago import MercadoPagoProvider
from payments_lab.adapters.transbank import WebpayPlusProvider


class FakeHTTP:
    def __init__(self):
        self.calls = []

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        return {"ok": True}


class KhipuAdapterTests(unittest.TestCase):
    def setUp(self):
        self.http = FakeHTTP()
        self.provider = KhipuProvider(api_key="secret", base_url="https://provider.invalid", http=self.http)

    def test_create_uses_v3_endpoint_and_api_key(self):
        self.provider.create({"amount": 1000})
        method, url, kwargs = self.http.calls[-1]
        self.assertEqual((method, url), ("POST", "https://provider.invalid/v3/payments"))
        self.assertEqual(kwargs["headers"], {"x-api-key": "secret"})

    def test_void_is_a_distinct_operation(self):
        self.provider.void("p-1")
        self.assertEqual(self.http.calls[-1][:2], ("POST", "https://provider.invalid/v3/payments/p-1/void"))


class MercadoPagoAdapterTests(unittest.TestCase):
    def setUp(self):
        self.http = FakeHTTP()
        self.provider = MercadoPagoProvider(access_token="token", base_url="https://provider.invalid", http=self.http)

    def test_create_requires_idempotency_key(self):
        with self.assertRaisesRegex(ValueError, "idempotency_key"):
            self.provider.create({"transaction_amount": 1000})

    def test_create_sends_bearer_and_idempotency_headers(self):
        self.provider.create({"transaction_amount": 1000}, idempotency_key="key-1")
        method, url, kwargs = self.http.calls[-1]
        self.assertEqual((method, url), ("POST", "https://provider.invalid/v1/payments"))
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer token")
        self.assertEqual(kwargs["headers"]["X-Idempotency-Key"], "key-1")

    def test_full_refund_uses_empty_payload(self):
        self.provider.refund("p-1", idempotency_key="refund-1")
        self.assertEqual(self.http.calls[-1][2]["payload"], {})


class WebpayAdapterTests(unittest.TestCase):
    def setUp(self):
        self.http = FakeHTTP()
        self.provider = WebpayPlusProvider(
            commerce_code="commerce",
            api_key="secret",
            base_url="https://provider.invalid/api/webpay/v1.2",
            http=self.http,
        )

    def test_commit_and_status_use_transaction_token(self):
        self.provider.commit("token-1")
        self.provider.get("token-1")
        self.assertEqual(self.http.calls[0][:2], ("PUT", "https://provider.invalid/api/webpay/v1.2/transactions/token-1"))
        self.assertEqual(self.http.calls[1][:2], ("GET", "https://provider.invalid/api/webpay/v1.2/transactions/token-1"))

    def test_headers_use_configured_credentials(self):
        self.assertEqual(
            self.provider.headers,
            {"Tbk-Api-Key-Id": "commerce", "Tbk-Api-Key-Secret": "secret"},
        )


class ConfigurationTests(unittest.TestCase):
    @patch.dict("os.environ", {}, clear=True)
    def test_khipu_requires_credentials(self):
        with self.assertRaises(RuntimeError):
            KhipuProvider(api_key="", base_url="")

    @patch.dict("os.environ", {}, clear=True)
    def test_mercado_pago_requires_token(self):
        with self.assertRaises(RuntimeError):
            MercadoPagoProvider(access_token="")


if __name__ == "__main__":
    unittest.main()
