(function () {
    let lastSent = 0;
    const MIN_INTERVAL_MS = 10;

    // Получение логина по двум XPath
    function getUserLogin() {
        const xpathPrimary = "/html/body/esia-root/div/esia-login/div/div[1]/form/div[1]/div[2]//input";
        const xpathFallback = "/html/body/esia-root/div/esia-login/div/div[1]/form/esia-login-found/div/div[2]/div/b";


        try {
            // Пробуем основной XPath (input)
            let result = document.evaluate(xpathPrimary, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
            let node = result.singleNodeValue;

            if (node && node.value && node.value.trim() !== "") {
                return node.value.trim();
            }

            // Если основной не найден — fallback
            result = document.evaluate(xpathFallback, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
            node = result.singleNodeValue;

            if (node) {
                const text = (node.innerText || node.textContent || "").trim();
                return text !== "" ? text : null;
            }

            return null;
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
                user_login: getUserLogin()
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
