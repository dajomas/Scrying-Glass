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

