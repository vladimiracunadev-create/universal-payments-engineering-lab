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

El [roadmap](https://github.com/vladimiracunadev-create/universal-payments-engineering-lab/blob/main/ROADMAP.md) indica qué capacidades aún faltan en este repositorio.

## Nivel 6 · Economía virtual y bienes digitales

### Laboratorio 6 — Comprar GEM y gastar GEM

- **Ejecuta:** `python scripts/paylab.py game-demo --scenario game-currency-success`.
- **Observa:** una orden CLP, un payment attempt, un `LOAD` GEM y otra orden GEM para `SKIN_DRAGON`.
- **Criterio:** no describes el crédito GEM como settlement CLP ni la skin como saldo.

### Laboratorio 7 — Efecto lógico único

- **Ejecuta:** `game-currency-duplicate-webhook`, `game-currency-response-lost` y `game-currency-crash-recovery`.
- **Observa:** delivery repetido, retry cliente y reinicio producen un solo crédito y un solo entitlement.
- **Criterio:** explicas *exactly-once logical effect* sin prometer transporte exactly-once.

### Laboratorio 8 — Consecuencias posteriores

- **Ejecuta:** refund, chargeback y restore.
- **Observa:** asientos compensatorios, saldo negativo/revisión y restauración sin segundo cargo.
- **Criterio:** distingues refund, chargeback, revoke, restore y política comercial.

Guía: [Economía virtual de comienzo a fin](verticals/VIRTUAL_GAME_ECONOMY.md).
