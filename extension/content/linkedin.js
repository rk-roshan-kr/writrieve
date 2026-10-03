// Write4U Content Script for LinkedIn
(function () {
  console.log("[Write4U] LinkedIn context script initialized");

  function injectBadgeIntoLinkedIn(composerEl) {
    if (composerEl.querySelector(".write4u-li-badge")) return;

    const actionToolbar = composerEl.querySelector(".share-box-footer") || 
                          composerEl.querySelector(".share-actions") || 
                          composerEl.querySelector(".share-creation-state__bottom-bar") || 
                          composerEl;

    const badge = document.createElement("button");
    badge.className = "write4u-badge-btn write4u-li-badge";
    badge.type = "button";
    badge.innerHTML = `
      <svg viewBox="0 0 24 24"><path d="M12 2L14.4 8.6L21 11L14.4 13.4L12 20L9.6 13.4L3 11L9.6 8.6L12 2Z"/></svg>
      Write4U ✦
    `;

    badge.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();

      // Extract LinkedIn Page Context
      const editor = composerEl.querySelector(".editor-content div[role='textbox'], .ql-editor, div[contenteditable='true']");
      const pageContext = {
        site: "linkedin",
        author: "User",
        type: "post_composer"
      };

      window.Write4UI.openModal(pageContext, (generatedText) => {
        if (editor) {
          editor.focus();
          document.execCommand("insertText", false, generatedText);
          editor.dispatchEvent(new Event("input", { bubbles: true }));
        }
      });
    });

    if (actionToolbar.firstChild) {
      actionToolbar.insertBefore(badge, actionToolbar.firstChild);
    } else {
      actionToolbar.appendChild(badge);
    }
  }

  const observer = new MutationObserver(() => {
    const shareBoxes = document.querySelectorAll(".share-box-feed-entry__wrapper, .share-creation-state, [role='dialog']");
    shareBoxes.forEach(box => injectBadgeIntoLinkedIn(box));
  });

  observer.observe(document.body, { childList: true, subtree: true });
})();
