// Write4U Background Service Worker (Manifest V3)
const BACKEND_BASE = "http://127.0.0.1:8000";

chrome.runtime.onInstalled.addListener(() => {
  console.log("[Write4U Worker] Extension installed and background worker active.");
  chrome.contextMenus.create({
    id: "write4u-generate",
    title: "✦ Write with Write4U Context",
    contexts: ["editable", "selection"]
  });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "write4u-generate" && tab?.id) {
    chrome.tabs.sendMessage(tab.id, { action: "TRIGGER_WRITE4U" });
  }
});

// Message listener for content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "EXECUTE_WRITE4U") {
    const payload = request.payload || {};
    
    // Call Write4U Backend v2 execution endpoint
    fetch(`${BACKEND_BASE}/api/v2/execute`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt: payload.prompt,
        recipient: payload.pageContext?.recipient || undefined,
        channel: payload.pageContext?.site === "gmail" ? "email" : (payload.pageContext?.site === "linkedin" ? "linkedin" : "generic"),
        urgency: "medium",
        style_preset: payload.style || "my_style",
        page_context: payload.pageContext
      })
    })
      .then(async (res) => {
        if (!res.ok) {
          const errText = await res.text();
          throw new Error(`Write4U API returned ${res.status}: ${errText}`);
        }
        return res.json();
      })
      .then((data) => {
        sendResponse({ success: true, data });
      })
      .catch((err) => {
        console.error("[Write4U Worker] Request failed:", err);
        sendResponse({ success: false, error: err.message });
      });

    return true; // Keep message channel open for async response
  }

  if (request.action === "CHECK_HEALTH") {
    fetch(`${BACKEND_BASE}/api/health`)
      .then((res) => res.json())
      .then((data) => sendResponse({ success: true, data }))
      .catch((err) => sendResponse({ success: false, error: err.message }));
    return true;
  }
});
