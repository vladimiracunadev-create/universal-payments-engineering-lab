"""Deterministic, no-money payment journeys for every catalog family."""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation

from .catalog import enriched_catalog
from .core.ledger import Entry, Ledger
from .core.reconciliation import PaymentRecord, reconcile

SCENARIOS = {
    "success": "Recorrido completo sin fallos.",
    "timeout-recovered": "La respuesta se pierde; una consulta recupera el resultado sin cobrar dos veces.",
    "duplicate-event": "El mismo evento llega dos veces y el segundo se ignora.",
    "reconciliation-mismatch": "El proveedor informa un monto distinto y se abre una excepción.",
}

TRANSFER_RAILS = {
    "chile-khipu",
    "bank-transfer",
    "ach",
    "direct-debit",
    "instant-payments",
    "open-finance",
    "international",
    "high-value",
}
CARD_RAILS = {
    "cards",
    "chile-webpay",
    "chile-oneclick",
    "mercado-pago",
    "tokenized-wallets",
    "acceptance-devices",
}
VALUE_RAILS = {"cash", "paper", "stored-value", "mobile-money", "cash-voucher", "digital-assets"}
MULTIPARTY_RAILS = {"platform-payments", "b2b", "machine-payments", "agentic-payments"}


@dataclass(frozen=True)
class DemoStep:
    number: int
    phase: str
    actor: str
    state: str
    explanation: str
    evidence: str
    technologies: tuple[str, ...] = ()


def _reference(rail_id: str, scenario: str, amount: Decimal, currency: str) -> str:
    raw = f"{rail_id}:{scenario}:{amount}:{currency}".encode()
    return f"DEMO-{hashlib.sha256(raw).hexdigest()[:12].upper()}"


def _family(rail_id: str) -> dict[str, object]:
    for family in enriched_catalog():
        if family["id"] == rail_id:
            return family
    raise KeyError(f"unknown payment family: {rail_id}")


def _template(rail_id: str) -> tuple[tuple[str, str, str, str], ...]:
    if rail_id in CARD_RAILS:
        return (
            ("Intent", "Comercio", "CREATED", "El comercio fija orden, monto y moneda."),
            (
                "Autenticación",
                "Pagador / emisor",
                "REQUIRES_AUTHENTICATION",
                "El instrumento se autentica sin exponer secretos al comercio.",
            ),
            (
                "Autorización",
                "Proveedor",
                "AUTHORIZED",
                "El proveedor aprueba o rechaza; todavía no demuestra abono bancario.",
            ),
            (
                "Captura",
                "Comercio / adquirente",
                "CAPTURED",
                "El cobro se confirma y se registra como efecto financiero.",
            ),
            ("Liquidación", "Adquirente / banco", "SETTLED", "El proveedor calcula neto, comisiones y fecha de abono."),
        )
    if rail_id in TRANSFER_RAILS:
        return (
            ("Intent", "Comercio", "CREATED", "Se crea una referencia estable con monto y beneficiario."),
            ("Consentimiento", "Pagador", "REQUIRES_AUTHENTICATION", "El pagador autoriza en el banco o proveedor."),
            (
                "Ejecución",
                "Banco / rail",
                "PROCESSING",
                "El rail acepta la instrucción; el resultado puede seguir pendiente.",
            ),
            (
                "Confirmación",
                "Banco / proveedor",
                "CAPTURED",
                "Una consulta o evento autoritativo confirma el movimiento.",
            ),
            (
                "Liquidación",
                "Banco receptor",
                "SETTLED",
                "Los fondos llegan al beneficiario según la finalidad del rail.",
            ),
        )
    if rail_id in MULTIPARTY_RAILS:
        return (
            ("Mandato", "Plataforma", "CREATED", "Se valida quién puede pagar, cuánto y a favor de quién."),
            ("Política", "Motor de reglas", "PROCESSING", "Límites, riesgo y aprobaciones determinan si se continúa."),
            ("Movimiento", "Proveedor", "CAPTURED", "Se ejecuta un único efecto externo con referencia estable."),
            ("Distribución", "Ledger", "CAPTURED", "El bruto se separa en comercio, comisión, reserva o payout."),
            ("Liquidación", "Tesorería", "SETTLED", "Los saldos se pagan y se contrastan con el banco."),
        )
    if rail_id == "credit-alternatives":
        return (
            ("Solicitud", "Cliente", "CREATED", "Se solicita financiación con importe y calendario claros."),
            ("Evaluación", "Financiador", "PROCESSING", "Riesgo, identidad y capacidad de pago se evalúan."),
            ("Contrato", "Cliente / financiador", "AUTHORIZED", "El cliente acepta costo, cuotas y condiciones."),
            ("Pago al comercio", "Financiador", "SETTLED", "El comercio recibe el neto según el acuerdo."),
            ("Recaudación", "Servicer", "SETTLED", "Las cuotas se cobran y concilian durante su ciclo."),
        )
    if rail_id in VALUE_RAILS:
        return (
            ("Orden", "Comercio", "CREATED", "Se emite una orden o referencia por un importe exacto."),
            ("Presentación", "Pagador", "PROCESSING", "El pagador presenta o entrega el instrumento de valor."),
            ("Validación", "Aceptador", "AUTHORIZED", "Se verifica autenticidad, vigencia y correspondencia."),
            ("Recepción", "Comercio", "CAPTURED", "El comercio registra la recepción sin ocultar diferencias."),
            ("Depósito", "Tesorería / proveedor", "SETTLED", "El valor se deposita o consolida para su liquidación."),
        )
    return (
        ("Intent", "Comercio", "CREATED", "Se crea la intención con referencia, monto, moneda y propósito."),
        ("Validación", "Plataforma", "PROCESSING", "Se comprueban contrato, identidad, límites y datos mínimos."),
        ("Ejecución", "Proveedor", "CAPTURED", "El proveedor procesa un único efecto financiero."),
        ("Notificación", "Proveedor", "CAPTURED", "El estado se recupera por evento autenticado o consulta."),
        ("Liquidación", "Proveedor / banco", "SETTLED", "El movimiento final se contrasta con la evidencia externa."),
    )


