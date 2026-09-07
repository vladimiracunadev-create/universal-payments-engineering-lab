# 🔴 Controlled live

Una prueba live mueve dinero real y solo procede con cuenta/instrumento propios, autorización, monto máximo, destinatario verificado y plan de devolución.

## Checklist go/no-go

- certificación previa aprobada;
- credencial productiva cargada desde secret manager;
- owner técnico, financiero y contacto del proveedor;
- orden y monto aprobados por escrito;
- dashboard/logs sanitizados y reloj UTC;
- status, refund/reversal y conciliación disponibles;
- prohibido retry manual si el resultado es incierto.

## Secuencia

Crear un pago, completar autenticación, consultar servidor-a-servidor, verificar ledger, observar evento, ejecutar refund si ese es el objetivo, consultar de nuevo y cerrar contra settlement/abono. Conservar la evidencia fuera del repositorio público.

## Abort conditions

Destino/monto inesperado, certificado o secreto dudoso, reloj desincronizado, observabilidad ausente, método de refund desconocido, respuesta contradictoria o cualquier dato real apareciendo en logs.
