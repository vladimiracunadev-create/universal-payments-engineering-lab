import hashlib
import hmac
import sys
import threading
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from payments_lab.core.webhooks import InvalidWebhookSignature
from payments_lab.virtual_economy import (
    GAME_SCENARIOS,
    Entitlement,
    FulfillmentState,
    GamePaymentState,
    VirtualEconomyEngine,
    WalletTransaction,
    run_virtual_economy_demo,
    sign_demo_webhook,
    verify_demo_webhook,
)


class VirtualEconomyJourneyTests(unittest.TestCase):
    def test_every_game_scenario_is_local_and_auditable(self):
        for scenario in GAME_SCENARIOS:
            with self.subTest(scenario=scenario):
                run = run_virtual_economy_demo(scenario)
                self.assertEqual(run["mode"], "DEMO")
                self.assertFalse(run["moves_money"])
                self.assertEqual(run["order"]["currency"], "CLP")
                self.assertEqual(run["wallet"]["currency"], "GEM")
                self.assertTrue(run["timeline"])
                self.assertTrue(run["correlation_id"])

    def test_ten_duplicate_webhooks_credit_exactly_once(self):
        run = run_virtual_economy_demo("game-currency-duplicate-webhook")
        loads = [item for item in run["wallet"]["transaction_history"] if item["kind"] == "LOAD"]
        self.assertEqual(len(loads), 1)
        self.assertEqual(loads[0]["amount"], "1000")
        self.assertEqual(run["webhook_delivery"]["deduplicated"], 9)

    def test_duplicate_client_retry_returns_same_order_and_attempt(self):
        engine = VirtualEconomyEngine()
        first = engine.create_currency_order("IDEM-CLIENT-RETRY")
        second = engine.create_currency_order("IDEM-CLIENT-RETRY")
        self.assertIs(first, second)
        self.assertEqual(len(engine.orders), 1)
        self.assertEqual(len(engine.attempts), 1)

    def test_timeout_is_unknown_until_recovery_without_second_charge(self):
        engine = VirtualEconomyEngine()
        order = engine.create_currency_order()
        attempt = engine.submit_payment(order, response_lost=True)
        self.assertEqual(attempt.state, GamePaymentState.UNKNOWN)
        engine.recover_unknown(attempt.provider_payment_id)
        self.assertEqual(attempt.state, GamePaymentState.PAID)
        self.assertEqual(len(engine.external_ledger.journals), 1)

    def test_paid_but_credit_failed_is_detected_and_recovered(self):
        run = run_virtual_economy_demo("game-currency-entitlement-failure")
        self.assertEqual(run["before_recovery"]["differences"][0]["kind"], "MISSING_CREDIT")
        self.assertEqual(run["reconciliation"]["status"], "RECONCILED")
        self.assertEqual(sum(1 for tx in run["wallet"]["transaction_history"] if tx["kind"] == "LOAD"), 1)

    def test_refund_and_chargeback_are_compensating_events(self):
        refunded = run_virtual_economy_demo("game-currency-refund")
        charged_back = run_virtual_economy_demo("game-currency-chargeback")
        self.assertEqual(refunded["payment_attempt"]["state"], "REFUNDED")
        self.assertEqual(charged_back["payment_attempt"]["state"], "CHARGEDBACK")
        self.assertEqual(refunded["wallet"]["balance"], "-900")
        self.assertEqual(charged_back["wallet"]["balance"], "-900")
        self.assertTrue(any(tx["kind"] == "REFUND" for tx in refunded["wallet"]["transaction_history"]))
        self.assertTrue(any(tx["kind"] == "CHARGEBACK" for tx in charged_back["wallet"]["transaction_history"]))

    def test_refund_before_payment_success_does_not_regress_state(self):
        engine = VirtualEconomyEngine()
        order = engine.create_currency_order()
        attempt = engine.submit_payment(order)
        engine.credit_wallet(attempt.provider_payment_id)
        engine.apply_refund(attempt.provider_payment_id)
        changed = engine.apply_late_payment_success(attempt.provider_payment_id, "EVT-LATE-SUCCESS")
        self.assertFalse(changed)
        self.assertEqual(engine.provider_transactions[attempt.provider_payment_id].state, GamePaymentState.REFUNDED)
        self.assertEqual(sum(tx.amount for tx in engine.wallet_transactions), Decimal("0"))

    def test_lost_delivery_response_returns_same_logical_result(self):
        run = run_virtual_economy_demo("game-currency-response-lost")
        self.assertTrue(run["client_retry"]["same_order"])
        self.assertTrue(run["client_retry"]["same_payment_attempt"])
        self.assertEqual(run["client_retry"]["wallet_loads"], 1)
        self.assertEqual(run["client_retry"]["entitlements"], 1)

    def test_process_crash_recovers_without_a_second_charge(self):
        run = run_virtual_economy_demo("game-currency-crash-recovery")
        self.assertTrue(run["recovery"]["process_restarted"])
        self.assertFalse(run["recovery"]["new_charge_created"])
        self.assertEqual(run["recovery"]["payment_attempts"], 1)
        self.assertEqual(run["client_retry"]["wallet_loads"], 1)

    def test_restore_purchase_reuses_entitlement_and_payment(self):
        run = run_virtual_economy_demo("game-restore-purchase")
        self.assertEqual(run["recovery"]["payment_attempts"], 1)
        self.assertEqual(run["client_retry"]["entitlements"], 1)
        self.assertTrue(any(event["action"] == "RESTORE_PURCHASE" for event in run["timeline"]))


