const API_URL = "http://127.0.0.1:8111/click";

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    if (msg.type === "click") {
        fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(msg.payload)
        }).catch(err => console.error("Error sending click:", err));
    }
});
