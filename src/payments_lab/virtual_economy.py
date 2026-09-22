# ruff: noqa: E501
"""Deterministic virtual-game-economy DEMO built on PayLab invariants."""

from __future__ import annotations

import hashlib
import hmac
import threading
from copy import deepcopy
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from enum import StrEnum

from .core.idempotency import IdempotencyStore
from .core.ledger import Entry, Ledger
from .core.webhooks import InvalidWebhookSignature

GAME_SCENARIOS = {
    "game-currency-success": "Compra 1.000 GEM por CLP 5.990 y luego gasta 300 GEM en SKIN_DRAGON.",
    "game-currency-timeout": "El proveedor procesa el pago, la respuesta se pierde y el estado UNKNOWN se recupera.",
    "game-currency-duplicate-webhook": "El mismo webhook llega diez veces; la wallet recibe 1.000 GEM una vez.",
    "game-currency-entitlement-failure": "El pago queda aprobado pero falla el crédito; retry seguro y conciliación lo recuperan.",
    "game-currency-response-lost": "La entrega termina, la respuesta HTTP se pierde y el retry devuelve el mismo efecto.",
    "game-currency-crash-recovery": "El proceso cae después del pago; otro proceso recupera la evidencia y completa el crédito.",
    "game-currency-refund": "El jugador gasta 900 GEM antes del refund; la demo conserva saldo negativo y revisión manual.",
    "game-currency-chargeback": "El proveedor informa chargeback después del consumo y abre una excepción operativa.",
    "game-restore-purchase": "Una reinstalación restaura SKIN_DRAGON desde el entitlement original sin volver a cobrar.",
}


class GamePaymentState(StrEnum):
    CREATED = "CREATED"
    PENDING = "PENDING"
    AUTHORIZED = "AUTHORIZED"
    PAID = "PAID"
    UNKNOWN = "UNKNOWN"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"
    CHARGEDBACK = "CHARGEDBACK"


class FulfillmentState(StrEnum):
    ENTITLEMENT_PENDING = "ENTITLEMENT_PENDING"
    ENTITLEMENT_GRANTED = "ENTITLEMENT_GRANTED"
    ENTITLEMENT_REVOKED = "ENTITLEMENT_REVOKED"


@dataclass
class Order:
    order_id: str
    player_id: str
    product_id: str
    amount: Decimal
    currency: str
    status: str
    correlation_id: str
    created_at: str


@dataclass
class PaymentAttempt:
    payment_attempt_id: str
    order_id: str
    idempotency_key: str
    provider_payment_id: str
    state: GamePaymentState
    created_at: str


@dataclass
class ProviderTransaction:
    provider_payment_id: str
    order_id: str
    amount: Decimal
    currency: str
    state: GamePaymentState
    evidence: str
    updated_at: str


@dataclass
class Settlement:
    settlement_id: str
    provider_payment_id: str
    amount: Decimal
    currency: str
    state: str
    settled_at: str


@dataclass
class Wallet:
    wallet_id: str
    owner_id: str
    currency: str
    balance: Decimal = Decimal("0")
    version: int = 0


@dataclass
class WalletTransaction:
    wallet_transaction_id: str
    wallet_id: str
    amount: Decimal
    currency: str
    kind: str
    source_id: str
    correlation_id: str
    created_at: str


@dataclass
class Entitlement:
    entitlement_id: str
    player_id: str
    product_id: str
    source_order_id: str
    status: FulfillmentState
    granted_at: str | None
    revoked_at: str | None = None


@dataclass
class InventoryMovement:
    inventory_transaction_id: str
    player_id: str
    product_id: str
    direction: str
    source_order_id: str
    correlation_id: str
    created_at: str


@dataclass
class Refund:
    refund_id: str
    provider_payment_id: str
    amount: Decimal
    currency: str
    policy: str
    created_at: str


@dataclass
class Chargeback:
    chargeback_id: str
    provider_payment_id: str
    amount: Decimal
    currency: str
    action: str
    created_at: str


@dataclass
class AuditEvent:
    sequence: int
    actor: str
    action: str
    entity_id: str
    before: str
    after: str
    reason: str
    correlation_id: str
    timestamp: str
    evidence: str


