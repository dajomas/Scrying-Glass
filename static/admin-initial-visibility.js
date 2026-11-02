/* SG-TODO-005: one initial decision per page, no saved preferences or polling. */
(() => {
    'use strict';
    if (window.scryingInitialPaneVisibilityInstalled) return;
    window.scryingInitialPaneVisibilityInstalled = true;
    const campaign = ['toggleCampaignPane', 'toggleCharacterPane'];
    const setup = ['toggleBattleSetupPane', 'toggleMonsterPane', 'toggleLairPane'];
    const touched = new Set();
    let initialized = false, applying = false;
    const text = value => typeof value === 'string' && value.trim().length > 0;
    const reference = value => value !== null && typeof value === 'object' && !Array.isArray(value)
        && text(value.campaign_id) && text(value.name);
    const valid = state => state !== null && typeof state === 'object' &&
        Object.prototype.hasOwnProperty.call(state, 'active_campaign_id') &&
        Object.prototype.hasOwnProperty.call(state, 'active_setup') &&
        (state.active_campaign_id === null || text(state.active_campaign_id)) &&
        (state.active_setup === null || reference(state.active_setup));
    for (const id of [...campaign, ...setup]) {
        document.getElementById(id)?.addEventListener('click', () => {
            if (!applying) touched.add(id);
        }, true);
    }
    function initialize(state) {
        if (initialized || !valid(state)) return;
        initialized = true;
        const ids = [...(text(state.active_campaign_id) ? campaign : []),
            ...(reference(state.active_setup) ? setup : [])];
        applying = true;
        try {
            for (const id of ids) {
                const button = document.getElementById(id);
                // Use existing toggle behavior, not an independent hidden-state model.
                // Hidden-but-enabled lair controls can still record the initial preference.
                if (button && !button.disabled && !touched.has(id) &&
                    button.getAttribute('aria-expanded') === 'true') button.click();
            }
        } finally { applying = false; }
    }
    // Installed after Admin/lair extensions; preserve the existing renderer contract.
    const render = window.scryingLairsRender;
    window.scryingLairsRender = function(state) {
        const result = typeof render === 'function' ? render.apply(this, arguments) : undefined;
        initialize(state);
        return result;
    };
    // Initial load may already have completed while deferred assets were executing.
    if (typeof latest !== 'undefined') initialize(latest);
})();
