let latest;
let editing = null;

const selectedCharacterIds = new Set();
const selectedMonsterIds = new Set();

let monsterSpeciesLookupTimer = null;
let monsterSpeciesLookupRequest = 0;

function setMonsterSpeciesLookupStatus(text, options = {}) {
    const {
        timed = false,
    } = options;

    const notification = document.querySelector(
        '#monsterAddNotification',
    );

    if (!notification) {
        return;
    }

    if (timed) {
        paneNotification('monsters', text);
        return;
    }

    clearTimeout(paneNotificationTimeouts.monsters);
    paneNotificationTimeouts.monsters = null;
    notification.textContent = (text === '') ? ' ' : text;
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

    const originalAc = acInput.value;
    const originalHpStart = hpStartInput.value;
    const originalHpEnd = hpEndInput.value;

    function isCurrentRequest() {
        return (
            requestId === monsterSpeciesLookupRequest &&
            speciesInput.value.trim() === species &&
            Boolean(overwriteInput?.checked) === overwriteFoundStats
        );
    }

    setMonsterSpeciesLookupStatus(
        `Looking up ${species} on D&D Beyond…`,
    );

    try {
        const suggestion = await request(
            `/api/dndbeyond/monster-stats?species=${encodeURIComponent(species)}`,
        );

        if (!isCurrentRequest()) {
            return;
        }

        if (!suggestion || suggestion.found !== true) {
            paneNotification(
                'monsters',
                suggestion?.reason
                    ? String(suggestion.reason)
                    : `No usable D&D Beyond stats found for ${species}; ` +
                      'enter AC and HP manually.',
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

        const edition = suggestion.legacy ? 'legacy' : 'current';

        if (changes.length) {
            paneNotification(
                'monsters',
                `Loaded ${changes.join(', ')} from the ` +
                `${edition} D&D Beyond result.`,
            );
            return;
        }

        if (!acUnchanged || !hpUnchanged) {
            paneNotification(
                'monsters',
                `Found ${edition} D&D Beyond stats; values edited ` +
                'while the lookup was running were left unchanged.',
            );
            return;
        }

        if (overwriteFoundStats) {
            paneNotification(
                'monsters',
                `Found ${edition} D&D Beyond stats, but no usable ` +
                'AC or HP values were returned.',
            );
        } else {
            paneNotification(
                'monsters',
                `Found ${edition} D&D Beyond stats; existing AC ` +
                'and HP were left unchanged. Enable overwrite to replace them.',
            );
        }
    } catch (error) {
        if (!isCurrentRequest()) {
            return;
        }

        console.debug(
            'Optional D&D Beyond stats lookup failed:',
            error,
        );

        setMonsterSpeciesLookupStatus(
            'D&D Beyond lookup is unavailable; enter AC and HP manually.',
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

const message = text => {
    document.querySelector('#message').textContent = text;
};

const paneNotificationTimeouts = {
    characters: null,
    monsters: null,
    campaign: null,
    battleSetup: null,
};

const paneNotificationIds = {
    characters: '#characterAddNotification',
    monsters: '#monsterAddNotification',
    campaign: '#campaignNotification',
    battleSetup: '#battleSetupNotification',
};

const paneNotification = (kind, text) => {
    const notification = document.querySelector(
        paneNotificationIds[kind],
    );

    if (!notification) {
        console.error(
            `Missing notification element for pane: ${kind}`,
        );
        return;
    }

    clearTimeout(paneNotificationTimeouts[kind]);

    notification.textContent = text;

    paneNotificationTimeouts[kind] = setTimeout(() => {
        notification.textContent = ' ';
        paneNotificationTimeouts[kind] = null;
    }, 3_000);
};

const all = () => [
    ...latest.monsters,
    ...latest.characters,
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

async function request(url, options = {}) {
    const response = await fetch(url, options);

    if (response.ok) {
        return response.json().catch(() => null);
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

    if (!ids.length) {
        paneNotification(kind, selectionMessage(kind));
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

    try {
        const result = await bulkRequest(kind, action, ids);
        const count = Number(result?.count ?? ids.length);
        paneNotification(kind, `${count} ${kind === 'characters' ? 'character' : 'monster'}${count === 1 ? '' : 's'} updated.`);
        await load();
    } catch (error) {
        paneNotification(kind, error.message);
    }
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

    try {
        await bulkRequest(kind, 'remove', [id]);

        paneNotification(kind, `${noun[0].toUpperCase()}${noun.slice(1)} ` + `“${item.name}” removed.`);

        await load();
    } catch (error) {
        paneNotification(kind, error.message);
    }
}

async function patch(kind, id, data) {
    try {
        await request(`/api/${kind}/${encodeURIComponent(id)}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        await load();
    } catch (error) {
        paneNotification(kind, error.message);
    }
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
    <tr class="${character.alive ? '' : 'dead'}">
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
        <button class="${character.alive ? 'on' : ''}" data-cl="${esc(character.id)}">${character.alive ? 'Alive' : 'Dead'}</button>
        <button class="${character.visible ? 'on' : ''}" data-cv="${esc(character.id)}">Visible</button>
        <button data-ct="${esc(character.id)}" class="${character.in_turn ? 'on' : ''}">Turn</button>
        <button data-cr="${esc(character.id)}" class="reset">Reset</button>
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
        Name <span class="required-marker" aria-hidden="true">*</span>
        <input name="name" required value="${esc(monster.name)}">
    </label>
    <label>
        Monster species <span class="required-marker" aria-hidden="true">*</span>
        <input name="monster_species" required value="${esc(monster.monster_species)}">
    </label>
    <label>
        AC <span class="required-marker" aria-hidden="true">*</span>
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
        Current HP <span class="required-marker" aria-hidden="true">*</span>
        <input name="hp" type="number" value="${monster.hp}">
    </label>
    <label>
        Max HP <span class="required-marker" aria-hidden="true">*</span>
        <input name="max_hp" type="number" min="0" value="${monster.max_hp}">
    </label>
    <label>
        Reset HP <span class="required-marker" aria-hidden="true">*</span>
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
        Name <span class="required-marker" aria-hidden="true">*</span>
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
        Current HP <span class="required-marker" aria-hidden="true">*</span>
        <input name="hp" type="number" value="${character.hp}">
    </label>
    <label>
        Max HP <span class="required-marker" aria-hidden="true">*</span>
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

async function setups() {
    try {
        campaignData = await request('/api/campaigns');
        renderCampaigns();

        if (campaignData.moved && campaignData.moved.length) {
            paneNotification('campaign', `Moved ${campaignData.moved.length} unassigned setup(s) into campaign Default: ` + campaignData.moved.join(', '));
        }
    } catch (error) {
        paneNotification('campaign', error.message);
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

async function load() {
    try {
        latest = await request('/api/state');

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

        document.querySelector('#backgroundColor').onclick = () => {
            document.querySelector('#backgroundColor').showPicker?.();
        };

        document.querySelector('#backgroundColor').oninput = event => {
            document.querySelector('#backgroundValue').value = event.target.value;
        };

        document.querySelector('#applyBackground').onclick = async () => {
            try {
                await applyBackground(
                    document.querySelector('#backgroundValue').value.trim() || '#080b14',
                );
                paneNotification('battleSetup', 'View screen background updated. Save the setup to keep it.');
            } catch (error) {
                paneNotification('battleSetup', error.message);
            }
        };

        document.querySelector('#clearBackgroundImage').onclick = async () => {
            try {
                await applyBackground(document.querySelector('#backgroundColor').value);
                paneNotification('battleSetup', 'View screen now uses the selected background color.');
            } catch (error) {
                paneNotification('battleSetup', error.message);
            }
        };

        document.querySelector('#backgroundImage').onchange = async event => {
            const [image] = event.target.files;

            if (!image) {
                return;
            }

            try {
                const form = new FormData();
                form.append('image', image);

                const result = await request('/api/display/background-image', {
                    method: 'POST',
                    body: form,
                });

                document.querySelector('#backgroundValue').value = result.background;
                await load();
                paneNotification('battleSetup', 'Background image uploaded. Save the setup to keep it.');
            } catch (error) {
                paneNotification('battleSetup', error.message);
            } finally {
                event.target.value = '';
            }
        };

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

    } catch (error) {
        message(error.message);
    }
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
        child: 'characterInput',
        saved: null,
    },
    battleSetup: {
        child: 'monsterInput',
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

    if (!dependency) {
        return;
    }

    const child = paneControlByKey.get(dependency.child);

    if (!child) {
        return;
    }

    /*
    * Save the child's original state only once per parent-hide cycle.
    * This prevents repeated page refreshes or repeated calls from overwriting
    * the original state with the forced-hidden state.
    */
    if (dependency.saved === null) {
        dependency.saved = {
            paneHidden: child.pane.hidden,
            buttonHidden: child.button.hidden,
        };
    }

    /*
    * Hide both the child input pane and its individual Show/Hide button.
    * The button must be hidden too: users must not be able to show a pane
    * whose parent is hidden.
    */
    child.pane.hidden = true;
    child.button.hidden = true;
}

function restoreDependentPane(parentKey) {
    const dependency = paneDependencies[parentKey];

    if (!dependency || dependency.saved === null) {
        return;
    }

    const child = paneControlByKey.get(dependency.child);
    const saved = dependency.saved;

    if (!child) {
        dependency.saved = null;
        return;
    }

    /*
    * Restore the child pane's original hidden state through the standard
    * function, so button wording and aria-expanded remain correct.
    */
    setPaneHidden(child, saved.paneHidden);

    /*
    * Restore whether the child toggle button itself was visible.
    * Normally this is false, but storing it makes restoration exact and
    * avoids coupling to other UI rules.
    */
    child.button.hidden = saved.buttonHidden;

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
    hideablePanes.forEach(control => setPaneHidden(control, hidden));
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

document.querySelector('#editForm').onsubmit = async event => {
    event.preventDefault();

    if (!editing) {
        return;
    }

    const form = event.target;
    const data = {
        name: form.elements.name.value.trim(),
        color: form.elements.color.value,
        hp: numberValue(form, 'hp', 0),
        max_hp: numberValue(form, 'max_hp', 0),
        initiative: form.elements.initiative.value === ''
            ? null
            : +form.elements.initiative.value,
    };

    if (editing.kind === 'monsters') {
        data.monster_species = form.elements.monster_species.value.trim();
        data.ac = numberValue(form, 'ac', 0);
        data.original_hp = numberValue(form, 'original_hp', 0);
        data.ally = form.elements.ally.value === 'true';

        const image = form.elements.image.files[0];

        try {
            if (image) {
                const formData = new FormData();

                Object.entries(data).forEach(([key, value]) => {
                    formData.append(key, value === null ? '' : String(value));
                });

                formData.append('image', image);

                const response = await fetch(
                    `/api/monsters/${encodeURIComponent(editing.id)}/edit`,
                    {
                        method: 'POST',
                        body: formData,
                    },
                );

                if (!response.ok) {
                    const error = await response.json().catch(() => ({
                        detail: response.statusText,
                    }));

                    throw new Error(error.detail);
                }
            } else {
                await request(`/api/monsters/${encodeURIComponent(editing.id)}`, {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data),
                });
            }
        } catch (error) {
            paneNotification('monsters', error.message);
            return;
        }
    } else {
        if (data.initiative === null) {
            delete data.initiative;
        }

        try {
            await request(`/api/characters/${encodeURIComponent(editing.id)}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });
        } catch (error) {
            paneNotification('character', error.message);
            return;
        }
    }

    closeEdit();
    await load();
};

document.querySelector('#openImport').onclick = async () => {
    await setups();
    document.querySelector('#importCampaign').value = campaignData.active || '';
    renderImportSetups();
    importModal.hidden = false;
};

document.querySelector('#importCampaign').onchange = renderImportSetups;

document.querySelector('#cancelImport').onclick = closeImport;

document.querySelector('#importForm').onsubmit = async event => {
    event.preventDefault();

    const formData = new FormData(event.target);
    const name = formData.get('name');
    const kind = formData.get('kind');
    const campaign = formData.get('campaign') || campaignData.active;

    if (!name) {
        paneNotification('setup', 'Choose a saved setup to import from');
        return;
    }

    if (!confirm(`Import ${kind} from ${name} into the current setup?`)) {
        return;
    }

    try {
        const result = await request('/api/setups/import', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, kind, campaign }),
        });

        closeImport();
        await load();

        paneNotification(
            'battleSetup',
            `Imported ${result.monsters} monster${result.monsters === 1 ? '' : 's'} from ${result.name}`,
        );
    } catch (error) {
        paneNotification('battleSetup', error.message);
    }
};

function closeCsvImport() {
    csvImportModal.hidden = true;
    csvImportKind = null;
    document.querySelector('#csvImportForm').reset();
}

function openCsvImport(kind) {
    csvImportKind = kind;

    const isMonster = kind === 'monsters';

    document.querySelector('#csvImportTitle').textContent =
        isMonster ? 'Import monsters from CSV' : 'Import characters from CSV';

    document.querySelector('#csvImportHelp').textContent =
        isMonster
            ? 'Required columns: name, monster_species, ac, hp. Optional id values are preserved; blank or missing IDs are generated automatically.'
            : 'Required column: name. Imported characters are added to the active campaign. Optional id values are preserved; blank or missing IDs are generated automatically.';

    csvImportModal.hidden = false;
}

document.querySelector('#openMonsterCsvImport').onclick = () => {
    openCsvImport('monsters');
};

document.querySelector('#openCharacterCsvImport').onclick = () => {
    openCsvImport('characters');
};

document.querySelector('#cancelCsvImport').onclick = closeCsvImport;

document.querySelector('#csvImportForm').onsubmit = async event => {
    event.preventDefault();

    if (!csvImportKind) {
        return;
    }

    const form = event.target;
    const submit = form.querySelector('button[type="submit"], button.import');

    submit.disabled = true;

    try {
        const endpoint = csvImportKind === 'monsters'
            ? '/api/monsters/import-csv'
            : '/api/characters/import-csv';

        const result = await request(endpoint, {
            method: 'POST',
            body: new FormData(form),
        });

        closeCsvImport();
        await load();

        paneNotification(
            csvImportKind === 'characters' ? 'campaign' : 'battleSetup',
            `Imported ${result.count} ${csvImportKind === 'monsters' ? 'monster' : 'character'
            }${result.count === 1 ? '' : 's'} from CSV.`,
        );

        const count = Number(result?.count ?? 0);
        const noun = csvImportKind === 'characters' ? 'character' : 'monster';
        const target = csvImportKind === 'characters' ? 'characters' : 'monsters';

        paneNotification(
            target,
            `${count} ${noun}${count === 1 ? '' : 's'} added successfully.`,
        );
    } catch (error) {
        paneNotification(csvImportKind === 'characters' ? 'campaign' : 'battleSetup', error.message);
    } finally {
        submit.disabled = false;
    }
};

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

    if (!currentCount) {
        message('The activity log is already empty.');
        return;
    }

    if (!confirm(`Clear all ${currentCount} activity log entries?`)) {
        return;
    }

    try {
        const result = await request('/api/activity-log/clear', {
            method: 'POST',
        });

        await load();

        message(
            `Cleared ${result.cleared} activity log ${result.cleared === 1 ? 'entry' : 'entries'
            }.`,
        );
    } catch (error) {
        message(error.message);
    }
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

document.querySelector('#rollMonsterInitiative').onclick = async () => {
    if (!latest.monsters.length) {
        paneNotification('monsters', 'There are no monsters to roll initiative for');
        return;
    }

    if (!confirm('Overwrite initiative for every monster with a random d20 roll?')) {
        return;
    }

    try {
        const result = await request('/api/monsters/roll-initiative', {
            method: 'POST',
        });

        await load();
        paneNotification('monsters', `Rolled d20 initiative for ${result.count} monster(s)`);
    } catch (error) {
        paneNotification('monsters', error.message);
    }
};

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

document.querySelector('#editCampaign').onclick = () => {
    const campaign = campaignById(document.querySelector('#campaignSelect').value);
    if (!campaign) {
        paneNotification('campaign', 'Choose a campaign to edit');
        return;
    }
    openCampaignModal(campaign);
};

// After a campaign is activated the server opens its most recently worked on
// (or newest) battle setup. Reflect that in the setup controls and reload state.
async function applyOpenedSetup(result) {
    renderCampaigns();

    if (!result || !result.opened_setup) {
        renderActiveBattleSetup();
        return '';
    }

    document.querySelector('#setupName').value = result.opened_setup;
    document.querySelector('#setupSelect').value = result.opened_setup;

    syncActiveBattleSetupControls();
    renderActiveBattleSetup();

    await load();

    return `; opened battle setup ${result.opened_setup}`;
}

const REPLACE_WARNING =
    'The current battle will be replaced by the campaign\'s most recently used battle setup. ' +
    'Unsaved changes will be lost.';

document.querySelector('#campaignForm').onsubmit = async event => {
    event.preventDefault();
    const form = event.target;
    const name = form.elements.name.value.trim();
    const description = form.elements.description.value.trim();

    if (!name) {
        paneNotification('campaign', 'Enter a campaign name');
        return;
    }

    try {
        if (campaignEditing) {
            campaignData = await request(`/api/campaigns/${encodeURIComponent(campaignEditing)}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, description }),
            });
            paneNotification('campaign', `Updated campaign: ${name}`);
        } else {
            if (!confirm(`Create and switch to campaign ${name}?\n\n${REPLACE_WARNING}`)) {
                return;
            }
            campaignData = await request('/api/campaigns', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, description, activate: true }),
            });
            closeCampaignModal();
            const opened = await applyOpenedSetup(campaignData);
            paneNotification('campaign', `Created and switched to campaign: ${name}${opened}`);
            return;
        }
        closeCampaignModal();
        renderCampaigns();
    } catch (error) {
        paneNotification('campaign', error.message);
    }
};

async function switchCampaign() {
    const campaignSelect = document.querySelector('#campaignSelect');
    const campaignId = campaignSelect.value;
    // Put the dropdown back on the active campaign when the switch does not happen.
    const revert = () => { campaignSelect.value = campaignData.active || ''; };
    if (!campaignId) {
        revert();
        paneNotification('campaign', 'Choose a campaign to switch to');
        return;
    }
    if (campaignId === campaignData.active) {
        paneNotification('campaign', `${activeCampaign()?.name || campaignId} is already the active campaign`);
        return;
    }
    const target = campaignById(campaignId);
    if (!confirm(`Switch to campaign ${target ? target.name : campaignId}?\n\n${REPLACE_WARNING}`)) {
        revert();
        return;
    }
    try {
        campaignData = await request(`/api/campaigns/${encodeURIComponent(campaignId)}/activate`, {
            method: 'POST',
        });
        document.querySelector('#setupSelect').value = '';
        const opened = await applyOpenedSetup(campaignData);
        paneNotification('campaign', `Switched to campaign: ${activeCampaign()?.name || campaignId}${opened}`);
    } catch (error) {
        revert();
        paneNotification('campaign', error.message);
    }
}

document.querySelector('#switchCampaign').onclick = switchCampaign;
// Selecting another campaign in the dropdown switches to it immediately.
document.querySelector('#campaignSelect').onchange = switchCampaign;

// The delete dialog lets the admin choose WHICH campaign to delete. The
// "move setups to" list always excludes the campaign chosen for deletion.
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
    if (campaignData.campaigns.length <= 1) {
        paneNotification('campaign', 'The last remaining campaign cannot be deleted');
        return;
    }
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

document.querySelector('#campaignDeleteTarget').onchange = renderCampaignDeleteDialog;
document.querySelector('#campaignDeleteAction').onchange = renderCampaignDeleteDialog;

document.querySelector('#campaignDeleteForm').onsubmit = async event => {
    event.preventDefault();
    const campaignId = document.querySelector('#campaignDeleteTarget').value;
    const campaign = campaignById(campaignId);
    if (!campaign) {
        paneNotification('campaign', 'Choose a campaign to delete');
        return;
    }
    const moveTo = document.querySelector('#campaignDeleteMoveTo').value;
    const hasSetups = campaign.setups.length > 0;
    const deleteSetups = hasSetups && document.querySelector('#campaignDeleteAction').value === 'delete';
    if (hasSetups && !deleteSetups && (!moveTo || moveTo === campaignId)) {
        paneNotification('campaign', 'Choose another campaign to move the battle setups to');
        return;
    }
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
    try {
        const result = await request(`/api/campaigns/${encodeURIComponent(campaignId)}${query}`, {
            method: 'DELETE',
        });
        campaignData = result;
        campaignDeleteModal.hidden = true;
        document.querySelector('#setupSelect').value = '';
        const opened = await applyOpenedSetup(result);
        paneNotification(
            'campaign',
            `Deleted campaign: ${campaign ? campaign.name : campaignId}` +
            (result.moved && result.moved.length ? ` (moved ${result.moved.length} setup(s))` : '') +
            (result.deleted_setups && result.deleted_setups.length ? ` (deleted ${result.deleted_setups.length} setup(s))` : '') +
            opened,
        );
    } catch (error) {
        paneNotification('campaign', error.message);
    }
};

document.querySelector('#openCampaignSetup').onclick = async () => {
    await setups();
    if (campaignData.campaigns.length < 2) {
        paneNotification('campaign', 'Create a second campaign first; setups can only be added from another campaign');
        return;
    }
    const target = document.querySelector('#campaignSelect').value || campaignData.active;
    const source = campaignData.campaigns.find(item => item.id !== target && item.setups.length)
        || campaignData.campaigns.find(item => item.id !== target);
    document.querySelector('#campaignSetupFrom').innerHTML = campaignOptions(source.id);
    document.querySelector('#campaignSetupTo').innerHTML = campaignOptions(target);
    renderCampaignSetupNames();
    campaignSetupModal.hidden = false;
};

document.querySelector('#campaignSetupFrom').onchange = renderCampaignSetupNames;

document.querySelector('#campaignSetupForm').onsubmit = async event => {
    event.preventDefault();
    const formData = new FormData(event.target);

    const from_campaign = formData.get('from_campaign');
    const setup = formData.get('setup');
    const to = formData.get('to_campaign');
    const mode = formData.get('mode');

    if (!setup) {
        paneNotification('campaign', 'Choose a battle setup');
        return;
    }
    if (from_campaign === to) {
        paneNotification('campaign', 'Source and target campaign are the same');
        return;
    }

    try {
        const result = await request(`/api/campaigns/${encodeURIComponent(to)}/setups`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ setup, from_campaign, mode }),
        });
        campaignData = result;
        campaignSetupModal.hidden = true;
        renderCampaigns();
        paneNotification(
            'campaign',
            `${mode === 'copy' ? 'Copied' : 'Moved'} setup ${setup} to campaign ` +
            `${campaignById(result.campaign)?.name || result.campaign}` +
            (result.setup !== setup ? ` as ${result.setup}` : ''),
        );
    } catch (error) {
        paneNotification('campaign', error.message);
    }
};

document.querySelector('#newSetup').onclick = async () => {
    const setupNameInput = document.querySelector('#setupName');
    const name = setupNameInput.value.trim();
    const activeCampaignName = activeCampaign()?.name || campaignData.active;

    if (!name) {
        paneNotification(
            'battleSetup',
            'Enter a unique battle setup name before creating it.',
        );
        setupNameInput.focus();
        return;
    }

    const existingNames = (activeCampaign()?.setups || [])
        .map(setupName => setupName.toLocaleLowerCase());

    if (existingNames.includes(name.toLocaleLowerCase())) {
        paneNotification(
            'battleSetup',
            `A battle setup named “${name}” already exists in ${activeCampaignName}.`,
        );
        setupNameInput.focus();
        return;
    }

    if (!confirm(
        `Discard the current battle setup and create a new empty setup named “${name}”?`,
    )) {
        return;
    }

    try {
        // First replace the current working encounter with an empty one.
        await request('/api/setups/new', {
            method: 'POST',
        });

        // Then persist it immediately using the requested unique name.
        const result = await request('/api/setups/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name,
                campaign: campaignData.active,
            }),
        });

        setupNameInput.value = result.name;

        // Refresh the campaign/setup lists, then select the saved setup.
        await setups();
        document.querySelector('#setupSelect').value = result.name;

        syncActiveBattleSetupControls();
        renderActiveBattleSetup();

        await load();

        paneNotification(
            'battleSetup',
            `Created and saved empty battle setup “${result.name}”.`,
        );
    } catch (error) {
        paneNotification('battleSetup', error.message);
    }
};

document.querySelector('#saveSetup').onclick = async () => {
    const name = document.querySelector('#setupName').value.trim();

    if (!name) {
        paneNotification('battleSetup', 'Enter a battle setup name before saving');
        return;
    }

    try {
        const result = await request('/api/setups/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, campaign: campaignData.active }),
        });

        document.querySelector('#setupName').value = result.name;
        await setups();
        document.querySelector('#setupSelect').value = result.name;

        syncActiveBattleSetupControls();
        renderActiveBattleSetup();

        paneNotification('battleSetup', `Saved setup: ${result.name} (campaign: ${campaignById(result.campaign)?.name || result.campaign})`);
    } catch (error) {
        paneNotification('battleSetup', error.message);
    }
};

async function loadSelectedSetup(event) {
    const setupSelect = document.querySelector('#setupSelect');
    const name = setupSelect.value;
    const fromDropdown = event && event.type === 'change';
    // Put the dropdown back on the currently loaded setup when the load does not happen.
    const revert = () => {
        const current = document.querySelector('#setupName').value;
        setupSelect.value = [...setupSelect.options].some(option => option.value === current) ? current : '';
    };

    if (!name) {
        if (!fromDropdown) {
            paneNotification('battleSetup', 'Choose a saved setup to load');
        }
        return;
    }

    if (!confirm(`Load ${name} and replace the current battle setup?`)) {
        revert();
        return;
    }

    try {
        const result = await request('/api/setups/load', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name,
                campaign: campaignData.active,
            }),
        });

        document.querySelector('#setupName').value = result.name;
        document.querySelector('#setupSelect').value = result.name;

        syncActiveBattleSetupControls();
        renderActiveBattleSetup();

        await load();

        paneNotification('battleSetup',
            `Loaded setup ${result.name} in campaign `
            + `${campaignById(result.campaign)?.name || result.campaign}`,
        );
    } catch (error) {
        revert();
        paneNotification('battleSetup', error.message);
    }
}

document.querySelector('#loadSetup').onclick = loadSelectedSetup;
// Selecting another battle setup in the dropdown loads it immediately.
document.querySelector('#setupSelect').onchange = loadSelectedSetup;

document.querySelector('#renameSetup').onclick = async () => {
    const name = document.querySelector('#setupSelect').value;
    if (!name) {
        paneNotification('battleSetup', 'Choose a saved setup to rename');
        return;
    }
    const newName = prompt(`Rename battle setup ${name} to:`, name);
    if (newName === null || !newName.trim() || newName.trim() === name) {
        return;
    }
    try {
        const result = await request('/api/setups/rename', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, new_name: newName.trim(), campaign: campaignData.active }),
        });
        if (document.querySelector('#setupName').value.trim() === name) {
            document.querySelector('#setupName').value = result.name;
        }

        await setups();
        document.querySelector('#setupSelect').value = result.name;

        syncActiveBattleSetupControls();
        renderActiveBattleSetup();

        paneNotification('battleSetup', `Renamed battle setup ${result.old_name} to ${result.name}`);
    } catch (error) {
        paneNotification('battleSetup', error.message);
    }
};

document.querySelector('#deleteSetup').onclick = async () => {
    const name = document.querySelector('#setupSelect').value;
    if (!name) {
        paneNotification('battleSetup', 'Choose a saved setup to delete');
        return;
    }
    if (!confirm(
        `Delete battle setup ${name} from campaign ${activeCampaign()?.name || campaignData.active}?\n\n` +
        'The next battle setup is opened afterwards (an empty "default" setup is created if this was the last one). ' +
        'Unsaved changes to the current battle will be lost.',
    )) {
        return;
    }
    try {
        const result = await request(
            `/api/setups/${encodeURIComponent(name)}?campaign=${encodeURIComponent(campaignData.active || '')}`,
            { method: 'DELETE' },
        );
        await setups();

        document.querySelector('#setupName').value = result.opened_setup;
        document.querySelector('#setupSelect').value = result.opened_setup;

        syncActiveBattleSetupControls();
        renderActiveBattleSetup();

        await load();

        paneNotification(
            'battleSetup',
            `Deleted battle setup ${result.deleted}; opened `
            + `${result.created_default ? 'new empty setup ' : ''}`
            + `${result.opened_setup}`,
        );
    } catch (error) {
        paneNotification('battleSetup', error.message);
    }
};

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

document.querySelector('#monsterForm').onsubmit = async event => {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);

    const hpRangeStart = String(
        formData.get('hprangestart') ?? ''
    ).trim();

    const hpRangeEnd = String(
        formData.get('hprangeend') ?? ''
    ).trim();

    const hpValidationError = validateMonsterHpRange(
        hpRangeStart,
        hpRangeEnd,
    );

    if (hpValidationError) {
        paneNotification('monsters', hpValidationError);

        const startIsInvalid =
            !hpRangeStart ||
            (
                !isDiceHpExpression(hpRangeStart) &&
                parseNonNegativeInteger(hpRangeStart) === null
            );

        (
            startIsInvalid
                ? form.elements.hprangestart
                : form.elements.hprangeend
        )?.focus();

        return;
    }

    // Submit normalized strings. In particular, retain a valid dice expression
    // such as "3d8+9" rather than converting it into Number/NaN.
    formData.set('hprangestart', hpRangeStart);
    formData.set('hprangeend', hpRangeEnd);

    const name = String(formData.get('name') ?? '').trim();

    try {
        const created = await request('/api/monsters', {
            method: 'POST',
            body: formData,
        });

        const count = Array.isArray(created) ? created.length : 0;

        form.reset();

        // Reload the authoritative state and redraw #monsters immediately.
        await load();

        paneNotification(
            'monsters',
            count === 1
                ? `Monster ${name} added to the battle setup.`
                : `${count} monsters added to the battle setup.`,
        );
    } catch (error) {
        paneNotification(
            'monsters',
            error instanceof Error
                ? error.message
                : 'Unable to add monster.',
        );
    }
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

document.querySelector('#monsterSpecies').addEventListener(
    'blur',
    () => {
        clearTimeout(monsterSpeciesLookupTimer);
        lookupMonsterSpeciesStats();
    },
);

document.querySelector('#monsterUpload').onsubmit = async event => {
    event.preventDefault();

    const form = event.currentTarget;
    const payload = new FormData(form);

    const uploadedFile = payload.get('monster_file');
    const fileName = (
        uploadedFile instanceof File && uploadedFile.name
    )
        ? uploadedFile.name
        : 'the uploaded file';

    const quantityText = String(payload.get('quantity') ?? '1').trim();
    const requestedQuantity = Number(quantityText);

    if (
        !/^\d+$/.test(quantityText) ||
        !Number.isInteger(requestedQuantity) ||
        requestedQuantity < 1 ||
        requestedQuantity > 50
    ) {
        paneNotification(
            'battleSetup',
            'Quantity must be a whole number between 1 and 50.',
        );
        return;
    }

    const submitButtons = Array.from(
        form.querySelectorAll(
            'button[type="submit"], button:not([type]), input[type="submit"]',
        ),
    );

    const originalDisabledStates = submitButtons.map(
        button => button.disabled,
    );

    submitButtons.forEach(button => {
        button.disabled = true;
    });

    try {
        let result;

        try {
            result = await request('/api/monsters/import', {
                method: 'POST',
                body: payload,
            });
        } catch (error) {
            paneNotification(
                'battleSetup',
                error instanceof Error
                    ? error.message
                    : 'Unable to import monsters.',
            );
            return;
        }

        const importedCount = Array.isArray(result)
            ? result.length
            : requestedQuantity;

        const successMessage = importedCount === 1
            ? `Monster imported from “${fileName}”.`
            : `${importedCount} monsters imported from “${fileName}”.`;

        form.reset();

        try {
            await load();
        } catch (error) {
            console.error(
                'Monster import succeeded, but refreshing the admin view failed:',
                error,
            );

            paneNotification(
                'battleSetup',
                `${successMessage} The view could not be refreshed; ` +
                'reload the page rather than importing again.',
            );
            return;
        }

        paneNotification(
            'battleSetup',
            successMessage,
        );
    } finally {
        submitButtons.forEach((button, index) => {
            button.disabled = originalDisabledStates[index];
        });
    }
};

document.querySelector('#characterForm').onsubmit = async event => {
    event.preventDefault();

    const formData = new FormData(event.target);

    try {
        await request('/api/characters', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: formData.get('name'),
                color: formData.get('color'),
                hp: +formData.get('hp'),
                initiative: formData.get('initiative') === ''
                    ? null
                    : +formData.get('initiative'),
            }),
        });

        paneNotification(
            'characters',
            `Character “${formData.get('name')}” added to the active campaign.`,
        );

        event.target.reset();
        await load();
    } catch (error) {
        paneNotification('characters', error.message);
    }
};

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

function activeBattleTargets() {
    if (!latest) {
        return [];
    }

    return [...latest.monsters, ...latest.characters]
        .filter(combatant => combatant.active)
        .sort((left, right) => left.name.localeCompare(right.name));
}

function closeBattleActions() {
    battleActionModal.hidden = true;
    battleActionActorId = null;
    battleActionRows.innerHTML = '';
}

function actionAmountRequired(action) {
    return action === 'damage' || action === 'heal';
}

function updateActionRowAmount(row) {
    const action = row.querySelector('[data-action-kind]').value;
    const amountField = row.querySelector('.amount-field');
    const amountInput = row.querySelector('[data-action-amount]');
    const required = actionAmountRequired(action);

    amountField.hidden = !required;
    amountInput.required = required;

    if (!required) {
        amountInput.value = '';
    }
}

function addBattleActionRow() {
    const targets = activeBattleTargets();

    if (!targets.length) {
        message('There are no active combatants available as targets.');
        return;
    }

    const row = document.createElement('div');
    row.className = 'battle-action-row';

    row.innerHTML = `
    <label>
        Target
        <select data-action-target required>
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
        <option value="buff">Buff</option>
        <option value="debuff">Debuff</option>
        </select>
    </label>

    <label class="amount-field">
        Amount
        <input data-action-amount type="number" min="1" max="99999" value="1">
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

        if (!battleActionRows.children.length) {
            addBattleActionRow();
        }
    });

    battleActionRows.appendChild(row);
    updateActionRowAmount(row);
}

function openBattleActions(actorId) {
    const actor = [...latest.monsters, ...latest.characters]
        .find(combatant => combatant.id === actorId);

    if (!actor || !actor.active || !actor.alive || !actor.in_turn) {
        message('Only the current active combatant can perform battle actions.');
        return;
    }

    battleActionActorId = actorId;
    document.querySelector('#battleActionTitle').textContent =
        `Battle actions: ${actor.name}`;

    battleActionRows.innerHTML = '';
    addBattleActionRow();
    battleActionModal.hidden = false;
}

document.querySelector('#addBattleActionTarget').onclick = () => {
    addBattleActionRow();
};

document.querySelector('#cancelBattleActions').onclick = closeBattleActions;

battleActionModal.addEventListener('click', event => {
    if (event.target === battleActionModal) {
        closeBattleActions();
    }
});

battleActionForm.onsubmit = async event => {
    event.preventDefault();

    if (!battleActionActorId) {
        return;
    }

    const rows = [...battleActionRows.querySelectorAll('.battle-action-row')];

    const actions = rows.map(row => {
        const action = row.querySelector('[data-action-kind]').value;
        const rawAmount = row.querySelector('[data-action-amount]').value;

        return {
            target_id: row.querySelector('[data-action-target]').value,
            action,
            amount: actionAmountRequired(action) ? Number(rawAmount) : null,
        };
    });

    const applyButton = battleActionForm.querySelector('button[type="submit"]');
    applyButton.disabled = true;

    try {
        const result = await request('/api/battle/actions', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                actor_id: battleActionActorId,
                actions,
            }),
        });

        closeBattleActions();
        await load();
        message(`Applied ${result.applied} battle action${result.applied === 1 ? '' : 's'}.`);
    } catch (error) {
        message(error.message);
    } finally {
        applyButton.disabled = false;
    }
};

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

        if (!confirm(`Remove ${kind} “${name}” from the current encounter?`)) {
            return;
        }

        button.disabled = true;

        try {
            const result = await request(`/api/combatants/${encodeURIComponent(id)}`, {
                method: 'DELETE',
            });

            await load();
            message(`Removed ${result.name}.`);
        } catch (error) {
            message(error.message);
            button.disabled = false;
        }

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
        request(`/api/combatants/${encodeURIComponent(id)}/reset`, { method: 'POST' })
            .then(load)
            .catch(error => message(error.message));
        return;
    }

    if (button.dataset.t) {
        patch('monsters', id, {
            [button.dataset.f]: !button.textContent.endsWith('on'),
        });
        return;
    }

    if (button.dataset.d) {
        const value = +prompt('Damage to remove:', '1');

        if (Number.isFinite(value)) {
            patch('monsters', id, { hp_delta: -Math.abs(value) });
        }

        return;
    }

    if (button.dataset.h) {
        const value = +prompt('Healing to add:', '1');

        if (Number.isFinite(value)) {
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
        const value = +prompt('Damage to remove:', '1');

        if (Number.isFinite(value)) {
            patch('characters', id, { hp_delta: -Math.abs(value) });
        }

        return;
    }

    if (button.dataset.ch) {
        const value = +prompt('Healing to add:', '1');

        if (Number.isFinite(value)) {
            patch('characters', id, { hp_delta: Math.abs(value) });
        }

        return;
    }

    if (button.dataset.cr) {
        request(`/api/combatants/${encodeURIComponent(id)}/reset`, { method: 'POST' })
            .then(load)
            .catch(error => message(error.message));
    }
});

