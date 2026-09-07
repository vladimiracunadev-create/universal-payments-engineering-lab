# 💥 Fault Lab

Este laboratorio reproduce fallas **alrededor del software propio**. No emula una red real, certifica un proveedor ni mueve dinero.

## Escenarios

| Falla | Inyección | Invariante |
|---|---|---|
| timeout antes de enviar | abortar conexión | retry controlado puede usar la misma identidad |
| timeout tras procesar | ocultar respuesta exitosa | consulta/retry idempotente evita doble efecto |
| webhook duplicado | entregar dos veces mismo event ID | un solo cambio y un solo journal |
| webhook perdido | no entregar evento | polling/reconciliación recupera |
| fuera de orden | `settled` antes de `captured` | consultar y aplicar estado monotónico |
| dos workers | ejecutar misma clave en paralelo | unique constraint/lock deja un efecto |
| 5xx / rate limit | secuencia programada | backoff con jitter y budget |
| respuesta corrupta | JSON inválido/campo ausente | cuarentena; no inventar estado |
| secreto rotado | invalidar credencial | alerta, rotación segura y no fallback inseguro |
| conciliación divergente | monto/referencia diferente | excepción visible, no autocorrección |

## Experimento mínimo

1. Crea una intención y clave `K`.
2. Configura el stub para aceptar y ocultar la respuesta.
3. Envía la operación: el estado local debe quedar `TIMEOUT/UNKNOWN`.
4. Repite con `K` o consulta por referencia.
5. Comprueba un solo efecto remoto, una sola contabilización y resultado final.
6. Guarda timeline y aserciones.

## Criterios

- cero doble efecto;
- ningún timeout transformado automáticamente en decline;
- todo `UNKNOWN` entra a recovery con owner;
- los duplicados son observables pero inocuos;
- los mensajes fallidos pueden re-drivearse;
- reconciliación detecta la divergencia.

El proyecto aún no incluye un servidor de fault injection; esta página define su contrato y su estado permanece `DOCUMENTED`.
