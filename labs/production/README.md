# 🏭 Production readiness

Producción no es un ambiente de práctica. Este gate evalúa una implementación concreta; el repositorio base no lo aprueba por sí solo.

| Dominio | Evidencia requerida |
|---|---|
| producto | owner, países, monedas, medios, límites y customer support |
| contrato | proveedor, esquema, certificación, SLA y escalamiento |
| seguridad | threat model, PCI/alcance, secrets, keys, pentest y respuesta |
| confiabilidad | SLO, capacidad, timeout/retry, DR y pruebas de recuperación |
| dinero | ledger, chart of accounts, settlement, reconciliación y payouts |
| fraude/compliance | controles, monitoreo, casos, regulación y aprobación |
| entrega | CI, revisión, artefacto, SBOM, provenance, rollback y flags |
| operación | dashboards, alertas, runbook, on-call, kill switch y postmortem |

## Decisión

`GO` solo con evidencia y aprobadores nombrados. `CONDITIONAL GO` incluye plazo/owner y nunca acepta brechas que permitan doble cargo, fuga de secretos, pérdida contable o incumplimiento. `NO-GO` es el resultado correcto cuando no puede demostrarse seguridad financiera.
