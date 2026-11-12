/* SG-TODO-009.7 Stage 1 Steps 2B-2E: save, load/switch, rename and delete battle setups;
 * Step 3: setup copy/move between campaigns (replaces the 050 modal handlers) and the View screen
 * background controls (formerly rebound by every 030 load()). Installed after the core Admin
 * bundle. New-setup creation (2A) lives in static/admin/060-source.js. */
(() => {
    'use strict';
    const $ = id => document.getElementById(id);
    const scopeOf = (campaign, setup) => JSON.stringify([campaign, setup ? campaign : null, setup || null]);
    const campaignName = id => (typeof campaignById === 'function' && campaignById(id)?.name) || id;

    // One explicit page-lane identity per operation and campaign; matching retries resolve it.
    // Options: region (default battleSetup) and an explicit target (default [operation, campaign]).
    function tickets(operation, campaign, label, options = {}) {
        const feedback = window.scryingAdminFeedback;
        const target = options.target ?? JSON.stringify([operation.replace('.', '-'), campaign]);
        const begin = suffix => feedback.begin({lane: 'page', region: options.region || 'battleSetup',
            operation: operation + suffix, target, label});
        return {feedback, begin};
    }

    function invalid(operation, campaign, label, text, focus, options) {
        const {feedback, begin} = tickets(operation, campaign, label, options);
        feedback.publish(begin('.validation'), {severity: 'error', text});
        focus?.focus?.();
    }

    function valid(operation, campaign, label, options) {
        const {feedback, begin} = tickets(operation, campaign, label, options);
        feedback.resolve(begin('.validation'));
    }

    // Reload the campaign/setup list, propagating failures (setups() reports and swallows them).
    async function refreshCampaigns(relevant) {
        const list = await request('/api/campaigns');
        if (!relevant()) return false;
        campaignData = list;
        renderCampaigns();
        announceMovedSetups(list?.moved);
        return true;
    }

    /* Shared guarded lifecycle. spec: operation, campaign, label, controls, mutate(), expected(result),
     * success(result), refresh(result, relevant), failed(error), noun. Never replays the mutation. */
    async function operate(spec) {
        const {feedback, begin} = tickets(spec.operation, spec.campaign, spec.label, spec);
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
                    throw new Error(spec.unapplied || 'The resulting setup state was not applied');
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

    // Duplicate activations of the same operation are ignored until it (and its refresh) settles.
    const pending = new Set();
    const guarded = (key, handler) => async event => {
        event?.preventDefault?.();
        if (pending.has(key)) return;
        pending.add(key);
        try {await handler(event);} finally {pending.delete(key);}
    };
    const active = () => (typeof latest === 'undefined' ? null : latest?.active_setup) || null;

    function installSetups() {
        const select = $('setupSelect'), input = $('setupName');
        const save = $('saveSetup'), loadButton = $('loadSetup'), rename = $('renameSetup'), remove = $('deleteSetup');
        if (!select || !input || !loadButton) return;
        let revision = 0;
        input.addEventListener?.('input', () => revision++);

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

    // Step 3: copy/move a saved setup between campaigns (campaign pane, modal workflow).
    function installTransfer() {
        const open = $('openCampaignSetup'), form = $('campaignSetupForm'), modal = $('campaignSetupModal');
        if (!open || !form || !modal) return;
        const label = 'Copy or move battle setup', region = {region: 'campaign'};
        const selection = {...region, target: JSON.stringify(['setup-transfer', 'selection'])};
        const cancel = $('cancelCampaignSetup');
        let session = 0;
        if (cancel) {
            const close = cancel.onclick;
            cancel.onclick = event => {session++; return close?.(event);};
        }
        open.onclick = guarded('transfer.open', async () => {
            session++;
            try {
                const list = await request('/api/campaigns');
                campaignData = list;
                renderCampaigns();
            } catch (error) {
                return invalid('setup.transfer.open', null, label, error.message, open, selection);
            }
            if (campaignData.campaigns.length < 2) return invalid('setup.transfer.open', null, label,
                'Create a second campaign first; setups can only be added from another campaign', open, selection);
            valid('setup.transfer.open', null, label, selection);
            const target = $('campaignSelect')?.value || campaignData.active;
            const source = campaignData.campaigns.find(item => item.id !== target && item.setups.length)
                || campaignData.campaigns.find(item => item.id !== target);
            $('campaignSetupFrom').innerHTML = campaignOptions(source.id);
            $('campaignSetupTo').innerHTML = campaignOptions(target);
            renderCampaignSetupNames();
            modal.hidden = false;
        });
        form.onsubmit = guarded('transfer', async event => {
            const data = new FormData(event?.target || form);
            const from = data.get('from_campaign'), setup = data.get('setup');
            const to = data.get('to_campaign'), mode = data.get('mode');
            const focus = $('campaignSetupName');
            if (!setup) return invalid('setup.transfer', null, label, 'Choose a battle setup', focus, selection);
            if (from === to) return invalid('setup.transfer', null, label,
                'Source and target campaign are the same', $('campaignSetupTo'), selection);
            valid('setup.transfer', null, label, selection);
            const own = session, reference = active();
            // Moving the loaded setup makes the server clear the active setup reference.
            const unloads = mode === 'move' && reference?.campaign_id === from && reference?.name === setup;
            const verb = mode === 'copy' ? 'copied' : 'moved';
            await operate({operation: 'setup.transfer', campaign: campaignData.active, label, ...region,
                target: JSON.stringify(['setup-transfer', from, setup, to]),
                controls: [form.querySelector?.('button.import')].filter(Boolean), retry: mode,
                mutate: () => request(`/api/campaigns/${encodeURIComponent(to)}/setups`, {method: 'POST',
                    headers: {'Content-Type': 'application/json'}, body: JSON.stringify({setup, from_campaign: from, mode})}),
                expected: () => unloads ? scopeOf(campaignData.active, null) : null,
                unapplied: 'The unloaded setup state was not applied',
                success: result => `${mode === 'copy' ? 'Copied' : 'Moved'} setup ${setup} to campaign ` +
                    `${campaignName(result.campaign)}` + (result.setup !== setup ? ` as ${result.setup}` : ''),
                noun: result => `Battle setup ${setup} was ${verb} to ${campaignName(result.campaign)}`,
                async refresh(result, relevant) {
                    campaignData = result;
                    if (own === session) modal.hidden = true;
                    renderCampaigns();
                    if (unloads) await load(true, relevant);
                },
            });
        });
    }

    // Step 3: View screen background color/image. Shared busy key: all three change one value.
    function installBackground() {
        const color = $('backgroundColor'), value = $('backgroundValue');
        const apply = $('applyBackground'), clear = $('clearBackgroundImage'), image = $('backgroundImage');
        if (!color || !value || !apply || !clear || !image) return;
        color.onclick = () => color.showPicker?.();
        color.oninput = event => {value.value = event.target.value;};
        const controls = [apply, clear, image];
        const change = (operation, text, mutate, done = 'updated') => operate({operation,
            campaign: campaignData.active, label: 'View screen background', controls, retry: 'background change',
            target: JSON.stringify(['view-background', campaignData.active]), mutate, expected: () => null,
            success: () => text, noun: () => `The View screen background was ${done}`,
            refresh: (result, relevant) => load(true, relevant)});
        const patch = background => request('/api/display/background', {method: 'PATCH',
            headers: {'Content-Type': 'application/json'}, body: JSON.stringify({background})});
        apply.onclick = guarded('background', () => change('background.apply',
            'View screen background updated. Save the setup to keep it.',
            () => patch(value.value.trim() || '#080b14')));
        clear.onclick = guarded('background', () => change('background.clear',
            'View screen now uses the selected background color.', () => patch(color.value)));
        image.onchange = guarded('background', async event => {
            const input = event?.target || image, [file] = input.files || [];
            if (!file) return;
            const form = new FormData();
            form.append('image', file);
            try {
                await change('background.upload', 'Background image uploaded. Save the setup to keep it.', async () => {
                    const result = await request('/api/display/background-image', {method: 'POST', body: form});
                    value.value = result.background;
                    return result;
                }, 'uploaded');
            } finally {
                input.value = '';
            }
        });
    }

    function install() {
        if (!window.scryingAdminFeedback) return;
        installSetups();
        installTransfer();
        installBackground();
    }
    if (document.readyState !== 'complete') {
        document.addEventListener('DOMContentLoaded', install, {once: true});
    } else install();
})();