class VirtualEconomySecurityTests(unittest.TestCase):
    def test_invalid_signature_is_rejected(self):
        body = b'{"event_id":"EVT-1"}'
        with self.assertRaisesRegex(InvalidWebhookSignature, "invalid"):
            verify_demo_webhook(
                body,
                timestamp_ms=1_700_000_000_000,
                signature="not-a-signature",
                secret="fictional-demo-secret",
                now=1_700_000_000,
            )

    def test_stale_webhook_is_rejected(self):
        body = b'{"event_id":"EVT-1"}'
        timestamp = 1_700_000_000_000
        signature = sign_demo_webhook(body, timestamp, "fictional-demo-secret")
        with self.assertRaisesRegex(InvalidWebhookSignature, "replay window"):
            verify_demo_webhook(
                body,
                timestamp_ms=timestamp,
                signature=signature,
                secret="fictional-demo-secret",
                now=1_700_000_301,
            )

    def test_valid_signature_uses_constant_contract(self):
        body = b'{"event_id":"EVT-1"}'
        timestamp = 1_700_000_000_000
        secret = "fictional-demo-secret"
        expected = hmac.new(secret.encode(), str(timestamp).encode() + b"." + body, hashlib.sha256).hexdigest()
        self.assertEqual(sign_demo_webhook(body, timestamp, secret), expected)
        verify_demo_webhook(body, timestamp_ms=timestamp, signature=expected, secret=secret, now=timestamp / 1000)


class VirtualEconomyConcurrencyTests(unittest.TestCase):
    def test_two_simultaneous_spends_cannot_overdraw(self):
        engine = VirtualEconomyEngine()
        engine.admin_adjust(Decimal("500"), operator="DEMO-OPS-01", reason="Concurrency fixture")
        barrier = threading.Barrier(3)
        results = []

        def spend(key):
            barrier.wait()
            results.append(engine.spend_gems(Decimal("400"), f"ITEM-{key}", key))

        workers = [threading.Thread(target=spend, args=(f"REQ-{index}",)) for index in range(2)]
        for worker in workers:
            worker.start()
        barrier.wait()
        for worker in workers:
            worker.join(timeout=2)
        self.assertEqual(sorted(results), [False, True])
        self.assertEqual(engine.wallet.balance, Decimal("100"))

    def test_entitlement_and_inventory_are_granted_once(self):
        engine = VirtualEconomyEngine()
        engine.admin_adjust(Decimal("1000"), operator="DEMO-OPS-01", reason="Idempotency fixture")
        self.assertTrue(engine.spend_gems(Decimal("300"), "SKIN_DRAGON", "IDEM-SKIN"))
        self.assertTrue(engine.spend_gems(Decimal("300"), "SKIN_DRAGON", "IDEM-SKIN"))
        self.assertEqual(len(engine.entitlements), 1)
        self.assertEqual(len(engine.inventory), 1)
        self.assertEqual(engine.wallet.balance, Decimal("700"))

    def test_admin_adjustment_requires_auditable_reason(self):
        engine = VirtualEconomyEngine()
        with self.assertRaisesRegex(ValueError, "operator and reason"):
            engine.admin_adjust(Decimal("500"), operator="", reason="")
        transaction = engine.admin_adjust(Decimal("500"), operator="DEMO-OPS-01", reason="Approved correction")
        self.assertEqual(transaction.kind, "ADMIN_ADJUSTMENT")
        self.assertEqual(engine.wallet.version, 1)

    def test_failed_spend_rolls_back_every_domain(self):
        engine = VirtualEconomyEngine()
        engine.admin_adjust(Decimal("100"), operator="DEMO-OPS-01", reason="Rollback fixture")
        journals_before = len(engine.virtual_ledger.journals)
        self.assertFalse(engine.spend_gems(Decimal("300"), "SKIN_DRAGON", "IDEM-ROLLBACK"))
        self.assertEqual(engine.wallet.balance, Decimal("100"))
        self.assertEqual(len(engine.virtual_ledger.journals), journals_before)
        self.assertFalse(engine.entitlements)
        self.assertFalse(engine.inventory)


class VirtualEconomyReconciliationTests(unittest.TestCase):
    def test_amount_and_currency_mismatch_are_classified(self):
        engine = VirtualEconomyEngine()
        order = engine.create_currency_order()
        attempt = engine.submit_payment(order)
        provider = engine.provider_transactions[attempt.provider_payment_id]
        provider.amount = Decimal("6000")
        provider.currency = "USD"
        kinds = {item["kind"] for item in engine.reconcile().differences}
        self.assertTrue({"AMOUNT_MISMATCH", "CURRENCY_MISMATCH", "MISSING_CREDIT"}.issubset(kinds))

    def test_orphan_wallet_transaction_is_detected(self):
        engine = VirtualEconomyEngine()
        engine.wallet_transactions.append(
            WalletTransaction(
                "WTX-ORPHAN",
                engine.wallet.wallet_id,
                Decimal("1000"),
                "GEM",
                "LOAD",
                "PAY-MISSING",
                engine.correlation_id,
                "2026-01-15T12:00:00+00:00",
            )
        )
        kinds = {item["kind"] for item in engine.reconcile().differences}
        self.assertIn("ORPHAN_TRANSACTION", kinds)

    def test_orphan_entitlement_and_inventory_mismatch_are_detected(self):
        engine = VirtualEconomyEngine()
        engine.entitlements["ENT-ORPHAN"] = Entitlement(
            "ENT-ORPHAN",
            engine.player_id,
            "DLC_02",
            "ORD-MISSING",
            FulfillmentState.ENTITLEMENT_GRANTED,
            "2026-01-15T12:00:00+00:00",
        )
        kinds = {item["kind"] for item in engine.reconcile().differences}
        self.assertTrue({"ORPHAN_ENTITLEMENT", "INVENTORY_MISMATCH"}.issubset(kinds))


if __name__ == "__main__":
    unittest.main()
