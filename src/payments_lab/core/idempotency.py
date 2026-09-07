import hashlib
import json

class IdempotencyConflict(RuntimeError):
    pass

class IdempotencyStore:
    def __init__(self):
        self._items = {}

    @staticmethod
    def fingerprint(payload) -> str:
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
        return hashlib.sha256(raw).hexdigest()

    def reserve(self, key: str, payload):
        fp = self.fingerprint(payload)
        old = self._items.get(key)
        if old and old != fp:
            raise IdempotencyConflict("Same idempotency key used with a different payload")
        self._items[key] = fp
        return fp
