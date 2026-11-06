/* SG-TODO-009.4, increment 1: presentation and selection context only. */
(() => {
    'use strict';
    if (window.scryingRosterPresentationInstalled) return;
    window.scryingRosterPresentationInstalled = true;
    const selectionActions = new Set(['', 'select-all', 'unselect-all', 'select-dead']);
    for (const kind of ['characters', 'monsters']) {
        const region = document.getElementById(kind);
        const select = document.getElementById(kind === 'characters' ? 'characterBulkAction' : 'monsterBulkAction');
        const pane = region?.closest('section');
        const toolbar = select?.closest('.bulk-action-toolbar');
        if (!region || !pane || !toolbar) continue;
        pane.classList.add('sg-roster-pane');
        region.classList.add('sg-roster-region');
        const heading = pane.querySelector('h2');
        if (heading && !heading.id) heading.id = kind + 'RosterHeading';
        region.setAttribute('role', 'region');
        if (heading) region.setAttribute('aria-labelledby', heading.id);
        region.setAttribute('tabindex', '0');
        const count = document.createElement('span');
        count.className = 'sg-selected-count';
        count.id = kind + 'SelectedCount';
        count.setAttribute('role', 'status');
        count.setAttribute('aria-live', 'polite');
        const refs = (select.getAttribute('aria-describedby') || '').split(/\s+/).filter(Boolean);
        select.setAttribute('aria-describedby', [...new Set([...refs, count.id])].join(' '));
        const originalDisabled = new WeakMap([...select.options].map(option => [option, option.disabled]));
        const clear = document.createElement('button');
        clear.type = 'button';
        clear.textContent = 'Clear selection';
        clear.id = kind + 'ClearSelection';
        clear.addEventListener('click', () => {
            setAllSelected(kind, false);
            update();
            toolbar.querySelector('[data-select-all-kind]')?.focus();
        });
        toolbar.prepend(count);
        toolbar.append(clear);
        function update() {
            const boxes = [...region.querySelectorAll('input[data-select-kind][data-select-id]')];
            const selected = boxes.filter(box => box.checked).length;
            const message = selected + ' selected';
            if (count.textContent !== message) count.textContent = message;
            clear.disabled = selected === 0;
            for (const option of select.options) {
                option.disabled = Boolean(originalDisabled.get(option)) ||
                    (!selectionActions.has(option.value) && selected === 0);
            }
            const items = typeof latest !== 'undefined' && Array.isArray(latest?.[kind]) ? latest[kind] : [];
            const byId = new Map(items.map(item => [String(item.id), item]));
            for (const box of boxes) {
                const row = box.closest('tr');
                if (!row) continue;
                row.classList.toggle('sg-row-selected', box.checked);
                const item = byId.get(box.dataset.selectId);
                const nameCell = row.cells[1];
                if (item && nameCell) {
                    let status = nameCell.querySelector('.sg-roster-state');
                    if (!status) {
                        status = document.createElement('span');
                        status.className = 'sg-roster-state';
                        nameCell.append(status);
                    }
                    const parts = [item.active ? 'In battle' : 'Not in battle', item.visible ? 'Visible' : 'Hidden'];
                    if (typeof item.life_state === 'string' && item.life_state) parts.push(item.life_state);
                    status.textContent = parts.join(' · ');
                    row.querySelector('input.initiative-edit')?.setAttribute('aria-label', item.name + ' initiative');
                }
            }
        }
        new MutationObserver(update).observe(region, {childList: true});
        pane.addEventListener('change', () => queueMicrotask(update));
        pane.addEventListener('click', () => queueMicrotask(update));
        if (kind === 'characters') {
            region.addEventListener('focusin', event => {
                const target = event.target;
                if (!(target instanceof HTMLElement) || target === region) return;
                const box = target.getBoundingClientRect();
                const left = region.getBoundingClientRect().left + region.clientLeft;
                const right = left + region.clientWidth;
                if (box.left < left + 4) region.scrollLeft += box.left - left - 4;
                else if (box.right > right - 4) region.scrollLeft += box.right - right + 4;
            });
        }
        update();
    }
})();
