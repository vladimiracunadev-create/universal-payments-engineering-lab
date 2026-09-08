const state = { families: [], scenarios: [] };
const rail = document.querySelector("#rail");
const scenario = document.querySelector("#scenario");
const runner = document.querySelector("#runner");
const result = document.querySelector("#result");
const catalog = document.querySelector("#catalog");
const search = document.querySelector("#search");

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function modeFor(family) {
  if (family.status === "REQUIRES_CREDENTIALS") return "SANDBOX";
  if (family.status === "REQUIRES_CERTIFICATION" || family.status === "REQUIRES_HARDWARE") return "EXTERNO";
  return "DEMO";
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
          <span class="mode demo">DEMO LISTO</span>
          <h3>${escapeHtml(family.title)}</h3>
          <p>${escapeHtml(family.solves)}</p>
          <button type="button" data-rail="${escapeHtml(family.id)}">
            Explorar recorrido · ${escapeHtml(modeFor(family))}
          </button>
        </article>
      `,
    )
    .join("");
}

function renderRun(run) {
  const steps = run.steps
    .map(
      (step) => `
        <article class="step">
          <span class="step-number">${step.number}</span>
          <div>
            <h3>${escapeHtml(step.phase)}</h3>
            <small>${escapeHtml(step.actor)}</small>
          </div>
          <div>
            <p>${escapeHtml(step.explanation)}</p>
            <span class="state ${step.state.includes("EXCEPTION") ? "exception" : ""}">${escapeHtml(step.state)}</span>
            <div class="evidence">${escapeHtml(step.evidence)}</div>
          </div>
        </article>
      `,
    )
    .join("");
  const journal = run.journal.entries
    .map((entry) => `<p>${escapeHtml(entry.account)} · ${escapeHtml(entry.amount)} ${escapeHtml(entry.currency)}</p>`)
    .join("");
  const reconciliation = run.differences.length
    ? run.differences.map((item) => `<p>${escapeHtml(item.kind)} · ${escapeHtml(item.detail)}</p>`).join("")
    : "<p>Sin diferencias: negocio, proveedor y ledger coinciden en esta simulación.</p>";

  result.innerHTML = `
    <header class="result-head">
      <div>
        <h2>${escapeHtml(run.rail.title)}</h2>
        <p>${escapeHtml(run.rail.demo_focus)}</p>
      </div>
      <span class="result-ref">${escapeHtml(run.reference)}</span>
    </header>
    <div class="timeline">${steps}</div>
    <div class="ledger">
      <div><h3>Asiento balanceado</h3>${journal}</div>
      <div><h3>Resultado de conciliación</h3>${reconciliation}</div>
    </div>
  `;
}

function list(items) {
  return `<ul>` + items.map((item) => `<li>` + escapeHtml(item) + `</li>`).join("") + `</ul>`;
}

function renderPlaybook(family) {
  const guide = family.playbook;
  const stack = guide.stack;
  document.querySelector("#playbook").innerHTML = `
    <article class="decision">
      <span class="mode demo">DECISIÓN</span>
      <h3>¿Qué lenguaje, API e infraestructura usar?</h3>
      <p>` + escapeHtml(guide.decision) + `</p>
    </article>
    <div class="architecture" aria-label="Arquitectura recomendada">
      <span>Navegador<br><small>TypeScript</small></span><b>→</b>
      <span>Tu backend<br><small>Python / FastAPI</small></span><b>→</b>
      <span>API proveedor<br><small>HTTPS REST</small></span><b>→</b>
      <span>Webhook + ledger<br><small>PostgreSQL</small></span>
    </div>
    <div class="playbook-grid">
      <details open><summary>Stack recomendado</summary>
        <dl><dt>Frontend</dt><dd>` + escapeHtml(stack.frontend) + `</dd>
        <dt>Backend</dt><dd>` + escapeHtml(stack.backend) + `</dd>
        <dt>API</dt><dd>` + escapeHtml(stack.api) + `</dd>
        <dt>Datos</dt><dd>` + escapeHtml(stack.storage) + `</dd>
        <dt>Operación</dt><dd>` + escapeHtml(stack.operations) + `</dd></dl>
      </details>
      <details open><summary>Alta, contrato y costo</summary>
        <h4>Dónde empezar</h4><p>` + escapeHtml(guide.access) + `</p>
        <h4>Qué pagar</h4><p>` + escapeHtml(guide.pricing) + `</p>
      </details>
      <details><summary>Implementación paso a paso</summary>` + list(guide.implementation) + `</details>
      <details><summary>Condiciones de prueba</summary>` + list(guide.testing) + `</details>
      <details><summary>Pros y contras</summary><h4>Pros</h4>` + list(guide.pros) + `<h4>Contras</h4>` + list(guide.cons) + `</details>
      <details><summary>Seguridad de datos bancarios</summary>` + list(guide.security) + `</details>
      <details><summary>Fallos y recuperación</summary>` + list(guide.failures) + `</details>
      <details><summary>Salida a producción</summary>` + list(guide.go_live) + `</details>
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
    const params = new URLSearchParams(window.location.search);
    const preset = params.get("preset");
    const requestedRail = preset === "webpay-timeout" ? "chile-webpay" : params.get("rail");
    const requestedScenario = preset === "webpay-timeout" ? "timeout-recovered" : params.get("scenario");
    if (requestedRail && state.families.some((family) => family.id === requestedRail)) {
      rail.value = requestedRail;
      renderPlaybook(state.families.find((family) => family.id === rail.value));
    }
    if (requestedScenario && state.scenarios.some((item) => item.id === requestedScenario)) {
      scenario.value = requestedScenario;
    }
    if (params.get("run") === "1" || preset === "webpay-timeout") runner.requestSubmit();
  } catch (error) {
    result.innerHTML = `<p class="error">No se pudo iniciar el laboratorio: ${escapeHtml(error.message)}</p>`;
    document.querySelector("#runtime-status").textContent = "Error";
  }
}

runner.addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = runner.querySelector("button");
  button.disabled = true;
  button.textContent = "Ejecutando…";
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
    result.innerHTML = `<p class="error">${escapeHtml(error.message)}</p>`;
  } finally {
    result.setAttribute("aria-busy", "false");
    button.disabled = false;
    button.textContent = "Ejecutar recorrido";
  }
});

catalog.addEventListener("click", (event) => {
  const button = event.target.closest("[data-rail]");
  if (!button) return;
  rail.value = button.dataset.rail;
  renderPlaybook(state.families.find((family) => family.id === rail.value));
  document.querySelector(".runner").scrollIntoView({ behavior: "smooth", block: "center" });
  rail.focus();
});

search.addEventListener("input", () => renderCatalog(search.value));
rail.addEventListener("change", () => renderPlaybook(state.families.find((family) => family.id === rail.value)));
initialize();
