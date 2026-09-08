# ruff: noqa: E501
"""Actionable web-integration playbooks for every payment family."""

from __future__ import annotations

from copy import deepcopy

from .configuration import configuration_for
from .teaching import teaching_for

WEB_STACK = {
    "frontend": "TypeScript + HTML/CSS. El navegador presenta el checkout y recibe el retorno; no guarda secretos.",
    "backend": "Python 3.11+ con FastAPI para este laboratorio. Node.js/TypeScript, Java, .NET o Go son equivalentes si el equipo los opera mejor.",
    "api": "HTTPS REST/JSON entre tu backend y el proveedor; webhooks HTTPS para cambios asíncronos.",
    "storage": "PostgreSQL para intents, eventos, idempotencia y ledger; Redis solo para cache/locks, nunca como libro contable.",
    "operations": "Docker, gestor de secretos, logs estructurados, métricas, alertas y job de conciliación.",
}

MANUAL_STACK = {
    "frontend": "Interfaz web administrativa para registrar recepción, custodia y diferencias; no inicia una red de pagos.",
    "backend": "Python/FastAPI o el stack transaccional existente del comercio.",
    "api": "API interna REST/JSON y, cuando exista, archivo/API de banco o red externa.",
    "storage": "PostgreSQL con auditoría inmutable y ledger de doble entrada.",
    "operations": "Control de acceso por rol, doble aprobación, respaldos y conciliación diaria.",
}

SECURITY = [
    "El monto, moneda, beneficiario y referencia nacen o se validan en el backend; nunca se confía en el navegador.",
    "Secretos en un gestor de secretos, rotación y mínimo privilegio; jamás en JavaScript, Git o logs.",
    "TLS, validación de firma/origen de webhooks, deduplicación persistente e idempotency key por operación.",
    "Minimizar datos: almacenar tokens y referencias del proveedor, no PAN, CVV, claves ni credenciales bancarias.",
    "Cifrado en reposo, control de acceso, trazabilidad y política de retención/borrado.",
]

FAILURES = [
    "Timeout después de enviar: marcar UNKNOWN, consultar por referencia y no crear otro cobro a ciegas.",
    "Webhook repetido o fuera de orden: autenticar, persistir primero y aplicar una sola vez por event_id.",
    "Rechazo: conservar código técnico, mostrar un mensaje seguro y permitir otra acción sin duplicar la anterior.",
    "Diferencia de monto/estado: abrir excepción; no corregir silenciosamente el ledger.",
    "Caída prolongada: circuit breaker, reintentos con backoff solo en operaciones seguras y conciliación posterior.",
]

TESTING = [
    "Happy path con montos mínimos, normales y límites documentados.",
    "Rechazo, cancelación del usuario, expiración y retorno del navegador manipulado.",
    "Timeout antes y después de enviar, webhook tardío, duplicado y fuera de orden.",
    "Refund total/parcial cuando aplique y conciliación con una diferencia intencional.",
    "Prueba end-to-end en sandbox/certificación con credenciales separadas; producción solo después de aprobar el checklist.",
]

GO_LIVE = [
    "Contrato y cuenta comercial aprobados; costos y plazos confirmados directamente con el proveedor.",
    "Credenciales productivas separadas, callbacks HTTPS públicos, dominios permitidos y rotación documentada.",
    "Alertas, runbook, soporte, refund/disputa y conciliación ensayados con responsables definidos.",
    "Piloto con límites y monitoreo reforzado; rollback que detiene nuevas operaciones sin perder evidencia.",
]

