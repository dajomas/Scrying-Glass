/* One initial decision per page; panel buttons are independent within each workflow. */
(() => {
    'use strict';
    if (window.scryingInitialPaneVisibilityInstalled) return;
    window.scryingInitialPaneVisibilityInstalled = true;
    // Retire the native parent/child links, not the native one-time battle collapse.
    // Existing onclick handlers consult this map on every click and now toggle only themselves.
    if (typeof paneDependencies !== 'undefined') {
        delete paneDependencies.campaign;
        delete paneDependencies.battleSetup;
    }
    const independent = ['toggleCampaignPane', 'toggleCharacterPane',
        'toggleBattleSetupPane', 'toggleMonsterPane',
        'toggleCharacterDisplayPane', 'toggleMonsterDisplayPane'];
    for (const id of independent) {
        const button = document.getElementById(id);
        if (button) button.hidden = false;
    }
    // The native callers (including tie confirmation) resolve startBattle dynamically.
    // Preserve its request/error contract, adding collapse only after a successful Start.
    if (typeof startBattle === 'function') {
        startBattle = async function(order) {
            const feedback = window.scryingAdminFeedback;
            const ticket = feedback.begin({region: 'global', operation: 'battle.start',
                target: 'battle', label: 'Start or restart battle'});
            try {
                await request('/api/battle/start', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({order}),
                });
            } catch (error) {
                feedback.publish(ticket, {severity: 'error', text: error.message});
                return;
            }
            // A superseded request must not collapse a different encounter's panels.
            if (!feedback.isCurrent(ticket)) return;
            feedback.resolve(ticket);
            setAllHideablePanesHidden(true);
            // load() owns refresh errors. The successful POST must not be retried.
            await load();
        };
    }
    // Lair eligibility and workflow filtering remain owned by their existing controllers/CSS.
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
    // Preserve renderer context, arguments and return, without polling or state mutations.
    const render = window.scryingLairsRender;
    window.scryingLairsRender = function(state) {
        const result = typeof render === 'function' ? render.apply(this, arguments) : undefined;
        initialize(state);
        return result;
    };
    if (typeof latest !== 'undefined') initialize(latest);
})();
