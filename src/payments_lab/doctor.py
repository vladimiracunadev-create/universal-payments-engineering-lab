"""Runtime readiness checks with explicit DEMO/SANDBOX/LIVE boundaries."""

from __future__ import annotations

import os
import platform
import sys

from .catalog import enriched_catalog
from .configuration import PROVIDER_VARIABLES


def diagnose() -> dict[str, object]:
    families = enriched_catalog()
    providers = []
    for provider, variables in PROVIDER_VARIABLES.items():
        missing = [str(item["name"]) for item in variables if not os.getenv(str(item["name"]))]
        providers.append(
            {
                "id": provider,
                "configured": not missing,
                "missing": missing,
                "note": (
                    "Configurado; valide el ambiente antes de operar."
                    if not missing
                    else "DEMO disponible; SANDBOX/LIVE no configurado."
                ),
            }
        )
    return {
        "status": "ready",
        "python": platform.python_version(),
        "python_supported": sys.version_info >= (3, 11),
        "platform": platform.platform(),
        "demo": {"ready": True, "families": len(families), "moves_money": False},
        "providers": providers,
        "safety": {
            "automatic_live_fallback": False,
            "rule": "El modo se fija antes del intento. Un timeout externo queda UNKNOWN; nunca se reemplaza por DEMO.",
        },
    }
