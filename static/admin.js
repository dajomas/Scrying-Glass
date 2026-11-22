function monsterSourceLabel(candidate, popup = false) {
    const source = candidate.source || (popup ? 'Source unavailable' : 'unknown source');
    if (candidate.provider === '5e.tools') {
        const labels = {
            MM: 'Monster Manuals 2014', XMM: 'Monster Manuals 2024',
            PHB: 'Player Handbook 2014', XPHB: 'Player Handbook 2024',
            DMG: 'Dungeon Master Guide 2014', XDMG: 'Dungeon Master Guide 2024',
        };
        const label = Object.prototype.hasOwnProperty.call(labels, source) ? labels[source] : source;
        return popup ? `5e.tools / ${label}` : `5e.tools (${label})`;
    }
    if (candidate.provider === 'Open5e') {
        return popup ? `Open5e / ${source}${candidate.legacy ? ' / legacy' : ''}` : `Open5e (${source})`;
    }
    const edition = candidate.legacy ? 'legacy' : 'current';
    return popup ? `${candidate.provider} / ${source} / ${edition}` : `${edition} D&D Beyond`;
}

let latest;
let editing = null;

const selectedCharacterIds = new Set();
const selectedMonsterIds = new Set();

let monsterSpeciesLookupTimer = null;
let monsterSpeciesLookupRequest = 0;

function setMonsterSpeciesLookupStatus(text, options) {
    if (text === '') {
        window.scryingAdminFeedback.invalidateLookup();
        return;
    }
    paneNotification('monsters', text, options);
}

async function lookupMonsterSpeciesStats() {
    clearTimeout(monsterSpeciesLookupTimer);
    monsterSpeciesLookupTimer = null;

    const requestId = ++monsterSpeciesLookupRequest;

    const speciesInput = document.querySelector('#monsterSpecies');
    const acInput = document.querySelector('#monsterAc');
    const hpStartInput = document.querySelector('#monsterHpRangeStart');
    const hpEndInput = document.querySelector('#monsterHpRangeEnd');
    const overwriteInput = document.querySelector(
        '#monsterSpeciesLookupOverwrite',
    );

    if (
        !speciesInput ||
        !acInput ||
        !hpStartInput ||
        !hpEndInput
    ) {
        return;
    }

    const species = speciesInput.value.trim();

    if (!species) {
        setMonsterSpeciesLookupStatus('');
        return;
    }

    const overwriteFoundStats = Boolean(overwriteInput?.checked);
    const feedback = window.scryingAdminFeedback.beginLookup(species);
    const lookupNotice = (kind, text, severity = 'success') =>
        paneNotification(kind, text, {ticket: feedback, severity});

    const originalAc = acInput.value;
    const originalHpStart = hpStartInput.value;
    const originalHpEnd = hpEndInput.value;

    function isCurrentRequest() {
        return (
            window.scryingAdminFeedback.isCurrent(feedback) &&
            requestId === monsterSpeciesLookupRequest &&
            speciesInput.value.trim() === species &&
            Boolean(overwriteInput?.checked) === overwriteFoundStats
        );
    }

    setMonsterSpeciesLookupStatus(
        `Looking up ${species} (${window.scryingLookupSources?.order() || 'enabled sources'})…`,
        {ticket: feedback, severity: 'info'},
    );

    try {
        const suggestion = await request(
            `/api/dndbeyond/monster-stats?species=${encodeURIComponent(species)}`,
        );

        if (!isCurrentRequest()) {
            return;
        }

        if (!suggestion || suggestion.found !== true) {
            lookupNotice(
                'monsters',
                suggestion?.reason
                    ? String(suggestion.reason)
                    : `No usable monster stats found for ${species}; ` +
                      'enter AC and HP manually.',
                'info',
            );
            return;
        }

        const changes = [];

        const acUnchanged = acInput.value === originalAc;
        const hpUnchanged = (
            hpStartInput.value === originalHpStart &&
            hpEndInput.value === originalHpEnd
        );

        const hasUsableAc = (
            typeof suggestion.ac === 'number' &&
            Number.isInteger(suggestion.ac) &&
            suggestion.ac >= 0 &&
            suggestion.ac <= 999
        );

        if (
            hasUsableAc &&
            acUnchanged &&
            (
                overwriteFoundStats ||
                !acInput.value.trim()
            )
        ) {
            acInput.value = String(suggestion.ac);
            changes.push(`AC ${suggestion.ac}`);
        }

        let suggestedHp = '';

        if (
            typeof suggestion.hp === 'number' &&
            Number.isFinite(suggestion.hp) &&
            suggestion.hp >= 0
        ) {
            suggestedHp = String(suggestion.hp);
        } else if (typeof suggestion.hp === 'string') {
            suggestedHp = suggestion.hp.trim();
        }

        if (
            suggestedHp !== '' &&
            hpUnchanged &&
            (
                overwriteFoundStats ||
                (
                    !hpStartInput.value.trim() &&
                    !hpEndInput.value.trim()
                )
            )
        ) {
            hpStartInput.value = suggestedHp;
            hpEndInput.value = '';
            changes.push(`HP ${suggestedHp}`);
        }

        const provider = monsterSourceLabel(suggestion);

        if (changes.length) {
            lookupNotice(
                'monsters',
                `Loaded ${changes.join(', ')} from the ` +
                `${provider} result.`,
            );
            return;
        }

        if (!acUnchanged || !hpUnchanged) {
            lookupNotice(
                'monsters',
                `Found ${provider} stats; values edited ` +
                'while the lookup was running were left unchanged.',
            );
            return;
        }

        if (overwriteFoundStats) {
            lookupNotice(
                'monsters',
                `Found ${provider} stats, but no usable ` +
                'AC or HP values were returned.',
                'info',
            );
        } else {
            lookupNotice(
                'monsters',
                `Found ${provider} stats; existing AC ` +
                'and HP were left unchanged. Enable overwrite to replace them.',
            );
        }
    } catch (error) {
        if (!isCurrentRequest()) {
            return;
        }

        console.debug(
            'Optional monster stats lookup failed:',
            error,
        );

        setMonsterSpeciesLookupStatus(
            'Monster lookup is unavailable; enter AC and HP manually.',
            {ticket: feedback, severity: 'error'},
        );
    }
}

function setColorPreview(preview, color) {
    if (!preview || !color) {
        return;
    }

    preview.style.backgroundColor = color;
}

function installColorPreview(inputSelector, previewSelector) {
    const input = document.querySelector(inputSelector);
    const preview = document.querySelector(previewSelector);

    if (!input || !preview) {
        return;
    }

    const update = () => {
        setColorPreview(preview, input.value);
    };

    update();

    input.addEventListener('input', update);
    input.addEventListener('change', update);
}

const message = (text, options) =>
    window.scryingAdminFeedback.deliver('global', text, options);

const paneNotification = (kind, text, options) =>
    window.scryingAdminFeedback.deliver(kind, text, options);

const all = () => [
    ...latest.monsters,
    ...latest.characters,
    ...(latest.lairs || []),
];

const editModal = document.querySelector('#editModal');
const importModal = document.querySelector('#importModal');
const csvImportModal = document.querySelector('#csvImportModal');
const campaignModal = document.querySelector('#campaignModal');
const campaignSetupModal = document.querySelector('#campaignSetupModal');
const campaignDeleteModal = document.querySelector('#campaignDeleteModal');
const characterBulkAction = document.querySelector('#characterBulkAction');
const monsterBulkAction = document.querySelector('#monsterBulkAction');
const monsterFileHelpModal = document.querySelector('#monsterFileHelpModal');
const DICE_HP_RE = /^\s*(?<count>[1-9]\d*)d\s*(?<sides>[2-9]\d*|1\d+)(?:\s*(?<operator>[+-])\s*(?<modifier>\d+))?\s*$/i;

function isDiceHpExpression(value) {
    return DICE_HP_RE.test(String(value ?? '').trim());
}

function parseNonNegativeInteger(value) {
    const text = String(value ?? '').trim();

    if (!/^\d+$/.test(text)) {
        return null;
    }

    const number = Number(text);
    return Number.isSafeInteger(number) ? number : null;
}

function validateMonsterHpRange(startValue, endValue) {
    const start = String(startValue ?? '').trim();
    const end = String(endValue ?? '').trim();

    if (!start) {
        return 'HP Range start is required.';
    }

    if (isDiceHpExpression(start)) {
        if (end) {
            return (
                'Leave HP Range end empty when HP Range start uses dice notation, ' +
                'for example 3d8+9.'
            );
        }
        return null;
    }

    const numericStart = parseNonNegativeInteger(start);

    if (numericStart === null) {
        return (
            'HP Range start must be a non-negative whole number or a dice expression ' +
            'such as 3d8+9. => ' + String(start)
        );
    }

    if (!end) {
        return null;
    }

    const numericEnd = parseNonNegativeInteger(end);

    if (numericEnd === null) {
        return 'HP Range end must be a non-negative whole number.';
    }

    if (numericStart > numericEnd) {
        return 'HP Range start cannot be higher than HP Range end.';
    }

    return null;
}

function updateBattleRound(state) {
    const element = document.querySelector('#battleRound');

    if (!element) {
        return;
    }

    const round = state?.battle_round;
    const active = Number.isInteger(round) && round >= 1;

    element.hidden = !active;
    element.textContent = active ? `Round ${round}` : '';
}

// Campaign registry as returned by GET /api/campaigns:
// {active: campaignId, campaigns: [{campaignId, name, description, setups: [...]}], moved: [...]}
let campaignData = { active: null, campaigns: [], moved: [] };
let campaignEditing = null;

let csvImportKind = null;

function closeEdit() {
    editModal.hidden = true;
    editing = null;
    document.querySelector('#editForm').innerHTML = '';
}

function closeImport() {
    importModal.hidden = true;
}

async function request(url, options = {}, stateCurrent = () => true) {
    const feedbackState = url === '/api/state' ? window.scryingAdminFeedback.stateRequest() : null;
    const response = await fetch(url, options);

    if (response.ok) {
        const result = await response.json().catch(() => null);
        if (feedbackState !== null && stateCurrent()) window.scryingAdminFeedback.observeState(result, feedbackState);
        return result;
    }

    const fallbackMessage = response.statusText
        ? `${response.status} ${response.statusText}`
        : `Request failed with HTTP ${response.status}`;

    function formatDetail(detail) {
        if (typeof detail === 'string') {
            return detail.trim();
        }

        if (typeof detail === 'number' || typeof detail === 'boolean') {
            return String(detail);
        }

        if (Array.isArray(detail)) {
            return detail
                .map(formatDetail)
                .filter(Boolean)
                .join('; ');
        }

        if (!detail || typeof detail !== 'object') {
            return '';
        }

        const explanation = (
            typeof detail.message === 'string'
                ? detail.message
                : (
                    typeof detail.msg === 'string'
                        ? detail.msg
                        : ''
                )
        ).trim();

        let field = '';

        if (typeof detail.field === 'string') {
            field = detail.field.trim();
        } else if (Array.isArray(detail.loc)) {
            field = detail.loc
                .filter(part => ![
                    'body',
                    'query',
                    'path',
                    'header',
                    'cookie',
                ].includes(part))
                .map(part => String(part))
                .join('.');
        }

        if (explanation) {
            return field
                ? `${field}: ${explanation}`
                : explanation;
        }

        if ('detail' in detail) {
            return formatDetail(detail.detail);
        }

        if ('error' in detail) {
            return formatDetail(detail.error);
        }

        return '';
    }

    let errorBody = null;

    try {
        errorBody = await response.json();
    } catch {
        // Non-JSON errors use the HTTP status rather than raw HTML.
    }

    const detail = (
        errorBody &&
        typeof errorBody === 'object' &&
        !Array.isArray(errorBody) &&
        'detail' in errorBody
    )
        ? errorBody.detail
        : errorBody;

    const error = new Error(
        formatDetail(detail) || fallbackMessage,
    );

    error.status = response.status;
    error.url = url;

    throw error;
}

function esc(value) {
    return String(value).replace(/[&<>"']/g, character => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;',
    }[character]));
}

function numberValue(form, name, fallback) {
    const value = form.elements[name].value;
    return value === '' ? fallback : +value;
}

function selectionFor(kind) {
    return kind === 'characters'
        ? selectedCharacterIds
        : selectedMonsterIds;
}

function itemsFor(kind) {
    return kind === 'characters'
        ? latest.characters
        : latest.monsters;
}

function pruneSelection(kind) {
    const validIds = new Set(itemsFor(kind).map(item => item.id));
    const selected = selectionFor(kind);

    for (const id of selected) {
        if (!validIds.has(id)) {
            selected.delete(id);
        }
    }
}

function selectedIds(kind) {
    pruneSelection(kind);
    return [...selectionFor(kind)];
}

function setAllSelected(kind, selected) {
    const selection = selectionFor(kind);

    selection.clear();

    if (selected) {
        for (const item of itemsFor(kind)) {
            selection.add(item.id);
        }
    }

    const selector = kind === 'characters'
        ? 'input[data-select-kind="characters"][data-select-id]'
        : 'input[data-select-kind="monsters"][data-select-id]';

    document.querySelectorAll(selector).forEach(checkbox => {
        checkbox.checked = selected;
    });
}

function updateRowSelection(kind, id, checked) {
    const selection = selectionFor(kind);

    if (checked) {
        selection.add(id);
    } else {
        selection.delete(id);
    }
}

async function bulkRequest(kind, action, ids) {
    return request(`/api/${kind}/bulk`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ action, ids }),
    });
}

function selectionMessage(kind) {
    return kind === 'characters'
        ? 'Select one or more characters first.'
        : 'Select one or more monsters first.';
}

const rosterPending = new Map();
async function rosterMutation(kind, operation, target, send, success) {
    const feedback = window.scryingAdminFeedback;
    const key = JSON.stringify([kind, operation, target]);
    const previous = rosterPending.get(key);
    if (previous && (feedback.isCurrent(previous.ticket) || feedback.isCurrent(previous.refresh))) return;
    const spec = {region: kind, operation, target: JSON.stringify([kind, target]), label: 'Update roster'};
    const ticket = feedback.begin(spec);
    const refresh = feedback.begin({...spec, operation: operation + '.refresh', label: 'Refresh roster'});
    const pending = {ticket, refresh};
    rosterPending.set(key, pending);
    try {
        let result;
        try {result = await send();}
        catch (error) {feedback.publish(ticket, {severity: 'error', text: error.message}); return;}
        if (!feedback.isCurrent(ticket)) return;
        if (success) feedback.publish(ticket, {severity: 'success', text: success(result)});
        else feedback.resolve(ticket);
        try {await load(true); feedback.resolve(refresh);}
        catch {feedback.publish(refresh, {severity: 'error', text:
            'Changes saved, but display reload failed. Reload the page; do not repeat the change.'});}
    } finally {
        if (rosterPending.get(key) === pending) rosterPending.delete(key);
    }
}

