const state = { families: [], scenarios: [], doctor: null };
const rail = document.querySelector("#rail");
const scenario = document.querySelector("#scenario");
const runner = document.querySelector("#runner");
const result = document.querySelector("#result");
const catalog = document.querySelector("#catalog");
const search = document.querySelector("#search");
const guidedRun = document.querySelector("#guided-run");

const LESSONS = {
  success: {
    title: "Autorizar no es lo mismo que liquidar",
    points: [
      "La intención pertenece al negocio; el proveedor solo procesa una referencia.",
      "La autorización permite continuar, pero el abono se demuestra después.",
      "Ledger y conciliación convierten una respuesta técnica en evidencia operativa.",
    ],
    production: "Confirmarías por API/webhook y conciliarías contra el reporte del proveedor.",
  },
  "timeout-recovered": {
    title: "Un timeout no significa que el pago falló",
    points: [
      "La solicitud pudo llegar al proveedor aunque tu sistema no recibiera la respuesta.",
      "Repetir el cobro a ciegas puede generar un segundo efecto financiero.",
      "La referencia estable permite consultar y recuperar exactamente la operación original.",
    ],
    production: "Guardarías UNKNOWN, consultarías con la misma referencia y alertarías si no se resuelve.",
  },
  "duplicate-event": {
    title: "Recibir dos eventos no debe producir dos cobros",
    points: [
      "Los webhooks se entregan al menos una vez: la repetición es normal.",
      "El event ID se registra antes de aplicar el cambio.",
      "El segundo evento se confirma, pero no vuelve a modificar estado ni ledger.",
    ],
    production: "Usarías un inbox persistente con restricción única por proveedor y event ID.",
  },
  "reconciliation-mismatch": {
    title: "Una diferencia visible es más segura que un ajuste silencioso",
    points: [
      "El negocio, el proveedor y el banco son fuentes distintas.",
      "Modificar el ledger para forzar un cuadre destruye la trazabilidad.",
      "La excepción conserva ambos valores hasta que una persona o regla autorizada la resuelva.",
    ],
    production: "Abrirías un caso operativo y un asiento compensatorio autorizado si corresponde.",
  },
};

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function icon(name, className = "") {
  return `<svg class="icon ` + className + `" aria-hidden="true"><use href="/icons.svg#` + name + `"></use></svg>`;
}

function modeFor(family) {
  if (family.status === "REQUIRES_CREDENTIALS") return "SANDBOX";
  if (family.status === "REQUIRES_CERTIFICATION" || family.status === "REQUIRES_HARDWARE") return "EXTERNO";
  return "DEMO";
}

function iconFor(family) {
  const id = family.id;
  if (id === "cash" || id === "cash-voucher") return "cash";
  if (["cards", "chile-webpay", "chile-oneclick", "mercado-pago", "tokenized-wallets"].includes(id)) return "card";
  if (["bank-transfer", "ach", "direct-debit", "instant-payments", "chile-khipu", "open-finance"].includes(id)) return "transfer";
  if (["digital-assets", "machine-payments", "agentic-payments"].includes(id)) return "code";
  return "route";
}

function selectedFamily() {
  return state.families.find((family) => family.id === rail.value);
}

function list(items) {
  return `<ul>` + items.map((item) => `<li>` + escapeHtml(item) + `</li>`).join("") + `</ul>`;
}

function renderSelectedSummary(family) {
  const teaching = family.playbook.teaching;
  document.querySelector("#selected-summary").innerHTML = `
    <div class="selected-icon">` + icon(iconFor(family)) + `</div>
    <p><strong>Qué resuelve</strong><span>` + escapeHtml(family.solves) + `</span></p>
    <p><strong>Qué observarás</strong><span>` + escapeHtml(family.demo_focus) + `</span></p>
    <p class="mental-model"><strong>Imagínalo así</strong><span>` + escapeHtml(teaching.mental_model) + `</span></p>
  `;
}

