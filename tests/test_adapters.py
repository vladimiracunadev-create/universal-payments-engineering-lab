import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from payments_lab.adapters.khipu import KhipuProvider
from payments_lab.adapters.mercadopago import MercadoPagoProvider
from payments_lab.adapters.transbank import WebpayPlusProvider
from payments_lab.adapters.transbank_oneclick import OneclickMallProvider


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

    def test_create_uses_v3_contract(self):
        self.provider.create(
            {"amount": "1000", "currency": "CLP", "subject": "Order 1", "return_url": "https://merchant.test/return"}
        )
        method, url, kwargs = self.http.calls[-1]
        self.assertEqual((method, url), ("POST", "https://provider.invalid/v3/payments"))
        self.assertEqual(kwargs["headers"], {"x-api-key": "secret"})

    def test_create_rejects_missing_contract_fields_and_floats(self):
        with self.assertRaisesRegex(ValueError, "missing required"):
            self.provider.create({"amount": 1000})
        with self.assertRaisesRegex(ValueError, "never float"):
            self.provider.create({"amount": 10.1, "currency": "CLP", "subject": "x"})

    def test_path_identifier_cannot_inject_segments(self):
        with self.assertRaises(ValueError):
            self.provider.get("../../secrets")


class MercadoPagoAdapterTests(unittest.TestCase):
    def setUp(self):
        self.http = FakeHTTP()
        self.provider = MercadoPagoProvider(access_token="token", base_url="https://provider.invalid", http=self.http)
        self.payload = {
            "transaction_amount": "1000",
            "payment_method_id": "visa",
            "payer": {"email": "payer@example.test"},
        }

    def test_create_requires_idempotency_key(self):
        with self.assertRaisesRegex(ValueError, "idempotency_key"):
            self.provider.create(self.payload)

    def test_create_sends_bearer_and_idempotency_headers(self):
        self.provider.create(self.payload, idempotency_key="key-1")
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

    def test_create_validates_and_serializes_contract(self):
        self.provider.create(
            {
                "buy_order": "order-1",
                "session_id": "session-1",
                "amount": 1000,
                "return_url": "https://merchant.test/return",
            }
        )
        self.assertEqual(self.http.calls[-1][:2], ("POST", "https://provider.invalid/api/webpay/v1.2/transactions"))

    def test_commit_and_status_use_transaction_token(self):
        self.provider.commit("token-1")
        self.provider.get("token-1")
        self.assertEqual(
            self.http.calls[0][:2], ("PUT", "https://provider.invalid/api/webpay/v1.2/transactions/token-1")
        )
        self.assertEqual(
            self.http.calls[1][:2], ("GET", "https://provider.invalid/api/webpay/v1.2/transactions/token-1")
        )


class OneclickAdapterTests(unittest.TestCase):
    def setUp(self):
        self.http = FakeHTTP()
        self.provider = OneclickMallProvider(
            commerce_code="mall",
            api_key="secret",
            base_url="https://provider.invalid/api/oneclick/v1.2",
            http=self.http,
        )

    def test_enrollment_lifecycle_uses_official_endpoints(self):
        self.provider.start_enrollment(
            username="user-1", email="user@example.test", response_url="https://merchant.test/oneclick/return"
        )
        self.provider.finish_enrollment("token-1")
        self.provider.delete_enrollment(tbk_user="tbk-user-1", username="user-1")
        self.assertEqual([call[0] for call in self.http.calls], ["POST", "PUT", "DELETE"])
        self.assertTrue(self.http.calls[0][1].endswith("/inscriptions"))
        self.assertTrue(self.http.calls[1][1].endswith("/inscriptions/token-1"))

    def test_authorize_requires_nonempty_details(self):
        with self.assertRaisesRegex(ValueError, "details"):
            self.provider.authorize({"username": "u", "tbk_user": "t", "buy_order": "o", "details": []})


class ConfigurationTests(unittest.TestCase):
    @patch.dict("os.environ", {}, clear=True)
    def test_credentials_are_required(self):
        with self.assertRaises(RuntimeError):
            KhipuProvider(api_key="", base_url="")
        with self.assertRaises(RuntimeError):
            MercadoPagoProvider(access_token="")
        with self.assertRaises(RuntimeError):
            OneclickMallProvider(commerce_code="", api_key="", base_url="")

    def test_plain_http_provider_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "HTTPS"):
            MercadoPagoProvider(access_token="token", base_url="http://provider.invalid")


if __name__ == "__main__":
    unittest.main()
