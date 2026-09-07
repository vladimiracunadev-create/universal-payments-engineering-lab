import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from payments_lab.core.idempotency import IdempotencyConflict, IdempotencyStore
from payments_lab.core.ledger import Entry, Ledger
from payments_lab.core.reconciliation import PaymentRecord, reconcile
from payments_lab.core.states import PaymentState, can_transition, transition


class StateTests(unittest.TestCase):
    def test_happy_path_transitions(self):
        self.assertEqual(transition(PaymentState.PROCESSING, PaymentState.AUTHORIZED), PaymentState.AUTHORIZED)
        self.assertTrue(can_transition(PaymentState.AUTHORIZED, PaymentState.CAPTURED))
        self.assertTrue(can_transition(PaymentState.SETTLED, PaymentState.RECONCILED))

    def test_impossible_transition_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Invalid payment transition"):
            transition(PaymentState.CREATED, PaymentState.REFUNDED)

    def test_unknown_can_recover_to_definitive_state(self):
        for target in (PaymentState.AUTHORIZED, PaymentState.CAPTURED, PaymentState.DECLINED, PaymentState.FAILED):
            with self.subTest(target=target):
                self.assertTrue(can_transition(PaymentState.UNKNOWN, target))


class LedgerTests(unittest.TestCase):
    def test_balanced_journal_is_appended(self):
        ledger = Ledger()
        journal = ledger.post(
            "p1",
            [Entry("customer", Decimal("-1000"), "CLP"), Entry("merchant", Decimal("1000"), "CLP")],
        )
        self.assertEqual(journal.reference, "p1")
        self.assertEqual(ledger.journals, (journal,))

    def test_unbalanced_journal_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unbalanced"):
            Ledger().post("bad", [Entry("a", Decimal("-10"), "CLP"), Entry("b", Decimal("9"), "CLP")])

    def test_single_entry_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "at least two"):
            Ledger().post("bad", [Entry("a", Decimal("0"), "CLP")])

    def test_mixed_currency_journal_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "single currency"):
            Ledger().post("bad", [Entry("a", Decimal("-1"), "CLP"), Entry("b", Decimal("1"), "USD")])


class IdempotencyTests(unittest.TestCase):
    def test_same_key_and_payload_is_idempotent(self):
        store = IdempotencyStore()
        first = store.reserve("x", {"amount": 100})
        self.assertEqual(store.reserve("x", {"amount": 100}), first)

    def test_same_key_with_different_payload_conflicts(self):
        store = IdempotencyStore()
        store.reserve("x", {"amount": 100})
        with self.assertRaises(IdempotencyConflict):
            store.reserve("x", {"amount": 200})

    def test_fingerprint_ignores_object_key_order(self):
        self.assertEqual(
            IdempotencyStore.fingerprint({"amount": 100, "currency": "CLP"}),
            IdempotencyStore.fingerprint({"currency": "CLP", "amount": 100}),
        )


class ReconciliationTests(unittest.TestCase):
    def test_reference_and_amount_differences(self):
        local = [PaymentRecord("A", Decimal("100"), "CLP"), PaymentRecord("B", Decimal("50"), "CLP")]
        remote = [PaymentRecord("A", Decimal("101"), "CLP"), PaymentRecord("C", Decimal("50"), "CLP")]
        self.assertEqual(
            {item.kind for item in reconcile(local, remote)}, {"AMOUNT_MISMATCH", "LOCAL_ONLY", "REMOTE_ONLY"}
        )

    def test_currency_difference(self):
        local = [PaymentRecord("A", Decimal("100"), "CLP")]
        remote = [PaymentRecord("A", Decimal("100"), "USD")]
        differences = reconcile(local, remote)
        self.assertEqual([(item.kind, item.reference) for item in differences], [("CURRENCY_MISMATCH", "A")])

    def test_matching_records_have_no_difference(self):
        record = PaymentRecord("A", Decimal("100"), "CLP")
        self.assertEqual(reconcile([record], [record]), [])


if __name__ == "__main__":
    unittest.main()
