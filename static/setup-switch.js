/* SG-TODO-009.7 Stage 1 Steps 2B-2E: save, load/switch, rename and delete battle setups.
 * Installed after the core Admin bundle; replaces the legacy 050 handlers for these controls.
 * New-setup creation (2A) lives in static/admin/060-source.js. */
(() => {
    'use strict';
    const $ = id => document.getElementById(id);
    const scopeOf = (campaign, setup) => JSON.stringify([campaign, setup ? campaign : null, setup || null]);
    const campaignName = id => (typeof campaignById === 'function' && campaignById(id)?.name) || id;

    // One explicit page-lane identity per operation and campaign; matching retries resolve it.
    function tickets(operation, campaign, label) {
        const feedback = window.scryingAdminFeedback;
        const begin = suffix => feedback.begin({lane: 'page', region: 'battleSetup', operation: operation + suffix,
            target: JSON.stringify([operation.replace('.', '-'), campaign]), label});
        return {feedback, begin};
    }

    function invalid(operation, campaign, label, text, focus) {
        const {feedback, begin} = tickets(operation, campaign, label);
        feedback.publish(begin('.validation'), {severity: 'error', text});
        focus?.focus?.();
    }

    function valid(operation, campaign, label) {
        const {feedback, begin} = tickets(operation, campaign, label);
        feedback.resolve(begin('.validation'));
    }

    // Reload the campaign/setup list, propagating failures (setups() reports and swallows them).
    async function refreshCampaigns(relevant) {
        const list = await request('/api/campaigns');
        if (!relevant()) return false;
        campaignData = list;
        renderCampaigns();
        if (list?.moved?.length) paneNotification('campaign',
            `Moved ${list.moved.length} unassigned setup(s) into campaign Default: ` + list.moved.join(', '));
        return true;
    }

    /* Shared guarded lifecycle. spec: operation, campaign, label, controls, mutate(), expected(result),
     * success(result), refresh(result, relevant), failed(error), noun. Never replays the mutation. */
    async function operate(spec) {
        const {feedback, begin} = tickets(spec.operation, spec.campaign, spec.label);
        const origin = feedback.encounterContext(), ticket = begin(''), refresh = begin('.refresh');
        const disabled = spec.controls.map(control => control.disabled);
        let expected = null, result;
        const relevant = () => {
            if (!feedback.isCurrent(refresh) || campaignData.active !== spec.campaign) return false;
            const now = feedback.encounterContext();
            return (now.epoch === origin.epoch && now.scope === origin.scope) ||
                Boolean(expected && now.epoch === origin.epoch + 1 && now.scope === expected);
        };
        for (const control of spec.controls) control.disabled = true;
        try {
            try {
                result = await spec.mutate();
            } catch (error) {
                if (relevant()) {
                    spec.failed?.(error);
                    feedback.publish(ticket, {severity: 'error', text: error.message});
                }
                return;
            }
            expected = spec.expected(result);
            if (!relevant()) return;
            feedback.publish(ticket, {severity: 'success', text: spec.success(result)});
            try {
                await spec.refresh(result, relevant);
                if (!relevant()) return;
                if (expected && feedback.encounterContext().scope !== expected) {
                    throw new Error('The resulting setup state was not applied');
                }
                feedback.resolve(refresh);
            } catch (error) {
                if (relevant()) feedback.publish(refresh, {severity: 'error', text: `${spec.noun(result)}, but ` +
                    `refreshing the view failed: ${error.message}. Reload the page; do not repeat the ` +
                    `${spec.retry} to retry the refresh.`});
            }
        } finally {
            spec.controls.forEach((control, index) => {control.disabled = disabled[index];});
        }
    }

    function install() {
        const select = $('setupSelect'), input = $('setupName');
        const save = $('saveSetup'), loadButton = $('loadSetup'), rename = $('renameSetup'), remove = $('deleteSetup');
        if (!select || !input || !loadButton || !window.scryingAdminFeedback) return;
        const pending = new Set();
        let revision = 0;
        input.addEventListener?.('input', () => revision++);
        const guarded = (key, handler) => async event => {
            event?.preventDefault?.();
            if (pending.has(key)) return;
            pending.add(key);
            try {await handler();} finally {pending.delete(key);}
        };
        const active = () => (typeof latest === 'undefined' ? null : latest?.active_setup) || null;

        // 2B: save the current setup under the entered name (server overwrite semantics retained).
        if (save) save.onclick = guarded('save', async () => {
            const campaign = campaignData.active, name = input.value.trim(), label = 'Save battle setup';
            if (!name) return invalid('setup.save', campaign, label, 'Enter a battle setup name before saving', input);
            valid('setup.save', campaign, label);
            const own = revision;
            await operate({operation: 'setup.save', campaign, label, controls: [save], retry: 'save',
                mutate: () => request('/api/setups/save', {method: 'POST',
                    headers: {'Content-Type': 'application/json'}, body: JSON.stringify({name, campaign})}),
                expected: result => scopeOf(result.campaign || campaign, result.name),
                success: result => `Saved setup: ${result.name} (campaign: ${campaignName(result.campaign)})`,
                noun: result => `Battle setup ${result.name} was saved`,
                async refresh(result, relevant) {
                    if (own === revision) input.value = result.name;
                    await load(true, relevant);
                    if (!relevant() || !await refreshCampaigns(relevant)) return;
                    select.value = result.name;
                    syncActiveBattleSetupControls();
                    renderActiveBattleSetup();
                },
            });
        });

        // 2C: effective load/switch owner for both the dropdown and Load button. No confirmation,
        // already-loaded no-op and request-failure selection restoration are retained.
        const switchSetup = guarded('load', async () => {
            const name = select.value, reference = active(), label = 'Load battle setup';
            const campaign = typeof campaignData === 'undefined' ? null : campaignData.active;
            if (!name) return invalid('setup.load', campaign, label, 'Choose a saved battle setup to load', select);
            if (!campaign) return invalid('setup.load', campaign, label, 'Choose an active campaign first', select);
            valid('setup.load', campaign, label);
            if (reference?.name === name && reference?.campaign_id === campaign) return;
            await operate({operation: 'setup.load', campaign, label, controls: [select, loadButton], retry: 'load',
                mutate: () => request('/api/setups/load', {method: 'POST',
                    headers: {'Content-Type': 'application/json'}, body: JSON.stringify({name, campaign})}),
                // Restore only our own selection; a newer choice is kept.
                failed: () => {if (select.value === name) select.value = reference?.name || '';},
                expected: result => scopeOf(result?.campaign || campaign, result?.name || name),
                success: result => `Loaded battle setup: ${result?.name || name}`,
                noun: result => `Battle setup ${result?.name || name} was loaded`,
                async refresh(result, relevant) {
                    input.value = result?.name || name;
                    await load(true, relevant);
                    if (!relevant() || !await refreshCampaigns(relevant)) return;
                    select.value = result?.name || name;
                },
            });
        });
        select.onchange = switchSetup;
        loadButton.onclick = switchSetup;

        // 2D: rename the selected saved setup. Cancel, blank and unchanged names stay no-ops.
        if (rename) rename.onclick = guarded('rename', async () => {
            const campaign = campaignData.active, name = select.value, label = 'Rename battle setup';
            if (!name) return invalid('setup.rename', campaign, label, 'Choose a saved setup to rename', select);
            valid('setup.rename', campaign, label);
            const entered = prompt(`Rename battle setup ${name} to:`, name);
            if (entered === null || !entered.trim() || entered.trim() === name) return;
            const reference = active(), wasActive = reference?.name === name && reference?.campaign_id === campaign;
            await operate({operation: 'setup.rename', campaign, label, controls: [rename], retry: 'rename',
                mutate: () => request('/api/setups/rename', {method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name, new_name: entered.trim(), campaign})}),
                expected: result => wasActive ? scopeOf(campaign, result.name) : null,
                success: result => `Renamed battle setup ${result.old_name} to ${result.name}`,
                noun: result => `Battle setup ${result.old_name} was renamed to ${result.name}`,
                async refresh(result, relevant) {
                    if (input.value.trim() === name) input.value = result.name;
                    if (!await refreshCampaigns(relevant)) return;
                    select.value = result.name;
                    // The loaded setup's reference changed on the server; reload it so it is not stale.
                    if (wasActive) await load(true, relevant);
                    if (!relevant()) return;
                    syncActiveBattleSetupControls();
                    renderActiveBattleSetup();
                },
            });
        });

        // 2E: delete the selected setup; the server opens the replacement (or a new empty default).
        if (remove) remove.onclick = guarded('delete', async () => {
            const campaign = campaignData.active, name = select.value, label = 'Delete battle setup';
            if (!name) return invalid('setup.delete', campaign, label, 'Choose a saved setup to delete', select);
            valid('setup.delete', campaign, label);
            if (!confirm(
                `Delete battle setup ${name} from campaign ${activeCampaign()?.name || campaign}?\n\n` +
                'The next battle setup is opened afterwards (an empty "default" setup is created if this was the last one). ' +
                'Unsaved changes to the current battle will be lost.',
            )) return;
            await operate({operation: 'setup.delete', campaign, label, controls: [remove], retry: 'deletion',
                mutate: () => request(`/api/setups/${encodeURIComponent(name)}?campaign=${encodeURIComponent(campaign || '')}`,
                    {method: 'DELETE'}),
                expected: result => scopeOf(result.campaign || campaign, result.opened_setup),
                success: result => `Deleted battle setup ${result.deleted}; opened ` +
                    `${result.created_default ? 'new empty setup ' : ''}${result.opened_setup}`,
                noun: result => `Battle setup ${result.deleted} was deleted and ${result.opened_setup} opened`,
                async refresh(result, relevant) {
                    if (!await refreshCampaigns(relevant)) return;
                    input.value = result.opened_setup;
                    select.value = result.opened_setup;
                    syncActiveBattleSetupControls();
                    renderActiveBattleSetup();
                    await load(true, relevant);
                },
            });
        });
    }
    if (document.readyState !== 'complete') {
        document.addEventListener('DOMContentLoaded', install, {once: true});
    } else install();
})();
