# Guía del producto

## La idea en una frase

PayLab permite seleccionar una tecnología de pago, ejecutar un recorrido seguro en localhost y observar qué ocurre en cada etapa sin necesitar dinero ni credenciales.

## Cómo usarlo

1. Ejecuta `python scripts/paylab.py doctor`.
2. Levanta `python scripts/paylab.py serve`.
3. Abre `http://127.0.0.1:8080`.
4. Selecciona una familia.
5. Elige una situación:
   - **éxito:** todas las fuentes coinciden;
   - **timeout recuperado:** la respuesta se pierde, se consulta y no se duplica el efecto;
   - **evento duplicado:** el inbox reconoce la repetición;
   - **diferencia de conciliación:** el monto externo no coincide y se abre una excepción.
6. Lee el recorrido de arriba abajo: actor, estado, explicación y evidencia.
7. Revisa el asiento y la conciliación al final.

## Qué demuestra y qué no

El modo DEMO demuestra comportamiento del software: transiciones, decisiones seguras, asiento balanceado y detección de diferencias. No demuestra conectividad, contrato, certificación, autorización del emisor ni settlement bancario.

SANDBOX y LIVE se habilitan por proveedor. La ausencia de credenciales nunca convierte una operación externa iniciada en DEMO.

## Los 28 casos

| Caso | Qué problema resuelve | Qué se observa en DEMO |
|---|---|---|
| Efectivo y caja | recibir valor físico | custodia, recepción, depósito y conciliación |
| Cheques y papel | cobrar una orden documental diferida | presentación, clearing y devolución |
| Tarjetas | aceptar crédito, débito o prepago | autenticación, autorización, captura y settlement |
| Webpay Plus | aceptar tarjetas en Chile por redirección | create, retorno, commit, status y refund |
| Oneclick Mall | inscribir y cobrar una credencial almacenada | inscripción, token, detalle por tienda, refund y baja |
| Khipu | iniciar un pago cuenta a cuenta en Chile | creación, redirección, consulta y webhook |
| Mercado Pago | aceptar varios medios mediante un PSP | idempotencia, estado, webhook y refund |
| POS/mPOS/SoftPOS | aceptar un instrumento presencial | lectura, CVM, autorización y cierre de lote |
| Wallets tokenizadas | pagar con token de red y criptograma | dispositivo, token, autenticación y autorización |
| Stored value | gastar un saldo prefinanciado | reserva, débito, expiración y restitución |
| Mobile money | mover dinero electrónico por app o agentes | cash-in, P2P, pago y cash-out |
| QR | transportar datos de iniciación | creación, lectura, expiración y confirmación |
| Transferencia bancaria | mover fondos entre cuentas | beneficiario, instrucción, confirmación y abono |
| ACH | procesar créditos/débitos por lotes | archivo, clearing, settlement y return |
| Débito directo | cobrar bajo mandato | mandato, presentación, rechazo y devolución |
| Pagos instantáneos | transferir A2A en segundos | alias, request-to-pay, aceptación y finalidad |
| Links y solicitudes | iniciar un pago desde URL, QR o factura | distribución, atribución y expiración |
| Voucher en efectivo | pagar una orden digital en una red física | referencia, barcode y confirmación diferida |
| BNPL | financiar la compra | evaluación, contrato, desembolso y cuotas |
| Carrier billing | cargar a saldo o factura móvil | consentimiento, OTP, límites y settlement |
| Marketplaces | dividir un cobro entre participantes | split, comisión, reserva y payout |
| B2B | pagar facturas con aprobaciones | factura, workflow, instrucción y ERP |
| Internacional | transferir entre países | FX, sanciones, corresponsales y fecha valor |
| Alto valor/RTGS | liquidar obligaciones críticas | cola, liquidez, prioridad y finalidad |
| Open Finance | iniciar desde una cuenta con consentimiento | OAuth/FAPI, alcance, token y confirmación |
| Activos digitales | mover Bitcoin, Lightning o stablecoins | firma, broadcast, confirmaciones y custodia |
| Máquina a máquina | pagar automáticamente por uso | identidad, medición, política y presupuesto |
| Pagos agentic | delegar compras a un agente | mandato, límites, aprobación humana y auditoría |

## Cómo leer una ejecución

### Intent

Representa lo que el negocio quiere cobrar. El monto y la moneda pertenecen al servidor, no al navegador.

### Autenticación y autorización

Autenticar demuestra control del instrumento. Autorizar significa que el proveedor aceptó una operación bajo sus reglas. Ninguna de las dos confirma el abono final.

### Captura o ejecución

Es el efecto monetario que debe ser único. Una pérdida de respuesta deja resultado desconocido; no autoriza un segundo intento ciego.

### Ledger

La demostración registra dos entradas que suman cero. Eso prueba la invariante contable local, no que exista una base de datos productiva.

### Settlement y conciliación

Settlement es el movimiento final declarado por la infraestructura externa. Conciliar significa contrastar negocio, proveedor, ledger y banco; una diferencia se conserva como excepción.

## Tecnologías

El catálogo conecta cada caso con sus mecanismos relevantes:

- **mensajería:** REST/JSON, SOAP/XML, gRPC, ISO 8583, ISO 20022, archivos batch, webhooks y colas;
- **seguridad:** TLS/mTLS, OAuth/OIDC/FAPI, PKI, HSM/KMS, tokenización y PCI DSS;
- **aceptación:** EMV, NFC, QR, 3DS, POS, mPOS, SoftPOS y Tap to Pay;
- **operación:** idempotencia, polling, retries controlados, conciliación, settlement y observabilidad;
- **riesgo:** fraude, AML/CFT, sanciones, disputas, chargebacks, privacidad y protección al consumidor;
- **emergentes:** wallets, blockchain, Lightning, custodia, identidad de dispositivo y autoridad delegada.

La presencia de una tecnología en el catálogo indica que forma parte del caso y del roadmap; solo la matriz de [cobertura](operations/COVERAGE.md) indica si ya existe implementación externa.

Para decidir **qué lenguaje y API usar**, cómo contratar/probar cada modalidad y cómo operar fallos y datos bancarios, continúa con la [guía de implementación](IMPLEMENTATION_GUIDE.md). El localhost muestra ese mismo playbook al cambiar el medio de pago.
