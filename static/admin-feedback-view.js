/* A single polite region per existing notice; stable nodes for unrelated results. */
(() => {
    'use strict';
    function mountView({controller, root, region, focusFallback}) {
        if (!controller || !root || typeof region !== 'string' || !region.trim() ||
            typeof focusFallback !== 'function') throw new TypeError('Controller, root, region and focus fallback are required');
        if (root.dataset.sgFeedbackMounted) throw new Error('Feedback region is already mounted');
        const document = root.ownerDocument, nodes = new Map();
        const prior = new Map(['role', 'aria-live', 'aria-relevant', 'aria-atomic', 'hidden', 'class']
            .map(name => [name, root.getAttribute(name)]));
        const titles = {success: 'Success', error: 'Error', warning: 'Warning', info: 'Information'};
        root.dataset.sgFeedbackMounted = 'true';
        root.classList.add('sg-feedback-region');
        root.setAttribute('role', 'status');
        root.setAttribute('aria-live', 'polite');
        root.setAttribute('aria-relevant', 'additions text');
        root.setAttribute('aria-atomic', 'false');
        root.replaceChildren();
        let lastOrder = [];
        function restoreFocus(removedIndex, nextOrder) {
            const next = nextOrder[Math.min(removedIndex, nextOrder.length - 1)];
            const target = next ? nodes.get(next)?.button : focusFallback();
            target?.focus?.({preventScroll: true});
        }
        function render(snapshot) {
            const items = snapshot.filter(item => item.region === region);
            const nextOrder = items.map(item => item.id), wanted = new Set(nextOrder);
            let focusedRemoval = -1;
            for (const [id, view] of nodes) {
                if (wanted.has(id)) continue;
                if (view.row.contains(document.activeElement)) focusedRemoval = lastOrder.indexOf(id);
                view.row.remove(); nodes.delete(id);
            }
            for (const item of items) {
                if (nodes.has(item.id)) continue;
                const row = document.createElement('span');
                row.className = 'sg-feedback-record'; row.dataset.severity = item.severity;
                row.dataset.feedbackId = item.id;
                const text = document.createElement('span');
                text.className = 'sg-feedback-text'; text.id = item.id + '-text';
                text.textContent = titles[item.severity] + ': ' + item.text;
                const button = document.createElement('button');
                button.type = 'button'; button.className = 'sg-feedback-dismiss';
                button.textContent = 'Dismiss';
                button.setAttribute('aria-label', 'Dismiss ' + item.label + ' ' + item.severity + ' message');
                button.addEventListener('click', () => controller.dismiss(item.id));
                row.append(text, button); root.append(row);
                nodes.set(item.id, {row, button});
            }
            root.hidden = items.length === 0;
            if (focusedRemoval >= 0) restoreFocus(focusedRemoval, nextOrder);
            lastOrder = nextOrder;
        }
        const unsubscribe = controller.subscribe(render);
        return Object.freeze({destroy() {
            unsubscribe();
            const focused = [...nodes.values()].some(view => view.row.contains(document.activeElement));
            root.replaceChildren(); nodes.clear();
            delete root.dataset.sgFeedbackMounted;
            for (const [name, value] of prior) {
                if (value === null) root.removeAttribute(name); else root.setAttribute(name, value);
            }
            if (focused) focusFallback()?.focus?.({preventScroll: true});
        }});
    }
    const api = Object.freeze({mountView});
    if (typeof module === 'object' && module.exports) module.exports = api;
    else globalThis.ScryingFeedbackView = api;
})();
