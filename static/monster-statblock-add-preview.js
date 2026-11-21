/* Show statblock in Add Monster (SG-TODO-022.15).
 *
 * The Appearance group of the Add Monster form gets a "Show statblock" button.
 * It is active only while a monster chosen from a statblock source (the lookup
 * or the source dropdown) is selected for the species in the form, and shows
 * that source's statblock with the form's current name, species, AC, HP and
 * initiative bonus. The statblock is prepared on the server from the signed
 * selection (POST /api/statblocks/preview) and nothing is saved; after the add,
 * the statblock is collected from the same source. A source without a
 * statblock disables the button with a note until another monster is chosen.
 */
(() => {
    'use strict';
    const sb = window.scryingStatblockImport;
    if (!sb) return;
    const SOURCES = new Set(['D&D Beyond', '5e.tools', 'Open5e']);
    const UNAVAILABLE = new Set(['not_found', 'statblock_unavailable', 'selected_unavailable', 'identity_mismatch',
        'no_source', 'provider_disabled']);
    const POLL_MS = 300;
    const wait = ms => new Promise(resolve => setTimeout(resolve, ms));

    function install() {
        const form = document.querySelector('#monsterForm');
        const image = document.querySelector('#monsterImage');
        if (!form || !image || form.querySelector('.monster-statblock-add-preview')) return;
        const anchor = image.closest('.sg-image-field') || image.closest('label.field') || image;
        const button = sb.element('button', {type: 'button', text: 'Show statblock', disabled: true,
            'aria-describedby': 'monsterStatblockPreviewNote'});
        const note = sb.element('span', {id: 'monsterStatblockPreviewNote', className: 'monster-statblock-add-note',
            text: 'Choose a monster from a source to see its statblock.'});
        const field = sb.element('div', {className: 'field monster-statblock-add-preview'}, [
            sb.element('span', {className: 'field-label', text: 'Statblock'}), button, note]);
        anchor.after(field);
        const species = form.elements.monster_species;
        let selection = null;
        let unavailable = null; // selection token whose source has no statblock

        const sync = () => {
            const current = selection && selection.species === species?.value.trim() &&
                SOURCES.has(selection.provider) && typeof selection.selection_token === 'string';
            button.disabled = !current || unavailable === selection.selection_token;
            if (!current) note.textContent = 'Choose a monster from a source to see its statblock.';
            else if (unavailable === selection.selection_token) note.textContent = `No statblock is available from ${selection.provider}.`;
            else note.textContent = `From ${selection.provider}; it is added with the monster.`;
        };
        document.addEventListener('scrying:monster-selection', event => { selection = event.detail || null; sync(); });
        species?.addEventListener('input', sync);
        form.addEventListener('reset', () => queueMicrotask(() => { selection = null; sync(); }));
        sync();

        button.addEventListener('click', async () => {
            if (button.disabled || !selection) return;
            const chosen = selection;
            const live = () => ({name: form.elements.name?.value.trim() || chosen.species,
                species: species?.value.trim(), ac: form.elements.ac?.value === '' ? null : Number(form.elements.ac?.value),
                hp: hpValue(form.elements.hprangestart?.value), max_hp: hpValue(form.elements.hprangestart?.value),
                initiative_bonus: form.elements.initiative_bonus?.value.trim() === '' ? null
                    : Number(form.elements.initiative_bonus?.value)});
            const view = shell(`Statblock: ${form.elements.name?.value.trim() || chosen.species}`);
            const control = {cancelled: false, jobId: null};
            view.onClose(() => { control.cancelled = true; if (control.jobId) sb.cancel(control.jobId); });
            view.status.textContent = `Preparing the statblock from ${chosen.provider}… This can take a few seconds.`;
            try {
                let job = await sb.api('/api/statblocks/preview', sb.json('POST',
                    {selection_token: chosen.selection_token, species: chosen.species}));
                control.jobId = job.job_id;
                while (job.status === 'queued' || job.status === 'running') {
                    await wait(POLL_MS);
                    if (control.cancelled) return;
                    job = await sb.api('/api/statblocks/jobs/' + encodeURIComponent(job.job_id));
                }
                if (control.cancelled) return;
                if (job.status !== 'completed') {
                    const code = job.error?.code;
                    if (UNAVAILABLE.has(code)) { unavailable = chosen.selection_token; sync(); }
                    view.status.textContent = job.error?.message || 'The statblock could not be prepared.';
                    return;
                }
                control.jobId = null;
                view.status.textContent = `${job.source_label} — ${chosen.provider}` +
                    (job.completeness === 'partial' ? ' — partial' : '') + '. Preview only; nothing is saved.';
                const area = sb.element('div', {className: 'monster-statblock-preview', tabindex: '0', 'aria-label': 'Statblock'});
                if (window.ScryingStatblock) area.append(window.ScryingStatblock.render(job.preview, live(), {prefix: 'add-preview-'}));
                view.body.append(area);
            } catch (error) {
                if (control.cancelled) return;
                if (UNAVAILABLE.has(error.code)) { unavailable = chosen.selection_token; sync(); }
                view.status.textContent = error.message;
            }
        });
    }

    function hpValue(text) {
        const value = String(text ?? '').trim();
        return /^\d+$/.test(value) ? Number(value) : null; // a dice expression is rolled when the monster is added
    }

    function shell(title) {
        const previous = document.activeElement;
        const status = sb.element('p', {role: 'status', 'aria-live': 'polite', className: 'monster-statblock-dialog-status'});
        const body = sb.element('div', {className: 'monster-statblock-dialog-body'});
        const close = sb.element('button', {type: 'button', text: 'Close'});
        const dialog = sb.element('dialog', {className: 'monster-statblock-dialog', 'aria-label': title},
            [sb.element('h2', {text: title}), status, body, sb.element('div', {className: 'monster-statblock-dialog-actions'}, [close])]);
        document.body.append(dialog);
        dialog.showModal();
        const closers = [];
        const shut = () => {
            closers.forEach(fn => fn());
            if (dialog.open) dialog.close();
            dialog.remove();
            previous?.focus?.();
        };
        close.addEventListener('click', shut);
        dialog.addEventListener('cancel', event => { event.preventDefault(); shut(); });
        close.focus();
        return {status, body, onClose: fn => closers.push(fn)};
    }

    if (document.readyState === 'loading' ||
        (document.readyState === 'interactive' && document.currentScript?.defer)) {
        document.addEventListener('DOMContentLoaded', install, {once: true});
    } else {
        install();
    }
})();
