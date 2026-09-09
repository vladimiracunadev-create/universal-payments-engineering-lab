#!/usr/bin/env python3
# ruff: noqa: E501
"""Generate the published end-to-end matrix from the executable catalog."""

from __future__ import annotations

import argparse
import html
from pathlib import Path

from payments_lab.catalog import enriched_catalog

TARGET = Path(__file__).resolve().parents[1] / "docs" / "payment-methods" / "END_TO_END_MATRIX.md"


def _cell(value: object) -> str:
    return html.escape(str(value).replace("\n", " ").strip())


def render() -> str:
    lines = [
        "# Tabla pedagógica: los 28 casos de comienzo a fin",
        "",
        '<p class="lede">No necesitas conocer términos de pagos. Busca una necesidad y lee su fila de izquierda a derecha. Cada columna es una pregunta concreta que una integración real debe responder.</p>',
        "",
        '<div class="reading-path"><span><b>1</b> Necesidad</span><i>→</i><span><b>2</b> Inicio</span><i>→</i><span><b>3</b> Proceso</span><i>→</i><span><b>4</b> Confirmación</span><i>→</i><span><b>5</b> Cierre</span></div>',
        "",
        '<section class="matrix-example"><p class="kicker">Ejemplo en 30 segundos</p><h2>Una compra de $19.990 con Webpay</h2><ol><li><b>Inicio:</b> tu backend crea una orden y una referencia.</li><li><b>Proceso:</b> Transbank presenta la pantalla y procesa la tarjeta.</li><li><b>Confirmar:</b> tu backend ejecuta <code>commit</code>; volver al navegador no basta.</li><li><b>Cerrar:</b> el ledger registra una sola operación y después se concilia con el reporte.</li><li><b>Si hay timeout:</b> queda <code>UNKNOWN</code> y se consulta; no se cobra otra vez a ciegas.</li></ol></section>',
        "",
        "## Aquí comienza la tabla: 28 casos",
        "",
        "Escribe una palabra para reducir las filas. Por ejemplo: **presencial**, **recurrente**, **Chile**, **banco** o **agente**.",
        "",
        '<label class="docs-filter" for="docs-case-filter"><span>Buscar un caso</span><input id="docs-case-filter" type="search" placeholder="Ej.: Webpay, recurrente, banco"></label>',
        '<p id="docs-case-count" class="docs-case-count">Mostrando 28 de 28 casos.</p>',
        "",
        '<div class="wide-table">',
        '<table id="docs-case-table" class="journey-table">',
        "<thead><tr>",
        '<th scope="col">#</th>',
        '<th scope="col">Caso</th>',
        '<th scope="col">¿Para qué sirve?</th>',
        '<th scope="col">1 · Inicio</th>',
        '<th scope="col">2 · Proceso</th>',
        '<th scope="col">3 · Confirmar</th>',
        '<th scope="col">4 · Cerrar</th>',
        '<th scope="col">Si falla</th>',
        '<th scope="col">Para hacerlo real</th>',
        "</tr></thead>",
        "<tbody>",
    ]
    for number, family in enumerate(enriched_catalog(), 1):
        journey = family["playbook"]["journey"]
        title = _cell(family["title"])
        rail_id = _cell(family["id"])
        search_text = _cell(" ".join([str(family["title"]), *journey.values()])).lower()
        lines.extend(
            [
                f'<tr data-search="{search_text}">',
                f'<td class="case-number">{number:02d}</td>',
                f'<th scope="row"><a href="https://vladimiracunadev-create.github.io/universal-payments-engineering-lab/payment-methods/cases/{rail_id}.html">{title}</a><small><a href="https://github.com/vladimiracunadev-create/universal-payments-engineering-lab/blob/main/docs/payment-methods/cases/{rail_id}.md">fuente MD</a> · <a href="https://vladimiracunadev-create.github.io/universal-payments-engineering-lab/downloads/universal-payments-engineering-lab.pdf#nameddest=case-{rail_id}">PDF</a></small></th>',
                f"<td>{_cell(journey['when'])}</td>",
                f"<td>{_cell(journey['start'])}</td>",
                f"<td>{_cell(journey['process'])}</td>",
                f"<td>{_cell(journey['confirm'])}</td>",
                f"<td>{_cell(journey['close'])}</td>",
                f'<td class="failure-cell">{_cell(journey["failure"])}</td>',
                f'<td class="real-cell">{_cell(journey["real"])}</td>',
                "</tr>",
            ]
        )
    lines.extend(
        [
            "</tbody>",
            "</table>",
            "</div>",
            "",
            "## Qué debes poder explicar después de elegir una fila",
            "",
            "1. **Quién crea la referencia:** normalmente tu backend.",
            "2. **Quién tiene autoridad para confirmar:** API, webhook, banco, operador o archivo; nunca una captura.",
            "3. **Qué pasa si no sabes el resultado:** conservar `UNKNOWN`, consultar y evitar un segundo efecto.",
            "4. **Cómo pruebas el dinero:** ledger balanceado y conciliación contra la fuente externa.",
            "5. **Qué falta para LIVE:** contrato, credenciales separadas, seguridad, operación y regulación.",
            "",
            "Después abre el [laboratorio en localhost](../LOCALHOST_AND_CONFIGURATION.md) para ejecutar cuatro fallos, o el [casebook detallado](CASEBOOK.md) para revisar cada modalidad.",
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
            "**En una frase:** la tecnología cambia por fila; las responsabilidades no. El backend decide, una fuente autoritativa confirma y la conciliación demuestra.",
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
