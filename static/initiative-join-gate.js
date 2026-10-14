/* UI guidance only; the server independently validates every join request. */
(() => {
    'use strict';
    function refresh() {
        if (typeof latest === 'undefined' || !latest) return;
        for (const [kind, attribute] of [['characters', 'data-ca'], ['monsters', 'data-ma']]) {
            const byId = new Map((latest[kind] || []).map(item => [item.id, item]));
            document.querySelectorAll(`button[${attribute}]`).forEach(button => {
                const item = byId.get(button.getAttribute(attribute));
                if (!item) return;
                const blocked = !item.active && !Number.isInteger(item.initiative);
                button.disabled = blocked;
                if (blocked) {
                    button.title = 'Enter initiative before joining battle.';
                    button.dataset.initiativeBlocked = 'true';
                } else if (button.dataset.initiativeBlocked) {
                    button.removeAttribute('title');
                    delete button.dataset.initiativeBlocked;
                }
            });
        }
    }
    for (const id of ['characters', 'monsters']) {
        const container = document.getElementById(id);
        if (container) new MutationObserver(refresh).observe(container, {childList: true, subtree: true});
    }
    refresh();
})();
