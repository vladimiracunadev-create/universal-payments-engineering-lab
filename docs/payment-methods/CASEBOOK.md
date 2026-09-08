# 🧩 Los 28 casos: del concepto al desarrollo

> ¿Quieres comparar los casos sin saltar entre secciones? Abre primero la [tabla de comienzo a fin](END_TO_END_MATRIX.html).

Cada caso responde cuatro preguntas: cómo imaginarlo, qué construir primero, qué prueba el éxito y qué falta antes de producción. Ejecuta el caso en localhost y contrasta el resultado con esta guía.

## Valor físico y documentario

### 1. Efectivo y caja

- **Imagínalo:** el dinero cambia de manos ahora; la evidencia y el depósito llegan después.
- **Primer desarrollo:** apertura por responsable → recibo por recepción → cierre/depósito por turno.
- **Prueba de éxito:** recibo, arqueo y depósito comparten referencia y la diferencia es explícita.
- **Antes de LIVE:** segregación de funciones, custodia, seguros y conciliación bancaria.

### 2. Cheques y papel

- **Imagínalo:** recibir el documento no equivale a cobrarlo.
- **Primer desarrollo:** registrar instrumento → mantener pendiente durante clearing → aplicar abono o devolución.
- **Prueba de éxito:** confirmación bancaria sin return dentro de la ventana aplicable.
- **Antes de LIVE:** política de imágenes/datos, fraude documental y plazos por jurisdicción.

### 3. Voucher pagable en efectivo

- **Imagínalo:** una orden digital se liquida en una red física.
- **Primer desarrollo:** referencia/barcode con expiración → recepción del recaudador → conciliación diferida.
- **Prueba de éxito:** la misma referencia aparece pagada y liquidada una sola vez.
- **Antes de LIVE:** contrato con red, prevención de reutilización y archivos de settlement.

## Tarjetas, dispositivos y wallets

### 4. Tarjetas

- **Imagínalo:** autorizar, capturar, liquidar y disputar son hechos separados.
- **Primer desarrollo:** checkout alojado/tokenización → intent → webhook → ledger → settlement.
- **Prueba de éxito:** ID capturado, evento autenticado y línea conciliada.
- **Antes de LIVE:** alcance PCI DSS, 3DS, fraude, refund y chargeback.

### 5. Transbank Webpay Plus

- **Imagínalo:** tu backend crea; Transbank presenta el pago; tu backend confirma el token.
- **Primer desarrollo:** create → redirección → commit único → status ante timeout.
- **Prueba de éxito:** token confirmado y reporte del comercio conciliado.
- **Configuración:** `TRANSBANK_COMMERCE_CODE`, `TRANSBANK_API_KEY` y `TRANSBANK_BASE_URL`.

### 6. Transbank Oneclick Mall

- **Imagínalo:** primero se inscribe una tarjeta; después se cobra con `tbk_user`.
- **Primer desarrollo:** start/finish inscripción → token protegido → authorize/status/refund/delete.
- **Prueba de éxito:** consentimiento, inscripción y autorización por tienda auditables.
- **Antes de LIVE:** límites, fraude, baja y cifrado de la credencial tokenizada.

### 7. Mercado Pago

- **Imagínalo:** el frontend tokeniza o redirige; el access token vive en backend.
- **Primer desarrollo:** aplicación test → inicio/token → creación idempotente → webhook/consulta.
- **Prueba de éxito:** payment/order ID aprobado y movimiento conciliado.
- **Configuración:** `MERCADOPAGO_ACCESS_TOKEN` solo en el proceso servidor.

### 8. POS, mPOS y SoftPOS

- **Imagínalo:** el dispositivo certificado autentica; la caja fija el monto.
- **Primer desarrollo:** terminal/SDK → solicitud desde caja → resultado → cierre de lote.
- **Prueba de éxito:** voucher, terminal, autorización y lote coinciden.
- **Antes de LIVE:** certificación, gestión de dispositivos, PCI y soporte en tienda.