async function runBulkAction(kind, action) {
    if (action === 'select-all') {
        setAllSelected(kind, true);
        return;
    }

    if (action === 'unselect-all') {
        setAllSelected(kind, false);
        return;
    }

    const ids = selectedIds(kind);
    const feedback = window.scryingAdminFeedback;
    const selectionSpec = {region: kind, operation: `roster.bulk.${action}.selection`,
        target: kind, label: 'Select combatants'};

    if (!ids.length) {
        feedback.publish(feedback.begin(selectionSpec), {severity: 'error', text: selectionMessage(kind)});
        return;
    }

    if (action === 'remove') {
        const noun = kind === 'characters' ? 'character' : 'monster';
        const destination = kind === 'characters'
            ? 'the active campaign'
            : 'the current battle setup';
        const names = itemsFor(kind)
            .filter(item => ids.includes(item.id))
            .map(item => item.name)
            .join(', ');

        if (!confirm(
            `Remove ${ids.length} selected ${noun}${ids.length === 1 ? '' : 's'} ` +
            `from ${destination}?\n\n${names}`,
        )) {
            return;
        }
    }

    feedback.resolve(feedback.begin(selectionSpec));
    return rosterMutation(kind, `roster.bulk.${action}`, JSON.stringify([...ids].map(String).sort()),
        () => bulkRequest(kind, action, ids), result => {
            const count = Number(result?.count ?? ids.length);
            return `${count} ${kind === 'characters' ? 'character' : 'monster'}${count === 1 ? '' : 's'} updated.`;
        });
}

async function removeCombatant(kind, id) {
    const item = itemsFor(kind).find(combatant => combatant.id === id);

    if (!item) {
        return;
    }

    const noun = kind === 'characters' ? 'character' : 'monster';
    const destination = kind === 'characters'
        ? 'the active campaign'
        : 'the current battle setup';

    if (!confirm(
        `Remove ${noun} “${item.name}” from ${destination}?`,
    )) {
        return;
    }

    return rosterMutation(kind, 'roster.remove', String(id),
        () => bulkRequest(kind, 'remove', [id]),
        () => `${noun[0].toUpperCase()}${noun.slice(1)} ` + `“${item.name}” removed.`);
}

async function patch(kind, id, data) {
    if (!['characters', 'monsters'].includes(kind)) throw new Error('Unsupported roster kind: ' + kind);
    return rosterMutation(kind, 'roster.patch', JSON.stringify([id, Object.keys(data).sort()]),
        () => request(`/api/${kind}/${encodeURIComponent(id)}`, {
            method: 'PATCH', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data),
        }));
}

// Colored dot in front of a combatant's name, styled like the battle-order
// turn marker, showing the color chosen for that combatant.
function colorMarker(combatant, fallback) {
    const color = esc(combatant.color || fallback);
    return `<span class="turn-marker" style="background:${color};color:${color}"` +
        ` title="Color: ${color}" aria-hidden="true"></span>`;
}

function monsterRow(monster) {
    const displayName = monster.ally
        ? `${monster.name} - Ally`
        : monster.name;

    return `
    <tr class="${monster.alive ? '' : 'dead'}">
        <td class="bulk-selection-cell">
            <input
                type="checkbox"
                class="bulk-selection-checkbox"
                data-select-kind="monsters"
                data-select-id="${esc(monster.id)}"
                aria-label="Select ${esc(monster.name)}"
                ${selectedMonsterIds.has(monster.id) ? 'checked' : ''}
            >
        </td>
        <td>
        ${colorMarker(monster, '#842029')}${esc(displayName)}
        <br>
        <small>${esc(monster.monster_species)}</small>
        </td>
        <td>${monster.ac}</td>
        <td>${monster.hp}/${monster.max_hp}</td>
        <td>
        <input
            class="initiative-edit"
            data-mi="${esc(monster.id)}"
            type="number"
            value="${monster.initiative ?? ''}"
            placeholder="init"
        >
        </td>
        <td>
        <button data-edit="${esc(monster.id)}" data-kind="monsters" class="edit">Edit</button>
        <button class="${monster.active ? 'on' : ''}" data-ma="${esc(monster.id)}">${monster.active ? 'In Battle' : 'Join Battle'}</button>
        <button class="${monster.ally ? 'on' : ''}" data-mally="${esc(monster.id)}">Ally</button>
        <button class="${monster.visible ? 'on' : ''}" data-mv="${esc(monster.id)}">Visible</button>
        <button data-mt="${esc(monster.id)}" class="${monster.in_turn ? 'on' : ''}">Turn</button>
        <button data-t="${esc(monster.id)}" data-f="show_ac">AC ${monster.show_ac ? 'on' : 'off'}</button>
        <button data-t="${esc(monster.id)}" data-f="show_hp">HP ${monster.show_hp ? 'on' : 'off'}</button>
        <button data-t="${esc(monster.id)}" data-f="show_initiative">Init ${monster.show_initiative ? 'on' : 'off'}</button>
        <button data-r="${esc(monster.id)}" class="reset">Reset</button>
        <button type="button" data-statistics="${esc(monster.id)}">Restore statistics</button>
        <button
            class="danger"
            type="button"
            data-remove-kind="monsters"
            data-remove-id="${esc(monster.id)}"
        >
            Remove
        </button>
        </td>
        <td>
        <button data-d="${esc(monster.id)}" class="danger">Damage</button>
        <button data-h="${esc(monster.id)}">Heal</button>
        </td>
    </tr>
    `;
}

function characterRow(character) {
    return `
    <tr class="${characterPermanentlyDead(character) ? 'dead' : ''}">
        <td class="bulk-selection-cell">
            <input
                type="checkbox"
                class="bulk-selection-checkbox"
                data-select-kind="characters"
                data-select-id="${esc(character.id)}"
                aria-label="Select ${esc(character.name)}"
                ${selectedCharacterIds.has(character.id) ? 'checked' : ''}
            >
        </td>
        <td>${colorMarker(character, '#1f4e79')}${esc(character.name)}</td>
        <td>
        <input class="hp-edit" data-chp="${esc(character.id)}" type="number" min="0" value="${character.hp}">
        /
        <input class="hp-edit" data-cmaxhp="${esc(character.id)}" type="number" min="0" value="${character.max_hp}">
        </td>
        <td>
        <input
            class="initiative-edit"
            data-ci="${esc(character.id)}"
            type="number"
            value="${character.initiative ?? ''}"
            placeholder="init"
        >
        </td>
        <td>
        <button data-edit="${esc(character.id)}" data-kind="characters" class="edit">Edit</button>
        <button class="${character.active ? 'on' : ''}" data-ca="${esc(character.id)}">${character.active ? 'In Battle' : 'Join Battle'}</button>
        <button class="${characterPermanentlyDead(character) ? '' : 'on'}" data-cl="${esc(character.id)}" title="Toggle explicit alive/dead state">${esc(character.life_state || (character.alive ? 'standing' : 'down'))}</button>
        <button class="${character.visible ? 'on' : ''}" data-cv="${esc(character.id)}">Visible</button>
        <button data-ct="${esc(character.id)}" class="${character.in_turn ? 'on' : ''}">Turn</button>
        <button data-cr="${esc(character.id)}" class="reset">Reset</button>
        <button type="button" data-statistics="${esc(character.id)}">Restore statistics</button>
        <button
            class="danger"
            type="button"
            data-remove-kind="characters"
            data-remove-id="${esc(character.id)}"
        >
            Remove
        </button>
        </td>
        <td>
        <button data-cd="${esc(character.id)}" class="danger">Damage</button>
        <button data-ch="${esc(character.id)}">Heal</button>
        </td>
    </tr>
    `;
}

function monsterEdit(monster) {
    const imagePreview = monster.image_url
        ? `
        <div class="monster-edit-image full">
            <img
                class="monster-edit-image-preview"
                src="${esc(monster.image_url)}"
                alt="${esc(monster.name)}"
            >
        </div>
        `
        : '';

    return `
    ${imagePreview}
    <label>
        <span>Name <span class="required-marker" aria-hidden="true">*</span></span>
        <input name="name" required value="${esc(monster.name)}">
    </label>
    <label>
        <span>Monster species <span class="required-marker" aria-hidden="true">*</span></span>
        <input name="monster_species" required value="${esc(monster.monster_species)}">
    </label>
    <label>
        <span>AC <span class="required-marker" aria-hidden="true">*</span></span>
        <input name="ac" type="number" min="0" value="${monster.ac}">
    </label>
    <label>
        Color
        <span class="color-picker-control">
            <input
                name="color"
                type="color"
                value="${esc(monster.color)}"
            >
            <span
                class="turn-marker color-picker-preview"
                style="background-color: ${esc(monster.color)}"
                aria-hidden="true"
            ></span>
        </span>
    </label>
    <label>
        <span>Current HP <span class="required-marker" aria-hidden="true">*</span></span>
        <input name="hp" type="number" value="${monster.hp}">
    </label>
    <label>
        <span>Max HP <span class="required-marker" aria-hidden="true">*</span></span>
        <input name="max_hp" type="number" min="0" value="${monster.max_hp}">
    </label>
    <label>
        <span>Reset HP <span class="required-marker" aria-hidden="true">*</span></span>
        <input name="original_hp" type="number" min="0" value="${monster.original_hp}">
    </label>
    <label>
        Initiative
        <input name="initiative" type="number" min="-100" max="100" value="${monster.initiative ?? ''}">
    </label>
    <label>
        Ally
        <select name="ally">
        <option value="false" ${monster.ally ? '' : 'selected'}>No</option>
        <option value="true" ${monster.ally ? 'selected' : ''}>Yes</option>
        </select>
    </label>
    <label>
        Replace image
        <input name="image" type="file" accept="image/*">
    </label>
    <div class="actions">
        <button>Save monster</button>
        <button type="button" id="cancelEdit">Cancel</button>
    </div>
    `;
}

function characterEdit(character) {
    return `
    <label>
        <span>Name <span class="required-marker" aria-hidden="true">*</span></span>
        <input name="name" required value="${esc(character.name)}">
    </label>
    <label>
        Color
        <span class="color-picker-control">
            <input
                name="color"
                type="color"
                value="${esc(character.color)}"
            >
            <span
                class="turn-marker color-picker-preview"
                style="background-color: ${esc(character.color)}"
                aria-hidden="true"
            ></span>
        </span>
    </label>
    <label>
        <span>Current HP <span class="required-marker" aria-hidden="true">*</span></span>
        <input name="hp" type="number" value="${character.hp}">
    </label>
    <label>
        <span>Max HP <span class="required-marker" aria-hidden="true">*</span></span>
        <input name="max_hp" type="number" min="0" value="${character.max_hp}">
    </label>
    <label>
        Initiative
        <input name="initiative" type="number" min="-100" max="100" value="${character.initiative ?? ''}">
    </label>
    <div class="actions">
        <button>Save character</button>
        <button type="button" id="cancelEdit">Cancel</button>
    </div>
    `;
}

function openEdit(kind, id) {
    const item = (kind === 'monsters' ? latest.monsters : latest.characters)
        .find(combatant => combatant.id === id);

    if (!item) {
        return;
    }

    editing = { kind, id };

    document.querySelector('#editTitle').textContent =
        `Edit ${kind === 'monsters' ? 'monster' : 'character'}: ${item.name}`;

    document.querySelector('#editForm').innerHTML =
        kind === 'monsters' ? monsterEdit(item) : characterEdit(item);

    if (kind === 'monsters') {
        const form = document.querySelector('#editForm');
        const imageInput = form.elements.image;
        const imagePreview = form.querySelector(
            '.monster-edit-image-preview'
        );

        if (imageInput && imagePreview) {
            imageInput.onchange = event => {
                const [file] = event.target.files;

                if (!file) {
                    return;
                }

                imagePreview.src = URL.createObjectURL(file);
                imagePreview.alt = `Selected replacement image for ${item.name}`;
            };
        }
    }

    document.querySelector('#cancelEdit').onclick = closeEdit;
    editModal.hidden = false;

    const editColorInput = document.querySelector(
        '#editForm input[name="color"]',
    );

    const editColorPreview = document.querySelector(
        '#editForm .color-picker-preview',
    );

    if (editColorInput && editColorPreview) {
        const updateEditColorPreview = () => {
            setColorPreview(editColorPreview, editColorInput.value);
        };

        updateEditColorPreview();

        editColorInput.addEventListener(
            'input',
            updateEditColorPreview,
        );

        editColorInput.addEventListener(
            'change',
            updateEditColorPreview,
        );
    }
}

function campaignById(campaignId) {
    return campaignData.campaigns.find(item => item.id === campaignId) || null;
}

function activeCampaign() {
    return campaignById(campaignData.active);
}

function syncActiveBattleSetupControls() {
    const activeSetup = latest?.active_setup;

    if (
        !activeSetup
        || typeof activeSetup.campaign_id !== 'string'
        || typeof activeSetup.name !== 'string'
    ) {
        return;
    }

    const activeCampaignEntry = activeCampaign();

    if (
        !activeCampaignEntry
        || activeCampaignEntry.id !== activeSetup.campaign_id
    ) {
        return;
    }

    const setupName = activeSetup.name.trim();

    if (!setupName) {
        return;
    }

    document.querySelector('#setupName').value = setupName;

    const setupSelect = document.querySelector('#setupSelect');

    if ([...setupSelect.options].some(option => option.value === setupName)) {
        setupSelect.value = setupName;
    }
}

function renderActiveBattleSetup() {
    const info = document.querySelector('#activeBattleSetupInfo');

    if (!info) {
        return;
    }

    const activeSetup = latest?.active_setup;

    if (
        !activeSetup
        || typeof activeSetup.campaign_id !== 'string'
        || typeof activeSetup.name !== 'string'
        || !activeSetup.campaign_id.trim()
        || !activeSetup.name.trim()
    ) {
        info.textContent = 'No saved battle setup loaded';
        return;
    }

    const activeCampaignEntry = activeCampaign();
    const sameCampaign = activeCampaignEntry
        && activeCampaignEntry.id === activeSetup.campaign_id;

    const isKnownSetup = Boolean(
        sameCampaign
        && Array.isArray(activeCampaignEntry.setups)
        && activeCampaignEntry.setups.includes(activeSetup.name),
    );

    if (!isKnownSetup) {
        info.textContent = 'Saved battle setup is no longer available';
        return;
    }

    info.innerHTML =
        `Active: <strong>${esc(activeSetup.name)}</strong>`;
}

