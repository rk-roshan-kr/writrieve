document.addEventListener("DOMContentLoaded", () => {
  const API_BASE = "http://127.0.0.1:8000";

  // Tab navigation between views
  const navTabs = document.querySelectorAll(".nav-tab");
  const viewPanels = document.querySelectorAll(".view-panel");

  navTabs.forEach(tab => {
    tab.addEventListener("click", () => {
      navTabs.forEach(t => t.classList.remove("active"));
      viewPanels.forEach(p => p.style.display = "none");

      tab.classList.add("active");
      const targetView = document.getElementById(tab.dataset.view);
      if (targetView) targetView.style.display = "block";

      if (tab.dataset.view === "benchmark-view") loadBenchmarkData();
      if (tab.dataset.view === "pool-view") loadCandidatePool("all");
    });
  });

  // Simulator tabs: Gmail vs LinkedIn
  const tabGmail = document.getElementById("tab-gmail");
  const tabLinkedIn = document.getElementById("tab-linkedin");
  const urlBar = document.getElementById("mock-url-bar");
  const composerTo = document.getElementById("composer-to");
  const composerSubject = document.getElementById("composer-subject");
  const simulatedEditor = document.getElementById("simulated-editor");

  let currentSiteMode = "gmail";

  tabGmail.addEventListener("click", () => {
    tabGmail.classList.add("active");
    tabLinkedIn.classList.remove("active");
    currentSiteMode = "gmail";
    urlBar.innerText = "https://mail.google.com/mail/u/0/#inbox/compose";
    composerTo.parentElement.style.display = "flex";
    composerSubject.parentElement.style.display = "flex";
    composerTo.innerText = "Prof. Xavier Vance <xvance@csail.mit.edu>";
    composerSubject.innerText = "Re: Continuing FieldChain Research & Adaptive Sharding Follow-up";
    simulatedEditor.innerText = "";
  });

  tabLinkedIn.addEventListener("click", () => {
    tabLinkedIn.classList.add("active");
    tabGmail.classList.remove("active");
    currentSiteMode = "linkedin";
    urlBar.innerText = "https://www.linkedin.com/feed/?shareActive=true";
    composerTo.parentElement.style.display = "none";
    composerSubject.parentElement.style.display = "none";
    simulatedEditor.innerText = "";
  });

  // In-simulator Write4U Button Click
  const simWrite4uBtn = document.getElementById("sim-write4u-btn");
  simWrite4uBtn.addEventListener("click", () => {
    const pageContext = currentSiteMode === "gmail" ? {
      site: "gmail",
      recipient: "Prof. Xavier Vance <xvance@csail.mit.edu>",
      subject: "Re: Continuing FieldChain Research & Adaptive Sharding Follow-up"
    } : {
      site: "linkedin",
      author: "Alex Rivera",
      subject: "CCNCPS Conference Post"
    };

    if (window.Write4UI) {
      window.Write4UI.openModal(pageContext, (cleanedDraft) => {
        simulatedEditor.innerText = cleanedDraft;
        updateLiveInspectionPanel();
      });
    }
  });

  // Load and render Benchmark Data
  async function loadBenchmarkData() {
    const tableBody = document.getElementById("bench-table-body");
    tableBody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding: 20px; color:#94a3b8;">Computing empirical benchmark results...</td></tr>`;

    try {
      const res = await fetch(`${API_BASE}/api/benchmark`);
      const data = await res.json();

      tableBody.innerHTML = data.map(row => {
        const isW4U = row.system.includes("Write4U");
        const rowClass = isW4U ? "highlight" : "";
        
        const noiseRate = Math.round(row.irrelevant_context_rate * 100);
        const noisePillClass = noiseRate <= 5 ? "green" : (noiseRate <= 50 ? "yellow" : "red");
        
        const accScore = Math.round(row.factual_accuracy_score * 100);
        const accPillClass = accScore >= 90 ? "green" : (accScore >= 75 ? "yellow" : "red");

        return `
          <tr class="${rowClass}">
            <td>${isW4U ? "★ " + row.system : row.system}</td>
            <td><strong>${row.context_items_sent}</strong> items</td>
            <td><strong>${row.tokens_used.toLocaleString()}</strong> tokens</td>
            <td><span class="metric-pill ${noisePillClass}">${noiseRate}% noise</span></td>
            <td><span class="metric-pill ${accPillClass}">${accScore}% verified</span></td>
            <td>${row.latency_ms.toFixed(0)} ms</td>
          </tr>
        `;
      }).join("");
    } catch (err) {
      tableBody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding: 20px; color:#ef4444;">Ensure FastAPI backend is running on ${API_BASE}</td></tr>`;
    }
  }

  document.getElementById("re-run-bench-btn").addEventListener("click", loadBenchmarkData);

  // Load Candidate Pool
  let cachedCandidates = [];
  async function loadCandidatePool(sourceFilter = "all") {
    const container = document.getElementById("candidate-grid-container");
    container.innerHTML = `<div style="color: #94a3b8;">Loading 200 signals from Happenstance MCP...</div>`;

    try {
      if (!cachedCandidates.length) {
        const res = await fetch(`${API_BASE}/api/candidates`);
        const data = await res.json();
        cachedCandidates = data.items;
      }

      const selectedIds = new Set([
        "gmail_39281", "calendar_812", "drive_1092", "contacts_404",
        "gmail_40112", "linkedin_5521", "drive_881", "calendar_810", "gmail_39450"
      ]);

      const filtered = sourceFilter === "all" ? cachedCandidates : cachedCandidates.filter(c => c.source === sourceFilter);

      container.innerHTML = filtered.map(c => {
        const isSelected = selectedIds.has(c.id);
        return `
          <div class="cand-item ${isSelected ? 'selected' : ''}">
            <div style="display: flex; justify-content: space-between;">
              <span style="font-weight: 700; color: ${isSelected ? '#34d399' : '#cbd5e1'};">[${c.source.toUpperCase()}] ${c.id}</span>
              ${isSelected ? '<span style="font-size: 10px; color: #34d399; font-weight: bold;">★ SELECTED (C*)</span>' : '<span style="font-size: 10px; color: #64748b;">Filtered</span>'}
            </div>
            <div style="font-size: 11px; color: #94a3b8;">Entities: ${c.entities.join(", ")}</div>
            <div style="font-size: 11px; color: #64748b; margin-top: 4px;">${c.content.substring(0, 95)}...</div>
          </div>
        `;
      }).join("");

    } catch (e) {
      container.innerHTML = `<div style="color: #ef4444;">Could not load candidate signals. Check backend connection.</div>`;
    }
  }

  // Filter Buttons
  document.querySelectorAll(".filter-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      loadCandidatePool(btn.dataset.filter);
    });
  });

  // Pre-load default evidence in right panel
  function updateLiveInspectionPanel() {
    const list = document.getElementById("live-evidence-list");
    list.innerHTML = `
      <div class="evidence-card">
        <div class="evidence-meta">
          <span>[GMAIL] Prof. Xavier Vance</span>
          <span class="evidence-score">Score: 0.94 (#1)</span>
        </div>
        <div class="evidence-body">Subject: Great meeting you at CCNCPS / FieldChain follow-up. Let's look into extending Byzantine consensus with adaptive sharding.</div>
      </div>
      <div class="evidence-card">
        <div class="evidence-meta">
          <span>[CALENDAR] Coffee Chat with Prof. Xavier</span>
          <span class="evidence-score">Score: 0.91 (#2)</span>
        </div>
        <div class="evidence-body">Hall B Lobby, CCNCPS 2026. Discussed FieldChain throughput benchmarks (18k TPS) and co-authoring IEEE S&P proposal.</div>
      </div>
      <div class="evidence-card">
        <div class="evidence-meta">
          <span>[DRIVE] FieldChain_V2_Benchmark_Report.pdf</span>
          <span class="evidence-score">Score: 0.89 (#3)</span>
        </div>
        <div class="evidence-body">Latest testbed results show 19.4k TPS across 128 nodes with 42ms finality under simulated network partition.</div>
      </div>
    `;
  }
  updateLiveInspectionPanel();
});
