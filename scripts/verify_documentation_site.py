#!/usr/bin/env python3
"""Validate the built documentation artifact and its internal navigation."""

from __future__ import annotations

import argparse
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

PAGES_PREFIX = "/universal-payments-engineering-lab/"


class References(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.targets: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        names = {"href"} if tag == "a" else {"src"} if tag in {"img", "script"} else set()
        for name, value in attrs:
            if name in names and value:
                self.targets.append(value)


def resolve_target(site: Path, page: Path, target: str) -> Path | None:
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc or target.startswith(("#", "mailto:", "tel:", "data:")):
        return None
    clean = unquote(parsed.path)
    if not clean:
        return None
    rooted = clean.startswith("/")
    if clean.startswith(PAGES_PREFIX):
        clean = clean[len(PAGES_PREFIX) :]
    candidate = (site / clean.lstrip("/")) if rooted else (page.parent / clean)
    if candidate.is_dir():
        candidate /= "index.html"
    return candidate.resolve()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site-dir", default="site")
    args = parser.parse_args()
    site = Path(args.site_dir).resolve()
    errors: list[str] = []
    pages = sorted(site.rglob("*.html"))
    if not pages:
        errors.append("the documentation build contains no HTML pages")

    for page in pages:
        content = page.read_text(encoding="utf-8")
        if "layout: default" in content or "{% include" in content:
            errors.append(f"template source leaked into {page.relative_to(site)}")
        refs = References()
        refs.feed(content)
        for target in refs.targets:
            resolved = resolve_target(site, page, target)
            if resolved is not None and site not in resolved.parents and resolved != site:
                errors.append(f"navigation escapes site: {page.relative_to(site)} -> {target}")
            elif resolved is not None and not resolved.exists():
                errors.append(f"broken built link: {page.relative_to(site)} -> {target}")

    case_pages = sorted((site / "payment-methods" / "cases").glob("*.html"))
    if len(case_pages) != 28:
        errors.append(f"expected 28 built case pages, found {len(case_pages)}")
    required_text = (
        "Ejemplo concreto",
        "Recorrido completo, paso a paso",
        "Qué ocurre si falla",
        "Cómo llevarlo a una aplicación real",
        "Seguridad de datos",
        "Checklist antes de LIVE",
    )
    for page in case_pages:
        content = page.read_text(encoding="utf-8")
        missing = [text for text in required_text if text not in content]
        if missing:
            errors.append(f"incomplete built case {page.name}: {missing}")

    matrix = site / "payment-methods" / "END_TO_END_MATRIX.html"
    if not matrix.is_file() or matrix.read_text(encoding="utf-8").count('data-search="') != 28:
        errors.append("built matrix is missing or does not expose 28 searchable rows")

    if errors:
        print("Documentation site verification FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Documentation site verification OK: {len(pages)} pages, 28 complete cases, 0 broken links")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
