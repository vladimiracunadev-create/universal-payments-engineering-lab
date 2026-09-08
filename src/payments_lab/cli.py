"""Command-line interface for controlled payment laboratory operations."""

import argparse
import json
import os
from pathlib import Path

from .adapters.khipu import KhipuProvider
from .adapters.mercadopago import MercadoPagoProvider
from .adapters.transbank import WebpayPlusProvider
from .catalog import catalog_text
from .core.states import PaymentState
from .demo import SCENARIOS, run_demo
from .doctor import diagnose
from .web import serve


def print_json(value) -> None:
    print(json.dumps(value, indent=2, ensure_ascii=False))


def load_json(path: str):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Universal Payments Engineering Lab CLI")
    commands = parser.add_subparsers(dest="cmd", required=True)
    commands.add_parser("catalog")
    commands.add_parser("states")
    commands.add_parser("doctor")
    demo = commands.add_parser("demo", help="Run a deterministic journey that never moves money")
    demo.add_argument("rail")
    demo.add_argument("--scenario", choices=tuple(SCENARIOS), default="success")
    demo.add_argument("--amount", default="19990")
    demo.add_argument("--currency", default="CLP")
    local = commands.add_parser("serve", help="Open the local DEMO portal")
    local.add_argument("--host", default=os.getenv("PAYLAB_HOST", "127.0.0.1"))
    local.add_argument("--port", type=int, default=os.getenv("PAYLAB_PORT", "8080"))

    khipu_create = commands.add_parser("khipu-create")
    khipu_create.add_argument("--subject", required=True)
    khipu_create.add_argument("--amount", required=True, help="Decimal string; never binary float")
    khipu_create.add_argument("--currency", default="CLP")
    khipu_create.add_argument("--return-url", required=True)
    khipu_create.add_argument("--notify-url")
    khipu_get = commands.add_parser("khipu-get")
    khipu_get.add_argument("payment_id")

    mp_create = commands.add_parser("mp-create")
    mp_create.add_argument("--payload", required=True)
    mp_create.add_argument("--idempotency-key", required=True)
    mp_get = commands.add_parser("mp-get")
    mp_get.add_argument("payment_id")
    mp_refund = commands.add_parser("mp-refund")
    mp_refund.add_argument("payment_id")
    mp_refund.add_argument("--idempotency-key", required=True)
    mp_refund.add_argument("--amount", help="Decimal string; omit for full refund")

    tbk_create = commands.add_parser("tbk-create")
    tbk_create.add_argument("--buy-order", required=True)
    tbk_create.add_argument("--session-id", required=True)
    tbk_create.add_argument("--amount", required=True, help="Integer/decimal string")
    tbk_create.add_argument("--return-url", required=True)
    for command in ("tbk-commit", "tbk-status"):
        commands.add_parser(command).add_argument("token")
    tbk_refund = commands.add_parser("tbk-refund")
    tbk_refund.add_argument("token")
    tbk_refund.add_argument("--amount", required=True, help="Integer/decimal string")
    return parser


def main(argv=None) -> None:
    args = build_parser().parse_args(argv)
    if args.cmd == "catalog":
        print(catalog_text())
    elif args.cmd == "states":
        print("\n".join(item.value for item in PaymentState))
    elif args.cmd == "doctor":
        print_json(diagnose())
    elif args.cmd == "demo":
        print_json(run_demo(args.rail, scenario=args.scenario, amount=args.amount, currency=args.currency))
    elif args.cmd == "serve":
        serve(args.host, args.port)
    elif args.cmd == "khipu-create":
        payload = {
            "subject": args.subject,
            "amount": args.amount,
            "currency": args.currency,
            "return_url": args.return_url,
        }
        if args.notify_url:
            payload["notify_url"] = args.notify_url
        print_json(KhipuProvider().create(payload))
    elif args.cmd == "khipu-get":
        print_json(KhipuProvider().get(args.payment_id))
    elif args.cmd == "mp-create":
        print_json(MercadoPagoProvider().create(load_json(args.payload), idempotency_key=args.idempotency_key))
    elif args.cmd == "mp-get":
        print_json(MercadoPagoProvider().get(args.payment_id))
    elif args.cmd == "mp-refund":
        print_json(
            MercadoPagoProvider().refund(args.payment_id, amount=args.amount, idempotency_key=args.idempotency_key)
        )
    elif args.cmd == "tbk-create":
        payload = {
            "buy_order": args.buy_order,
            "session_id": args.session_id,
            "amount": args.amount,
            "return_url": args.return_url,
        }
        print_json(WebpayPlusProvider().create(payload))
    elif args.cmd == "tbk-commit":
        print_json(WebpayPlusProvider().commit(args.token))
    elif args.cmd == "tbk-status":
        print_json(WebpayPlusProvider().get(args.token))
    elif args.cmd == "tbk-refund":
        print_json(WebpayPlusProvider().refund(args.token, args.amount))


if __name__ == "__main__":
    main()
