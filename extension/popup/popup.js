document.addEventListener("DOMContentLoaded", async () => {
  const statusEl = document.getElementById("engine-status");
  const providerStatusEl = document.getElementById("provider-status");
  const memoryStatEl = document.getElementById("memory-stat");
  const openTabBtn = document.getElementById("open-active-tab-btn");
  const connectBtn = document.getElementById("connect-composio-btn");
  const benchmarkBtn = document.getElementById("run-benchmark-btn");
  const benchmarkView = document.getElementById("benchmark-view");
  const benchTableWrap = document.getElementById("bench-table-wrap");

  const BACKEND_BASE = "http://127.0.0.1:8000";

  // 1. Check Backend Health
  try {
    const res = await fetch(`${BACKEND_BASE}/api/health`);
    if (res.ok) {
      const data = await res.json();
      statusEl.innerText = "Online";
      statusEl.classList.add("online");

      if (data.context_provider) {
        providerStatusEl.innerText = data.context_provider.includes("Composio") ? "Composio Live" : "Active Provider";
      }
    } else {
      statusEl.innerText = "Offline";
    }
  } catch (err) {
    statusEl.innerText = "Backend Offline";
  }

  // 2. Load Memory Stats
  try {
    const memRes = await fetch(`${BACKEND_BASE}/api/memory`);
    if (memRes.ok) {
      const memData = await memRes.json();
      const facts = memData.facts_count || (memData.facts ? memData.facts.length : 0);
      const rels = memData.relationships_count || (memData.relationships ? memData.relationships.length : 0);
      memoryStatEl.innerText = `${facts} Facts • ${rels} Entities • Style`;
    }
  } catch (e) {
    // Keep default
  }

  // 3. Connect Gmail OAuth via Composio
  if (connectBtn) {
    connectBtn.addEventListener("click", async () => {
      connectBtn.innerText = "⏳ Generating OAuth...";
      try {
        const res = await fetch(`${BACKEND_BASE}/api/connect/gmail`);
        const data = await res.json();
        if (data.success && data.connect_url) {
          window.open(data.connect_url, "_blank");
          connectBtn.innerText = "✅ Link Opened";
          setTimeout(() => { connectBtn.innerText = "🔗 Connect Gmail (Composio OAuth)"; }, 4000);
        } else {
          alert("Composio OAuth: " + (data.error || "Please verify credentials"));
          connectBtn.innerText = "🔗 Connect Gmail (Composio OAuth)";
        }
      } catch (err) {
        alert("Ensure FastAPI backend is running on " + BACKEND_BASE);
        connectBtn.innerText = "🔗 Connect Gmail (Composio OAuth)";
      }
    });
  }

  // 4. Focus composer on active tab
  openTabBtn.addEventListener("click", async () => {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab && tab.id) {
      chrome.tabs.sendMessage(tab.id, { action: "TRIGGER_WRITE4U" }, () => {
        window.close();
      });
    }
  });

  // 5. Run Benchmark
  benchmarkBtn.addEventListener("click", async () => {
    benchmarkBtn.innerText = "Computing 3-way evaluation...";
    benchmarkBtn.disabled = true;

    try {
      const res = await fetch(`${BACKEND_BASE}/api/benchmark`);
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
        const isWritrieve = row.system.includes("Writrieve") || row.system.includes("Write4U");
        const highlight = isWritrieve ? 'style="color:#34d399; font-weight:bold;"' : '';
        tableHtml += `
          <tr ${highlight}>
            <td>${isWritrieve ? "★ Writrieve" : (row.system.includes("RAG") ? "RAG" : "Full Context")}</td>
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
      alert("Please ensure FastAPI backend is running on " + BACKEND_BASE);
    } finally {
      benchmarkBtn.innerText = "📊 Run 3-Way Benchmark";
      benchmarkBtn.disabled = false;
    }
  });
});