SOURCES = {
    "transbank": [
        {"title": "Transbank · Cómo empezar", "url": "https://www.transbankdevelopers.cl/documentacion/como_empezar"},
        {"title": "Transbank · API Webpay", "url": "https://www.transbankdevelopers.cl/referencia/webpay"},
    ],
    "oneclick": [
        {"title": "Transbank · API Oneclick", "url": "https://www.transbankdevelopers.cl/referencia/oneclick"},
        {"title": "Transbank · Cómo empezar", "url": "https://www.transbankdevelopers.cl/documentacion/como_empezar"},
    ],
    "khipu": [
        {"title": "Khipu · Guía de implementación", "url": "https://www.khipu.com/en-us/page/guia-de-implementacion"},
        {
            "title": "Khipu · Payment API",
            "url": "https://docs.khipu.com/en/payment-solutions/instant-payments/payment-api",
        },
    ],
    "mercadopago": [
        {
            "title": "Mercado Pago · Primeros pasos",
            "url": "https://www.mercadopago.cl/developers/es/docs/getting-started",
        },
        {
            "title": "Mercado Pago · Payments API",
            "url": "https://www.mercadopago.cl/developers/es/docs/checkout-api-payments/overview",
        },
    ],
    "cards": [
        {"title": "PCI SSC · PCI DSS", "url": "https://www.pcisecuritystandards.org/standards/pci-dss/"},
        {"title": "EMVCo · Especificaciones", "url": "https://www.emvco.com/emv-technologies/"},
    ],
    "bank": [
        {"title": "ISO · ISO 20022", "url": "https://www.iso20022.org/"},
        {"title": "BIS CPMI · sistemas de pago", "url": "https://www.bis.org/cpmi/index.htm"},
    ],
    "open": [
        {"title": "OpenID Foundation · FAPI", "url": "https://openid.net/wg/fapi/"},
        {"title": "IETF · OAuth 2.0 Security BCP", "url": "https://www.rfc-editor.org/rfc/rfc9700"},
    ],
    "digital": [
        {"title": "Bitcoin Developer Guides", "url": "https://developer.bitcoin.org/devguide/"},
        {"title": "Lightning specifications", "url": "https://github.com/lightning/bolts"},
    ],
    "general": [
        {
            "title": "OWASP · Application Security Verification Standard",
            "url": "https://owasp.org/www-project-application-security-verification-standard/",
        },
        {"title": "PCI SSC · PCI DSS", "url": "https://www.pcisecuritystandards.org/standards/pci-dss/"},
    ],
}

PROVIDER = {
    "chile-webpay": {
        "access": "Crear la integración con credenciales de integración de Transbank; para LIVE, contratar Webpay y completar puesta en producción.",
        "pricing": "El laboratorio cuesta $0. La tarifa real depende del contrato del comercio: consultar la oferta vigente de Transbank antes de decidir.",
        "api": "REST Webpay Plus: create → redirección alojada → commit en backend → status/refund.",
        "pros": ["Checkout alojado y reconocimiento local en Chile.", "El comercio no captura datos de tarjeta."],
        "cons": [
            "Redirección fuera de tu sitio.",
            "Contrato, validación productiva y dependencia operativa del proveedor.",
        ],
        "sources": "transbank",
    },
    "chile-oneclick": {
        "access": "Solicitar/contratar Oneclick Mall y usar primero sus credenciales y tarjetas de integración.",
        "pricing": "El DEMO cuesta $0; afiliación y transacciones reales se cotizan/contratan con Transbank.",
        "api": "REST Oneclick: start/finish de inscripción; authorize/status/refund para cobros; delete para baja.",
        "pros": ["Cobros posteriores sin volver a ingresar tarjeta.", "Token alojado por Transbank."],
        "cons": ["Mayor riesgo por cobro recurrente.", "Exige consentimiento, baja y protección estricta de tbk_user."],
        "sources": "oneclick",
    },
    "chile-khipu": {
        "access": "Registrarse como cobrador en Khipu, crear llaves/API y activar el ambiente indicado por el proveedor.",
        "pricing": "El DEMO cuesta $0. Comisiones y liquidación varían por servicio/contrato; confirmar la tabla vigente con Khipu.",
        "api": "REST de pagos instantáneos: autenticar, crear pago, redirigir/abrir experiencia, consultar y recibir webhook.",
        "pros": ["Cuenta a cuenta y sin capturar claves bancarias.", "Confirmación asíncrona consultable."],
        "cons": ["Cobertura depende de bancos/producto.", "La experiencia puede salir del comercio."],
        "sources": "khipu",
    },
    "mercado-pago": {
        "access": "Crear cuenta de vendedor y una aplicación en Mercado Pago Developers; separar credenciales de prueba y producción.",
        "pricing": "El DEMO cuesta $0. La comisión real cambia por país, producto y plazo de disponibilidad: usar el enlace de costos de la cuenta.",
        "api": "REST/JSON Payments API existente; evaluar Orders API para una integración nueva. Tokenización en frontend y cobro en backend.",
        "pros": ["Varios medios y SDKs.", "Sandbox, webhooks, consulta y refunds."],
        "cons": ["Superficie API amplia y reglas por país.", "La disponibilidad del dinero afecta la tarifa."],
        "sources": "mercadopago",
    },
}