function campaignOptions(selected, placeholder = '') {
    return (placeholder ? `<option value="">${esc(placeholder)}</option>` : '') +
        campaignData.campaigns
            .map(item =>
                `<option value="${esc(item.id)}"${item.id === selected ? ' selected' : ''}>` +
                `${esc(item.name)} (${item.setups.length})</option>`)
            .join('');
}

function setupOptions(names, placeholder, selected = '') {
    return `<option value="">${esc(placeholder)}</option>` +
        names
            .map(name =>
                `<option value="${esc(name)}"${name === selected ? ' selected' : ''}>${esc(name)}</option>`)
            .join('');
}

function renderImportSetups() {
    const importCampaign = document.querySelector('#importCampaign');
    const importSelect = document.querySelector('#importSetup');
    const campaign = campaignById(importCampaign.value) || activeCampaign();
    const names = campaign ? campaign.setups : [];
    const oldValue = importSelect.value;
    importSelect.innerHTML = setupOptions(names, 'Choose setup…', names.includes(oldValue) ? oldValue : '');
}

function renderCampaignSetupNames() {
    const from = campaignById(document.querySelector('#campaignSetupFrom').value);
    const select = document.querySelector('#campaignSetupName');
    const names = from ? from.setups : [];
    const oldValue = select.value;
    select.innerHTML = setupOptions(names, 'Choose setup…', names.includes(oldValue) ? oldValue : '');
}

function renderCampaigns() {
    const active = activeCampaign();

    document.querySelector('#activeCampaignInfo').innerHTML = active
        ? `Active: <strong>${esc(active.name)}</strong>` +
        (active.description ? ` — ${esc(active.description)}` : '')
        : 'No active campaign';

    document.querySelector('#campaignSelect').innerHTML =
        campaignOptions(campaignData.active);

    const setupSelect = document.querySelector('#setupSelect');
    const oldSetupValue = setupSelect.value;
    const names = active ? active.setups : [];
    setupSelect.innerHTML = setupOptions(
        names,
        active ? `Load saved setup from ${active.name}…` : 'Load saved setup…',
        names.includes(oldSetupValue) ? oldSetupValue : '',
    );

    const importCampaign = document.querySelector('#importCampaign');
    const oldImportCampaign = importCampaign.value;
    importCampaign.innerHTML = campaignOptions(
        campaignById(oldImportCampaign) ? oldImportCampaign : campaignData.active,
    );
    renderImportSetups();

    syncActiveBattleSetupControls();
    renderActiveBattleSetup();
}

// Stage 4: typed campaign-list feedback. A load error persists until a later load
// succeeds; the moved-setups notice is information that persists until replaced.
function campaignListNotice(operation, severity, text) {
    const feedback = window.scryingAdminFeedback;
    const ticket = feedback.begin({lane: 'page', region: 'campaign', operation,
        target: 'campaign-list', label: 'Campaign list'});
    return text ? feedback.publish(ticket, {severity, text}) : feedback.resolve(ticket);
}

function announceMovedSetups(moved) {
    if (moved?.length) campaignListNotice('campaign.setups.moved', 'info',
        `Moved ${moved.length} unassigned setup(s) into campaign Default: ` + moved.join(', '));
}

async function setups() {
    try {
        campaignData = await request('/api/campaigns');
        renderCampaigns();
        campaignListNotice('campaign.setups.load');
        announceMovedSetups(campaignData.moved);
    } catch (error) {
        campaignListNotice('campaign.setups.load', 'error', error.message);
    }
}

function updateBattleState(state) {
    const battleState = document.querySelector('#battleState');

    if (!battleState) {
        return;
    }

    const battleOrder = Array.isArray(state?.battle_order)
        ? state.battle_order
        : [];

    const battleActive = battleOrder.length > 0;

    battleState.textContent = battleActive ? 'Active' : 'Inactive';
    battleState.classList.toggle('active', battleActive);
    battleState.classList.toggle('inactive', !battleActive);
}

function activityStateClass(state) {
    return state === 'alive'
        ? 'activity-state-alive'
        : state === 'dead'
            ? 'activity-state-dead'
            : '';
}

function activityActionClass(action) {
    if (action === 'heal' || action === 'buff') {
        return 'activity-action-positive';
    }

    if (action === 'damage' || action === 'debuff') {
        return 'activity-action-negative';
    }

    return '';
}

function activityTime(value) {
    const date = new Date(value);

    return Number.isNaN(date.getTime())
        ? esc(value || '')
        : esc(date.toLocaleString());
}

function renderActivityLog(entries) {
    const container = document.querySelector('#activityLog');

    if (!entries.length) {
        container.textContent = 'No activity recorded.';
        return;
    }

    const rows = [...entries]
        .reverse()
        .map(entry => `
        <tr>
        <td>${activityTime(entry.timestamp)}</td>
        <td>${esc(entry.active_combatant || 'System')}</td>
        <td class="${activityStateClass(entry.active_combatant_state)}">
            ${esc(entry.active_combatant_state || 'unknown')}
        </td>
        <td>${esc(entry.target_combatant || '')}</td>
        <td class="${activityStateClass(entry.target_combatant_state)}">
            ${esc(entry.target_combatant_state || 'unknown')}
        </td>
        <td class="${activityActionClass(entry.action)}">
            ${esc(entry.action || '')}
        </td>
        <td>${esc(entry.amount ?? '')}</td>
        <td class="activity-log-details">${esc(entry.note ?? '')}</td>
        </tr>
    `)
        .join('');

    container.innerHTML = `
    <table>
        <tr>
        <th>Time</th>
        <th>Active combatant</th>
        <th>Active state</th>
        <th>Target</th>
        <th>Target state</th>
        <th>Action</th>
        <th>Amount</th>
        <th>Details</th>
        </tr>
        ${rows}
    </table>
    `;
}

function sortedMonstersForAdmin() {
    const battleOrder = Array.isArray(latest.battle_order)
        ? latest.battle_order
        : [];

    const battleActive = battleOrder.length > 0;

    const battleOrderIndex = new Map(
        battleOrder.map((id, index) => [id, index]),
    );

    function maxHp(monster) {
        const value = Number(monster.max_hp);

        return Number.isFinite(value)
            ? value
            : -Infinity;
    }

    function initiative(monster) {
        const value = monster.initiative;

        return typeof value === 'number' && Number.isFinite(value)
            ? value
            : null;
    }

    function byName(left, right) {
        return String(left.name || '').localeCompare(
            String(right.name || ''),
            undefined,
            { sensitivity: 'base' },
        );
    }

    return [...latest.monsters].sort((left, right) => {
        /*
        * Group 1: Active monsters.
        * Group 2: Inactive monsters.
        */
        if (Boolean(left.active) !== Boolean(right.active)) {
            return left.active ? -1 : 1;
        }

        if (left.active) {
            /*
            * While a battle is active, retain the actual battle order for entries
            * included in it. Active monsters not yet in that order follow.
            */
            if (battleActive) {
                const leftOrder = battleOrderIndex.get(left.id);
                const rightOrder = battleOrderIndex.get(right.id);

                const leftInOrder = leftOrder !== undefined;
                const rightInOrder = rightOrder !== undefined;

                if (leftInOrder !== rightInOrder) {
                    return leftInOrder ? -1 : 1;
                }

                if (leftInOrder && rightInOrder && leftOrder !== rightOrder) {
                    return leftOrder - rightOrder;
                }
            }

            /*
            * Outside battle—or for active entries not present in an existing
            * battle order—sort by Max HP descending.
            */
            if (maxHp(left) !== maxHp(right)) {
                return maxHp(right) - maxHp(left);
            }

            return byName(left, right);
        }

        /*
        * Inactive monsters:
        * numeric initiative first, descending;
        * null/blank initiative after numeric values;
        * then Max HP descending.
        */
        const leftInitiative = initiative(left);
        const rightInitiative = initiative(right);

        const leftHasInitiative = leftInitiative !== null;
        const rightHasInitiative = rightInitiative !== null;

        if (leftHasInitiative !== rightHasInitiative) {
            return leftHasInitiative ? -1 : 1;
        }

        if (
            leftHasInitiative &&
            rightHasInitiative &&
            leftInitiative !== rightInitiative
        ) {
            return rightInitiative - leftInitiative;
        }

        if (maxHp(left) !== maxHp(right)) {
            return maxHp(right) - maxHp(left);
        }

        return byName(left, right);
    });
}

async function load(rethrowErrors = false, current = () => true) {
    return window.scryingAdminFeedback.loadState(
        () => request('/api/state', {}, current), state => {
        latest = state;
        window.scryingStatisticsState?.(latest);
        window.scryingMonsterColorState?.(latest);
        window.scryingLairsRender?.(latest);
        window.updateEncounterToolsVisibility?.(latest);

        updateBattleOrderFontControls(latest.display?.battle_order_font_size);
        updateBattleRound(latest);

        syncActiveBattleSetupControls();
        renderActiveBattleSetup();

        setBackgroundInputs();

        renderActivityLog(
            Array.isArray(latest.activity_log)
                ? latest.activity_log
                : [],
        );

        updateBattleState(latest);

        updatePaneVisibilityForBattle();

        document.querySelector('#monsters').innerHTML =
            '<table>' +
            '<tr>' +
            '<th scope="col" class="bulk-selection-cell">Select</th>' +
            '<th>Monster</th>' +
            '<th>AC</th>' +
            '<th>HP</th>' +
            '<th>Initiative</th>' +
            '<th>Display/status</th>' +
            '<th>HP change</th>' +
            '</tr>' +
            sortedMonstersForAdmin().map(monsterRow).join('') +
            '</table>';

        document.querySelector('#characters').innerHTML =
            '<table>' +
            '<tr>' +
            '<th scope="col" class="bulk-selection-cell">Select</th>' +
            '<th>Character</th>' +
            '<th>Current / Max HP</th>' +
            '<th>Initiative</th>' +
            '<th>Display/status</th>' +
            '<th>HP change</th>' +
            '</tr>' +
            latest.characters.map(characterRow).join('') +
            '</table>';

        const battleInfo = document.querySelector('#battleInfo');

        if (!latest.battle_order.length) {
            battleInfo.textContent = 'No battle order set';
            return;
        }

        battleInfo.innerHTML =
            'Order: ' +
            latest.battle_order
                .map(id => all().find(combatant => combatant.id === id))
                .filter(Boolean)
                .map(combatant => {
                    const displayName = combatant.monster_species && combatant.ally
                        ? `${combatant.name} - Ally`
                        : combatant.name;

                    const name = '<span style="white-space: nowrap">' + esc(displayName) + '</span>';

                    if (!combatant.in_turn) {
                        return name;
                    }

                    const color = esc(combatant.color || '#ffffff');
                    const combatantId = esc(combatant.id);

                    return `
            <button
                type="button"
                class="battle-order-combatant active-turn"
                data-battle-actor="${combatantId}"
                title="Apply an action as ${esc(displayName)}"
            >
                <strong><u>
                <span
                    class="turn-marker"
                    style="background:${color};color:${color}"
                    aria-label="Current turn"
                    title="Current turn"
                ></span>${name}
                </u></strong>
            </button>
            `;
                })
                .join(' ⇒ ');

    }, rethrowErrors, current);
}

const hideablePanes = [
    {
        key: 'campaign',
        button: document.querySelector('#toggleCampaignPane'),
        pane: document.querySelector('#campaignInputPane'),
        hiddenLabel: 'Hide campaign input',
        visibleLabel: 'Show campaign input',
    },
    {
        key: 'characterInput',
        button: document.querySelector('#toggleCharacterPane'),
        pane: document.querySelector('#characterInputPane'),
        hiddenLabel: 'Hide character input',
        visibleLabel: 'Show character input',
    },
    {
        key: 'battleSetup',
        button: document.querySelector('#toggleBattleSetupPane'),
        pane: document.querySelector('#battleSetupInputPane'),
        hiddenLabel: 'Hide battle setup input',
        visibleLabel: 'Show battle setup input',
    },
    {
        key: 'lairInput',
        button: document.querySelector('#toggleLairPane'),
        pane: document.querySelector('#lairTools'),
        hiddenLabel: 'Hide lair input',
        visibleLabel: 'Show lair input',
    },
    {
        key: 'monsterInput',
        button: document.querySelector('#toggleMonsterPane'),
        pane: document.querySelector('#monsterInputPane'),
        hiddenLabel: 'Hide monster input',
        visibleLabel: 'Show monster input',
    },
    {
        key: 'characterDisplay',
        button: document.querySelector('#toggleCharacterDisplayPane'),
        pane: document.querySelector('#characterDisplayPane'),
        hiddenLabel: 'Hide character display',
        visibleLabel: 'Show character display',
    },
    {
        key: 'monsterDisplay',
        button: document.querySelector('#toggleMonsterDisplayPane'),
        pane: document.querySelector('#monsterDisplayPane'),
        hiddenLabel: 'Hide monster display',
        visibleLabel: 'Show monster display',
    },
];

const paneControlByKey = new Map(
    hideablePanes.map(control => [control.key, control]),
);

/*
* Parent pane -> dependent child pane.
*
* A child pane has two independent pieces of state:
* - whether the pane itself was hidden by its own toggle;
* - whether its own toggle button was visible.
*
* When a parent hides, save both values. When it reopens, restore both values
* exactly as they were. This means:
*
* - Child visible before parent hide -> child and button visible after restore.
* - Child hidden before parent hide -> child remains hidden, but its "Show"
*   button becomes visible again after parent restore.
*/
const paneDependencies = {
    campaign: {
        children: ['characterInput'],
        saved: null,
    },
    battleSetup: {
        children: ['lairInput', 'monsterInput'],
        saved: null,
    },
};

// Tracks whether this page has already performed the automatic collapse for
// the current battle. Once set, a manually opened pane remains untouched.
let collapsedForBattle = false;

function setPaneHidden(control, hidden) {
    control.pane.hidden = hidden;
    control.button.textContent = hidden
        ? control.visibleLabel
        : control.hiddenLabel;
    control.button.setAttribute('aria-expanded', String(!hidden));
}

function hideDependentPane(parentKey) {
    const dependency = paneDependencies[parentKey];
    if (!dependency) return;

    // Preserve each child's independent preference once per hide cycle.
    if (dependency.saved === null) dependency.saved = {};
    for (const key of dependency.children) {
        const child = paneControlByKey.get(key);
        if (!child) continue;
        if (!(key in dependency.saved)) {
            dependency.saved[key] = {
                paneHidden: child.pane.hidden,
                buttonHidden: child.button.hidden,
            };
        }
        setPaneHidden(child, true);
        child.button.hidden = true;
    }
}

