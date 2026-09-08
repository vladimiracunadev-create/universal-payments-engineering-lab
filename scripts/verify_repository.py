#!/usr/bin/env python3
"""Deterministic repository/documentation coherence checks (stdlib only)."""

from __future__ import annotations

import ast
import importlib
import json
import re
import sys
import tomllib
import unittest
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
TEXT_SUFFIXES = {".md", ".py", ".toml", ".yaml", ".yml", ".txt"}
IGNORED_PARTS = {".git", ".venv", "__pycache__", "build", "dist"}
ALLOWED_STATUSES = {
    "OPERATIVE_LOCAL",
    "REQUIRES_CREDENTIALS",
    "REQUIRES_CERTIFICATION",
    "REQUIRES_HARDWARE",
    "DOCUMENTED",
}
REQUIRED = {
    ".env.example",
    "README.md",
    "LICENSE",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "CHANGELOG.md",
    "ROADMAP.md",
    "config/payment_rails.yaml",
    "config/case_guides.json",
    "docs/PRODUCT_GUIDE.md",
    "docs/START_HERE.md",
    "docs/LEARNING_PATH.md",
    "docs/LOCALHOST_AND_CONFIGURATION.md",
    "docs/GITHUB_PAGES.md",
    "docs/index.md",
    "docs/_layouts/default.html",
    "docs/assets/docs.css",
    "docs/REFERENCE_REPOSITORIES.md",
    "docs/diagrams/PAYMENT_JOURNEY.md",
    "docs/payment-methods/CASEBOOK.md",
    "docs/IMPLEMENTATION_GUIDE.md",
    "docs/payment-methods/CATALOG.md",
    "docs/operations/RUNBOOK.md",
    "web/index.html",
    "web/styles.css",
    "web/app.js",
    "scripts/start_paylab.ps1",
    "scripts/verify_portal_ui.py",
}


def text_files():
    for path in ROOT.rglob("*"):
        if (
            path.is_file()
            and path.suffix.lower() in TEXT_SUFFIXES
            and not any(part in IGNORED_PARTS for part in path.parts)
        ):
            yield path


def check_encoding(errors: list[str]) -> None:
    suspicious = ("m\u00c3", "\u00c2\u00b7", "\u00e2\u20ac", "\u00f0\u0178")
    for path in text_files():
        raw = path.read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            errors.append(f"UTF-8 BOM: {path.relative_to(ROOT)}")
        try:
            content = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            errors.append(f"invalid UTF-8: {path.relative_to(ROOT)} ({exc})")
            continue
        if any(marker in content for marker in suspicious):
            errors.append(f"possible mojibake: {path.relative_to(ROOT)}")


def check_versions(errors: list[str]) -> None:
    project_version = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    init_text = (ROOT / "src/payments_lab/__init__.py").read_text(encoding="utf-8")
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)', init_text)
    package_version = match.group(1) if match else None
    if project_version != package_version:
        errors.append(f"version drift: pyproject={project_version}, package={package_version}")


def check_catalog(errors: list[str]) -> int:
    content = (ROOT / "config/payment_rails.yaml").read_text(encoding="utf-8")
    families = re.findall(r"^  - id: ([a-z0-9-]+)$", content, flags=re.MULTILINE)
    statuses = re.findall(r"^    status: ([A-Z_]+)$", content, flags=re.MULTILINE)
    if len(families) < 20:
        errors.append(f"catalog too small: {len(families)} families")
    if len(families) != len(set(families)):
        errors.append("duplicate family id in payment catalog")
    unknown = sorted(set(statuses) - ALLOWED_STATUSES)
    if unknown:
        errors.append(f"unknown catalog statuses: {unknown}")
    if len(statuses) != len(families):
        errors.append(f"each family needs one status: {len(families)} families, {len(statuses)} statuses")
    guides = json.loads((ROOT / "config/case_guides.json").read_text(encoding="utf-8"))
    missing_guides = sorted(set(families) - set(guides))
    extra_guides = sorted(set(guides) - set(families))
    if missing_guides or extra_guides:
        errors.append(f"catalog/guide drift: missing={missing_guides}, extra={extra_guides}")
    for rail_id, guide in guides.items():
        missing = sorted({"title", "solves", "demo_focus"} - set(guide))
        if missing:
            errors.append(f"incomplete guide for {rail_id}: {missing}")
    for adapter in re.findall(r"^    adapter: ([A-Za-z0-9_.]+)$", content, flags=re.MULTILINE):
        module_name, _, class_name = adapter.rpartition(".")
        try:
            module = importlib.import_module(module_name)
            getattr(module, class_name)
        except (ImportError, AttributeError) as exc:
            errors.append(f"catalog adapter cannot be imported: {adapter} ({exc})")
    metadata = json.loads((ROOT / ".github" / "repository-metadata.json").read_text(encoding="utf-8"))
    if f"{len(families)} familias" not in metadata.get("description", ""):
        errors.append("repository metadata family count does not match catalog")
    return len(families)


