# Khipu Instant Payments v3: integración de punta a punta

## Cuándo usarlo

Pago cuenta-a-cuenta iniciado por el pagador. El comercio crea una orden Khipu, redirige al usuario y confirma el resultado servidor-a-servidor. No capture credenciales bancarias: esa interacción pertenece a Khipu/banco.

## Alta y ambientes

1. Crear la cuenta de cobro Khipu, completar identidad y asociar/validar la cuenta bancaria de abono.
2. Obtener credenciales de desarrollo y ejecutar el flujo completo sin usar datos ajenos.
3. Solicitar/habilitar producción y guardar la API key en el secret manager del backend.
4. Configurar URL de notificación HTTPS y secreto de webhook; separar completamente desarrollo/producción.
5. Acordar operación: monedas, límites, devolución, soporte, abono y archivo/reporte de conciliación.

Guías oficiales: [implementación](https://www.khipu.com/en-us/page/guia-de-implementacion), [autenticación](https://docs.khipu.com/en/payment-solutions/instant-payments/payment-auth) y [Payments API](https://docs.khipu.com/en/payment-solutions/instant-payments/payment-api).

## Crear, redirigir y confirmar

```python
from payments_lab.adapters.khipu import KhipuProvider

khipu = KhipuProvider()  # KHIPU_API_KEY + KHIPU_WEBHOOK_SECRET
created = khipu.create({
    "amount": "19990",
    "currency": "CLP",
    "subject": "Orden ORD-20260907-001",
    "transaction_id": "ORD-20260907-001",
    "return_url": "https://shop.example/pagos/khipu/retorno",
    "cancel_url": "https://shop.example/pagos/khipu/cancelado",
    "notify_url": "https://api.example/webhooks/khipu",
    "notify_api_version": "3.0",
})
# Persistir payment_id + URL; redirigir. Nunca interpretar return_url como pago.
status = khipu.get(created["payment_id"])
```

La creación oficial es `POST /v3/payments`; la consulta es `GET /v3/payments/{id}`. El código expone también `GET /v3/banks` y `DELETE` del pago. No se publican aquí rutas de anulación/devolución no verificadas contra el contrato v3 actual: agréguelas únicamente desde el OpenAPI habilitado a su comercio.

## Webhook autenticado

Lea el body como bytes una sola vez. Verifique `x-khipu-signature` antes de parsearlo:

```python
raw = request.get_data(cache=False)
khipu.verify_webhook(raw, request.headers["x-khipu-signature"])
# Después: JSON, inbox con unique(provider,event/payment id), transición y 200.
```

Khipu firma `timestamp.raw_body` con HMAC-SHA256 y Base64. La implementación usa comparación de tiempo constante y ventana de cinco minutos. Guía oficial: [payment webhook](https://docs.khipu.com/en/payment-solutions/instant-payments/payment-webhook).

## Fallas y recuperación

- Si crear vence por timeout, busque por su `transaction_id`/registro operativo antes de recrear. Mantenga `UNKNOWN` mientras no exista evidencia.
- Si el webhook no llega, consulte status con backoff y jitter. Khipu espera una respuesta rápida; desacople el procesamiento mediante inbox.
- Si llega duplicado, el índice único impide aplicar dos veces el mismo efecto.
- Si retorna el navegador pero status no es pagado, muestre “procesando” y continúe la recuperación.
- Concilie diariamente `transaction_id`, `payment_id`, monto, moneda, estado, fecha de pago, abono neto y comisión.

## Ciberseguridad específica

La API key tiene privilegios amplios: guárdela en KMS/Vault, restrinja lectura a la identidad del workload, rote ante exposición y alerte por 401/403. El webhook puede contener documento/identificador y datos bancarios del pagador: minimice, cifre, aplique acceso por rol y retención legal. Nunca registre el body completo. Aplique rate limit/WAF al endpoint sin bloquear reintentos legítimos.

## Go-live

Cuenta y banco validados; callbacks HTTPS; secreto rotado; casos pagado/rechazado/cancelado/timeout/duplicado; consulta de rescate; fulfillment condicionado al estado definitivo; reembolso validado con soporte; conciliación y alertas; responsables y teléfonos de escalamiento.
