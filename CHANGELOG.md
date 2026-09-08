# Changelog

## [Unreleased]

### Added

- portal localhost con API y UI responsive;
- recorridos DEMO deterministas para las 28 familias del catálogo;
- escenarios de éxito, timeout recuperado, evento duplicado y diferencia de conciliación;
- comandos `doctor`, `demo` y `serve`;
- guía de producto, capturas verificadas y arranque específico para Windows.
- playbooks por modalidad con lenguaje/API, alta, costos, pruebas, seguridad, fallos, puesta en producción y fuentes oficiales.
- matriz visual y filtrable con los 28 recorridos completos: necesidad, inicio, proceso, confirmación, cierre, recuperación e implementación real.
- GitHub Pages rediseñado como sitio navegable; las guías principales ahora se renderizan con el mismo tema.
- Markdown limpio de metadatos Jekyll y páginas HTML separadas; matriz con nueve columnas explícitas, ejemplo y filtro.
- 28 guías pedagógicas individuales en Markdown y HTML, enlazadas desde cada fila de la matriz.
- experiencia pedagógica con objetivo explícito, ejemplo guiado, iconos, mapas del recorrido y lecciones por escenario;
- guías “Empieza aquí”, ruta de aprendizaje, diagramas y revisión comparativa de repositorios de referencia.
- casebook pedagógico de 28 modalidades, configuración por variables de entorno y documentación de GitHub Pages.
- Catálogo transversal de 28 familias de pago y tecnologías asociadas.
- Documentación profunda de lifecycle, arquitectura, protocolos, seguridad, regulación, operaciones, settlement y conciliación.
- Currículo de 8 partes y 32 módulos con resultados verificables.
- Runbooks de certificación, controlled live, fault injection y production readiness.
- Verificación automatizada de versión, enlaces, UTF-8, catálogo y estructura.
- Integración real de Transbank Oneclick Mall: inscripción, autorización, consulta, devolución y baja.
- Verificación HMAC y protección anti-replay para webhooks de Khipu y Mercado Pago.
- Guías operativas caso a caso para Khipu, Mercado Pago, Webpay Plus y Oneclick.
- CI multi-versión, build de wheel, Ruff, Bandit, pip-audit, CodeQL y Dependabot.

### Changed

- Estados de integración corregidos para no confundir presencia de código con credenciales/certificación reales.
- Transporte HTTP endurecido con HTTPS obligatorio, límites de respuesta y resultados de red inciertos.
- Adaptadores con validación de contratos, identificadores, URLs e importes sin punto flotante.
- Operaciones Khipu sin endpoint v3 verificado retiradas hasta disponer del contrato aplicable.

### Fixed

- el catálogo ya no atribuye void/refund inexistentes al adapter Khipu;
- Oneclick cuenta como integración propia en el catálogo;
- configuración y assets web se incluyen en la distribución;
- la documentación distingue ventana de frescura de deduplicación anti-replay.

Todos los cambios relevantes se documentan aquí siguiendo [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) y versionado semántico cuando exista una release.

## [0.1.0] - 2026-09-07

### Added

- Núcleo inicial de estados, ledger, idempotencia y reconciliación.
- Adaptadores HTTP iniciales para Khipu, Mercado Pago y Transbank.
