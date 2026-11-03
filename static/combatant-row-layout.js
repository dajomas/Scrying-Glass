/* SG-TODO-007: normalize refreshed combatant tables and expose focused controls. */
(() => {
    'use strict';
    if (window.scryingCombatantRowsInstalled) return;
    window.scryingCombatantRowsInstalled = true;

    for (const id of ['monsters', 'characters']) {
        const container = document.getElementById(id);
        if (!container) continue;
        function removeHpChangeColumn() {
            const table = container.querySelector(':scope > table');
            if (!table || !table.rows.length) return;
            const index = [...table.rows[0].cells].findIndex(
                cell => cell.textContent.trim() === 'HP change');
            if (index < 0) return;
            const cells = [...table.rows].map(row => row.cells[index]);
            // Fail closed if the renderer ever gives this column another operation.
            if (cells.some((cell, row) => !cell || (row > 0 && (
                cell.querySelectorAll('button').length !== 2 ||
                cell.querySelectorAll('[data-d], [data-h], [data-cd], [data-ch]').length !== 2
            )))) return;
            cells.forEach(cell => cell.remove());
        }
        // load() replaces the container's table. Observe that boundary only;
        // our cell removals are below it, so they do not retrigger the observer.
        new MutationObserver(removeHpChangeColumn).observe(container, {childList: true});
        removeHpChangeColumn();
    }

    const region = document.getElementById('monsters');
    if (!region) return;
    region.addEventListener('focusin', event => {
        const target = event.target;
        if (!(target instanceof HTMLElement) || target === region) return;
        const box = target.getBoundingClientRect();
        const left = region.getBoundingClientRect().left + region.clientLeft;
        const right = left + region.clientWidth;
        const padding = 4;
        if (box.left < left + padding) {
            region.scrollLeft += box.left - left - padding;
        } else if (box.right > right - padding) {
            region.scrollLeft += box.right - right + padding;
        }
    });
})();
