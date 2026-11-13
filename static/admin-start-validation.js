/* SG-TODO-009.7 4A.3: validation feedback only; request ownership stays in 4A.2. */
(() => {
    'use strict';
    if (window.scryingStartValidationInstalled) return;
    const feedback = window.scryingAdminFeedback;
    const begin = (operation, label) => feedback.begin({region: 'global', operation,
        target: 'battle', label});
    window.scryingStartValidationInstalled = true;
    document.querySelector('#startBattle').onclick = () => {
        const ticket = begin('battle.start.eligibility', 'Start eligibility');
        const order = normalOrder();
        if (!order.length && !(latest.lairs || []).some(x => x.active)) {
            feedback.publish(ticket, {severity: 'error',
                text: 'Activate at least one turn-eligible participant first'});
            return;
        }
        feedback.resolve(ticket);
        if (!tiedBuckets().length) {
            feedback.resolve(begin('battle.start.tie-order', 'Start tie order'));
            startBattle(order);
            return;
        }
        document.querySelector('#tieGroups').innerHTML = tieUI();
        document.querySelector('#tieModal').hidden = false;
    };
    document.querySelector('#confirmOrder').onclick = () => {
        const ticket = begin('battle.start.tie-order', 'Start tie order');
        try {
            const orderedTies = readTieOrder();
            let tieIndex = 0;
            const order = [];
            for (const bucket of initiativeBuckets()) {
                if (bucket.initiative !== null && bucket.members.length > 1) {
                    order.push(...orderedTies[tieIndex++]);
                } else {
                    order.push(...bucket.members.map(combatant => combatant.id));
                }
            }
            feedback.resolve(ticket);
            document.querySelector('#tieModal').hidden = true;
            startBattle(order);
        } catch (error) {
            feedback.publish(ticket, {severity: 'error', text: error.message});
        }
    };
})();
