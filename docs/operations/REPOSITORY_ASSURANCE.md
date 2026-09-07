# ✅ Garantías del repositorio

## Controles automatizados

| Control | Fuente de verdad | Ejecución |
|---|---|---|
| pruebas | `tests/` | `python -m unittest discover -s tests -v` |
| versión | `pyproject.toml` y `payments_lab.__version__` | `python scripts/verify_repository.py` |
| catálogo | `config/payment_rails.yaml` | IDs únicos, status permitido y cobertura mínima |
| currículo | `curriculum/README.md` | 32 filas numeradas |
| enlaces locales | todos los Markdown | resolución determinista de targets |
| codificación | archivos de texto | UTF-8 sin BOM ni patrones de mojibake |
| secretos | historial Git | gitleaks en cada push/PR y semanalmente |
| supply chain | workflows | acciones fijadas a SHA completo |

## Controles remotos

El repositorio se publica como `public`, usa `main`, mantiene description/topics en `.github/repository-metadata.json`, tiene secret scanning y push protection habilitados y acepta reportes privados de vulnerabilidades.

Los topics se aplican mediante el endpoint específico de GitHub y se verifican por API, porque el endpoint general de actualización del repositorio no garantiza procesarlos.

## Revisión

No se afirma un gate verde por configuración: se espera la conclusión real de GitHub Actions. Cualquier workflow fallido mantiene la publicación en revisión hasta corregir o explicar su causa con evidencia.
