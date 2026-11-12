/* SG-TODO-009.7 Admin wiring. Caller migration remains explicit; Deliverable 2 field association. */
(() => {
    'use strict';
    if (window.scryingAdminFeedback) return;
    const controller = ScryingFeedback.createController();
    const scopes = new Map(), views = new Map();
    let stateSequence = 0, lookupSequence = 0, encounterEpoch = 0;
    let stateRequestEpoch = 0, acceptedStateSequence = 0, acceptedStateEpoch = 0;
    const regions = {
        global: ['message', ['nextBattle', 'startBattle']],
        campaign: ['campaignNotification', ['toggleCampaignPane', 'switchCampaign']],
        characters: ['characterAddNotification', ['toggleCharacterPane']],
        battleSetup: ['battleSetupNotification', ['toggleBattleSetupPane', 'saveSetup']],
        monsters: ['monsterAddNotification', ['toggleMonsterPane']],
        // Stage 3 local regions: encounter tools, lair pane, lair-action dialog, viewer access.
        tools: ['featureFeedback', ['featureRefresh']],
        lair: ['lairNotice', ['saveLair']],
        lairAction: ['lairActionNotice', ['applyLairAction', 'cancelLairAction']],
        campaignViewer: ['campaignViewerFeedback', ['saveCampaignViewers', 'campaignViewerAccessTitle']],
    };
    function setScope(lane, scope) {
        const changed = controller.setScope(lane, scope);
        scopes.set(lane, scope);
        if (changed && lane === 'encounter') encounterEpoch++;
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
    // Stage 4: the untyped pane compatibility path is retired. Every producer,
    // global or pane, supplies an explicit ticket for this region and a severity.
    function deliver(region, text, options) {
        if (!options?.ticket) throw new Error('Feedback requires an explicit ticket and severity: ' + region);
        if (options.ticket.region !== region) throw new Error('Feedback destination mismatch');
        return controller.publish(options.ticket, {severity: options.severity, text});
    }
    function stateRequest() {
        stateRequestEpoch = encounterEpoch;
        return ++stateSequence;
    }
    function observeState(snapshot, sequence) {
        if (sequence !== stateSequence || stateRequestEpoch !== encounterEpoch || !snapshot || typeof snapshot !== 'object' ||
            !Object.hasOwn(snapshot, 'active_campaign_id') || !Object.hasOwn(snapshot, 'active_setup')) return false;
        const campaign = snapshot.active_campaign_id;
        const setup = snapshot.active_setup;
        if (campaign !== null && (typeof campaign !== 'string' || !campaign.trim())) return false;
        if (setup !== null && (typeof setup !== 'object' ||
            typeof setup.name !== 'string' || typeof setup.campaign_id !== 'string')) return false;
        const scope = JSON.stringify([campaign, setup?.campaign_id ?? null, setup?.name ?? null]);
        if (setScope('encounter', scope)) invalidateLookup();
        acceptedStateSequence = sequence;
        acceptedStateEpoch = encounterEpoch;
        return true;
    }
    async function loadState(fetchState, render, rethrowErrors = false, current = () => true) {
        if (!current()) return;
        const spec = {region: 'global', operation: 'state.load', target: 'state', label: 'Load encounter state'};
        let ticket = begin(spec), sequence;
        try {
            // request() allocates its state identity synchronously, before its first await.
            const pending = fetchState();
            sequence = stateSequence;
            const state = await pending;
            if (!current()) return;
            if (sequence !== stateSequence) return;
            if (acceptedStateSequence !== sequence) {
                if (!controller.isCurrent(ticket)) return;
                throw new Error('State response could not be applied. Reload to retry.');
            }
            if (acceptedStateEpoch !== encounterEpoch) return;
            // An accepted campaign/setup transition invalidates the original encounter ticket.
            if (!controller.isCurrent(ticket)) ticket = begin(spec);
            render(state);
            if (current()) controller.resolve(ticket);
        } catch (error) {
            if (!current()) return;
            if ((sequence === undefined || sequence === stateSequence) && controller.isCurrent(ticket)) {
                controller.publish(ticket, {severity: 'error', text: error.message});
            }
            if (rethrowErrors === true) throw error;
        }
    }
    // Deliverable 2: near-field association. A ticket naming an explicit `field` selector marks the
    // matching control aria-invalid while its error/warning record exists and adds a non-live hint
    // after it (the record itself stays the single live announcement). Removal, dismissal, matching
    // resolution or a scope change restores the control; re-rendered controls are re-associated.
    const hints = new Map(), priors = new WeakMap();
    let fieldRecords = [], observer = null, queued = false;
    function token(node, id, add) {
        const list = (node.getAttribute('aria-describedby') || '').split(/\s+/).filter(Boolean)
            .filter(item => item !== id);
        if (add) list.push(id);
        if (list.length) node.setAttribute('aria-describedby', list.join(' '));
        else node.removeAttribute('aria-describedby');
    }
    function release(view) {
        view.hint.remove();
        const node = view.node, prior = priors.get(node);
        token(node, view.hint.id, false);
        if (prior && --prior.count === 0) {
            priors.delete(node);
            if (prior.invalid === null) node.removeAttribute('aria-invalid');
            else node.setAttribute('aria-invalid', prior.invalid);
        }
    }
    function associate() {
        queued = false;
        const wanted = new Map();
        for (const record of fieldRecords) {
            let node = null;
            try { node = document.querySelector(record.field); } catch { node = null; }
            if (node) wanted.set(record.id, {record, node});
        }
        for (const [id, view] of hints) {
            const next = wanted.get(id);
            if (next && next.node === view.node && view.hint.isConnected) continue;
            release(view); hints.delete(id);
        }
        for (const [id, {record, node}] of wanted) {
            if (hints.has(id)) continue;
            const hint = document.createElement('span');
            hint.className = 'sg-field-error'; hint.id = id + '-field';
            hint.dataset.severity = record.severity; hint.textContent = record.text;
            const prior = priors.get(node) || {invalid: node.getAttribute('aria-invalid'), count: 0};
            prior.count++; priors.set(node, prior);
            node.setAttribute('aria-invalid', 'true');
            token(node, hint.id, true);
            node.after(hint);
            hints.set(id, {node, hint});
        }
        if (fieldRecords.length && !observer && typeof MutationObserver === 'function') {
            observer = new MutationObserver(() => {
                if (!queued) { queued = true; queueMicrotask(associate); }
            });
            observer.observe(document.body, {childList: true, subtree: true});
        } else if (!fieldRecords.length && observer) { observer.disconnect(); observer = null; }
    }
    controller.subscribe(snapshot => {
        fieldRecords = snapshot.filter(record => record.field &&
            (record.severity === 'error' || record.severity === 'warning'));
        if (fieldRecords.length || hints.size) associate();
    });
    // Explicit selector for a control: the first constraint-invalid control of a form, or the node.
    const escape = value => globalThis.CSS?.escape ? CSS.escape(value)
        : String(value).replace(/[^a-zA-Z0-9_-]/g, character => '\\' + character);
    function field(node) {
        if (node?.tagName === 'FORM') node = node.querySelector(':invalid') || null;
        if (!node) return null;
        if (node.id) return '#' + escape(node.id);
        const form = node.form || node.closest?.('form');
        if (form?.id && node.name) return '#' + escape(form.id) + ' [name="' + escape(node.name) + '"]';
        return null;
    }
    const api = Object.freeze({loadState, field,
        // Explicit selector for a roster initiative input (characters: data-ci, monsters: data-mi).
        initiativeField: (kind, id) => `input[data-${kind === 'characters' ? 'ci' : 'mi'}="${escape(String(id))}"]`, begin, deliver, mount, setScope, stateRequest, observeState, invalidateLookup,
        encounterContext: () => Object.freeze({scope: scopes.get('encounter'), epoch: encounterEpoch}),
        beginLookup(target) {
            invalidateLookup();
            return begin({lane: 'lookup', region: 'monsters', operation: 'monster.lookup', target, label: 'Monster lookup'});
        },
        publish: controller.publish, resolve: controller.resolve, isCurrent: controller.isCurrent,
        snapshot: controller.snapshot,
    });
    window.scryingAdminFeedback = api;
    for (const [region, [id, fallbackIds]] of Object.entries(regions)) mount(region, id, fallbackIds);
})();