function renderConfiguration(family) {
  const configuration = family.playbook.configuration;
  const providerStatus = state.doctor.providers.find((provider) => provider.id === family.id);
  const variables = [...configuration.global_variables, ...configuration.provider_variables];
  const rows = variables
    .map(
      (variable) => `
        <tr>
          <td><code>${escapeHtml(variable.name)}</code></td>
          <td>${variable.required ? "requerida" : "opcional"}${variable.secret ? " · secreta" : ""}</td>
          <td>${escapeHtml(variable.purpose)}</td>
        </tr>
      `,
    )
    .join("");
  const callbacks = configuration.callbacks.length
    ? list(configuration.callbacks.map((path) => `HTTPS público + ` + path))
    : "<p>No existe callback concreto hasta elegir proveedor y regulación para esta familia.</p>";
  const setupExample = configuration.provider_variables.length
    ? [
        "# Define valores reales solo en tu terminal o secret manager",
        "$env:" + configuration.provider_variables[0].name + '="<valor-de-sandbox>"',
        "python scripts/paylab.py doctor",
      ].join("\n")
    : ['$env:PAYLAB_PORT="8080"', "python scripts/paylab.py serve"].join("\n");
  document.querySelector("#configuration-panel").innerHTML = `
    <div class="configuration-summary">
      ` + icon(providerStatus?.configured ? "check" : "shield") + `
      <div><p class="eyebrow">` + escapeHtml(family.title) + `</p>
      <h3>` + (providerStatus ? (providerStatus.configured ? "Adapter configurado; verifica el ambiente" : "DEMO listo; proveedor no configurado") : "DEMO listo; primero elige proveedor") + `</h3>
      <p>` + escapeHtml(configuration.provider_note) + `</p></div>
    </div>
    <div class="configuration-grid">
      <div>
        <h3>Variables de entorno</h3>
        <div class="table-wrap"><table><thead><tr><th>Nombre</th><th>Tipo</th><th>Para qué sirve</th></tr></thead><tbody>` + rows + `</tbody></table></div>
      </div>
      <div>
        <h3>Ejemplo PowerShell</h3>
        <pre><code>` + escapeHtml(setupExample) + `</code></pre>
        <h3>Callbacks de desarrollo</h3>` + callbacks + `
      </div>
    </div>
    <p class="pages-warning">` + icon("alert") + `<span><strong>GitHub Pages no ejecuta esta configuración.</strong> ` + escapeHtml(configuration.github_pages) + ` Usa localhost o un backend desplegado para APIs y webhooks.</span></p>
  `;
}

function renderCatalog(query = "") {
  const needle = query.trim().toLocaleLowerCase("es");
  const visible = state.families.filter((family) => {
    const haystack = [family.title, family.solves, family.id, ...(family.technologies || [])].join(" ").toLocaleLowerCase("es");
    return haystack.includes(needle);
  });
  catalog.innerHTML = visible
    .map(
      (family) => `
        <article class="case-card">
          <div class="case-icon">` + icon(iconFor(family)) + `</div>
          <span class="mode demo">DEMO LISTO</span>
          <h3>${escapeHtml(family.title)}</h3>
          <p>${escapeHtml(family.solves)}</p>
          <button type="button" data-rail="${escapeHtml(family.id)}">
            Explorar y aprender · ${escapeHtml(modeFor(family))}
          </button>
        </article>
      `,
    )
    .join("");
}

function renderRun(run) {
  const lesson = LESSONS[run.scenario];
  const steps = run.steps
    .map(
      (step) => `
        <article class="step">
          <span class="step-number">${step.number}</span>
          <div>
            <h3>${escapeHtml(step.phase)}</h3>
            <small>Actor: ${escapeHtml(step.actor)}</small>
          </div>
          <div>
            <p>${escapeHtml(step.explanation)}</p>
            <span class="state ${step.state.includes("EXCEPTION") || step.state === "UNKNOWN" ? "exception" : ""}">Estado: ${escapeHtml(step.state)}</span>
            <div class="evidence">Evidencia: ${escapeHtml(step.evidence)}</div>
          </div>
        </article>
      `,
    )
    .join("");
  const journal = run.journal.entries
    .map((entry) => `<p><strong>${escapeHtml(entry.amount)}</strong> ${escapeHtml(entry.currency)} · ${escapeHtml(entry.account)}</p>`)
    .join("");
  const reconciliation = run.differences.length
    ? run.differences.map((item) => `<p>${escapeHtml(item.kind)} · ${escapeHtml(item.detail)}</p>`).join("")
    : "<p><strong>Sin diferencias.</strong> Negocio, proveedor y ledger coinciden en esta simulación.</p>";
  const flow = run.steps
    .map(
      (step, index) => `
        <div class="flow-node ${step.state.includes("UNKNOWN") || step.state.includes("EXCEPTION") ? "warning" : ""}">
          ` + icon(step.state.includes("UNKNOWN") || step.state.includes("EXCEPTION") ? "alert" : "check") + `
          <strong>${escapeHtml(step.phase)}</strong>
          <small>${escapeHtml(step.state)}</small>
        </div>
        ${index < run.steps.length - 1 ? '<b class="flow-arrow" aria-hidden="true">→</b>' : ""}
      `,
    )
    .join("");

  result.innerHTML = `
    <header class="result-head">
      <div>
        <p class="eyebrow">Resultado explicado · ` + escapeHtml(run.scenario_explanation) + `</p>
        <h2>` + escapeHtml(run.rail.title) + `</h2>
        <p>` + escapeHtml(run.rail.demo_focus) + `</p>
      </div>
      <div class="result-identity"><span class="mode demo">NO MOVIÓ DINERO</span><span class="result-ref">` + escapeHtml(run.reference) + `</span></div>
    </header>
    <section class="journey-map" aria-labelledby="journey-map-title">
      <h3 id="journey-map-title">Mapa completo: de la orden a la comprobación final</h3>
      <p>Cada bloque es una decisión observable. La flecha indica orden, no movimiento de dinero.</p>
      <div class="flow-track">` + flow + `</div>
    </section>
    <section class="lesson">
      <div class="lesson-heading">` + icon("book") + `<div><p class="eyebrow">Qué debes llevarte</p><h3>` + escapeHtml(lesson.title) + `</h3></div></div>
      ` + list(lesson.points) + `
      <p class="production-note"><strong>En producción:</strong> ` + escapeHtml(lesson.production) + `</p>
    </section>
    <div class="timeline-heading"><h3>Historia paso a paso</h3><p>Lee actor → explicación → estado → evidencia.</p></div>
    <div class="timeline">` + steps + `</div>
    <div class="ledger">
      <div>` + icon("database") + `<h3>Asiento balanceado</h3><p class="helper">Negativo: origen del valor. Positivo: destino. La suma debe ser cero.</p>` + journal + `</div>
      <div>` + icon(run.differences.length ? "alert" : "check") + `<h3>Resultado de conciliación</h3><p class="helper">Compara negocio, proveedor y ledger usando la misma referencia.</p>` + reconciliation + `</div>
    </div>
  `;
}

