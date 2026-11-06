/* SG-TODO-013: within-roster initiative navigation; native saves remain authoritative. */
(() => {
    'use strict';
    if (window.scryingInitiativeNavigationInstalled) return;
    window.scryingInitiativeNavigationInstalled = true;
    let anchor = null;
    const restored = new WeakMap();
    const changed = new WeakMap();
    const selectors = {characters: 'input[data-ci]', monsters: 'input[data-mi]'};
    const identity = (node, kind) => node.getAttribute(kind === 'characters' ? 'data-ci' : 'data-mi');
    function scope() {
        const state = typeof latest === 'undefined' ? null : latest;
        return JSON.stringify([state?.active_campaign_id ?? null,
            state?.active_setup?.campaign_id ?? null, state?.active_setup?.name ?? null]);
    }
    function fields(region, kind) {
        return [...region.querySelectorAll(selectors[kind])].filter(node =>
            !node.matches(':disabled') && !node.readOnly && node.tabIndex >= 0 &&
            !node.closest('[inert]') && node.getClientRects().length > 0 &&
            getComputedStyle(node).visibility === 'visible');
    }
    document.addEventListener('pointerdown', () => { anchor = null; }, true);
    document.addEventListener('focusin', event => {
        if (anchor && event.target !== anchor.node) anchor = null;
    });
    window.addEventListener('blur', () => { anchor = null; });
    document.addEventListener('change', event => {
        changed.set(event.target, event.target.value);
        restored.delete(event.target);
    }, true);
    document.addEventListener('focusout', event => {
        const node = event.target;
        const draft = restored.get(node);
        if (!draft) return;
        queueMicrotask(() => {
            if (restored.get(node) !== draft) return;
            restored.delete(node);
            if (node.isConnected && draft.scope === scope() && document.activeElement !== node &&
                node.value !== node.defaultValue) {
                node.dispatchEvent(new Event('change', {bubbles: true}));
            }
        });
    });
    for (const kind of Object.keys(selectors)) {
        const region = document.getElementById(kind);
        if (!region) continue;
        region.addEventListener('keydown', event => {
            if (event.key !== 'Tab' || event.altKey || event.ctrlKey || event.metaKey ||
                event.isComposing || event.defaultPrevented) return;
            const list = fields(region, kind);
            const index = list.indexOf(event.target);
            if (index < 0) return;
            const next = list[index + (event.shiftKey ? -1 : 1)];
            if (!next) { anchor = null; return; }
            event.preventDefault();
            anchor = {region, kind, id: identity(next, kind), scope: scope(), node: next};
            next.focus();
        });
        new MutationObserver(() => {
            if (!anchor || anchor.region !== region) return;
            if (anchor.scope !== scope()) { anchor = null; return; }
            if (anchor.node.isConnected) return;
            if (document.activeElement !== document.body && document.activeElement !== region) {
                anchor = null;
                return;
            }
            const next = fields(region, kind).find(node => identity(node, kind) === anchor.id);
            if (!next) { anchor = null; return; }
            // Retain a draft typed in the destination while the preceding save refreshed rows.
            if (anchor.node.value !== anchor.node.defaultValue) {
                next.value = anchor.node.value;
                if (changed.get(anchor.node) === anchor.node.value) changed.set(next, next.value);
                else restored.set(next, {scope: anchor.scope});
            }
            anchor.node = next;
            next.focus();
        }).observe(region, {childList: true});
    }
})();
