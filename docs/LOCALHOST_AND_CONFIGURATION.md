---
layout: default
title: Localhost y configuración
---

# ⚙️ Localhost, variables y configuración por medio de pago

## Dos superficies distintas

| Superficie | Para qué sirve | Qué puede ejecutar | Secretos |
|---|---|---|---|
| localhost | laboratorio interactivo en tu computador | Python, API DEMO, adapters autorizados y UI | solo en el proceso backend |
| GitHub Pages | documentación pública del repositorio | HTML/Markdown/diagramas estáticos | nunca |

GitHub Pages no reemplaza el localhost: no ejecuta `src/payments_lab/web.py`, no puede recibir un webhook privado y no debe contener access tokens.

## Variables globales del laboratorio

| Variable | Predeterminado | Uso |
|---|---|---|
| `PAYLAB_HOST` | `127.0.0.1` | interfaz local; el código rechaza hosts no-loopback |
| `PAYLAB_PORT` | `8080` | puerto del portal |
| `PAYLAB_CONFIG_DIR` | configuración empaquetada | catálogo/guías alternativos |

En PowerShell, configura el proceso actual:

```powershell
$env:PAYLAB_HOST = "127.0.0.1"
$env:PAYLAB_PORT = "8765"
python scripts/paylab.py doctor
python scripts/paylab.py serve
```

Estas variables se heredan al proceso Python y desaparecen al cerrar la terminal. Es el alcance recomendado para desarrollo. No uses `setx` para secretos: los deja persistentes para otros procesos y complica la rotación.

El archivo [`.env.example`](../.env.example) es inventario, no contiene valores reales y **no se carga automáticamente**. Esta decisión mantiene el runtime sin dependencias y evita una falsa sensación de gestión de secretos.

## Configuración por adapter

### Khipu

```powershell
$env:KHIPU_API_KEY = "<secreto-de-tu-ambiente-autorizado>"
python scripts/paylab.py doctor
```

- retorno sugerido de tu aplicación: `/payments/khipu/return`;
- webhook sugerido: `/webhooks/khipu`;
- el portal actual sigue en DEMO; el adapter CLI necesita una cuenta y endpoint autorizados.

### Mercado Pago

```powershell
$env:MERCADOPAGO_ACCESS_TOKEN = "<access-token-de-prueba>"
python scripts/paylab.py doctor
```

- retorno sugerido: `/payments/mercado-pago/return`;
- webhook sugerido: `/webhooks/mercado-pago`;
- el token pertenece al backend; nunca se inserta en `web/app.js` ni GitHub Pages.

### Transbank Webpay Plus

```powershell
$env:TRANSBANK_COMMERCE_CODE = "<codigo-de-integracion>"
$env:TRANSBANK_API_KEY = "<api-key-de-integracion>"
$env:TRANSBANK_BASE_URL = "<url-oficial-del-ambiente>"
python scripts/paylab.py doctor
```

- retorno sugerido: `/payments/webpay/return`;
- create, commit, status y refund se ejecutan desde backend;
- la URL base evita mezclar integración y producción.

### Transbank Oneclick

```powershell
$env:TRANSBANK_ONECLICK_COMMERCE_CODE = "<codigo-de-integracion>"
$env:TRANSBANK_ONECLICK_API_KEY = "<api-key-de-integracion>"
$env:TRANSBANK_ONECLICK_BASE_URL = "<url-oficial-del-ambiente>"
python scripts/paylab.py doctor
```

- retorno sugerido: `/payments/oneclick/return`;
- el `tbk_user` es una credencial tokenizada: requiere cifrado, control de acceso y baja;
- inscripción y cobro son procesos diferentes.

## ¿Y las otras 24 familias?

Son modalidades pedagógicas sin adapter externo en este release. La ventana de configuración muestra solo las variables globales y obliga a elegir primero:

1. país y regulación;
2. proveedor o infraestructura;
3. API/protocolo y ambiente;
4. credenciales y callbacks;
5. reporte de settlement;
6. obligaciones de seguridad y operación.

No inventar una URL o secreto genérico es parte del diseño honesto del laboratorio.

## Callback desde un sandbox

`127.0.0.1` solo es visible desde tu computador. Un proveedor externo necesita una URL HTTPS pública y temporal que reenvíe al entorno de desarrollo.

Antes de usar un túnel:

1. permite solo la ruta necesaria;
2. verifica firma/HMAC/mTLS según proveedor;
3. aplica límite de tamaño y rate limit;
4. no registra secretos ni datos completos;
5. deduplica por event ID;
6. cierra el túnel al terminar.

El servidor DEMO incluido no expone endpoints de webhook productivos. Implementarlos requiere persistencia, autenticación del evento e inbox durable.

## Diagnóstico esperado

`paylab doctor` informa nombres faltantes y booleanos, nunca valores. “Configurado” significa que las variables existen; no prueba que sean correctas, que el contrato esté activo ni que el ambiente sea SANDBOX.
