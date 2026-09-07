# ⚖️ Mapa regulatorio y de estándares

> [!WARNING]
> Material educativo, no asesoría legal ni de cumplimiento. La obligación depende de país, rol, flujo de fondos, instrumento, datos y contrato. Verifica siempre la norma y guía vigentes con la autoridad y profesionales competentes.

## Método de análisis

1. Identificar jurisdicciones del pagador, comercio, entidad y settlement.
2. Dibujar actores, contratos y quién toca fondos/datos.
3. Clasificar instrumento, canal, rail y modelo push/pull.
4. Determinar licencias/registros y reglas de esquema.
5. Mapear datos de cuenta, PII, autenticación y retención.
6. Evaluar AML/CFT, sanciones, fraude, consumidor, disputas e impuestos según rol.
7. Establecer resiliencia, outsourcing, auditoría y reporte de incidentes.
8. Conservar versión, fecha, owner y evidencia de cada obligación.

## Chile-first

| Dominio | Pregunta | Fuente primaria |
|---|---|---|
| sistemas de pago | ¿Es bajo/alto valor, cámara, operador o participante? | [Banco Central de Chile — Sistemas de pagos](https://www.bcentral.cl/areas/sistemas-de-pagos) |
| normativa financiera | ¿Qué capítulo del CNF aplica a tarjetas, cámaras o LBTR? | [Compendio de Normas Financieras](https://www.bcentral.cl/areas/normativas/compendio-de-normas-financieras) |
| fintech/Open Finance | ¿El rol queda dentro de Ley 21.521 y NCG 514/SFA? | [CMF — portal normativa](https://www.cmfchile.cl/portal/principal/613/w3-channel.html) |
| datos personales | ¿Base, finalidad, seguridad, derechos y transferencias? | [BCN — legislación chilena](https://www.bcn.cl/leychile/) |
| consumidor | ¿Información, cargos, reversas y responsabilidad? | [SERNAC](https://www.sernac.cl/) |
| AML/CFT | ¿La entidad es sujeto obligado y qué reporta? | [UAF Chile](https://www.uaf.cl/) |

El Banco Central distingue sistemas de alto valor (incluido LBTR) y bajo valor; las tarjetas, TEF, cheques y cajeros tienen reglas e infraestructuras propias. La implementación del Sistema de Finanzas Abiertas es dinámica: antes de construir, releer la NCG 514 y su anexo técnico vigente, no una copia de este documento.

## Estándares y marcos globales

| Tema | Alcance | Fuente primaria |
|---|---|---|
| datos de tarjeta | baseline técnico/operativo para account data | [PCI DSS y biblioteca PCI SSC](https://www.pcisecuritystandards.org/document_library/) |
| EMV | chip/contactless, 3DS, tokenización, SRC y QR | [EMVCo Technologies](https://www.emvco.com/emv-technologies/) |
| infraestructuras | finalidad, riesgo de crédito/liquidez, continuidad | [CPMI-IOSCO PFMI](https://www.bis.org/committees/cpmi/pfmi/overview) |
| mensajes | definiciones versionadas para pagos y reporting | [ISO 20022 Catalogue](https://www.iso20022.org/catalogue-messages) |
| API financiera | perfil OAuth de alta seguridad | [FAPI 2.0](https://openid.net/specs/fapi-security-profile-2_0-final.html) |
| OAuth | mejores prácticas actuales de seguridad | [RFC 9700](https://www.rfc-editor.org/rfc/rfc9700.html) |

PCI es un estándar de industria, no una licencia financiera. EMV define interoperabilidad y pruebas, no reemplaza reglas de cada esquema/adquirente. ISO 20022 es un modelo de mensajes; cada comunidad tiene su usage guideline. Cumplir uno no implica cumplir los demás.

## Checklist por modelo

### Comercio que acepta pagos

Contrato de adquirencia/PSP, PCI y checkout, información al consumidor, impuestos/documentos, fraude, refunds/disputes, conciliación, privacidad y continuidad.

### PSP/orquestador/marketplace

Licencia o exclusión, flujo/custodia de fondos, safeguarding, KYB/KYC y beneficiario efectivo, AML/sanciones, subcomercios, reservas/payouts, outsourcing, capital/garantías, reportes, auditoría y resolución.

### Payment initiation/Open Finance

Registro, directorio y certificados, consentimiento, FAPI/perfil local, redirect/app-to-app, SCA si aplica, alcance/finalidad, revocación, incidentes, terceros y evidencia.

### Activos digitales

Clasificación del activo/servicio, custodia, transferencias, Travel Rule cuando aplique, AML/sanciones, reservas/redención de stablecoin, divulgación de riesgo, contabilidad/impuestos y ciberseguridad de claves.

## Registro de decisiones

Toda integración real debería producir una matriz con `requirement_id`, fuente enlazada, versión/fecha, aplicabilidad, control, evidencia, owner, frecuencia de revisión y excepción. No copies texto normativo extenso: enlaza la fuente, traduce la obligación a un control verificable y registra la interpretación profesional.

**Revisión documental:** 7 de septiembre de 2026. Las fuentes dinámicas deben revalidarse antes de uso real.