def run_demo(
    rail_id: str,
    *,
    scenario: str = "success",
    amount: str = "19990",
    currency: str = "CLP",
) -> dict[str, object]:
    if scenario not in SCENARIOS:
        raise ValueError(f"unknown demo scenario: {scenario}")
    family = _family(rail_id)
    try:
        decimal_amount = Decimal(amount)
    except InvalidOperation as exc:
        raise ValueError("amount must be a valid decimal string") from exc
    if not decimal_amount.is_finite() or decimal_amount <= 0:
        raise ValueError("amount must be positive and finite")
    if not currency.isalpha() or len(currency) != 3:
        raise ValueError("currency must be a three-letter code")
    currency = currency.upper()
    reference = _reference(rail_id, scenario, decimal_amount, currency)
    technologies = tuple(str(item) for item in family.get("technologies", []))
    steps = []
    step_number = 1
    for template_index, (phase, actor, state, explanation) in enumerate(_template(rail_id), start=1):
        if scenario == "timeout-recovered" and template_index == 3:
            steps.append(
                DemoStep(
                    step_number,
                    "Timeout",
                    actor,
                    "UNKNOWN",
                    "La respuesta se perdió. No se reintenta el efecto; se consulta por la misma referencia.",
                    f"timeout:{reference}",
                    technologies[:2],
                )
            )
            step_number += 1
            steps.append(
                DemoStep(
                    step_number,
                    "Recuperación",
                    "Recovery worker",
                    state,
                    "La consulta autoritativa confirma el resultado original antes de continuar.",
                    f"query:{reference}",
                    technologies[:2],
                )
            )
            step_number += 1
            continue
        steps.append(
            DemoStep(
                step_number,
                phase,
                actor,
                state,
                explanation,
                f"event:{reference}:{template_index}",
                technologies[:2],
            )
        )
        step_number += 1
    event_delivery = {"event_id": f"evt-{reference}", "accepted": 1, "ignored": 0}
    if scenario == "duplicate-event":
        seen_event_ids = {event_delivery["event_id"]}
        event_delivery["ignored"] = int(event_delivery["event_id"] in seen_event_ids)
        steps.append(
            DemoStep(
                len(steps) + 1,
                "Duplicado",
                "Webhook inbox",
                "SETTLED",
                "El event ID ya existe; se confirma recepción sin repetir estado ni ledger.",
                f"duplicate-ignored:{reference}",
                technologies[:2],
            )
        )

    ledger = Ledger()
    journal = ledger.post(
        reference,
        [Entry("cash/provider", -decimal_amount, currency), Entry("merchant/receivable", decimal_amount, currency)],
    )
    remote_amount = decimal_amount + Decimal("1") if scenario == "reconciliation-mismatch" else decimal_amount
    differences = reconcile(
        [PaymentRecord(reference, decimal_amount, currency)],
        [PaymentRecord(reference, remote_amount, currency)],
    )
    final_state = "RECONCILIATION_EXCEPTION" if differences else "RECONCILED"
    steps.append(
        DemoStep(
            len(steps) + 1,
            "Conciliación",
            "Operaciones",
            final_state,
            "Las referencias, monto y moneda coinciden."
            if not differences
            else "La diferencia permanece visible y requiere resolución; no se altera el ledger.",
            f"reconciliation:{reference}",
            ("reconciliation", "double-entry-ledger"),
        )
    )
    return {
        "mode": "DEMO",
        "moves_money": False,
        "reference": reference,
        "rail": family,
        "scenario": scenario,
        "scenario_explanation": SCENARIOS[scenario],
        "amount": format(decimal_amount, "f"),
        "currency": currency,
        "started_at": datetime.now(UTC).isoformat(),
        "final_state": final_state,
        "steps": [asdict(step) for step in steps],
        "journal": {
            "reference": journal.reference,
            "entries": [
                {"account": entry.account, "amount": format(entry.amount, "f"), "currency": entry.currency}
                for entry in journal.entries
            ],
        },
        "differences": [asdict(item) for item in differences],
        "event_delivery": event_delivery,
        "disclaimer": "Simulación determinista: no contacta proveedores, no usa credenciales y no mueve dinero.",
    }
