/**
 * GmailAdapter: Native integration for Google Mail web client.
 * Discovers compose dialogs, inline replies, subjects, recipients, and toolbars.
 */
class GmailAdapter extends SiteAdapter {
  constructor() {
    super("gmail");
  }

  findComposer(container = document) {
    // Matches active compose dialogs, inline replies, and popouts
    return container.querySelector(
      "div[role='dialog'] div[role='textbox'], div.Am.Al.editable, div[aria-label='Message Body']"
    );
  }

  getComposerWrapper(composer) {
    if (!composer) return null;
    return (
      composer.closest("div[role='dialog']") ||
      composer.closest(".AD") ||
      composer.closest(".M9") ||
      composer.closest("table") ||
      composer.parentElement
    );
  }

  getRecipient(composer) {
    const wrapper = this.getComposerWrapper(composer);
    if (!wrapper) return null;

    // Check chips / recipient spans / to fields
    const recipientSpan =
      wrapper.querySelector("span[email]") ||
      wrapper.querySelector(".vR span") ||
      wrapper.querySelector(".aoD.hl span") ||
      wrapper.querySelector("input[name='to']");

    if (recipientSpan) {
      return (
        recipientSpan.getAttribute("email") ||
        recipientSpan.value ||
        recipientSpan.innerText ||
        null
      );
    }
    return null;
  }

  getSubject(composer) {
    const wrapper = this.getComposerWrapper(composer);
    if (!wrapper) return null;

    const subjectInput =
      wrapper.querySelector("input[name='subjectbox']") ||
      wrapper.querySelector("input[aria-label='Subject']") ||
      wrapper.querySelector(".aoT");

    if (subjectInput) {
      return subjectInput.value || subjectInput.innerText || null;
    }
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
      wrapper.querySelector(".btC") ||
      wrapper.querySelector("div[role='toolbar']") ||
      wrapper.querySelector(".gU.Up") ||
      wrapper.querySelector(".IZ")
    );
  }

  observeComposer(callback) {
    const visited = new WeakSet();

    const scan = () => {
      // Check for all dialogs and inline reply boxes
      const dialogs = document.querySelectorAll(
        "div[role='dialog'], .AD, .inboxsdk__compose, .M9, .ha"
      );
      dialogs.forEach((dialog) => {
        const composer = this.findComposer(dialog);
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
  window.GmailAdapter = GmailAdapter;
}
