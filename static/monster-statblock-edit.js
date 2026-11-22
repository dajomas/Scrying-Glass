/* Edit Monster statblock import (SG-TODO-022.13).
 *
 * A Statblock section in the monster Edit dialog: "Find statblock" searches the
 * enabled sources for the species in the form (exact candidates, original
 * tracker source first) and "Upload .monster file" uses a Tetra-cube file. The
 * chosen statblock is prepared and previewed without saving; "Use this
 * statblock" stages it in hidden fields and Save monster saves it atomically
 * with the ordinary edit. Cancelling the chooser discards its unconfirmed
 * choice; cancelling Edit discards everything staged. expected_values carries
 * the previous values of explicitly edited fields so a concurrent change
 * rejects the save instead of being overwritten. "Show statblock" shows the
 * staged statblock when there is one, otherwise the saved one, with the
 * dialog's current name, species, AC and HP (022.15 correction).
 */
(() => {
    'use strict';
    const sb = window.scryingStatblockImport;
    if (!sb || typeof openEdit !== 'function') return;
    const FIELDS = ['name', 'monster_species', 'ac', 'hp', 'max_hp', 'original_hp', 'color', 'initiative', 'ally'];
    const text = value => (value === null || value === undefined ? '' : String(value));
    let staged = null; // {jobId, session, job}

    const previousOpen = openEdit;
    openEdit = function(kind, id, ...rest) {
        const result = previousOpen.call(this, kind, id, ...rest);
        if (kind === 'monsters') install(id);
        return result;
    };
    const previousClose = closeEdit;
    closeEdit = function(...args) {
        if (staged) { sb.cancel(staged.jobId); staged = null; } // unsaved or consumed: both release it
        return previousClose.apply(this, args);
    };

    function install(id) {
        const form = document.querySelector('#editForm');
        const item = (latest?.monsters || []).find(monster => monster.id === id);
        if (!form || !item || form.querySelector('.monster-statblock-edit')) return;
        const session = editing;
        const original = Object.fromEntries(FIELDS.map(field => [field, item[field]]));
        const hidden = name => Object.assign(document.createElement('input'), {type: 'hidden', name});
        const selection = hidden('statblock_selection_id');
        const operation = hidden('statblock_operation_id');
        const revision = hidden('statblock_expected_revision');
        const expected = hidden('expected_values');
        const status = sb.element('p', {className: 'monster-statblock-status', role: 'status', 'aria-live': 'polite',
            text: 'Checking the saved statblock…'});
        const find = sb.element('button', {type: 'button', text: 'Find statblock'});
        const upload = sb.element('input', {type: 'file', accept: '.monster,application/json'});
        const uploadLabel = sb.element('label', {className: 'monster-statblock-upload'}, [
            sb.element('span', {text: 'Upload .monster file'}), upload]);
        const show = sb.element('button', {type: 'button', text: 'Show statblock', disabled: true});
        const clear = sb.element('button', {type: 'button', text: 'Keep current statblock', hidden: true});
        const section = sb.element('fieldset', {className: 'monster-statblock-edit full'}, [
            sb.element('legend', {text: 'Statblock'}), status,
            sb.element('div', {className: 'monster-statblock-actions'}, [show, find, uploadLabel, clear]),
            selection, operation, revision, expected]);
        const actions = form.querySelector('.actions');
        if (actions) actions.before(section); else form.append(section);
        const current = () => editing === session && !editModal.hidden;
        const say = value => { status.textContent = value; };
        let saved = null;
        const syncShow = () => { show.disabled = !(staged || saved?.statblock_revision); };
        const live = () => ({name: form.elements.name?.value.trim(), species: form.elements.monster_species?.value.trim(),
            ac: Number(form.elements.ac?.value), hp: Number(form.elements.hp?.value),
            max_hp: Number(form.elements.max_hp?.value), initiative_bonus: item.initiative_bonus});

        const syncExpected = () => {
            const changed = {};
            for (const field of FIELDS) {
                const input = form.elements[field];
                if (!input || typeof input.value !== 'string') continue;
                const value = field === 'name' || field === 'monster_species' ? input.value.trim() : input.value;
                if (value !== text(original[field])) changed[field] = original[field] ?? null;
            }
            expected.value = Object.keys(changed).length ? JSON.stringify(changed) : '';
        };
        form.addEventListener('input', syncExpected);
        form.addEventListener('change', syncExpected);
        syncExpected();

        sb.state().then(state => {
            if (!current()) return;
            saved = state.monsters.find(row => row.monster_id === id) || null;
            say(`Current: ${sb.statusText(saved)}.`);
            syncShow();
        }).catch(error => { if (current()) say(`Current statblock unknown: ${error.message}`); });

        function unstage() {
            if (staged) sb.cancel(staged.jobId);
            staged = null;
            selection.value = operation.value = revision.value = '';
            clear.hidden = true;
            syncShow();
        }
        clear.addEventListener('click', () => { unstage(); say(`Current: ${sb.statusText(saved)}. No change.`); });

        async function choose(prepare, label) {
            const control = {cancelled: false};
            const dialog = chooser(label, control);
            try {
                const context = await sb.state();
                const row = context.monsters.find(entry => entry.monster_id === id);
                const base = row ? row.statblock_revision : 0;
                dialog.say('Preparing the statblock… This can take a few seconds.');
                const job = await prepare(context, base, control);
                if (control.cancelled || !current()) { sb.cancel(job.job_id); return; }
                const accepted = await dialog.review(job, live());
                if (!accepted || !current()) { sb.cancel(job.job_id); return; }
                unstage();
                staged = {jobId: job.job_id, session, job};
                syncShow();
                selection.value = job.selection_id;
                operation.value = sb.operationId();
                revision.value = String(base);
                clear.hidden = false;
                say(`Selected: ${job.source_label} (${job.source?.provider || 'file'})` +
                    `${job.completeness === 'partial' ? ', partial' : ''}. Save monster to apply; it expires at ` +
                    `${sb.time(job.expires_at)}.`);
            } catch (error) {
                if (error.code !== 'cancelled' && current()) dialog.say(error.message, true);
                if (error.code === 'cancelled') dialog.close();
            }
        }

        show.addEventListener('click', async () => {
            if (staged) {
                viewer(`Statblock: ${form.elements.name?.value.trim() || item.name}`,
                    'Selected statblock — not saved until you save the monster.', area => sb.preview(area, staged.job, live()));
                return;
            }
            show.disabled = true;
            show.setAttribute('aria-busy', 'true');
            try {
                const body = await sb.api('/api/statblocks/monsters/' + encodeURIComponent(id));
                if (!current()) return;
                if (!body.statblock) {
                    say(`Current: ${sb.statusText(body)}.`);
                    saved = body;
                    return;
                }
                const label = [body.statblock.source_label, body.source?.provider, body.source?.source_code].filter(Boolean).join(' · ');
                viewer(`Statblock: ${form.elements.name?.value.trim() || item.name}`,
                    `Saved statblock (revision ${body.statblock_revision})${label ? ' — ' + label : ''}.`,
                    area => area.append(window.ScryingStatblock.render(body.statblock, live(), {prefix: 'saved-' + id + '-'})));
            } catch (error) {
                if (current()) say(`The statblock could not be shown: ${error.message}`);
            } finally {
                show.removeAttribute('aria-busy');
                if (current()) syncShow();
            }
        });

        find.addEventListener('click', async () => {
            const species = form.elements.monster_species?.value.trim();
            if (!species) { say('Enter the monster species first.'); return; }
            find.disabled = true;
            find.setAttribute('aria-busy', 'true');
            say(`Searching the sources for ${species}…`);
            try {
                const {result} = await sb.discover([id], species);
                if (!current()) return;
                const row = result.monsters[0];
                const notes = sb.providerNotes(row);
                const candidates = row.candidates.filter(candidate => !candidate.disabled);
                if (!candidates.length) {
                    say([`No statblocks found for ${species}.`, ...notes].join(' '));
                    return;
                }
                say(notes.join(' ') || `${candidates.length} statblock(s) found for ${species}.`);
                const candidate = await pick(species, candidates, notes);
                if (!candidate || !current()) return;
                await choose((context, base, control) => sb.prepareCandidate(context, id, base, candidate.candidate_id, control),
                    sb.candidateLabel(candidate));
            } catch (error) {
                if (current()) say(error.message);
            } finally {
                find.disabled = false;
                find.removeAttribute('aria-busy');
            }
        });

        upload.addEventListener('change', async () => {
            const [file] = upload.files || [];
            upload.value = '';
            if (!file) return;
            if (file.size > 5 * 1024 * 1024) { say('The file is larger than 5 MiB.'); return; }
            await choose((context, base, control) => sb.prepareFile(context, id, base, file, control), file.name);
        });
    }

    function shell(title) {
        const previous = document.activeElement;
        const status = sb.element('p', {role: 'status', 'aria-live': 'polite', className: 'monster-statblock-dialog-status'});
        const body = sb.element('div', {className: 'monster-statblock-dialog-body'});
        const actions = sb.element('div', {className: 'monster-statblock-dialog-actions'});
        const dialog = sb.element('dialog', {className: 'monster-statblock-dialog', 'aria-label': title},
            [sb.element('h2', {text: title}), status, body, actions]);
        document.body.append(dialog);
        dialog.showModal();
        const close = () => { if (dialog.open) dialog.close(); dialog.remove(); previous?.focus?.(); };
        return {dialog, status, body, actions, close};
    }

    function viewer(title, note, fill) {
        const view = shell(title);
        view.status.textContent = note;
        const area = sb.element('div', {className: 'monster-statblock-preview', tabindex: '0', 'aria-label': 'Statblock'});
        if (window.ScryingStatblock) fill(area);
        view.body.append(area);
        const close = sb.element('button', {type: 'button', text: 'Close'});
        close.addEventListener('click', view.close);
        view.dialog.addEventListener('cancel', event => { event.preventDefault(); view.close(); });
        view.actions.append(close);
        close.focus();
    }

    function pick(species, candidates, notes) {
        return new Promise(resolve => {
            const view = shell(`Choose a statblock for ${species}`);
            view.status.textContent = notes.join(' ') || 'Choose one source. Nothing is saved until you save the monster.';
            const list = sb.element('div', {role: 'group', 'aria-label': 'Statblock sources', className: 'monster-statblock-candidates'});
            let done = false;
            const finish = value => { if (done) return; done = true; view.close(); resolve(value); };
            const option = (candidate, grouped) => {
                const button = sb.element('button', {type: 'button', text: sb.candidateLabel(candidate, {grouped})});
                button.addEventListener('click', () => finish(candidate));
                return button;
            };
            for (const {candidate, versions} of sb.groupCandidates(candidates)) {
                list.append(option(candidate, false));
                if (!versions.length) continue;
                // SG-TODO-033: a base creature's 5e.tools versions, in a sub-list under it.
                const group = sb.element('details', {className: 'monster-statblock-versions'});
                group.append(sb.element('summary', {text: `${versions.length} version(s) of ${candidate.name || candidate.label}`}),
                    sb.element('div', {role: 'group', 'aria-label': `Versions of ${candidate.name || candidate.label}`},
                        versions.map(version => option(version, true))));
                list.append(group);
            }
            const cancel = sb.element('button', {type: 'button', text: 'Cancel'});
            cancel.addEventListener('click', () => finish(null));
            view.dialog.addEventListener('cancel', event => { event.preventDefault(); finish(null); });
            view.body.append(list);
            view.actions.append(cancel);
            list.querySelector('button')?.focus();
        });
    }

    function chooser(label, control) {
        const view = shell(`Statblock: ${label}`);
        const cancel = sb.element('button', {type: 'button', text: 'Cancel'});
        let resolveReview = null;
        const stop = () => {
            control.cancelled = true;
            if (resolveReview) resolveReview(false);
            view.close();
        };
        cancel.addEventListener('click', stop);
        view.dialog.addEventListener('cancel', event => { event.preventDefault(); stop(); });
        view.actions.append(cancel);
        cancel.focus();
        return {
            say(message, failed) {
                view.status.textContent = message;
                if (failed) cancel.textContent = 'Close';
            },
            close: () => view.close(),
            review(job, live) {
                return new Promise(resolve => {
                    resolveReview = value => { resolveReview = null; view.close(); resolve(value); };
                    view.status.textContent = job.completeness === 'partial'
                        ? 'Preview — partial: some source content could not be resolved.' : 'Preview. Nothing is saved yet.';
                    const area = sb.element('div', {className: 'monster-statblock-preview', tabindex: '0',
                        'aria-label': 'Statblock preview'});
                    sb.preview(area, job, live);
                    view.body.append(area);
                    const use = sb.element('button', {type: 'button', text: 'Use this statblock'});
                    use.addEventListener('click', () => resolveReview(true));
                    view.actions.prepend(use);
                    use.focus();
                });
            },
        };
    }
})();
