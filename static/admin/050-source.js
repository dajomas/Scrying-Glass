// Stage 1 Step 1D.1: delete validation/request ownership; follow-up guarded in 1D.2a; feedback migration remains 1D.2b.
let campaignDeleteSession = 0, campaignDeleteRevision = 0, campaignDeletePending = false;
const campaignDeleteFeedback = (operation, target, label) => window.scryingAdminFeedback.begin({
    lane: 'page', region: 'campaign', operation, target, label,
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
        feedback.publish(validation, {severity: 'error', text: 'Choose a campaign to delete'});
        return;
    }
    const moveTo = document.querySelector('#campaignDeleteMoveTo').value;
    const hasSetups = campaign.setups.length > 0;
    const deleteSetups = hasSetups && document.querySelector('#campaignDeleteAction').value === 'delete';
    if (hasSetups && !deleteSetups && (!moveTo || moveTo === campaignId)) {
        feedback.publish(validation, {severity: 'error', text: 'Choose another campaign to move the battle setups to'});
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
        feedback.resolve(ticket);
        if (!same()) return; // The settled request ticket is not a subsequent context guard.
        // Existing applied-deletion/setup/success/error behavior belongs to 1D.2.
        try {
            campaignData = result;
            applied = true;
            closedByAttempt = true;
            campaignDeleteModal.hidden = true;
            document.querySelector('#setupSelect').value = '';
            const opened = await applyOpenedSetup(result);
            if (!same()) return;
            paneNotification(
                'campaign',
                `Deleted campaign: ${campaign ? campaign.name : campaignId}` +
                (result.moved && result.moved.length ? ` (moved ${result.moved.length} setup(s))` : '') +
                (result.deleted_setups && result.deleted_setups.length ? ` (deleted ${result.deleted_setups.length} setup(s))` : '') +
                opened,
            );
            if (same()) feedback.resolve(refresh);
        } catch (error) { if (same()) paneNotification('campaign', error.message); }
    } finally { submit.disabled = disabled; campaignDeletePending = false; }
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
        // Validate uniqueness and create the named empty setup atomically.
        const result = await request('/api/setups/new', {
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
        await load();
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

