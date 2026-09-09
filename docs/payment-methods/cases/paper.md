# 02. Cheques y órdenes en papel

[← Volver a la tabla](../END_TO_END_MATRIX.md) · [Ver esta guía .md en GitHub](https://github.com/vladimiracunadev-create/universal-payments-engineering-lab/blob/main/docs/payment-methods/cases/paper.md)

## El mismo caso en tres formatos

| Formato | Para qué sirve | Enlace |
|---|---|---|
| Markdown | Fuente única, revisable en GitHub. | [Abrir fuente .md](https://github.com/vladimiracunadev-create/universal-payments-engineering-lab/blob/main/docs/payment-methods/cases/paper.md) |
| HTML | Página generada automáticamente para navegar. | [Abrir en GitHub Pages](https://vladimiracunadev-create.github.io/universal-payments-engineering-lab/payment-methods/cases/paper.html) |
| PDF | Manual descargable; el índice lleva a este caso. | [Abrir PDF en este caso](https://vladimiracunadev-create.github.io/universal-payments-engineering-lab/downloads/universal-payments-engineering-lab.pdf#nameddest=case-paper) |

Los tres muestran el mismo catálogo. Markdown es la fuente; HTML y PDF son salidas generadas y verificadas.

## En una frase

**Sirve para:** Cheque u orden física con cobro diferido.

**Modelo mental:** Recibir un cheque no equivale a cobrarlo: existe un período de presentación y posible devolución.

## Ejemplo concreto

<div class="case-example-grid">
<article><span>Situación</span><p>Una empresa recibe un cheque por $1.200.000. La factura sigue pendiente hasta que el banco confirme el cobro; recibir el papel no libera el pedido.</p></article>
<article><span>Detrás de la pantalla</span><p>Registra emisor, monto, fecha e imagen restringida. Entrega el documento al banco y queda PENDING.</p></article>
<article><span>Se acepta como pagado cuando</span><p>El banco informa cobro o devolución. Después: Aplica asiento final y concilia cartola.</p></article>
</div>

### No confundas estas tres cosas

| Lo que ocurre | Lo que significa | Lo que NO significa |
|---|---|---|
| El usuario vuelve a tu web | Terminó la experiencia del navegador | Que el dinero esté confirmado |
| El proveedor autoriza/confirma | Existe evidencia operativa del proveedor | Que el abono bancario ya esté conciliado |
| El reporte y el ledger cuadran | Puedes explicar el cierre financiero | Que nunca pueda existir devolución o disputa |

## Quién participa

- Cliente o pagador
- Comercio/cajero
- Custodio o recaudador
- Banco y equipo de conciliación

## Recorrido completo, paso a paso

| Etapa | Qué ocurre | Pregunta de control |
|---|---|---|
| 1. Inicio | Registra emisor, monto, fecha e imagen restringida. | ¿Existe una referencia propia, monto, moneda y expiración? |
| 2. Proceso | Entrega el documento al banco y queda PENDING. | ¿Qué sistema externo puede producir el efecto financiero? |
| 3. Confirmación | El banco informa cobro o devolución. | ¿La evidencia viene de una API, webhook, banco o archivo autoritativo? |
| 4. Cierre | Aplica asiento final y concilia cartola. | ¿Ledger, proveedor y banco pueden explicar el mismo resultado? |

```mermaid
flowchart LR
  A["Inicio<br/>Registra emisor, monto, fecha e imagen restringida."] --> B["Proceso<br/>Entrega el documento al banco y queda PENDING."]
  B --> C["Confirmar<br/>El banco informa cobro o devolución."]
  C --> D["Cerrar<br/>Aplica asiento final y concilia cartola."]
  B -.-> U["Sin respuesta<br/>UNKNOWN"]
  U -.-> R["Consultar misma referencia<br/>no duplicar"]
  R -.-> C
```

## Qué ocurre si falla

**Fallo característico:** Cheque devuelto revierte disponibilidad y abre cobranza.

Regla operativa: un timeout no equivale a rechazo. Conserva la operación como `UNKNOWN`, consulta mediante la misma referencia y permite un nuevo intento sólo cuando puedas demostrar que el anterior no produjo efecto.

Escenarios que debes probar:

- Happy path con montos mínimos, normales y límites documentados.
- Rechazo, cancelación del usuario, expiración y retorno del navegador manipulado.
- Timeout antes y después de enviar, webhook tardío, duplicado y fuera de orden.
- Refund total/parcial cuando aplique y conciliación con una diferencia intencional.
- Prueba end-to-end en sandbox/certificación con credenciales separadas; producción solo después de aprobar el checklist.

## Cómo llevarlo a una aplicación real

**Primer incremento de desarrollo:**

- Capturar referencia sin almacenar imágenes innecesarias.
- Mantener estado pendiente durante clearing.
- Aplicar abono o devolución mediante evento bancario.

**Evidencia para considerarlo exitoso:** Confirmación del banco y ausencia de devolución dentro de la ventana aplicable.

**Construcción concreta:** Backoffice + custodia + API/archivo bancario + reglas locales.

### Lenguaje, API y almacenamiento

| Capa | Recomendación para este laboratorio | Responsabilidad |
|---|---|---|
| Frontend | Interfaz web administrativa para registrar recepción, custodia y diferencias; no inicia una red de pagos. | Experiencia; nunca secretos. |
| Backend | Python/FastAPI o el stack transaccional existente del comercio. | Orden, autenticación, idempotencia y estados. |
| API/canal | API interna REST/JSON y, cuando exista, archivo/API de banco o red externa. | Comunicar con proveedor o rail. |
| Datos | PostgreSQL con auditoría inmutable y ledger de doble entrada. | Evidencia, ledger y auditoría. |
| Operación | Control de acceso por rol, doble aprobación, respaldos y conciliación diaria. | Despliegue, observabilidad y recuperación. |

**Tecnologías del catálogo:** `image-clearing`, `micr`, `batch-clearing`

**Operaciones cubiertas:** `cheque`, `cashiers-cheque`, `bank-draft`, `money-order`

### Alta, contrato y costo

- **Dónde comenzar:** Elegir un proveedor regulado que ofrezca esta modalidad en tu país, abrir cuenta comercial, verificar la empresa y solicitar sandbox.
- **Costo:** El DEMO cuesta $0. Precio, impuestos, reservas y plazo de liquidación dependen del proveedor, país y volumen; pedir cotización vigente.
- **Decisión:** Usa Cheques y órdenes en papel solo si su cobertura, experiencia, reversibilidad y conciliación resuelven tu caso; compara al menos dos proveedores antes de LIVE.

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

El DEMO permite observar el recorrido de **Cheques y órdenes en papel**, incluyendo éxito, timeout recuperado, evento duplicado y diferencia de conciliación. No contacta al proveedor, no valida credenciales, no certifica cumplimiento y no mueve dinero.

## Fuentes

- [ISO · ISO 20022](https://www.iso20022.org/)
- [BIS CPMI · sistemas de pago](https://www.bis.org/committees/cpmi/overview)

---

[Abrir Cheques y órdenes en papel en la tabla](../END_TO_END_MATRIX.md) · [Configurar localhost](../../LOCALHOST_AND_CONFIGURATION.md)
