# 🔌 Adaptadores incluidos

## Contrato y límites

Los adaptadores son transportes HTTP pequeños para estudiar el contrato. No incluyen persistencia, verificación de webhook, retries, telemetría, tokenización de tarjeta ni certificación. Las pruebas usan un transporte falso y nunca llaman a una API externa.

| Adaptador | Implementado | Pendiente antes de operación real | Fuente oficial |
|---|---|---|---|
| Khipu Instant Payments | create, get, delete, void, refund | confirmar base URL/auth del contrato habilitado, estados, notificación, idempotencia y conciliación | [API 3.0](https://docs.khipu.com/en/payment-solutions/instant-payments/description) |
| Mercado Pago Payments | create, get, refund | estado completo, webhook firmado, rate limit, settlement y payload por producto/país | [Developers Chile](https://www.mercadopago.cl/developers/es/docs) |
| Transbank Webpay Plus | create, commit, status, refund | redirect completo, expiración, estados/códigos, timeout de commit y conciliación | [Transbank Developers](https://www.transbankdevelopers.cl/producto/webpay) |

> [!IMPORTANT]
> La documentación oficial y las credenciales asignadas al comercio son la fuente de verdad. Si difieren del código, no ejecutes: actualiza el adaptador, sus pruebas y la matriz de cobertura.

## Variables

| Variable | Uso | Secreto |
|---|---|---:|
| `KHIPU_API_KEY` | autenticación Khipu | sí |
| `KHIPU_BASE_URL` | endpoint autorizado | no, pero debe controlarse |
| `MERCADOPAGO_ACCESS_TOKEN` | bearer token backend | sí |
| `MERCADOPAGO_BASE_URL` | endpoint API | no |
| `TRANSBANK_COMMERCE_CODE` | identificador comercio | sensible operacionalmente |
| `TRANSBANK_API_KEY` | autenticación | sí |
| `TRANSBANK_BASE_URL` | endpoint de integración/producción | no, pero debe controlarse |

Nunca permitas que un usuario final elija `BASE_URL`: convertiría el adapter en una vía de exfiltración de credenciales (SSRF). En producción usa allowlist y configuración inmutable por ambiente.

## Mercado Pago e idempotencia

El adaptador exige `X-Idempotency-Key` al crear y reembolsar. La [guía oficial](https://www.mercadopago.cl/developers/es/news/2023/01/04/Idempotency-key-usage-will-be-mandatory) explica su obligatoriedad. La clave pertenece a la operación estable: repetir el mismo intento reutiliza la clave; un nuevo intento intencional obtiene otra.

## Webpay y retorno

Crear devuelve token y URL para presentar el formulario del proveedor. El backend debe hacer commit/consulta; la navegación de retorno no prueba autorización. Status existe precisamente para recuperar condiciones inesperadas. Refund puede resultar en reversa o anulación según las reglas y estado de la transacción.

## Cómo extender

Implementa el ABC mínimo, declara capabilities adicionales sin asumir que son universales, inyecta el cliente HTTP para test, mapea errores/estados en un módulo dedicado y aporta fixtures sintéticos. Completa los diez puntos del [contrato de un medio](../payment-methods/CATALOG.md#contrato-para-agregar-un-nuevo-medio).

**Revisión de enlaces:** 7 de septiembre de 2026. Revalidar contratos antes de uso.
