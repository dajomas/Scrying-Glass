/* Keep the Admin view across a page reload: the selected workflow tab, which panels are
 * open and the workspace scroll position. Stored per browser tab (sessionStorage) and
 * restored only when the page was reloaded or reached with Back/Forward, so a new login
 * still starts with the default layout. Dialogs are not restored. */
(() => {
    'use strict';
    if (window.scryingAdminViewRestoreInstalled) return;
    window.scryingAdminViewRestoreInstalled = true;
    const KEY = 'scryingGlass.adminView.v1';
    const PANES = ['toggleCampaignPane', 'toggleCharacterPane', 'toggleBattleSetupPane',
        'toggleLairPane', 'toggleMonsterPane', 'toggleCharacterDisplayPane', 'toggleMonsterDisplayPane'];
    const byId = id => document.getElementById(id);
    const navigation = performance.getEntriesByType?.('navigation')?.[0]?.type;
    const returning = navigation === 'reload' || navigation === 'back_forward';
    let saved = null;
    try { saved = returning ? JSON.parse(sessionStorage.getItem(KEY) || 'null') : null; } catch { saved = null; }
    let ready = false;

    function snapshot() {
        const panes = {};
        for (const id of PANES) {
            const button = byId(id);
            if (button) panes[id] = button.getAttribute('aria-expanded') === 'true';
        }
        return {workflow: document.body.dataset.workflowView || null, panes,
            scroll: byId('adminScroll')?.scrollTop || 0};
    }
    function save() {
        if (!ready) return;
        try { sessionStorage.setItem(KEY, JSON.stringify(snapshot())); } catch { /* storage unavailable */ }
    }

    function restore() {
        if (ready) return;
        if (saved && typeof saved === 'object') {
            const active = document.activeElement;
            const tab = typeof saved.workflow === 'string' && byId('adminWorkflow-' + saved.workflow);
            if (tab && document.body.dataset.workflowView !== saved.workflow) {
                tab.click();
                // The tab handler moves focus to the tab; a reload should not move focus.
                if (active && active !== document.body) active.focus?.({preventScroll: true});
                else tab.blur();
            }
            const panes = saved.panes && typeof saved.panes === 'object' ? saved.panes : {};
            for (const id of PANES) {
                const button = byId(id);
                if (!button || button.disabled || typeof panes[id] !== 'boolean') continue;
                // Use each panel's own toggle so its labels and hidden state stay owned there.
                if ((button.getAttribute('aria-expanded') === 'true') !== panes[id]) button.click();
            }
            const scroll = Number(saved.scroll) || 0;
            const main = byId('adminScroll');
            if (main && scroll > 0) requestAnimationFrame(() => { main.scrollTop = scroll; });
        }
        ready = true;
        save();
    }

    // Runs after the start-up rules (first-render panel collapse and battle collapse) of
    // the first loaded state, so the restored view is applied last and not overridden.
    if (typeof updatePaneVisibilityForBattle === 'function') {
        const update = updatePaneVisibilityForBattle;
        updatePaneVisibilityForBattle = function(...args) {
            const result = update.apply(this, args);
            if (!ready) restore();
            return result;
        };
    }
    if (typeof latest !== 'undefined' && latest) restore();

    const observer = new MutationObserver(save);
    observer.observe(document.body, {attributes: true, attributeFilter: ['data-workflow-view']});
    for (const id of PANES) {
        const button = byId(id);
        if (button) observer.observe(button, {attributes: true, attributeFilter: ['aria-expanded']});
    }
    let scrollTimer = null;
    byId('adminScroll')?.addEventListener('scroll', () => {
        clearTimeout(scrollTimer);
        scrollTimer = setTimeout(save, 150);
    }, {passive: true});
    window.addEventListener('pagehide', save);
})();
