/**
 * Legacy modal completely disabled.
 * Writrieve operates strictly via native inline composer injection.
 */
(function () {
  window.Write4UI = {
    openModal: function (pageContext, callback) {
      console.log("[Writrieve] Native inline injection active; modal suppressed.");
      const bar = document.querySelector(".writrieve-inline-bar");
      if (bar) {
        bar.scrollIntoView({ behavior: "smooth", block: "nearest" });
        const input = bar.querySelector(".writrieve-inline-input");
        if (input) input.focus();
      }
    }
  };
})();
