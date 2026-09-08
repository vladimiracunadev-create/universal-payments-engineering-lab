import os
import sys
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from payments_lab.catalog import enriched_catalog, load_catalog
from payments_lab.demo import SCENARIOS, run_demo
from payments_lab.doctor import diagnose


class CatalogTests(unittest.TestCase):
    def test_every_family_has_a_plain_language_guide(self):
        catalog = enriched_catalog()
        self.assertEqual(len(catalog), 28)
        self.assertEqual({item["id"] for item in catalog}, {item["id"] for item in load_catalog()})
        for family in catalog:
            with self.subTest(rail=family["id"]):
                self.assertTrue(family["title"])
                self.assertTrue(family["solves"])
                self.assertTrue(family["demo_focus"])


class DemoJourneyTests(unittest.TestCase):
    def test_every_family_runs_every_demo_scenario(self):
        for family in enriched_catalog():
            for scenario in SCENARIOS:
                with self.subTest(rail=family["id"], scenario=scenario):
                    run = run_demo(family["id"], scenario=scenario)
                    self.assertEqual(run["mode"], "DEMO")
                    self.assertFalse(run["moves_money"])
                    self.assertGreaterEqual(len(run["steps"]), 6)
                    total = sum(Decimal(entry["amount"]) for entry in run["journal"]["entries"])
                    self.assertEqual(total, Decimal("0"))

    def test_demo_reference_is_deterministic(self):
        first = run_demo("chile-webpay", amount="1000", currency="clp")
        second = run_demo("chile-webpay", amount="1000", currency="CLP")
        self.assertEqual(first["reference"], second["reference"])

    def test_timeout_is_recovered_without_a_second_effect(self):
        run = run_demo("instant-payments", scenario="timeout-recovered")
        states = [step["state"] for step in run["steps"]]
        self.assertIn("UNKNOWN", states)
        phases = [step["phase"] for step in run["steps"]]
        self.assertEqual(phases.index("Recuperación"), phases.index("Timeout") + 1)
        self.assertEqual([step["number"] for step in run["steps"]], list(range(1, len(run["steps"]) + 1)))
        self.assertEqual(len(run["journal"]["entries"]), 2)
        self.assertEqual(run["final_state"], "RECONCILED")

    def test_duplicate_event_is_counted_as_ignored(self):
        run = run_demo("chile-khipu", scenario="duplicate-event")
        self.assertEqual(run["event_delivery"], {"event_id": f"evt-{run['reference']}", "accepted": 1, "ignored": 1})

    def test_reconciliation_difference_stays_visible(self):
        run = run_demo("mercado-pago", scenario="reconciliation-mismatch")
        self.assertEqual(run["final_state"], "RECONCILIATION_EXCEPTION")
        self.assertEqual(run["differences"][0]["kind"], "AMOUNT_MISMATCH")

    def test_invalid_inputs_are_rejected(self):
        with self.assertRaisesRegex(KeyError, "unknown payment family"):
            run_demo("not-a-rail")
        with self.assertRaisesRegex(ValueError, "unknown demo scenario"):
            run_demo("cash", scenario="magic")
        with self.assertRaisesRegex(ValueError, "positive"):
            run_demo("cash", amount="-1")


class DoctorTests(unittest.TestCase):
    @patch.dict(os.environ, {}, clear=True)
    def test_demo_is_ready_without_credentials(self):
        report = diagnose()
        self.assertEqual(report["status"], "ready")
        self.assertEqual(report["demo"]["families"], 28)
        self.assertFalse(report["demo"]["moves_money"])
        self.assertFalse(report["safety"]["automatic_live_fallback"])
        self.assertTrue(all(not provider["configured"] for provider in report["providers"]))


if __name__ == "__main__":
    unittest.main()
