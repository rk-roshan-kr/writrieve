/**
 * GenericAdapter: Universal fallback for arbitrary websites.
 * Detects focused textareas, inputs, and contenteditables, rendering a floating ✦ Write4U badge.
 */
class GenericAdapter extends SiteAdapter {
  constructor() {
    super("generic");
    this.currentActiveEl = null;
    this.floatingBadge = null;
  }

  findComposer(container = document) {
    const el = document.activeElement;
    if (this.isEditable(el)) return el;
    return container.querySelector("textarea, [contenteditable='true']");
  }

  isEditable(el) {
    if (!el) return false;
    const tag = el.tagName;
    if (tag === "TEXTAREA") return true;
    if (tag === "INPUT" && ["text", "search", "email"].includes(el.type || "text")) return true;
    if (el.isContentEditable) return true;
    return false;
  }

  getRecipient(composer) {
    return null;
  }

  getSubject(composer) {
    return document.title || null;
  }

  getExistingText(composer) {
    if (!composer) return "";
    return composer.isContentEditable ? composer.innerText : composer.value || "";
  }

  getToolbar(composer) {
    return null; // Floating button managed directly
  }

  observeComposer(callback) {
    document.addEventListener("focusin", (e) => {
      const target = e.target;
      if (this.isEditable(target)) {
        this.currentActiveEl = target;
        callback(target, this);
      }
    });

    // Also support keyboard shortcut / context menu trigger
    chrome.runtime?.onMessage?.addListener((request, sender, sendResponse) => {
      if (request.action === "TRIGGER_WRITE4U") {
        const target = this.currentActiveEl || this.findComposer();
        if (target) {
          callback(target, this);
        }
        sendResponse({ status: "ok" });
      }
    });
  }
}

if (typeof window !== "undefined") {
  window.GenericAdapter = GenericAdapter;
}
