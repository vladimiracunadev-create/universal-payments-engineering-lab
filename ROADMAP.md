# 🗺️ Roadmap

El roadmap expresa trabajo futuro; no eleva la [cobertura actual](docs/operations/COVERAGE.md).

## Fase 1 — Hardening del núcleo

- dinero tipado en unidades menores/`Decimal` de extremo a extremo;
- payment intent/attempt y capability model;
- persistencia transaccional, constraints y migraciones;
- idempotency record con respuesta/TTL y concurrencia;
- ledger con chart of accounts y referencias únicas;
- conciliación por estado, fees, neto, fechas y lotes.

## Fase 2 — API y eventos

- Payments API versionada;
- outbox/inbox, cola y webhook gateway;
- verificadores específicos por proveedor;
- recovery scheduler para estados inciertos;
- OpenTelemetry, métricas y dashboards;
- fault-injection server reproducible.

## Fase 3 — Integraciones verificadas

- contract tests de los tres adapters existentes;
- evidencia de sandbox/certificación privada y sanitizada;
- state/error mapping completo;
- refund/reversal/webhook/reconciliation por proveedor;
- adaptador A2A adicional solo con acceso oficial.

## Fase 4 — Operación de plataforma

- multi-provider routing con safe failover;
- marketplace ledger, reserves y payouts;
- risk/limits engine y approval workflow;
- DR, capacity, SLO, incident drills y supply-chain attestations;
- sitio navegable del currículo y laboratorios.

## Condición de salida

Una fase termina con tests, documentación, evidencia, amenazas, operación y matriz de cobertura actualizados; nunca por completar solo el happy path.