document.addEventListener('change', event => {
    const input = event.target;

    if (input.dataset.mi && input.value !== '') {
        patch('monsters', input.dataset.mi, { initiative: +input.value });
    }

    if (input.dataset.ci && input.value !== '') {
        patch('characters', input.dataset.ci, { initiative: +input.value });
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

function living() {
    return all().filter(combatant => combatant.active && combatant.alive);
}

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
    const ties = tiedBuckets();

    return ties.map((bucket, bucketIndex) => `
    <div class="tie-title">Initiative ${bucket.initiative}</div>
    ${bucket.members.map((member, memberIndex) => `
        <label class="tie">
        ${esc(member.name)}
        <select data-tie-bucket="${bucketIndex}" data-tie-member="${member.id}">
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

async function startBattle(order) {
    try {
        await request('/api/battle/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ order }),
        });

        await load();
    } catch (error) {
        message(error.message);
    }
}

document.querySelector('#startBattle').onclick = () => {
    const order = normalOrder();

    if (!order.length) {
        message('Activate at least one living combatant first');
        return;
    }

    if (!tiedBuckets().length) {
        startBattle(order);
        return;
    }

    document.querySelector('#tieGroups').innerHTML = tieUI();
    document.querySelector('#tieModal').hidden = false;
};

document.querySelector('#confirmOrder').onclick = () => {
    try {
        const orderedTies = readTieOrder();
        let tieIndex = 0;
        const order = [];

        for (const bucket of initiativeBuckets()) {
            if (bucket.initiative !== null && bucket.members.length > 1) {
                order.push(...orderedTies[tieIndex++]);
            } else {
                order.push(...bucket.members.map(combatant => combatant.id));
            }
        }

        document.querySelector('#tieModal').hidden = true;
        startBattle(order);
    } catch (error) {
        message(error.message);
    }
};

document.querySelector('#cancelOrder').onclick = () => {
    document.querySelector('#tieModal').hidden = true;
};

document.querySelector('#nextBattle').onclick = async () => {
    try {
        await request('/api/battle/next', {
            method: 'POST',
        });

        await load();
    } catch (error) {
        message(error.message);
    }
};

document.querySelector('#endBattle').onclick = async () => {
    if (!latest?.battle_order?.length) {
        message('There is no active battle to end.');
        return;
    }

    if (!confirm('End the battle without resetting combatants?')) {
        return;
    }

    try {
        await request('/api/battle/end', {
            method: 'POST',
        });

        await load();
        message('Battle ended. Combatants were not reset.');
    } catch (error) {
        message(error.message);
    }
};

document.querySelector('#resetAll').onclick = async () => {
    if (!confirm('Reset every monster and character?')) {
        return;
    }

    try {
        await request('/api/battle/reset-all', {
            method: 'POST',
        });

        await load();
    } catch (error) {
        message(error.message);
    }
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

async function adjustBattleOrderFont(direction) {
    if (battleOrderFontAdjustmentPending) {
        return;
    }

    battleOrderFontAdjustmentPending = true;

    updateBattleOrderFontControls(
        latest?.display?.battle_order_font_size,
    );

    try {
        const result = await request(
            '/api/display/battle-order-font',
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ direction }),
            },
        );

        if (latest?.display) {
            latest.display.battle_order_font_size = (
                result.battle_order_font_size
            );
        }

        updateBattleOrderFontControls(
            result.battle_order_font_size,
        );
    } catch (error) {
        message(
            error instanceof Error
                ? error.message
                : 'Unable to change viewer font size.',
        );
    } finally {
        battleOrderFontAdjustmentPending = false;

        updateBattleOrderFontControls(
            latest?.display?.battle_order_font_size,
        );
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
