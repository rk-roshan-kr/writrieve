/**
 * SubstackAdapter: Integration for Substack post, note, and newsletter composer.
 */
class SubstackAdapter extends SiteAdapter {
  constructor() {
    super("substack");
  }

  findComposer(container = document) {
    return container.querySelector(
      "div.post-editor, div.prose, div[role='textbox'], div[contenteditable='true'], textarea"
    );
  }

  getComposerWrapper(composer) {
    if (!composer) return null;
    return composer.closest(".post-editor-container") || composer.closest("main") || composer.parentElement;
  }

  getRecipient(composer) {
    return "Substack Subscribers";
  }

  getSubject(composer) {
    const titleEl = document.querySelector("textarea[placeholder='Title'], h1.post-title");
    return titleEl ? (titleEl.value || titleEl.innerText || "") : "Substack Post";
  }

  getExistingText(composer) {
    return composer ? (composer.innerText || composer.textContent || "") : "";
  }

  getToolbar(composer) {
    const wrapper = this.getComposerWrapper(composer);
    if (!wrapper) return composer ? composer.parentElement : null;
    return wrapper.querySelector(".editor-toolbar, .post-editor-header, .top-bar") || composer.parentElement;
  }

  observeComposer(callback) {
    const visited = new WeakSet();
    const scan = () => {
      const composers = document.querySelectorAll(
        "div.post-editor, div.prose, div[role='textbox'], textarea.post-content"
      );
      composers.forEach((composer) => {
        if (!visited.has(composer)) {
          visited.add(composer);
          callback(composer, this);
        }
      });
    };
    scan();
    const observer = new MutationObserver(() => scan());
    observer.observe(document.body, { childList: true, subtree: true });
  }
}

if (typeof window !== "undefined") {
  window.SubstackAdapter = SubstackAdapter;
}
