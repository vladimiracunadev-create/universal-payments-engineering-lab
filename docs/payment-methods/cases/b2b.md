# 22. Pagos B2B y tesorería

[← Volver a la tabla web](../END_TO_END_MATRIX.html) · [← Volver a la tabla Markdown](../END_TO_END_MATRIX.md)

## En una frase

**Sirve para:** Pago de facturas con aprobaciones empresariales.

**Modelo mental:** La factura necesita aprobación, instrucción bancaria y aplicación contable en ERP.

## Ejemplo concreto

Imagina esta necesidad: Pago de facturas con aprobaciones empresariales. El negocio no puede limitarse a mostrar «pago exitoso»; debe conservar una referencia, obtener una confirmación autoritativa y demostrar después cómo terminó el dinero.

## Quién participa

- Pagador
- Canal o frontend
- Backend del negocio
- Proveedor o rail
- Operaciones y conciliación

## Recorrido completo, paso a paso

| Etapa | Qué ocurre | Pregunta de control |
|---|---|---|
| 1. Inicio | Ingiere factura y valida proveedor. | ¿Existe una referencia propia, monto, moneda y expiración? |
| 2. Proceso | Segregación de funciones aprueba instrucción. | ¿Qué sistema externo puede producir el efecto financiero? |
| 3. Confirmación | Banco confirma ejecución y remittance. | ¿La evidencia viene de una API, webhook, banco o archivo autoritativo? |
| 4. Cierre | ERP, banco y factura se concilian. | ¿Ledger, proveedor y banco pueden explicar el mismo resultado? |

```mermaid
flowchart LR
  A["Inicio<br/>Ingiere factura y valida proveedor."] --> B["Proceso<br/>Segregación de funciones aprueba instrucción."]
  B --> C["Confirmar<br/>Banco confirma ejecución y remittance."]
  C --> D["Cerrar<br/>ERP, banco y factura se concilian."]
  B -. "sin respuesta" .-> U["UNKNOWN"]
  U -. "consultar; no duplicar" .-> C
```

## Qué ocurre si falla

**Fallo característico:** Duplicado/cambio de cuenta bloquea pago y escala revisión.

Regla operativa: un timeout no equivale a rechazo. Conserva la operación como `UNKNOWN`, consulta mediante la misma referencia y permite un nuevo intento sólo cuando puedas demostrar que el anterior no produjo efecto.

Escenarios que debes probar:

- Happy path con montos mínimos, normales y límites documentados.
- Rechazo, cancelación del usuario, expiración y retorno del navegador manipulado.
- Timeout antes y después de enviar, webhook tardío, duplicado y fuera de orden.
- Refund total/parcial cuando aplique y conciliación con una diferencia intencional.
- Prueba end-to-end en sandbox/certificación con credenciales separadas; producción solo después de aprobar el checklist.

## Cómo llevarlo a una aplicación real

**Primer incremento de desarrollo:**

- Ingerir y validar factura.
- Modelar segregación de funciones/aprobaciones.
- Enviar pago y aplicar remittance al ERP.

**Evidencia para considerarlo exitoso:** Factura aprobada, instrucción bancaria y asiento ERP con la misma referencia.

**Construcción concreta:** ERP + workflow de aprobación + API bancaria/SFTP + sanciones.

### Lenguaje, API y almacenamiento

| Capa | Recomendación para este laboratorio | Responsabilidad |
|---|---|---|
| Frontend | Interfaz web administrativa para registrar recepción, custodia y diferencias; no inicia una red de pagos. | Experiencia; nunca secretos. |
| Backend | Python/FastAPI o el stack transaccional existente del comercio. | Orden, autenticación, idempotencia y estados. |
| API/canal | API interna REST/JSON y, cuando exista, archivo/API de banco o red externa. | Comunicar con proveedor o rail. |
| Datos | PostgreSQL con auditoría inmutable y ledger de doble entrada. | Evidencia, ledger y auditoría. |
| Operación | Control de acceso por rol, doble aprobación, respaldos y conciliación diaria. | Despliegue, observabilidad y recuperación. |

**Tecnologías del catálogo:** `erp`, `edi`, `iso20022`, `approval-workflow`

**Operaciones cubiertas:** `virtual-card`, `purchasing-card`, `invoice-payment`, `edi`, `treasury-payment`

### Alta, contrato y costo

- **Dónde comenzar:** Elegir un proveedor regulado que ofrezca esta modalidad en tu país, abrir cuenta comercial, verificar la empresa y solicitar sandbox.
- **Costo:** El DEMO cuesta $0. Precio, impuestos, reservas y plazo de liquidación dependen del proveedor, país y volumen; pedir cotización vigente.
- **Decisión:** Usa Pagos B2B y tesorería solo si su cobertura, experiencia, reversibilidad y conciliación resuelven tu caso; compara al menos dos proveedores antes de LIVE.

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

El DEMO permite observar el recorrido de **Pagos B2B y tesorería**, incluyendo éxito, timeout recuperado, evento duplicado y diferencia de conciliación. No contacta al proveedor, no valida credenciales, no certifica cumplimiento y no mueve dinero.

## Fuentes

- [ISO · ISO 20022](https://www.iso20022.org/)
- [BIS CPMI · sistemas de pago](https://www.bis.org/cpmi/index.htm)

---

[Abrir Pagos B2B y tesorería en la tabla web](../END_TO_END_MATRIX.html) · [Configurar localhost](../../LOCALHOST_AND_CONFIGURATION.html)
