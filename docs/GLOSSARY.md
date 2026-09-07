# 📖 Glosario operacional de pagos

| Término | Definición operacional |
|---|---|
| **adquirente** | entidad que habilita la aceptación del comercio y presenta transacciones hacia una red o sistema |
| **autenticación** | evidencia de control de una credencial, dispositivo o factor; no equivale a autorización financiera |
| **autorización** | decisión del emisor/proveedor de aceptar o rechazar y, según el rail, reservar fondos o línea |
| **captura** | confirmación de que una autorización debe presentarse para clearing |
| **chargeback** | reversión disputada bajo reglas de un esquema; no es un refund voluntario |
| **clearing** | validación, intercambio y cálculo de obligaciones antes de liquidar |
| **credencial almacenada** | referencia para usos posteriores, gobernada por consentimiento/mandato y reglas del esquema |
| **emisor** | entidad que provee cuenta o instrumento al pagador y toma la decisión de autorización |
| **finalidad** | punto legal y operativo desde el cual la liquidación es irrevocable |
| **gateway** | capa tecnológica entre comercio y procesador/adquirente; puede no mover fondos |
| **idempotencia** | repetir la misma intención identificada no crea un segundo efecto monetario |
| **instrumento** | mecanismo para ordenar o consentir: tarjeta, cuenta, efectivo, mandato o wallet |
| **ledger** | registro de efectos financieros; en doble partida, cada asiento balancea por moneda |
| **mandato** | autorización persistente para cobros iniciados por el beneficiario bajo condiciones acordadas |
| **orquestador** | capa que normaliza y enruta hacia proveedores sin borrar diferencias del rail |
| **PAN** | número primario de cuenta de tarjeta; dato sujeto a controles específicos |
| **payment intent** | intención comercial estable y su progreso, separada de cada intento |
| **PSP** | proveedor de servicios de pago; el alcance legal varía por jurisdicción |
| **rail** | reglas, mensajería y participantes que transportan y liquidan valor |
| **reconciliación** | comparación de negocio, proveedor, ledger, clearing y banco para explicar diferencias |
| **refund** | nueva operación que devuelve valor tras un cobro; no borra el original |
| **reversal** | liberación o anulación antes o durante la presentación, según el rail |
| **settlement** | descarga de obligaciones mediante transferencia del activo de liquidación |
| **switch** | componente que enruta y transforma mensajes entre participantes |
| **token de pago** | sustituto de PAN/credencial, restringible por dispositivo, comercio o uso |
| **webhook** | notificación servidor-a-servidor que debe autenticarse, deduplicarse y validarse |

Referencia terminológica: [glosario del CPMI/BIS](https://www.bis.org/cpmi/publ/d00b.htm).
