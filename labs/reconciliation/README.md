# 🧮 Laboratorio de conciliación

## Objetivo

Comparar al menos orden, intento, referencia del proveedor, monto bruto, moneda, estado, fee, neto, fecha de proceso, lote y abono. El núcleo actual cubre referencia/monto/moneda; el resto es extensión requerida.

## Dataset sintético

Prepara casos matched, local-only, remote-only, amount/currency/state/fee mismatch, duplicate y missing settlement. Ejecuta `reconcile`, verifica clasificación y diseña owner/SLA para cada diferencia.

## Aceptación

Totales de control por moneda cuadran; rerun no duplica casos; ninguna diferencia se cierra sin evidencia; los asientos correctivos son compensatorios; settlement se vincula a banco. Desarrollo completo en [Conciliación y settlement](../../docs/operations/RECONCILIATION_SETTLEMENT.md).
