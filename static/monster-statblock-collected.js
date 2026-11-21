/* Confirm statblocks collected for added monsters (SG-TODO-022.15).
 *
 * Add Monster (selected source) and Import .monster collect a statblock in the
 * background. A monster that meanwhile got a different statblock, or whose
 * species or source was edited, is never overwritten silently: the server
 * holds the collected statblock and this dialog asks Replace / Keep current per
 * monster. After an add the Admin checks for waiting statblocks for a short
 * while, and once when the page loads. "Decide later" closes the dialog; the
 * statblocks keep waiting until they expire and are shown again after the next
 * add or reload.
 */
(() => {
    'use strict';
    const sb = window.scryingStatblockImport;
    if (!sb) return;
    const POLL_MS = 2000, POLL_FOR_MS = 40000;
    const later = new Set();
    let pollUntil = 0, timer = null, view = null;

    const REASONS = {
        changed: 'Its species or source was edited after it was added.',
        has_statblock: 'It already has a different statblock.',
    };

    function schedule(delay) {
        clearTimeout(timer);
        timer = setTimeout(check, delay);
    }

    function watch() {
        pollUntil = Date.now() + POLL_FOR_MS;
        schedule(POLL_MS);
    }

    async function check() {
        timer = null;
        let body = null;
        try {
            body = await sb.api('/api/statblocks/collected');
        } catch (error) {
            body = null; // not signed in as a campaign admin, or offline: nothing to ask
        }
        const items = (body?.items || []).filter(item => !later.has(item.collected_id));
        if (items.length) show(items);
        else if (Date.now() < pollUntil) schedule(POLL_MS);
    }

    function reasonText(item) {
        const parts = (item.reasons || []).map(reason => REASONS[reason]).filter(Boolean);
        if ((item.reasons || []).includes('has_statblock') && item.current_source_label) {
            parts.push(`Current statblock: ${item.current_source_label} (revision ${item.statblock_revision}).`);
        }
        return parts.join(' ');
    }

    function show(items) {
        if (!view) view = open();
        const known = new Set([...view.list.children].map(card => card.dataset.id));
        for (const item of items) if (!known.has(item.collected_id)) view.list.append(card(item));
        view.update();
    }

    function open() {
        const previous = document.activeElement;
        const status = sb.element('p', {role: 'status', 'aria-live': 'polite', className: 'monster-statblock-dialog-status',
            text: 'Statblocks were collected for monsters you added, but these monsters changed meanwhile. ' +
                  'Nothing is replaced until you choose.'});
        const list = sb.element('div', {className: 'monster-statblock-rows'});
        const close = sb.element('button', {type: 'button', text: 'Decide later'});
        const dialog = sb.element('dialog', {className: 'monster-statblock-dialog monster-statblock-collected',
            'aria-label': 'Replace statblocks?'},
            [sb.element('h2', {text: 'Replace statblocks?'}), status, list,
             sb.element('div', {className: 'monster-statblock-dialog-actions'}, [close])]);
        document.body.append(dialog);
        dialog.showModal();
        const shut = () => {
            for (const row of list.children) later.add(row.dataset.id);
            if (dialog.open) dialog.close();
            dialog.remove();
            view = null;
            previous?.focus?.();
        };
        close.addEventListener('click', shut);
        dialog.addEventListener('cancel', event => { event.preventDefault(); shut(); });
        const state = {dialog, status, list, shut,
            update() {
                if (!list.children.length) { shut(); return; }
                list.querySelector('button')?.focus();
            }};
        return state;
    }

    function card(item) {
        const note = sb.element('p', {className: 'monster-statblock-row-status', role: 'status', 'aria-live': 'polite'});
        const replace = sb.element('button', {type: 'button', text: 'Replace'});
        const keep = sb.element('button', {type: 'button', text: 'Keep current'});
        const preview = sb.element('div', {className: 'monster-statblock-preview', tabindex: '0',
            'aria-label': `Collected statblock for ${item.name}`});
        if (window.ScryingStatblock && item.preview) {
            preview.append(window.ScryingStatblock.render(item.preview, item.live || {}, {prefix: 'collected-' + item.collected_id + '-'}));
        }
        const details = sb.element('details', {}, [sb.element('summary', {text: 'Show the collected statblock'}), preview]);
        const row = sb.element('section', {className: 'monster-statblock-row', 'aria-label': item.name}, [
            sb.element('h3', {text: `${item.name}${item.species ? ' — ' + item.species : ''}`}),
            sb.element('p', {text: reasonText(item)}),
            sb.element('p', {text: `Collected: ${item.source_label} (${item.provider})` +
                (item.completeness === 'partial' ? ', partial' : '') + '.'}),
            details,
            sb.element('div', {className: 'monster-statblock-row-controls'}, [replace, keep]), note]);
        row.dataset.id = item.collected_id;
        const decide = async decision => {
            replace.disabled = keep.disabled = true;
            note.textContent = decision === 'replace' ? 'Replacing…' : 'Keeping the current statblock…';
            try {
                await sb.api('/api/statblocks/collected/' + encodeURIComponent(item.collected_id),
                    sb.json('POST', {decision, expected_statblock_revision: item.statblock_revision}));
                row.remove();
                if (decision === 'replace' && typeof load === 'function') load();
                view?.status && (view.status.textContent = `${item.name}: ` +
                    (decision === 'replace' ? 'statblock replaced.' : 'current statblock kept.'));
                view?.update();
            } catch (error) {
                if (error.code === 'collected_expired' || error.code === 'encounter_changed') {
                    note.textContent = error.message;
                    setTimeout(() => { row.remove(); view?.update(); }, 2500);
                } else {
                    note.textContent = error.message;
                    replace.disabled = keep.disabled = false;
                    if (error.code === 'stale_revision') { row.remove(); view?.update(); watch(); }
                }
            }
        };
        replace.addEventListener('click', () => decide('replace'));
        keep.addEventListener('click', () => decide('keep'));
        return row;
    }

    for (const selector of ['#monsterForm', '#monsterUpload']) {
        document.querySelector(selector)?.addEventListener('submit', watch);
    }
    schedule(1000); // statblocks still waiting from before a reload

    window.scryingCollectedStatblocks = {check, watch};
})();
