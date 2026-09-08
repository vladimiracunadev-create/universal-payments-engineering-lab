# 🎓 Ruta de aprendizaje

Esta ruta convierte el repositorio en un curso práctico. Cada laboratorio comienza con una pregunta, produce evidencia y termina con un criterio verificable.

## Nivel 1 · Comprender el pago

### Laboratorio 1 — El pago exitoso

- **Pregunta:** ¿en qué momento existe un pago?
- **Ejecuta:** `python scripts/paylab.py demo cards --scenario success`.
- **Observa:** CREATED, autenticación, autorización, captura, settlement y conciliación.
- **Criterio:** puedes explicar por qué `AUTHORIZED` y `SETTLED` no son sinónimos.

### Laboratorio 2 — Resultado desconocido

- **Pregunta:** ¿un timeout autoriza un reintento?
- **Ejecuta:** `python scripts/paylab.py demo chile-webpay --scenario timeout-recovered`.
- **Observa:** `UNKNOWN` seguido de una consulta por la misma referencia.
- **Criterio:** propones recuperación sin crear un segundo efecto.

## Nivel 2 · Construir invariantes

### Laboratorio 3 — Evento repetido

- **Pregunta:** ¿qué pasa cuando el proveedor entrega dos veces el webhook?
- **Ejecuta:** escenario `duplicate-event`.
- **Observa:** un evento aceptado y uno ignorado.
- **Criterio:** distingues autenticación del mensaje, deduplicación e idempotencia.

### Laboratorio 4 — Contabilidad

- **Pregunta:** ¿cómo se representa el efecto sin modificar historia?
- **Observa:** las entradas `cash/provider` y `merchant/receivable`.
- **Criterio:** verificas que la suma por moneda sea cero y propones compensación, no borrado.

### Laboratorio 5 — Conciliación

- **Pregunta:** ¿qué ocurre si el proveedor reporta otro monto?
- **Ejecuta:** escenario `reconciliation-mismatch`.
- **Observa:** `RECONCILIATION_EXCEPTION`.
- **Criterio:** mantienes ambas fuentes y abres un caso operativo.

## Nivel 3 · Elegir tecnología

Compara tres familias en el portal:

1. Webpay Plus: tarjeta y redirección alojada.
2. Khipu: iniciación cuenta a cuenta.
3. Efectivo: custodia física y depósito.

Para cada una completa:

| Decisión | Tu respuesta |
|---|---|
| problema de negocio | ¿qué necesidad resuelve? |
| experiencia | ¿redirección, QR, dispositivo o proceso manual? |
| API/protocolo | ¿REST, webhook, archivo, ISO 20022 u otro? |
| datos sensibles | ¿qué dato nunca debe tocar tu sistema? |
| resultado incierto | ¿cómo se consulta? |
| liquidación | ¿qué evidencia externa llega y cuándo? |
| costo total | ¿tarifa, plazo, reservas, soporte y operación? |

## Nivel 4 · Preparar SANDBOX

1. Elige un proveedor y revisa su fuente oficial.
2. Abre una cuenta de prueba autorizada.
3. Separa credenciales, URLs y datos de test.
4. Implementa callbacks HTTPS verificables.
5. Ejecuta éxito, rechazo, cancelación, timeout, duplicado y refund.
6. Documenta qué fue simulado y qué respondió realmente el sandbox.

El laboratorio no cambia a DEMO después de iniciar una operación externa. Esa separación evita presentar una simulación como evidencia real.

## Nivel 5 · Diseñar LIVE

Antes de mover dinero, debes poder demostrar:

- idempotencia y deduplicación persistentes;
- máquina de estados monotónica;
- ledger durable y balanceado;
- recuperación de `UNKNOWN`;
- conciliación con proveedor y banco;
- rotación de secretos y trazabilidad;
- alertas, responsables y runbooks;
- refund, disputa y reversa probados;
- contrato, certificación y obligaciones regulatorias aplicables.

El [roadmap](../ROADMAP.md) indica qué capacidades aún faltan en este repositorio.
