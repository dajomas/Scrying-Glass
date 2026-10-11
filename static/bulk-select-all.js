/* Reuse the existing selection sets; do not merely check DOM boxes. */
(() => {
    'use strict';
    document.querySelectorAll('button[data-select-all-kind]').forEach(button=>{
        button.addEventListener('click',()=>{
            const kind=button.dataset.selectAllKind;
            if(kind!=='characters'&&kind!=='monsters')return;
            if(typeof latest==='undefined'||!latest||!Array.isArray(latest[kind]))return;
            setAllSelected(kind,true);
        });
    });

    function isDead(kind, item) {
        if (kind === 'characters') {
            return item.life_state === 'dead' || (item.death_failures ?? 0) >= 3;
        }
        return item.life_state === 'dead' || item.alive === false;
    }

    for (const id of ['characterBulkAction', 'monsterBulkAction']) {
        const select = document.getElementById(id);
        if (!select || [...select.options].some(option => option.value === 'select-dead')) continue;
        const all = [...select.options].find(option => option.value === 'select-all');
        if (all) all.after(new Option('Select dead', 'select-dead'));
    }

    const originalRunBulkAction = runBulkAction;
    runBulkAction = async function (kind, action) {
        if (action !== 'select-dead') {
            return originalRunBulkAction.apply(this, arguments);
        }
        if (kind !== 'characters' && kind !== 'monsters') return;
        if (typeof latest === 'undefined' || !latest || !Array.isArray(latest[kind])) return;
        const deadIds = new Set(latest[kind].filter(item => isDead(kind, item)).map(item => item.id));
        setAllSelected(kind, false);
        for (const id of deadIds) updateRowSelection(kind, id, true);
        document.querySelectorAll(`input[data-select-kind="${kind}"][data-select-id]`).forEach(checkbox => {
            checkbox.checked = deadIds.has(checkbox.dataset.selectId);
        });
        const noun = kind === 'characters' ? 'character' : 'monster';
        paneNotification(kind, `Selected ${deadIds.size} dead ${noun}${deadIds.size === 1 ? '' : 's'}.`);
    };
})();
