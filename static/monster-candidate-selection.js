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
    // Enabled lookup providers, in lookup order, for the status message and help text.
    let providers = ['D&D Beyond', '5e.tools', 'Open5e'];
    const sourcesHelp = document.querySelector('#monsterLookupSources');
    function describeProviders() {
        const names = providers.map(name => name === '5e.tools' ? 'configured 5e.tools sources' : name);
        if (sourcesHelp) sourcesHelp.textContent = !names.length ? 'no lookup sources'
            : names.length === 1 ? names[0] : `${names.slice(0, -1).join(', ')} and ${names.at(-1)}`;
    }
    function refreshProviders() {
        if (typeof fetch !== 'function') return Promise.resolve();
        // Plain fetch: a failed wording refresh must not raise Admin notifications.
        return fetch('/api/monsters/lookup-providers', {credentials: 'same-origin'})
            .then(response => response.ok ? response.json() : null).then(result => {
            if (Array.isArray(result?.providers) && result.providers.every(name => typeof name === 'string')) {
                providers = result.providers;
                describeProviders();
            }
        }).catch(() => {});
    }
    window.scryingLookupSources = {
        order: () => providers.length ? providers.join(', then ') : 'no lookup sources are enabled',
        refresh: refreshProviders,
    };
    refreshProviders();
    window.addEventListener('focus', refreshProviders);
    let selected = null;
    let imageChoice = null;   // Another found candidate whose image replaces the selected one.
    let lastLookup = null;    // {species, candidates, at} of the last multi-candidate lookup.
    let reuseLookup = null;
    const REUSE_MS = 20 * 60 * 1000;  // Signed selection tokens last 30 minutes.
    let reselectButton = null;
    function updateReselect() {
        const show = Boolean(lastLookup && lastLookup.species === speciesInput.value.trim() &&
            Date.now() - lastLookup.at < REUSE_MS);
        if (show && !reselectButton) {
            reselectButton = document.createElement('button');
            reselectButton.type = 'button';
            reselectButton.id = 'monsterSpeciesReselect';
            reselectButton.className = 'monster-species-reselect';
            reselectButton.textContent = 'Choose again';
            reselectButton.title = 'Choose again from the monsters found for this species';
            reselectButton.addEventListener('click', () => {
                if (!lastLookup || lastLookup.species !== speciesInput.value.trim()) return updateReselect();
                reuseLookup = lastLookup;
                if (typeof lookupMonsterSpeciesStats === 'function') lookupMonsterSpeciesStats();
            });
            (speciesInput.closest('label.field') || speciesInput).after(reselectButton);
        }
        if (reselectButton) reselectButton.hidden = !show;
    }
    function uploadChosen() {
        const file = document.querySelector('#monsterImage');
        return Boolean(file?.files && file.files.length);
    }
    function chooseImage(candidate, candidates, kept) {
        // Image picker lives in monster-image-choice.js (fragment size limit).
        const picker = window.scryingMonsterImageChoice;
        if (!picker) return Promise.resolve(candidate);
        const open = picker.open(candidate, candidates, other => monsterSourceLabel(other, true), kept);
        cancelPopup = open.cancel;
        return open.promise.finally(() => {
            if (cancelPopup === open.cancel) cancelPopup = null;
        });
    }
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
                image_url: (imageChoice || selected).image_url || null} : null
        }));
    }
    function invalidate() {
        generation++;
        selected = null;
        imageChoice = null;
        updateReselect();
        clearAppliedOffer();
        publishSelection();
        if (cancelPopup) cancelPopup();
    }
    speciesInput.addEventListener('input', invalidate, true);
    overwrite?.addEventListener('change', invalidate, true);
    form.addEventListener('reset', () => {
        lastLookup = null;
        invalidate();
    });
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
        event.formData.delete('image_selection_token');
        if (currentSelection && imageChoice && imageChoice !== selected &&
                typeof imageChoice.selection_token === 'string') {
            event.formData.set('image_selection_token', imageChoice.selection_token);
        }
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
            // Keep provider order; within a provider, sort rows by book source label.
            const providerRank = new Map();
            candidates.forEach(candidate => {
                if (!providerRank.has(candidate.provider)) providerRank.set(candidate.provider, providerRank.size);
            });
            const rows = candidates.map((candidate, position) =>
                ({candidate, position, label: monsterSourceLabel(candidate, true)}));
            rows.sort((a, b) =>
                providerRank.get(a.candidate.provider) - providerRank.get(b.candidate.provider) ||
                a.label.localeCompare(b.label, undefined, {sensitivity: 'base', numeric: true}) ||
                a.position - b.position);
            rows.map(row => row.candidate).forEach((candidate, index) => {
                const row = document.createElement('p');
                const button = document.createElement('button');
                button.type = 'button';
                const image = typeof candidate.image_url === 'string' && candidate.image_url
                    ? 'Image available' : 'No image available';
                button.textContent = `${index + 1}. ${candidate.name || candidate.species} — ` +
                    `${monsterSourceLabel(candidate, true)} — ` +
                    `AC ${candidate.ac ?? '—'}, HP ${candidate.hp ?? '—'} — ${offerText(candidate)} — ${image}`;
                button.addEventListener('click', () => finish(candidate));
                row.className = 'monster-candidate-row';
                row.style.margin = '0 0 .75rem';
                row.append(button);
                // Source link and attribution sit on their own line below the button.
                const details = document.createElement('small');
                details.className = 'monster-candidate-details';
                details.style.display = 'block';
                details.style.marginTop = '.25rem';
                if (candidate.source_url && candidate.source_url.startsWith('https://')) {
                    const link = document.createElement('a');
                    link.href = candidate.source_url;
                    link.target = '_blank';
                    link.rel = 'noopener noreferrer';
                    link.textContent = 'View source';
                    details.append(link);
                }
                if (typeof candidate.attribution === 'string' && candidate.attribution) {
                    const credit = document.createElement('span');
                    credit.className = 'monster-candidate-attribution';
                    credit.textContent = details.childElementCount ? ` · ${candidate.attribution}` : candidate.attribution;
                    details.append(credit);
                }
                if (details.childElementCount) row.append(details);
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
        refreshProviders();
        const requestId = monsterSpeciesLookupRequest;
        const originalBonus = bonusInput?.value;
        const originalBonusRevision = bonusRevision;
        const overwriteBonus = Boolean(overwrite?.checked);
        const reuse = reuseLookup && reuseLookup.species === species &&
            Date.now() - reuseLookup.at < REUSE_MS ? reuseLookup : null;
        reuseLookup = null;
        // Choose again keeps the current monster and image until a new monster is picked.
        const kept = reuse && selected && selected.species === species ? (imageChoice || selected) : null;
        if (!kept) {
            selected = null;
            imageChoice = null;
            clearAppliedOffer();
            publishSelection();
        }
        if (cancelPopup) cancelPopup();
        const scopeGuard = window.scryingAdminFeedback.begin({region: 'monsters',
            operation: 'monster.candidate.lookup', target: 'monster-form', label: 'Select monster source'});
        const isCurrent = () => window.scryingAdminFeedback.isCurrent(scopeGuard) &&
            current === generation && requestId === monsterSpeciesLookupRequest &&
            speciesInput.value.trim() === species && Boolean(overwrite?.checked) === overwriteBonus;
        pending++;
        try {
            const result = reuse ? {status: 'ok', candidates: reuse.candidates}
                : await originalRequest(`/api/monsters/lookup?species=${encodeURIComponent(species)}`, options);
            if (!isCurrent()) return {found: false, reason: 'Lookup superseded.'};
            if (!result || result.status !== 'ok') return {found: false,
                reason: result?.reason || 'Monster lookup failed; enter stats manually.'};
            const candidates = result.candidates || [];
            if (!candidates.length) return {found: false,
                reason: `No usable monster stats found for ${species}; enter AC and HP manually.`};
            if (candidates.length > 1 && !reuse) {
                lastLookup = {species, candidates, at: Date.now()};
            } else if (candidates.length <= 1) {
                lastLookup = null;
            }
            updateReselect();
            const candidate = candidates.length === 1 ? candidates[0] : await choose(candidates);
            if (!isCurrent()) return {found: false, reason: 'Lookup superseded.'};
            if (!candidate) return {found: false, reason: kept
                ? 'Monster selection cancelled; the current monster and image are kept.'
                : 'Monster selection cancelled; manual entry remains available.'};
            if (kept) clearAppliedOffer();
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
            // Offer images from the other found monsters unless an upload already overrides them.
            const imageOwner = candidates.length > 1 && !uploadChosen()
                ? await chooseImage(candidate, candidates, kept) : candidate;
            if (!isCurrent()) return {found: false, reason: 'Lookup superseded.'};
            selected = candidate;
            imageChoice = imageOwner && imageOwner !== candidate ? imageOwner : null;
            publishSelection();
            return candidate;
        } finally {
            pending--;
            settlePendingSubmit();
            window.scryingAdminFeedback.resolve(scopeGuard);
        }
    };
})();