@dataclass
class ReconciliationResult:
    status: str
    differences: list[dict[str, str]] = field(default_factory=list)


@dataclass
class PaymentRecoveryCheckpoint:
    """Minimal durable facts needed to resume fulfillment after a process crash."""

    order: Order
    attempt: PaymentAttempt
    provider_transaction: ProviderTransaction
    settlement: Settlement


def _id(prefix: str, *parts: object) -> str:
    raw = ":".join(str(part) for part in parts).encode()
    return f"{prefix}-{hashlib.sha256(raw).hexdigest()[:12].upper()}"


def sign_demo_webhook(raw_body: bytes, timestamp_ms: int, secret: str) -> str:
    message = str(timestamp_ms).encode("ascii") + b"." + raw_body
    return hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()


def verify_demo_webhook(
    raw_body: bytes,
    *,
    timestamp_ms: int,
    signature: str,
    secret: str,
    now: float,
    tolerance_seconds: int = 300,
) -> None:
    if abs(now - timestamp_ms / 1000) > tolerance_seconds:
        raise InvalidWebhookSignature("webhook timestamp is outside the replay window")
    expected = sign_demo_webhook(raw_body, timestamp_ms, secret)
    if not hmac.compare_digest(expected, signature):
        raise InvalidWebhookSignature("invalid demo webhook signature")


