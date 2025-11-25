(function () {
    const MIN_INTERVAL_MS = 10;
    let lastSent = 0;

    function getAuthButton() {
        return document.querySelector('lib-header-auth button');
    }

    function getUserNameElement() {
        return document.querySelector('lib-header-user-name p');
    }

    function clickAuthButton() {
        const btn = getAuthButton();
        if (btn) {
            btn.click();
            return true;
        }
        return false;
    }

    function clickUserNameElement() {
        const el = getUserNameElement();
        if (el) {
            el.click();
            return true;
        }
        return false;
    }

    function getUserName() {
        const el = getUserNameElement();
        if (!el) return null;
        const text = (el.innerText || el.textContent || "").trim();
        return text !== "" ? text : null;
    }

    // Автоклик по кнопке авторизации после загрузки DOM
    document.addEventListener("DOMContentLoaded", () => {
        const tryClickAuth = setInterval(() => {
            if (clickAuthButton()) {
                clearInterval(tryClickAuth);
                waitForUserName();
            }
        }, 300);
    });

    // Ждём появления имени пользователя и кликаем по нему
    function waitForUserName() {
        const interval = setInterval(() => {
            if (clickUserNameElement()) {
                const name = getUserName();
                if (name) {
                    chrome.runtime.sendMessage({
                        type: "user_login",
                        payload: {
                            user_name: name,
                            timestamp: new Date().toISOString(),
                            page_url: window.location.href,
                            page_title: document.title || ""
                        }
                    });
                    clearInterval(interval);
                }
            }
        }, 200);
    }

    // Логика трекера кликов с обязательным getUserNameElement после getAuthButton
    document.addEventListener('click', function (e) {
        try {
            const now = Date.now();
            if (now - lastSent < MIN_INTERVAL_MS) return;
            lastSent = now;

            // Сначала пытаемся кликнуть по кнопке авторизации
            clickAuthButton();

            // После этого получаем имя пользователя
            const userNameEl = getUserNameElement();
            const userName = userNameEl ? (userNameEl.innerText || userNameEl.textContent || '').trim() : null;

            const el = e.target;
            const link = el.closest('a')?.href || null;
            let text = (el.innerText || el.textContent || '').trim();

            // Если элемент не имеет текста, но это кнопка, взять value или aria-label
            if (!text && el.tagName.toLowerCase() === 'button') {
                text = el.value || el.getAttribute('aria-label') || 'button';
            }

            chrome.runtime.sendMessage({
                type: "click",
                payload: {
                    url: link,
                    text: text,
                    page_url: window.location.href,
                    page_title: document.title || '',
                    mechanism: "click",
                    timestamp: new Date().toISOString(),
                    user_login: userName
                }
            });

        } catch (err) {
            console.error("Click tracker exception:", err);
        }
    }, true);

})();
