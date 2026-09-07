# 🛡️ Threat model de pagos

## Activos

Fondos, autoridad de pago, PAN/tokens, credenciales, PII, claves de firma/cifrado, ledger, reglas de routing, archivos de settlement, evidencia y disponibilidad. Un atacante puede ser externo, cliente malicioso, comercio comprometido, insider, proveedor afectado o dependencia comprometida.

## Fronteras

Navegador/app, edge/API, servicios internos, provider API, webhook público, colas, bases, analytics, CI/CD, operadores y terceros. Todo dato que cruza una frontera se autentica, valida, minimiza y registra de forma segura.

## Amenazas y controles

| Amenaza | Escenario | Prevención | Detección/recuperación |
|---|---|---|---|
| doble cargo | retry tras timeout | idempotencia, query-before-retry | `UNKNOWN` aging, reconciliación, refund controlado |
| manipulación | cliente cambia monto/moneda | cálculo server-side, firma/schema | comparar orden-intent-provider-ledger |
| webhook falso/replay | POST fabricado o repetido | firma/mTLS, timestamp, raw body, inbox unique | cuarentena, alerta, consulta remota |
| account takeover | credenciales/sesión robadas | MFA resistente a phishing, risk, step-up | velocity, device/risk signals, bloqueo |
| APP fraud | usuario autoriza al estafador | confirmación de beneficiario, warnings, cooling-off | case management y contacto con rail |
| secreto filtrado | key en Git/log | secret manager, scanning, short-lived creds | revocación, rotación, auditoría |
| skimming/formjacking | captura de tarjeta en checkout | hosted fields/tokenización, CSP, integridad | monitoreo de cambios/scripts y respuesta PCI |
| fraude de refund | operador desvía devolución | refund al instrumento original, RBAC, dual control | alertas, journal y revisión |
| ledger alterado | cambio/borrado de asientos | append-only, constraints, acceso segregado | hash/audit trail, reconciliación |
| supply chain | dependencia/action maliciosa | pin, SBOM, least privilege, review | scanning, provenance y rollback |
| prompt injection | agente recibe instrucción hostil | policy engine fuera del modelo, allowlist y límites | human approval, audit y revoke |
| indisponibilidad | proveedor/rail caído | bulkheads, capacity, safe degradation | SLO, circuit breaker y recovery queue |

## Datos prohibidos

No persistir CVV/CVC/CID después de autorizar, PIN/PIN block fuera de componente autorizado, track data, claves privadas/seeds, secretos de API ni PAN completo salvo diseño y alcance expresamente aprobados. Logs, traces, errores, screenshots y fixtures también cuentan como almacenamiento.

## Webhook checklist

- HTTPS y endpoint dedicado;
- cuerpo crudo conservado solo si está sanitizado/cifrado y la retención lo permite;
- verificación según el proveedor, sin inventar un HMAC genérico;
- comparación constant-time cuando aplica;
- timestamp/nonce y ventana anti-replay;
- deduplicación persistente;
- autorización por tipo de evento/comercio;
- procesamiento asíncrono, DLQ y re-drive seguro;
- consulta remota ante contradicción.

## PCI y alcance

PCI DSS aplica a entidades que almacenan, procesan o transmiten datos de cuenta, y también a sistemas que pueden afectar la seguridad del entorno. Tokenización/hosted fields pueden reducir alcance, no lo eliminan por declaración. Determina el SAQ/ROC y controles con un asesor competente y la [biblioteca oficial PCI SSC](https://www.pcisecuritystandards.org/document_library/).

## Evidencia segura

Una evidencia de laboratorio incluye timestamp UTC, environment, versión, IDs no sensibles, request/response redactados, transición, consulta, journal y conciliación. Nunca publica credenciales, datos reales del pagador ni URLs firmadas vigentes.
