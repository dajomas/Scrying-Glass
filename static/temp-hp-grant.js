/* SG-TODO-027: grant temporary HP per target in Battle Actions (5e: no stacking).
 * Adds two choices to each target row's Action list; reaction rows keep damage and healing. */
(() => {
    'use strict';
    const rows = document.getElementById('battleActionRows');
    if (!rows || window.scryingTempHpGrantInstalled) return;
    window.scryingTempHpGrantInstalled = true;

    if (typeof actionAmountRequired === 'function') {
        const previous = actionAmountRequired;
        actionAmountRequired = action => action === 'temp-hp' || action === 'temp-hp-replace' || previous(action);
    }

    const choices = [
        ['temp-hp', 'Temporary HP (keep higher)'],
        ['temp-hp-replace', 'Temporary HP (replace)'],
    ];

    function extend(row) {
        if (row.querySelector('[data-action-source]')) return;  // reactions: damage or healing only
        const select = row.querySelector('select[data-action-kind]');
        if (!select || select.querySelector('option[value="temp-hp"]')) return;
        for (const [value, label] of choices) {
            const option = document.createElement('option');
            option.value = value;
            option.textContent = label;
            select.append(option);
        }
        select.title = 'Temporary HP never stack: keep higher takes the new amount only if it is higher.';
    }

    const observer = new MutationObserver(() => rows.querySelectorAll('.battle-action-row').forEach(extend));
    observer.observe(rows, {childList: true});
    rows.querySelectorAll('.battle-action-row').forEach(extend);
})();
