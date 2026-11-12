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
            target: 'campaign-edit-selection', label: 'Choose campaign to edit'});
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
        const begin = suffix => feedback.begin({...spec, operation: 'campaign.edit' + suffix});
        const validation = begin('.validation');
        const values = [form.elements.name.value, form.elements.description.value];
        const name = values[0].trim(), description = values[1].trim();
        if (!name || !form.reportValidity()) {
            feedback.publish(validation, {severity: 'error', text: !name
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
        const begin = suffix => feedback.begin({...spec, operation: 'campaign.create' + suffix});
        const validation = begin('.validation');
        const values = [form.elements.name.value, form.elements.description.value];
        const name = values[0].trim(), description = values[1].trim();
        if (!name || !form.reportValidity()) {
            feedback.publish(validation, {severity: 'error', text: !name
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

// Stage 1 Step 1C.1: switch validation/request ownership; legacy follow-up retained.
(() => {
    if (typeof switchCampaign !== 'function') return;
    const select = document.querySelector('#campaignSelect'), button = document.querySelector('#switchCampaign');
    let pending = false, revision = 0;
    select.addEventListener('input', () => { revision++; });
    switchCampaign = async function() {
        if (pending) return;
        const feedback = window.scryingAdminFeedback, id = select.value;
        const selectionSpec = {lane: 'page', region: 'campaign', operation: 'campaign.switch.validation',
            target: 'campaign-switch-selection', label: 'Choose campaign to switch to'};
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
        const ticket = feedback.begin({lane: 'page', region: 'campaign', operation: 'campaign.switch',
            target: JSON.stringify(['campaign-switch', id]), label: 'Switch campaign'});
        let result;
        const same = () => {
            const now = feedback.encounterContext();
            const unchanged = now.epoch === origin.epoch && now.scope === origin.scope;
            const intended = result && now.epoch === origin.epoch + 1 && now.scope ===
                JSON.stringify([result.active, result.opened_setup ? result.active : null, result.opened_setup || null]);
            return revision === owner && select.value === id && campaignData === registry && (unchanged || intended);
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
            feedback.resolve(ticket);
            if (!same()) return; // A settled ticket is not a subsequent relevance guard.
            // Existing applied-switch/setup/success/error behavior belongs to 1C.2.
            try {
                campaignData = result;
                document.querySelector('#setupSelect').value = '';
                const opened = await applyOpenedSetup(campaignData);
                paneNotification('campaign', `Switched to campaign: ${activeCampaign()?.name || id}${opened}`);
            } catch (error) { revert(); paneNotification('campaign', error.message); }
        } finally { button.disabled = disabled; pending = false; }
    };
    button.onclick = switchCampaign;
    select.onchange = () => { revision++; return switchCampaign(); };
})();