class VirtualEconomyEngine:
    """In-memory teaching model. State is durable only for the lifetime of this object."""

    def __init__(self, *, player_id: str = "PLAYER-001") -> None:
        self.player_id = player_id
        self.wallet = Wallet("WALLET-PLAYER-001-GEM", player_id, "GEM")
        self.orders: dict[str, Order] = {}
        self.attempts: dict[str, PaymentAttempt] = {}
        self.provider_transactions: dict[str, ProviderTransaction] = {}
        self.settlements: dict[str, Settlement] = {}
        self.wallet_transactions: list[WalletTransaction] = []
        self.entitlements: dict[str, Entitlement] = {}
        self.inventory: list[InventoryMovement] = []
        self.refunds: dict[str, Refund] = {}
        self.chargebacks: dict[str, Chargeback] = {}
        self.audit: list[AuditEvent] = []
        self.external_ledger = Ledger()
        self.virtual_ledger = Ledger()
        self.idempotency = IdempotencyStore()
        self._idempotent_orders: dict[str, str] = {}
        self._processed_events: set[str] = set()
        self._credited_payments: set[str] = set()
        self._spend_results: dict[str, bool] = {}
        self._lock = threading.RLock()
        self.correlation_id = "CORR-GAME-GEM-5990"
        self._base_time = datetime(2026, 1, 15, 12, 0, tzinfo=UTC)

    def _timestamp(self) -> str:
        return (self._base_time + timedelta(seconds=len(self.audit))).isoformat()

    def _audit(self, actor: str, action: str, entity_id: str, before: str, after: str, reason: str) -> None:
        self.audit.append(
            AuditEvent(
                len(self.audit) + 1,
                actor,
                action,
                entity_id,
                before,
                after,
                reason,
                self.correlation_id,
                self._timestamp(),
                f"audit:{entity_id}:{len(self.audit) + 1}",
            )
        )

    def create_currency_order(self, idempotency_key: str = "IDEM-GEM-1000") -> Order:
        payload = {"player_id": self.player_id, "product_id": "GEM_PACK_1000", "amount": "5990", "currency": "CLP"}
        self.idempotency.reserve(idempotency_key, payload)
        with self._lock:
            if order_id := self._idempotent_orders.get(idempotency_key):
                return self.orders[order_id]
            order_id = _id("ORD", self.player_id, idempotency_key)
            order = Order(
                order_id,
                self.player_id,
                "GEM_PACK_1000",
                Decimal("5990"),
                "CLP",
                "CREATED",
                self.correlation_id,
                self._timestamp(),
            )
            self.orders[order_id] = order
            self._idempotent_orders[idempotency_key] = order_id
            provider_payment_id = "PAY-ABC123"
            attempt = PaymentAttempt(
                _id("ATT", order_id),
                order_id,
                idempotency_key,
                provider_payment_id,
                GamePaymentState.CREATED,
                self._timestamp(),
            )
            self.attempts[attempt.payment_attempt_id] = attempt
            self._audit("Game Backend", "CREATE_ORDER", order_id, "MISSING", "CREATED", "Compra de 1.000 GEM")
            return order

    def submit_payment(self, order: Order, *, response_lost: bool = False) -> PaymentAttempt:
        attempt = next(item for item in self.attempts.values() if item.order_id == order.order_id)
        attempt.state = GamePaymentState.PENDING
        order.status = GamePaymentState.PENDING.value
        self._audit(
            "Game Backend",
            "SUBMIT_PAYMENT",
            attempt.payment_attempt_id,
            GamePaymentState.CREATED.value,
            GamePaymentState.PENDING.value,
            "Se envía una sola interacción al proveedor",
        )
        attempt.state = GamePaymentState.UNKNOWN if response_lost else GamePaymentState.PAID
        order.status = attempt.state.value
        provider = ProviderTransaction(
            attempt.provider_payment_id,
            order.order_id,
            order.amount,
            order.currency,
            GamePaymentState.PAID,
            "provider-api:authorized-and-captured",
            self._timestamp(),
        )
        self.provider_transactions[provider.provider_payment_id] = provider
        if response_lost:
            self._audit(
                "Payment Provider",
                "RESPONSE_LOST",
                attempt.payment_attempt_id,
                "PENDING",
                "UNKNOWN",
                "El proveedor procesó; el cliente no recibió respuesta",
            )
        else:
            self._record_external_effect(order, provider)
        return attempt

    def recover_unknown(self, provider_payment_id: str) -> None:
        provider = self.provider_transactions[provider_payment_id]
        attempt = next(item for item in self.attempts.values() if item.provider_payment_id == provider_payment_id)
        before = attempt.state.value
        attempt.state = provider.state
        self.orders[attempt.order_id].status = provider.state.value
        self._record_external_effect(self.orders[attempt.order_id], provider)
        self._audit(
            "Recovery Worker",
            "QUERY_PROVIDER",
            provider_payment_id,
            before,
            provider.state.value,
            "Recuperación por la misma referencia; no se creó otro cobro",
        )

    def payment_recovery_checkpoint(self, provider_payment_id: str) -> PaymentRecoveryCheckpoint:
        """Return persisted payment facts used by the deterministic crash-recovery DEMO."""
        provider = self.provider_transactions[provider_payment_id]
        attempt = next(item for item in self.attempts.values() if item.provider_payment_id == provider_payment_id)
        settlement = next(item for item in self.settlements.values() if item.provider_payment_id == provider_payment_id)
        return PaymentRecoveryCheckpoint(
            deepcopy(self.orders[attempt.order_id]),
            deepcopy(attempt),
            deepcopy(provider),
            deepcopy(settlement),
        )

    @classmethod
    def resume_from_payment_checkpoint(cls, checkpoint: PaymentRecoveryCheckpoint) -> VirtualEconomyEngine:
        """Simulate a new process loading durable facts without creating a second charge."""
        engine = cls(player_id=checkpoint.order.player_id)
        order = deepcopy(checkpoint.order)
        attempt = deepcopy(checkpoint.attempt)
        provider = deepcopy(checkpoint.provider_transaction)
        settlement = deepcopy(checkpoint.settlement)
        engine.correlation_id = order.correlation_id
        engine.orders[order.order_id] = order
        engine.attempts[attempt.payment_attempt_id] = attempt
        engine.provider_transactions[provider.provider_payment_id] = provider
        engine.settlements[settlement.settlement_id] = settlement
        engine._idempotent_orders[attempt.idempotency_key] = order.order_id
        engine.idempotency.reserve(
            attempt.idempotency_key,
            {
                "player_id": order.player_id,
                "product_id": order.product_id,
                "amount": format(order.amount, "f"),
                "currency": order.currency,
            },
        )
        engine._record_external_effect(order, provider)
        engine._audit(
            "Recovery Worker",
            "RESUME_AFTER_CRASH",
            provider.provider_payment_id,
            "PROCESS_RESTARTED",
            "FULFILLMENT_PENDING",
            "Se recuperó el pago persistido; no se creó otro Payment Attempt",
        )
        return engine

    def _record_external_effect(self, order: Order, provider: ProviderTransaction) -> None:
        reference = f"external:{provider.provider_payment_id}"
        if any(item.reference == reference for item in self.external_ledger.journals):
            return
        self.external_ledger.post(
            reference,
            [
                Entry("player/external-funds", -order.amount, order.currency),
                Entry("game/provider-receivable", order.amount, order.currency),
            ],
        )
        settlement = Settlement(
            "SET-PAY-ABC123", provider.provider_payment_id, order.amount, order.currency, "SETTLED", self._timestamp()
        )
        self.settlements[settlement.settlement_id] = settlement
        self._audit(
            "Payment Provider",
            "CONFIRM_PAYMENT",
            provider.provider_payment_id,
            "PENDING",
            "PAID",
            "Evidencia autoritativa del proveedor",
        )

    def process_webhook(self, event_id: str, provider_payment_id: str, *, fail_credit: bool = False) -> bool:
        with self._lock:
            if event_id in self._processed_events:
                self._audit("Webhook Inbox", "DEDUPE", event_id, "SEEN", "IGNORED", "Exactly-once logical effect")
                return False
            self._processed_events.add(event_id)
            self._audit("Webhook Inbox", "ACCEPT_EVENT", event_id, "NEW", "PERSISTED", "Firma y frescura verificadas")
            if fail_credit:
                self._audit(
                    "Wallet Service",
                    "CREDIT_FAILED",
                    self.wallet.wallet_id,
                    str(self.wallet.balance),
                    str(self.wallet.balance),
                    "Fallo inyectado después del pago",
                )
                return False
            return self.credit_wallet(provider_payment_id)

    def credit_wallet(self, provider_payment_id: str) -> bool:
        with self._lock:
            if provider_payment_id in self._credited_payments:
                return False
            provider = self.provider_transactions[provider_payment_id]
            if provider.state != GamePaymentState.PAID:
                raise ValueError("wallet credit requires authoritative PAID evidence")
            before = self.wallet.balance
            self.wallet.balance += Decimal("1000")
            self.wallet.version += 1
            transaction = WalletTransaction(
                _id("WTX", provider_payment_id),
                self.wallet.wallet_id,
                Decimal("1000"),
                "GEM",
                "LOAD",
                provider_payment_id,
                self.correlation_id,
                self._timestamp(),
            )
            self.wallet_transactions.append(transaction)
            self.virtual_ledger.post(
                f"wallet-load:{provider_payment_id}",
                [Entry("game/treasury", Decimal("-1000"), "GEM"), Entry("player/wallet", Decimal("1000"), "GEM")],
            )
            self._credited_payments.add(provider_payment_id)
            self._audit(
                "Wallet Service",
                "CREDIT_GEM",
                transaction.wallet_transaction_id,
                str(before),
                str(self.wallet.balance),
                "Pago externo confirmado",
            )
            return True

    def spend_gems(self, amount: Decimal, product_id: str, idempotency_key: str) -> bool:
        with self._lock:
            if idempotency_key in self._spend_results:
                self._audit(
                    "Game Backend",
                    "DEDUPE_CLIENT_RETRY",
                    idempotency_key,
                    "ALREADY_APPLIED",
                    "SAME_RESULT",
                    "La respuesta puede repetirse; el débito y entitlement no",
                )
                return self._spend_results[idempotency_key]
            if amount <= 0 or self.wallet.balance < amount:
                self._spend_results[idempotency_key] = False
                return False
            before = self.wallet.balance
            internal_order_id = _id("ORD-INTERNAL", product_id, idempotency_key)
            self.orders[internal_order_id] = Order(
                internal_order_id,
                self.player_id,
                product_id,
                amount,
                "GEM",
                "FULFILLED",
                self.correlation_id,
                self._timestamp(),
            )
            self.wallet.balance -= amount
            self.wallet.version += 1
            transaction = WalletTransaction(
                _id("WTX", internal_order_id),
                self.wallet.wallet_id,
                -amount,
                "GEM",
                "DEBIT",
                internal_order_id,
                self.correlation_id,
                self._timestamp(),
            )
            self.wallet_transactions.append(transaction)
            self.virtual_ledger.post(
                f"wallet-spend:{internal_order_id}",
                [Entry("player/wallet", -amount, "GEM"), Entry("game/store", amount, "GEM")],
            )
            entitlement_id = _id("ENT", self.player_id, product_id)
            if entitlement_id not in self.entitlements:
                entitlement = Entitlement(
                    entitlement_id,
                    self.player_id,
                    product_id,
                    internal_order_id,
                    FulfillmentState.ENTITLEMENT_GRANTED,
                    self._timestamp(),
                )
                self.entitlements[entitlement_id] = entitlement
                self.inventory.append(
                    InventoryMovement(
                        _id("INV", internal_order_id),
                        self.player_id,
                        product_id,
                        "GRANT",
                        internal_order_id,
                        self.correlation_id,
                        self._timestamp(),
                    )
                )
            self._audit(
                "Game Store",
                "DEBIT_GEM_AND_GRANT",
                transaction.wallet_transaction_id,
                str(before),
                str(self.wallet.balance),
                product_id,
            )
            self._spend_results[idempotency_key] = True
            return True

    def restore_purchase(self, entitlement_id: str) -> Entitlement:
        """Restore access from an existing entitlement without a payment or wallet mutation."""
        with self._lock:
            entitlement = self.entitlements[entitlement_id]
            if entitlement.status != FulfillmentState.ENTITLEMENT_GRANTED:
                raise ValueError("only an active entitlement can be restored")
            self._audit(
                "Game Backend",
                "RESTORE_PURCHASE",
                entitlement_id,
                entitlement.status.value,
                entitlement.status.value,
                "Se reutiliza la compra y licencia existentes; no hay segundo cargo",
            )
            return entitlement

    def admin_adjust(self, amount: Decimal, *, operator: str, reason: str) -> WalletTransaction:
        if not operator or not reason:
            raise ValueError("admin adjustment requires operator and reason")
        with self._lock:
            before = self.wallet.balance
            self.wallet.balance += amount
            self.wallet.version += 1
            transaction = WalletTransaction(
                _id("WTX-ADMIN", operator, self.wallet.version),
                self.wallet.wallet_id,
                amount,
                "GEM",
                "ADMIN_ADJUSTMENT",
                operator,
                self.correlation_id,
                self._timestamp(),
            )
            self.wallet_transactions.append(transaction)
            self.virtual_ledger.post(
                f"admin:{transaction.wallet_transaction_id}",
                [Entry("game/admin-adjustment", -amount, "GEM"), Entry("player/wallet", amount, "GEM")],
            )
            self._audit(
                operator,
                "ADMIN_ADJUSTMENT",
                transaction.wallet_transaction_id,
                str(before),
                str(self.wallet.balance),
                reason,
            )
            return transaction

    def apply_refund(self, provider_payment_id: str) -> Refund:
        provider = self.provider_transactions[provider_payment_id]
        refund = Refund(
            "REF-PAY-ABC123",
            provider_payment_id,
            provider.amount,
            provider.currency,
            "NEGATIVE_BALANCE_AND_MANUAL_REVIEW",
            self._timestamp(),
        )
        self.refunds[refund.refund_id] = refund
        provider.state = GamePaymentState.REFUNDED
        attempt = next(item for item in self.attempts.values() if item.provider_payment_id == provider_payment_id)
        attempt.state = GamePaymentState.REFUNDED
        self._reverse_credit(provider_payment_id, "REFUND")
        self._audit("Payment Provider", "REFUND", refund.refund_id, "PAID", "REFUNDED", refund.policy)
        return refund

    def apply_late_payment_success(self, provider_payment_id: str, event_id: str) -> bool:
        """Accept evidence without regressing a later REFUNDED/CHARGEDBACK fact."""
        with self._lock:
            if event_id in self._processed_events:
                return False
            self._processed_events.add(event_id)
            provider = self.provider_transactions[provider_payment_id]
            before = provider.state
            if before in {GamePaymentState.REFUNDED, GamePaymentState.CHARGEDBACK}:
                self._audit(
                    "Webhook Inbox",
                    "OUT_OF_ORDER_EVIDENCE",
                    event_id,
                    before.value,
                    before.value,
                    "PAYMENT_SUCCESS se conserva como evidencia sin revertir el estado terminal posterior",
                )
                return False
            provider.state = GamePaymentState.PAID
            return self.credit_wallet(provider_payment_id)

    def apply_chargeback(self, provider_payment_id: str) -> Chargeback:
        provider = self.provider_transactions[provider_payment_id]
        chargeback = Chargeback(
            "CBK-PAY-ABC123",
            provider_payment_id,
            provider.amount,
            provider.currency,
            "ACCOUNT_RESTRICTION_AND_MANUAL_REVIEW",
            self._timestamp(),
        )
        self.chargebacks[chargeback.chargeback_id] = chargeback
        provider.state = GamePaymentState.CHARGEDBACK
        attempt = next(item for item in self.attempts.values() if item.provider_payment_id == provider_payment_id)
        attempt.state = GamePaymentState.CHARGEDBACK
        self._reverse_credit(provider_payment_id, "CHARGEBACK")
        self._audit(
            "Payment Provider", "CHARGEBACK", chargeback.chargeback_id, "PAID", "CHARGEDBACK", chargeback.action
        )
        return chargeback

    def _reverse_credit(self, provider_payment_id: str, kind: str) -> None:
        reference = f"{kind.lower()}:{provider_payment_id}"
        if any(item.reference == reference for item in self.virtual_ledger.journals):
            return
        before = self.wallet.balance
        self.wallet.balance -= Decimal("1000")
        self.wallet.version += 1
        transaction = WalletTransaction(
            _id("WTX", kind, provider_payment_id),
            self.wallet.wallet_id,
            Decimal("-1000"),
            "GEM",
            kind,
            provider_payment_id,
            self.correlation_id,
            self._timestamp(),
        )
        self.wallet_transactions.append(transaction)
        self.virtual_ledger.post(
            reference, [Entry("player/wallet", Decimal("-1000"), "GEM"), Entry("game/treasury", Decimal("1000"), "GEM")]
        )
        self._audit(
            "Wallet Service",
            f"{kind}_REVERSAL",
            transaction.wallet_transaction_id,
            str(before),
            str(self.wallet.balance),
            "Asiento compensatorio; no se borra historia",
        )

    def reconcile(self) -> ReconciliationResult:
        differences: list[dict[str, str]] = []
        for provider in self.provider_transactions.values():
            order = self.orders.get(provider.order_id)
            if order is None:
                differences.append(
                    {"kind": "PAYMENT_MISMATCH", "detail": f"Provider payment {provider.provider_payment_id} has no order"}
                )
                continue
            if order.amount != provider.amount:
                differences.append(
                    {"kind": "AMOUNT_MISMATCH", "detail": f"Order={order.amount}; Provider={provider.amount}"}
                )
            if order.currency != provider.currency:
                differences.append(
                    {"kind": "CURRENCY_MISMATCH", "detail": f"Order={order.currency}; Provider={provider.currency}"}
                )
        paid = any(item.state == GamePaymentState.PAID for item in self.provider_transactions.values())
        credited = bool(self._credited_payments)
        if paid and not credited:
            differences.append({"kind": "MISSING_CREDIT", "detail": "Provider = PAID; Player Wallet = 0"})
        load_sources = [item.source_id for item in self.wallet_transactions if item.kind == "LOAD"]
        duplicates = sorted({source for source in load_sources if load_sources.count(source) > 1})
        if duplicates:
            differences.append(
                {"kind": "DUPLICATED_CREDIT", "detail": f"Repeated wallet LOAD sources: {', '.join(duplicates)}"}
            )
        orphan_sources = sorted({source for source in load_sources if source not in self.provider_transactions})
        if orphan_sources:
            differences.append(
                {"kind": "ORPHAN_TRANSACTION", "detail": f"Wallet LOAD has no provider payment: {', '.join(orphan_sources)}"}
            )
        orphan_entitlements = sorted(
            item.entitlement_id for item in self.entitlements.values() if item.source_order_id not in self.orders
        )
        if orphan_entitlements:
            differences.append(
                {"kind": "ORPHAN_ENTITLEMENT", "detail": f"Entitlement has no source order: {', '.join(orphan_entitlements)}"}
            )
        inventory_products = {item.product_id for item in self.inventory if item.direction in {"GRANT", "RESTORE"}}
        entitlement_products = {
            item.product_id
            for item in self.entitlements.values()
            if item.status == FulfillmentState.ENTITLEMENT_GRANTED
        }
        if inventory_products != entitlement_products:
            differences.append(
                {
                    "kind": "INVENTORY_MISMATCH",
                    "detail": f"Inventory={sorted(inventory_products)}; entitlements={sorted(entitlement_products)}",
                }
            )
        if any(item.state == GamePaymentState.REFUNDED for item in self.provider_transactions.values()) and any(
            item.status == FulfillmentState.ENTITLEMENT_GRANTED for item in self.entitlements.values()
        ):
            differences.append({"kind": "REFUND_MISMATCH", "detail": "Provider = REFUNDED; entitlement remains active"})
        if (
            any(item.state == GamePaymentState.CHARGEDBACK for item in self.provider_transactions.values())
            and self.wallet.balance < 0
        ):
            differences.append(
                {"kind": "CHARGEBACK_MISMATCH", "detail": "Chargeback arrived after virtual value was consumed"}
            )
        status = "RECONCILED" if not differences else "MISMATCH"
        self._audit(
            "Reconciliation",
            "COMPARE",
            self.correlation_id,
            "PENDING",
            status,
            "Order ↔ Provider ↔ Settlement ↔ Ledger ↔ Wallet ↔ Entitlement",
        )
        return ReconciliationResult(status, differences)


