/* SG-TODO-009.4 and SG-TODO-018 B: roster presentation; existing mutation helpers remain authoritative. */
(() => {
    'use strict';
    if (window.scryingRosterPresentationInstalled) return;
    window.scryingRosterPresentationInstalled = true;
    const selectionActions = new Set(['', 'select-all', 'unselect-all', 'select-dead']);
    const displayLife = value => value === 'standing' ? 'alive' : value;
    const fixedFields = {show_ac: 'AC', show_hp: 'HP', show_initiative: 'Init'};
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
                if (!item || !nameCell) continue;
                let status = nameCell.querySelector('.sg-roster-state');
                if (!status) {
                    status = document.createElement('span');
                    status.className = 'sg-roster-state';
                    nameCell.append(status);
                }
                const parts = [item.active ? 'In battle' : 'Not in battle', item.visible ? 'Visible' : 'Hidden'];
                if (typeof item.life_state === 'string' && item.life_state) parts.push(displayLife(item.life_state));
                const key = JSON.stringify(parts);
                if (status.dataset.rosterState !== key) {
                    status.textContent = '';
                    for (const text of parts) {
                        const part = document.createElement('span');
                        part.className = 'sg-roster-state-item';
                        part.textContent = text;
                        status.append(part);
                    }
                    status.dataset.rosterState = key;
                }
                const input = row.querySelector('input.initiative-edit');
                if (kind === 'characters') input?.setAttribute('aria-label', item.name + ' initiative');
                if (kind === 'monsters') {
                    const label = input?.closest('label');
                    if (label?.firstChild?.nodeType === Node.TEXT_NODE && label.firstChild.textContent.trim() === 'Roll') {
                        label.firstChild.remove();
                    }
                    const total = row.querySelector('.sg-monster-initiative-total');
                    if (total?.textContent.endsWith(' (legacy)')) {
                        total.textContent = total.textContent.replace(/ \(legacy\)$/, '');
                        total.title = 'Retained total; no raw roll recorded.';
                    }
                }
                const life = row.querySelector('button[data-cl]');
                if (life?.textContent === 'standing') life.textContent = 'alive';
                const toggles = kind === 'monsters'
                    ? [['data-ma', 'active'], ['data-mally', 'ally'], ['data-mv', 'visible']]
                    : [['data-ca', 'active'], ['data-cv', 'visible']];
                for (const [attribute, field] of toggles) {
                    const button = row.querySelector(`button[${attribute}]`);
                    if (button) {
                        button.setAttribute('aria-pressed', String(Boolean(item[field])));
                        button.setAttribute('aria-label', button.textContent.trim());
                    }
                }
                for (const button of row.querySelectorAll('button[data-t][data-f]')) {
                    const field = button.dataset.f;
                    if (!Object.hasOwn(fixedFields, field)) continue;
                    const enabled = Boolean(item[field]);
                    if (button.textContent !== fixedFields[field]) button.textContent = fixedFields[field];
                    button.classList.toggle('on', enabled);
                    button.setAttribute('aria-pressed', String(enabled));
                    button.setAttribute('aria-label', fixedFields[field]);
                    button.title = `${fixedFields[field]} display ${enabled ? 'enabled' : 'disabled'}`;
                }
                const actionCell = row.querySelector('button[data-edit]')?.closest('td');
                if (actionCell && !actionCell.querySelector(':scope > .sg-roster-actions')) {
                    const actions = document.createElement('div');
                    actions.className = 'sg-roster-actions';
                    actions.append(...actionCell.querySelectorAll(':scope > button'));
                    actionCell.append(actions);
                }
            }
        }
        // Observe late decorators as well as table replacement; all writes above
        // are idempotent, so subtree decoration cannot create an observer loop.
        new MutationObserver(update).observe(region, {childList: true, subtree: true});
        pane.addEventListener('change', () => queueMicrotask(update));
        pane.addEventListener('click', () => queueMicrotask(update));
        if (kind === 'monsters') {
            // The legacy document delegate reads a visible on/off suffix. Fixed
            // labels instead use server-derived aria-pressed; stop that delegate
            // and call the same patch helper exactly once, without optimistic edits.
            region.addEventListener('click', event => {
                const button = event.target.closest('button[data-t][data-f]');
                if (!button || !region.contains(button) || !Object.hasOwn(fixedFields, button.dataset.f)) return;
                event.stopPropagation();
                patch('monsters', button.dataset.t, {
                    [button.dataset.f]: button.getAttribute('aria-pressed') !== 'true',
                });
            });
        }
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
