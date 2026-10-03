/**
 * Write4U Core Detector:
 * Selects and mounts the appropriate SiteAdapter on page load.
 */
(function () {
  console.log("[Write4U] Core Detector initializing on:", window.location.hostname);

  const hostname = window.location.hostname.toLowerCase();
  let adapter = null;

  if (hostname.includes("mail.google.com")) {
    adapter = new window.GmailAdapter();
  } else if (hostname.includes("linkedin.com")) {
    adapter = new window.LinkedInAdapter();
  } else {
    adapter = new window.GenericAdapter();
  }

  const injector = new window.Write4UInjector();

  // Watch for composer elements
  adapter.observeComposer((composer, currentAdapter) => {
    if (currentAdapter.name === "generic") {
      injector.showFloatingBadge(composer, currentAdapter);
    } else {
      injector.injectToolbarButton(composer, currentAdapter);
    }
  });

  // Runtime message listener for popup and background actions
  if (typeof chrome !== "undefined" && chrome.runtime && chrome.runtime.onMessage) {
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
      if (request.action === "INSERT_TEXT" && request.text) {
        const activeComposer = adapter.findComposer() || document.activeElement;
        if (activeComposer) {
          adapter.insertText(activeComposer, request.text);
          sendResponse({ success: true });
          return true;
        }
      }
      if (request.action === "TRIGGER_WRITE4U" || request.action === "TRIGGER_WRITRIEVE") {
        const activeComposer = adapter.findComposer() || document.activeElement;
        if (activeComposer) {
          injector.focusInlineBar(activeComposer, adapter);
          sendResponse({ success: true });
          return true;
        }
      }
      sendResponse({ success: false });
      return true;
    });
  }

  // Export instances for debugging / testing
  window.__WRITE4U_ADAPTER__ = adapter;
  window.__WRITE4U_INJECTOR__ = injector;
})();
