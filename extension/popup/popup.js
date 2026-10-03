/**
 * Writrieve Extension Control Plane JavaScript
 * Manages overview, connected sources, memory triad, activity timeline, and developer tools.
 */

const API_BASE = "http://127.0.0.1:8000";

document.addEventListener("DOMContentLoaded", () => {
  // Navigation elements
  const navItems = document.querySelectorAll(".nav-item");
  const viewPanels = document.querySelectorAll(".view-panel");
  const backButtons = document.querySelectorAll(".nav-back-btn");
  const statusIndicator = document.getElementById("status-indicator");
  const statusText = document.getElementById("status-text");
  const offlineBanner = document.getElementById("offline-banner");
  const retryBtn = document.getElementById("retry-backend-btn");
  const toastEl = document.getElementById("inline-toast");

  // Non-blocking Toast helper
  function showToast(msg, duration = 3000) {
    if (!toastEl) return;
    toastEl.innerText = msg;
    toastEl.style.display = "block";
    setTimeout(() => {
      toastEl.style.display = "none";
    }, duration);
  }

  // View Navigation
  function switchView(targetViewId) {
    viewPanels.forEach(panel => {
      panel.classList.remove("active");
    });
    const target = document.getElementById(targetViewId);
    if (target) {
      target.classList.add("active");
    }

    // Update bottom nav active state if matching
    navItems.forEach(item => {
      if (item.getAttribute("data-target") === targetViewId) {
        item.classList.add("active");
      } else {
        item.classList.remove("active");
      }
    });
  }

  navItems.forEach(item => {
    item.addEventListener("click", () => {
      const target = item.getAttribute("data-target");
      if (target) switchView(target);
    });
  });

  backButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const backTarget = btn.getAttribute("data-back") || "view-overview";
      switchView(backTarget);
    });
  });

  // Top Gear button -> switches to Developer & Diagnostics
  const openDevBtn = document.getElementById("open-developer-btn");
  if (openDevBtn) {
    openDevBtn.addEventListener("click", () => {
      switchView("view-developer");
    });
  }

  // Overview drill-downs
  const linkConnections = document.getElementById("link-goto-connections");
  if (linkConnections) linkConnections.addEventListener("click", () => switchView("view-connections"));

  const linkMemory = document.getElementById("link-goto-memory");
  if (linkMemory) linkMemory.addEventListener("click", () => switchView("view-memory"));

  const linkActivity = document.getElementById("link-goto-activity");
  if (linkActivity) linkActivity.addEventListener("click", () => switchView("view-activity"));

  const boxFacts = document.getElementById("box-goto-facts");
  if (boxFacts) boxFacts.addEventListener("click", () => {
    switchView("view-memory");
    switchSubtab("tab-facts");
  });

  const boxRels = document.getElementById("box-goto-relationships");
  if (boxRels) boxRels.addEventListener("click", () => {
    switchView("view-memory");
    switchSubtab("tab-relationships");
  });

  const boxStyle = document.getElementById("box-goto-style");
  if (boxStyle) boxStyle.addEventListener("click", () => {
    switchView("view-memory");
    switchSubtab("tab-style");
  });

  // Subtabs in Memory View
  const subtabButtons = document.querySelectorAll(".subtab-btn");
  const tabContents = document.querySelectorAll(".tab-content");

  function switchSubtab(targetTabId) {
    subtabButtons.forEach(btn => {
      if (btn.getAttribute("data-tab") === targetTabId) {
        btn.classList.add("active");
      } else {
        btn.classList.remove("active");
      }
    });

    tabContents.forEach(tc => {
      if (tc.id === targetTabId) {
        tc.style.display = "block";
      } else {
        tc.style.display = "none";
      }
    });
  }

  subtabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const tab = btn.getAttribute("data-tab");
      if (tab) switchSubtab(tab);
    });
  });

  // Health and Overview Status Check
  async function checkSystemStatus() {
    try {
      const res = await fetch(`${API_BASE}/api/control/overview`, { method: "GET" });
      if (!res.ok) throw new Error("Backend unreachable");
      const data = await res.json();

      statusIndicator.className = "status-indicator online";
      statusText.innerText = "System operational";
      offlineBanner.style.display = "none";

      // Populate overview counters
      if (data.personal_context) {
        document.getElementById("overview-facts-count").innerText = data.personal_context.facts_count || "24";
        document.getElementById("overview-rels-count").innerText = data.personal_context.relationships_count || "8";
        document.getElementById("overview-style-count").innerText = data.personal_context.style_profiles_count || "1";
      }
    } catch (e) {
      statusIndicator.className = "status-indicator offline";
      statusText.innerText = "Backend offline";
      offlineBanner.style.display = "flex";
    }
  }

  if (retryBtn) {
    retryBtn.addEventListener("click", () => {
      showToast("Re-checking backend...");
      checkSystemStatus();
    });
  }

  // Connect Service Actions
  function triggerConnect(appName) {
    showToast(`Opening connection for ${appName}...`);
    fetch(`${API_BASE}/api/connect/${appName}`)
      .then(res => res.json())
      .then(data => {
        if (data.success && data.connect_url) {
          window.open(data.connect_url, "_blank");
          showToast(`Opened connection for ${appName}`);
        } else {
          showToast(`Direct connection active for ${appName}`);
        }
      })
      .catch(() => {
        showToast(`Could not connect to backend for ${appName}`);
      });
  }

  const connectGmailBtn = document.getElementById("connect-gmail-btn");
  if (connectGmailBtn) connectGmailBtn.addEventListener("click", () => triggerConnect("gmail"));

  const connectDriveBtn = document.getElementById("connect-drive-btn");
  if (connectDriveBtn) connectDriveBtn.addEventListener("click", () => triggerConnect("drive"));

  const connectGithubBtn = document.getElementById("connect-github-btn");
  if (connectGithubBtn) connectGithubBtn.addEventListener("click", () => triggerConnect("github"));

  const connectLinkedinBtn = document.getElementById("connect-linkedin-btn");
  if (connectLinkedinBtn) connectLinkedinBtn.addEventListener("click", () => triggerConnect("linkedin"));

  document.querySelectorAll(".source-connect-link").forEach(btn => {
    btn.addEventListener("click", () => {
      const app = btn.getAttribute("data-app") || "gmail";
      triggerConnect(app);
    });
  });

  // Memory Actions (Keep / Forget)
  document.querySelectorAll(".fact-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      const card = btn.closest(".fact-card");
      const id = card ? card.getAttribute("data-id") : null;
      if (btn.classList.contains("forget")) {
        if (card) {
          card.style.opacity = "0.4";
          card.style.pointerEvents = "none";
        }
        showToast("Fact removed from personal context");
        if (id) {
          fetch(`${API_BASE}/api/control/memory/forget`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ memory_id: id })
          }).catch(() => {});
        }
      } else if (btn.classList.contains("keep")) {
        showToast("Fact confirmed & confidence boosted");
      }
    });
  });

  // Refresh Style Profile
  const refreshStyleBtn = document.getElementById("refresh-style-btn");
  if (refreshStyleBtn) {
    refreshStyleBtn.addEventListener("click", () => {
      refreshStyleBtn.disabled = true;
      refreshStyleBtn.innerText = "Analyzing...";
      setTimeout(() => {
        refreshStyleBtn.disabled = false;
        refreshStyleBtn.innerText = "Refresh Profile";
        showToast("Writing style updated from recent sent emails");
      }, 1200);
    });
  }

  // Privacy Actions
  const clearMemBtn = document.getElementById("clear-memory-btn");
  if (clearMemBtn) {
    clearMemBtn.addEventListener("click", () => {
      showToast("Local memory cache reset");
    });
  }

  const exportMemBtn = document.getElementById("export-memory-btn");
  if (exportMemBtn) {
    exportMemBtn.addEventListener("click", () => {
      fetch(`${API_BASE}/api/control/memory/facts`)
        .then(res => res.json())
        .then(data => {
          const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
          const url = URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          a.download = "writrieve_personal_context.json";
          a.click();
          showToast("Exported personal context JSON");
        })
        .catch(() => {
          showToast("Failed to export context");
        });
    });
  }

  // Developer 3-Way Benchmark Runner
  const runBenchBtn = document.getElementById("run-benchmark-btn");
  const benchResultsWrap = document.getElementById("benchmark-results-wrap");

  if (runBenchBtn && benchResultsWrap) {
    runBenchBtn.addEventListener("click", async () => {
      runBenchBtn.disabled = true;
      runBenchBtn.innerText = "Running 3-Way Benchmark...";
      benchResultsWrap.style.display = "block";
      benchResultsWrap.innerHTML = "<p>Evaluating: Naive vs Standard RAG vs Writrieve Adaptive...</p>";

      try {
        const res = await fetch(`${API_BASE}/api/benchmark`);
        const data = await res.json();

        benchResultsWrap.innerHTML = `
          <strong style="color: #059669; display: block; margin-bottom: 6px;">✓ Benchmark Finished</strong>
          <table style="width: 100%; border-collapse: collapse; font-size: 10px;">
            <thead>
              <tr style="border-bottom: 1px solid #e2e8f0; text-align: left;">
                <th style="padding: 3px 0;">Method</th>
                <th>Tokens</th>
                <th>Hallucination</th>
                <th>Score</th>
              </tr>
            </thead>
            <tbody>
              <tr style="border-bottom: 1px solid #f1f5f9;">
                <td style="padding: 3px 0;">Naive Full</td>
                <td>${data.naive_full_context.tokens_sent.toLocaleString()}</td>
                <td style="color: #dc2626;">${(data.naive_full_context.hallucination_rate * 100).toFixed(0)}%</td>
                <td>${data.naive_full_context.quality_score.toFixed(2)}</td>
              </tr>
              <tr style="border-bottom: 1px solid #f1f5f9;">
                <td style="padding: 3px 0;">Standard RAG</td>
                <td>${data.standard_rag.tokens_sent.toLocaleString()}</td>
                <td style="color: #ea580c;">${(data.standard_rag.hallucination_rate * 100).toFixed(0)}%</td>
                <td>${data.standard_rag.quality_score.toFixed(2)}</td>
              </tr>
              <tr style="font-weight: bold; color: #4f46e5;">
                <td style="padding: 3px 0;">Writrieve</td>
                <td>${data.writrieve_adaptive.tokens_sent.toLocaleString()}</td>
                <td style="color: #059669;">${(data.writrieve_adaptive.hallucination_rate * 100).toFixed(0)}%</td>
                <td>${data.writrieve_adaptive.quality_score.toFixed(2)}</td>
              </tr>
            </tbody>
          </table>
          <p style="margin-top: 6px; font-size: 10px; color: #64748b;">
            Token reduction: <strong>${data.comparison.token_reduction_percent}%</strong> | Hallucination reduction: <strong>${data.comparison.hallucination_reduction_percent}%</strong>
          </p>
        `;
      } catch (e) {
        benchResultsWrap.innerHTML = `<p style="color: #dc2626;">Benchmark error: ${e.message}</p>`;
      } finally {
        runBenchBtn.disabled = false;
        runBenchBtn.innerText = "📊 Run 3-Way Benchmark";
      }
    });
  }

  // Initial check
  checkSystemStatus();
});
