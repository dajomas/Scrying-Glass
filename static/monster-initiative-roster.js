/* Monster roster bonus presentation only; no initiative mutations. */
(() => {
    'use strict';
    const region = document.getElementById('monsters');
    if (!region) return;
    function update() {
        const table = region.querySelector(':scope > table');
        if (!table || !table.rows.length || table.dataset.monsterBonusColumn) return;
        const header = table.rows[0];
        const index = [...header.cells].findIndex(cell => cell.textContent.trim() === 'Initiative');
        if (index < 0) return;
        const items = typeof latest !== 'undefined' && Array.isArray(latest?.monsters)
            ? latest.monsters : [];
        const byId = new Map(items.map(item => [String(item.id), item]));
        const changes = [];
        for (const row of [...table.rows].slice(1)) {
            const box = row.querySelector('input[data-select-kind="monsters"][data-select-id]');
            const anchor = row.cells[index];
            if (!box || !anchor) return;
            const item = byId.get(box.dataset.selectId);
            const value = item?.initiative_bonus === undefined ? 0 : item.initiative_bonus;
            const valid = Boolean(item) && Number.isSafeInteger(value);
            const text = valid ? (value >= 0 ? `+${value}` : String(value)) : 'Unavailable';
            const origin = item?.initiative_bonus_origin ?? (value === 0 ? 'default' : null);
            const knownOrigin = ['default', 'manual', 'import', 'source'].includes(origin);
            const cell = document.createElement('td');
            cell.className = 'sg-monster-initiative-bonus';
            cell.textContent = text;
            cell.title = valid
                ? `Assigned bonus (${knownOrigin ? origin : 'origin unavailable'}). Change it in Edit.`
                : 'Bonus unavailable or not exactly representable in this view. Review it in Edit.';
            changes.push({row, anchor, cell});
        }
        const heading = document.createElement('th');
        heading.scope = 'col';
        heading.className = 'sg-monster-initiative-bonus';
        heading.textContent = 'Initiative bonus';
        header.cells[index].before(heading);
        for (const {anchor, cell} of changes) anchor.before(cell);
        table.dataset.monsterBonusColumn = 'true';
    }
    new MutationObserver(update).observe(region, {childList: true});
    update();
})();
