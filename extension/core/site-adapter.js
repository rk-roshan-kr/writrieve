/**
 * Base SiteAdapter interface for Write4U browser integration.
 * Adapters decouple website-specific DOM structures from the Write4U engine.
 */
class SiteAdapter {
  constructor(name) {
    this.name = name;
  }

  /**
   * Locate the active composer element(s) on the page.
   * @returns {HTMLElement|null}
   */
  findComposer() {
    throw new Error("findComposer() must be implemented by subclass");
  }

  /**
   * Extract recipient or conversation partner if available.
   * @returns {string|null}
   */
  getRecipient(composer) {
    return null;
  }

  /**
   * Extract email subject or thread title if available.
   * @returns {string|null}
   */
  getSubject(composer) {
    return null;
  }

  /**
   * Extract any existing draft or preceding text.
   * @returns {string}
   */
  getExistingText(composer) {
    return "";
  }

  /**
   * Locate the action toolbar where the Write4U button should be injected.
   * @returns {HTMLElement|null}
   */
  getToolbar(composer) {
    return composer;
  }

  /**
   * Safely insert generated text into the active composer.
   * Preserves undo stack and triggers site-specific change events.
   * @param {HTMLElement} composer
   * @param {string} text
   */
  insertText(composer, text) {
    if (!composer) return false;
    composer.focus();

    if (composer.isContentEditable) {
      // Use execCommand to preserve browser undo history
      const success = document.execCommand("insertText", false, text);
      if (!success) {
        composer.innerText = text;
      }
      composer.dispatchEvent(new Event("input", { bubbles: true }));
      composer.dispatchEvent(new Event("change", { bubbles: true }));
      return true;
    } else if (composer.tagName === "TEXTAREA" || composer.tagName === "INPUT") {
      const start = composer.selectionStart || 0;
      const end = composer.selectionEnd || 0;
      const val = composer.value;
      composer.value = val.substring(0, start) + text + val.substring(end);
      composer.selectionStart = composer.selectionEnd = start + text.length;
      composer.dispatchEvent(new Event("input", { bubbles: true }));
      composer.dispatchEvent(new Event("change", { bubbles: true }));
      return true;
    }
    return false;
  }

  /**
   * Observe DOM mutations for newly opened composers.
   * @param {function(composer: HTMLElement, adapter: SiteAdapter)} callback
   */
  observeComposer(callback) {
    throw new Error("observeComposer() must be implemented by subclass");
  }
}

if (typeof window !== "undefined") {
  window.SiteAdapter = SiteAdapter;
}
