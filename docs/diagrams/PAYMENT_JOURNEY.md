# 📊 Diagramas para comprender un pago

## 1. Quién hace qué

```mermaid
flowchart LR
    U[Persona\nelige pagar] --> F[Frontend\nmuestra experiencia]
    F --> B[Backend del comercio\nfija monto y referencia]
    B --> P[Proveedor\nautoriza o procesa]
    P -->|API / webhook| B
    B --> L[Ledger\nregistra efecto único]
    P --> S[Settlement\nreporte o abono]
    L --> C[Conciliación]
    S --> C
```

La frontera crítica está entre frontend y backend: el navegador puede iniciar la experiencia, pero no decide el monto final ni guarda la llave secreta.

## 2. Estado técnico frente a dinero

```mermaid
stateDiagram-v2
    [*] --> CREATED: orden creada
    CREATED --> REQUIRES_AUTHENTICATION: falta acción del pagador
    CREATED --> PROCESSING: proveedor aceptó procesar
    REQUIRES_AUTHENTICATION --> AUTHORIZED: instrumento aprobado
    AUTHORIZED --> CAPTURED: efecto confirmado
    PROCESSING --> UNKNOWN: respuesta perdida
    UNKNOWN --> CAPTURED: consulta recupera resultado
    CAPTURED --> SETTLED: proveedor declara liquidación
    SETTLED --> RECONCILED: fuentes coinciden
    SETTLED --> RECONCILIATION_EXCEPTION: existe diferencia
```

`AUTHORIZED` responde “¿el proveedor aprobó?”. `SETTLED` responde “¿el proveedor declaró el movimiento?”. `RECONCILED` responde “¿nuestras fuentes coinciden?”.

## 3. Timeout seguro

```mermaid
sequenceDiagram
    participant C as Comercio
    participant P as Proveedor
    C->>P: cobrar(ref=ABC, idempotency=XYZ)
    P->>P: procesa una vez
    P--xC: respuesta se pierde
    Note over C: Estado UNKNOWN
    C->>P: consultar(ref=ABC)
    P-->>C: resultado original
    Note over C: No se creó otro cobro
```

La consulta no es un segundo pago. Usa la referencia del primer intento para descubrir el hecho que ya pudo ocurrir.

## 4. Webhook repetido

```mermaid
flowchart TD
    W[Webhook recibido] --> A{¿firma y tiempo válidos?}
    A -- no --> R[Rechazar y registrar]
    A -- sí --> I{¿event ID ya existe?}
    I -- sí --> OK[Responder OK\nsin repetir efecto]
    I -- no --> P[Persistir evento]
    P --> M[Aplicar transición permitida]
    M --> L[Actualizar ledger una vez]
```

Verificar la firma no deduplica. La deduplicación necesita memoria persistente del identificador del evento.

## 5. Conciliación

```mermaid
flowchart LR
    O[Orden del negocio\n19.990 CLP] --> C{Comparar referencia,\nmonto y moneda}
    P[Reporte proveedor\n19.990 CLP] --> C
    L[Ledger\n19.990 CLP] --> C
    B[Abono banco\nsegún settlement] --> C
    C -- coincide --> R[RECONCILED]
    C -- difiere --> E[EXCEPTION\ncon evidencia]
```

Conciliar no significa modificar datos hasta que cuadren; significa detectar, explicar y resolver diferencias sin borrar historia.

## Leyenda

| Elemento | Significado |
|---|---|
| rectángulo | actor, dato o decisión observable |
| rombo | regla que puede producir resultados distintos |
| flecha | orden o mensaje; no prueba por sí sola movimiento de dinero |
| `UNKNOWN` | no existe evidencia suficiente para afirmar éxito o fallo |
| `EXCEPTION` | fuentes en conflicto; requiere resolución |
