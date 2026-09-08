import json
import sys
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from payments_lab.web import create_server


class LocalPortalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = create_server(port=0)
        cls.origin = f"http://127.0.0.1:{cls.server.server_port}"
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def get(self, path):
        with urllib.request.urlopen(self.origin + path, timeout=2) as response:
            return response, response.read()

    def test_home_and_health_are_served_with_security_headers(self):
        response, body = self.get("/")
        self.assertIn(b"PayLab", body)
        self.assertIn("Cómo implementar la modalidad".encode(), body)
        self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")
        response, body = self.get("/api/health")
        self.assertEqual(json.loads(body)["mode"], "DEMO")

    def test_catalog_exposes_all_guided_families(self):
        _, body = self.get("/api/catalog")
        families = json.loads(body)["families"]
        self.assertEqual(len(families), 28)
        self.assertTrue(all("solves" in family for family in families))
        self.assertTrue(all("playbook" in family for family in families))
        for family in families:
            guide = family["playbook"]
            self.assertIn("backend", guide["stack"])
            self.assertTrue(guide["implementation"])
            self.assertTrue(guide["testing"])
            self.assertTrue(guide["security"])
            self.assertTrue(guide["failures"])
            self.assertTrue(all(source["url"].startswith("https://") for source in guide["sources"]))

    def test_demo_endpoint_returns_observable_journey(self):
        request = urllib.request.Request(
            self.origin + "/api/demo/chile-webpay",
            data=json.dumps({"scenario": "duplicate-event", "amount": "2500", "currency": "CLP"}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=2) as response:
            run = json.load(response)
        self.assertEqual(response.status, 201)
        self.assertEqual(run["final_state"], "RECONCILED")
        self.assertTrue(any(step["phase"] == "Duplicado" for step in run["steps"]))

    def test_unknown_family_and_oversized_request_are_rejected(self):
        request = urllib.request.Request(
            self.origin + "/api/demo/unknown",
            data=b"{}",
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with self.assertRaises(urllib.error.HTTPError) as unknown:
            urllib.request.urlopen(request, timeout=2)
        self.assertEqual(unknown.exception.code, 404)

        request = urllib.request.Request(
            self.origin + "/api/demo/cash",
            data=b"x" * 16_385,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with self.assertRaises(urllib.error.HTTPError) as oversized:
            urllib.request.urlopen(request, timeout=2)
        self.assertEqual(oversized.exception.code, 413)


if __name__ == "__main__":
    unittest.main()
