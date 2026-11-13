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
// are owned by setup-switch.js; #newSetup by the 060 owner, which wraps this install point.
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

