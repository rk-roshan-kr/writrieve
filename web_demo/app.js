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
      if (tab.dataset.view === "memory-view") loadMemoryData();
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

  // Composio OAuth Connection Button
  const composioBtn = document.getElementById("composio-connect-btn");
  if (composioBtn) {
    composioBtn.addEventListener("click", async () => {
      composioBtn.innerText = "⏳ Generating OAuth...";
      try {
        const res = await fetch(`${API_BASE}/api/connect/gmail`);
        const data = await res.json();
        if (data.success && data.connect_url) {
          window.open(data.connect_url, "_blank");
          composioBtn.innerText = "✅ Link Opened";
          setTimeout(() => { composioBtn.innerText = "🔗 Connect Gmail (Composio)"; }, 4000);
        } else {
          alert("Composio Connect: " + (data.error || "Please verify credentials"));
          composioBtn.innerText = "🔗 Connect Gmail (Composio)";
        }
      } catch (e) {
        alert("Failed to reach Write4U backend at " + API_BASE);
        composioBtn.innerText = "🔗 Connect Gmail (Composio)";
      }
    });
  }

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

  // Load Structured Long-Term Memory
  async function loadMemoryData() {
    const factsList = document.getElementById("facts-memory-list");
    const relList = document.getElementById("rel-memory-list");
    const styleList = document.getElementById("style-memory-list");
    const factsBadge = document.getElementById("facts-count-badge");
    const relBadge = document.getElementById("rel-count-badge");

    try {
      const res = await fetch(`${API_BASE}/api/memory`);
      const data = await res.json();

      // Bucket 1: Facts
      factsBadge.innerText = `${data.facts_count || (data.facts ? data.facts.length : 0)} Facts`;
      if (data.facts && data.facts.length > 0) {
        factsList.innerHTML = data.facts.map(f => `
          <div style="padding: 10px; background: rgba(56, 189, 248, 0.08); border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 8px;">
            <div style="display: flex; justify-content: space-between; font-weight: 600; color: #38bdf8; font-size: 12px;">
              <span>${f.topic || 'Fact'}</span>
              <span style="color: #34d399;">${f.lifecycle_status || 'CONFIRMED'} (${Math.round((f.confidence || 0.95)*100)}%)</span>
            </div>
            <div style="color: #e2e8f0; margin-top: 4px; font-size: 13px;">${f.fact}</div>
          </div>
        `).join("");
      } else {
        factsList.innerHTML = `<div style="color: #94a3b8;">No verified facts found.</div>`;
      }

      // Bucket 2: Relationships
      relBadge.innerText = `${data.relationships_count || (data.relationships ? data.relationships.length : 0)} Entities`;
      if (data.relationships && data.relationships.length > 0) {
        relList.innerHTML = data.relationships.map(r => `
          <div style="padding: 10px; background: rgba(167, 139, 250, 0.08); border: 1px solid rgba(167, 139, 250, 0.2); border-radius: 8px;">
            <div style="display: flex; justify-content: space-between; font-weight: 600; color: #a78bfa; font-size: 12px;">
              <span>${r.person_name}</span>
              <span style="color: #cbd5e1;">${r.relationship || 'Collaborator'}</span>
            </div>
            <div style="color: #94a3b8; font-size: 12px; margin-top: 3px;">Affiliation: ${r.affiliation || 'Academic Research'}</div>
            <div style="color: #cbd5e1; font-size: 12px; margin-top: 4px;">Context: ${r.shared_context || 'N/A'}</div>
          </div>
        `).join("");
      } else {
        relList.innerHTML = `<div style="color: #94a3b8;">No relationship entries found.</div>`;
      }

      // Bucket 3: Style Habits
      if (data.writing_style) {
        const habits = data.writing_style.observed_habits || [];
        styleList.innerHTML = `
          <div style="display: flex; flex-direction: column; gap: 8px;">
            <div style="padding: 8px 12px; background: rgba(52, 211, 153, 0.08); border-radius: 6px; border: 1px solid rgba(52, 211, 153, 0.2);">
              <span style="color: #94a3b8; font-size: 12px;">Preferred Greeting:</span>
              <div style="color: #34d399; font-weight: 600;">${data.writing_style.preferred_greeting || 'Dear Professor {name},'}</div>
            </div>
            <div style="padding: 8px 12px; background: rgba(52, 211, 153, 0.08); border-radius: 6px; border: 1px solid rgba(52, 211, 153, 0.2);">
              <span style="color: #94a3b8; font-size: 12px;">Preferred Closing:</span>
              <div style="color: #34d399; font-weight: 600;">${data.writing_style.preferred_closing || 'Best regards,\nAlex Rivera'}</div>
            </div>
            <div style="padding: 8px 12px; background: rgba(52, 211, 153, 0.08); border-radius: 6px; border: 1px solid rgba(52, 211, 153, 0.2);">
              <span style="color: #94a3b8; font-size: 12px;">Sentence Length / Density:</span>
              <div style="color: #e2e8f0;">${data.writing_style.sentence_length_preference || 'Medium (14-18 words per sentence)'}</div>
            </div>
            <div style="padding: 8px 12px; background: rgba(52, 211, 153, 0.08); border-radius: 6px; border: 1px solid rgba(52, 211, 153, 0.2);">
              <span style="color: #94a3b8; font-size: 12px;">Observed Writing Habits:</span>
              <div style="color: #cbd5e1; font-size: 12px; margin-top: 4px;">
                ${habits.map(h => `• ${h}`).join("<br>")}
              </div>
            </div>
          </div>
        `;
      } else {
        styleList.innerHTML = `<div style="color: #94a3b8;">No style habits found.</div>`;
      }
    } catch (e) {
      factsList.innerHTML = `<div style="color: #ef4444;">Failed to load memory: Ensure backend is running.</div>`;
    }
  }

  const refreshMemBtn = document.getElementById("refresh-memory-btn");
  if (refreshMemBtn) {
    refreshMemBtn.addEventListener("click", loadMemoryData);
  }
});
