# 🧪 Laboratorio de certificación

Usa exclusivamente cuentas, credenciales y ambientes oficiales autorizados. Antes de ejecutar, revisa la documentación vigente: paths, headers, campos y estados pueden cambiar.

## Gate de entrada

- contrato `LAB-CONTRACT.yaml` completado;
- owner y ventana de prueba;
- secretos fuera de Git;
- monto/datos sintéticos autorizados;
- mecanismo de status y refund/reversal conocido;
- webhooks autenticados o declarados pendientes;
- evidencia privada y sanitización preparada.

## CLI disponible

### Khipu

```bash
export KHIPU_API_KEY='...'
python scripts/paylab.py khipu-create \
  --subject 'Laboratorio autorizado' --amount 1000 --currency CLP \
  --return-url 'https://example.invalid/payments/return'
python scripts/paylab.py khipu-get PROVIDER_PAYMENT_ID
```

### Mercado Pago

El payload permanece explícito porque los campos varían por medio y país.

```bash
export MERCADOPAGO_ACCESS_TOKEN='...'
python scripts/paylab.py mp-create --payload payment.json --idempotency-key lab-001
python scripts/paylab.py mp-get PROVIDER_PAYMENT_ID
python scripts/paylab.py mp-refund PROVIDER_PAYMENT_ID --idempotency-key refund-001
```

### Transbank Webpay Plus

```bash
export TRANSBANK_COMMERCE_CODE='...'
export TRANSBANK_API_KEY='...'
export TRANSBANK_BASE_URL='ENDPOINT_OFICIAL_DEL_AMBIENTE'
python scripts/paylab.py tbk-create \
  --buy-order O-100 --session-id S-100 --amount 1000 \
  --return-url 'https://example.invalid/webpay/commit'
python scripts/paylab.py tbk-commit TOKEN
python scripts/paylab.py tbk-status TOKEN
```

> [!CAUTION]
> Los argumentos `--amount` del CLI son una interfaz demostrativa actual y usan `float`; los adaptadores envían el valor recibido. Antes de producción se debe migrar a decimal/unidades menores y validar moneda/exponente.

## Gate de salida

Crear, autenticar/confirmar, consultar, manejar rechazo y timeout, ejecutar reversa/refund, verificar evento si aplica, reconciliar y demostrar que no hay secretos/datos sensibles en evidencia. Si falta un punto, registrar `PARTIAL`, no `PASSED`.
