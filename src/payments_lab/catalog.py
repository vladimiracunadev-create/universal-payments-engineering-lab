"""Dependency-free catalog loading for source checkouts and installed packages."""

from __future__ import annotations

import json
import os
import sysconfig
from pathlib import Path


def _candidate_paths(filename: str) -> tuple[Path, ...]:
    candidates = []
    if configured := os.getenv("PAYLAB_CONFIG_DIR"):
        candidates.append(Path(configured) / filename)
    candidates.extend(
        (
            Path.cwd() / "config" / filename,
            Path(__file__).resolve().parents[2] / "config" / filename,
            Path(sysconfig.get_path("data")) / "config" / filename,
        )
    )
    return tuple(candidates)


def config_path(filename: str) -> Path:
    for candidate in _candidate_paths(filename):
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(
        f"{filename} was not found; set PAYLAB_CONFIG_DIR or reinstall the package with its data files"
    )


def catalog_text() -> str:
    return config_path("payment_rails.yaml").read_text(encoding="utf-8")


def _inline_list(value: str) -> list[str]:
    value = value.strip()
    if not (value.startswith("[") and value.endswith("]")):
        raise ValueError(f"expected an inline YAML list, got {value!r}")
    return [item.strip() for item in value[1:-1].split(",") if item.strip()]


def load_catalog() -> list[dict[str, object]]:
    families: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    for raw_line in catalog_text().splitlines():
        if raw_line == "cross_cutting:":
            break
        if raw_line.startswith("  - id: "):
            current = {"id": raw_line.split(":", 1)[1].strip()}
            families.append(current)
            continue
        if current is None or not raw_line.startswith("    "):
            continue
        key, separator, value = raw_line.strip().partition(":")
        if separator:
            value = value.strip()
            current[key] = _inline_list(value) if value.startswith("[") else value
    return families


def load_guides() -> dict[str, dict[str, object]]:
    decoded = json.loads(config_path("case_guides.json").read_text(encoding="utf-8"))
    if not isinstance(decoded, dict):
        raise ValueError("case_guides.json root must be an object")
    return decoded


def enriched_catalog() -> list[dict[str, object]]:
    from .playbooks import build_playbook

    guides = load_guides()
    result = []
    for family in load_catalog():
        rail_id = str(family["id"])
        guide = guides.get(rail_id)
        if guide is None:
            raise ValueError(f"missing guide for payment family {rail_id}")
        enriched = {**family, **guide}
        enriched["playbook"] = build_playbook(rail_id, str(guide["title"]))
        result.append(enriched)
    return result
