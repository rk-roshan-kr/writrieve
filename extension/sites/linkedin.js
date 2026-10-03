/**
 * LinkedInAdapter: Native integration for LinkedIn web app.
 * Detects feed post composers, article drafts, and 1:1 direct messages.
 */
class LinkedInAdapter extends SiteAdapter {
  constructor() {
    super("linkedin");
  }

  findComposer(container = document) {
    return container.querySelector(
      "div.editor-content div[role='textbox'], div.ql-editor, div[contenteditable='true'][data-placeholder], .msg-form__contenteditable"
    );
  }

  getComposerWrapper(composer) {
    if (!composer) return null;
    return (
      composer.closest(".share-creation-state") ||
      composer.closest(".share-box-feed-entry__wrapper") ||
      composer.closest(".msg-form") ||
      composer.closest("div[role='dialog']") ||
      composer.parentElement
    );
  }

  getRecipient(composer) {
    const wrapper = this.getComposerWrapper(composer);
    if (!wrapper) return null;

    // Check message header if inside direct message thread
    const msgPartner =
      wrapper.closest(".msg-convo-wrapper")?.querySelector(".msg-entity-lockup__entity-title") ||
      document.querySelector(".msg-overlay-bubble-header__title");

    if (msgPartner) {
      return msgPartner.innerText.trim();
    }
    return null;
  }

  getSubject(composer) {
    // LinkedIn posts do not have subject lines; returns topic or null
    return null;
  }

  getExistingText(composer) {
    if (!composer) return "";
    return composer.innerText || composer.textContent || "";
  }

  getToolbar(composer) {
    const wrapper = this.getComposerWrapper(composer);
    if (!wrapper) return composer ? composer.parentElement : null;

    return (
      wrapper.querySelector(".share-box-footer") ||
      wrapper.querySelector(".share-actions") ||
      wrapper.querySelector(".share-creation-state__bottom-bar") ||
      wrapper.querySelector(".msg-form__footer") ||
      wrapper.querySelector(".msg-form__left-actions")
    );
  }

  observeComposer(callback) {
    const visited = new WeakSet();

    const scan = () => {
      const candidates = document.querySelectorAll(
        ".share-creation-state, .share-box-feed-entry__wrapper, div[role='dialog'], .msg-form"
      );
      candidates.forEach((cand) => {
        const composer = this.findComposer(cand);
        if (composer && !visited.has(composer)) {
          visited.add(composer);
          callback(composer, this);
        }
      });
    };

    scan();
    const observer = new MutationObserver(() => scan());
    observer.observe(document.body, { childList: true, subtree: true });
    return observer;
  }
}

if (typeof window !== "undefined") {
  window.LinkedInAdapter = LinkedInAdapter;
}
