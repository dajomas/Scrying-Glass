/* SG-TODO-009.7 / 4A.5: scoped End feedback; no combatant reset. */
(() => {
    'use strict';
    const button = document.getElementById('endBattle');
    if (!button) return;
    button.onclick = async () => {
        const feedback = window.scryingAdminFeedback;
        const validation = () => feedback.begin({region: 'global',
            operation: 'battle.end.validation', target: 'battle', label: 'End battle validation'});
        if (!latest?.battle_order?.length) {
            feedback.publish(validation(), {severity: 'error', text: 'There is no active battle to end.'});
            return;
        }
        const setup = typeof latest?.active_setup === 'string' ? latest.active_setup : latest?.active_setup?.name;
        if (!confirm(`End the battle in ${setup ? `battle setup “${setup}”` : 'the current battle setup'} without resetting combatants?`)) return;
        feedback.resolve(validation());
        const ticket = feedback.begin({region: 'global', operation: 'battle.end',
            target: 'battle', label: 'End battle'});
        try {
            await request('/api/battle/end', {method: 'POST'});
        } catch (error) {
            feedback.publish(ticket, {severity: 'error', text: error.message});
            return;
        }
        // Do not announce or refresh a different encounter or a superseded attempt.
        if (!feedback.isCurrent(ticket)) return;
        feedback.publish(ticket, {severity: 'success', text: 'Battle ended. Combatants were not reset.'});
        // load() owns refresh errors. End has already succeeded; never retry its POST here.
        await load();
    };
})();
