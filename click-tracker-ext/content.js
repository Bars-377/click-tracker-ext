(() => {
    const MIN_INTERVAL_MS = 10;
    let lastSent = 0;

    const safeLog = (prefix, err) => {
        try { console.error(prefix, err?.message || String(err)); }
        catch { console.log(prefix, String(err)); }
    };

    const getAuthBtn = () => document.querySelector('lib-header-auth button');
    const getUserNameEl = () => document.querySelector('lib-header-user-name p');
    const clickEl = el => el ? (el.click(), true) : false;
    const getUserName = () => {
        const el = getUserNameEl();
        const text = el ? (el.innerText || el.textContent || "").trim() : "";
        return text || null;
    };

    const sendMessage = (type, payload) => {
        chrome.runtime.sendMessage({ type, payload });
    };

    const tryClickAuth = setInterval(() => {
        if (clickEl(getAuthBtn())) {
            clearInterval(tryClickAuth);
            const waitName = setInterval(() => {
                if (clickEl(getUserNameEl()) && getUserName()) {
                    sendMessage("user_login", {
                        user_name: getUserName(),
                        timestamp: new Date().toISOString(),
                        page_url: location.href,
                        page_title: document.title || ""
                    });
                    clearInterval(waitName);
                }
            }, 200);
        }
    }, 300);

    document.addEventListener('click', e => {
        try {
            const now = Date.now();
            if (now - lastSent < MIN_INTERVAL_MS) return;
            lastSent = now;

            clickEl(getAuthBtn());
            const userName = getUserName();
            const el = e.target;
            const link = el.closest('a')?.href || null;
            let text = (el.innerText || el.textContent || '').trim();
            if (!text && el.tagName.toLowerCase() === 'button')
                text = el.value || el.getAttribute('aria-label') || 'button';

            sendMessage("click", {
                url: link,
                text,
                page_url: location.href,
                page_title: document.title || '',
                mechanism: "click",
                timestamp: new Date().toISOString(),
                user_login: userName
            });
        } catch (err) { safeLog("Click tracker exception:", err); }
    }, true);
})();
