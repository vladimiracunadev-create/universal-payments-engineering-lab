#!/usr/bin/env python3
# ruff: noqa: E501
"""Generate one clean Markdown guide and one Pages wrapper per payment case."""

from __future__ import annotations

import argparse
import html
from pathlib import Path

from payments_lab.catalog import enriched_catalog

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "docs" / "payment-methods" / "cases"


def _text(value: object) -> str:
    return str(value).replace("\n", " ").strip()


def _list(items: list[object]) -> list[str]:
    return [f"- {_text(item)}" for item in items]


def _actors(rail_id: str) -> list[str]:
    if rail_id in {"cash", "paper", "cash-voucher"}:
        return ["Cliente o pagador", "Comercio/cajero", "Custodio o recaudador", "Banco y equipo de conciliación"]
    if rail_id in {"cards", "chile-webpay", "chile-oneclick", "acceptance-devices", "tokenized-wallets"}:
        return [
            "Cliente",
            "Frontend del comercio",
            "Backend del comercio",
            "PSP/adquirente/red",
            "Banco emisor",
            "Operaciones y conciliación",
        ]
    if rail_id in {"bank-transfer", "ach", "direct-debit", "instant-payments", "chile-khipu", "open-finance"}:
        return [
            "Pagador",
            "Backend del comercio o TPP",
            "Proveedor/API bancaria",
            "Banco pagador",
            "Banco receptor",
            "Operaciones y conciliación",
        ]
    if rail_id == "platform-payments":
        return ["Comprador", "Marketplace", "PSP", "Vendedores/beneficiarios", "Motor de subledger y payouts"]
    if rail_id in {"machine-payments", "agentic-payments"}:
        return [
            "Propietario humano",
            "Máquina o agente",
            "Motor de políticas",
            "Backend de pagos",
            "Proveedor/rail",
            "Auditoría",
        ]
    return ["Pagador", "Canal o frontend", "Backend del negocio", "Proveedor o rail", "Operaciones y conciliación"]


