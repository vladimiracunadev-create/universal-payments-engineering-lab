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

CASE_SCENARIOS = {
    "cash": "Una cafetería cobra $12.500 en efectivo. Al cierre, el recibo, la caja física y el depósito del día siguiente deben explicar esos mismos $12.500.",
    "paper": "Una empresa recibe un cheque por $1.200.000. La factura sigue pendiente hasta que el banco confirme el cobro; recibir el papel no libera el pedido.",
    "cards": "Una tienda vende un notebook por $649.990. El cliente ve una aprobación inmediata, pero el comercio todavía debe capturar, liquidar y conciliar el abono neto.",
    "chile-webpay": "Una persona compra entradas por $19.990. Tu backend crea la transacción, Transbank procesa la tarjeta y sólo el commit del backend permite confirmar la orden.",
    "chile-oneclick": "Un cliente inscribe su tarjeta una vez y luego paga una compra de $9.990. El comercio usa tbk_user, aplica límites y conserva el consentimiento de inscripción.",
    "chile-khipu": "Un cliente paga una factura de $35.000 desde su banco. Khipu inicia la experiencia y el comercio espera un webhook o consulta del payment ID antes de entregar.",
    "mercado-pago": "Una tienda cobra $24.990 con Checkout. El frontend obtiene un token o redirección; el access token permanece en backend y el webhook se deduplica.",
    "acceptance-devices": "Una caja envía $18.500 a un POS. El terminal procesa la tarjeta y el cierre de lote debe coincidir con el voucher, la caja y el adquirente.",
    "tokenized-wallets": "Una persona paga $32.990 con una wallet. El comercio recibe un token de red y criptograma, nunca el PAN completo, y procesa el cargo mediante su PSP.",
    "stored-value": "Un cliente usa $8.000 de una gift card con saldo $10.000. El sistema reserva, captura y deja $2.000 sin permitir dos consumos simultáneos.",
    "mobile-money": "Una persona envía el equivalente a $15.000 desde su wallet móvil a un comercio. El operador confirma y luego se cuadran saldos y comisión del agente.",
    "qr": "Un restaurante genera un QR por $27.500 con expiración. Escanearlo sólo inicia el pago; el pedido se confirma cuando responde el rail subyacente.",
    "bank-transfer": "Un cliente transfiere $180.000 por una factura. La imagen del comprobante no sirve como confirmación: el abono debe aparecer en la API o cartola bancaria.",
    "ach": "Una empresa envía una nómina de 500 pagos. El operador acepta el lote hoy, pero cada entry puede liquidar o volver días después con su propio código.",
    "direct-debit": "Una academia cobra $29.990 mensuales. Antes del primer débito guarda el mandato; si se revoca o vuelve por fondos, detiene la secuencia según la regla.",
    "instant-payments": "Un cliente paga $42.000 mediante un rail 24/7. La respuesta llega en segundos, pero un timeout sigue necesitando consulta por referencia end-to-end.",
    "payment-initiation": "Un profesional envía un link por una factura de $75.000. La URL expira y sólo conecta la orden con el medio elegido; no demuestra el pago por sí sola.",
    "cash-voucher": "Una tienda crea un voucher por $16.990 pagable en un recaudador. La orden queda pendiente hasta recibir el archivo o evento de la red física.",
    "credit-alternatives": "Una persona compra un teléfono en cuatro cuotas. El financiador evalúa y paga al comercio; el cliente acepta un contrato con costo total y calendario.",
    "carrier-billing": "Un usuario compra contenido por $3.990 cargado a su cuenta móvil. El operador valida línea, límite y OTP, y después reporta el reparto de ingresos.",
    "platform-payments": "Un marketplace cobra $100.000: $85.000 son del vendedor, $10.000 comisión y $5.000 reserva. El subledger debe conservar esa igualdad.",
    "b2b": "Una compañía paga una factura de $8.000.000. Compras valida, tesorería aprueba con doble control, el banco ejecuta y el ERP recibe la remittance.",
    "international": "Una empresa envía USD 10.000 a otro país. Antes fija tasa y fees; después explica cuánto salió, cuánto cobraron corresponsales y cuánto recibió el beneficiario.",
    "high-value": "Tesorería instruye un pago RTGS de alto valor. Dos personas autorizan, el rail puede ponerlo en cola y sólo la finalidad oficial permite cerrarlo.",
    "open-finance": "Una app inicia $55.000 desde la cuenta bancaria del usuario. El consentimiento limita monto y propósito; FAPI y mTLS protegen el intercambio con el banco.",
    "digital-assets": "Un comercio emite una invoice Lightning o dirección Bitcoin por un monto y tiempo definidos. Payment hash o confirmaciones se enlazan con la orden.",
    "machine-payments": "Un cargador de vehículo paga automáticamente por 18 kWh. La identidad del dispositivo, la medición y un presupuesto máximo deben viajar juntos.",
    "agentic-payments": "Un agente reserva un hotel dentro de un presupuesto de $300.000. Si cambia precio, destino o límite, pide aprobación humana antes de ejecutar.",
}


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
        f"[← Volver a la tabla](../END_TO_END_MATRIX.html) · [Ver esta guía .md en GitHub](https://github.com/vladimiracunadev-create/universal-payments-engineering-lab/blob/main/docs/payment-methods/cases/{rail_id}.md)",
        "",
        "## En una frase",
        "",
        f"**Sirve para:** {_text(journey['when'])}",
        "",
        f"**Modelo mental:** {_text(teaching['mental_model'])}",
        "",
        "## Ejemplo concreto",
        "",
        '<div class="case-example-grid">',
        f"<article><span>Situación</span><p>{CASE_SCENARIOS[rail_id]}</p></article>",
        f"<article><span>Detrás de la pantalla</span><p>{_text(journey['start'])} {_text(journey['process'])}</p></article>",
        f"<article><span>Se acepta como pagado cuando</span><p>{_text(journey['confirm'])} Después: {_text(journey['close'])}</p></article>",
        "</div>",
        "",
        "### No confundas estas tres cosas",
        "",
        "| Lo que ocurre | Lo que significa | Lo que NO significa |",
        "|---|---|---|",
        "| El usuario vuelve a tu web | Terminó la experiencia del navegador | Que el dinero esté confirmado |",
        "| El proveedor autoriza/confirma | Existe evidencia operativa del proveedor | Que el abono bancario ya esté conciliado |",
        "| El reporte y el ledger cuadran | Puedes explicar el cierre financiero | Que nunca pueda existir devolución o disputa |",
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
