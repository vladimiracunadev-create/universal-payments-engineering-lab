# 🔐 Política de seguridad

## Reportar una vulnerabilidad

No abras un issue público con secretos, datos personales o detalles explotables. Usa el reporte privado de vulnerabilidades de GitHub del repositorio. Incluye componente, versión/commit, impacto, reproducción mínima y mitigación sugerida; reemplaza toda credencial y dato real por valores sintéticos.

Este es un proyecto educativo mantenido según disponibilidad; no existe SLA comercial. Se confirmará recepción y se coordinará divulgación responsable cuando el canal esté disponible.

## Reglas no negociables

1. Secretos solo desde entorno o secret manager; nunca Git, fixtures, ejemplos o logs.
2. Nunca almacenar CVV/CVC/CID, PIN, track data ni claves privadas/seeds.
3. No usar PAN ni identidades reales en pruebas.
4. TLS para servicios externos; mTLS/firma cuando el contrato lo exija.
5. Idempotencia en toda mutación monetaria que lo permita.
6. Tras timeout, consultar estado antes de crear un segundo efecto.
7. Verificar webhooks con el mecanismo oficial y deduplicarlos persistentemente.
8. Separar credenciales y datos de test/certificación/producción.
9. Ledger append-only y reconciliación contra proveedor y banco.
10. Menor privilegio, rotación, auditoría y doble control para refunds/payouts sensibles.

## Uso autorizado

Solo ejecuta contra cuentas, comercios, instrumentos y ambientes propios o expresamente autorizados. No realices card testing, enumeración, bypass de controles, pruebas de carga ni ataques contra proveedores desde este laboratorio.

Consulta el [threat model](docs/security/THREAT_MODEL.md), el [runbook](docs/operations/RUNBOOK.md) y el [mapa regulatorio](docs/regulations/README.md).
