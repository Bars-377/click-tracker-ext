(function () {
    let lastSent = 0;
    const MIN_INTERVAL_MS = 10;

    document.addEventListener('click', function (e) {
        try {
            const now = Date.now();
            if (now - lastSent < MIN_INTERVAL_MS) return;
            lastSent = now;

            const el = e.target;
            const link = el.closest('a')?.href || null;
            const text = (el.innerText || el.textContent || '').trim();

            const data = {
                url: link,
                text: text,
                page_url: window.location.href,
                page_title: document.title || '',
                mechanism: "click",
                timestamp: new Date().toISOString()
            };

            // отправляем сообщение в background.js
            chrome.runtime.sendMessage({
                type: "click",
                payload: data
            });

        } catch (err) {
            console.error("Click tracker exception:", err);
        }
    }, true);
})();
