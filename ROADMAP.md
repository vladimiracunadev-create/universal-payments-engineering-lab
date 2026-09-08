# Roadmap integral

Este roadmap separa lo que **funciona hoy** de lo que requiere especialización, credenciales, certificación, hardware o infraestructura productiva. Una fase solo cambia de estado cuando código, pruebas, documentación y evidencia coinciden.

## Estado actual

Disponible en localhost:

- portal y API local sin dependencias externas;
- 28 familias ejecutables en DEMO;
- cuatro situaciones transversales: éxito, timeout recuperado, duplicado y diferencia de conciliación;
- diagnóstico de Python, catálogo y credenciales;
- estados, idempotencia, ledger y conciliación en memoria;
- adaptadores HTTP para Khipu, Mercado Pago, Webpay Plus y Oneclick.

Los recorridos DEMO actuales son modelos pedagógicos por tipo de rail. Las siguientes fases añaden semántica especializada y ambientes oficiales.

## Entregas

### Fase 1 — Producto local reproducible

Estado: **en desarrollo activo**

- portal localhost accesible y responsive;
- CLI `doctor`, `demo` y `serve`;
- API de catálogo, salud y escenarios;
- assets y configuración incluidos en el wheel;
- smoke test del paquete instalado;
- scripts de arranque para Windows;
- documentación inicial orientada a tareas.

### Fase 2 — Núcleo transaccional persistente

- `PaymentIntent` y `PaymentAttempt` con identificadores y timestamps;
- SQLite local con migraciones y restricciones únicas;
- idempotencia atómica con fingerprint, respuesta y TTL;
- inbox/outbox persistentes;
- deduplicación real de eventos;
- recovery scheduler para `UNKNOWN`;
- ledger con referencias únicas, cuentas y journals compensatorios;
- conciliación con estado, fees, neto, fechas y lotes;
- exportación de evidencia sanitizada.

### Fase 3 — DEMO especializado por familia

- estados y errores propios de cada rail;
- payloads y eventos didácticos fieles a su semántica;
- refunds, reversals, returns, disputas y chargebacks donde correspondan;
- settlement y conciliación específicos;
- fault injection configurable;
- diagramas y guías enlazados desde el resultado.

### Fase 4 — SANDBOX de proveedores

- Khipu: create, query, delete, bancos y webhook;
- Mercado Pago: create, query, refund y webhook;
- Webpay Plus: create, retorno, commit, status y refund;
- Oneclick: inscripción, autorización por tienda, status, refund y baja;
- contract tests contra stubs grabados y, separadamente, sandbox autorizado;
- selector explícito de ambiente y bloqueo de endpoints productivos por defecto;
- evidencia privada y sanitizada por ejecución.

### Fase 5 — Plataforma operativa

- Payments API versionada;
- routing por capacidad, país, moneda y salud;
- policy/risk engine y aprobación humana;
- observabilidad, métricas, trazas y SLO;
- dashboard de `UNKNOWN`, webhooks, ledger y conciliación;
- backups, recovery, DR y runbooks ejecutables;
- contenedores y distribución Windows.

### Fase 6 — Certificación y LIVE controlado

- checklist contractual por proveedor;
- segregación de credenciales y ambientes;
- límites monetarios y kill switch;
- pruebas de certificación requeridas;
- transacción propia de monto aprobado y reversa;
- conciliación con abono bancario;
- aprobación de seguridad, negocio, legal y cumplimiento.

## Matriz de los 28 casos

