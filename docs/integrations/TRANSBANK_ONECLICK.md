# Transbank Oneclick Mall: inscripción, cobro y baja

Oneclick permite inscribir una tarjeta mediante Transbank y cobrar posteriormente usando `tbk_user`; el comercio no almacena PAN ni CVV. Requiere producto Oneclick Mall contratado, códigos del mall/tiendas y certificación. Contrato oficial: [referencia Oneclick](https://www.transbankdevelopers.cl/referencia/oneclick).

## 1. Inscripción

```python
from payments_lab.adapters.transbank_oneclick import OneclickMallProvider

oneclick = OneclickMallProvider()
start = oneclick.start_enrollment(
    username="customer-42",  # id opaco, estable, no email/RUT
    email="buyer@example.com",
    response_url="https://shop.example/oneclick/return",
)
# Browser: POST a start['url_webpay'] con TBK_TOKEN=start['token']
finish = oneclick.finish_enrollment(start["token"])
if finish["response_code"] != 0:
    raise RuntimeError("inscripción rechazada")
# Cifrar finish['tbk_user']; mostrar solo card_number enmascarado devuelto.
```

`POST /inscriptions` inicia y `PUT /inscriptions/{token}` finaliza con body `{}`. El retorno no basta: finish determina el resultado. Persista estado `STARTED/ACTIVE/FAILED/DELETED`, token de proceso temporal, username y `tbk_user` cifrado; una restricción única evita inscripciones duplicadas activas.

## 2. Cobro

```python
result = oneclick.authorize({
    "username": "customer-42",
    "tbk_user": decrypted_tbk_user,
    "buy_order": "MALL-20260907-001",
    "details": [{
        "commerce_code": "store-commerce-code",
        "buy_order": "STORE-20260907-001",
        "amount": 19990,
    }],
})
fresh = oneclick.status("MALL-20260907-001")
```

Valide respuesta por cada tienda: response code, autorización, buy order y monto. Un mall con dos detalles necesita asientos y conciliación por comercio hijo. La autorización es server-to-server pero no autoriza cobros arbitrarios: mantenga consentimiento, finalidad, límites y evidencia.

## 3. Reembolso y baja

```python
oneclick.refund(
    "MALL-20260907-001",
    commerce_code="store-commerce-code",
    detail_buy_order="STORE-20260907-001",
    amount=19990,
)
oneclick.delete_enrollment(tbk_user=decrypted_tbk_user, username="customer-42")
```

La baja es `DELETE /inscriptions` con body; debe ser idempotente a nivel del comercio, revocar uso inmediato y conservar evidencia mínima según retención. No borre el historial contable.

## Seguridad de credenciales almacenadas

- `tbk_user` es una credencial de pago: cifrado por registro con clave KMS, acceso solo al servicio de cobro y nunca logs/analytics.
- Separe tokenización/inscripción de autorización; use scopes e identidades distintas si la plataforma lo permite.
- MFA y doble aprobación para cobros administrativos/reembolsos; límites por cliente, día, comercio e importe.
- Consentimiento versionado, descripción del mandato, cancelación accesible y aviso al cliente.
- Detección de account takeover: step-up auth para alta/cambio/baja, device binding y notificación fuera de banda.
- No solicite CVV/PAN. La redirección alojada mantiene esos datos fuera del comercio, pero PCI DSS, privacidad y obligaciones contractuales deben evaluarse formalmente.

## Fallas operativas

Timeout de inscripción: no activar hasta `finish`. Timeout de autorización: estado `UNKNOWN` y consulta por mall buy order antes de otro cargo. Resultado parcial por tiendas: no colapse a booleano; registre cada detalle y compense según contrato. Baja fallida: bloquee localmente nuevos cargos, reintente de forma controlada y escale hasta confirmar en Transbank. Concilie autorización, devolución y abono por mall/store buy order.
