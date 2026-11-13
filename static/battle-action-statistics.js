/* SG-TODO-015: read-only selector descriptions; never replace controls or drafts. */
(() => {
    'use strict';
    const modal = document.getElementById('battleActionModal');
    const rows = document.getElementById('battleActionRows');
    if (!modal || !rows || window.scryingActionStatsInstalled) return;
    window.scryingActionStatsInstalled = true;
    const selector = 'select[data-action-target], select[data-action-source]';
    const summaries = new WeakMap();
    let counter = 0;
    let snapshot = typeof latest === 'undefined' ? null : latest;
    const scope = state => JSON.stringify([
        state?.active_campaign_id ?? state?.active_setup?.campaign_id ?? null,
        typeof state?.active_setup === 'string' ? state.active_setup : state?.active_setup?.name ?? null,
    ]);
    let sessionScope = modal.hidden ? null : scope(snapshot);
    const fields = [['ac', 'AC'], ['hp', 'HP'], ['max_hp', 'HP MAX']];
    function summaryFor(select) {
        let node = summaries.get(select);
        if (!node) {
            node = document.createElement('p');
            node.className = 'sg-action-stats';
            do { node.id = 'sg-action-stats-' + (++counter); }
            while (document.getElementById(node.id));
            node.hidden = true;
            node.setAttribute('role', 'status');
            node.setAttribute('aria-live', 'polite');
            node.setAttribute('aria-atomic', 'true');
            summaries.set(select, node);
            // Keep the existing selector name from absorbing the appended statistics.
            if (!select.hasAttribute('aria-label') && !select.hasAttribute('aria-labelledby')) {
                select.setAttribute('aria-label', select.hasAttribute('data-action-source') ? 'Reaction source' : 'Target');
            }
        }
        if (select.nextElementSibling !== node) select.after(node);
        const described = (select.getAttribute('aria-describedby') || '').split(/\s+/).filter(Boolean);
        if (!described.includes(node.id)) {
            select.setAttribute('aria-describedby', [...described, node.id].join(' '));
        }
        return node;
    }
    const options = {childList: true, subtree: true, attributes: true, attributeFilter: ['selected']};
    const observer = new MutationObserver(render);
    function render() {
        // Do not recursively observe our own text/description construction.
        observer.disconnect();
        try {
            if (modal.hidden) sessionScope = null;
            else if (sessionScope === null) sessionScope = scope(snapshot);
            const sameScope = !modal.hidden && sessionScope === scope(snapshot);
            const combatants = [...(Array.isArray(snapshot?.monsters) ? snapshot.monsters : []),
                ...(Array.isArray(snapshot?.characters) ? snapshot.characters : [])];
            for (const select of rows.querySelectorAll(selector)) {
                const node = summaryFor(select);
                const item = sameScope && select.value
                    ? combatants.find(entry => entry && String(entry.id) === select.value) : null;
                const text = item ? fields.filter(([key]) => typeof item[key] === 'number' && Number.isFinite(item[key]))
                    .map(([key, label]) => label + ' ' + item[key]).join(' · ') : '';
                if (node.textContent !== text) node.textContent = text;
                node.hidden = !text;
            }
        } finally { observer.observe(rows, options); }
    }
    rows.addEventListener('change', event => {
        if (event.target.matches?.(selector)) render();
    });
    new MutationObserver(() => {
        sessionScope = modal.hidden ? null : scope(snapshot);
        render();
    }).observe(modal, {attributes: true, attributeFilter: ['hidden']});
    const previous = window.scryingLairsRender;
    window.scryingLairsRender = function(state) {
        const result = typeof previous === 'function' ? previous.apply(this, arguments) : undefined;
        snapshot = state;
        render();
        return result;
    };
    render();
    document.body.dataset.actionStats = 'ready';
})();
