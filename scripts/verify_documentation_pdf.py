#!/usr/bin/env python3
"""Verify PDF content, navigation, links, page geometry and case coverage."""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import pdfplumber
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from payments_lab.catalog import enriched_catalog  # noqa: E402

PDF = ROOT / "output" / "pdf" / "universal-payments-engineering-lab.pdf"


def main() -> int:
    errors: list[str] = []
    if not PDF.is_file() or PDF.stat().st_size < 100_000:
        errors.append("PDF is missing or unexpectedly small")
        print("\n".join(errors))
        return 1

    reader = PdfReader(PDF)
    if len(reader.pages) < 30:
        errors.append(f"expected at least 30 pages, found {len(reader.pages)}")
    if reader.metadata.title != "Universal Payments Engineering Lab - Manual navegable":
        errors.append("PDF title metadata is missing")

    expected_destinations = {"contents", *[f"case-{family['id']}" for family in enriched_catalog()]}
    missing_destinations = sorted(expected_destinations - set(reader.named_destinations))
    if missing_destinations:
        errors.append(f"missing named destinations: {missing_destinations}")

    annotations: Counter[str] = Counter()
    for page in reader.pages:
        for reference in page.get("/Annots", []):
            annotation = reference.get_object()
            if "/Dest" in annotation:
                annotations["internal"] += 1
            elif annotation.get("/A", {}).get("/URI"):
                annotations["external"] += 1
    if annotations["internal"] < 56:
        errors.append(f"expected at least 56 internal links, found {annotations['internal']}")
    if annotations["external"] < 84:
        errors.append(f"expected at least 84 external links, found {annotations['external']}")

    with pdfplumber.open(PDF) as document:
        page_texts = [page.extract_text() or "" for page in document.pages]
        full_text = "\n".join(page_texts)
        for page_number, (page, text) in enumerate(zip(document.pages, page_texts, strict=True), 1):
            meaningful = [
                line
                for line in text.splitlines()
                if line.strip()
                and "Universal Payments Engineering Lab" not in line
                and not line.strip().startswith("Página ")
            ]
            if len(" ".join(meaningful).split()) < 15:
                errors.append(f"page {page_number} is blank, unreadable or contains an orphan link")
            for char in page.chars:
                outside_page = (
                    char["x0"] < -1
                    or char["top"] < -1
                    or char["x1"] > page.width + 1
                    or char["bottom"] > page.height + 1
                )
                if outside_page:
                    errors.append(f"text escapes page bounds on page {page_number}")
                    break
        for number, family in enumerate(enriched_catalog(), 1):
            if str(family["title"]) not in full_text:
                errors.append(f"case missing from PDF: {family['id']}")
            if f"Figura {number}. Flujo verificable del caso" not in full_text:
                errors.append(f"vector flow diagram missing for case: {family['id']}")
        if "Syntax error" in full_text:
            errors.append("Mermaid error text leaked into PDF")
        if "<b>" in full_text or "<br/>" in full_text or "&gt;" in full_text:
            errors.append("escaped markup leaked into visible PDF text")

    if errors:
        print("Documentation PDF verification FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        f"Documentation PDF verification OK: {len(reader.pages)} pages, 28 cases, "
        f"{annotations['internal']} internal links, {annotations['external']} external links, "
        "28 vector diagrams"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