function renderPlaybook(family) {
  const guide = family.playbook;
  const stack = guide.stack;
  const teaching = guide.teaching;
  document.querySelector("#playbook").innerHTML = `
    <article class="case-teaching">
      <div class="lesson-heading">` + icon(iconFor(family)) + `<div><p class="eyebrow">` + escapeHtml(family.title) + ` · del concepto al desarrollo</p><h3>` + escapeHtml(teaching.mental_model) + `</h3></div></div>
      <h4>Primer incremento real</h4>` + list(teaching.development_path) + `
      <p class="production-note"><strong>Evidencia de éxito:</strong> ` + escapeHtml(teaching.success_evidence) + `</p>
    </article>
    <article class="decision">
      <div class="lesson-heading">` + icon("code") + `<div><span class="mode demo">DECISIÓN</span><h3>¿Qué lenguaje, API e infraestructura usar?</h3></div></div>
      <p>` + escapeHtml(guide.decision) + `</p>
    </article>
    <div class="architecture" aria-label="Arquitectura recomendada">
      <span>` + icon("code") + `Navegador<small>TypeScript</small></span><b>→</b>
      <span>` + icon("shield") + `Tu backend<small>Python / FastAPI</small></span><b>→</b>
      <span>` + icon("transfer") + `API proveedor<small>HTTPS REST</small></span><b>→</b>
      <span>` + icon("database") + `Webhook + ledger<small>PostgreSQL</small></span>
    </div>
    <p class="diagram-legend"><strong>Regla:</strong> el navegador muestra; tu backend decide y protege secretos; el proveedor procesa; webhook y ledger demuestran.</p>
    <div class="playbook-grid">
      <details open><summary>` + icon("code") + `Stack recomendado</summary>
        <dl><dt>Frontend</dt><dd>` + escapeHtml(stack.frontend) + `</dd>
        <dt>Backend</dt><dd>` + escapeHtml(stack.backend) + `</dd>
        <dt>API</dt><dd>` + escapeHtml(stack.api) + `</dd>
        <dt>Datos</dt><dd>` + escapeHtml(stack.storage) + `</dd>
        <dt>Operación</dt><dd>` + escapeHtml(stack.operations) + `</dd></dl>
      </details>
      <details open><summary>` + icon("route") + `Alta, contrato y costo</summary>
        <h4>Dónde empezar</h4><p>` + escapeHtml(guide.access) + `</p>
        <h4>Qué pagar</h4><p>` + escapeHtml(guide.pricing) + `</p>
      </details>
      <details><summary>` + icon("play") + `Implementación paso a paso</summary>` + list(guide.implementation) + `</details>
      <details><summary>` + icon("flask") + `Condiciones de prueba</summary>` + list(guide.testing) + `</details>
      <details><summary>` + icon("route") + `Pros y contras</summary><h4>Pros</h4>` + list(guide.pros) + `<h4>Contras</h4>` + list(guide.cons) + `</details>
      <details><summary>` + icon("shield") + `Seguridad de datos bancarios</summary>` + list(guide.security) + `</details>
      <details><summary>` + icon("alert") + `Fallos y recuperación</summary>` + list(guide.failures) + `</details>
      <details><summary>` + icon("check") + `Salida a producción</summary>` + list(guide.go_live) + `</details>
    </div>
    <div class="sources"><h3>Fuentes oficiales</h3>` +
      guide.sources.map((source) => `<a href="` + escapeHtml(source.url) + `" target="_blank" rel="noreferrer">` + escapeHtml(source.title) + ` ↗</a>`).join("") +
    `</div>
  `;
}

