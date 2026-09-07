import json
import urllib.request
import urllib.error

class ProviderHTTPError(RuntimeError):
    def __init__(self, status, body):
        super().__init__(f"Provider HTTP {status}: {body[:500]}")
        self.status = status
        self.body = body

class JsonHTTPClient:
    def request(self, method, url, *, headers=None, payload=None, timeout=30):
        body = None
        h = {"Accept": "application/json", **(headers or {})}
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            h.setdefault("Content-Type", "application/json")
        req = urllib.request.Request(url, data=body, headers=h, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            raise ProviderHTTPError(exc.code, raw) from exc
