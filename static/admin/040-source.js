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

    const kind = csvImportKind;
    const form = event.target;
    const submit = form.querySelector('button[type="submit"], button.import');

    submit.disabled = true;

    try {
        const endpoint = kind === 'monsters'
            ? '/api/monsters/import-csv'
            : '/api/characters/import-csv';

        const result = await request(endpoint, {
            method: 'POST',
            body: new FormData(form),
        });

        closeCsvImport();
        await load();

        paneNotification(
            kind === 'characters' ? 'campaign' : 'battleSetup',
            `Imported ${result.count} ${kind === 'monsters' ? 'monster' : 'character'
            }${result.count === 1 ? '' : 's'} from CSV.`,
        );

        const count = Number(result?.count ?? 0);
        const noun = kind === 'characters' ? 'character' : 'monster';
        const target = kind === 'characters' ? 'characters' : 'monsters';

        paneNotification(
            target,
            `${count} ${noun}${count === 1 ? '' : 's'} added successfully.`,
        );
    } catch (error) {
        paneNotification(kind === 'characters' ? 'campaign' : 'battleSetup', error.message);
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
