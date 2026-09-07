from enum import StrEnum


class PaymentState(StrEnum):
    CREATED = "CREATED"
    REQUIRES_PAYMENT_METHOD = "REQUIRES_PAYMENT_METHOD"
    REQUIRES_AUTHENTICATION = "REQUIRES_AUTHENTICATION"
    PROCESSING = "PROCESSING"
    AUTHORIZED = "AUTHORIZED"
    CAPTURED = "CAPTURED"
    SETTLED = "SETTLED"
    RECONCILED = "RECONCILED"
    DECLINED = "DECLINED"
    TIMEOUT = "TIMEOUT"
    UNKNOWN = "UNKNOWN"
    CANCELLED = "CANCELLED"
    REVERSED = "REVERSED"
    FAILED = "FAILED"
    PARTIALLY_REFUNDED = "PARTIALLY_REFUNDED"
    REFUNDED = "REFUNDED"
    DISPUTED = "DISPUTED"
    CHARGEBACK = "CHARGEBACK"


ALLOWED_TRANSITIONS = {
    PaymentState.CREATED: {PaymentState.REQUIRES_PAYMENT_METHOD, PaymentState.PROCESSING, PaymentState.CANCELLED},
    PaymentState.REQUIRES_PAYMENT_METHOD: {
        PaymentState.REQUIRES_AUTHENTICATION,
        PaymentState.PROCESSING,
        PaymentState.CANCELLED,
    },
    PaymentState.REQUIRES_AUTHENTICATION: {PaymentState.PROCESSING, PaymentState.DECLINED, PaymentState.CANCELLED},
    PaymentState.PROCESSING: {
        PaymentState.AUTHORIZED,
        PaymentState.CAPTURED,
        PaymentState.DECLINED,
        PaymentState.TIMEOUT,
        PaymentState.UNKNOWN,
        PaymentState.FAILED,
    },
    PaymentState.AUTHORIZED: {
        PaymentState.CAPTURED,
        PaymentState.REVERSED,
        PaymentState.CANCELLED,
        PaymentState.UNKNOWN,
    },
    PaymentState.CAPTURED: {
        PaymentState.SETTLED,
        PaymentState.PARTIALLY_REFUNDED,
        PaymentState.REFUNDED,
        PaymentState.DISPUTED,
        PaymentState.CHARGEBACK,
    },
    PaymentState.SETTLED: {
        PaymentState.RECONCILED,
        PaymentState.PARTIALLY_REFUNDED,
        PaymentState.REFUNDED,
        PaymentState.DISPUTED,
        PaymentState.CHARGEBACK,
    },
    PaymentState.PARTIALLY_REFUNDED: {PaymentState.PARTIALLY_REFUNDED, PaymentState.REFUNDED, PaymentState.DISPUTED},
    PaymentState.TIMEOUT: {
        PaymentState.UNKNOWN,
        PaymentState.AUTHORIZED,
        PaymentState.CAPTURED,
        PaymentState.DECLINED,
        PaymentState.FAILED,
    },
    PaymentState.UNKNOWN: {
        PaymentState.AUTHORIZED,
        PaymentState.CAPTURED,
        PaymentState.DECLINED,
        PaymentState.FAILED,
        PaymentState.REVERSED,
    },
}


def can_transition(current: PaymentState, target: PaymentState) -> bool:
    return target in ALLOWED_TRANSITIONS.get(current, set())


def transition(current: PaymentState, target: PaymentState) -> PaymentState:
    if not can_transition(current, target):
        raise ValueError(f"Invalid payment transition: {current} -> {target}")
    return target
