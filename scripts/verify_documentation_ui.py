#!/usr/bin/env python3
"""Browser-level verification and screenshots for the generated documentation."""

from __future__ import annotations

import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--origin", default="http://127.0.0.1:8000/universal-payments-engineering-lab")
    parser.add_argument("--output", type=Path, default=Path("artifacts/evidence/documentation"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        page.on(
            "response",
            lambda response: errors.append(f"{response.status} {response.url}")
            if response.status >= 400 and not response.url.endswith("/releases/latest")
            else None,
        )

        page.goto(f"{args.origin}/", wait_until="networkidle")
        page.get_by_role("heading", name="Entiende un pago desde el primer clic hasta la conciliación.").wait_for()
        assert page.locator(".mermaid svg").count() == 1
        page.screenshot(path=args.output / "docs-home.png", full_page=True)

        page.goto(f"{args.origin}/payment-methods/END_TO_END_MATRIX.html", wait_until="networkidle")
        assert page.locator("#docs-case-table tbody tr").count() == 28
        page.locator("#docs-case-filter").fill("Webpay")
        assert page.locator("#docs-case-table tbody tr:visible").count() == 1
        page.screenshot(path=args.output / "docs-28-case-matrix.png", full_page=True)

        page.goto(f"{args.origin}/payment-methods/cases/chile-webpay.html", wait_until="networkidle")
        page.get_by_role("heading", name="04. Transbank Webpay Plus").wait_for()
        for heading in (
            "Ejemplo concreto",
            "Recorrido completo, paso a paso",
            "Qué ocurre si falla",
            "Cómo llevarlo a una aplicación real",
            "Seguridad de datos",
            "Checklist antes de LIVE",
        ):
            assert page.get_by_role("heading", name=heading).is_visible()
        assert page.locator(".case-example-grid article").count() == 3
        assert page.locator(".mermaid svg").count() == 1
        page.screenshot(path=args.output / "docs-webpay-guide.png", full_page=True)
        browser.close()

    if errors:
        raise AssertionError(f"browser console errors: {errors}")
    print("Documentation UI OK: home, Mermaid, 28-case filter and complete Webpay guide")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
