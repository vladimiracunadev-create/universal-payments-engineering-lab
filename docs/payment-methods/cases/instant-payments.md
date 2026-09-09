# 16. Pagos instantáneos

[← Volver a la tabla](../END_TO_END_MATRIX.md) · [Ver esta guía .md en GitHub](https://github.com/vladimiracunadev-create/universal-payments-engineering-lab/blob/main/docs/payment-methods/cases/instant-payments.md)

## En una frase

**Sirve para:** Transferencia cuenta a cuenta casi inmediata 24/7.

**Modelo mental:** El rail confirma en segundos, pero tu sistema aún necesita idempotencia y conciliación.

## Ejemplo concreto

<div class="case-example-grid">
<article><span>Situación</span><p>Un cliente paga $42.000 mediante un rail 24/7. La respuesta llega en segundos, pero un timeout sigue necesitando consulta por referencia end-to-end.</p></article>
<article><span>Detrás de la pantalla</span><p>Resuelve alias/cuenta y crea referencia end-to-end. Rail valida e instruye en tiempo real.</p></article>
<article><span>Se acepta como pagado cuando</span><p>Confirmación con finalidad declarada cierra el pago. Después: Concilia mensajes, cuentas técnicas y banco.</p></article>
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
| 1. Inicio | Resuelve alias/cuenta y crea referencia end-to-end. | ¿Existe una referencia propia, monto, moneda y expiración? |
| 2. Proceso | Rail valida e instruye en tiempo real. | ¿Qué sistema externo puede producir el efecto financiero? |
| 3. Confirmación | Confirmación con finalidad declarada cierra el pago. | ¿La evidencia viene de una API, webhook, banco o archivo autoritativo? |
| 4. Cierre | Concilia mensajes, cuentas técnicas y banco. | ¿Ledger, proveedor y banco pueden explicar el mismo resultado? |

```mermaid
flowchart LR
  A["Inicio<br/>Resuelve alias/cuenta y crea referencia end-to-end."] --> B["Proceso<br/>Rail valida e instruye en tiempo real."]
  B --> C["Confirmar<br/>Confirmación con finalidad declarada cierra el pago."]
  C --> D["Cerrar<br/>Concilia mensajes, cuentas técnicas y banco."]
  B -. "sin respuesta" .-> U["UNKNOWN"]
  U -. "consultar; no duplicar" .-> C
```

## Qué ocurre si falla

**Fallo característico:** UNKNOWN exige status; rapidez no autoriza duplicar.

Regla operativa: un timeout no equivale a rechazo. Conserva la operación como `UNKNOWN`, consulta mediante la misma referencia y permite un nuevo intento sólo cuando puedas demostrar que el anterior no produjo efecto.

Escenarios que debes probar:

- Happy path con montos mínimos, normales y límites documentados.
- Rechazo, cancelación del usuario, expiración y retorno del navegador manipulado.
- Timeout antes y después de enviar, webhook tardío, duplicado y fuera de orden.
- Refund total/parcial cuando aplique y conciliación con una diferencia intencional.
- Prueba end-to-end en sandbox/certificación con credenciales separadas; producción solo después de aprobar el checklist.

## Cómo llevarlo a una aplicación real

**Primer incremento de desarrollo:**

- Resolver alias/beneficiario.
- Enviar instrucción o request-to-pay.
- Consumir confirmación final y conciliar en tiempo casi real.

**Evidencia para considerarlo exitoso:** ID end-to-end con finalidad confirmada por el rail.

**Construcción concreta:** Participante/proveedor + API ISO 20022/local + operación 24/7.

### Lenguaje, API y almacenamiento

| Capa | Recomendación para este laboratorio | Responsabilidad |
|---|---|---|
| Frontend | TypeScript + HTML/CSS. El navegador presenta el checkout y recibe el retorno; no guarda secretos. | Experiencia; nunca secretos. |
| Backend | Python 3.11+ con FastAPI para este laboratorio. Node.js/TypeScript, Java, .NET o Go son equivalentes si el equipo los opera mejor. | Orden, autenticación, idempotencia y estados. |
| API/canal | HTTPS REST/JSON entre tu backend y el proveedor; webhooks HTTPS para cambios asíncronos. | Comunicar con proveedor o rail. |
| Datos | PostgreSQL para intents, eventos, idempotencia y ledger; Redis solo para cache/locks, nunca como libro contable. | Evidencia, ledger y auditoría. |
| Operación | Docker, gestor de secretos, logs estructurados, métricas, alertas y job de conciliación. | Despliegue, observabilidad y recuperación. |

**Tecnologías del catálogo:** `iso20022`, `aliases`, `qr`, `request-to-pay`, `api`, `real-time-settlement`

**Operaciones cubiertas:** `pix`, `upi`, `spei`, `fednow`, `rtp`, `faster-payments`, `sepa-instant`

### Alta, contrato y costo

- **Dónde comenzar:** Elegir un proveedor regulado que ofrezca esta modalidad en tu país, abrir cuenta comercial, verificar la empresa y solicitar sandbox.
- **Costo:** El DEMO cuesta $0. Precio, impuestos, reservas y plazo de liquidación dependen del proveedor, país y volumen; pedir cotización vigente.
- **Decisión:** Usa Pagos instantáneos solo si su cobertura, experiencia, reversibilidad y conciliación resuelven tu caso; compara al menos dos proveedores antes de LIVE.

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

El DEMO permite observar el recorrido de **Pagos instantáneos**, incluyendo éxito, timeout recuperado, evento duplicado y diferencia de conciliación. No contacta al proveedor, no valida credenciales, no certifica cumplimiento y no mueve dinero.

## Fuentes

- [ISO · ISO 20022](https://www.iso20022.org/)
- [BIS CPMI · sistemas de pago](https://www.bis.org/committees/cpmi/overview)

---

[Abrir Pagos instantáneos en la tabla](../END_TO_END_MATRIX.md) · [Configurar localhost](../../LOCALHOST_AND_CONFIGURATION.md)
