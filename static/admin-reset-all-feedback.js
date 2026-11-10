/* SG-TODO-009.7 / 4A.6: scoped Reset All feedback. */
(() => {
    'use strict';
    const button = document.getElementById('resetAll');
    if (!button) return;
    button.onclick = async () => {
        if (!confirm('Reset every monster and character?')) return;
        const feedback = window.scryingAdminFeedback;
        const ticket = feedback.begin({region: 'global', operation: 'battle.reset-all',
            target: 'battle', label: 'Reset all combatants'});
        try {
            await request('/api/battle/reset-all', {method: 'POST'});
        } catch (error) {
            feedback.publish(ticket, {severity: 'error', text: error.message});
            return;
        }
        // Never refresh another encounter or resolve a superseding attempt's error.
        if (!feedback.isCurrent(ticket)) return;
        feedback.resolve(ticket);
        // The reset succeeded. load() owns refresh errors; do not repeat the POST.
        await load();
    };
})();
