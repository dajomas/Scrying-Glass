/* SG-TODO-009.7 Admin wiring. Caller migration remains explicit. */
(() => {
    'use strict';
    if (window.scryingAdminFeedback) return;
    const controller = ScryingFeedback.createController();
    const scopes = new Map(), views = new Map(), legacyRegions = new Set();
    let stateSequence = 0, lookupSequence = 0;
    const regions = {
        global: ['message', ['nextBattle', 'startBattle']],
        campaign: ['campaignNotification', ['toggleCampaignPane', 'switchCampaign']],
        characters: ['characterAddNotification', ['toggleCharacterPane']],
        battleSetup: ['battleSetupNotification', ['toggleBattleSetupPane', 'saveSetup']],
        monsters: ['monsterAddNotification', ['toggleMonsterPane']],
    };
    function setScope(lane, scope) {
        const changed = controller.setScope(lane, scope);
        scopes.set(lane, scope);
        return changed;
    }
    setScope('page', 'page');
    setScope('encounter', JSON.stringify(['uninitialized']));
    function invalidateLookup() {
        setScope('lookup', JSON.stringify([scopes.get('encounter'), ++lookupSequence]));
    }
    invalidateLookup();
    const available = node => node && !node.disabled && !node.closest('[inert]') && node.getClientRects().length;
    function fallback(region) {
        const nested = [...document.querySelectorAll('.modal:not([hidden]),dialog[open]')]
            .filter(available).at(-1);
        if (nested) {
            const node = [...nested.querySelectorAll('button,input,select,textarea,a[href],[tabindex]')]
                .find(n => available(n) && n.tabIndex >= 0);
            if (node) return node;
        }
        const candidates = [...(regions[region]?.[1] || []), 'adminScroll', 'startBattle'];
        return candidates.map(id => document.getElementById(id)).find(available) || null;
    }
    function mount(region, id, fallbackIds = []) {
        if (views.has(region)) return false;
        const root = document.getElementById(id);
        if (!root) return false;
        regions[region] = [id, fallbackIds];
        views.set(region, ScryingFeedbackView.mountView({controller, root, region,
            focusFallback: () => fallback(region)}));
        return true;
    }
    function begin(spec) {
        if (!regions[spec.region]) throw new Error('Unknown feedback region: ' + spec.region);
        const lane = spec.lane || 'encounter';
        if (!scopes.has(lane)) throw new Error('Activate feedback lane first: ' + lane);
        return controller.begin({...spec, lane, scope: spec.scope || scopes.get(lane),
            placement: spec.region === 'global' ? 'global' : 'pane'});
    }
    function deliver(region, text, options) {
        if (options !== undefined) {
            if (!options.ticket || options.ticket.region !== region) throw new Error('Feedback destination mismatch');
            return controller.publish(options.ticket, {severity: options.severity, text});
        }
        // Temporary, observable compatibility route. No severity inference or expiry.
        // Remove its use by migrating the remaining producers before D1 approval.
        legacyRegions.add(region);
        const ticket = begin({region, operation: 'legacy.' + region, target: region,
            label: 'Unmigrated feedback'});
        const value = String(text ?? '');
        return value.trim() ? controller.publish(ticket, {severity: 'info', text: value}) : controller.resolve(ticket);
    }
    function stateRequest() { return ++stateSequence; }
    function observeState(snapshot, sequence) {
        if (sequence !== stateSequence || !snapshot || typeof snapshot !== 'object' ||
            !Object.hasOwn(snapshot, 'active_campaign_id') || !Object.hasOwn(snapshot, 'active_setup')) return false;
        const campaign = snapshot.active_campaign_id;
        const setup = snapshot.active_setup;
        if (campaign !== null && (typeof campaign !== 'string' || !campaign.trim())) return false;
        if (setup !== null && (typeof setup !== 'object' ||
            typeof setup.name !== 'string' || typeof setup.campaign_id !== 'string')) return false;
        const scope = JSON.stringify([campaign, setup?.campaign_id ?? null, setup?.name ?? null]);
        if (setScope('encounter', scope)) invalidateLookup();
        return true;
    }
    const api = Object.freeze({begin, deliver, mount, setScope, stateRequest, observeState, invalidateLookup,
        beginLookup(target) {
            invalidateLookup();
            return begin({lane: 'lookup', region: 'monsters', operation: 'monster.lookup', target, label: 'Monster lookup'});
        },
        publish: controller.publish, resolve: controller.resolve, isCurrent: controller.isCurrent,
        snapshot: controller.snapshot, legacyRegions: () => [...legacyRegions],
    });
    window.scryingAdminFeedback = api;
    for (const [region, [id, fallbackIds]] of Object.entries(regions)) mount(region, id, fallbackIds);
})();
