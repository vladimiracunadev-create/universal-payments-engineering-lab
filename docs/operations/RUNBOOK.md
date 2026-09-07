# 🛠️ Runbook operacional

## Antes de habilitar un medio

- owner técnico y de negocio asignados;
- credenciales por ambiente, rotación y revocación probadas;
- egress/DNS/TLS y reloj sincronizado;
- montos, monedas, países y beneficiarios permitidos;
- idempotencia y referencias únicas;
- webhook + polling + conciliación;
- reversal/refund y contacto de escalamiento;
- dashboards, alertas y límite para kill switch;
- prueba controlada con evidencia sanitizada.

## Triage en 10 minutos

1. Delimitar proveedor, método, región, moneda, versión y ventana temporal.
2. Congelar retries no idempotentes; no borrar mensajes ni editar estados a mano.
3. Comparar tasa base y salud de dependencias.
4. Muestrear IDs internos y consultar estado remoto sin exponer datos.
5. Clasificar: rechazo legítimo, degradación, timeout/unknown, webhook, ledger, conciliación o settlement.
6. Mitigar: deshabilitar método, reducir tráfico, pausar payouts o activar proveedor alternativo solo bajo regla segura.
7. Mantener un timeline UTC y registrar decisiones.

## Matriz de incidentes

| Síntoma | Riesgo | Primera acción | Prohibido |
|---|---|---|---|
| suben timeouts de create | doble cargo | detener retry ciego y consultar por referencia | tratar como decline |
| webhook lag | estados locales stale | ampliar polling/recovery y revisar firma/cola | marcar pagos fallidos en masa |
| duplicados | doble efecto/ledger | deduplicar por event/op ID y revisar unique constraints | borrar evidencia |
| autorización alta, captura baja | pérdida de ingreso/holds | revisar jobs/cutoff y estado de auth | recapturar sin verificar |
| settlement menor | pérdida/fee/hold | pausar payout afectado y conciliar por lote | ajustar saldo sin journal |
| firma webhook falla | spoofing o rotación | poner evento en cuarentena y validar key/version | desactivar verificación |
| credencial expuesta | compromiso | revocar/rotar, aislar, auditar uso | solo borrar el log |
| beneficiario incorrecto | pérdida de fondos | detener pagos y activar escalamiento bancario | prometer reversa garantizada |

## Estado desconocido

`UNKNOWN` tiene owner y SLA. El job de recuperación consulta usando referencia estable, con backoff y límite. Si expira la ventana automática, abre caso manual con orden, attempt, proveedor, timestamps, respuesta/timeout, consulta y asiento; nunca solicita PAN/CVV.

## Deploy y rollback

Cambios de adaptador usan canary por comercio/método, compatibilidad hacia atrás, feature flag y observación de tasas financieras. Rollback de código no revierte dinero: las operaciones ya enviadas pasan a recuperación y conciliación.

## Cierre del incidente

Cerrar solo cuando el tráfico está estable, todos los `UNKNOWN` tienen resultado o caso, ledger/proveedor/banco cuadran, payouts se reanudaron de forma segura, secretos fueron rotados si aplica y existe postmortem con acciones y dueños.

## Ejecución controlada desde este repo

No se cargan automáticamente archivos `.env`. Exporta variables en el proceso o usa un secret manager. Primero corre tests y verificación; luego un solo pago de monto autorizado. Guarda evidencia sanitizada fuera del Git público. No hay necesidad de Docker para el CLI actual.
