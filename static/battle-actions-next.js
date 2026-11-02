/* SG-TODO-003: compose normal close, turn progression, refresh and actor open. */
(() => {
    'use strict';
    function install() {
        const button = document.getElementById('nextBattleActions');
        const main = document.getElementById('nextBattle');
        const modal = document.getElementById('battleActionModal');
        if (!button || !main || !modal) return;
        const originalRequest = request;
        let moving = false, writes = 0, advancing = false;
        const scope = state => JSON.stringify([
            state?.active_campaign_id ?? state?.active_setup?.campaign_id ?? null,
            typeof state?.active_setup === 'string' ? state.active_setup : state?.active_setup?.name ?? null,
        ]);
        const current = state => [...(state?.characters || []), ...(state?.monsters || []),
            ...(state?.lairs || [])].find(item => item.active && item.in_turn);
        const report = text => {
            message(text);
            const notice = document.getElementById('battleActionNotice');
            if (notice) notice.textContent = text;
        };
        // Include refresh time: the existing forms keep their submit controls disabled.
        const applying = () => writes > 0 || battleActionsApplying ||
            [...modal.querySelectorAll('button[type="submit"]')].some(control => control.disabled);
        request = async function(url, options = {}) {
            const action = url === '/api/battle/actions' && options.method === 'POST';
            const next = url === '/api/battle/next' && options.method === 'POST';
            if (action && (moving || advancing)) throw new Error('Turn advancement is in progress.');
            if (next && (advancing || writes || battleActionsApplying))
                throw new Error('Another battle operation is in progress.');
            if (action) writes++;
            if (next) advancing = true;
            try { return await originalRequest(url, options); }
            finally {
                if (action) writes--;
                if (next) advancing = false;
            }
        };
        // Capture before either existing form handler can submit a new action.
        modal.addEventListener('submit', event => {
            if (!moving && !advancing) return;
            event.preventDefault();
            event.stopImmediatePropagation();
        }, true);
        async function next(fromModal) {
            if (moving || advancing || applying()) return;
            if (fromModal && modal.hidden) return;
            const beforeScope = scope(latest);
            const actor = fromModal ? battleActionActorId : null;
            moving = true;
            const controls = [...new Set([main, button, ...modal.querySelectorAll('input,select,button')])];
            const disabled = controls.map(control => control.disabled);
            let submitted = false, confirmed = false, closed = false;
            try {
                // Resolve context before discarding drafts or issuing a mutation.
                const before = await request('/api/state', {cache: 'no-store'});
                if (scope(before) !== beforeScope || scope(latest) !== beforeScope ||
                    (fromModal && (modal.hidden || battleActionActorId !== actor || current(before)?.id !== actor))) {
                    report('Encounter or turn changed. Refresh and reopen the current participant.');
                    await load(true);
                    return;
                }
                if (applying()) return;
                if (fromModal) {
                    closeBattleActions();
                    closed = modal.hidden;
                    if (!closed) return;
                }
                controls.forEach(control => {control.disabled = true;});
                submitted = true;
                const result = await request('/api/battle/next', {method: 'POST'});
                confirmed = true;
                await load(true);
                const after = await request('/api/state', {cache: 'no-store'});
                if (scope(latest) !== beforeScope || scope(after) !== beforeScope) {
                    report('Turn request completed, but the encounter changed. No action screen was reopened.');
                    return;
                }
                // Require agreement with the refreshed rendering and mutation response.
                const active = current(after), rendered = current(latest);
                const expected = result?.current?.id ?? null;
                if ((active?.id ?? null) !== expected || (rendered?.id ?? null) !== expected ||
                    latest.battle_round !== after.battle_round ||
                    JSON.stringify(latest.statistics_token) !== JSON.stringify(after.statistics_token)) {
                    report('Turn changed again while refreshing. Review the current turn before continuing.');
                    return;
                }
                if (fromModal && active) {
                    // Do not replace an action screen explicitly opened while awaiting I/O.
                    if (!modal.hidden) {
                        closeBattleActions();
                        report('Turn advanced; an action screen was opened meanwhile. Reopen the current participant.');
                        return;
                    }
                    openBattleActions(active.id);
                } else if (fromModal) report('No active participant remains.');
            } catch (error) {
                // A transport failure can occur after the server has committed. Never retry POST.
                let reconciled = false;
                try { await load(true); reconciled = true; } catch { /* keep closed on refresh failure */ }
                if (closed && !modal.hidden) closeBattleActions();
                report((submitted ? (confirmed ? 'Turn advanced, but refresh/reconciliation failed. '
                    : 'Turn advance failed or its outcome is uncertain. ') : 'Unable to prepare turn advancement. ') +
                    String(error.message || error) + (reconciled
                        ? ' State refreshed; review the current turn. No automatic retry was made.'
                        : ' Refresh before continuing. No automatic retry was made.'));
            } finally {
                controls.forEach((control, index) => {control.disabled = disabled[index];});
                moving = false;
            }
        }
        button.onclick = () => next(true);
        // Both entry points share the same transport/refresh guard, not a new turn algorithm.
        main.onclick = () => next(false);
    }
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', install, {once: true});
    else install();
})();