function restoreDependentPane(parentKey) {
    const dependency = paneDependencies[parentKey];
    if (!dependency || dependency.saved === null) return;

    for (const key of dependency.children) {
        const child = paneControlByKey.get(key);
        const saved = dependency.saved[key];
        if (!child || !saved) continue;
        setPaneHidden(child, saved.paneHidden);
        child.button.hidden = saved.buttonHidden;
    }
    dependency.saved = null;
}

function setParentPaneHidden(parentKey, hidden) {
    const parent = paneControlByKey.get(parentKey);

    if (!parent) {
        return;
    }

    setPaneHidden(parent, hidden);

    if (hidden) {
        hideDependentPane(parentKey);
    } else {
        restoreDependentPane(parentKey);
    }
}

function setAllHideablePanesHidden(hidden) {
    // A global layout transition supersedes saved parent/child toggle state.
    Object.values(paneDependencies).forEach(dependency => {
        dependency.saved = null;
    });
    hideablePanes.forEach(control => {
        control.button.hidden = false;
        setPaneHidden(control, hidden);
    });
}

hideablePanes.forEach(control => {
    control.button.onclick = () => {
        /*
        * This is intentionally only a direct UI change. It does not modify
        * collapsedForBattle, so battle-state refreshes cannot re-hide a pane
        * that the GM manually opened during the battle.
        */
        const hidden = !control.pane.hidden;

        if (paneDependencies[control.key]) {
            setParentPaneHidden(control.key, hidden);
            return;
        }

        setPaneHidden(control, hidden);
    };
});

function updatePaneVisibilityForBattle() {
    const battleActive = Boolean(
        latest &&
        Array.isArray(latest.battle_order) &&
        latest.battle_order.length,
    );

    if (battleActive) {
        // Collapse once when a battle begins or an active setup is loaded.
        // Subsequent load() calls from Next, edits, bulk actions, etc. do nothing.
        if (!collapsedForBattle) {
            setAllHideablePanesHidden(true);
            collapsedForBattle = true;
        }

        return;
    }

    // A non-battle setup, a new setup, or Reset All restores the normal admin
    // layout and prepares automatic collapse for the next battle.
    if (collapsedForBattle) {
        setAllHideablePanesHidden(false);
        collapsedForBattle = false;

        /*
        * Battle end/reset restores the standard normal layout. Any temporary
        * parent-child hiding state from before the battle is no longer applied.
        */
        Object.values(paneDependencies).forEach(dependency => {
            dependency.saved = null;
        });
    }
}

// Character and monster saves are owned by character-edit-feedback.js and
// monster-initiative-edit.js, which delegate only unsupported kinds here.
document.querySelector('#editForm').onsubmit = event => {
    event.preventDefault();
};

// Setup import (#openImport, #importCampaign, #cancelImport, #importForm) is bound with the CSV import below.

function closeCsvImport() {
    csvImportModal.hidden = true;
    csvImportKind = null;
    document.querySelector('#csvImportForm').reset();
}

let csvImportSession = null;
let setupImportSession = null;
const modalImportPending = new WeakSet();
const modalImportRevision = new WeakMap();
for (const id of ['#csvImportForm', '#importForm']) {
    const form = document.querySelector(id);
    const edited = () => modalImportRevision.set(form, (modalImportRevision.get(form) || 0) + 1);
    for (const name of ['input', 'change', 'reset']) form.addEventListener(name, edited);
}
const previousCloseImport = closeImport;
closeImport = function() {
    if (setupImportSession) setupImportSession.closed = true;
    previousCloseImport();
};

async function runModalImport(form, spec, session, getSession, modal, prepare) {
    if (modalImportPending.has(form)) return;
    modalImportPending.add(form);
    const feedback = window.scryingAdminFeedback;
    let buttons = [], disabled = [];
    try {
        const validation = feedback.begin({...spec, operation: spec.operation + '.validation'});
        const prepared = prepare();
        if (prepared.error || !form.reportValidity()) {
            const field = prepared.error ? null : feedback.field?.(form);
            feedback.publish(field ? feedback.begin({...spec, operation: spec.operation + '.validation', field}) : validation, {severity: 'error', text: prepared.error || 'Select a valid import file and options.'});
            return;
        }
        feedback.resolve(validation);
        if (prepared.confirmation && !confirm(prepared.confirmation)) return;
        const tickets = prepared.regions.map(region => feedback.begin({...spec, region,
            target: JSON.stringify([spec.target, region])}));
        const refresh = feedback.begin({...spec, operation: spec.operation + '.refresh'});
        const revision = modalImportRevision.get(form) || 0;
        buttons = [...form.querySelectorAll('button[type="submit"], button:not([type]), input[type="submit"]')];
        disabled = buttons.map(button => button.disabled);
        buttons.forEach(button => {button.disabled = true;});
        const relevant = () => feedback.isCurrent(refresh) && getSession() === session;
        const current = () => relevant() && !session.closed && !modal.hidden;
        let result;
        try {result = await prepared.send();}
        catch (error) {
            if (current()) feedback.publish(tickets[0], {severity: 'error', text: error.message});
            return;
        }
        if (!current()) return;
        try {
            const messages = prepared.messages(result);
            for (let index = 0; index < tickets.length; index++) {
                if (!current()) return;
                feedback.publish(tickets[index], {severity: 'success', text: messages[index]});
            }
            // Do not discard files/options edited after the request was sent.
            if ((modalImportRevision.get(form) || 0) === revision) prepared.close();
            if (!relevant()) return;
            await load(true);
            if (relevant()) feedback.resolve(refresh);
        } catch {
            if (relevant()) feedback.publish(refresh, {severity: 'error', text:
                'Import succeeded, but updating the view failed. Reload the page; do not import again.'});
        }
    } finally {
        buttons.forEach((button, index) => {button.disabled = disabled[index];});
        modalImportPending.delete(form);
    }
}

function openCsvImport(kind) {
    csvImportKind = kind;
    csvImportSession = {kind, closed: false};
    const isMonster = kind === 'monsters';
    document.querySelector('#csvImportTitle').textContent = isMonster ? 'Import monsters from CSV' : 'Import characters from CSV';
    document.querySelector('#csvImportHelp').textContent = isMonster
        ? 'Required columns: name, monster_species, ac, hp. Optional id values are preserved; blank or missing IDs are generated automatically.'
        : 'Required column: name. Imported characters are added to the active campaign. Optional id values are preserved; blank or missing IDs are generated automatically.';
    csvImportModal.hidden = false;
}
function closeCsvImport() {
    if (csvImportSession) csvImportSession.closed = true;
    csvImportModal.hidden = true;
    csvImportKind = null;
    document.querySelector('#csvImportForm').reset();
}
document.querySelector('#openMonsterCsvImport').onclick = () => openCsvImport('monsters');
document.querySelector('#openCharacterCsvImport').onclick = () => openCsvImport('characters');
document.querySelector('#cancelCsvImport').onclick = closeCsvImport;
document.querySelector('#csvImportForm').onsubmit = event => {
    event.preventDefault();
    if (!csvImportKind || !csvImportSession) return;
    const kind = csvImportKind;
    const primary = kind === 'characters' ? 'campaign' : 'battleSetup';
    return runModalImport(event.currentTarget || event.target,
        {region: primary, operation: 'roster.import.csv', target: kind, label: 'Import CSV'},
        csvImportSession, () => csvImportSession, csvImportModal, () => {
            const payload = new FormData(event.currentTarget || event.target);
            const noun = kind === 'characters' ? 'character' : 'monster';
            return {
                regions: [primary, kind], close: closeCsvImport,
                send: () => request(kind === 'monsters' ? '/api/monsters/import-csv' : '/api/characters/import-csv',
                    {method: 'POST', body: payload}),
                messages: result => [
                    `Imported ${result.count} ${noun}${result.count === 1 ? '' : 's'} from CSV.`,
                    `${Number(result?.count ?? 0)} ${noun}${Number(result?.count ?? 0) === 1 ? '' : 's'} added successfully.`,
                ],
            };
        });
};

async function openSetupImport() {
    const feedback = window.scryingAdminFeedback;
    const session = setupImportSession = {closed: false};
    const ticket = feedback.begin({region: 'battleSetup', operation: 'setup.import.open',
        target: 'setup-import', label: 'Open setup import'});
    try {await setups();}
    catch (error) {feedback.publish(ticket, {severity: 'error', text: error.message}); return;}
    if (!feedback.isCurrent(ticket) || setupImportSession !== session || session.closed) return;
    feedback.resolve(ticket);
    document.querySelector('#importCampaign').value = campaignData.active || '';
    document.querySelector('#importLifeFilter').value = 'alive';
    renderImportSetups();
    importModal.hidden = false;
}
function submitSetupImport(event) {
    event.preventDefault();
    if (!setupImportSession) return;
    return runModalImport(event.currentTarget || event.target,
        {region: 'battleSetup', operation: 'setup.import', target: 'setup-import', label: 'Import saved setup'},
        setupImportSession, () => setupImportSession, importModal, () => {
            const payload = new FormData(event.currentTarget || event.target);
            const name = payload.get('name'), kind = payload.get('kind');
            const life_filter = payload.get('life_filter') || 'alive';
            const lifeLabel = {alive: 'Alive', dead: 'Dead', all: 'Alive and Dead'}[life_filter];
            const campaign = payload.get('campaign') || campaignData.active;
            if (!lifeLabel) return {error: 'Choose a valid monster state to import'};
            if (!name) return {error: 'Choose a saved setup to import from'};
            return {
                regions: ['battleSetup'], close: () => closeImport(),
                confirmation: `Import ${lifeLabel} ${kind} from ${name} into the current setup?`,
                send: () => request('/api/setups/import', {method: 'POST',
                    headers: {'Content-Type': 'application/json'}, body: JSON.stringify({name, kind, campaign, life_filter})}),
                messages: result => [`Imported ${result.monsters} monster${result.monsters === 1 ? '' : 's'} from ${result.name}`],
            };
        });
}
// Rebind the earlier setup-import handlers to this session-aware owner.
document.querySelector('#openImport').onclick = () => openSetupImport();
document.querySelector('#importCampaign').onchange = renderImportSetups;
document.querySelector('#cancelImport').onclick = () => closeImport();
document.querySelector('#importForm').onsubmit = submitSetupImport;

document.querySelector('#exportActivityLogCsv').onclick = () => {
    window.location.href = '/api/activity-log.csv';
};

document.querySelector('#exportActivityLogJson').onclick = () => {
    window.location.href = '/api/activity-log.json';
};

document.querySelector('#clearActivityLog').onclick = async () => {
    const currentCount = Array.isArray(latest?.activity_log)
        ? latest.activity_log.length
        : 0;
    const feedback = window.scryingAdminFeedback;
    const spec = {region: 'global', operation: 'activity-log.clear',
        target: 'activity-log', label: 'Clear activity log'};

    if (!currentCount) {
        feedback.publish(feedback.begin(spec), {
            severity: 'info', text: 'The activity log is already empty.',
        });
        return;
    }

    if (!confirm(`Clear all ${currentCount} activity log entries?`)) return;
    const ticket = feedback.begin(spec);
    let result;
    try {
        result = await request('/api/activity-log/clear', {method: 'POST'});
    } catch (error) {
        feedback.publish(ticket, {severity: 'error', text: error.message});
        return;
    }
    if (!feedback.isCurrent(ticket)) return;
    feedback.publish(ticket, {severity: 'success',
        text: `Cleared ${result.cleared} activity log ${result.cleared === 1 ? 'entry' : 'entries'}.`});
    // Clear succeeded; load() owns refresh errors. Never replay POST here.
    await load();
};

csvImportModal.addEventListener('click', event => {
    if (event.target === csvImportModal) {
        closeCsvImport();
    }
});

document.querySelector(
    '#monsterSpeciesLookupOverwrite',
).addEventListener('change', event => {
    if (
        event.target.checked &&
        document.querySelector('#monsterSpecies').value.trim()
    ) {
        lookupMonsterSpeciesStats();
    }
});

// Roll-all has one pending owner through mutation and display refresh.
(() => {
    const button = document.querySelector('#rollMonsterInitiative');
    let pending = false;
    button.onclick = async () => {
        if (pending) return;
        const feedback = window.scryingAdminFeedback;
        const spec = {region: 'monsters', target: 'all-monsters', label: 'Roll monster initiative'};
        const begin = operation => feedback.begin({...spec, operation: 'monster.roll-all.' + operation});
        const validation = begin('validation');
        if (!latest.monsters.length) {
            feedback.publish(validation, {severity: 'info', text: 'There are no monsters to roll initiative for'});
            return;
        }
        if (!confirm(`Overwrite initiative for all ${latest.monsters.length} monster(s) with a random d20 roll?`)) return;
        feedback.resolve(validation);
        const ticket = begin('request'), refresh = begin('refresh');
        const current = () => feedback.isCurrent(ticket) && feedback.isCurrent(refresh);
        const disabled = button.disabled;
        pending = true;
        button.disabled = true;
        try {
            let result;
            try {
                result = await request('/api/monsters/roll-initiative', {method: 'POST'});
            } catch (error) {
                if (current()) feedback.publish(ticket, {severity: 'error', text: error.message});
                return;
            }
            if (!current()) return;
            feedback.publish(ticket, {severity: 'success',
                text: `Rolled d20 initiative for ${result.count} monster(s)`});
            if (!feedback.isCurrent(refresh)) return;
            try {
                await load(true);
                feedback.resolve(refresh);
            } catch (error) {
                feedback.publish(refresh, {severity: 'error', text:
                    `Initiative rolled, but refresh failed: ${error.message}. Reload the page; do not roll again to retry the refresh.`});
            }
        } finally {
            button.disabled = disabled;
            pending = false;
        }
    };
})();

editModal.addEventListener('click', event => {
    if (event.target === editModal) {
        closeEdit();
    }
});

importModal.addEventListener('click', event => {
    if (event.target === importModal) {
        closeImport();
    }
});

function closeMonsterFileHelp() {
    monsterFileHelpModal.hidden = true;
    document.querySelector('#openMonsterFileHelp').focus();
}

document.querySelector('#openMonsterFileHelp').onclick = () => {
    monsterFileHelpModal.hidden = false;
    document.querySelector('#closeMonsterFileHelp').focus();
};

document.querySelector('#closeMonsterFileHelp').onclick = closeMonsterFileHelp;
document.querySelector('#closeMonsterFileHelpBottom').onclick = closeMonsterFileHelp;

