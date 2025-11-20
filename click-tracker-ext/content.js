(function () {
    let lastSent = 0;
    const MIN_INTERVAL_MS = 10;

    // Получение логина по XPath
    function getUserLogin() {
        try {
            const xpath = "/html/body/esia-root/div/esia-login/div/div[1]/form/div[1]/div[2]//input";
            const result = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
            const input = result.singleNodeValue;
            return input ? input.value.trim() : null;
        } catch (err) {
            console.error("Ошибка при получении логина:", err);
            return null;
        }
    }

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
                timestamp: new Date().toISOString(),
                user_login: getUserLogin()   // добавляем логин
            };

            chrome.runtime.sendMessage({
                type: "click",
                payload: data
            });

        } catch (err) {
            console.error("Click tracker exception:", err);
        }
    }, true);
})();