### 9. Wallets tokenizadas

- **Imagínalo:** la wallet entrega token de red y criptograma, no PAN real.
- **Primer desarrollo:** registro de dominio/app → validación de token → procesamiento por PSP.
- **Prueba de éxito:** criptograma aceptado y autorización con referencia de red.
- **Antes de LIVE:** certificación de wallet, gestión de claves y fallback controlado.

## Cuenta a cuenta

### 10. Khipu

- **Imagínalo:** el cliente autoriza en su banco; el comercio conserva referencia y estado.
- **Primer desarrollo:** crear → abrir experiencia → webhook autenticado → consulta por payment ID.
- **Prueba de éxito:** API/evento y abono coinciden.
- **Configuración:** `KHIPU_API_KEY` y callbacks HTTPS autorizados.

### 11. Transferencia bancaria

- **Imagínalo:** un comprobante visual no prueba el abono.
- **Primer desarrollo:** beneficiario/referencia → instrucción o espera → cartola/API → conciliación.
- **Prueba de éxito:** movimiento bancario autoritativo con monto, moneda y referencia.
- **Antes de LIVE:** validación de beneficiario, fraude y permisos bancarios.

### 12. ACH y batch

- **Imagínalo:** el lote se acepta ahora y cada entry puede liquidar o volver después.
- **Primer desarrollo:** generar/validar lote → controlar ventana/totales → settlement/returns.
- **Prueba de éxito:** acuse, entry y return code conciliados.
- **Antes de LIVE:** acuerdo con ODFI/operador, NACHA o norma local y cutoffs.

### 13. Débito directo

- **Imagínalo:** el cobro depende de un mandato revocable.
- **Primer desarrollo:** consentimiento versionado → presentación → rechazo/return → conciliación.
- **Prueba de éxito:** mandato vigente y settlement sin devolución.
- **Antes de LIVE:** reglas de notificación, revocación y protección del consumidor.

### 14. Pagos instantáneos

- **Imagínalo:** rapidez no elimina idempotencia ni conciliación.
- **Primer desarrollo:** resolver alias → instrucción/request-to-pay → confirmación final.
- **Prueba de éxito:** ID end-to-end con finalidad declarada por el rail.
- **Antes de LIVE:** límites, fraude en tiempo real y operación 24/7.

### 15. Open Finance

- **Imagínalo:** la aplicación solo actúa dentro del consentimiento otorgado.
- **Primer desarrollo:** registro TPP → FAPI/PKCE → consentimiento → token ligado → payment ID.
- **Prueba de éxito:** consentimiento, alcance y confirmación reproducibles.
- **Antes de LIVE:** licencia/registro, certificados, mTLS y regulación local.

## Experiencias de iniciación

### 16. QR

- **Imagínalo:** el QR inicia; no confirma.
- **Primer desarrollo:** QR estático/dinámico → validación/expiración → confirmación por rail.
- **Prueba de éxito:** QR único ligado a un evento autoritativo.
- **Antes de LIVE:** estándar interoperable, firma, límites y fraude de sustitución.

### 17. Links y solicitudes de pago

- **Imagínalo:** el link conecta orden y experiencia; otro rail mueve el valor.
- **Primer desarrollo:** orden expirable → URL firmada → atribución del resultado.
- **Prueba de éxito:** orden, apertura y confirmación comparten referencia.
- **Antes de LIVE:** anti-phishing, dominio, expiración y reuso.

## Saldos, mobile y crédito

### 18. Stored value y gift cards

- **Imagínalo:** el programa mantiene su propio saldo.
- **Primer desarrollo:** cuenta → reserva atómica → captura/liberación → expiración.
- **Prueba de éxito:** saldo anterior + journals = saldo nuevo.
- **Antes de LIVE:** pasivo financiero, fraude, breakage y normativa.

### 19. Mobile money

