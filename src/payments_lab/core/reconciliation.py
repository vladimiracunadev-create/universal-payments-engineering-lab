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
    l = {x.reference: x for x in local}
    r = {x.reference: x for x in remote}
    diffs = []
    for ref in sorted(set(l) | set(r)):
        if ref not in l:
            diffs.append(Difference("REMOTE_ONLY", ref, "Exists in provider but not locally"))
            continue
        if ref not in r:
            diffs.append(Difference("LOCAL_ONLY", ref, "Exists locally but not in provider"))
            continue
        if l[ref].amount != r[ref].amount:
            diffs.append(Difference("AMOUNT_MISMATCH", ref, f"local={l[ref].amount} remote={r[ref].amount}"))
        if l[ref].currency != r[ref].currency:
            diffs.append(Difference("CURRENCY_MISMATCH", ref, f"local={l[ref].currency} remote={r[ref].currency}"))
    return diffs
