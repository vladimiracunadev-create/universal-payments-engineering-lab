from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class PaymentRecord:
    reference: str
    amount: Decimal
    currency: str


@dataclass(frozen=True)
class Difference:
    kind: str
    reference: str
    detail: str


def reconcile(local: list[PaymentRecord], remote: list[PaymentRecord]) -> list[Difference]:
    local_by_reference = {item.reference: item for item in local}
    remote_by_reference = {item.reference: item for item in remote}
    diffs = []
    for ref in sorted(set(local_by_reference) | set(remote_by_reference)):
        if ref not in local_by_reference:
            diffs.append(Difference("REMOTE_ONLY", ref, "Exists in provider but not locally"))
            continue
        if ref not in remote_by_reference:
            diffs.append(Difference("LOCAL_ONLY", ref, "Exists locally but not in provider"))
            continue
        local_item = local_by_reference[ref]
        remote_item = remote_by_reference[ref]
        if local_item.amount != remote_item.amount:
            diffs.append(Difference("AMOUNT_MISMATCH", ref, f"local={local_item.amount} remote={remote_item.amount}"))
        if local_item.currency != remote_item.currency:
            diffs.append(
                Difference("CURRENCY_MISMATCH", ref, f"local={local_item.currency} remote={remote_item.currency}")
            )
    return diffs
