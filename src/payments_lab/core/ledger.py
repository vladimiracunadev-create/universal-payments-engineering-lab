from dataclasses import dataclass, field
from decimal import Decimal
from datetime import datetime, timezone
from uuid import uuid4

@dataclass(frozen=True)
class Entry:
    account: str
    amount: Decimal
    currency: str

@dataclass(frozen=True)
class Journal:
    id: str
    reference: str
    entries: tuple[Entry, ...]
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class Ledger:
    def __init__(self):
        self._journals: list[Journal] = []

    def post(self, reference: str, entries: list[Entry]) -> Journal:
        if len(entries) < 2:
            raise ValueError("A journal requires at least two entries")
        currencies = {e.currency for e in entries}
        if len(currencies) != 1:
            raise ValueError("Each journal must use a single currency")
        total = sum((e.amount for e in entries), Decimal("0"))
        if total != Decimal("0"):
            raise ValueError(f"Unbalanced journal: {total}")
        journal = Journal(str(uuid4()), reference, tuple(entries))
        self._journals.append(journal)
        return journal

    @property
    def journals(self):
        return tuple(self._journals)
