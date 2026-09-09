(() => {
  if (globalThis.mermaid) {
    globalThis.mermaid.initialize({ startOnLoad: false, securityLevel: "strict", theme: "neutral" });
    globalThis.mermaid.run({ querySelector: ".mermaid" });
  }

  const input = document.querySelector("#docs-case-filter");
  const table = document.querySelector("#docs-case-table");
  const count = document.querySelector("#docs-case-count");
  if (!input || !table || !count) return;

  const rows = [...table.querySelectorAll("tbody tr")];
  input.addEventListener("input", () => {
    const query = input.value.trim().toLocaleLowerCase("es");
    let visible = 0;
    for (const row of rows) {
      const matches = row.dataset.search.includes(query);
      row.hidden = !matches;
      if (matches) visible += 1;
    }
    count.textContent = `Mostrando ${visible} de 28 casos.`;
  });
})();
