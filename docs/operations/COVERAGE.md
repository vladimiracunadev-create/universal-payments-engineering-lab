# 📊 Cobertura y madurez verificables

## Niveles

| Estado | Significa | No significa |
|---|---|---|
| `OPERATIVE_LOCAL` | código ejecutable y probado sin red financiera | producción endurecida |
| `REQUIRES_CREDENTIALS` | existe transporte hacia API oficial configurable | certificación, contrato ni prueba live completada |
| `REQUIRES_CERTIFICATION` | el caso necesita onboarding/reglas/infraestructura externa | que un mock sea equivalente |
| `REQUIRES_HARDWARE` | necesita dispositivo o infraestructura física/certificada | que Docker pueda reemplazarla |
| `DOCUMENTED` | cobertura conceptual y contrato de laboratorio | implementación ejecutable |

Todos los casos tienen un recorrido `DEMO` local. Ese recorrido demuestra la
semántica educativa común; el estado de esta tabla indica la madurez de la
implementación específica y de su acceso externo.

## Matriz actual

| Capacidad | Estado | Evidencia | Brecha antes de producción |
|---|---|---|---|
| transiciones de pago | `OPERATIVE_LOCAL` | `core/states.py` + pruebas | persistencia, concurrencia y estados por provider |
| ledger balanceado | `OPERATIVE_LOCAL` | `core/ledger.py` + pruebas | DB, chart of accounts, uniqueness, cierre de período |
| idempotencia por fingerprint | `OPERATIVE_LOCAL` | `core/idempotency.py` + pruebas | TTL, respuesta cacheada, atomicidad distribuida |
| conciliación referencia/monto/moneda | `OPERATIVE_LOCAL` | `core/reconciliation.py` + pruebas | estado, fees, FX, lotes, fechas y workflow de excepciones |
| HTTP JSON | `OPERATIVE_LOCAL` | `core/http.py` + pruebas | proxy/mTLS, telemetría y redacción del entorno anfitrión |
| firma de webhooks Khipu/MP | `OPERATIVE_LOCAL` | HMAC, tiempo constante y ventana de frescura + pruebas | deduplicación/inbox persistente, rate limit y gestión real de secretos |
| motor DEMO | `OPERATIVE_LOCAL` | 28 familias × 4 situaciones verificadas | escenarios especializados por proveedor y persistencia |
| portal localhost | `OPERATIVE_LOCAL` | API, UI responsive y pruebas HTTP | persistencia, autenticación y despliegue compartido |
| diagnóstico de modos | `OPERATIVE_LOCAL` | `paylab doctor` | prueba de conectividad/autorización contra cada sandbox |
| Khipu v3 | `REQUIRES_CREDENTIALS` | adapter + guía de punta a punta | prueba live, devolución habilitada y conciliación propia |
| Mercado Pago Payments | `REQUIRES_CREDENTIALS` | adapter + guía de punta a punta | prueba live, estados por producto y conciliación propia |
| Webpay Plus REST | `REQUIRES_CREDENTIALS` | adapter + CLI | flujo navegador, timeout/commit y certificación propia |
| Oneclick Mall | `REQUIRES_CERTIFICATION` | inscripción, cobro, status, refund y baja | contrato comercial, certificación y prueba live |
| resto del catálogo | `DOCUMENTED` o acceso externo | catálogo y docs | adaptador, pruebas contractuales y evidencia oficial |

> [!CAUTION]
> `REQUIRES_CREDENTIALS` no afirma que se haya ejecutado una transacción real desde este checkout. Los tests automatizados no hacen cargos ni consumen credenciales.

## Definition of Done de un rail

Para elevar una familia a integración certificable se requiere:

- contrato oficial y versionado; sandbox/certificación identificado;
- secrets y autenticación sin valores embebidos;
- create/status y operaciones complementarias reales;
- tabla exhaustiva de estados y errores;
- idempotencia o estrategia anti-duplicado demostrada;
- webhook autenticado, deduplicado y recuperación por polling;
- timeout antes/después de enviar y `UNKNOWN` resuelto;
- reversal/refund/return/dispute cuando aplique;
- ledger, fees, settlement y conciliación;
- pruebas unitarias, contractuales, fault injection y evidencia sanitizada;
- runbook, SLO, alertas, rollback y owner;
- aprobación contractual, seguridad y cumplimiento.

## Conteos actuales

Los conteos se verifican con `python scripts/verify_repository.py`; no se mantienen manualmente en esta página para evitar drift. La fuente canónica de familias y madurez es `config/payment_rails.yaml`.