def check_product_assets(errors: list[str]) -> None:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    for asset in (
        "config/payment_rails.yaml",
        "config/case_guides.json",
        "web/index.html",
        "web/styles.css",
        "web/app.js",
        "web/icons.svg",
    ):
        if asset not in pyproject:
            errors.append(f"package data missing from pyproject.toml: {asset}")
    html = (ROOT / "web/index.html").read_text(encoding="utf-8")
    if "<script>" in html or "style=" in html:
        errors.append("portal must keep scripts/styles external for its strict CSP")
    for teaching_marker in ("Empieza aquí", "Qué aprenderás", "Cómo leer el resultado", "Ejemplo guiado"):
        if teaching_marker not in html:
            errors.append(f"portal is missing teaching marker: {teaching_marker}")
    from payments_lab.catalog import enriched_catalog

    for family in enriched_catalog():
        guide = family.get("playbook", {})
        required = {
            "stack",
            "access",
            "pricing",
            "implementation",
            "testing",
            "security",
            "failures",
            "go_live",
            "sources",
            "teaching",
            "configuration",
        }
        missing = sorted(required - set(guide))
        if missing:
            errors.append(f"incomplete implementation playbook for {family['id']}: {missing}")
        if not guide.get("sources") or not all(
            source.get("url", "").startswith("https://") for source in guide["sources"]
        ):
            errors.append(f"implementation playbook needs HTTPS official sources: {family['id']}")
        teaching = guide.get("teaching", {})
        if (
            not teaching.get("mental_model")
            or not teaching.get("development_path")
            or not teaching.get("success_evidence")
        ):
            errors.append(f"incomplete pedagogical explanation for {family['id']}")


def check_markdown_links(errors: list[str]) -> None:
    pattern = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
    for path in ROOT.rglob("*.md"):
        if any(part in IGNORED_PARTS for part in path.parts):
            continue
        for target in pattern.findall(path.read_text(encoding="utf-8")):
            target = target.strip().split("#", 1)[0]
            if not target or "://" in target or target.startswith(("mailto:", "#")):
                continue
            if not (path.parent / unquote(target)).resolve().exists():
                errors.append(f"broken link: {path.relative_to(ROOT)} -> {target}")


def check_curriculum(errors: list[str]) -> None:
    content = (ROOT / "curriculum/README.md").read_text(encoding="utf-8")
    modules = re.findall(r"^\| \d{2} \|", content, flags=re.MULTILINE)
    if len(modules) != 32:
        errors.append(f"curriculum declares 32 modules but contains {len(modules)} rows")


def count_tests() -> int:
    sys.path.insert(0, str(ROOT / "src"))
    return unittest.defaultTestLoader.discover(str(ROOT / "tests")).countTestCases()


def check_python_syntax(errors: list[str]) -> None:
    for path in text_files():
        if path.suffix == ".py":
            try:
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            except SyntaxError as exc:
                errors.append(f"python syntax: {path.relative_to(ROOT)}:{exc.lineno}: {exc.msg}")


def check_workflows(errors: list[str]) -> int:
    workflows = sorted((ROOT / ".github" / "workflows").glob("*.yml"))
    mutable = re.compile(r"^\s*uses:\s*[^@\s]+@(?![0-9a-f]{40}(?:\s|$))", re.MULTILINE)
    for path in workflows:
        if mutable.search(path.read_text(encoding="utf-8")):
            errors.append(f"workflow action is not pinned to a 40-character SHA: {path.relative_to(ROOT)}")
    return len(workflows)


def main() -> int:
    errors: list[str] = []
    missing = sorted(item for item in REQUIRED if not (ROOT / item).exists())
    if missing:
        errors.append(f"missing required files: {missing}")
    check_encoding(errors)
    check_versions(errors)
    families = check_catalog(errors)
    check_markdown_links(errors)
    check_curriculum(errors)
    check_python_syntax(errors)
    check_product_assets(errors)
    workflows = check_workflows(errors)
    tests = count_tests()
    if tests < 40:
        errors.append(f"expected at least 40 tests, discovered {tests}")
    if errors:
        print("Repository verification FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        f"Repository verification OK: {families} payment families, 32 curriculum modules, "
        f"{tests} tests, {workflows} workflows"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
