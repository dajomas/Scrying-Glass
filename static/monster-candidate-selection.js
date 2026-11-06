/* Extend only the existing stats request, retaining its overwrite/edit guards. */
(() => {
    'use strict';
    const originalRequest = request;
    const form = document.querySelector('#monsterForm');
    const speciesInput = document.querySelector('#monsterSpecies');
    const overwrite = document.querySelector('#monsterSpeciesLookupOverwrite');
    if (!form || !speciesInput) return;
    let selected = null;
    let cancelPopup = null;
    let generation = 0;
    let pending = 0;
    function publishSelection() {
        document.dispatchEvent(new CustomEvent('scrying:monster-selection', {
            detail: selected ? {species: selected.species, provider: selected.provider,
                image_url: selected.image_url || null} : null
        }));
    }
    function invalidate() {
        generation++;
        selected = null;
        publishSelection();
        if (cancelPopup) cancelPopup();
    }
    speciesInput.addEventListener('input', invalidate, true);
    overwrite?.addEventListener('change', invalidate, true);
    form.addEventListener('reset', invalidate);
    form.addEventListener('submit', event => {
        if (pending) {
            event.preventDefault();
            event.stopImmediatePropagation();
            paneNotification('monsters', 'Finish or cancel the monster lookup before adding.');
        }
    }, true);
    form.addEventListener('formdata', event => {
        event.formData.set('selection_token', selected && selected.species === speciesInput.value.trim()
            ? selected.selection_token : 'manual');
    });
    function choose(candidates) {
        return new Promise(resolve => {
            const previousFocus = document.activeElement;
            const dialog = document.createElement('dialog');
            dialog.setAttribute('aria-label', 'Select monster candidate');
            dialog.style.maxWidth = 'min(48rem, 90vw)';
            const heading = document.createElement('h2');
            heading.textContent = 'Select monster';
            let finished = false;
            function finish(candidate) {
                if (finished) return;
                finished = true;
                cancelPopup = null;
                dialog.close();
                dialog.remove();
                previousFocus?.focus();
                resolve(candidate);
            }
            dialog.append(heading);
            candidates.forEach((candidate, index) => {
                const row = document.createElement('p');
                const button = document.createElement('button');
                button.type = 'button';
                button.textContent = `${index + 1}. ${candidate.name || candidate.species} — ` +
                    `${monsterSourceLabel(candidate, true)} — ` +
                    `AC ${candidate.ac ?? '—'}, HP ${candidate.hp ?? '—'}`;
                button.addEventListener('click', () => finish(candidate));
                row.append(button);
                if (candidate.source_url && candidate.source_url.startsWith('https://')) {
                    const link = document.createElement('a');
                    link.href = candidate.source_url;
                    link.target = '_blank';
                    link.rel = 'noopener noreferrer';
                    link.textContent = ' View source';
                    row.append(link);
                }
                dialog.append(row);
            });
            const cancel = document.createElement('button');
            cancel.type = 'button';
            cancel.textContent = 'Cancel';
            cancel.addEventListener('click', () => finish(null));
            dialog.addEventListener('cancel', event => {event.preventDefault(); finish(null);});
            dialog.append(cancel);
            document.body.append(dialog);
            cancelPopup = () => finish(null);
            dialog.showModal();
        });
    }
    request = async function(url, options = {}) {
        const prefix = '/api/dndbeyond/monster-stats?species=';
        if (typeof url !== 'string' || !url.startsWith(prefix)) return originalRequest(url, options);
        const species = new URLSearchParams(url.split('?')[1]).get('species');
        const current = ++generation;
        const requestId = monsterSpeciesLookupRequest;
        selected = null;
        publishSelection();
        if (cancelPopup) cancelPopup();
        const isCurrent = () => current === generation && requestId === monsterSpeciesLookupRequest &&
            speciesInput.value.trim() === species;
        pending++;
        try {
            const result = await originalRequest(`/api/monsters/lookup?species=${encodeURIComponent(species)}`, options);
            if (!isCurrent()) return {found: false, reason: 'Lookup superseded.'};
            if (!result || result.status !== 'ok') return {found: false,
                reason: result?.reason || 'Monster lookup failed; enter stats manually.'};
            const candidates = result.candidates || [];
            if (!candidates.length) return {found: false,
                reason: `No usable monster stats found for ${species}; enter AC and HP manually.`};
            const candidate = candidates.length === 1 ? candidates[0] : await choose(candidates);
            if (!isCurrent()) return {found: false, reason: 'Lookup superseded.'};
            if (!candidate) return {found: false,
                reason: 'Monster selection cancelled; manual entry remains available.'};
            selected = candidate;
            publishSelection();
            return candidate;
        } finally {
            pending--;
        }
    };
})();
