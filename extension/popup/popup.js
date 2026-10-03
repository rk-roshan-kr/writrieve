document.addEventListener("DOMContentLoaded", async () => {
  const statusEl = document.getElementById("engine-status");
  const modelEl = document.getElementById("model-name");
  const openTabBtn = document.getElementById("open-active-tab-btn");
  const benchmarkBtn = document.getElementById("run-benchmark-btn");
  const benchmarkView = document.getElementById("benchmark-view");
  const benchTableWrap = document.getElementById("bench-table-wrap");

  // 1. Check Backend Health
  try {
    const res = await fetch("http://127.0.0.1:8000/api/health");
    if (res.ok) {
      const data = await res.json();
      statusEl.innerText = "Online";
      statusEl.classList.add("online");
      modelEl.innerText = data.model_architecture.split("+")[0].trim();
    } else {
      statusEl.innerText = "Offline";
    }
  } catch (err) {
    statusEl.innerText = "Backend Offline";
  }

  // 2. Launch on active tab
  openTabBtn.addEventListener("click", async () => {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab && tab.id) {
      chrome.tabs.sendMessage(tab.id, { action: "TRIGGER_WRITE4U" }, () => {
        window.close();
      });
    }
  });

  // 3. Run Benchmark
  benchmarkBtn.addEventListener("click", async () => {
    benchmarkBtn.innerText = "Computing 3-way evaluation...";
    benchmarkBtn.disabled = true;

    try {
      const res = await fetch("http://127.0.0.1:8000/api/benchmark");
      const benchData = await res.json();

      let tableHtml = `
        <table class="bench-table">
          <thead>
            <tr>
              <th>System</th>
              <th>Items</th>
              <th>Tokens</th>
              <th>Noise</th>
              <th>Accuracy</th>
            </tr>
          </thead>
          <tbody>
      `;

      benchData.forEach(row => {
        const isW4U = row.system.includes("Write4U");
        const highlight = isW4U ? 'style="color:#34d399; font-weight:bold;"' : '';
        tableHtml += `
          <tr ${highlight}>
            <td>${isW4U ? "★ Write4U" : (row.system.includes("RAG") ? "RAG" : "Full Context")}</td>
            <td>${row.context_items_sent}</td>
            <td>${row.tokens_used}</td>
            <td>${Math.round(row.irrelevant_context_rate * 100)}%</td>
            <td>${Math.round(row.factual_accuracy_score * 100)}%</td>
          </tr>
        `;
      });

      tableHtml += `</tbody></table>`;
      benchTableWrap.innerHTML = tableHtml;
      benchmarkView.style.display = "block";
    } catch (e) {
      alert("Please ensure FastAPI backend is running on http://127.0.0.1:8000");
    } finally {
      benchmarkBtn.innerText = "📊 Run 3-Way Benchmark";
      benchmarkBtn.disabled = false;
    }
  });
});
