/* Extend only the existing stats request, retaining its overwrite/edit guards. */
(() => {
    'use strict';
    const originalRequest = request;
    const form = document.querySelector('#monsterForm');
    const speciesInput = document.querySelector('#monsterSpecies');
    const overwrite = document.querySelector('#monsterSpeciesLookupOverwrite');
    const bonusInput = document.querySelector('#monsterInitiativeBonus');
    if (!form || !speciesInput) return;
    let selected = null;
    let appliedOffer = null;
    let cancelPopup = null;
    let generation = 0;
    let pending = 0;
    function clearAppliedOffer() {
        appliedOffer = null;
    }
    bonusInput?.addEventListener('input', clearAppliedOffer);
    bonusInput?.addEventListener('change', clearAppliedOffer);
    function publishSelection() {
        document.dispatchEvent(new CustomEvent('scrying:monster-selection', {
            detail: selected ? {species: selected.species, provider: selected.provider,
                image_url: selected.image_url || null} : null
        }));
    }
    function invalidate() {
        generation++;
        selected = null;
        clearAppliedOffer();
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
        const currentSelection = selected && selected.species === speciesInput.value.trim();
        event.formData.set('selection_token', currentSelection ? selected.selection_token : 'manual');
        event.formData.delete('initiative_bonus_offer_token');
        if (currentSelection && appliedOffer &&
                appliedOffer.selectionToken === selected.selection_token &&
                appliedOffer.species === speciesInput.value.trim() &&
                bonusInput?.value === appliedOffer.value) {
            event.formData.set('initiative_bonus_offer_token', appliedOffer.token);
        }
    });
    function offerAvailable(candidate) {
        return candidate.initiative_bonus_status === 'available' &&
            Number.isSafeInteger(candidate.initiative_bonus);
    }
    function signedOfferAvailable(candidate) {
        return offerAvailable(candidate) &&
            typeof candidate.initiative_bonus_offer_token === 'string' &&
            candidate.initiative_bonus_offer_token.length > 0 &&
            candidate.initiative_bonus_offer_token.length <= 8192;
    }
    function offerText(candidate) {
        if (offerAvailable(candidate)) {
            const value = candidate.initiative_bonus;
            return `Initiative bonus ${value >= 0 ? '+' : ''}${value}`;
        }
        return `Initiative bonus unavailable: ${candidate.initiative_bonus_reason ||
            'No supported explicit source modifier.'}`;
    }
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
                    `AC ${candidate.ac ?? '—'}, HP ${candidate.hp ?? '—'} — ${offerText(candidate)}`;
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
    function reviewOffer(candidate) {
        return new Promise(resolve => {
            const previousFocus = document.activeElement;
            const dialog = document.createElement('dialog');
            dialog.setAttribute('aria-label', 'Review monster initiative bonus');
            dialog.style.maxWidth = 'min(40rem, 90vw)';
            const heading = document.createElement('h2');
            heading.textContent = 'Review initiative bonus';
            const summary = document.createElement('p');
            summary.textContent = `${candidate.name || candidate.species} — ` +
                `${monsterSourceLabel(candidate, true)} — ${offerText(candidate)}`;
            const explanation = document.createElement('p');
            explanation.textContent = 'Nothing is assigned by opening this review. ' +
                (signedOfferAvailable(candidate)
                    ? 'Copying retains a signed source offer for server validation when you add the monster. ' +
                      'Editing the bonus or changing selection clears source attribution. '
                    : 'Copying sets an editable manual value; no signed source offer is available. ') +
                'This does not create a monster. The Armor Class/HP overwrite option does not apply to this bonus.';
            const current = document.createElement('p');
            current.textContent = `Current creation bonus: ${bonusInput?.value || 'blank (default 0)'}.`;
            dialog.append(heading, summary, explanation, current);
            if (candidate.initiative_bonus_evidence) {
                const evidence = document.createElement('p');
                evidence.textContent = `Source excerpt: ${candidate.initiative_bonus_evidence}`;
                dialog.append(evidence);
            }
            let finished = false;
            function finish(decision) {
                if (finished) return;
                finished = true;
                cancelPopup = null;
                dialog.close();
                dialog.remove();
                previousFocus?.focus();
                resolve(decision);
            }
            const apply = document.createElement('button');
            apply.type = 'button';
            apply.textContent = 'Copy offered bonus to creation form';
            apply.disabled = !bonusInput || !offerAvailable(candidate);
            apply.addEventListener('click', () => finish('apply'));
            const keep = document.createElement('button');
            keep.type = 'button';
            keep.textContent = 'Keep current bonus and use candidate';
            keep.addEventListener('click', () => finish('keep'));
            const cancel = document.createElement('button');
            cancel.type = 'button';
            cancel.textContent = 'Cancel selection';
            cancel.addEventListener('click', () => finish('cancel'));
            dialog.addEventListener('cancel', event => {event.preventDefault(); finish('cancel');});
            dialog.append(apply, keep, cancel);
            document.body.append(dialog);
            cancelPopup = () => finish('cancel');
            dialog.showModal();
            keep.focus();
        });
    }
    request = async function(url, options = {}) {
        const prefix = '/api/dndbeyond/monster-stats?species=';
        if (typeof url !== 'string' || !url.startsWith(prefix)) return originalRequest(url, options);
        const species = new URLSearchParams(url.split('?')[1]).get('species');
        const current = ++generation;
        const requestId = monsterSpeciesLookupRequest;
        selected = null;
        clearAppliedOffer();
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
            const previousBonus = bonusInput?.value;
            const decision = await reviewOffer(candidate);
            if (!isCurrent()) return {found: false, reason: 'Lookup superseded.'};
            if (decision === 'cancel') return {found: false,
                reason: 'Monster selection cancelled; manual entry remains available.'};
            if (decision === 'apply' && bonusInput && offerAvailable(candidate)) {
                if (bonusInput.value === previousBonus) {
                    bonusInput.value = String(candidate.initiative_bonus);
                    bonusInput.dispatchEvent(new Event('input', {bubbles: true}));
                    bonusInput.dispatchEvent(new Event('change', {bubbles: true}));
                    if (signedOfferAvailable(candidate)) {
                        appliedOffer = {token: candidate.initiative_bonus_offer_token,
                            selectionToken: candidate.selection_token, species,
                            value: bonusInput.value};
                    }
                } else {
                    paneNotification('monsters', 'Bonus changed during review; your current value was kept.');
                }
            }
            selected = candidate;
            publishSelection();
            return candidate;
        } finally {
            pending--;
        }
    };
})();
