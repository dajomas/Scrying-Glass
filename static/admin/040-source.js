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
            feedback.publish(validation, {severity: 'error', text: prepared.error || 'Select a valid import file and options.'});
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
        if (!confirm('Overwrite initiative for every monster with a random d20 roll?')) return;
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
        document.querySelector('#setupName').value = '';
        document.querySelector('#setupSelect').value = '';
        await load();
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
