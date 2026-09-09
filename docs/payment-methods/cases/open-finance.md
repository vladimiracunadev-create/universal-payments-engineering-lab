# 25. Open Finance e iniciación

[← Volver a la tabla](../END_TO_END_MATRIX.md) · [Ver esta guía .md en GitHub](https://github.com/vladimiracunadev-create/universal-payments-engineering-lab/blob/main/docs/payment-methods/cases/open-finance.md)

## En una frase

**Sirve para:** Iniciar pago desde una app con consentimiento bancario.

**Modelo mental:** Una aplicación inicia desde la cuenta solo dentro del consentimiento y alcance otorgados.

## Ejemplo concreto

<div class="case-example-grid">
<article><span>Situación</span><p>Una app inicia $55.000 desde la cuenta bancaria del usuario. El consentimiento limita monto y propósito; FAPI y mTLS protegen el intercambio con el banco.</p></article>
<article><span>Detrás de la pantalla</span><p>TPP crea consentimiento con alcance y expiración. Cliente autentica en banco; FAPI entrega token ligado.</p></article>
<article><span>Se acepta como pagado cuando</span><p>Payment ID se consulta hasta estado final. Después: Banco y comercio concilian referencia end-to-end.</p></article>
</div>

### No confundas estas tres cosas

| Lo que ocurre | Lo que significa | Lo que NO significa |
|---|---|---|
| El usuario vuelve a tu web | Terminó la experiencia del navegador | Que el dinero esté confirmado |
| El proveedor autoriza/confirma | Existe evidencia operativa del proveedor | Que el abono bancario ya esté conciliado |
| El reporte y el ledger cuadran | Puedes explicar el cierre financiero | Que nunca pueda existir devolución o disputa |

## Quién participa

- Pagador
- Backend del comercio o TPP
- Proveedor/API bancaria
- Banco pagador
- Banco receptor
- Operaciones y conciliación

## Recorrido completo, paso a paso

| Etapa | Qué ocurre | Pregunta de control |
|---|---|---|
| 1. Inicio | TPP crea consentimiento con alcance y expiración. | ¿Existe una referencia propia, monto, moneda y expiración? |
| 2. Proceso | Cliente autentica en banco; FAPI entrega token ligado. | ¿Qué sistema externo puede producir el efecto financiero? |
| 3. Confirmación | Payment ID se consulta hasta estado final. | ¿La evidencia viene de una API, webhook, banco o archivo autoritativo? |
| 4. Cierre | Banco y comercio concilian referencia end-to-end. | ¿Ledger, proveedor y banco pueden explicar el mismo resultado? |

```mermaid
flowchart LR
  A["Inicio<br/>TPP crea consentimiento con alcance y expiración."] --> B["Proceso<br/>Cliente autentica en banco; FAPI entrega token ligado."]
  B --> C["Confirmar<br/>Payment ID se consulta hasta estado final."]
  C --> D["Cerrar<br/>Banco y comercio concilian referencia end-to-end."]
  B -. "sin respuesta" .-> U["UNKNOWN"]
  U -. "consultar; no duplicar" .-> C
```

## Qué ocurre si falla

**Fallo característico:** Consentimiento revocado/token vencido exige nueva autorización.

Regla operativa: un timeout no equivale a rechazo. Conserva la operación como `UNKNOWN`, consulta mediante la misma referencia y permite un nuevo intento sólo cuando puedas demostrar que el anterior no produjo efecto.

Escenarios que debes probar:

- Happy path con montos mínimos, normales y límites documentados.
- Rechazo, cancelación del usuario, expiración y retorno del navegador manipulado.
- Timeout antes y después de enviar, webhook tardío, duplicado y fuera de orden.
- Refund total/parcial cuando aplique y conciliación con una diferencia intencional.
- Prueba end-to-end en sandbox/certificación con credenciales separadas; producción solo después de aprobar el checklist.

## Cómo llevarlo a una aplicación real

**Primer incremento de desarrollo:**

- Registrar TPP/cliente según regulación.
- Implementar FAPI, PKCE y consentimiento.
- Usar token ligado, iniciar y consultar el pago.

**Evidencia para considerarlo exitoso:** Consent ID, token con alcance mínimo y payment ID confirmado.

**Construcción concreta:** Registro/licencia TPP + OAuth/OIDC FAPI + mTLS + API bancaria.

### Lenguaje, API y almacenamiento

| Capa | Recomendación para este laboratorio | Responsabilidad |
|---|---|---|
| Frontend | TypeScript + HTML/CSS. El navegador presenta el checkout y recibe el retorno; no guarda secretos. | Experiencia; nunca secretos. |
| Backend | Python 3.11+ con FastAPI para este laboratorio. Node.js/TypeScript, Java, .NET o Go son equivalentes si el equipo los opera mejor. | Orden, autenticación, idempotencia y estados. |
| API/canal | HTTPS REST/JSON entre tu backend y el proveedor; webhooks HTTPS para cambios asíncronos. | Comunicar con proveedor o rail. |
| Datos | PostgreSQL para intents, eventos, idempotencia y ledger; Redis solo para cache/locks, nunca como libro contable. | Evidencia, ledger y auditoría. |
| Operación | Docker, gestor de secretos, logs estructurados, métricas, alertas y job de conciliación. | Despliegue, observabilidad y recuperación. |

**Tecnologías del catálogo:** `oauth2`, `oidc`, `fapi2`, `mtls`, `dpop`, `par`, `private-key-jwt`

**Operaciones cubiertas:** `payment-initiation`, `consent`, `account-information`

### Alta, contrato y costo

- **Dónde comenzar:** Elegir un proveedor regulado que ofrezca esta modalidad en tu país, abrir cuenta comercial, verificar la empresa y solicitar sandbox.
- **Costo:** El DEMO cuesta $0. Precio, impuestos, reservas y plazo de liquidación dependen del proveedor, país y volumen; pedir cotización vigente.
- **Decisión:** Usa Open Finance e iniciación solo si su cobertura, experiencia, reversibilidad y conciliación resuelven tu caso; compara al menos dos proveedores antes de LIVE.

### Variables y callbacks

| Variable | Obligatoria | Tratamiento | Propósito |
|---|---|---|---|
| `PAYLAB_HOST` | No | No secreta | Interfaz local. Solo se aceptan direcciones loopback. |
| `PAYLAB_PORT` | No | No secreta | Puerto del portal localhost. |
| `PAYLAB_CONFIG_DIR` | No | No secreta | Directorio alternativo para catálogo y guías. |

**Callbacks previstos:**

- No hay callback concreto hasta seleccionar un proveedor.

> GitHub Pages nunca usa estas variables. Configúralas únicamente en localhost, CI protegido o el secret manager del backend.

### Orden recomendado de implementación

1. Crear una orden/intención propia en el backend y fijar monto, moneda, comercio y expiración.
2. Enviar al proveedor desde el backend con credencial secreta e idempotency key; persistir referencia y request seguro.
3. Entregar al frontend solo el token, QR o URL de redirección de alcance mínimo.
4. Tratar el retorno del navegador como experiencia, no como prueba de pago; confirmar por API/webhook.
5. Validar y deduplicar el webhook, aplicar una máquina de estados monotónica y contabilizar una sola vez.
6. Consultar operaciones UNKNOWN y conciliar diariamente contra proveedor/banco; gestionar refunds y disputas.

## Seguridad de datos

- El monto, moneda, beneficiario y referencia nacen o se validan en el backend; nunca se confía en el navegador.
- Secretos en un gestor de secretos, rotación y mínimo privilegio; jamás en JavaScript, Git o logs.
- TLS, validación de firma/origen de webhooks, deduplicación persistente e idempotency key por operación.
- Minimizar datos: almacenar tokens y referencias del proveedor, no PAN, CVV, claves ni credenciales bancarias.
- Cifrado en reposo, control de acceso, trazabilidad y política de retención/borrado.

## Ventajas y desventajas

### Ventajas

- Amplía las opciones de pago y desacopla el comercio de la red subyacente.

### Desventajas

- Disponibilidad, costos y reglas dependen del proveedor y la regulación local.

## Checklist antes de LIVE

- [ ] Contrato y cuenta comercial aprobados; costos y plazos confirmados directamente con el proveedor.
- [ ] Credenciales productivas separadas, callbacks HTTPS públicos, dominios permitidos y rotación documentada.
- [ ] Alertas, runbook, soporte, refund/disputa y conciliación ensayados con responsables definidos.
- [ ] Piloto con límites y monitoreo reforzado; rollback que detiene nuevas operaciones sin perder evidencia.

## Qué demuestra el DEMO y qué no

El DEMO permite observar el recorrido de **Open Finance e iniciación**, incluyendo éxito, timeout recuperado, evento duplicado y diferencia de conciliación. No contacta al proveedor, no valida credenciales, no certifica cumplimiento y no mueve dinero.

## Fuentes

- [OpenID Foundation · FAPI](https://openid.net/wg/fapi/)
- [IETF · OAuth 2.0 Security BCP](https://www.rfc-editor.org/rfc/rfc9700)

---

[Abrir Open Finance e iniciación en la tabla](../END_TO_END_MATRIX.md) · [Configurar localhost](../../LOCALHOST_AND_CONFIGURATION.md)