- **Imagínalo:** el valor entra, circula y sale entre cliente, agente y operador.
- **Primer desarrollo:** identidad/cuenta → cash-in → pago → cash-out → float.
- **Prueba de éxito:** referencia del operador y saldos de agentes cuadrados.
- **Antes de LIVE:** KYC, red de agentes, liquidez y límites.

### 20. BNPL y crédito alternativo

- **Imagínalo:** el financiador paga al comercio; el cliente adquiere cuotas.
- **Primer desarrollo:** evaluación → consentimiento/costo total → desembolso → servicing.
- **Prueba de éxito:** contrato, desembolso y calendario contable.
- **Antes de LIVE:** licencia, reporting crediticio, mora y protección al consumidor.

### 21. Carrier billing

- **Imagínalo:** el operador carga a factura o saldo móvil.
- **Primer desarrollo:** elegibilidad → consentimiento/OTP → cargo → settlement.
- **Prueba de éxito:** consentimiento, transaction ID y reporte del operador.
- **Antes de LIVE:** límites, suscripciones, reclamos y reparto de ingresos.

## Plataformas y empresas

### 22. Marketplaces, splits y payouts

- **Imagínalo:** un bruto se divide entre participantes, comisión, reserva y payout.
- **Primer desarrollo:** onboarding/KYB → split inmutable → subledger → payout.
- **Prueba de éxito:** bruto = netos + comisión + reserva.
- **Antes de LIVE:** safeguarding, impuestos, riesgo y licencias.

### 23. B2B y tesorería

- **Imagínalo:** la factura cruza aprobaciones, banco y ERP.
- **Primer desarrollo:** ingestión → segregación/aprobación → pago → remittance.
- **Prueba de éxito:** factura, instrucción y asiento ERP comparten referencia.
- **Antes de LIVE:** poderes, doble aprobación, sanciones y continuidad.

### 24. Internacional

- **Imagínalo:** FX, fees, corresponsales y fecha valor alteran lo recibido.
- **Primer desarrollo:** cotización → screening → instrucción → tracking/settlement.
- **Prueba de éxito:** tasa, fees, referencia y monto recibido son explicables.
- **Antes de LIVE:** licencias, AML/CFT, sanciones y corredores.

### 25. RTGS y alto valor

- **Imagínalo:** la instrucción puede esperar liquidez, pero su finalidad debe ser inequívoca.
- **Primer desarrollo:** canal autorizado → aprobación dual → cola/prioridad → finalidad.
- **Prueba de éxito:** aceptación RTGS con timestamp y conciliación intradía.
- **Antes de LIVE:** acceso institucional, PKI/HSM y operación crítica.

## Activos y autoridad delegada

### 26. Bitcoin, Lightning y activos digitales

- **Imagínalo:** la firma autoriza; custodia y confirmaciones determinan el riesgo.
- **Primer desarrollo:** elegir red/custodia → address/invoice → broadcast → confirmación.
- **Prueba de éxito:** transaction ID o payment hash ligado a la orden.
- **Antes de LIVE:** claves, fees, volatilidad, compliance y recovery.

### 27. Máquina a máquina

- **Imagínalo:** el dispositivo paga dentro de presupuesto, uso y tiempo.
- **Primer desarrollo:** identidad → medición → política → credencial limitada → settlement.
- **Prueba de éxito:** identidad, consumo y decisión están unidos.
- **Antes de LIVE:** attestation, revocación, límites y seguridad física.

### 28. Pagos agentic

- **Imagínalo:** el agente ejecuta un mandato, no una autoridad ilimitada.
- **Primer desarrollo:** mandato/presupuesto → política → aprobación humana → pago.
- **Prueba de éxito:** mandato, decisión, aprobación y referencia son reproducibles.
- **Antes de LIVE:** identidad del agente, responsabilidad, fraude y auditoría.

## Regla de cierre

Un caso pasa de “DEMO comprensible” a “desarrollo real” cuando existe un proveedor concreto, configuración separada, prueba autoritativa, recuperación de fallos, persistencia, ledger y conciliación. Pasa a LIVE solo con contrato, seguridad, operación y regulación verificadas.
