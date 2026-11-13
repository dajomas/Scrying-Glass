/* UI feedback only; the server independently validates every join request. */
(() => {
    'use strict';
    if (window.scryingJoinReportingInstalled) return;
    window.scryingJoinReportingInstalled = true;
    const feedback = window.scryingAdminFeedback;
    const owner = Symbol('Join reporting owner');
    // Deliverable 2: a single-combatant Join error is associated with that combatant's initiative input.
    const joinTicket = (kind, id) => feedback.begin({region: 'global', operation: 'roster.join',
        target: JSON.stringify([kind, id]), label: 'Join battle',
        ...(typeof id === 'string' ? {field: feedback.initiativeField?.(kind, id)} : {})});
    function showRejection(text, ticket) {
        feedback.publish(ticket, {severity: 'error', text});
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
        showRejection('Enter initiative before joining battle: ' + (item.name || item.id),
            joinTicket(button.hasAttribute('data-ca') ? 'characters' : 'monsters', item.id));
    }, true);

    const originalFetch = window.fetch.bind(window);
    window.fetch = async function (input, options = {}) {
        let joining = false, ticket = null;
        try {
            const url = new URL(typeof input === 'string' ? input : input.url, window.location.href);
            const body = typeof options.body === 'string' ? JSON.parse(options.body) : null;
            joining = url.origin === window.location.origin &&
                /^\/api\/(characters|monsters)(\/[^/]+)?$/.test(url.pathname) &&
                (options.method || 'GET').toUpperCase() !== 'GET' &&
                (body?.active === true || body?.action === 'join-battle');
            if (joining && !options[owner]) ticket = joinTicket(url.pathname.split('/')[2],
                url.pathname.split('/')[3] ? decodeURIComponent(url.pathname.split('/')[3])
                    : [...(body.ids || [])].map(String).sort());
        } catch { /* Non-JSON and unrelated requests keep their original behavior. */ }
        let response;
        try {
            response = await originalFetch(input, options);
        } catch (error) {
            if (joining && !options[owner]) showRejection('Unable to join battle: ' + error.message, ticket);
            throw error;
        }
        if (joining && !options[owner] && !response.ok) {
            let detail;
            try { detail = (await response.clone().json()).detail; } catch { /* Use HTTP fallback. */ }
            showRejection(typeof detail === 'string' && detail.trim()
                ? detail : `Join Battle rejected (HTTP ${response.status}).`, ticket);
        }
        if (joining && !options[owner] && response.ok) feedback.resolve(ticket);
        return response;
    };

    async function ownedJoin(kind, target, send) {
        const ticket = joinTicket(kind, target);
        let result;
        try {
            result = await send(ticket);
        } catch (error) {
            showRejection(error.message, ticket);
            return null;
        }
        if (!feedback.isCurrent(ticket)) return null;
        feedback.resolve(ticket);
        return {result};
    }
    function installCoreReporting() {
        // This deferred asset precedes admin.js; bind after all deferred scripts.
        if (typeof patch !== 'function' || typeof runBulkAction !== 'function') return;
        const corePatch = patch, coreBulkAction = runBulkAction;
        patch = async function (kind, id, data) {
            if (!['characters', 'monsters'].includes(kind) || data.active !== true) {
                return corePatch(kind, id, data);
            }
            const outcome = await ownedJoin(kind, id, ticket => request(
                `/api/${kind}/${encodeURIComponent(id)}`, {
                    method: 'PATCH', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data), [owner]: ticket,
                }));
            if (outcome) await load();
        };
        const bulkJoinPending = new Map();
        runBulkAction = async function (kind, action) {
            if (!['characters', 'monsters'].includes(kind) || action !== 'join-battle') {
                return coreBulkAction(kind, action);
            }
            const ids = selectedIds(kind);
            if (!ids.length) return coreBulkAction(kind, action);
            const canonical = [...ids].map(String).sort();
            const target = JSON.stringify([kind, canonical]);
            const previous = bulkJoinPending.get(target);
            if (previous && (feedback.isCurrent(previous.ticket) || feedback.isCurrent(previous.refresh))) return;
            feedback.resolve(feedback.begin({region: kind, operation: 'roster.bulk.join-battle.selection',
                target: kind, label: 'Select combatants'}));
            const spec = {region: kind, operation: 'roster.bulk.join-battle', target, label: 'Join selected combatants'};
            const ticket = feedback.begin(spec);
            const refresh = feedback.begin({...spec, operation: spec.operation + '.refresh'});
            const pending = {ticket, refresh};
            bulkJoinPending.set(target, pending);
            try {
                // The existing owner remains the sole Join rejection reporter.
                const outcome = await ownedJoin(kind, canonical, join => request(
                    `/api/${kind}/bulk`, {
                        method: 'POST', headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({action, ids}), [owner]: join,
                    }));
                if (!outcome || !feedback.isCurrent(ticket) || !feedback.isCurrent(refresh)) return;
                const count = Number(outcome.result?.count ?? ids.length);
                feedback.publish(ticket, {severity: 'success',
                    text: `${count} ${kind === 'characters' ? 'character' : 'monster'}${count === 1 ? '' : 's'} updated.`});
                if (!feedback.isCurrent(refresh)) return;
                try {await load(true); feedback.resolve(refresh);}
                catch {feedback.publish(refresh, {severity: 'error', text:
                    'Join succeeded, but display reload failed. Reload the page; do not repeat the Join.'});}
            } finally {
                if (bulkJoinPending.get(target) === pending) bulkJoinPending.delete(target);
            }
        };
    }
    if (document.readyState === 'complete') installCoreReporting();
    else document.addEventListener('DOMContentLoaded', installCoreReporting, {once: true});
    for (const id of ['characters', 'monsters']) {
        const container = document.getElementById(id);
        if (container) new MutationObserver(refresh).observe(container, {childList: true, subtree: true});
    }
    refresh();
})();
