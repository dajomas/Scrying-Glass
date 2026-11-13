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
        `Looking up ${species} (D&D Beyond, then 5e.tools)…`,
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

