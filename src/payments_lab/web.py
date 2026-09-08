"""Local HTTP API and static portal for the payment laboratory."""

from __future__ import annotations

import argparse
import json
import mimetypes
import re
import sysconfig
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from .catalog import enriched_catalog
from .demo import SCENARIOS, run_demo
from .doctor import diagnose

MAX_REQUEST_BYTES = 16_384
DEMO_ROUTE = re.compile(r"^/api/demo/([a-z0-9-]+)$")
STATIC_FILES = {
    "/": "index.html",
    "/index.html": "index.html",
    "/app.js": "app.js",
    "/styles.css": "styles.css",
}


def _web_root() -> Path:
    candidates = (
        Path.cwd() / "web",
        Path(__file__).resolve().parents[2] / "web",
        Path(sysconfig.get_path("data")) / "share" / "paylab" / "web",
    )
    for candidate in candidates:
        if (candidate / "index.html").is_file():
            return candidate
    raise FileNotFoundError("PayLab web assets were not found; reinstall the package with its data files")


class PayLabHandler(BaseHTTPRequestHandler):
    server_version = "PayLab/0.1"

    def _headers(self, status: int, content_type: str, length: int) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(length))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self'; script-src 'self'")
        self.end_headers()

    def _json(self, value: object, status: int = HTTPStatus.OK) -> None:
        raw = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self._headers(status, "application/json; charset=utf-8", len(raw))
        self.wfile.write(raw)

    def _error(self, status: int, code: str, detail: str) -> None:
        self._json({"error": code, "detail": detail}, status)

    def do_GET(self) -> None:  # noqa: N802
        path = urlsplit(self.path).path
        if path == "/api/health":
            self._json({"status": "ok", "mode": "DEMO", "moves_money": False})
            return
        if path == "/api/doctor":
            self._json(diagnose())
            return
        if path == "/api/catalog":
            self._json({"families": enriched_catalog()})
            return
        if path == "/api/scenarios":
            self._json({"scenarios": [{"id": key, "description": value} for key, value in SCENARIOS.items()]})
            return
        filename = STATIC_FILES.get(path)
        if filename is None:
            self._error(HTTPStatus.NOT_FOUND, "not_found", "Route not found")
            return
        asset = _web_root() / filename
        raw = asset.read_bytes()
        content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        if content_type.startswith("text/") or content_type == "application/javascript":
            content_type += "; charset=utf-8"
        self._headers(HTTPStatus.OK, content_type, len(raw))
        self.wfile.write(raw)

    def do_POST(self) -> None:  # noqa: N802
        match = DEMO_ROUTE.fullmatch(urlsplit(self.path).path)
        if match is None:
            self._error(HTTPStatus.NOT_FOUND, "not_found", "Route not found")
            return
        try:
            declared = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._error(HTTPStatus.BAD_REQUEST, "invalid_length", "Content-Length must be numeric")
            return
        if declared < 0 or declared > MAX_REQUEST_BYTES:
            self._error(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, "request_too_large", "Request body exceeds 16 KiB")
            return
        try:
            payload = json.loads(self.rfile.read(declared) or b"{}")
            if not isinstance(payload, dict):
                raise ValueError("JSON body must be an object")
            result = run_demo(
                match.group(1),
                scenario=str(payload.get("scenario", "success")),
                amount=str(payload.get("amount", "19990")),
                currency=str(payload.get("currency", "CLP")),
            )
        except KeyError as exc:
            self._error(HTTPStatus.NOT_FOUND, "unknown_rail", str(exc))
            return
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            self._error(HTTPStatus.BAD_REQUEST, "invalid_request", str(exc))
            return
        self._json(result, HTTPStatus.CREATED)

    def log_message(self, format: str, *args: object) -> None:
        print(f"{self.address_string()} - {format % args}")


def create_server(host: str = "127.0.0.1", port: int = 8080) -> ThreadingHTTPServer:
    if host not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("the laboratory binds to localhost only")
    return ThreadingHTTPServer((host, port), PayLabHandler)


def serve(host: str = "127.0.0.1", port: int = 8080) -> None:
    server = create_server(host, port)
    print(f"PayLab DEMO available at http://{host}:{server.server_port}")
    print("Mode: DEMO · no credentials · no external providers · no money movement")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Serve the PayLab localhost portal")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args(argv)
    serve(args.host, args.port)


if __name__ == "__main__":
    main()