def render_markdown(family: dict[str, object], number: int) -> str:
    guide = family["playbook"]
    journey = guide["journey"]
    teaching = guide["teaching"]
    configuration = guide["configuration"]
    title = _text(family["title"])
    rail_id = _text(family["id"])
    technologies = ", ".join(f"`{item}`" for item in family.get("technologies", []))
    cases = ", ".join(f"`{item}`" for item in family.get("cases", []))
    variables = [*configuration["global_variables"], *configuration["provider_variables"]]
    variable_rows = [
        f"| `{item['name']}` | {'Sí' if item['required'] else 'No'} | {'Secreta' if item['sensitive'] else 'No secreta'} | {_text(item['purpose'])} |"
        for item in variables
    ]
    callback_lines = _list(configuration["callbacks"]) or ["- No hay callback concreto hasta seleccionar un proveedor."]
    source_lines = [f"- [{source['title']}]({source['url']})" for source in guide["sources"]]

    lines = [
        f"# {number:02d}. {title}",
        "",
        "[← Volver a la tabla web](../END_TO_END_MATRIX.html) · [← Volver a la tabla Markdown](../END_TO_END_MATRIX.md)",
        "",
        "## En una frase",
        "",
        f"**Sirve para:** {_text(journey['when'])}",
        "",
        f"**Modelo mental:** {_text(teaching['mental_model'])}",
        "",
        "## Ejemplo concreto",
        "",
        f"Imagina esta necesidad: {_text(journey['when'])} El negocio no puede limitarse a mostrar «pago exitoso»; debe conservar una referencia, obtener una confirmación autoritativa y demostrar después cómo terminó el dinero.",
        "",
        "## Quién participa",
        "",
        *_list(_actors(rail_id)),
        "",
        "## Recorrido completo, paso a paso",
        "",
        "| Etapa | Qué ocurre | Pregunta de control |",
        "|---|---|---|",
        f"| 1. Inicio | {_text(journey['start'])} | ¿Existe una referencia propia, monto, moneda y expiración? |",
        f"| 2. Proceso | {_text(journey['process'])} | ¿Qué sistema externo puede producir el efecto financiero? |",
        f"| 3. Confirmación | {_text(journey['confirm'])} | ¿La evidencia viene de una API, webhook, banco o archivo autoritativo? |",
        f"| 4. Cierre | {_text(journey['close'])} | ¿Ledger, proveedor y banco pueden explicar el mismo resultado? |",
        "",
        "```mermaid",
        "flowchart LR",
        f'  A["Inicio<br/>{html.escape(_text(journey["start"]))}"] --> B["Proceso<br/>{html.escape(_text(journey["process"]))}"]',
        f'  B --> C["Confirmar<br/>{html.escape(_text(journey["confirm"]))}"]',
        f'  C --> D["Cerrar<br/>{html.escape(_text(journey["close"]))}"]',
        '  B -. "sin respuesta" .-> U["UNKNOWN"]',
        '  U -. "consultar; no duplicar" .-> C',
        "```",
        "",
        "## Qué ocurre si falla",
        "",
        f"**Fallo característico:** {_text(journey['failure'])}",
        "",
        "Regla operativa: un timeout no equivale a rechazo. Conserva la operación como `UNKNOWN`, consulta mediante la misma referencia y permite un nuevo intento sólo cuando puedas demostrar que el anterior no produjo efecto.",
        "",
        "Escenarios que debes probar:",
        "",
        *_list(guide["testing"]),
        "",
        "## Cómo llevarlo a una aplicación real",
        "",
        "**Primer incremento de desarrollo:**",
        "",
        *_list(teaching["development_path"]),
        "",
        f"**Evidencia para considerarlo exitoso:** {_text(teaching['success_evidence'])}",
        "",
        f"**Construcción concreta:** {_text(journey['real'])}",
        "",
        "### Lenguaje, API y almacenamiento",
        "",
        "| Capa | Recomendación para este laboratorio | Responsabilidad |",
        "|---|---|---|",
        f"| Frontend | {_text(guide['stack']['frontend'])} | Experiencia; nunca secretos. |",
        f"| Backend | {_text(guide['stack']['backend'])} | Orden, autenticación, idempotencia y estados. |",
        f"| API/canal | {_text(guide['stack']['api'])} | Comunicar con proveedor o rail. |",
        f"| Datos | {_text(guide['stack']['storage'])} | Evidencia, ledger y auditoría. |",
        f"| Operación | {_text(guide['stack']['operations'])} | Despliegue, observabilidad y recuperación. |",
        "",
        f"**Tecnologías del catálogo:** {technologies or 'se definen al elegir proveedor.'}",
        "",
        f"**Operaciones cubiertas:** {cases or 'se concretan con el proveedor.'}",
        "",
        "### Alta, contrato y costo",
        "",
        f"- **Dónde comenzar:** {_text(guide['access'])}",
        f"- **Costo:** {_text(guide['pricing'])}",
        f"- **Decisión:** {_text(guide['decision'])}",
        "",
        "### Variables y callbacks",
        "",
        "| Variable | Obligatoria | Tratamiento | Propósito |",
        "|---|---|---|---|",
        *variable_rows,
        "",
        "**Callbacks previstos:**",
        "",
        *callback_lines,
        "",
        "> GitHub Pages nunca usa estas variables. Configúralas únicamente en localhost, CI protegido o el secret manager del backend.",
        "",
        "### Orden recomendado de implementación",
        "",
        *[f"{index}. {_text(item)}" for index, item in enumerate(guide["implementation"], 1)],
        "",
        "## Seguridad de datos",
        "",
        *_list(guide["security"]),
        "",
        "## Ventajas y desventajas",
        "",
        "### Ventajas",
        "",
        *_list(guide["pros"]),
        "",
        "### Desventajas",
        "",
        *_list(guide["cons"]),
        "",
        "## Checklist antes de LIVE",
        "",
        *[f"- [ ] {_text(item)}" for item in guide["go_live"]],
        "",
        "## Qué demuestra el DEMO y qué no",
        "",
        f"El DEMO permite observar el recorrido de **{title}**, incluyendo éxito, timeout recuperado, evento duplicado y diferencia de conciliación. No contacta al proveedor, no valida credenciales, no certifica cumplimiento y no mueve dinero.",
        "",
        "## Fuentes",
        "",
        *source_lines,
        "",
        "---",
        "",
        f"[Abrir {title} en la tabla web](../END_TO_END_MATRIX.html) · [Configurar localhost](../../LOCALHOST_AND_CONFIGURATION.html)",
        "",
    ]
    return "\n".join(lines)


def render_wrapper(family: dict[str, object]) -> str:
    rail_id = _text(family["id"])
    title = _text(family["title"])
    return "\n".join(
        [
            "---",
            "layout: default",
            f"title: {title}",
            "---",
            f"{{% capture guide %}}{{% include_relative {rail_id}.md %}}{{% endcapture %}}",
            "{{ guide | markdownify }}",
            "",
        ]
    )


def expected_files() -> dict[Path, str]:
    files: dict[Path, str] = {}
    for number, family in enumerate(enriched_catalog(), 1):
        rail_id = _text(family["id"])
        files[TARGET / f"{rail_id}.md"] = render_markdown(family, number)
        files[TARGET / f"{rail_id}.html"] = render_wrapper(family)
    return files


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    files = expected_files()
    stale = [
        path for path, content in files.items() if not path.is_file() or path.read_text(encoding="utf-8") != content
    ]
    if args.check:
        if stale:
            raise SystemExit(f"Individual case guides are stale: {len(stale)} files")
        print("Individual case guides are synchronized: 28 Markdown + 28 HTML")
        return 0
    TARGET.mkdir(parents=True, exist_ok=True)
    for path, content in files.items():
        path.write_text(content, encoding="utf-8")
    print("Generated 28 pedagogical Markdown guides and 28 Pages wrappers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