async function json(url, options) {
  const response = await fetch(url, options);
  const body = await response.json();
  if (!response.ok) throw new Error(body.detail || "La solicitud no pudo completarse");
  return body;
}

async function initialize() {
  try {
    const [catalogData, scenarioData, doctor] = await Promise.all([
      json("/api/catalog"),
      json("/api/scenarios"),
      json("/api/doctor"),
    ]);
    state.families = catalogData.families;
    state.scenarios = scenarioData.scenarios;
    state.doctor = doctor;
    rail.innerHTML = state.families
      .map((family) => `<option value="${escapeHtml(family.id)}">${escapeHtml(family.title)}</option>`)
      .join("");
    scenario.innerHTML = state.scenarios
      .map((item) => `<option value="${escapeHtml(item.id)}">${escapeHtml(item.description)}</option>`)
      .join("");
    document.querySelector("#family-count").textContent = doctor.demo.families;
    document.querySelector("#runtime-status").textContent = doctor.status === "ready" ? "Operativo" : "Revisar";
    renderCatalog();
    renderPlaybook(state.families[0]);
    renderSelectedSummary(state.families[0]);
    renderConfiguration(state.families[0]);
    const params = new URLSearchParams(window.location.search);
    const preset = params.get("preset");
    const requestedRail = preset === "webpay-timeout" ? "chile-webpay" : params.get("rail");
    const requestedScenario = preset === "webpay-timeout" ? "timeout-recovered" : params.get("scenario");
    if (requestedRail && state.families.some((family) => family.id === requestedRail)) {
      rail.value = requestedRail;
      renderPlaybook(selectedFamily());
      renderSelectedSummary(selectedFamily());
      renderConfiguration(selectedFamily());
    }
    if (requestedScenario && state.scenarios.some((item) => item.id === requestedScenario)) {
      scenario.value = requestedScenario;
    }
    if (params.get("run") === "1" || preset === "webpay-timeout") runner.requestSubmit();
  } catch (error) {
    result.innerHTML = `<p class="error" role="alert">No se pudo iniciar el laboratorio: ${escapeHtml(error.message)}</p>`;
    document.querySelector("#runtime-status").textContent = "Error";
  }
}

runner.addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = runner.querySelector("button");
  button.disabled = true;
  button.textContent = "Ejecutando y preparando explicación…";
  result.setAttribute("aria-busy", "true");
  try {
    const run = await json(`/api/demo/${encodeURIComponent(rail.value)}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        scenario: scenario.value,
        amount: document.querySelector("#amount").value,
        currency: document.querySelector("#currency").value,
      }),
    });
    renderRun(run);
    result.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    result.innerHTML = `<p class="error" role="alert">${escapeHtml(error.message)}</p>`;
  } finally {
    result.setAttribute("aria-busy", "false");
    button.disabled = false;
    button.innerHTML = icon("play") + "Ejecutar y explicar";
  }
});

catalog.addEventListener("click", (event) => {
  const button = event.target.closest("[data-rail]");
  if (!button) return;
  rail.value = button.dataset.rail;
  renderPlaybook(selectedFamily());
  renderSelectedSummary(selectedFamily());
  renderConfiguration(selectedFamily());
  document.querySelector(".runner").scrollIntoView({ behavior: "smooth", block: "center" });
  rail.focus();
});

search.addEventListener("input", () => renderCatalog(search.value));
rail.addEventListener("change", () => {
  renderPlaybook(selectedFamily());
  renderSelectedSummary(selectedFamily());
  renderConfiguration(selectedFamily());
});
guidedRun.addEventListener("click", () => {
  rail.value = "chile-webpay";
  scenario.value = "timeout-recovered";
  renderPlaybook(selectedFamily());
  renderSelectedSummary(selectedFamily());
  renderConfiguration(selectedFamily());
  runner.requestSubmit();
});
initialize();
