(function () {
    let lastSent = 0;
    const MIN_INTERVAL_MS = 10; // Можно сделать меньше, чтобы не терять быстрые клики

    document.addEventListener('click', function (e) {
        try {
            const now = Date.now();
            if (now - lastSent < MIN_INTERVAL_MS) return;
            lastSent = now;

            // Получаем текст элемента и ссылку, если есть
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

            fetch("http://127.0.0.1:8000/click", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data),
            }).then(resp => {
                if (!resp.ok) {
                    return resp.text().then(t => console.error("Click tracking failed:", resp.status, t));
                }
            }).catch(err => console.error("Click tracking error:", err));

        } catch (err) {
            console.error("Click tracker exception:", err);
        }
    }, true);
})();
