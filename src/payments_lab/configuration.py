"""Safe, inspectable environment configuration for local and provider modes."""

from __future__ import annotations

GLOBAL_VARIABLES = (
    {
        "name": "PAYLAB_HOST",
        "required": False,
        "sensitive": False,
        "default": "127.0.0.1",
        "purpose": "Interfaz local. Solo se aceptan direcciones loopback.",
    },
    {
        "name": "PAYLAB_PORT",
        "required": False,
        "sensitive": False,
        "default": "8080",
        "purpose": "Puerto del portal localhost.",
    },
    {
        "name": "PAYLAB_CONFIG_DIR",
        "required": False,
        "sensitive": False,
        "default": "config empaquetada",
        "purpose": "Directorio alternativo para catálogo y guías.",
    },
)

PROVIDER_VARIABLES = {
    "chile-khipu": (
        {
            "name": "KHIPU_API_KEY",
            "required": True,
            "sensitive": True,
            "purpose": "Autenticar la API de Khipu.",
        },
    ),
    "mercado-pago": (
        {
            "name": "MERCADOPAGO_ACCESS_TOKEN",
            "required": True,
            "sensitive": True,
            "purpose": "Autenticar llamadas servidor a servidor.",
        },
    ),
    "chile-webpay": (
        {
            "name": "TRANSBANK_COMMERCE_CODE",
            "required": True,
            "sensitive": False,
            "purpose": "Identificar el comercio Webpay.",
        },
        {
            "name": "TRANSBANK_API_KEY",
            "required": True,
            "sensitive": True,
            "purpose": "Autenticar la API Webpay.",
        },
        {
            "name": "TRANSBANK_BASE_URL",
            "required": True,
            "sensitive": False,
            "purpose": "Separar explícitamente integración y producción.",
        },
    ),
    "chile-oneclick": (
        {
            "name": "TRANSBANK_ONECLICK_COMMERCE_CODE",
            "required": True,
            "sensitive": False,
            "purpose": "Identificar el comercio Oneclick.",
        },
        {
            "name": "TRANSBANK_ONECLICK_API_KEY",
            "required": True,
            "sensitive": True,
            "purpose": "Autenticar la API Oneclick.",
        },
        {
            "name": "TRANSBANK_ONECLICK_BASE_URL",
            "required": True,
            "sensitive": False,
            "purpose": "Separar explícitamente integración y producción.",
        },
    ),
}

CALLBACKS = {
    "chile-khipu": ("/webhooks/khipu", "/payments/khipu/return"),
    "mercado-pago": ("/webhooks/mercado-pago", "/payments/mercado-pago/return"),
    "chile-webpay": ("/payments/webpay/return",),
    "chile-oneclick": ("/payments/oneclick/return",),
}


def configuration_for(rail_id: str) -> dict[str, object]:
    provider_variables = PROVIDER_VARIABLES.get(rail_id, ())
    return {
        "mode": "DEMO",
        "global_variables": [dict(item) for item in GLOBAL_VARIABLES],
        "provider_variables": [dict(item) for item in provider_variables],
        "callbacks": list(CALLBACKS.get(rail_id, ())),
        "provider_note": (
            "Estas variables habilitan el adapter; todavía debes verificar sandbox, contrato y permisos."
            if provider_variables
            else (
                "Esta familia es conceptual en el adapter actual. "
                "Elige proveedor y país antes de definir secretos o endpoints."
            )
        ),
        "github_pages": (
            "Solo documentación estática: no ejecuta Python, no recibe webhooks y nunca debe contener secretos."
        ),
    }
