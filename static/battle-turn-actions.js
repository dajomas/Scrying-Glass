(() => {
    'use strict';

    function buildTurnActions(actorId, damage, healing) {
        return [['damage', damage], ['heal', healing]].flatMap(([action, raw]) => {
            const text = String(raw).trim();
            if (!text) return [];
            const amount = Number(text);
            if (!Number.isSafeInteger(amount) || amount < 0 || amount > 99999) {
                throw new Error('Damage and healing must be whole numbers from 0 to 99999.');
            }
            return amount === 0 ? [] : [{
                target_id: actorId, action, amount, critical_hit: false,
            }];
        });
    }

    function reorderCriticalFields(rows) {
        for (const row of rows.querySelectorAll('.battle-action-row')) {
            const amount = row.querySelector('.amount-field');
            const checkbox = row.querySelector('input[type="checkbox"]');
            const field = checkbox?.closest('label');
            if (amount && field && field.parentNode === amount.parentNode &&
                field.nextElementSibling !== amount) {
                amount.before(field);
            }
        }
    }

    function install() {
        const $ = id => document.getElementById(id);
        const modal = $('battleActionModal');
        const rows = $('battleActionRows');
        const form = $('battleTurnEffectsForm');
        if (!modal || !rows || !form) return;
        let busy = false;
        let session = 0;
        const actor = () => typeof battleActionActorId === 'undefined' || !latest
            ? null
            : [...latest.characters, ...latest.monsters]
                .find(item => item.id === battleActionActorId);
        const notice = text => { $('battleTurnNotice').textContent = text; };
        const updateActor = () => {
            const item = actor();
            $('battleTurnCombatant').textContent = item
                ? `${item.name}: HP ${item.hp}/${item.max_hp} · Temporary HP ${item.temp_hp || 0}`
                : 'No current combatant.';
        };
        new MutationObserver(() => reorderCriticalFields(rows))
            .observe(rows, {childList: true, subtree: true});
        new MutationObserver(() => {
            session += 1;
            if (modal.hidden) return;
            form.reset();
            notice('');
            updateActor();
            reorderCriticalFields(rows);
        }).observe(modal, {attributes: true, attributeFilter: ['hidden']});
        reorderCriticalFields(rows);

        form.addEventListener('submit', async event => {
            event.preventDefault();
            if (busy) return;
            const item = actor();
            if (!item || !item.active || !item.in_turn) {
                notice('Only the current active combatant can apply start-of-turn changes.');
                return;
            }
            let actions;
            try {
                actions = buildTurnActions(item.id, $('battleTurnDamage').value,
                    $('battleTurnHealing').value);
            } catch (error) { notice(error.message); return; }
            if (!actions.length) { notice('Enter damage or healing greater than zero.'); return; }
            if (typeof window.scryingDamagePreview === 'function' &&
                !confirm(actions.map(row => window.scryingDamagePreview(item,
                    row.action === 'damage' ? -row.amount : row.amount, true)).join('\n\n') +
                    '\n\nDamage is applied before healing.')) return;
            const submittedSession = session;
            busy = true;
            const button = form.querySelector('button[type="submit"]');
            const controls = [...form.querySelectorAll('input, button'),
                ...$('battleActionForm').querySelectorAll('input, select, button')];
            const previous = controls.map(control => control.disabled);
            controls.forEach(control => { control.disabled = true; });
            let applied = false;
            try {
                await request('/api/battle/actions', {
                    method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({actor_id: item.id, actions}),
                });
                applied = true;
                if (session === submittedSession) {
                    form.reset();
                    notice('Start-of-turn changes applied.');
                }
                await load();
                if (session !== submittedSession) return;
                updateActor();
                const current = actor();
                if (!current || !current.in_turn || !current.active || !current.alive) {
                    closeBattleActions();
                    message('Start-of-turn changes applied; this combatant can no longer act.');
                }
            } catch (error) {
                if (session === submittedSession) notice(applied
                    ? `Changes were applied, but refresh failed: ${error.message}. Refresh before continuing.`
                    : error.message);
            } finally {
                controls.forEach((control, index) => { control.disabled = previous[index]; });
                button.disabled = false;
                busy = false;
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', install, {once: true});
    } else install();
})();