monsterFileHelpModal.addEventListener('click', event => {
    if (event.target === monsterFileHelpModal) {
        closeMonsterFileHelp();
    }
});

document.addEventListener('keydown', event => {
    if (event.key !== 'Escape') {
        return;
    }

    if (!editModal.hidden) {
        closeEdit();
    }

    if (!importModal.hidden) {
        closeImport();
    }

    if (!csvImportModal.hidden) {
        closeCsvImport();
    }

    if (!campaignModal.hidden) {
        closeCampaignModal();
    }

    if (!campaignSetupModal.hidden) {
        campaignSetupModal.hidden = true;
    }

    if (!campaignDeleteModal.hidden) {
        campaignDeleteModal.hidden = true;
    }

    if (!monsterFileHelpModal.hidden) {
        closeMonsterFileHelp();
    }
});

// ---- Campaigns --------------------------------------------------------

function closeCampaignModal() {
    campaignModal.hidden = true;
    campaignEditing = null;
}

function openCampaignModal(campaign = null) {
    const form = document.querySelector('#campaignForm');
    campaignEditing = campaign ? campaign.id : null;
    document.querySelector('#campaignModalTitle').textContent =
        campaign ? `Edit campaign: ${campaign.name}` : 'New campaign';
    document.querySelector('#campaignSubmit').textContent = campaign ? 'Save' : 'Create';
    form.elements.name.value = campaign ? campaign.name : '';
    form.elements.description.value = campaign ? (campaign.description || '') : '';
    campaignModal.hidden = false;
    form.elements.name.focus();
}

document.querySelector('#cancelCampaign').onclick = closeCampaignModal;
document.querySelector('#cancelCampaignSetup').onclick = () => { campaignSetupModal.hidden = true; };
document.querySelector('#cancelCampaignDelete').onclick = () => { campaignDeleteModal.hidden = true; };

document.querySelector('#newCampaign').onclick = () => openCampaignModal();

// #editCampaign is bound by the campaign-edit owner further below.

// After a campaign is activated the server opens its most recently worked on
// (or newest) battle setup. Reflect that in the setup controls and reload state.
async function applyOpenedSetup(result, followup = null) {
    const current = followup || (() => true);
    if (!current()) return '';
    renderCampaigns();
    if (!current()) return '';
    if (!result || !result.opened_setup) {
        document.querySelector('#setupName').value = '';
        document.querySelector('#setupSelect').value = '';
        await (followup ? load(true, followup) : load());
        if (!current()) return '';
        renderActiveBattleSetup();
        return '';
    }
    document.querySelector('#setupName').value = result.opened_setup;
    document.querySelector('#setupSelect').value = result.opened_setup;
    syncActiveBattleSetupControls();
    if (!current()) return '';
    renderActiveBattleSetup();
    if (!current()) return '';
    await (followup ? load(true, followup) : load());
    return current() ? `; opened battle setup ${result.opened_setup}` : '';
}



const REPLACE_WARNING =
    'The current battle will be replaced by the campaign\'s most recently used battle setup. ' +
    'Unsaved changes will be lost.';

// Campaign create/edit submit and switching are owned by the campaign feedback code at
// the end of this file. These placeholders are the install points those owners wrap or replace.
document.querySelector('#campaignForm').onsubmit = event => {
    event.preventDefault();
};

async function switchCampaign() {}

document.querySelector('#switchCampaign').onclick = switchCampaign;
// Selecting another campaign in the dropdown switches to it immediately.
document.querySelector('#campaignSelect').onchange = switchCampaign;

// The delete dialog lets the admin choose WHICH campaign to delete. The
// "move setups to" list always excludes the campaign chosen for deletion.
// Stage 1 Step 1D: owned validation/request/success and guarded applied-deletion refresh.
let campaignDeleteSession = 0, campaignDeleteRevision = 0, campaignDeletePending = false;
const campaignDeleteFeedback = (operation, target, label, field) => window.scryingAdminFeedback.begin({
    lane: 'page', region: 'campaign', operation, target, label, ...(field ? {field} : {}),
});
const campaignDeleteForm = document.querySelector('#campaignDeleteForm');
campaignDeleteForm.addEventListener('input', () => { campaignDeleteRevision++; });
campaignDeleteForm.addEventListener('reset', () => { campaignDeleteRevision++; });
const campaignDeleteCancel = document.querySelector('#cancelCampaignDelete').onclick;
document.querySelector('#cancelCampaignDelete').onclick = () => {
    campaignDeleteSession++;
    campaignDeleteCancel();
};

function renderCampaignDeleteDialog() {
    const campaign = campaignById(document.querySelector('#campaignDeleteTarget').value);
    if (!campaign) {
        return;
    }
    const others = campaignData.campaigns.filter(item => item.id !== campaign.id);
    const hasSetups = campaign.setups.length > 0;
    const isActive = campaign.id === campaignData.active;
    document.querySelector('#campaignDeleteTitle').textContent = `Delete campaign: ${campaign.name}`;
    document.querySelector('#campaignDeleteText').textContent =
        (hasSetups
            ? `${campaign.name} contains ${campaign.setups.length} battle setup(s): ${campaign.setups.join(', ')}. ` +
            'Choose below whether to move them to another campaign or delete them.'
            : `${campaign.name} contains no battle setups.`) +
        (isActive ? ' This is the active campaign; another campaign becomes active after deleting it.' : '');
    const deleteSetups = document.querySelector('#campaignDeleteAction').value === 'delete';
    document.querySelector('#campaignDeleteActionLabel').hidden = !hasSetups;
    document.querySelector('#campaignDeleteMoveLabel').hidden = !hasSetups || deleteSetups;
    const moveTo = document.querySelector('#campaignDeleteMoveTo');
    const previous = moveTo.value;
    const preferred =
        others.find(item => item.id === previous) ||
        others.find(item => item.id === campaignData.active) ||
        others[0];
    moveTo.innerHTML = others
        .map(item =>
            `<option value="${esc(item.id)}"${item.id === preferred.id ? ' selected' : ''}>${esc(item.name)}</option>`)
        .join('');
}

document.querySelector('#deleteCampaign').onclick = () => {
    campaignDeleteSession++;
    const feedback = window.scryingAdminFeedback;
    const validation = campaignDeleteFeedback('campaign.delete.open', 'campaign-delete-selection', 'Delete campaign');
    if (campaignData.campaigns.length <= 1) {
        feedback.publish(validation, {severity: 'error', text: 'The last remaining campaign cannot be deleted'});
        return;
    }
    feedback.resolve(validation);
    // Preselect the first campaign that is NOT active, so the active campaign is
    // never deleted by accident; it can still be chosen explicitly.
    const initial =
        campaignData.campaigns.find(item => item.id !== campaignData.active) ||
        campaignData.campaigns[0];
    document.querySelector('#campaignDeleteTarget').innerHTML = campaignData.campaigns
        .map(item =>
            `<option value="${esc(item.id)}"${item.id === initial.id ? ' selected' : ''}>` +
            `${esc(item.name)}${item.id === campaignData.active ? ' (active)' : ''}</option>`)
        .join('');
    document.querySelector('#campaignDeleteMoveTo').innerHTML = '';
    document.querySelector('#campaignDeleteAction').value = 'move';
    renderCampaignDeleteDialog();
    campaignDeleteModal.hidden = false;
};

const campaignDeleteChanged = () => { campaignDeleteRevision++; renderCampaignDeleteDialog(); };
document.querySelector('#campaignDeleteTarget').onchange = campaignDeleteChanged;
document.querySelector('#campaignDeleteAction').onchange = campaignDeleteChanged;
document.querySelector('#campaignDeleteMoveTo').onchange = () => { campaignDeleteRevision++; };

document.querySelector('#campaignDeleteForm').onsubmit = async event => {
    event.preventDefault();
    if (campaignDeletePending || campaignDeleteModal.hidden) return;
    const feedback = window.scryingAdminFeedback;
    const validation = campaignDeleteFeedback('campaign.delete.validation', 'campaign-delete-selection', 'Delete campaign');
    const campaignId = document.querySelector('#campaignDeleteTarget').value;
    const campaign = campaignById(campaignId);
    if (!campaign) {
        feedback.publish(campaignDeleteFeedback('campaign.delete.validation', 'campaign-delete-selection',
            'Delete campaign', '#campaignDeleteTarget'), {severity: 'error', text: 'Choose a campaign to delete'});
        return;
    }
    const moveTo = document.querySelector('#campaignDeleteMoveTo').value;
    const hasSetups = campaign.setups.length > 0;
    const deleteSetups = hasSetups && document.querySelector('#campaignDeleteAction').value === 'delete';
    if (hasSetups && !deleteSetups && (!moveTo || moveTo === campaignId)) {
        feedback.publish(campaignDeleteFeedback('campaign.delete.validation', 'campaign-delete-selection',
            'Delete campaign', '#campaignDeleteMoveTo'), {severity: 'error', text: 'Choose another campaign to move the battle setups to'});
        return;
    }
    feedback.resolve(validation);
    const query = !hasSetups
        ? ''
        : deleteSetups
            ? '?delete_setups=true'
            : `?move_to=${encodeURIComponent(moveTo)}`;
    const setupNote = !hasSetups
        ? ''
        : deleteSetups
            ? `\n\nIts ${campaign.setups.length} battle setup(s) will be PERMANENTLY DELETED: ${campaign.setups.join(', ')}`
            : `\n\nIts ${campaign.setups.length} battle setup(s) will be moved to ${campaignById(moveTo)?.name || moveTo}.`;
    if (campaignId === campaignData.active
        ? !confirm(
            `${campaign.name} is the active campaign. After deleting it another campaign ` +
            `becomes active.${setupNote}\n\n${REPLACE_WARNING}`,
        )
        : !confirm(`Delete campaign ${campaign.name}?${setupNote}`)) {
        return;
    }
    const owner = campaignDeleteSession, revision = campaignDeleteRevision, registry = campaignData;
    const origin = feedback.encounterContext();
    const action = document.querySelector('#campaignDeleteAction').value;
    const ticket = campaignDeleteFeedback('campaign.delete', JSON.stringify(['campaign-delete', campaignId]), 'Delete campaign');
    const refresh = campaignDeleteFeedback('campaign.delete.refresh', JSON.stringify(['campaign-delete', campaignId]), 'Refresh after campaign deletion');
    const submit = document.querySelector('#campaignDeleteForm .danger'), disabled = submit.disabled;
    let result, applied = false, closedByAttempt = false;
    const same = () => {
        const now = feedback.encounterContext();
        const unchanged = now.scope === origin.scope && now.epoch === origin.epoch;
        const intended = result && now.epoch === origin.epoch + 1 && now.scope ===
            JSON.stringify([result.active, result.opened_setup ? result.active : null, result.opened_setup || null]);
        return feedback.isCurrent(refresh) && (!campaignDeleteModal.hidden || closedByAttempt) && campaignDeleteSession === owner && campaignDeleteRevision === revision &&
            campaignData === (applied ? result : registry) && document.querySelector('#campaignDeleteTarget').value === campaignId &&
            document.querySelector('#campaignDeleteAction').value === action &&
            document.querySelector('#campaignDeleteMoveTo').value === moveTo && (unchanged || intended);
    };
    campaignDeletePending = true; submit.disabled = true;
    try {
        try {
            result = await request(`/api/campaigns/${encodeURIComponent(campaignId)}${query}`, {method: 'DELETE'});
        } catch (error) {
            if (same() && feedback.isCurrent(ticket)) feedback.publish(ticket, {severity: 'error', text: error.message});
            return;
        }
        if (!same() || !feedback.isCurrent(ticket)) return;
        try {
            campaignData = result;
            applied = true;
            closedByAttempt = true;
            campaignDeleteModal.hidden = true;
            const opened = result.opened_setup ? `; opened battle setup ${result.opened_setup}` : '';
            feedback.publish(ticket, {severity: 'success', text:
                `Deleted campaign: ${campaign.name}` +
                (result.moved?.length ? ` (moved ${result.moved.length} setup(s))` : '') +
                (result.deleted_setups?.length ? ` (deleted ${result.deleted_setups.length} setup(s))` : '') + opened});
            if (!same()) return; // Refresh owns relevance after the success ticket settles.
            document.querySelector('#setupSelect').value = '';
            await applyOpenedSetup(result, same);
            if (!same()) return;
            if (feedback.encounterContext().scope !== JSON.stringify([
                result.active, result.opened_setup ? result.active : null, result.opened_setup || null])) {
                throw new Error('Deleted-campaign refresh state was not applied');
            }
            feedback.resolve(refresh);
        } catch (error) {
            if (same()) feedback.publish(refresh, {severity: 'error', text:
                `Campaign deleted, but refreshing the view failed: ${error.message}. Reload the page; do not delete the campaign again to retry the refresh.`});
        }
    } finally { submit.disabled = disabled; campaignDeletePending = false; }
};

// Setup transfer (#openCampaignSetup, #campaignSetupForm) and save/load/rename/delete
// are owned by setup-switch.js; #newSetup by the new-setup owner below, which wraps this install point.
document.querySelector('#campaignSetupFrom').onchange = renderCampaignSetupNames;

document.querySelector('#newSetup').onclick = async () => {};

function currentBackground() {
    return String(latest?.display?.background || '#080b14').trim();
}

function setBackgroundInputs(background = currentBackground()) {
    const color = document.querySelector('#backgroundColor');
    const value = document.querySelector('#backgroundValue');

    value.value = background;

    if (/^#[0-9a-fA-F]{6}$/.test(background)) {
        color.value = background;
    }
}

async function applyBackground(background) {
    await request('/api/display/background', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ background }),
    });

    await load();
}

