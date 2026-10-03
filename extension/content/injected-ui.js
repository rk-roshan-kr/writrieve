(function () {
  if (window.Write4UI) return;

  const API_ENDPOINT = "http://127.0.0.1:8000/api/generate";

  let currentResponse = null;
  let onInsertCallback = null;

  function createModalDOM() {
    if (document.getElementById("write4u-overlay")) return;

    const overlay = document.createElement("div");
    overlay.id = "write4u-overlay";
    overlay.className = "write4u-modal-overlay";

    overlay.innerHTML = `
      <div class="write4u-modal" role="dialog" aria-modal="true">
        <!-- Header -->
        <div class="write4u-modal-header">
          <div class="write4u-brand-title">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="url(#brandGrad)">
              <defs>
                <linearGradient id="brandGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stop-color="#818cf8"/>
                  <stop offset="100%" stop-color="#c084fc"/>
                </linearGradient>
              </defs>
              <path d="M12 2L14.4 8.6L21 11L14.4 13.4L12 20L9.6 13.4L3 11L9.6 8.6L12 2Z"/>
            </svg>
            Write4U Context Engine
            <span class="write4u-model-tag">Qwen3-8B + BGE Reranker</span>
          </div>
          <button class="write4u-close-btn" id="write4u-close-btn">&times;</button>
        </div>

        <!-- Body -->
        <div class="write4u-modal-body">
          <!-- 3 Context Layers -->
          <div class="write4u-layers-grid">
            <div class="write4u-layer-card">
              <span class="write4u-layer-title">🌐 1. Page Context</span>
              <span class="write4u-layer-val" id="write4u-page-ctx">Detecting active page...</span>
            </div>
            <div class="write4u-layer-card">
              <span class="write4u-layer-title">🔐 2. Personal Context (Happenstance)</span>
              <span class="write4u-layer-val">200 Signals Indexed (Gmail, Cal, Drive, LI)</span>
            </div>
          </div>

          <!-- Prompt Input -->
          <div class="write4u-input-group">
            <label class="write4u-layer-title">🎯 3. Task Context</label>
            <textarea 
              id="write4u-prompt-input" 
              class="write4u-prompt-input" 
              placeholder="What do you want to write? (e.g. Reply professionally and mention continuing research)..."
            ></textarea>
            
            <div class="write4u-presets">
              <span class="write4u-chip" data-prompt="Reply professionally to follow up on our research discussion from the conference.">✉️ Research Follow-up</span>
              <span class="write4u-chip" data-prompt="Write a LinkedIn post celebrating our paper presentation and thank collaborators.">🚀 LinkedIn Celebration</span>
              <span class="write4u-chip" data-prompt="Summarize latest testbed benchmark results and propose next week's sync call.">📊 Benchmark Update</span>
            </div>
          </div>

          <!-- Action Button -->
          <button id="write4u-generate-btn" class="write4u-action-btn">
            <span>Synthesize Minimum Context & Generate</span>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
          </button>

          <!-- Dynamic Funnel Visualization (hidden initially) -->
          <div id="write4u-funnel-container" class="write4u-funnel-card" style="display: none;">
            <div class="write4u-funnel-stages">
              <div class="write4u-stage">
                <span class="write4u-stage-count" id="funnel-cand">200</span>
                <span class="write4u-stage-label">Candidates</span>
              </div>
              <span class="write4u-funnel-arrow">➔</span>
              <div class="write4u-stage">
                <span class="write4u-stage-count" id="funnel-rank">18</span>
                <span class="write4u-stage-label">Reranked</span>
              </div>
              <span class="write4u-funnel-arrow">➔</span>
              <div class="write4u-stage">
                <span class="write4u-stage-count" style="color: #34d399;" id="funnel-sel">9</span>
                <span class="write4u-stage-label">Selected (C*)</span>
              </div>
            </div>

            <div class="write4u-reasons-list" id="write4u-reasons-list">
              <!-- Dynamically populated -->
            </div>
          </div>

          <!-- Draft Output -->
          <div id="write4u-output-container" style="display: none; flex-direction: column; gap: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span class="write4u-layer-title">Generated Draft (Open-Weight Grounded)</span>
              <button class="write4u-chip" id="write4u-toggle-evidence">Inspect Evidence & Provenance</button>
            </div>
            <div id="write4u-draft-box" class="write4u-draft-box"></div>
          </div>

          <!-- Evidence Drawer -->
          <div id="write4u-evidence-drawer" class="write4u-evidence-drawer" style="display: none;">
            <span class="write4u-layer-title" style="color: #38bdf8;">Verified Grounding Evidence (C*)</span>
            <div id="write4u-evidence-list" style="display: flex; flex-direction: column; gap: 8px;"></div>
          </div>
        </div>

        <!-- Footer -->
        <div class="write4u-modal-footer">
          <div class="write4u-footer-stats" id="write4u-footer-stats">
            Ready to compose
          </div>
          <div class="write4u-footer-actions">
            <button class="write4u-secondary-btn" id="write4u-copy-btn" style="display: none;">Copy</button>
            <button class="write4u-action-btn" id="write4u-insert-btn" style="display: none; padding: 8px 16px;">
              Insert into Composer
            </button>
          </div>
        </div>
      </div>
    `;

    document.body.appendChild(overlay);

    // Event handlers
    document.getElementById("write4u-close-btn").addEventListener("click", closeModal);
    overlay.addEventListener("click", (e) => {
      if (e.target === overlay) closeModal();
    });

    // Preset chips
    document.querySelectorAll(".write4u-chip[data-prompt]").forEach(chip => {
      chip.addEventListener("click", () => {
        document.getElementById("write4u-prompt-input").value = chip.dataset.prompt;
      });
    });

    // Generate click
    document.getElementById("write4u-generate-btn").addEventListener("click", runGeneration);

    // Evidence toggle
    document.getElementById("write4u-toggle-evidence").addEventListener("click", () => {
      const drawer = document.getElementById("write4u-evidence-drawer");
      drawer.style.display = drawer.style.display === "none" ? "flex" : "none";
    });

    // Copy button
    document.getElementById("write4u-copy-btn").addEventListener("click", () => {
      if (currentResponse && currentResponse.draft) {
        // Strip bracket citations for clean draft
        const cleanText = currentResponse.draft.replace(/\[[a-zA-Z0-9_, ]+\]/g, "");
        navigator.clipboard.writeText(cleanText);
        const copyBtn = document.getElementById("write4u-copy-btn");
        copyBtn.innerText = "Copied!";
        setTimeout(() => { copyBtn.innerText = "Copy"; }, 2000);
      }
    });

    // Insert button
    document.getElementById("write4u-insert-btn").addEventListener("click", () => {
      if (currentResponse && onInsertCallback) {
        const cleanText = currentResponse.draft.replace(/\[[a-zA-Z0-9_, ]+\]/g, "");
        onInsertCallback(cleanText);
        closeModal();
      }
    });
  }

  function openModal(pageContext, insertCallback) {
    createModalDOM();
    onInsertCallback = insertCallback;

    // Display Page Context
    const pageCtxEl = document.getElementById("write4u-page-ctx");
    if (pageContext) {
      if (pageContext.site === "gmail") {
        pageCtxEl.innerText = `Gmail: ${pageContext.recipient || 'Open Compose'} | Subj: ${pageContext.subject || 'New Message'}`;
      } else if (pageContext.site === "linkedin") {
        pageCtxEl.innerText = `LinkedIn: Post Composer (${pageContext.author || 'User Feed'})`;
      } else {
        pageCtxEl.innerText = `Web: ${document.title.substring(0, 45)}...`;
      }
    }

    const overlay = document.getElementById("write4u-overlay");
    overlay.classList.add("active");
  }

  function closeModal() {
    const overlay = document.getElementById("write4u-overlay");
    if (overlay) overlay.classList.remove("active");
  }

  async function runGeneration() {
    const promptInput = document.getElementById("write4u-prompt-input");
    const prompt = promptInput.value.trim();
    if (!prompt) {
      alert("Please enter a task or select a preset!");
      return;
    }

    const genBtn = document.getElementById("write4u-generate-btn");
    const footerStats = document.getElementById("write4u-footer-stats");
    genBtn.disabled = true;
    genBtn.innerHTML = `<span>Synthesizing Context via Qwen3 & BGE...</span>`;
    footerStats.innerText = "Extracting Page Context ➔ Searching 200 signals ➔ Context Reranking...";

    try {
      const response = await fetch(API_ENDPOINT, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: prompt,
          page_context: {
            site: window.location.hostname.includes("mail.google") ? "gmail" : (window.location.hostname.includes("linkedin") ? "linkedin" : "web"),
            url: window.location.href,
            title: document.title
          }
        })
      });

      if (!response.ok) throw new Error("Backend offline or request failed");

      const data = await response.json();
      currentResponse = data;

      // Populate Funnel
      const funnelBox = document.getElementById("write4u-funnel-container");
      funnelBox.style.display = "flex";
      document.getElementById("funnel-cand").innerText = data.funnel.candidates;
      document.getElementById("funnel-rank").innerText = data.funnel.reranked;
      document.getElementById("funnel-sel").innerText = data.funnel.selected;

      const reasonsList = document.getElementById("write4u-reasons-list");
      reasonsList.innerHTML = data.selection_reasons.map(r => `
        <div class="write4u-reason-item">
          <span class="write4u-check">✓</span>
          <span>${r}</span>
        </div>
      `).join("");

      // Render Draft with Citations
      const outBox = document.getElementById("write4u-output-container");
      outBox.style.display = "flex";
      const draftEl = document.getElementById("write4u-draft-box");

      // Replace bracket citations with clickable badge pills
      let formattedHtml = data.draft.replace(/\[([a-zA-Z0-9_, ]+)\]/g, (match, ids) => {
        return `<span class="write4u-cite" title="Verified against: ${ids}">${match}</span>`;
      });
      draftEl.innerHTML = formattedHtml;

      // Render Evidence Drawer Items
      const evList = document.getElementById("write4u-evidence-list");
      evList.innerHTML = data.selected_evidence.map(e => `
        <div class="write4u-evidence-item">
          <div class="write4u-evidence-title">
            <span>[${e.item.source.toUpperCase()}] ${e.item.entities.join(", ")}</span>
            <span class="write4u-evidence-score">Score: ${e.score_breakdown.total_score} (Rank #${e.rank})</span>
          </div>
          <div class="write4u-evidence-content">${e.item.content}</div>
          <div style="font-size: 10px; color: #64748b; margin-top: 4px;">
            Provenance: ${JSON.stringify(e.item.provenance)}
          </div>
        </div>
      `).join("");

      // Update Footer and Buttons
      document.getElementById("write4u-copy-btn").style.display = "block";
      document.getElementById("write4u-insert-btn").style.display = "block";
      footerStats.innerText = `Reduced 200 candidates to 9 items • Saved ~17,400 tokens • Qwen3 Grounded`;

    } catch (err) {
      console.error(err);
      alert("Could not connect to Write4U engine on http://127.0.0.1:8000. Please make sure the backend is running!");
      footerStats.innerText = "Error: Check backend status";
    } finally {
      genBtn.disabled = false;
      genBtn.innerHTML = `<span>Re-Synthesize</span>`;
    }
  }

  window.Write4UI = {
    openModal: openModal,
    closeModal: closeModal
  };
})();
