/* SG-TODO-016: Source and Monster dropdowns in Monster identity.
 * Sources: configured 5e.tools sources and Open5e documents (D&D Beyond is name-search only).
 * Picking a monster sets Monster species and runs the normal one-candidate lookup, so AC, HP,
 * initiative bonus and image follow the existing empty-field/overwrite rules; the name is
 * filled in when empty or when overwrite is ticked.
 */
(() => {
    'use strict';
    const form = document.querySelector('#monsterForm');
    const speciesInput = document.querySelector('#monsterSpecies');
    const nameInput = document.querySelector('#monsterName');
    const overwrite = document.querySelector('#monsterSpeciesLookupOverwrite');
    if (!form || !speciesInput || typeof fetch !== 'function') return;
    let sources = [];
    let generation = 0;
    let picked = null;

    function field(labelText, id) {
        const label = document.createElement('label');
        label.className = 'field monster-source-field';
        const span = document.createElement('span');
        span.className = 'field-label';
        span.textContent = labelText;
        const select = document.createElement('select');
        select.id = id;
        span.id = id + 'Label';
        // Name from the visible label only, not the selected option text.
        select.setAttribute('aria-labelledby', span.id);
        label.append(span, select);
        return {label, select};
    }
    function option(select, value, text, disabled = false) {
        const node = document.createElement('option');
        node.value = value;
        node.textContent = text;
        node.disabled = disabled;
        select.append(node);
        return node;
    }
    const source = field('Source', 'monsterSourceSelect');
    const monster = field('Monster', 'monsterSourceMonster');
    const status = document.createElement('small');
    status.id = 'monsterSourceStatus';
    status.className = 'monster-source-status';
    status.setAttribute('aria-live', 'polite');
    status.style.flex = '1 1 100%';
    status.hidden = true;
    function setStatus(text) {
        status.textContent = text;
        status.hidden = !text;
    }
    function showMonster(flag) {
        monster.label.hidden = !flag;
        monster.label.style.display = flag ? '' : 'none';
    }
    showMonster(false);
    monster.select.setAttribute('aria-describedby', status.id);
    const anchor = speciesInput.closest('label.field') || speciesInput;
    anchor.parentElement.append(source.label, monster.label, status);

    function label(item) {
        const candidate = {provider: item.provider, source: item.label || item.source, legacy: item.legacy};
        return typeof monsterSourceLabel === 'function' ? monsterSourceLabel(candidate, true)
            : `${item.provider} / ${candidate.source}`;
    }
    function renderSources(unavailable = []) {
        const current = source.select.value;
        source.select.replaceChildren();
        option(source.select, '', 'None');
        sources.forEach((item, index) => option(source.select, String(index), label(item)));
        source.select.value = [...source.select.options].some(node => node.value === current) ? current : '';
        source.select.title = unavailable.length ? `Sources unavailable: ${unavailable.join(', ')}` : '';
    }
    async function json(url) {
        const response = await fetch(url, {credentials: 'same-origin'});
        if (!response.ok) {
            let reason = '';
            try { reason = (await response.json())?.detail || ''; } catch (_) { /* not JSON */ }
            throw new Error(typeof reason === 'string' && reason ? reason : `Request failed (${response.status})`);
        }
        return response.json();
    }
    async function loadSources() {
        try {
            const result = await json('/api/monsters/catalog/sources');
            if (result?.status !== 'ok' || !Array.isArray(result.sources)) throw new Error('Invalid source list');
            sources = result.sources.filter(item => item && typeof item.provider === 'string' &&
                typeof item.source === 'string');
            renderSources(Array.isArray(result.unavailable) ? result.unavailable : []);
        } catch (_) {
            sources = [];
            renderSources();
            source.select.title = 'Monster sources could not be loaded; use Monster species.';
        }
    }
    function chosenSource() {
        return source.select.value === '' ? null : sources[Number(source.select.value)] || null;
    }
    function resetMonster(text = '') {
        picked = null;
        monster.select.replaceChildren();
        monster.select.disabled = true;
        setStatus(text);
    }
    async function sourceChanged() {
        const current = ++generation;
        const item = chosenSource();
        resetMonster();
        showMonster(Boolean(item));
        if (!item) return;
        option(monster.select, '', 'Loading monsters…', true).selected = true;
        setStatus('Loading the complete monster list…');
        const query = new URLSearchParams({provider: item.provider, source: item.source});
        let result;
        try {
            result = await json('/api/monsters/catalog/monsters?' + query);
        } catch (error) {
            result = {status: 'error', reason: error.message};
        }
        if (current !== generation) return;  // A newer source choice wins.
        monster.select.replaceChildren();
        if (result?.status !== 'ok' || result.complete !== true || !Array.isArray(result.monsters)) {
            option(monster.select, '', 'Monster list unavailable', true).selected = true;
            setStatus(`Could not load the monster list (${result?.reason || 'incomplete list'}). ` +
                'Choose the source again to retry, or use Monster species.');
            return;
        }
        if (!result.monsters.length) {
            option(monster.select, '', 'No monsters in this source', true).selected = true;
            setStatus('This source has no monsters.');
            return;
        }
        option(monster.select, '', `Choose a monster (${result.monsters.length})`).selected = true;
        for (const entry of result.monsters) {
            if (entry && typeof entry.id === 'string' && typeof entry.name === 'string') {
                option(monster.select, entry.id, entry.name);
            }
        }
        monster.select.disabled = false;
        setStatus(`${result.monsters.length} monsters, complete list.`);
    }
    async function monsterChanged() {
        const item = chosenSource();
        const id = monster.select.value;
        const current = ++generation;
        picked = null;
        if (!item || !id) return;
        setStatus('Loading monster…');
        const query = new URLSearchParams({provider: item.provider, source: item.source, id});
        let result;
        try {
            result = await json('/api/monsters/catalog/monster?' + query);
        } catch (error) {
            result = {status: 'error', reason: error.message};
        }
        if (current !== generation || monster.select.value !== id) return;
        const candidate = result?.candidate;
        if (result?.status !== 'ok' || !candidate || typeof candidate.name !== 'string') {
            setStatus(`Could not load this monster (${result?.reason || 'unavailable'}); retry or use Monster species.`);
            return;
        }
        setStatus('');
        const replace = Boolean(overwrite?.checked);
        if (nameInput && (replace || !nameInput.value.trim())) nameInput.value = candidate.name;
        picked = candidate.name;
        speciesInput.value = candidate.name;
        window.scryingMonsterSelection?.preset(candidate.name, candidate);
        if (typeof lookupMonsterSpeciesStats === 'function') await lookupMonsterSpeciesStats();
    }
    source.select.addEventListener('change', sourceChanged);
    monster.select.addEventListener('change', monsterChanged);
    speciesInput.addEventListener('input', () => {
        // Typing another species leaves the picked monster behind.
        if (picked !== null && speciesInput.value.trim() !== picked) {
            picked = null;
            generation++;
            monster.select.value = '';
            setStatus('');
        }
    });
    form.addEventListener('reset', () => {
        generation++;
        source.select.value = '';
        resetMonster();
        showMonster(false);
    });
    renderSources();
    loadSources();
    window.scryingMonsterSourcePicker = {reload: loadSources};
})();
