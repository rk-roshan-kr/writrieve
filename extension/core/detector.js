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

  // Export instances for debugging / testing
  window.__WRITE4U_ADAPTER__ = adapter;
  window.__WRITE4U_INJECTOR__ = injector;
})();
