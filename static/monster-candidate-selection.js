/* Extend only the existing stats request, retaining its overwrite/edit guards. */
(() => {
    'use strict';
    const originalRequest = request;
    const form = document.querySelector('#monsterForm');
    const speciesInput = document.querySelector('#monsterSpecies');
    const overwrite = document.querySelector('#monsterSpeciesLookupOverwrite');
    const bonusInput = document.querySelector('#monsterInitiativeBonus');
    if (!form || !speciesInput) return;
    const label = overwrite?.closest('label')?.querySelector('span');
    if (label) label.textContent = 'Overwrite AC, HP range and initiative bonus with source values. Missing initiative bonus defaults to 0.';
    let selected = null;
    let appliedOffer = null;
    let cancelPopup = null;
    let generation = 0;
    let pending = 0;
    const pendingSubmitSpec = {region: 'monsters', operation: 'monster.lookup.pending-submit',
        target: 'monster-form', label: 'Finish monster lookup'};
    let pendingSubmitGuard = null;
    function blockPendingSubmit() {
        const feedback = window.scryingAdminFeedback;
        pendingSubmitGuard = feedback.begin({...pendingSubmitSpec, operation: 'monster.lookup.pending-submit.guard'});
        feedback.publish(feedback.begin(pendingSubmitSpec), {severity: 'error',
            text: 'Finish or cancel the monster lookup before adding.'});
    }
    function settlePendingSubmit() {
        const feedback = window.scryingAdminFeedback;
        if (pending === 0 && pendingSubmitGuard && feedback.isCurrent(pendingSubmitGuard)) {
            feedback.resolve(feedback.begin(pendingSubmitSpec));
            feedback.resolve(pendingSubmitGuard);
            pendingSubmitGuard = null;
        }
    }
    let bonusRevision = 0;
    function clearAppliedOffer() {
        appliedOffer = null;
    }
    function bonusEdited() {
        bonusRevision++;
        clearAppliedOffer();
    }
    bonusInput?.addEventListener('input', bonusEdited);
    bonusInput?.addEventListener('change', bonusEdited);
    const bonusHelp = document.querySelector('#monsterInitiativeBonusHelp');
    if (bonusHelp) {
        bonusHelp.append(' The overwrite option above also applies to available source initiative bonuses. ' +
            'Blank bonuses are filled automatically; existing values are replaced only when overwrite is enabled. ' +
            'Missing bonuses default to 0 when overwrite is enabled. ' +
            'Invalid source bonuses and values edited during lookup are kept unchanged.');
    }
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
            blockPendingSubmit();
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
                if (typeof candidate.attribution === 'string' && candidate.attribution) {
                    const credit = document.createElement('small');
                    credit.className = 'monster-candidate-attribution';
                    credit.textContent = ` ${candidate.attribution}`;
                    row.append(credit);
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
    request = async function(url, options = {}, ...extra) {
        const prefix = '/api/dndbeyond/monster-stats?species=';
        if (typeof url !== 'string' || !url.startsWith(prefix)) return originalRequest(url, options, ...extra);
        const species = new URLSearchParams(url.split('?')[1]).get('species');
        const current = ++generation;
        const requestId = monsterSpeciesLookupRequest;
        const originalBonus = bonusInput?.value;
        const originalBonusRevision = bonusRevision;
        const overwriteBonus = Boolean(overwrite?.checked);
        selected = null;
        clearAppliedOffer();
        publishSelection();
        if (cancelPopup) cancelPopup();
        const scopeGuard = window.scryingAdminFeedback.begin({region: 'monsters',
            operation: 'monster.candidate.lookup', target: 'monster-form', label: 'Select monster source'});
        const isCurrent = () => window.scryingAdminFeedback.isCurrent(scopeGuard) &&
            current === generation && requestId === monsterSpeciesLookupRequest &&
            speciesInput.value.trim() === species && Boolean(overwrite?.checked) === overwriteBonus;
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
            const bonusUnchanged = bonusInput && bonusInput.value === originalBonus &&
                bonusRevision === originalBonusRevision;
            if (bonusUnchanged && offerAvailable(candidate) &&
                    (overwriteBonus || !bonusInput.value.trim())) {
                const value = String(candidate.initiative_bonus);
                bonusInput.value = value;
                // Clear old attribution before binding this exact offer after application events.
                bonusInput.dispatchEvent(new Event('input', {bubbles: true}));
                bonusInput.dispatchEvent(new Event('change', {bubbles: true}));
                if (!isCurrent()) return {found: false, reason: 'Lookup superseded.'};
                if (bonusInput.value === value && signedOfferAvailable(candidate)) {
                    appliedOffer = {token: candidate.initiative_bonus_offer_token,
                        selectionToken: candidate.selection_token, species, value};
                }
            } else if (bonusUnchanged && overwriteBonus &&
                    candidate.initiative_bonus_status === 'missing' && candidate.initiative_bonus == null) {
                // Blank submits through the existing default-zero path, never as source-backed zero.
                bonusInput.value = '';
                bonusInput.dispatchEvent(new Event('input', {bubbles: true}));
                bonusInput.dispatchEvent(new Event('change', {bubbles: true}));
                if (!isCurrent()) return {found: false, reason: 'Lookup superseded.'};
            }
            selected = candidate;
            publishSelection();
            return candidate;
        } finally {
            pending--;
            settlePendingSubmit();
            window.scryingAdminFeedback.resolve(scopeGuard);
        }
    };
})();
