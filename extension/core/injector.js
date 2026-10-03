/**
 * Writrieve UI Injector:
 * Responsible for injecting native writing controls and the inline "Describe your message"
 * bar directly into the host website's composer without any modal popups.
 */
class Write4UInjector {
  constructor() {
    this.currentComposer = null;
    this.currentAdapter = null;
    this.currentResponse = null;
    this.floatingBadge = null;
  }

  /**
   * Injects the native ✦ Writrieve button into a composer toolbar,
   * along with the inline "Describe your message" pill bar above the composer.
   */
  injectToolbarButton(composer, adapter) {
    this.currentComposer = composer;
    this.currentAdapter = adapter;

    // 1. Inject the inline "Describe your message" pill bar directly into composer wrapper
    this.ensureInlineDescribeBar(composer, adapter);

    // 2. Inject toolbar button
    const toolbar = adapter.getToolbar(composer);
    if (!toolbar) return;

    if (toolbar.querySelector(".writrieve-injected-trigger")) return;

    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "write4u-badge-btn writrieve-injected-trigger";
    btn.innerHTML = `
      <svg width="14" height="14" viewBox="0 0 24 24" fill="url(#brandGrad)">
        <defs>
          <linearGradient id="brandGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#818cf8"/>
            <stop offset="100%" stop-color="#c084fc"/>
          </linearGradient>
        </defs>
        <path d="M12 2L14.4 8.6L21 11L14.4 13.4L12 20L9.6 13.4L3 11L9.6 8.6L12 2Z"/>
      </svg>
      <span>✦ Writrieve</span>
    `;

    btn.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      this.focusInlineBar(composer, adapter);
    });

    if (toolbar.firstChild) {
      toolbar.insertBefore(btn, toolbar.firstChild);
    } else {
      toolbar.appendChild(btn);
    }
  }

  /**
   * Injects the native inline "Describe your message" bar inside the composer container.
   */
  ensureInlineDescribeBar(composer, adapter) {
    const parent = composer.parentElement;
    if (!parent) return;

    if (parent.querySelector(".writrieve-inline-bar")) return;

    const bar = document.createElement("div");
    bar.className = "writrieve-inline-bar";
    bar.innerHTML = `
      <div class="writrieve-inline-inner">
        <span class="writrieve-inline-icon">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2L14.4 8.6L21 11L14.4 13.4L12 20L9.6 13.4L3 11L9.6 8.6L12 2Z"/>
          </svg>
        </span>
        <input 
          type="text" 
          class="writrieve-inline-input" 
          placeholder="Describe your message (e.g. Follow up with Professor Xavier about FieldChain)..." 
        />
        <div class="writrieve-inline-actions">
          <span class="writrieve-inline-badge">Composio + Memory</span>
          <button type="button" class="writrieve-inline-btn">Create</button>
        </div>
      </div>
    `;

    // Insert right before the composer or at top of parent
    parent.insertBefore(bar, composer);

    const input = bar.querySelector(".writrieve-inline-input");
    const createBtn = bar.querySelector(".writrieve-inline-btn");

    const handleCreate = () => {
      const prompt = input.value.trim();
      if (!prompt) return;
      this.executeInlineGeneration(prompt, composer, adapter, bar);
    };

    createBtn.addEventListener("click", (e) => {
      e.preventDefault();
      handleCreate();
    });

    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleCreate();
      }
    });
  }

  focusInlineBar(composer, adapter) {
    const parent = composer.parentElement;
    const bar = parent ? parent.querySelector(".writrieve-inline-bar") : null;
    if (bar) {
      const input = bar.querySelector(".writrieve-inline-input");
      if (input) {
        input.focus();
        bar.scrollIntoView({ behavior: "smooth", block: "nearest" });
      }
    } else {
      this.ensureInlineDescribeBar(composer, adapter);
      this.focusInlineBar(composer, adapter);
    }
  }

  /**
   * Executes the context retrieval and generation, inserting directly into composer.
   */
  async executeInlineGeneration(prompt, composer, adapter, bar) {
    const input = bar.querySelector(".writrieve-inline-input");
    const createBtn = bar.querySelector(".writrieve-inline-btn");

    input.disabled = true;
    createBtn.disabled = true;
    createBtn.innerText = "Writing...";

    const pageContext = {
      site: adapter.name,
      recipient: adapter.getRecipient(composer),
      subject: adapter.getSubject(composer),
      existingText: adapter.getExistingText(composer),
      url: window.location.href,
      title: document.title
    };

    try {
      const data = await window.Write4UMessaging.executeTask({
        prompt,
        pageContext,
        style: "my_style",
        length: "auto"
      });

      this.currentResponse = data;

      // Insert generated draft directly into the composer
      adapter.insertText(composer, data.draft);

      // Render inline verification pill directly beneath the bar
      this.renderStatusPill(bar, composer, adapter, data);

      // Clear input
      input.value = "";
    } catch (err) {
      alert(`Writrieve Error: ${err.message}`);
    } finally {
      input.disabled = false;
      createBtn.disabled = false;
      createBtn.innerText = "Create";
    }
  }

  renderStatusPill(bar, composer, adapter, data) {
    const existingPill = bar.parentElement.querySelector(".writrieve-status-pill");
    if (existingPill) existingPill.remove();

    const pill = document.createElement("div");
    pill.className = "writrieve-status-pill";
    pill.innerHTML = `
      <span>✦ Grounded with Composio (${data.evidence_state?.source_counts?.gmail ?? 1} emails, ${data.evidence_state?.source_counts?.calendar ?? 1} events, memory)</span>
      <span class="pill-action" id="w4u-recreate-btn">🔄 Recreate</span>
      <span class="pill-action" id="w4u-dismiss-btn" style="color: #94a3b8;">✕ Dismiss</span>
    `;

    bar.after(pill);

    pill.querySelector("#w4u-recreate-btn").addEventListener("click", () => {
      this.focusInlineBar(composer, adapter);
    });

    pill.querySelector("#w4u-dismiss-btn").addEventListener("click", () => {
      pill.remove();
    });
  }

  /**
   * Positions a floating ✦ button near a focused editable element on generic sites.
   */
  showFloatingBadge(composer, adapter) {
    if (!this.floatingBadge) {
      this.floatingBadge = document.createElement("button");
      this.floatingBadge.type = "button";
      this.floatingBadge.className = "write4u-badge-btn write4u-floating-pill";
      this.floatingBadge.innerHTML = `<span>✦ Writrieve</span>`;
      document.body.appendChild(this.floatingBadge);

      this.floatingBadge.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (this.currentComposer && this.currentAdapter) {
          this.focusInlineBar(this.currentComposer, this.currentAdapter);
        }
      });
    }

    this.currentComposer = composer;
    this.currentAdapter = adapter;

    const rect = composer.getBoundingClientRect();
    this.floatingBadge.style.position = "fixed";
    this.floatingBadge.style.zIndex = "999999";
    this.floatingBadge.style.top = `${Math.max(10, rect.bottom - 36)}px`;
    this.floatingBadge.style.left = `${Math.max(10, rect.right - 110)}px`;
    this.floatingBadge.style.display = "flex";
  }

  hideFloatingBadge() {
    if (this.floatingBadge) {
      this.floatingBadge.style.display = "none";
    }
  }
}

if (typeof window !== "undefined") {
  window.Write4UInjector = Write4UInjector;
}
