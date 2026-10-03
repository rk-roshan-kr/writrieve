// Write4U Generic Content Script
(function () {
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "TRIGGER_WRITE4U") {
      const activeEl = document.activeElement;
      const isEditable = activeEl && (
        activeEl.tagName === "TEXTAREA" ||
        activeEl.tagName === "INPUT" ||
        activeEl.isContentEditable
      );

      const pageContext = {
        site: window.location.hostname,
        title: document.title,
        url: window.location.href,
        hasActiveInput: !!isEditable
      };

      if (window.Write4UI) {
        window.Write4UI.openModal(pageContext, (generatedText) => {
          if (isEditable) {
            if (activeEl.isContentEditable) {
              document.execCommand("insertText", false, generatedText);
            } else {
              activeEl.value = generatedText;
            }
          }
        });
      }
      sendResponse({ status: "ok" });
    }
  });
})();