// Stage 1 Step 2A: create a new empty setup.
(() => {
    const button = document.querySelector('#newSetup'), input = document.querySelector('#setupName');
    if (!button || typeof button.onclick !== 'function' || !input || typeof activeCampaign !== 'function') return;
    let pending = false, revision = 0;
    input.addEventListener('input', () => revision++);
    button.onclick = async () => {
        if (pending) return;
        const feedback = window.scryingAdminFeedback, campaign = campaignData.active, name = input.value.trim();
        const begin = (suffix, field) => feedback.begin({lane: 'page', region: 'battleSetup', operation: 'setup.new' + suffix,
            target: JSON.stringify(['setup-new', campaign]), label: 'Create battle setup', ...(field ? {field} : {})});
        const validation = begin('.validation', '#setupName');
        const known = (activeCampaign()?.setups || []).map(item => item.toLocaleLowerCase());
        const invalid = !name ? 'Enter a unique battle setup name before creating it.'
            : known.includes(name.toLocaleLowerCase())
                ? `A battle setup named “${name}” already exists in ${activeCampaign()?.name || campaign}.` : '';
        if (invalid) {
            feedback.publish(validation, {severity: 'error', text: invalid});
            input.focus();
            return;
        }
        feedback.resolve(validation);
        if (!confirm(`Discard the current battle setup and create a new empty setup named “${name}”?`)) return;
        const origin = feedback.encounterContext(), own = revision, ticket = begin(''), refresh = begin('.refresh');
        const disabled = button.disabled;
        let result, scope;
        const relevant = () => {
            if (!feedback.isCurrent(refresh) || campaignData.active !== campaign) return false;
            const now = feedback.encounterContext();
            return (now.epoch === origin.epoch && now.scope === origin.scope) ||
                Boolean(scope && now.epoch === origin.epoch + 1 && now.scope === scope);
        };
        pending = true;
        button.disabled = true;
        try {
            try {
                result = await request('/api/setups/new', {method: 'POST',
                    headers: {'Content-Type': 'application/json'}, body: JSON.stringify({name, campaign})});
            } catch (error) {
                if (relevant()) feedback.publish(ticket, {severity: 'error', text: error.message});
                return;
            }
            const setup = result.name, owner = result.campaign || campaign;
            scope = JSON.stringify([owner, owner, setup]);
            if (!relevant()) return;
            feedback.publish(ticket, {severity: 'success', text: `Created and saved empty battle setup “${setup}”.`});
            try {
                // Newer typing wins; the created setup is still selected and loaded.
                if (own === revision) input.value = setup;
                const list = await request('/api/campaigns');
                if (!relevant()) return;
                campaignData = list;
                renderCampaigns();
                announceMovedSetups(list.moved);
                document.querySelector('#setupSelect').value = setup;
                syncActiveBattleSetupControls();
                renderActiveBattleSetup();
                await load(true, relevant);
                if (relevant()) {
                    if (feedback.encounterContext().scope !== scope) throw new Error('The created setup state was not applied');
                    feedback.resolve(refresh);
                }
            } catch (error) {
                if (relevant()) feedback.publish(refresh, {severity: 'error', text: `Battle setup “${setup}” was created and ` +
                    `saved, but refreshing the view failed: ${error.message}. Reload the page; do not create the setup again to retry the refresh.`});
            }
        } finally {
            button.disabled = disabled;
            pending = false;
        }
    };
})();

const entryFormPending = new WeakSet();
async function submitEntryForm(form, region, operation, prepare) {
    if (entryFormPending.has(form)) return;
    entryFormPending.add(form);
    const feedback = window.scryingAdminFeedback;
    const spec = {region, operation, target: form.id, label: 'Create or import combatants'};
    let controls = [], disabled = [];
    try {
        const check = field => feedback.begin({...spec, operation: operation + '.validation', ...(field ? {field} : {})});
        let validation = check(null);
        if (!form.reportValidity()) {
            validation = check(feedback.field?.(form));
            feedback.publish(validation, {severity: 'error', text: 'Review the required fields and valid values before submitting.'});
            return;
        }
        let prepared;
        try { prepared = prepare(); }
        catch (error) {
            feedback.publish(validation, {severity: 'error', text: error.message});
            return;
        }
        if (prepared.error) {
            if (prepared.focus) validation = check(feedback.field?.(prepared.focus));
            feedback.publish(validation, {severity: 'error', text: prepared.error});
            prepared.focus?.focus();
            return;
        }
        feedback.resolve(validation);
        const ticket = feedback.begin(spec);
        const refresh = feedback.begin({...spec, operation: operation + '.refresh'});
        controls = [...form.querySelectorAll('input, select, textarea, button')];
        disabled = controls.map(control => control.disabled);
        controls.forEach(control => { control.disabled = true; });
        let result;
        try { result = await prepared.send(); }
        catch (error) {
            feedback.publish(ticket, {severity: 'error', text: error instanceof Error
                ? error.message : 'Unable to create or import combatants.'});
            return;
        }
        if (!feedback.isCurrent(refresh)) return;
        feedback.publish(ticket, {severity: 'success', text: prepared.success(result)});
        try {
            form.reset();
            await load(true);
            feedback.resolve(refresh);
        } catch {
            feedback.publish(refresh, {severity: 'error', text:
                'Changes saved, but updating the view failed. Reload the page; do not repeat the submission.'});
        }
    } finally {
        controls.forEach((control, index) => { control.disabled = disabled[index]; });
        entryFormPending.delete(form);
    }
}

document.querySelector('#characterForm').onsubmit = async event => {
    event.preventDefault();
    const form = event.currentTarget || event.target;
    return submitEntryForm(form, 'characters', 'character.create', () => {
        const payload = new FormData(form);
        const box = form.elements.track_hp, track = box ? box.checked : true;  // SG-TODO-024
        const data = {
            name: payload.get('name'), color: payload.get('color'),
            ...(track ? {hp: +payload.get('hp')} : {}),
            initiative: payload.get('initiative') === '' ? null : +payload.get('initiative'),
            ...(box ? {track_hp: track} : {}),
        };
        return {
            send: () => request('/api/characters', {method: 'POST',
                headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)}),
            success: () => `Character “${payload.get('name')}” added to the active campaign.`,
        };
    });
};

document.querySelector('#monsterForm').onsubmit = async event => {
    event.preventDefault();
    const form = event.currentTarget || event.target;
    return submitEntryForm(form, 'monsters', 'monster.create', () => {
        const payload = new FormData(form);
        const start = String(payload.get('hprangestart') ?? '').trim();
        const end = String(payload.get('hprangeend') ?? '').trim();
        const error = validateMonsterHpRange(start, end);
        if (error) {
            const invalidStart = !start || (!isDiceHpExpression(start) && parseNonNegativeInteger(start) === null);
            return {error, focus: invalidStart ? form.elements.hprangestart : form.elements.hprangeend};
        }
        payload.set('hprangestart', start);
        payload.set('hprangeend', end);
        const name = String(payload.get('name') ?? '').trim();
        return {
            send: () => request('/api/monsters', {method: 'POST', body: payload}),
            success: result => {
                const count = Array.isArray(result) ? result.length : 0;
                return count === 1 ? `Monster ${name} added to the battle setup.`
                    : `${count} monsters added to the battle setup.`;
            },
        };
    });
};

document.querySelector('#monsterUpload').onsubmit = async event => {
    event.preventDefault();
    const form = event.currentTarget || event.target;
    return submitEntryForm(form, 'battleSetup', 'monster.import.file', () => {
        const payload = new FormData(form);
        const file = payload.get('monster_file');
        const fileName = file instanceof File && file.name ? file.name : 'the uploaded file';
        const text = String(payload.get('quantity') ?? '1').trim();
        const quantity = Number(text);
        if (!/^\d+$/.test(text) || !Number.isInteger(quantity) || quantity < 1 || quantity > 50) {
            return {error: 'Quantity must be a whole number between 1 and 50.'};
        }
        return {
            send: () => request('/api/monsters/import', {method: 'POST', body: payload}),
            success: result => {
                const count = Array.isArray(result) ? result.length : quantity;
                return count === 1 ? `Monster imported from “${fileName}”.`
                    : `${count} monsters imported from “${fileName}”.`;
            },
        };
    });
};

document.querySelector('#monsterSpecies').addEventListener(
    'input',
    () => {
        clearTimeout(monsterSpeciesLookupTimer);
        monsterSpeciesLookupTimer = null;

        ++monsterSpeciesLookupRequest;

        const species = document.querySelector(
            '#monsterSpecies',
        ).value.trim();

        if (!species) {
            setMonsterSpeciesLookupStatus('');
            return;
        }

        setMonsterSpeciesLookupStatus('');

        monsterSpeciesLookupTimer = setTimeout(
            lookupMonsterSpeciesStats,
            600,
        );
    },
);

characterBulkAction.addEventListener('change', async () => {
    const action = characterBulkAction.value;
    characterBulkAction.value = '';

    if (action) {
        await runBulkAction('characters', action);
    }
});

monsterBulkAction.addEventListener('change', async () => {
    const action = monsterBulkAction.value;
    monsterBulkAction.value = '';

    if (action) {
        await runBulkAction('monsters', action);
    }
});

const battleActionModal = document.querySelector('#battleActionModal');
const battleActionForm = document.querySelector('#battleActionForm');
const battleActionRows = document.querySelector('#battleActionRows');
let battleActionActorId = null;
let battleStatisticsToken = null;
let battleActionsApplying = false;

function activeBattleTargets() {
    if (!latest) {
        return [];
    }

    return [...latest.monsters, ...latest.characters]
        .filter(combatant => combatant.active)
        .sort((left, right) => left.name.localeCompare(right.name));
}

function battleActionFeedback(operation, target, label, outcome) {
    const feedback = window.scryingAdminFeedback;
    const ticket = feedback.begin({region: 'global', operation: `battle.actions.${operation}`,
        target: String(target), label});
    return outcome === undefined ? feedback.resolve(ticket) : feedback.publish(ticket, outcome);
}

function closeBattleActions() {
    if (battleActionsApplying) return;
    battleActionModal.hidden = true;
    battleActionActorId = null;
    battleActionRows.innerHTML = '';
}

function actionAmountRequired(action) {
    return action === 'damage' || action === 'heal' || action === 'reduce-stat';
}

function updateActionRowAmount(row) {
    const action = row.querySelector('[data-action-kind]').value;
    const amountField = row.querySelector('.amount-field');
    const amountInput = row.querySelector('[data-action-amount]');
    const required = actionAmountRequired(action);

    amountField.hidden = !required;
    amountInput.required = required;
    const critical=row.querySelector('[data-action-critical]');
    if(critical){critical.parentElement.hidden=action!=='damage';if(action!=='damage')critical.checked=false;}

    if (!required) {
        amountInput.value = '';
    }
}

function addBattleActionRow(reaction = false) {
    if (battleActionsApplying) return;
    const targets = activeBattleTargets();

    if (!targets.length) {
        battleActionFeedback('targets', 'active', 'Battle-action targets',
            {severity: 'error', text: 'There are no active combatants available as targets.'});
        return;
    }

    battleActionFeedback('targets', 'active', 'Battle-action targets');
    const row = document.createElement('div');
    row.className = 'battle-action-row' + (reaction ? ' battle-reaction-row' : '');

    row.innerHTML = `
    ${reaction ? `<label>Reaction source
        <select data-action-source required>
        <option value="" disabled selected>Select source…</option>
        ${targets.map(source =>
            `<option value="${esc(source.id)}">${esc(source.name)}${source.alive ? '' : ' (down/dead)'}</option>`
        ).join('')}</select></label>` : ''}
    <label>
        Target
        <select data-action-target required>
        <option value="" disabled selected>Select target…</option>
        ${targets.map(target => `
            <option value="${esc(target.id)}">
            ${esc(target.monster_species && target.ally ? `${target.name} - Ally` : (!target.monster_species) ? `${target.name} - Character` : `${target.name} - Monster`)}
            </option>
        `).join('')}
        </select>
    </label>

    <label>
        Action
        <select data-action-kind required>
        <option value="damage">Damage</option>
        <option value="heal">Heal</option>
        ${reaction ? '' : '<option value="buff">Buff</option><option value="debuff">Debuff</option>'}
        </select>
    </label>

    <label class="amount-field">
        Amount
        <input data-action-amount type="number" min="1" max="99999" value="1">
        <span class="critical-option"><input data-action-critical type="checkbox"> Critical hit</span>
    </label>

    <button type="button" class="danger" data-remove-action-row>
        Remove
    </button>
    `;

    row.querySelector('[data-action-kind]').addEventListener('change', () => {
        updateActionRowAmount(row);
    });

    row.querySelector('[data-remove-action-row]').addEventListener('click', () => {
        row.remove();


    });

    battleActionRows.appendChild(row);
    updateActionRowAmount(row);
}

function addStatisticsReductionRow() {
    if (battleActionsApplying) return;
    const targets = activeBattleTargets().filter(x => x.alive);
    if (!targets.length) {
        battleActionFeedback('targets', 'living', 'Statistics-reduction targets',
            {severity: 'error', text: 'There are no living active targets.'});
        return;
    }
    battleActionFeedback('targets', 'living', 'Statistics-reduction targets');
    const row = document.createElement('div');
    row.className = 'battle-action-row statistics-reduction-row';
    row.innerHTML = `
        <input data-action-kind type="hidden" value="reduce-stat">
        <label>Target <select data-action-target required>
          <option value="" disabled selected>Select target…</option>
          ${targets.map(x=>`<option value="${esc(x.id)}">${esc(x.name)}</option>`).join('')}
        </select></label>
        <label>Statistic <select data-action-stat required>
          <option value="max_hp">Max HP</option><option value="strength">STR</option>
          <option value="dexterity">DEX</option><option value="constitution">CON</option>
          <option value="intelligence">INT</option><option value="wisdom">WIS</option>
          <option value="charisma">CHA</option>
        </select></label>
        <label class="amount-field">Amount to reduce
          <input data-action-amount type="number" required min="1" max="99999" step="1" value="1">
        </label>
        <button data-remove-action-row type="button" class="danger">Remove</button>`;
    row.querySelector('[data-remove-action-row]').addEventListener('click',()=>row.remove());
    battleActionRows.appendChild(row);
}

function openBattleActions(actorId) {
    if (battleActionsApplying) return;
    if ((latest.lairs || []).some(x => x.id === actorId)) {
        window.scryingOpenLairAction?.(actorId);
        return;
    }
    const actor = [...latest.monsters, ...latest.characters]
        .find(combatant => combatant.id === actorId);

    if (!actor || !actor.active || !actor.in_turn) {
        battleActionFeedback('eligibility', actorId, `Battle actions: ${actor?.name || actorId}`,
            {severity: 'error', text: 'Only the current active combatant can perform battle actions.'});
        return;
    }

    battleActionFeedback('eligibility', actorId, `Battle actions: ${actor.name}`);
    document.querySelector('#battleActionNotice').textContent = '';
    battleActionActorId = actorId;
    battleStatisticsToken = latest.statistics_token;
    document.querySelector('#battleActionTitle').textContent =
        `Battle actions: ${actor.name}`;

    battleActionRows.innerHTML = '';
    addBattleActionRow(!actor.alive);
    battleActionModal.hidden = false;
}

document.querySelector('#addBattleActionTarget').onclick = () => {
    addBattleActionRow();
};

document.querySelector('#addBattleReaction').onclick = () => addBattleActionRow(true);
document.querySelector('#addStatisticsReduction').onclick = addStatisticsReductionRow;

document.querySelector('#closeBattleActions').onclick = closeBattleActions;

