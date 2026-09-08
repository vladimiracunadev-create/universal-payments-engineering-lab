#!/usr/bin/env python3
# ruff: noqa: E501
"""Generate the published end-to-end matrix from the executable catalog."""

from __future__ import annotations

import argparse
from pathlib import Path

from payments_lab.catalog import enriched_catalog

TARGET = Path(__file__).resolve().parents[1] / "docs" / "payment-methods" / "END_TO_END_MATRIX.md"


def _cell(value: object) -> str:
    return str(value).replace("|", "&#124;").replace("\n", " ").strip()


def render() -> str:
    lines = [
        "---",
        "layout: default",
        "title: Matriz de los 28 recorridos de pago",
        "description: Cada modalidad de pago explicada desde la necesidad hasta producción.",
        "---",
        "",
        "# Los 28 casos, de comienzo a fin",
        "",
        '<p class="lede">Esta es la vista central del producto. Cada fila responde: <strong>cuándo usar el caso, cómo comienza, quién procesa, cómo se confirma, cómo se cierra, qué hacer si falla y qué construir en un sistema real.</strong></p>',
        "",
        '<div class="reading-path"><span><b>1</b> Necesidad</span><i>→</i><span><b>2</b> Inicio</span><i>→</i><span><b>3</b> Proceso</span><i>→</i><span><b>4</b> Confirmación</span><i>→</i><span><b>5</b> Cierre</span></div>',
        "",
        "> Confirmar responde «¿ocurrió?». Cerrar responde «¿el ledger, el proveedor y el banco explican el mismo dinero?». Un retorno del navegador o una captura nunca bastan.",
        "",
        '<div class="wide-table" markdown="1">',
        "",
        "| # / caso / cuándo | Inicio → proceso | Confirmación → cierre | Si falla | Implementación real |",
        "|---|---|---|---|---|",
    ]
    for number, family in enumerate(enriched_catalog(), 1):
        journey = family["playbook"]["journey"]
        title = _cell(family["title"])
        case = f"**{number}. {title}**<br>{_cell(journey['when'])}"
        beginning = f"**Inicio:** {_cell(journey['start'])}<br>**Proceso:** {_cell(journey['process'])}"
        ending = f"**Confirmar:** {_cell(journey['confirm'])}<br>**Cerrar:** {_cell(journey['close'])}"
        failure = _cell(journey["failure"])
        real = _cell(journey["real"])
        lines.append(f"| {case} | {beginning} | {ending} | {failure} | {real} |")
    lines.extend(
        [
            "",
            "</div>",
            "",
            "## Cómo usar esta tabla",
            "",
            "1. Encuentra la necesidad en la primera columna.",
            "2. Implementa primero el camino feliz de las dos columnas centrales.",
            "3. Antes de liberar, reproduce el fallo descrito y demuestra que no duplica dinero ni evidencia.",
            "4. Abre el [laboratorio en localhost](../LOCALHOST_AND_CONFIGURATION.html) para ejecutar cuatro escenarios.",
            "5. Usa el [casebook detallado](CASEBOOK.html) para revisar alta, seguridad y salida a producción.",
            "",
            "## La arquitectura común",
            "",
            "```mermaid",
            "flowchart LR",
            "  U[Persona o sistema] --> F[Frontend o canal]",
            "  F --> B[Backend: orden e idempotencia]",
            "  B --> P[Proveedor o rail]",
            "  P --> C[API, webhook o archivo]",
            "  C --> L[Ledger]",
            "  L --> R[Conciliación y operación]",
            "```",
            "",
            "La tecnología cambia por fila; las responsabilidades no: el backend decide, la fuente autoritativa confirma y la conciliación demuestra.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail if the generated page is stale.")
    args = parser.parse_args()
    expected = render()
    if args.check:
        if not TARGET.is_file() or TARGET.read_text(encoding="utf-8") != expected:
            raise SystemExit("END_TO_END_MATRIX.md is stale; run scripts/generate_case_matrix.py")
        print("End-to-end matrix is synchronized: 28 cases")
        return 0
    TARGET.write_text(expected, encoding="utf-8")
    print(f"Generated {TARGET} with 28 cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