CARD_IDS = {"cards", "acceptance-devices", "tokenized-wallets", "qr", "stored-value"}
BANK_IDS = {"paper", "bank-transfer", "ach", "direct-debit", "instant-payments", "b2b", "international", "high-value"}
OPEN_IDS = {"open-finance"}
DIGITAL_IDS = {"digital-assets", "machine-payments", "agentic-payments"}
MANUAL_IDS = {"cash", "paper", "b2b", "high-value"}


def _source_key(rail_id: str) -> str:
    if rail_id in PROVIDER:
        return str(PROVIDER[rail_id]["sources"])
    if rail_id in CARD_IDS:
        return "cards"
    if rail_id in BANK_IDS:
        return "bank"
    if rail_id in OPEN_IDS:
        return "open"
    if rail_id in DIGITAL_IDS:
        return "digital"
    return "general"


def build_playbook(rail_id: str, title: str) -> dict[str, object]:
    """Return a complete decision and implementation guide for one family."""
    specific = PROVIDER.get(rail_id, {})
    stack = deepcopy(MANUAL_STACK if rail_id in MANUAL_IDS else WEB_STACK)
    if api := specific.get("api"):
        stack["api"] = str(api)
    access = str(
        specific.get(
            "access",
            "Elegir un proveedor regulado que ofrezca esta modalidad en tu país, abrir cuenta comercial, verificar la empresa y solicitar sandbox.",
        )
    )
    pricing = str(
        specific.get(
            "pricing",
            "El DEMO cuesta $0. Precio, impuestos, reservas y plazo de liquidación dependen del proveedor, país y volumen; pedir cotización vigente.",
        )
    )
    return {
        "teaching": teaching_for(rail_id),
        "configuration": configuration_for(rail_id),
        "decision": f"Usa {title} solo si su cobertura, experiencia, reversibilidad y conciliación resuelven tu caso; compara al menos dos proveedores antes de LIVE.",
        "stack": stack,
        "access": access,
        "pricing": pricing,
        "implementation": [
            "Crear una orden/intención propia en el backend y fijar monto, moneda, comercio y expiración.",
            "Enviar al proveedor desde el backend con credencial secreta e idempotency key; persistir referencia y request seguro.",
            "Entregar al frontend solo el token, QR o URL de redirección de alcance mínimo.",
            "Tratar el retorno del navegador como experiencia, no como prueba de pago; confirmar por API/webhook.",
            "Validar y deduplicar el webhook, aplicar una máquina de estados monotónica y contabilizar una sola vez.",
            "Consultar operaciones UNKNOWN y conciliar diariamente contra proveedor/banco; gestionar refunds y disputas.",
        ],
        "testing": deepcopy(TESTING),
        "pros": list(
            specific.get("pros", ["Amplía las opciones de pago y desacopla el comercio de la red subyacente."])
        ),
        "cons": list(
            specific.get("cons", ["Disponibilidad, costos y reglas dependen del proveedor y la regulación local."])
        ),
        "security": deepcopy(SECURITY),
        "failures": deepcopy(FAILURES),
        "go_live": deepcopy(GO_LIVE),
        "sources": deepcopy(SOURCES[_source_key(rail_id)]),
    }
