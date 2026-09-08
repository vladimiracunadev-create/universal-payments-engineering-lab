# Ejecutar PayLab en Windows

## Requisitos

- Windows 10 u 11;
- Python 3.11 o superior disponible como `python`;
- PowerShell 5.1 o posterior.

Docker, Node.js y credenciales externas no son necesarios para DEMO.

## Arranque

Desde la raíz del repositorio:

```powershell
.\scripts\start_paylab.ps1
```

Si la política local no permite scripts, no la desactives globalmente. Usa:

```powershell
python scripts\paylab.py doctor
python scripts\paylab.py serve
```

Después abre `http://127.0.0.1:8080`.

También existe `scripts\start_paylab.cmd` para un arranque básico desde CMD.

## Instalación aislada

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e .
paylab doctor
paylab serve
```

## Puertos y exposición

El servidor acepta únicamente `127.0.0.1`, `localhost` o `::1`. Esta restricción
evita publicar accidentalmente un laboratorio sin autenticación en la red local.

Para una futura exposición compartida se necesita una entrega distinta con
autenticación, proxy TLS, rate limit, logging sanitizado y revisión de amenazas.

## Credenciales de proveedores

El proyecto no lee `.env` automáticamente. Inyecta secretos en el proceso o con
un secret manager. Ejecuta `paylab doctor` antes de seleccionar SANDBOX.

Configurar variables no prueba que la cuenta esté autorizada. Nunca uses
credenciales, tarjetas o cuentas que no sean propias o explícitamente autorizadas.