| Caso | DEMO actual | Próxima capacidad | Dependencia externa |
|---|---|---|---|
| Efectivo | recorrido genérico de valor físico | caja, arqueo y depósito especializado | operación física |
| Papel/cheque | recorrido genérico diferido | clearing, protesto y devolución | banco/cámara |
| Tarjetas | autorización/captura simuladas | ISO 8583, 3DS, dispute y chargeback | adquirente/red |
| Webpay Plus | flujo de tarjeta + adapter | sandbox completo y callback local | comercio Transbank |
| Oneclick | flujo de credencial + adapter | inscripción/cobro sandbox | contrato/certificación |
| Khipu | flujo A2A + adapter | sandbox y webhook local | cuenta y API key |
| Mercado Pago | flujo PSP + adapter | sandbox por producto | aplicación y token |
| POS/mPOS/SoftPOS | flujo presencial conceptual | EMV/CVM y simulador de terminal | hardware/certificación |
| Wallet tokenizada | token/criptograma conceptual | wallet sandbox y token de red | wallet/red |
| Stored value | débito de saldo simulado | ledger de saldo, expiración y reversa | licencia según modelo |
| Mobile money | movimiento de e-money | agentes, cash-in/out y límites | operador |
| QR | iniciación simulada | MPM/CPM, CRC y expiración | esquema/proveedor |
| Transferencia | flujo A2A | beneficiarios, polling y abono | banco/API |
| ACH | flujo batch | archivos, returns y ventanas | operador ACH |
| Débito directo | cobro con mandato | lifecycle y devoluciones | banco/mandato |
| Instant payments | confirmación inmediata | perfiles Pix/UPI/SPEI/FedNow/RTP/FPS/SCT Inst | participante/PSP |
| Payment initiation | link/solicitud | expiración, firma y atribución | proveedor |
| Cash voucher | referencia física | barcode, red y confirmación | red de recaudación |
| BNPL | crédito y cuotas | underwriting, disclosures y mora | financiador |
| Carrier billing | cargo telecom | OTP, límites y settlement | operador móvil |
| Marketplace | split simulado | subcuentas, reservas y payouts | PSP/KYB |
| B2B | aprobación simulada | ERP/EDI, roles y pagos masivos | banco/ERP |
| Internacional | cadena transfronteriza | SWIFT, FX, sanciones y tracking | bancos/corresponsales |
| Alto valor | liquidación conceptual | cola, liquidez y finalidad RTGS | banco central/participante |
| Open Finance | consentimiento conceptual | FAPI, mTLS/DPoP y PIS | autorización/banco |
| Activos digitales | firma/confirmación conceptual | nodo, wallet, Lightning y custodia | red/custodio |
| Máquina a máquina | política por uso | identidad, metering y credencial | dispositivo/proveedor |
| Agentic payments | mandato y límites | intent verificable, approval y post-compra | proveedor/policy |

## Tecnologías por desarrollar

| Dominio | Tecnologías |
|---|---|
| API y eventos | REST, webhooks, polling, outbox/inbox, colas, gRPC |
| Mensajería financiera | ISO 8583, ISO 20022, SWIFT y formatos batch |
| Tarjetas | EMV L1/L2/L3, 3DS, network tokens, HSM y PCI DSS |
| Identidad y consentimiento | OAuth 2.0, OIDC, FAPI 2, PAR, DPoP, mTLS y PKI |
| Aceptación | QR MPM/CPM, NFC, POS, mPOS, SoftPOS y Tap to Pay |
| Dinero y contabilidad | ledger de doble partida, fees, reservas, FX, settlement y payouts |
| Operación | retries, circuit breaking, recovery, conciliación, SLO y observabilidad |
| Riesgo y cumplimiento | fraude, AML/CFT, sanciones, privacidad, disputas y chargebacks |
| Activos digitales | wallets, signing, nodos, indexers, Lightning y custodia |
| Automatización | identidad de dispositivo, metering, policy engine, mandatos y aprobación humana |

## Gates obligatorios por entrega

1. Tests unitarios, contractuales e integrales verdes.
2. Ruff y verificador de coherencia verdes.
3. Build de sdist y wheel reproducible.
4. Instalación del wheel en un entorno limpio y smoke test de `doctor`, `catalog`, `demo` y `serve`.
5. Captura del portal para cambios visuales.
6. Revisión de secretos, encoding y acciones fijadas a SHA.
7. Commit acotado, push a `main` y GitHub Actions verde.

## Regla de seguridad

Un fallo de transporte no demuestra un fallo financiero. Después de enviar una mutación SANDBOX/LIVE, cualquier timeout produce `UNKNOWN` y recuperación; jamás un fallback DEMO.
