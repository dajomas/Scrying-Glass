/* Choose a monster image from the configured monster sources (Edit modal and bulk action). */
(() => {
    'use strict';
    const BULK_ACTION = 'select-source-image';
    const label = candidate => (typeof monsterSourceLabel === 'function'
        ? monsterSourceLabel(candidate, true) : candidate.provider || 'Source');
    const hasImage = candidate => typeof candidate?.image_url === 'string' &&
        candidate.image_url.startsWith('https://') && typeof candidate.selection_token === 'string';

    async function sourceImages(speciesList) {
        // One lookup per species; candidates without an https image are skipped, duplicates merged.
        const found = [];
        const seen = new Set();
        const reasons = [];
        for (const species of speciesList) {
            const result = await request(`/api/monsters/lookup?species=${encodeURIComponent(species)}`);
            if (!result || result.status !== 'ok') {
                reasons.push(result?.reason || `Lookup failed for ${species}.`);
                continue;
            }
            for (const candidate of result.candidates || []) {
                if (!hasImage(candidate) || seen.has(candidate.image_url)) continue;
                seen.add(candidate.image_url);
                found.push({candidate, species,
                    caption: speciesList.length > 1 ? `${species}: ${label(candidate)}` : label(candidate)});
            }
        }
        return {found, reasons};
    }

    function choose(title, options) {
        // Resolves with the chosen {candidate, species} or null on Cancel/Escape.
        return new Promise(resolve => {
            const previousFocus = document.activeElement;
            const dialog = document.createElement('dialog');
            dialog.className = 'monster-image-choice monster-source-image-choice';
            dialog.setAttribute('aria-label', title);
            dialog.style.maxWidth = 'min(48rem, 90vw)';
            const heading = document.createElement('h2');
            heading.textContent = title;
            const intro = document.createElement('p');
            intro.textContent = 'Choose an image found in the monster sources, or cancel to keep the current image.';
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
            for (const option of options) {
                const tile = document.createElement('button');
                tile.type = 'button';
                tile.className = 'monster-image-option';
                tile.style.cssText = 'display:grid;gap:.25rem;justify-items:center;width:10rem;padding:.4rem;';
                const thumb = document.createElement('img');
                thumb.src = option.candidate.image_url;
                thumb.alt = '';
                thumb.loading = 'lazy';
                thumb.referrerPolicy = 'no-referrer';
                thumb.style.cssText = 'width:8rem;height:8rem;object-fit:contain;';
                const caption = document.createElement('span');
                caption.textContent = option.caption;
                caption.style.fontSize = '.8rem';
                tile.setAttribute('aria-label', `Use image: ${option.caption}`);
                tile.append(thumb, caption);
                tile.addEventListener('click', () => finish(option));
                grid.append(tile);
            }
            const cancel = document.createElement('button');
            cancel.type = 'button';
            cancel.textContent = 'Cancel';
            cancel.title = 'Keep the current image';
            cancel.addEventListener('click', () => finish(null));
            dialog.addEventListener('cancel', event => { event.preventDefault(); finish(null); });
            dialog.append(heading, intro, grid, cancel);
            document.body.append(dialog);
            dialog.showModal();
        });
    }

    // Edit modal: a button next to "Replace image"; the choice is saved with Save monster.
    const previousOpen = openEdit;
    openEdit = function(kind, id, ...rest) {
        const result = previousOpen.call(this, kind, id, ...rest);
        if (kind === 'monsters') addEditButton(id);
        return result;
    };

    function addEditButton(id) {
        const form = document.querySelector('#editForm');
        const file = form?.elements?.image;
        if (!file || form.querySelector('.monster-source-image-edit')) return;
        const session = editing;
        const wrapper = document.createElement('div');
        wrapper.className = 'monster-source-image-edit';
        const pick = document.createElement('button');
        pick.type = 'button';
        pick.textContent = 'Select image from sources';
        const status = document.createElement('span');
        status.className = 'monster-source-image-status';
        status.setAttribute('aria-live', 'polite');
        status.style.marginInlineStart = '.5rem';
        const token = Object.assign(document.createElement('input'),
            {type: 'hidden', name: 'image_selection_token'});
        const species = Object.assign(document.createElement('input'),
            {type: 'hidden', name: 'image_species'});
        wrapper.append(pick, status, token, species);
        file.closest('label').after(wrapper);
        file.addEventListener('change', () => {
            // An uploaded file replaces a source choice.
            if (file.files?.length) {
                token.value = '';
                species.value = '';
                status.textContent = '';
            }
        });
        pick.addEventListener('click', async () => {
            const name = form.elements.monster_species?.value.trim();
            if (!name) {
                status.textContent = 'Enter the monster species first.';
                return;
            }
            pick.disabled = true;
            status.textContent = `Looking up images for ${name}…`;
            try {
                const {found, reasons} = await sourceImages([name]);
                if (editing !== session || editModal.hidden) return;
                if (!found.length) {
                    status.textContent = reasons[0] || `No source images found for ${name}.`;
                    return;
                }
                status.textContent = '';
                const choice = await choose('Select monster image', found);
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
                status.textContent = `Selected: ${choice.caption}. Save to apply.`;
            } catch (error) {
                if (editing === session) status.textContent = error.message;
            } finally {
                pick.disabled = false;
            }
        });
    }

    // Monster action dropdown: one source image for all selected monsters.
    const bulk = document.querySelector('#monsterBulkAction');
    if (!bulk) return;
    const option = document.createElement('option');
    option.value = BULK_ACTION;
    option.textContent = 'Select image from sources';
    const remove = bulk.querySelector('option[value="remove"]');
    bulk.insertBefore(option, remove || null);
    let busy = false;
    const originalBulk = runBulkAction;
    runBulkAction = async function(kind, action, ...rest) {
        if (kind !== 'monsters' || action !== BULK_ACTION) return originalBulk.call(this, kind, action, ...rest);
        if (busy) return;
        const ids = [...selectedIds('monsters')];
        const feedback = window.scryingAdminFeedback;
        const spec = {region: 'monsters', operation: 'monster.source-image',
            target: 'monster-bulk', label: 'Select image from sources'};
        const ticket = feedback.begin(spec);
        if (!ids.length) {
            feedback.publish(ticket, {severity: 'error', text: 'Select at least one monster first.'});
            return;
        }
        const monsters = (latest?.monsters || []).filter(item => ids.includes(item.id));
        const speciesList = [...new Set(monsters.map(item => (item.monster_species || '').trim()).filter(Boolean))];
        if (!speciesList.length) {
            feedback.publish(ticket, {severity: 'error', text: 'The selected monsters have no species to look up.'});
            return;
        }
        busy = true;
        try {
            feedback.publish(ticket, {severity: 'info', text: 'Looking up source images…'});
            const {found, reasons} = await sourceImages(speciesList);
            if (!found.length) {
                feedback.publish(ticket, {severity: 'error',
                    text: reasons[0] || `No source images found for ${speciesList.join(', ')}.`});
                return;
            }
            feedback.resolve(ticket);
            const count = ids.length === 1 ? '1 monster' : `${ids.length} monsters`;
            const choice = await choose(`Select image for ${count}`, found);
            if (!choice) return;
            const apply = feedback.begin(spec);
            try {
                await request('/api/monsters/source-image', {
                    method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ids, image_selection_token: choice.candidate.selection_token,
                        image_species: choice.species}),
                });
            } catch (error) {
                feedback.publish(apply, {severity: 'error', text: error.message});
                return;
            }
            try {
                await load(true);
                feedback.publish(apply, {severity: 'success', text: `Image updated for ${count}.`});
            } catch (error) {
                feedback.publish(apply, {severity: 'error',
                    text: `Image updated, but refresh failed: ${error.message}. Reload before continuing.`});
            }
        } catch (error) {
            feedback.publish(ticket, {severity: 'error', text: error.message});
        } finally {
            busy = false;
        }
    };
})();
