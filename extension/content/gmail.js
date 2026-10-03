// Write4U Content Script for Gmail
(function () {
  console.log("[Write4U] Gmail context script initialized");

  function injectBadgeIntoCompose(composeEl) {
    if (composeEl.querySelector(".write4u-gmail-badge")) return;

    // Look for Gmail toolbar or compose header
    const toolbar = composeEl.querySelector(".btC") || composeEl.querySelector("[role='toolbar']") || composeEl;

    const badge = document.createElement("button");
    badge.className = "write4u-badge-btn write4u-gmail-badge";
    badge.type = "button";
    badge.innerHTML = `
      <svg viewBox="0 0 24 24"><path d="M12 2L14.4 8.6L21 11L14.4 13.4L12 20L9.6 13.4L3 11L9.6 8.6L12 2Z"/></svg>
      Write4U ✦
    `;

    badge.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();

      // Extract Gmail Page Context
      const recipientInput = composeEl.querySelector("[name='to']") || composeEl.querySelector(".vR span");
      const subjectInput = composeEl.querySelector("[name='subjectbox']");
      const messageBody = composeEl.querySelector("[role='textbox']") || composeEl.querySelector(".Am.Al.editable");

      const recipient = recipientInput ? (recipientInput.value || recipientInput.innerText || "Recipient") : "Prof. Xavier Vance";
      const subject = subjectInput ? (subjectInput.value || "Continuing Research") : "Great meeting you at CCNCPS";

      const pageContext = {
        site: "gmail",
        recipient: recipient,
        subject: subject,
        type: "email_compose"
      };

      window.Write4UI.openModal(pageContext, (generatedText) => {
        if (messageBody) {
          messageBody.focus();
          // Insert formatted text into Gmail contenteditable
          document.execCommand("insertText", false, generatedText);
          messageBody.dispatchEvent(new Event("input", { bubbles: true }));
        }
      });
    });

    if (toolbar.firstChild) {
      toolbar.insertBefore(badge, toolbar.firstChild);
    } else {
      toolbar.appendChild(badge);
    }
  }

  // Observe Gmail DOM for newly opened compose dialogs
  const observer = new MutationObserver(() => {
    const dialogs = document.querySelectorAll("[role='dialog'], .AD, .inboxsdk__compose");
    dialogs.forEach(dialog => injectBadgeIntoCompose(dialog));
  });

  observer.observe(document.body, { childList: true, subtree: true });
})();
