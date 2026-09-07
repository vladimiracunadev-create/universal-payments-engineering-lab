import base64
import hashlib
import hmac
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from payments_lab.core.http import InvalidProviderResponse, JsonHTTPClient, ProviderHTTPError, require_https_base_url
from payments_lab.core.webhooks import InvalidWebhookSignature, verify_khipu_signature, verify_mercadopago_signature


class WebhookTests(unittest.TestCase):
    def test_khipu_signature_authenticates_raw_body(self):
        body, secret, timestamp = b'{"payment_id":"p1"}', "secret", 1_700_000_000_000
        digest = hmac.new(secret.encode(), str(timestamp).encode() + b"." + body, hashlib.sha256).digest()
        header = f"t={timestamp},s={base64.b64encode(digest).decode()}"
        verify_khipu_signature(body, header, secret, now=timestamp / 1000)
        with self.assertRaises(InvalidWebhookSignature):
            verify_khipu_signature(body + b" ", header, secret, now=timestamp / 1000)

    def test_mercadopago_signature_and_replay_window(self):
        timestamp, secret = 1_700_000_000_000, "secret"
        manifest = f"id:123;request-id:req-1;ts:{timestamp};"
        digest = hmac.new(secret.encode(), manifest.encode(), hashlib.sha256).hexdigest()
        header = f"ts={timestamp},v1={digest}"
        verify_mercadopago_signature(
            data_id="123", request_id="req-1", signature_header=header, secret=secret, now=timestamp / 1000
        )
        with self.assertRaisesRegex(InvalidWebhookSignature, "replay window"):
            verify_mercadopago_signature(
                data_id="123", request_id="req-1", signature_header=header, secret=secret, now=timestamp / 1000 + 301
            )


class TransportTests(unittest.TestCase):
    def test_https_and_embedded_credentials_are_enforced(self):
        for url in ("http://provider.test", "https://user:secret@provider.test"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                require_https_base_url(url)

    def test_json_root_must_be_object(self):
        with self.assertRaises(InvalidProviderResponse):
            JsonHTTPClient._decode(b"[]")

    def test_http_errors_classify_retryability(self):
        self.assertTrue(ProviderHTTPError(503, "down").retryable)
        self.assertFalse(ProviderHTTPError(422, "invalid").retryable)


if __name__ == "__main__":
    unittest.main()
