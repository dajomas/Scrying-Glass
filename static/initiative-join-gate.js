/* UI feedback only; the server independently validates every join request. */
(() => {
    'use strict';
    function showRejection(text) {
        const area = document.getElementById('message');
        if (area) area.textContent = text;
    }
    function itemFor(button) {
        if (typeof latest === 'undefined' || !latest) return null;
        const character = button.hasAttribute('data-ca');
        const kind = character ? 'characters' : 'monsters';
        const id = button.getAttribute(character ? 'data-ca' : 'data-ma');
        return (latest[kind] || []).find(item => item.id === id);
    }
    function refresh() {
        document.querySelectorAll('button[data-ca], button[data-ma]').forEach(button => {
            const item = itemFor(button);
            if (!item) return;
            const blocked = !item.active && !Number.isInteger(item.initiative);
            // Remain clickable so rejected attempts can explain the requirement.
            button.disabled = false;
            if (blocked) {
                button.title = 'Enter initiative before joining battle.';
                button.setAttribute('aria-disabled', 'true');
                button.dataset.initiativeBlocked = 'true';
            } else if (button.dataset.initiativeBlocked) {
                button.removeAttribute('title');
                button.removeAttribute('aria-disabled');
                delete button.dataset.initiativeBlocked;
            }
        });
    }
    document.addEventListener('click', event => {
        const button = event.target.closest?.('button[data-ca], button[data-ma]');
        if (!button) return;
        const item = itemFor(button);
        if (!item || item.active || Number.isInteger(item.initiative)) return;
        event.preventDefault();
        event.stopImmediatePropagation();
        showRejection('Enter initiative before joining battle: ' + (item.name || item.id));
    }, true);

    const originalFetch = window.fetch.bind(window);
    window.fetch = async function (input, options = {}) {
        let joining = false;
        try {
            const url = new URL(typeof input === 'string' ? input : input.url, window.location.href);
            const body = typeof options.body === 'string' ? JSON.parse(options.body) : null;
            joining = url.origin === window.location.origin &&
                /^\/api\/(characters|monsters)(\/[^/]+)?$/.test(url.pathname) &&
                (options.method || 'GET').toUpperCase() !== 'GET' &&
                (body?.active === true || body?.action === 'join-battle');
        } catch { /* Non-JSON and unrelated requests keep their original behavior. */ }
        let response;
        try {
            response = await originalFetch(input, options);
        } catch (error) {
            if (joining) showRejection('Unable to join battle: ' + error.message);
            throw error;
        }
        if (joining && !response.ok) {
            let detail;
            try { detail = (await response.clone().json()).detail; } catch { /* Use HTTP fallback. */ }
            showRejection(typeof detail === 'string' && detail.trim()
                ? detail : `Join Battle rejected (HTTP ${response.status}).`);
        }
        return response;
    };
    for (const id of ['characters', 'monsters']) {
        const container = document.getElementById(id);
        if (container) new MutationObserver(refresh).observe(container, {childList: true, subtree: true});
    }
    refresh();
})();
