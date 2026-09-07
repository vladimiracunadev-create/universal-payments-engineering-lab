# Mercado Pago Payments API: integración de punta a punta

## Alta y selección del producto

1. Crear cuenta comercial y aplicación en Mercado Pago Developers; completar validación/KYC y habilitaciones del país.
2. Elegir el producto oficial (Checkout Pro, Bricks/API u Orders API) según experiencia y alcance PCI.
3. Usar credenciales de prueba, usuarios de prueba y tarjetas publicadas; después obtener credenciales de producción.
4. Configurar Webhooks, copiar el secreto de firma y registrar HTTPS público.
5. Validar cuotas, medios habilitados, antifraude, retenciones, comisiones, settlement y reembolsos.

El adaptador conserva Payments API (`POST /v1/payments`) para sistemas que usan ese contrato. Nuevas integraciones deben evaluar la [Orders API](https://www.mercadopago.cl/developers/es/reference/online-payments/checkout-api/create-order/post) vigente antes de decidir. Referencia general: [API](https://www.mercadopago.cl/developers/es/reference).

## Crear y recuperar

```python
from payments_lab.adapters.mercadopago import MercadoPagoProvider

mp = MercadoPagoProvider()  # access token y webhook secret solo en backend
payment = mp.create({
    "transaction_amount": "19990",
    "description": "Orden ORD-20260907-001",
    "payment_method_id": "visa",
    "token": token_recibido_del_frontend_oficial,
    "installments": 1,
    "external_reference": "ORD-20260907-001",
    "payer": {"email": "buyer@example.com"},
}, idempotency_key="pay-ORD-20260907-001-v1")

fresh = mp.get(str(payment["id"]))
refund = mp.refund(str(payment["id"]), idempotency_key="refund-ORD-20260907-001-v1")
```

El token de tarjeta debe originarse en el SDK/checkout oficial y no persistirse. `X-Idempotency-Key` es obligatoria en creación y devolución; misma intención + mismo payload reutilizan clave, una intención nueva recibe otra. No use timestamp aleatorio al reintentar.

## Webhook autenticado

```python
mp.verify_webhook(
    data_id=request.args["data.id"],
    request_id=request.headers["x-request-id"],
    signature_header=request.headers["x-signature"],
)
# ACK rápido; consultar GET /v1/payments/{data.id}; aplicar inbox idempotente.
```

Se valida el manifiesto `id:...;request-id:...;ts:...;` con HMAC-SHA256 hexadecimal y ventana anti-replay. No confíe en el JSON notificado como estado final: autentique, deduplique y consulte. Referencia oficial: [Webhooks](https://www.mercadopago.cl/developers/es/docs/your-integrations/notifications/webhooks).

## Estados y cumplimiento de la orden

Mapee `approved` a autorización/captura solo si monto, moneda, comercio y `external_reference` coinciden. `pending`/`in_process` no entregan bienes irreversibles. `rejected`, `cancelled`, `refunded` y `charged_back` son distintos; preserve `status_detail`. Un chargeback inicia un flujo de disputa y ajuste contable, no borra el cargo.

## Fallas y ciberseguridad

- Timeout de POST: conservar la idempotency key y consultar por referencia antes de repetir.
- 429/5xx: backoff con jitter; respete `Retry-After`; circuit breaker solo evita saturación, no decide el pago.
- Token/access token: KMS, mínimo privilegio, rotación y separación por ambiente; nunca frontend/log.
- Webhook: HMAC, timestamp, allowlist lógica por app, rate limit, inbox y respuesta rápida.
- Datos de tarjeta: hosted fields/tokenización; nunca PAN/CVV. Revise alcance PCI DSS con un QSA.
- Fraude: device/session data del SDK oficial, velocity, listas, 3DS cuando corresponda y revisión humana.
- Privacidad: minimice email/documento/dirección, cifre, defina retención y derechos del titular.

## Conciliación y go-live

Cruce `external_reference`, payment id, gross, fee, taxes/withholdings, net, currency, status, settlement date y bank credit. Pruebe aprobación, rechazo, pendiente, duplicado, devolución parcial/total, chargeback, webhook fuera de orden y caída del backend. Producción requiere credenciales reales, URLs aprobadas, alertas, dashboard, runbook y owner.
