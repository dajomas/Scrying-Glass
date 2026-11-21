/* Selected-monster bulk statblock loading (SG-TODO-022.14).
 *
 * "Load statblocks" in the monster Bulk dropdown opens one row per selected
 * monster. Each row has its own choice: Keep current (default), a discovered
 * candidate (original tracker source first) or a .monster file. Discovery runs
 * in batches of 50 with one lookup per species; preparations are submitted one
 * after another as capacity allows (at most two at a time from this dialog), and
 * rows show not-submitted, preparing, ready or failed states. Apply sends the
 * ready rows in atomic batches of at most 50; each batch has its own operation
 * ID, so a retry never applies twice, and a later failed batch does not undo
 * earlier ones. Cancel stops all unfinished preparations; nothing is saved.
 */
(() => {
    'use strict';
    const sb = window.scryingStatblockImport;
    const bulk = document.querySelector('#monsterBulkAction');
    if (!sb || !bulk || typeof runBulkAction !== 'function') return;
    const ACTION = 'load-statblocks';
    const BATCH = 50;
    const PARALLEL = 2;
    const option = sb.element('option', {value: ACTION, text: 'Load statblocks'});
    bulk.insertBefore(option, bulk.querySelector('option[value="refresh-source-review"], option[value="remove"]') || null);
    let open = false;

    const original = runBulkAction;
    runBulkAction = async function(kind, action, ...rest) {
        if (kind !== 'monsters' || action !== ACTION) return original.call(this, kind, action, ...rest);
        const feedback = window.scryingAdminFeedback;
        const spec = {region: 'monsters', operation: 'monster.statblocks', target: 'monster-bulk', label: 'Load statblocks'};
        const ids = [...selectedIds('monsters')];
        const monsters = (latest?.monsters || []).filter(item => ids.includes(item.id));
        if (!monsters.length) {
            feedback.publish(feedback.begin(spec), {severity: 'error', text: 'Select at least one monster first.'});
            return;
        }
        if (open) return;
        open = true;
        try {
            const outcome = await dialog(monsters);
            if (!outcome || !outcome.applied) return;
            const ticket = feedback.begin(spec);
            try { await load(true); } catch (error) { /* reported below */ }
            const text = `Statblocks saved for ${outcome.applied} monster(s).` +
                (outcome.failed ? ` ${outcome.failed} could not be saved.` : '');
            feedback.publish(ticket, {severity: outcome.failed ? 'error' : 'success', text});
        } finally {
            open = false;
        }
    };

    function dialog(monsters) {
        return new Promise(resolve => {
            const previous = document.activeElement;
            const title = `Load statblocks for ${monsters.length === 1 ? '1 monster' : `${monsters.length} monsters`}`;
            const status = sb.element('p', {role: 'status', 'aria-live': 'polite', className: 'monster-statblock-dialog-status'});
            const help = sb.element('p', {text: 'Choose a statblock per monster. Rows left on "Keep current" are not changed. ' +
                'Nothing is saved until you apply.'});
            const list = sb.element('div', {className: 'monster-statblock-rows'});
            const apply = sb.element('button', {type: 'button', text: 'Apply statblocks', disabled: true});
            const cancel = sb.element('button', {type: 'button', text: 'Cancel'});
            const box = sb.element('dialog', {className: 'monster-statblock-dialog monster-statblock-bulk', 'aria-label': title},
                [sb.element('h2', {text: title}), status, help, list,
                 sb.element('div', {className: 'monster-statblock-dialog-actions'}, [apply, cancel])]);
            const rows = new Map();
            let context = null, finished = false, applying = false, applied = 0, failed = 0, active = 0;
            const queue = [];

            for (const monster of monsters) {
                const select = sb.element('select', {'aria-label': `Statblock for ${monster.name || monster.id}`, disabled: true});
                select.append(sb.element('option', {value: 'keep', text: 'Keep current'}));
                const file = sb.element('input', {type: 'file', accept: '.monster,application/json', hidden: true,
                    'aria-label': `.monster file for ${monster.name || monster.id}`});
                const note = sb.element('p', {className: 'monster-statblock-row-status', text: 'Waiting for the source search…'});
                const retry = sb.element('button', {type: 'button', text: 'Retry', hidden: true,
                    'aria-label': `Retry ${monster.name || monster.id}`});
                const preview = sb.element('details', {className: 'monster-statblock-row-preview', hidden: true},
                    [sb.element('summary', {text: 'Preview'})]);
                const section = sb.element('section', {className: 'monster-statblock-row', 'data-monster-id': monster.id}, [
                    sb.element('h3', {text: `${monster.name || monster.id}${monster.monster_species ? ` (${monster.monster_species})` : ''}`}),
                    sb.element('div', {className: 'monster-statblock-row-controls'}, [select, file, retry]), note, preview]);
                list.append(section);
                const row = {monster, select, file, retry, note, preview, section, state: 'keep', job: null, control: null,
                    candidates: new Map(), revision: 0, notes: []};
                rows.set(monster.id, row);
                select.addEventListener('change', () => change(row));
                retry.addEventListener('click', async () => {
                    // A rejected or failed row is prepared again against the current saved revision.
                    if (!row.source || applying) return;
                    try {
                        const current = await sb.state();
                        const saved = current.monsters.find(entry => entry.monster_id === monster.id);
                        row.revision = saved ? saved.statblock_revision : 0;
                    } catch (error) { /* keep the known revision; preparation reports problems */ }
                    enqueue(row, row.source);
                });
                file.addEventListener('change', () => {
                    const [chosen] = file.files || [];
                    if (chosen) enqueue(row, {file: chosen});
                });
            }

            const say = text => { status.textContent = text; };
            const counts = () => {
                const all = [...rows.values()];
                return {waiting: all.filter(r => r.state === 'waiting').length, preparing: all.filter(r => r.state === 'preparing').length,
                        ready: all.filter(r => r.state === 'ready').length};
            };
            function sync() {
                const {waiting, preparing, ready} = counts();
                apply.disabled = applying || !ready || waiting > 0 || preparing > 0;
                apply.textContent = ready ? `Apply statblocks (${ready})` : 'Apply statblocks';
                if (context && !applying) {
                    say(waiting || preparing ? `Preparing: ${preparing} running, ${waiting} not yet submitted, ${ready} ready.`
                        : ready ? `${ready} ready to apply.` : 'Choose statblocks to load.');
                }
            }
            function rowNote(row, text) {
                row.note.textContent = [text, ...row.notes].filter(Boolean).join(' ');
                row.retry.hidden = row.state !== 'failed' || !row.source;
            }

            function reset(row) {
                if (row.control) row.control.cancelled = true;
                if (row.job) sb.cancel(row.job.job_id);
                const index = queue.indexOf(row);
                if (index >= 0) queue.splice(index, 1);
                row.job = null; row.control = null;
                row.preview.hidden = true; row.preview.open = false;
                row.preview.replaceChildren(row.preview.firstChild);
            }

            function change(row) {
                reset(row);
                const value = row.select.value;
                row.file.hidden = value !== 'file';
                if (value === 'keep') { row.state = 'keep'; rowNote(row, 'Keep current.'); sync(); return; }
                if (value === 'file') { row.state = 'keep'; rowNote(row, 'Choose a .monster file.'); sync(); return; }
                enqueue(row, {candidate: row.candidates.get(value)});
            }

            function enqueue(row, source) {
                reset(row);
                row.source = source;
                row.state = 'waiting';
                rowNote(row, 'Not yet submitted.');
                queue.push(row);
                sync();
                pump();
            }

            function pump() {
                while (!finished && active < PARALLEL && queue.length) {
                    const row = queue.shift();
                    active++;
                    run(row).finally(() => { active--; pump(); sync(); });
                }
            }

            async function run(row) {
                const control = row.control = {cancelled: false,
                    onAccepted: job => { row.state = 'preparing'; rowNote(row, `Preparing (deadline ${sb.time(job.deadline)})…`); sync(); }};
                try {
                    const job = row.source.file
                        ? await sb.prepareFile(context, row.monster.id, row.revision, row.source.file, control)
                        : await sb.prepareCandidate(context, row.monster.id, row.revision, row.source.candidate.candidate_id, control);
                    if (control.cancelled || finished) { sb.cancel(job.job_id); return; }
                    row.job = job; row.state = 'ready';
                    rowNote(row, `Ready: ${job.source_label} (${job.source?.provider || 'file'})` +
                        `${job.completeness === 'partial' ? ', partial' : ''}.`);
                    row.preview.hidden = false;
                    row.preview.addEventListener('toggle', () => {
                        if (row.preview.open && row.preview.children.length === 1 && row.job === job) {
                            const area = sb.element('div', {className: 'monster-statblock-preview'});
                            sb.preview(area, job, {name: row.monster.name, species: row.monster.monster_species, ac: row.monster.ac,
                                hp: row.monster.hp, max_hp: row.monster.max_hp, initiative_bonus: row.monster.initiative_bonus});
                            row.preview.append(area);
                        }
                    });
                } catch (error) {
                    if (control.cancelled || finished || error.code === 'cancelled') return;
                    row.job = null;
                    row.state = 'failed';
                    rowNote(row, `Failed: ${error.message}${error.retryAt ? ` Retry after ${sb.time(error.retryAt)}.` : ''}`);
                } finally {
                    if (row.control === control) row.control = null;
                }
            }

            function finish(value) {
                if (finished) return;
                finished = true;
                for (const row of rows.values()) {
                    if (row.control) row.control.cancelled = true;
                    if (row.job && (!value || row.state !== 'applied')) sb.cancel(row.job.job_id);
                }
                if (box.open) box.close();
                box.remove();
                previous?.focus?.();
                resolve(value);
            }

            async function applyReady() {
                applying = true;
                failed = 0;
                sync();
                const ready = [...rows.values()].filter(row => row.state === 'ready');
                const batches = [];
                for (let index = 0; index < ready.length; index += BATCH) batches.push(ready.slice(index, index + BATCH));
                for (const [number, batch] of batches.entries()) {
                    say(batches.length > 1 ? `Applying batch ${number + 1} of ${batches.length}…` : 'Applying…');
                    batch.operation = batch.operation || sb.operationId();
                    try {
                        const result = await sb.api('/api/statblocks/apply', sb.json('POST', {operation_id: batch.operation,
                            campaign_id: context.campaign_id, encounter_token: context.encounter_token,
                            items: batch.map(row => ({monster_id: row.monster.id, expected_statblock_revision: row.revision,
                                                      selection_id: row.job.selection_id}))}));
                        for (const entry of result.applied || []) {
                            const row = rows.get(entry.monster_id);
                            row.state = 'applied';
                            rowNote(row, `Saved (revision ${entry.statblock_revision}).`);
                            row.select.disabled = true;
                            applied++;
                        }
                    } catch (error) {
                        const items = new Map((error.items || []).map(item => [item.monster_id, item.message]));
                        for (const row of batch) {
                            if (row.job) sb.cancel(row.job.job_id);
                            row.job = null;
                            row.state = 'failed';
                            rowNote(row, `Not saved: ${items.get(row.monster.id) || error.message}`);
                            failed++;
                        }
                    }
                }
                applying = false;
                failed = [...rows.values()].filter(row => row.state === 'failed').length;
                if (!failed) { finish({applied, failed}); return; }
                cancel.textContent = 'Close';
                sync();
                say(`${applied} saved; ${failed} not saved (batches are separate: saved batches stay saved). ` +
                    'Retry the failed rows or close.');
            }

            apply.addEventListener('click', () => { if (!applying) applyReady(); });
            cancel.addEventListener('click', () => finish(applied ? {applied, failed} : null));
            box.addEventListener('cancel', event => {
                if (event.target !== box) return; // a dismissed file picker's cancel event bubbles here
                event.preventDefault();
                finish(applied ? {applied, failed} : null);
            });
            document.body.append(box);
            box.showModal();
            cancel.focus();
            discoverAll();

            async function discoverAll() {
                const ids = [...rows.keys()];
                let complete = true;
                box.setAttribute('aria-busy', 'true');
                try {
                    for (let index = 0; index < ids.length; index += BATCH) {
                        const part = ids.slice(index, index + BATCH);
                        say(ids.length > BATCH ? `Searching the sources… batch ${index / BATCH + 1} of ${Math.ceil(ids.length / BATCH)}.`
                            : 'Searching the sources…');
                        const {state, result} = await sb.discover(part);
                        if (finished) return;
                        if (context && context.encounter_token !== state.encounter_token) throw new Error('The encounter changed; close and try again.');
                        context = state;
                        complete = complete && result.complete;
                        for (const found of result.monsters) fill(rows.get(found.monster_id), found, state);
                    }
                } catch (error) {
                    if (finished) return;
                    say(`Search failed: ${error.message}`);
                    for (const row of rows.values()) if (row.select.disabled) rowNote(row, 'Not searched.');
                    return;
                } finally {
                    box.setAttribute('aria-busy', 'false');
                }
                say(complete ? 'Search complete. Choose statblocks to load.'
                    : 'Search incomplete for some sources (see rows); the lists may not be exhaustive.');
            }

            function fill(row, found, state) {
                const summary = state.monsters.find(entry => entry.monster_id === row.monster.id);
                row.revision = summary ? summary.statblock_revision : 0;
                row.notes = sb.providerNotes(found);
                const option = (candidate, grouped) => {
                    row.candidates.set(candidate.candidate_id, candidate);
                    return sb.element('option', {value: candidate.candidate_id, text: sb.candidateLabel(candidate, {grouped}),
                        disabled: Boolean(candidate.disabled)});
                };
                for (const {candidate, versions} of sb.groupCandidates(found.candidates)) {
                    row.select.append(option(candidate, false));
                    // SG-TODO-033: a base creature's 5e.tools versions as an option group under it.
                    if (versions.length) row.select.append(sb.element('optgroup',
                        {label: `Versions of ${candidate.name || candidate.label}`}, versions.map(version => option(version, true))));
                }
                row.select.append(sb.element('option', {value: 'file', text: 'Upload a .monster file…'}));
                row.select.disabled = false;
                rowNote(row, `Current: ${sb.statusText(summary)}. ${found.candidates.length ? '' : 'No statblocks found.'}`);
            }
        });
    }
})();
