#!/usr/bin/env python3
"""Browser-level verification and readable evidence screenshots for PayLab."""

from __future__ import annotations

import argparse
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError as exc:
    raise SystemExit("Install the optional QA tool with: python -m pip install playwright") from exc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--origin", default="http://127.0.0.1:8080")
    parser.add_argument("--output", type=Path, default=Path("docs/assets"))
    parser.add_argument("--executable", help="Optional Chromium executable when the bundled revision differs")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    console_errors: list[str] = []

    with sync_playwright() as playwright:
        browser = (
            playwright.chromium.launch(executable_path=args.executable)
            if args.executable
            else playwright.chromium.launch()
        )
        page = browser.new_page(viewport={"width": 1440, "height": 1000}, device_scale_factor=1)
        page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
        page.goto(args.origin, wait_until="networkidle")
        page.get_by_text("Empieza aquí", exact=False).first.wait_for()
        assert page.locator("#family-count").inner_text() == "28"
        assert page.get_by_role("heading", name="Qué aprenderás").is_visible()
        assert page.locator("#configuration-panel").is_visible()
        assert page.locator("svg.icon use").count() >= 10
        page.screenshot(path=args.output / "paylab-home.png")

        page.locator("#rail").select_option("chile-webpay")
        page.get_by_text("TRANSBANK_API_KEY", exact=True).wait_for()
        page.locator("#configuration").screenshot(path=args.output / "paylab-configuration.png")

        page.get_by_role("button", name="Ejemplo guiado").click()
        page.get_by_text("Un timeout no significa que el pago falló", exact=True).wait_for()
        assert page.get_by_text("Estado: UNKNOWN", exact=True).is_visible()
        assert page.get_by_text("NO MOVIÓ DINERO", exact=True).is_visible()
        page.locator("#result").screenshot(path=args.output / "paylab-timeout-recovered.png")

        mobile = browser.new_page(viewport={"width": 390, "height": 844})
        mobile.goto(args.origin, wait_until="networkidle")
        overflow = mobile.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth")
        assert not overflow
        assert mobile.get_by_role("button", name="Ejemplo guiado").is_visible()
        browser.close()

    if console_errors:
        raise AssertionError(f"browser console errors: {console_errors}")
    print("Portal UI OK: purpose, 28 cases, icons, configuration, guided timeout and mobile layout")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