battleActionModal.addEventListener('click', event => {
    if (event.target === battleActionModal) {
        closeBattleActions();
    }
});

battleActionForm.onsubmit = async event => {
    event.preventDefault();

    if (!battleActionActorId || battleActionsApplying) {
        return;
    }

    // Also enforce native validation when the handler is invoked directly.
    if (!battleActionForm.reportValidity()) {
        return;
    }

    const rows = [...battleActionRows.querySelectorAll('.battle-action-row')]
        .filter(row => row.dataset.applied !== 'true');

    const actions = rows.map(row => {
        const action = row.querySelector('[data-action-kind]').value;
        const rawAmount = row.querySelector('[data-action-amount]').value;

        return {
            source_id: row.querySelector('[data-action-source]')?.value || null,
            target_id: row.querySelector('[data-action-target]').value,
            action,
            amount: actionAmountRequired(action) ? Number(rawAmount) : null,
            critical_hit: action==='damage'&&Boolean(row.querySelector('[data-action-critical]')?.checked),
            ...(action === 'reduce-stat' ? {stat: row.querySelector('[data-action-stat]').value} : {}),
        };
    });

    if (!actions.length) {
        battleActionFeedback('pending', battleActionActorId, 'Battle actions',
            {severity: 'info', text: 'No pending actions or reactions. Add a new row to apply more.'});
        return;
    }
    const applyButton = battleActionForm.querySelector('button[type="submit"]');
    if (applyButton.disabled) return;
    battleActionFeedback('pending', battleActionActorId, 'Battle actions');
    battleActionsApplying = true;
    // Freeze this batch and the separate start-of-turn form until refresh ends.
    const controls = [...battleActionModal.querySelectorAll('input, select, button')];
    const previousDisabled = controls.map(control => control.disabled);
    controls.forEach(control => { control.disabled = true; });
    battleActionModal.setAttribute('aria-busy', 'true');
    let applied = false;

    try {
        const result = await request('/api/battle/actions', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                actor_id: battleActionActorId,
                actions,
                ...(actions.some(x=>x.action==='reduce-stat') ? {statistics_token: battleStatisticsToken} : {}),
            }),
        });

        // Record success before refreshing: a failed refresh must not replay HP changes.
        applied = true;
        for (const row of rows) {
            row.dataset.applied = 'true';
            const status = document.createElement('span');
            status.className = 'battle-action-applied-status';
            status.textContent = 'Applied';
            row.appendChild(status);
        }
        document.querySelector('#battleActionNotice').textContent =
            `Applied ${result.applied} battle action${result.applied === 1 ? '' : 's'}. ` +
            'Add targets or reactions to continue, or Close when finished.';
        await load(true);
        if (typeof battleStatisticsToken !== 'undefined') battleStatisticsToken = latest.statistics_token;
    } catch (error) {
        document.querySelector('#battleActionNotice').textContent = applied
            ? `Actions were applied, but refresh failed: ${error.message}. Refresh before continuing.`
            : error.message;
    } finally {
        controls.forEach((control, index) => {
            control.disabled = previousDisabled[index] ||
                control.closest('.battle-action-row')?.dataset.applied === 'true';
        });
        battleActionsApplying = false;
        battleActionModal.removeAttribute('aria-busy');
    }
};

async function resetCombatantWithFeedback(kind, id) {
    const feedback = window.scryingAdminFeedback;
    const name = latest?.[kind]?.find(combatant => combatant.id === id)?.name || id;
    const noun = kind === 'monsters' ? 'monster' : 'character';
    const ticket = feedback.begin({region: 'global', operation: 'combatant.reset',
        target: JSON.stringify([kind, id]), label: `Reset ${noun}: ${name}`});
    try {
        await request(`/api/combatants/${encodeURIComponent(id)}/reset`, {method: 'POST'});
    } catch (error) {
        feedback.publish(ticket, {severity: 'error', text: error.message});
        return;
    }
    if (!feedback.isCurrent(ticket)) return;
    feedback.resolve(ticket);
    // Reset succeeded; refresh failures remain owned by load(), not the mutation.
    await load();
}

document.addEventListener('click', async event => {
    const button = event.target.closest('button');

    if (!button) {
        return;
    }

    if (button.dataset.removeKind && button.dataset.removeId) {
        await removeCombatant(
            button.dataset.removeKind,
            button.dataset.removeId,
        );
        return;
    }

    if (button.dataset.remove) {
        const id = button.dataset.remove;
        const kind = button.dataset.removeKind || 'combatant';
        const row = button.closest('tr');
        const name = row?.querySelector('td')?.textContent.trim() || kind;

        if (!confirm(`Remove ${kind} “${name}” from the current encounter?`)) return;
        const feedback = window.scryingAdminFeedback;
        const ticket = feedback.begin({region: 'global', operation: 'combatant.remove.fallback',
            target: id, label: `Remove ${kind}: ${name}`});
        button.disabled = true;
        let result;
        try {
            result = await request(`/api/combatants/${encodeURIComponent(id)}`, {method: 'DELETE'});
        } catch (error) {
            if (feedback.isCurrent(ticket)) {
                feedback.publish(ticket, {severity: 'error', text: error.message});
                button.disabled = false;
            }
            return;
        }
        if (!feedback.isCurrent(ticket)) return;
        feedback.publish(ticket, {severity: 'success', text: `Removed ${result?.name ?? name}.`});
        // Deletion succeeded; load() owns refresh errors. Do not replay DELETE.
        await load();
        return;
    }

    if (button.dataset.battleActor) {
        openBattleActions(button.dataset.battleActor);
        return;
    }

    if (button.dataset.edit) {
        openEdit(button.dataset.kind, button.dataset.edit);
        return;
    }

    const id =
        button.dataset.ma ||
        button.dataset.mally ||
        button.dataset.mv ||
        button.dataset.mt ||
        button.dataset.t ||
        button.dataset.d ||
        button.dataset.h ||
        button.dataset.r ||
        button.dataset.ca ||
        button.dataset.cl ||
        button.dataset.cv ||
        button.dataset.ct ||
        button.dataset.cd ||
        button.dataset.ch ||
        button.dataset.cr;

    if (!id) {
        return;
    }

    if (button.dataset.ma) {
        patch('monsters', id, { active: !button.classList.contains('on') });
        return;
    }

    if (button.dataset.mally) {
        patch('monsters', id, { ally: !button.classList.contains('on') });
        return;
    }

    if (button.dataset.mv) {
        patch('monsters', id, { visible: !button.classList.contains('on') });
        return;
    }

    if (button.dataset.mt) {
        patch('monsters', id, { in_turn: !button.classList.contains('on') });
        return;
    }

    if (button.dataset.r) {
        await resetCombatantWithFeedback('monsters', id);
        return;
    }

    if (button.dataset.t) {
        patch('monsters', id, {
            [button.dataset.f]: !button.textContent.endsWith('on'),
        });
        return;
    }

    if (button.dataset.d) {
        const entered = prompt('Damage to remove:', '1');
        if (entered === null || entered.trim() === '') {
            return;
        }
        const value = Number(entered);

        if (Number.isSafeInteger(value) && value > 0) {
            patch('monsters', id, { hp_delta: -Math.abs(value) });
        }

        return;
    }

    if (button.dataset.h) {
        const entered = prompt('Healing to add:', '1');
        if (entered === null || entered.trim() === '') {
            return;
        }
        const value = Number(entered);

        if (Number.isSafeInteger(value) && value > 0) {
            patch('monsters', id, { hp_delta: Math.abs(value) });
        }

        return;
    }

    if (button.dataset.ca) {
        patch('characters', id, { active: !button.classList.contains('on') });
        return;
    }

    if (button.dataset.cl) {
        patch('characters', id, { alive: !button.classList.contains('on') });
        return;
    }

    if (button.dataset.cv) {
        patch('characters', id, { visible: !button.classList.contains('on') });
        return;
    }

    if (button.dataset.ct) {
        patch('characters', id, { in_turn: !button.classList.contains('on') });
        return;
    }

    if (button.dataset.cd) {
        const entered = prompt('Damage to remove:', '1');
        if (entered === null || entered.trim() === '') {
            return;
        }
        const value = Number(entered);

        if (Number.isSafeInteger(value) && value > 0) {
            patch('characters', id, { hp_delta: -Math.abs(value) });
        }

        return;
    }

    if (button.dataset.ch) {
        const entered = prompt('Healing to add:', '1');
        if (entered === null || entered.trim() === '') {
            return;
        }
        const value = Number(entered);

        if (Number.isSafeInteger(value) && value > 0) {
            patch('characters', id, { hp_delta: Math.abs(value) });
        }

        return;
    }

    if (button.dataset.cr) {
        await resetCombatantWithFeedback('characters', id);
    }
});

document.addEventListener('change', event => {
    const input = event.target;

    if (input.dataset.mi) {
        patch('monsters', input.dataset.mi, { initiative: input.value === '' ? null : +input.value });
    }

    if (input.dataset.ci) {
        patch('characters', input.dataset.ci, { initiative: input.value === '' ? null : +input.value });
    }

    if (input.dataset.chp && input.value !== '') {
        patch('characters', input.dataset.chp, { hp: +input.value });
    }

    if (input.dataset.cmaxhp && input.value !== '') {
        patch('characters', input.dataset.cmaxhp, { max_hp: +input.value });
    }
});

document.addEventListener('change', event => {
    const checkbox = event.target.closest('input[data-select-kind][data-select-id]');

    if (!checkbox) {
        return;
    }

    updateRowSelection(
        checkbox.dataset.selectKind,
        checkbox.dataset.selectId,
        checkbox.checked,
    );
});

function characterPermanentlyDead(character) {
    return character.life_state==='dead'||(character.death_failures??0)>=3;
}
function turnEligible(combatant) {
    if(!combatant.active||combatant.life_state==='dead')return false;
    return !('monster_species' in combatant)?!characterPermanentlyDead(combatant):Boolean(combatant.alive);
}
function living(){return all().filter(x => x.kind !== 'lair' && turnEligible(x));}

function initiativeOf(combatant) {
    return typeof combatant.initiative === 'number' &&
        Number.isFinite(combatant.initiative)
        ? combatant.initiative
        : null;
}

function initiativeBuckets() {
    const buckets = new Map();

    for (const combatant of living()) {
        const initiative = initiativeOf(combatant);
        const key = initiative === null ? 'blank' : `n:${initiative}`;
        const bucket = buckets.get(key) || {
            initiative,
            members: [],
        };

        bucket.members.push(combatant);
        buckets.set(key, bucket);
    }

    return [...buckets.values()].sort((left, right) => {
        if (left.initiative === null && right.initiative === null) {
            return 0;
        }

        if (left.initiative === null) {
            return 1;
        }

        if (right.initiative === null) {
            return -1;
        }

        return right.initiative - left.initiative;
    });
}

function tiedBuckets() {
    return initiativeBuckets().filter(bucket =>
        bucket.initiative !== null && bucket.members.length > 1,
    );
}

function normalOrder() {
    return initiativeBuckets().flatMap(bucket =>
        bucket.members.map(combatant => combatant.id),
    );
}

function tieUI() {
    const characterIds = new Set(latest.characters.map(character => character.id));
    const ties = tiedBuckets().map(bucket => ({
        ...bucket,
        members: bucket.members.slice().sort((left, right) =>
            Number(characterIds.has(right.id)) - Number(characterIds.has(left.id)),
        ),
    }));

    return ties.map((bucket, bucketIndex) => `
    <div class="tie-title">Initiative ${bucket.initiative}</div>
    ${bucket.members.map((member, memberIndex) => `
        <label class="tie">
        ${esc(member.name)}
        <select data-tie-bucket="${bucketIndex}" data-tie-member="${esc(member.id)}" data-tie-position="${memberIndex + 1}">
            ${bucket.members.map((_, position) => `
            <option value="${position + 1}" ${position === memberIndex ? 'selected' : ''}>
                ${position + 1}
            </option>
            `).join('')}
        </select>
        </label>
    `).join('')}
    `).join('');
}

function swapTiePosition(event) {
    const select = event.target;

    if (!select.matches('select[data-tie-bucket][data-tie-member]')) {
        return;
    }

    const previous = select.dataset.tiePosition;
    const chosen = select.value;

    if (chosen === previous) {
        return;
    }

    const other = [...event.currentTarget.querySelectorAll(
        'select[data-tie-bucket][data-tie-member]',
    )].find(candidate =>
        candidate !== select &&
        candidate.dataset.tieBucket === select.dataset.tieBucket &&
        candidate.value === chosen,
    );

    if (other) {
        other.value = previous;
        other.dataset.tiePosition = previous;
    }

    select.dataset.tiePosition = chosen;
}

document.querySelector('#tieGroups').addEventListener('change', swapTiePosition);

function readTieOrder() {
    const ties = tiedBuckets();
    const orderedBuckets = [];

    for (let index = 0; index < ties.length; index++) {
        const bucket = ties[index];
        const selections = [
            ...document.querySelectorAll(`[data-tie-bucket="${index}"]`),
        ];

        if (selections.length !== bucket.members.length) {
            throw new Error('Tie selection data is incomplete');
        }

        const positions = selections.map(select => Number(select.value));

        if (new Set(positions).size !== positions.length) {
            throw new Error(
                'Each combatant in an initiative tie must have a unique position',
            );
        }

        const positionsByMember = new Map(
            selections.map(select => [
                select.dataset.tieMember,
                Number(select.value),
            ]),
        );

        orderedBuckets.push(
            bucket.members
                .slice()
                .sort((left, right) =>
                    positionsByMember.get(left.id) - positionsByMember.get(right.id),
                )
                .map(combatant => combatant.id),
        );
    }

    return orderedBuckets;
}

// Install point wrapped by admin-initial-visibility.js (typed feedback, Start collapse).
// Start/tie confirmation, Next, End and Reset All controls are bound by
// admin-start-validation.js, battle-actions-next.js, admin-end-feedback.js and
// admin-reset-all-feedback.js. Errors propagate to the owning caller.
async function startBattle(order) {
    await request('/api/battle/start', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({order}),
    });
    await load();
}

document.querySelector('#cancelOrder').onclick = () => {
    document.querySelector('#tieModal').hidden = true;
};

let battleOrderFontAdjustmentPending = false;

function updateBattleOrderFontControls(fontSize) {
    const numericSize = Number(fontSize);
    const size = Number.isInteger(numericSize)
        ? Math.max(12, Math.min(40, numericSize))
        : 16;

    const label = document.querySelector('#battleOrderFontSize');
    const decrease = document.querySelector('#battleOrderFontDecrease');
    const increase = document.querySelector('#battleOrderFontIncrease');

    if (label) {
        label.textContent = `${size} px`;
    }

    if (decrease) {
        decrease.disabled = (
            battleOrderFontAdjustmentPending || size <= 12
        );
    }

    if (increase) {
        increase.disabled = (
            battleOrderFontAdjustmentPending || size >= 40
        );
    }
}

