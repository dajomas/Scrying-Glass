/* SG-TODO-025: "Add Max HP increase" in Battle Actions, next to the statistics reduction.
 * Current HP rises by the same amount (SG-TODO-026); the server stays authoritative. */
(() => {
    'use strict';
    const reduction = document.getElementById('addStatisticsReduction');
    const rows = document.getElementById('battleActionRows');
    if (!reduction || !rows || window.scryingMaxHpIncreaseInstalled) return;
    window.scryingMaxHpIncreaseInstalled = true;

    if (typeof actionAmountRequired === 'function') {
        const previous = actionAmountRequired;
        actionAmountRequired = action => action === 'increase-max-hp' || previous(action);
    }

    const tracked = item => !window.scryingTracksHp || window.scryingTracksHp(item);
    const dead = item => item.life_state === 'dead' || (!('monster_species' in item) && (item.death_failures || 0) >= 3);

    function addRow() {
        if (typeof battleActionsApplying !== 'undefined' && battleActionsApplying) return;
        const targets = (typeof activeBattleTargets === 'function' ? activeBattleTargets() : [])
            .filter(item => !dead(item) && tracked(item));
        const feedback = typeof battleActionFeedback === 'function' ? battleActionFeedback : null;
        if (!targets.length) {
            feedback?.('targets', 'increase', 'Max HP increase targets',
                {severity: 'error', text: 'There are no active targets whose HP is tracked.'});
            return;
        }
        feedback?.('targets', 'increase', 'Max HP increase targets');
        const row = document.createElement('div');
        row.className = 'battle-action-row max-hp-increase-row';
        row.innerHTML = `
        <input data-action-kind type="hidden" value="increase-max-hp">
        <label>Target <select data-action-target required>
          <option value="" disabled selected>Select target…</option>
          ${targets.map(x => `<option value="${esc(x.id)}">${esc(x.name)}</option>`).join('')}
        </select></label>
        <label class="amount-field">Max HP increase
          <input data-action-amount type="number" required min="1" max="99999" step="1" value="1">
        </label>
        <p class="field-help">Current HP rises by the same amount. Remove it again with Restore statistics.</p>
        <button data-remove-action-row type="button" class="danger">Remove</button>`;
        row.querySelector('[data-remove-action-row]').addEventListener('click', () => row.remove());
        rows.appendChild(row);
    }

    const button = document.createElement('button');
    button.type = 'button';
    button.id = 'addMaxHpIncrease';
    button.textContent = 'Add Max HP increase';
    button.addEventListener('click', addRow);
    reduction.after(button);
})();
