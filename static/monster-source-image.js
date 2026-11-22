/* Choose monster images from the configured monster sources (Edit modal and bulk action). */
(() => {
    'use strict';
    const BULK_ACTION = 'select-source-image';
    const CACHE_MS = 10 * 60 * 1000; // Selection tokens stay valid for 30 minutes on the server.
    const label = candidate => (typeof monsterSourceLabel === 'function'
        ? monsterSourceLabel(candidate, true) : candidate.provider || 'Source');
    const hasImage = candidate => typeof candidate?.image_url === 'string' &&
        candidate.image_url.startsWith('https://') && typeof candidate.selection_token === 'string';

    // One lookup per species: concurrent and repeated requests share the same promise.
    const lookups = new Map();
    function speciesImages(species) {
        const key = species.trim().toLowerCase();
        const cached = lookups.get(key);
        if (cached && Date.now() - cached.at < CACHE_MS) return cached.promise;
        const promise = request(`/api/monsters/lookup?images=true&species=${encodeURIComponent(species)}`).then(result => {
            if (!result || result.status !== 'ok') {
                throw new Error(result?.reason || `Image lookup failed for ${species}.`);
            }
            const seen = new Set();
            const images = [];
            for (const candidate of result.candidates || []) {
                if (!hasImage(candidate) || seen.has(candidate.image_url)) continue;
                seen.add(candidate.image_url);
                images.push({candidate, species, caption: label(candidate)});
            }
            images.warning = typeof result.warning === 'string' ? result.warning : '';
            return images;
        });
        const entry = {at: Date.now(), promise};
        lookups.set(key, entry);
        // Failed or partial lookups are not reused, so the next attempt retries every source.
        const forget = () => { if (lookups.get(key) === entry) lookups.delete(key); };
        promise.then(images => { if (images.warning) forget(); }, forget);
        return promise;
    }

    function tile(image, caption, onPick) {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'monster-image-option';
        button.style.cssText = 'display:grid;gap:.25rem;justify-items:center;align-content:start;width:9rem;padding:.4rem;outline-offset:-3px;';
        const thumb = document.createElement('img');
        if (image) thumb.src = image;
        thumb.alt = '';
        thumb.loading = 'lazy';
        thumb.referrerPolicy = 'no-referrer';
        thumb.style.cssText = 'width:7rem;height:7rem;object-fit:contain;border-radius:.35rem;background:rgba(0,0,0,.25);';
        const text = document.createElement('span');
        text.textContent = caption;
        text.style.fontSize = '.8rem';
        button.append(thumb, text);
        button.addEventListener('click', onPick);
        return button;
    }

    function dialogShell(title) {
        const dialog = document.createElement('dialog');
        dialog.className = 'monster-image-choice monster-source-image-choice';
        dialog.setAttribute('aria-label', title);
        dialog.style.maxWidth = 'min(60rem, 92vw)';
        const heading = document.createElement('h2');
        heading.textContent = title;
        heading.style.fontFamily = 'inherit';
        const status = document.createElement('p');
        status.className = 'monster-source-image-progress';
        status.setAttribute('role', 'status');
        status.setAttribute('aria-live', 'polite');
        dialog.append(heading, status);
        return {dialog, status};
    }

    function chooseOne(title, images) {
        // Resolves with the chosen image or null on Cancel/Escape.
        return new Promise(resolve => {
            const previousFocus = document.activeElement;
            const {dialog, status} = dialogShell(title);
            status.textContent = 'Choose an image found in the monster sources, or cancel to keep the current image.';
            const grid = document.createElement('div');
            grid.style.cssText = 'display:flex;flex-wrap:wrap;gap:.75rem;margin:.75rem 0;';
            let finished = false;
            const finish = choice => {
                if (finished) return;
                finished = true;
                dialog.close();
                dialog.remove();
                previousFocus?.focus?.();
                resolve(choice);
            };
            for (const image of images) {
                const button = tile(image.candidate.image_url, image.caption, () => finish(image));
                button.setAttribute('aria-label', `Use image: ${image.caption}`);
                grid.append(button);
            }
            const cancel = document.createElement('button');
            cancel.type = 'button';
            cancel.textContent = 'Cancel';
            cancel.title = 'Keep the current image';
            cancel.addEventListener('click', () => finish(null));
            dialog.addEventListener('cancel', event => { event.preventDefault(); finish(null); });
            dialog.append(grid, cancel);
            document.body.append(dialog);
            dialog.showModal();
        });
    }

    // Edit modal: a button bottom-aligned with "Replace image"; the choice is saved with Save monster.
    const previousOpen = openEdit;
    openEdit = function(kind, id, ...rest) {
        const result = previousOpen.call(this, kind, id, ...rest);
        if (kind === 'monsters') addEditButton();
        return result;
    };

    function addEditButton() {
        const form = document.querySelector('#editForm');
        const file = form?.elements?.image;
        if (!file || form.querySelector('.monster-source-image-edit')) return;
        const session = editing;
        const fileLabel = file.closest('label');
        const wrapper = document.createElement('div');
        wrapper.className = 'monster-source-image-edit';
        wrapper.style.cssText = 'align-self:end;min-width:0;';
        const pick = document.createElement('button');
        pick.type = 'button';
        pick.textContent = 'Select image from sources';
        const token = Object.assign(document.createElement('input'),
            {type: 'hidden', name: 'image_selection_token'});
        const species = Object.assign(document.createElement('input'),
            {type: 'hidden', name: 'image_species'});
        wrapper.append(pick, token, species);
        // The status is its own grid item in the next row, under the button.
        const status = document.createElement('p');
        status.className = 'monster-source-image-status';
        status.setAttribute('role', 'status');
        status.setAttribute('aria-live', 'polite');
        status.style.cssText = 'margin:0;font-size:.9rem;';
        status.hidden = true;
        fileLabel.after(wrapper, status);
        status.style.gridColumn = wrapper.offsetLeft > fileLabel.offsetLeft ? '2' : '1 / -1';
        const say = text => { status.textContent = text; status.hidden = !text; };
        file.addEventListener('change', () => {
            // An uploaded file replaces a source choice.
            if (file.files?.length) {
                token.value = '';
                species.value = '';
                say('');
            }
        });
        pick.addEventListener('click', async () => {
            const name = form.elements.monster_species?.value.trim();
            if (!name) {
                say('Enter the monster species first.');
                return;
            }
            pick.disabled = true;
            pick.setAttribute('aria-busy', 'true');
            say(`Looking up images for ${name}…`);
            try {
                const images = await speciesImages(name);
                if (editing !== session || editModal.hidden) return;
                if (!images.length) {
                    say(`No source images found for ${name}.${images.warning ? ` ${images.warning}` : ''}`);
                    return;
                }
                say(images.warning);
                const choice = await chooseOne('Select monster image', images);
                if (!choice || editing !== session || editModal.hidden) return;
                token.value = choice.candidate.selection_token;
                species.value = choice.species;
                file.value = '';
                let preview = form.querySelector('.monster-edit-image-preview');
                if (!preview) {
                    const box = document.createElement('div');
                    box.className = 'monster-edit-image full';
                    preview = document.createElement('img');
                    preview.className = 'monster-edit-image-preview';
                    box.append(preview);
                    form.prepend(box);
                }
                preview.src = choice.candidate.image_url;
                preview.alt = `Selected source image: ${choice.caption}`;
                say(`Selected: ${choice.caption}. Save to apply.`);
            } catch (error) {
                if (editing === session) say(error.message);
            } finally {
                pick.disabled = false;
                pick.removeAttribute('aria-busy');
            }
        });
    }

    // Monster action dropdown: one row per selected monster, one image choice per monster.
    const bulk = document.querySelector('#monsterBulkAction');
    if (!bulk) return;
    const option = document.createElement('option');
    option.value = BULK_ACTION;
    option.textContent = 'Select image from sources';
    bulk.insertBefore(option, bulk.querySelector('option[value="refresh-source-review"], option[value="remove"]') || null);
    let open = false;
    const originalBulk = runBulkAction;
    runBulkAction = async function(kind, action, ...rest) {
        if (kind !== 'monsters' || action !== BULK_ACTION) return originalBulk.call(this, kind, action, ...rest);
        const feedback = window.scryingAdminFeedback;
        const spec = {region: 'monsters', operation: 'monster.source-image',
            target: 'monster-bulk', label: 'Select image from sources'};
        const ids = [...selectedIds('monsters')];
        const monsters = (latest?.monsters || []).filter(item => ids.includes(item.id));
        if (!monsters.length) {
            feedback.publish(feedback.begin(spec), {severity: 'error', text: 'Select at least one monster first.'});
            return;
        }
        if (open) return;
        open = true;
        try {
            const choices = await chooseRows(monsters);
            if (!choices || !choices.length) return;
            const count = choices.length === 1 ? '1 monster' : `${choices.length} monsters`;
            const ticket = feedback.begin(spec);
            try {
                await request('/api/monsters/source-image', {
                    method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({items: choices}),
                });
            } catch (error) {
                feedback.publish(ticket, {severity: 'error', text: error.message});
                return;
            }
            try {
                await load(true);
                feedback.publish(ticket, {severity: 'success', text: `Image updated for ${count}.`});
            } catch (error) {
                feedback.publish(ticket, {severity: 'error',
                    text: `Images updated, but refresh failed: ${error.message}. Reload before continuing.`});
            }
        } finally {
            open = false;
        }
    };

    function chooseRows(monsters) {
        // Resolves with [{id, image_selection_token, image_species}] for changed rows, or null on Cancel.
        return new Promise(resolve => {
            const previousFocus = document.activeElement;
            const title = monsters.length === 1 ? 'Select image for 1 monster'
                : `Select images for ${monsters.length} monsters`;
            const {dialog, status} = dialogShell(title);
            const help = document.createElement('p');
            help.textContent = 'Choose an image per monster. Monsters left on "Keep current" are not changed.';
            const rows = document.createElement('div');
            rows.style.cssText = 'display:grid;gap:1rem;margin:.75rem 0;max-height:60vh;overflow:auto;';
            const chosen = new Map();
            const actions = document.createElement('div');
            actions.style.cssText = 'display:flex;gap:.5rem;';
            const apply = document.createElement('button');
            apply.type = 'button';
            apply.textContent = 'Apply images';
            apply.disabled = true;
            const cancel = document.createElement('button');
            cancel.type = 'button';
            cancel.textContent = 'Cancel';
            actions.append(apply, cancel);
            dialog.append(help, rows, actions);
            let finished = false;
            const finish = value => {
                if (finished) return;
                finished = true;
                dialog.close();
                dialog.remove();
                previousFocus?.focus?.();
                resolve(value);
            };
            const syncApply = () => {
                apply.disabled = chosen.size === 0;
                apply.textContent = chosen.size ? `Apply images (${chosen.size})` : 'Apply images';
            };
            const rowFor = new Map();
            for (const monster of monsters) {
                const row = document.createElement('section');
                row.className = 'monster-source-image-row';
                row.dataset.monsterId = monster.id;
                row.style.cssText = 'margin:0;padding:.6rem .75rem;min-height:0;';
                const heading = document.createElement('h3');
                heading.style.cssText = 'margin:0 0 .4rem;font-size:1rem;';
                heading.textContent = `${monster.name || monster.id}${monster.monster_species ? ` (${monster.monster_species})` : ''}`;
                const grid = document.createElement('div');
                grid.setAttribute('role', 'group');
                grid.setAttribute('aria-label', `Images for ${monster.name || monster.id}`);
                grid.style.cssText = 'display:flex;flex-wrap:wrap;gap:.5rem;align-items:flex-start;';
                const note = document.createElement('p');
                note.className = 'monster-source-image-row-status';
                note.style.cssText = 'margin:.4rem 0 0;font-size:.85rem;opacity:.8;';
                const species = (monster.monster_species || '').trim();
                note.textContent = species ? `Looking up images for ${species}…` : 'No species to look up.';
                row.append(heading, grid, note);
                rows.append(row);
                rowFor.set(monster.id, {monster, grid, note});
                const keep = tile(monster.image_url || '', monster.image_url ? 'Keep current' : 'Keep current (no image)', () => select(monster.id, null, keep));
                keep.setAttribute('aria-label', `Keep current image: ${monster.name || monster.id}`);
                keep.setAttribute('aria-pressed', 'true');
                keep.style.outline = '3px solid currentColor';
                grid.append(keep);
            }
            function select(id, image, button) {
                const {grid} = rowFor.get(id);
                for (const other of grid.querySelectorAll('.monster-image-option')) {
                    const on = other === button;
                    other.setAttribute('aria-pressed', on ? 'true' : 'false');
                    other.style.outline = on ? '3px solid currentColor' : '';
                }
                if (image) {
                    chosen.set(id, {id, image_selection_token: image.candidate.selection_token,
                        image_species: image.species});
                } else {
                    chosen.delete(id);
                }
                syncApply();
            }
            const speciesList = [...new Set(monsters.map(m => (m.monster_species || '').trim()).filter(Boolean))];
            let done = 0;
            const progress = () => {
                status.textContent = done < speciesList.length
                    ? `Looking up images… ${done} of ${speciesList.length} species done.`
                    : `Image lookup finished for ${speciesList.length} species.`;
                dialog.setAttribute('aria-busy', done < speciesList.length ? 'true' : 'false');
            };
            progress();
            // One lookup per species, run one after another; each species fills all of its rows.
            (async () => {
                for (const species of speciesList) {
                    let images = null;
                    let failure = '';
                    try {
                        images = await speciesImages(species);
                    } catch (error) {
                        failure = error.message;
                    }
                    if (finished) return;
                    done++;
                    for (const {monster, grid, note} of rowFor.values()) {
                        if ((monster.monster_species || '').trim() !== species) continue;
                        if (failure) {
                            note.textContent = failure;
                            continue;
                        }
                        note.textContent = [images.length ? '' : `No source images found for ${species}.`,
                            images.warning].filter(Boolean).join(' ');
                        note.hidden = !note.textContent;
                        for (const image of images) {
                            const button = tile(image.candidate.image_url, image.caption,
                                () => select(monster.id, image, button));
                            button.setAttribute('aria-label', `Use image for ${monster.name || monster.id}: ${image.caption}`);
                            button.setAttribute('aria-pressed', 'false');
                            grid.append(button);
                        }
                    }
                    progress();
                }
            })();
            apply.addEventListener('click', () => finish([...chosen.values()]));
            cancel.addEventListener('click', () => finish(null));
            dialog.addEventListener('cancel', event => { event.preventDefault(); finish(null); });
            document.body.append(dialog);
            dialog.showModal();
        });
    }
})();
