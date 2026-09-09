<section class="docs-hero">
  <p class="kicker">Laboratorio ejecutable + manual de implementación</p>
  <h1>Entiende un pago desde el primer clic hasta la conciliación.</h1>
  <p class="lede">PayLab convierte 28 modalidades de pago en recorridos legibles: quién inicia, quién procesa, qué prueba el resultado, qué ocurre si falla y qué debes construir antes de producción.</p>
  <div class="hero-actions">
    <a class="primary-button" href="payment-methods/END_TO_END_MATRIX.html">Ver la tabla de los 28 casos</a>
    <a class="secondary-button" href="START_HERE.html">Hacer el recorrido de 10 minutos</a>
    <a class="secondary-button" href="https://vladimiracunadev-create.github.io/universal-payments-engineering-lab/downloads/universal-payments-engineering-lab.pdf">Descargar PDF navegable</a>
  </div>
  <div class="truth-banner"><strong>DEMO enseña</strong><span>SANDBOX conecta</span><span>LIVE mueve valor</span></div>
</section>

## Qué resuelve este repositorio

<div class="visual-cards">
  <article><span class="card-number">01</span><h3>Ver lo invisible</h3><p>Estados, actores, evidencia, ledger y conciliación aparecen en pantalla.</p></article>
  <article><span class="card-number">02</span><h3>Practicar fallos</h3><p>Timeout, webhook duplicado y diferencias se simulan sin dinero ni credenciales.</p></article>
  <article><span class="card-number">03</span><h3>Construirlo de verdad</h3><p>Cada caso indica alta, API, variables, seguridad, pruebas y paso a producción.</p></article>
</div>

## Un pago completo tiene cinco preguntas

<div class="reading-path">
  <span><b>1</b> ¿Qué necesita pagar?</span><i>→</i>
  <span><b>2</b> ¿Cómo se inicia?</span><i>→</i>
  <span><b>3</b> ¿Quién procesa?</span><i>→</i>
  <span><b>4</b> ¿Quién confirma?</span><i>→</i>
  <span><b>5</b> ¿Cómo se concilia?</span>
</div>

```mermaid
flowchart LR
    A["Necesidad<br/>orden y monto"] --> B["Inicio<br/>backend crea referencia"]
    B --> C["Proceso<br/>proveedor o rail"]
    C --> D["Confirmación<br/>API, webhook o archivo"]
    D --> E["Cierre<br/>ledger + conciliación"]
    C -.-> U["Timeout<br/>UNKNOWN"]
    U -.-> R["Consultar misma referencia<br/>no duplicar"]
    R -.-> D
```

> La pantalla de retorno no confirma un pago. La prueba llega desde una fuente autoritativa y el cierre exige explicar el dinero en ledger, proveedor y banco.

## Elige tu entrada

<div class="docs-grid">
  <a href="payment-methods/END_TO_END_MATRIX.html"><small>Vista central + 28 guías individuales</small><strong>Tabla: 28 casos de comienzo a fin</strong><span>Cada fila abre un documento propio con ejemplo, actores, API, variables, pruebas, fallos, seguridad y LIVE.</span></a>
  <a href="START_HERE.html"><small>Primera vez</small><strong>Empieza aquí</strong><span>Objetivo, vocabulario y una práctica guiada de diez minutos.</span></a>
  <a href="LOCALHOST_AND_CONFIGURATION.html"><small>Ejecutar</small><strong>Localhost y variables</strong><span>Instalación, variables globales, credenciales por proveedor y callbacks.</span></a>
  <a href="IMPLEMENTATION_GUIDE.html"><small>Desarrollar</small><strong>Implementar en cualquier web</strong><span>Lenguaje, API, frontend, backend, datos, seguridad y operación.</span></a>
  <a href="payment-methods/CASEBOOK.html"><small>Profundizar</small><strong>Casebook pedagógico</strong><span>Modelo mental, primer incremento, evidencia y condiciones LIVE por caso.</span></a>
  <a href="diagrams/PAYMENT_JOURNEY.html"><small>Visualizar</small><strong>Diagramas explicados</strong><span>Estados, timeout, webhook duplicado, ledger y conciliación.</span></a>
  <a href="LEARNING_PATH.html"><small>Aprender</small><strong>Ruta por niveles</strong><span>De primer DEMO a un piloto productivo con criterios de salida.</span></a>
  <a href="GITHUB_PAGES.html"><small>Publicación</small><strong>GitHub Pages</strong><span>Qué publica, qué no ejecuta y por qué jamás contiene secretos.</span></a>
  <a href="FORMATS_AND_TRACEABILITY.html"><small>Correspondencia</small><strong>Markdown, HTML y PDF</strong><span>Qué genera cada formato y cómo abrir el mismo caso en los tres.</span></a>
</div>

## Localhost y GitHub Pages no son lo mismo

| | Localhost | GitHub Pages |
|---|---|---|
| Propósito | ejecutar y observar recorridos | leer, comparar y navegar la documentación |
| Runtime | Python + API + JavaScript | HTML/CSS/diagramas estáticos |
| Puede simular | sí, 28 casos × 4 escenarios | no |
| Variables | lee el proceso local | no usa credenciales |
| Webhooks | sólo con backend/túnel controlado | no puede recibirlos |
| Riesgo monetario | $0 en DEMO | $0; es documentación |

![Portal local: selección, recorrido y explicación](assets/paylab-home.png)

## Resultado esperado

Al terminar, debes poder señalar una fila de la [matriz completa](payment-methods/END_TO_END_MATRIX.md) y explicar: **qué inicia la operación, qué sistema tiene autoridad, cómo sobrevives a un estado incierto, qué asiento se genera y con qué reporte se concilia**. Si una de esas respuestas falta, la integración todavía no está lista.
