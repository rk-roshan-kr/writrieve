/**
 * Write4U Messaging Client.
 * Bridges between the thin in-page Content Script and the Extension Service Worker / Backend.
 */
class Write4UMessaging {
  static async executeTask({ prompt, pageContext, style = "my_style", length = "auto" }) {
    // 1. Try sending via chrome.runtime to Background Service Worker
    if (typeof chrome !== "undefined" && chrome.runtime && chrome.runtime.sendMessage) {
      try {
        const response = await new Promise((resolve, reject) => {
          chrome.runtime.sendMessage(
            {
              action: "EXECUTE_WRITE4U",
              payload: { prompt, pageContext, style, length }
            },
            (res) => {
              if (chrome.runtime.lastError) {
                reject(new Error(chrome.runtime.lastError.message));
              } else {
                resolve(res);
              }
            }
          );
        });

        if (response && response.success) {
          return response.data;
        } else if (response && response.error) {
          throw new Error(response.error);
        }
      } catch (err) {
        console.warn("[Write4U Messaging] Service worker dispatch failed, falling back to direct fetch:", err);
      }
    }

    // 2. Direct fetch fallback (for local web simulator or worker timeout)
    const res = await fetch("http://127.0.0.1:8000/api/v2/execute", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt: prompt,
        recipient: pageContext.recipient || undefined,
        channel: pageContext.site === "gmail" ? "email" : (pageContext.site === "linkedin" ? "linkedin" : "generic"),
        urgency: "medium",
        style_preset: style,
        page_context: pageContext
      })
    });

    if (!res.ok) {
      const errBody = await res.text();
      throw new Error(`Write4U Backend error (${res.status}): ${errBody}`);
    }

    return await res.json();
  }
}

if (typeof window !== "undefined") {
  window.Write4UMessaging = Write4UMessaging;
}
