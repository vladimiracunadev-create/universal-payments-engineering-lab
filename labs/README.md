# 🧪 Laboratorios

Los laboratorios avanzan por nivel de riesgo. Empieza local; la ejecución externa exige autorización y evidencia.

| Nivel | Dinero real | Dependencias | Objetivo |
|---|---:|---|---|
| 0 — core local | no | Python | estados, idempotencia, ledger y conciliación |
| 1 — fault lab | no | software local | fallos sin fingir un rail real |
| 2 — certificación | no/según proveedor | credenciales oficiales | demostrar contrato y estados |
| 3 — controlled live | sí, monto aprobado | cuenta propia | validar extremo a extremo y refund |
| 4 — production readiness | sí | organización autorizada | gates de operación, seguridad y compliance |

## Nivel 0

```bash
python -m unittest discover -s tests -v
python scripts/paylab.py doctor
python scripts/paylab.py demo chile-webpay --scenario timeout-recovered
python scripts/paylab.py serve
python scripts/paylab.py states
python scripts/paylab.py catalog
python scripts/verify_repository.py
```

Criterio: tests verdes, portal accesible en localhost, catálogo legible y
capacidad de explicar por qué `TIMEOUT` no es `DECLINED`.

## Evidencia común

Usa `labs/certification/LAB-CONTRACT.yaml` como plantilla. Toda evidencia externa es privada y sanitizada. Registra UTC, entorno, commit, proveedor, IDs no sensibles, transición, consulta, operación compensatoria y resultado de conciliación.

Continúa con [certificación](certification/README.md), [controlled live](controlled-live/README.md), [reconciliación](reconciliation/README.md) y [production readiness](production/README.md).