// Stage 1 Steps 1A/1B: campaign creation and metadata editing feedback.
(() => {
    const form = document.querySelector('#campaignForm');
    if (!form || typeof form.onsubmit !== 'function' || typeof openCampaignModal !== 'function' ||
        typeof closeCampaignModal !== 'function') return;
    const previousOpen = openCampaignModal, previousClose = closeCampaignModal;
    const previousSubmit = form.onsubmit;
    let session = null, sequence = 0, pending = false;
    openCampaignModal = function(...args) {
        session = {id: ++sequence, revision: 0, closed: false};
        return previousOpen.apply(this, args);
    };
    closeCampaignModal = function(...args) {
        if (session) session.closed = true;
        return previousClose.apply(this, args);
    };
    // The earlier cancel button captured the original close function by value.
    document.querySelector('#cancelCampaign').onclick = closeCampaignModal;
    for (const type of ['input', 'change', 'reset']) form.addEventListener(type, () => {
        if (session) session.revision++;
    });
    const editButton = document.querySelector('#editCampaign');
    if (editButton && typeof campaignById === 'function') editButton.onclick = () => {
        const feedback = window.scryingAdminFeedback;
        const validation = feedback.begin({lane: 'page', region: 'campaign', operation: 'campaign.edit.open',
            target: 'campaign-edit-selection', label: 'Choose campaign to edit', field: '#campaignSelect'});
        const campaign = campaignById(document.querySelector('#campaignSelect').value);
        if (!campaign) {
            feedback.publish(validation, {severity: 'error', text: 'Choose a campaign to edit'});
            return;
        }
        feedback.resolve(validation);
        openCampaignModal(campaign);
    };
    async function saveCampaignEdit(event) {
        event.preventDefault();
        if (!session || session.closed) return;
        const owner = session, revision = owner.revision, id = campaignEditing;
        const registry = campaignData, select = document.querySelector('#campaignSelect'), selection = select.value;
        const feedback = window.scryingAdminFeedback, origin = feedback.encounterContext();
        const spec = {lane: 'page', region: 'campaign', target: JSON.stringify(['campaign-edit', id]),
            label: 'Save campaign'};
        const begin = (suffix, field) => feedback.begin({...spec, operation: 'campaign.edit' + suffix, ...(field ? {field} : {})});
        const validation = begin('.validation');
        const values = [form.elements.name.value, form.elements.description.value];
        const name = values[0].trim(), description = values[1].trim();
        if (!name || !form.reportValidity()) {
            const field = feedback.field?.(!name ? form.elements.name : form);
            feedback.publish(field ? begin('.validation', field) : validation, {severity: 'error', text: !name
                ? 'Enter a campaign name' : 'Enter valid campaign details.'});
            return;
        }
        feedback.resolve(validation);
        const ticket = begin(''), render = begin('.render');
        const button = document.querySelector('#campaignSubmit'), disabled = button.disabled;
        let result, applied = false, closedByAttempt = false;
        const relevant = (ownRender = false) => {
            const now = feedback.encounterContext();
            return feedback.isCurrent(render) && session === owner &&
                (!owner.closed || closedByAttempt) && campaignEditing === (closedByAttempt ? null : id) &&
                now.scope === origin.scope && now.epoch === origin.epoch &&
                campaignData === (applied ? result : registry) && (ownRender || select.value === selection);
        };
        const currentDraft = () => owner.revision === revision &&
            form.elements.name.value === values[0] && form.elements.description.value === values[1];
        pending = true;
        button.disabled = true;
        try {
            try {
                result = await request(`/api/campaigns/${encodeURIComponent(id)}`, {
                    method: 'PATCH', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name, description}),
                });
            } catch (error) {
                if (relevant() && currentDraft()) feedback.publish(ticket, {severity: 'error', text: error.message});
                return;
            }
            if (!relevant()) return;
            campaignData = result;
            applied = true;
            try {
                if (currentDraft()) {
                    feedback.publish(ticket, {severity: 'success', text: `Updated campaign: ${name}`});
                    if (!relevant()) return;
                    closedByAttempt = true;
                    closeCampaignModal();
                } else feedback.resolve(ticket);
                if (!relevant()) return;
                try { renderCampaigns(); } finally {
                    // Restore only our own rendering's selection change, never a newer session.
                    if (relevant(true)) select.value = selection;
                }
                if (relevant()) feedback.resolve(render);
            } catch (error) {
                if (relevant() && currentDraft()) feedback.publish(render, {severity: 'error', text:
                    `Campaign saved, but updating the view failed: ${error.message}. Reload the page; do not save the campaign again to retry the view update.`});
            }
        } finally {
            button.disabled = disabled;
            pending = false;
        }
    }
    form.onsubmit = async function(event) {
        if (pending) {event.preventDefault(); return;}
        if (campaignEditing) return saveCampaignEdit(event);
        event.preventDefault();
        if (!session || session.closed) return;
        const owner = session, revision = owner.revision;
        const feedback = window.scryingAdminFeedback;
        const spec = {lane: 'page', region: 'campaign', target: JSON.stringify(['campaign-create', owner.id]),
            label: 'Create campaign'};
        const begin = (suffix, field) => feedback.begin({...spec, operation: 'campaign.create' + suffix, ...(field ? {field} : {})});
        const validation = begin('.validation');
        const values = [form.elements.name.value, form.elements.description.value];
        const name = values[0].trim(), description = values[1].trim();
        if (!name || !form.reportValidity()) {
            const field = feedback.field?.(!name ? form.elements.name : form);
            feedback.publish(field ? begin('.validation', field) : validation, {severity: 'error', text: !name
                ? 'Enter a campaign name' : 'Enter valid campaign details.'});
            return;
        }
        feedback.resolve(validation);
        if (!confirm(`Create and switch to campaign ${name}?\n\n${REPLACE_WARNING}`)) return;
        const origin = feedback.encounterContext(), active = campaignData.active;
        const ticket = begin(''), refresh = begin('.refresh');
        const button = document.querySelector('#campaignSubmit'), disabled = button.disabled;
        let result, applied = false, closedByAttempt = false;
        const relevant = () => {
            if (!feedback.isCurrent(refresh) || session !== owner || (owner.closed && !closedByAttempt)) return false;
            const now = feedback.encounterContext();
            const unchanged = now.epoch === origin.epoch && now.scope === origin.scope;
            const expected = result && now.epoch === origin.epoch + 1 && now.scope ===
                JSON.stringify([result.active, result.opened_setup ? result.active : null, result.opened_setup || null]);
            return Boolean((unchanged || expected) && campaignData.active === (applied ? result.active : active));
        };
        const currentDraft = () => owner.revision === revision &&
            form.elements.name.value === values[0] && form.elements.description.value === values[1];
        pending = true;
        button.disabled = true;
        try {
            try {
                result = await request('/api/campaigns', {
                    method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name, description, activate: true}),
                });
            } catch (error) {
                if (relevant() && currentDraft()) feedback.publish(ticket, {severity: 'error', text: error.message});
                return;
            }
            if (!relevant()) return;
            campaignData = result;
            applied = true;
            try {
                if (currentDraft()) {
                    const opened = result.opened_setup ? `; opened battle setup ${result.opened_setup}` : '';
                    feedback.publish(ticket, {severity: 'success', text: `Created and switched to campaign: ${name}${opened}`});
                    if (!relevant()) return;
                    closedByAttempt = true;
                    closeCampaignModal();
                } else feedback.resolve(ticket);
                if (!relevant()) return;
                // Mirror existing creation setup-opening behavior, but propagate reload failure.
                // Do not change the shared helper used by switch/delete.
                renderCampaigns();
                if (!result.opened_setup) {
                    document.querySelector('#setupName').value = '';
                    document.querySelector('#setupSelect').value = '';
                    await load(true);
                    if (relevant()) renderActiveBattleSetup();
                } else {
                    document.querySelector('#setupName').value = result.opened_setup;
                    document.querySelector('#setupSelect').value = result.opened_setup;
                    syncActiveBattleSetupControls();
                    renderActiveBattleSetup();
                    await load(true);
                }
                if (relevant()) {
                    if (feedback.encounterContext().epoch === origin.epoch) {
                        throw new Error('The created campaign state was not applied');
                    }
                    feedback.resolve(refresh);
                }
            } catch (error) {
                if (relevant() && currentDraft()) feedback.publish(refresh, {severity: 'error', text:
                    `Campaign created and activated, but refresh failed: ${error.message}. Reload the page; do not create the campaign again to retry the refresh.`});
            }
        } finally {
            button.disabled = disabled;
            pending = false;
        }
    };
})();

async function adjustBattleOrderFont(direction) {
    if (battleOrderFontAdjustmentPending) return;
    const feedback = window.scryingAdminFeedback;
    const ticket = feedback.begin({region: 'global', operation: 'display.battle-order-font',
        target: 'battle-order', label: 'Change viewer font size'});
    battleOrderFontAdjustmentPending = true;

    try {
        updateBattleOrderFontControls(latest?.display?.battle_order_font_size);
        let result;
        try {
            result = await request('/api/display/battle-order-font', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({direction}),
            });
        } catch (error) {
            feedback.publish(ticket, {severity: 'error', text: error instanceof Error
                ? error.message : 'Unable to change viewer font size.'});
            return;
        }
        if (!feedback.isCurrent(ticket)) return;
        // Request succeeded: resolve only its error; UI failures are not POST failures.
        feedback.resolve(ticket);
        if (latest?.display) latest.display.battle_order_font_size = result.battle_order_font_size;
        updateBattleOrderFontControls(result.battle_order_font_size);
    } finally {
        battleOrderFontAdjustmentPending = false;
        updateBattleOrderFontControls(latest?.display?.battle_order_font_size);
    }
}

document.querySelector(
    '#battleOrderFontDecrease',
).addEventListener('click', () => {
    adjustBattleOrderFont('decrease');
});

document.querySelector(
    '#battleOrderFontIncrease',
).addEventListener('click', () => {
    adjustBattleOrderFont('increase');
});

installColorPreview('#monsterColor', '#monsterColorPreview');
installColorPreview('#monsterFileColor', '#monsterFileColorPreview',);
installColorPreview('#characterColor', '#characterColorPreview',);
installColorPreview('#backgroundColor', '#backgroundColorPreview',);

load();
setups();

// Stage 1 Step 1C.1: switch validation/request ownership; explicit success/refresh (1C.2).
(() => {
    if (typeof switchCampaign !== 'function') return;
    const select = document.querySelector('#campaignSelect'), button = document.querySelector('#switchCampaign');
    let pending = false, revision = 0;
    select.addEventListener('input', () => { revision++; });
    switchCampaign = async function() {
        if (pending) return;
        const feedback = window.scryingAdminFeedback, id = select.value;
        const selectionSpec = {lane: 'page', region: 'campaign', operation: 'campaign.switch.validation',
            target: 'campaign-switch-selection', label: 'Choose campaign to switch to', field: '#campaignSelect'};
        const validation = feedback.begin(selectionSpec);
        const revert = () => { select.value = campaignData.active || ''; };
        if (!id) {
            revert();
            feedback.publish(validation, {severity: 'error', text: 'Choose a campaign to switch to'});
            return;
        }
        if (id === campaignData.active) {
            feedback.resolve(validation);
            feedback.publish(feedback.begin(selectionSpec), {severity: 'info', text: `${activeCampaign()?.name || id} is already the active campaign`});
            return;
        }
        feedback.resolve(validation);
        const target = campaignById(id);
        if (!confirm(`Switch to campaign ${target ? target.name : id}?\n\n${REPLACE_WARNING}`)) { revert(); return; }
        const registry = campaignData, owner = revision, origin = feedback.encounterContext();
        const spec = {lane: 'page', region: 'campaign', operation: 'campaign.switch',
            target: JSON.stringify(['campaign-switch', id]), label: 'Switch campaign'};
        const ticket = feedback.begin(spec);
        const refresh = feedback.begin({...spec, operation: 'campaign.switch.refresh', label: 'Refresh switched campaign'});
        let result, applied = false;
        const same = () => {
            const now = feedback.encounterContext();
            const unchanged = now.epoch === origin.epoch && now.scope === origin.scope;
            const intended = result && now.epoch === origin.epoch + 1 && now.scope ===
                JSON.stringify([result.active, result.opened_setup ? result.active : null, result.opened_setup || null]);
            return feedback.isCurrent(refresh) && revision === owner && select.value === id &&
                campaignData === (applied ? result : registry) && (unchanged || intended);
        };
        const disabled = button.disabled;
        pending = true; button.disabled = true;
        try {
            try { result = await request(`/api/campaigns/${encodeURIComponent(id)}/activate`, {method: 'POST'}); }
            catch (error) {
                if (same() && feedback.isCurrent(ticket)) {
                    revert(); feedback.publish(ticket, {severity: 'error', text: error.message});
                }
                return;
            }
            if (!same() || !feedback.isCurrent(ticket)) return;
            campaignData = result;
            applied = true;
            try {
                const opened = result.opened_setup ? `; opened battle setup ${result.opened_setup}` : '';
                feedback.publish(ticket, {severity: 'success', text: `Switched to campaign: ${activeCampaign()?.name || id}${opened}`});
                if (!same()) return; // Refresh has its own live ticket; success settled the request ticket.
                document.querySelector('#setupSelect').value = '';
                renderCampaigns();
                if (!same()) return;
                if (!result.opened_setup) {
                    document.querySelector('#setupName').value = '';
                    document.querySelector('#setupSelect').value = '';
                    await load(true);
                    if (same()) renderActiveBattleSetup();
                } else {
                    document.querySelector('#setupName').value = result.opened_setup;
                    document.querySelector('#setupSelect').value = result.opened_setup;
                    syncActiveBattleSetupControls();
                    renderActiveBattleSetup();
                    await load(true);
                }
                if (same()) {
                    if (feedback.encounterContext().epoch === origin.epoch) {
                        throw new Error('Switched campaign state was not applied');
                    }
                    feedback.resolve(refresh);
                }
            } catch (error) {
                if (same()) feedback.publish(refresh, {severity: 'error', text:
                    `Campaign switched and activated, but refresh failed: ${error.message}. Reload the page; do not switch the campaign again to retry the refresh.`});
            }
        } finally { button.disabled = disabled; pending = false; }
    };
    button.onclick = switchCampaign;
    select.onchange = () => { revision++; return switchCampaign(); };
})();