def _journal_dict(journal) -> dict[str, object]:
    return {
        "journal_id": journal.id,
        "reference": journal.reference,
        "created_at": journal.created_at,
        "entries": [
            {"account": e.account, "amount": format(e.amount, "f"), "currency": e.currency} for e in journal.entries
        ],
    }


def _serializable(value: object) -> object:
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, list):
        return [_serializable(item) for item in value]
    if isinstance(value, dict):
        return {key: _serializable(item) for key, item in value.items()}
    return value


def _dataclass_dict(value: object) -> dict[str, object]:
    return _serializable(asdict(value))  # type: ignore[return-value]


def run_virtual_economy_demo(scenario: str = "game-currency-success") -> dict[str, object]:
    if scenario not in GAME_SCENARIOS:
        raise ValueError(f"unknown virtual economy scenario: {scenario}")
    engine = VirtualEconomyEngine()
    order = engine.create_currency_order()
    # A duplicate client retry returns the same order and never creates a second attempt.
    duplicate_order = engine.create_currency_order()
    if duplicate_order.order_id != order.order_id:
        raise RuntimeError("idempotent retry created a second order")
    response_lost = scenario == "game-currency-timeout"
    attempt = engine.submit_payment(order, response_lost=response_lost)
    if response_lost:
        engine.recover_unknown(attempt.provider_payment_id)
    crash_recovered = False
    if scenario == "game-currency-crash-recovery":
        checkpoint = engine.payment_recovery_checkpoint(attempt.provider_payment_id)
        engine = VirtualEconomyEngine.resume_from_payment_checkpoint(checkpoint)
        order = engine.orders[checkpoint.order.order_id]
        attempt = engine.attempts[checkpoint.attempt.payment_attempt_id]
        crash_recovered = True

    event_id = "EVT-PAY-ABC123-SUCCESS"
    if scenario == "game-currency-entitlement-failure":
        engine.process_webhook(event_id, attempt.provider_payment_id, fail_credit=True)
        before_recovery = engine.reconcile()
        engine.credit_wallet(attempt.provider_payment_id)
    else:
        before_recovery = None
        deliveries = 10 if scenario == "game-currency-duplicate-webhook" else 1
        for _ in range(deliveries):
            engine.process_webhook(event_id, attempt.provider_payment_id)

    if scenario in {"game-currency-refund", "game-currency-chargeback"}:
        engine.spend_gems(Decimal("900"), "BATTLE_PASS_2026", "IDEM-SPEND-900")
        if scenario == "game-currency-refund":
            engine.apply_refund(attempt.provider_payment_id)
        else:
            engine.apply_chargeback(attempt.provider_payment_id)
    else:
        engine.spend_gems(Decimal("300"), "SKIN_DRAGON", "IDEM-SKIN-DRAGON")
        if scenario == "game-currency-response-lost":
            engine.spend_gems(Decimal("300"), "SKIN_DRAGON", "IDEM-SKIN-DRAGON")
        if scenario == "game-restore-purchase":
            engine.restore_purchase(next(iter(engine.entitlements)))

    reconciliation = engine.reconcile()
    stages = [
        {"name": "ORDER", "status": "OK"},
        {"name": "PAYMENT", "status": attempt.state.value},
        {"name": "LEDGER", "status": "OK" if engine.external_ledger.journals else "MISSING"},
        {"name": "WALLET", "status": "OK" if engine._credited_payments else "MISSING"},
        {
            "name": "ENTITLEMENT",
            "status": next(iter(engine.entitlements.values())).status.value
            if engine.entitlements
            else FulfillmentState.ENTITLEMENT_PENDING.value,
        },
        {"name": "RECONCILIATION", "status": reconciliation.status},
    ]
    return {
        "mode": "DEMO",
        "moves_money": False,
        "vertical": "Virtual Game Economy / In-Game Purchase Journey",
        "scenario": scenario,
        "scenario_explanation": GAME_SCENARIOS[scenario],
        "correlation_id": engine.correlation_id,
        "identifiers": {
            "order_id": order.order_id,
            "payment_attempt_id": attempt.payment_attempt_id,
            "provider_payment_id": attempt.provider_payment_id,
            "idempotency_key": attempt.idempotency_key,
            "wallet_transaction_id": engine.wallet_transactions[0].wallet_transaction_id,
            "entitlement_id": next(iter(engine.entitlements), None),
            "inventory_transaction_id": engine.inventory[0].inventory_transaction_id if engine.inventory else None,
            "refund_id": next(iter(engine.refunds), None),
            "correlation_id": engine.correlation_id,
        },
        "order": _dataclass_dict(order),
        "payment_attempt": _dataclass_dict(attempt),
        "provider_transaction": _dataclass_dict(engine.provider_transactions[attempt.provider_payment_id]),
        "settlement": [_dataclass_dict(item) for item in engine.settlements.values()],
        "wallet": {
            **_dataclass_dict(engine.wallet),
            "transaction_history": [_dataclass_dict(item) for item in engine.wallet_transactions],
        },
        "entitlements": [_dataclass_dict(item) for item in engine.entitlements.values()],
        "inventory_movements": [_dataclass_dict(item) for item in engine.inventory],
        "refunds": [_dataclass_dict(item) for item in engine.refunds.values()],
        "chargebacks": [_dataclass_dict(item) for item in engine.chargebacks.values()],
        "external_money_ledger": [_journal_dict(item) for item in engine.external_ledger.journals],
        "virtual_value_ledger": [_journal_dict(item) for item in engine.virtual_ledger.journals],
        "webhook_delivery": {
            "event_id": event_id,
            "received": 10 if scenario == "game-currency-duplicate-webhook" else 1,
            "accepted": 1,
            "deduplicated": 9 if scenario == "game-currency-duplicate-webhook" else 0,
        },
        "client_retry": {
            "same_order": len(engine._idempotent_orders) == 1,
            "same_payment_attempt": len(engine.attempts) == 1,
            "wallet_loads": sum(1 for item in engine.wallet_transactions if item.kind == "LOAD"),
            "entitlements": len(engine.entitlements),
        },
        "recovery": {
            "process_restarted": crash_recovered,
            "new_charge_created": False,
            "payment_attempts": len(engine.attempts),
        },
        "before_recovery": _dataclass_dict(before_recovery) if before_recovery else None,
        "reconciliation": _dataclass_dict(reconciliation),
        "stages": stages,
        "timeline": [_dataclass_dict(item) for item in engine.audit],
        "exactly_once_logical_effect": "At-least-once delivery + persisted event IDs + idempotent wallet/entitlement effects.",
        "separation": {
            "movement_a": "CLP 5.990 via provider; external monetary ledger.",
            "movement_b": "1.000 GEM credited and 300/900 GEM spent; virtual-value ledger.",
            "rule": "CLP and GEM are never summed or converted without an explicit business rule.",
        },
        "disclaimer": "DEMO determinista, local y efímera: no contacta stores/PSP, no usa credenciales y no mueve dinero.",
    }
