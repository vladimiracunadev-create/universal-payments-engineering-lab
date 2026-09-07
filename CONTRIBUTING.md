# 🤝 Contribuir

## Principio

Una contribución debe aumentar capacidad o claridad sin inflar madurez. Un ejemplo, mock o documento no convierte un rail en operativo.

## Flujo local

```bash
python -m venv .venv
# activa el entorno según tu sistema
python -m pip install -e .
python -m unittest discover -s tests -v
python scripts/verify_repository.py
```

## Para un nuevo adaptador

Incluye documentación oficial/versionada, capabilities, autenticación, status mapping, idempotencia/retry, webhook/polling, timeout/unknown, refund/reversal, settlement, sanitización y tests con transporte falso. No hagas llamadas financieras en CI.

## Commits y PR

- cambio pequeño y coherente;
- sin secretos, PII ni evidencia real;
- tests y verificador verdes;
- documentación/`config/payment_rails.yaml` sincronizados;
- explicar límites y riesgos;
- no modificar referencias históricas del changelog para hacerlas parecer actuales.

Al contribuir aceptas el [Código de Conducta](CODE_OF_CONDUCT.md) y que tu aporte se distribuya bajo [MIT](LICENSE).
