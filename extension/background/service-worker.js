// Write4U Background Service Worker (Manifest V3)
chrome.runtime.onInstalled.addListener(() => {
  console.log("Write4U Extension Installed successfully.");
  chrome.contextMenus.create({
    id: "write4u-generate",
    title: "Generate with Write4U (Context Engine)",
    contexts: ["editable", "selection"]
  });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "write4u-generate" && tab.id) {
    chrome.tabs.sendMessage(tab.id, { action: "TRIGGER_WRITE4U" });
  }
});
