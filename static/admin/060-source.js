async function applyBackground(background) {
    await request('/api/display/background', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ background }),
    });

    await load();
}

// Stage 1 Step 2A: create a new empty setup.
(() => {
    const button = document.querySelector('#newSetup'), input = document.querySelector('#setupName');
    if (!button || typeof button.onclick !== 'function' || !input || typeof activeCampaign !== 'function') return;
    let pending = false, revision = 0;
    input.addEventListener('input', () => revision++);
    button.onclick = async () => {
        if (pending) return;
        const feedback = window.scryingAdminFeedback, campaign = campaignData.active, name = input.value.trim();
        const begin = suffix => feedback.begin({lane: 'page', region: 'battleSetup', operation: 'setup.new' + suffix,
            target: JSON.stringify(['setup-new', campaign]), label: 'Create battle setup'});
        const validation = begin('.validation');
        const known = (activeCampaign()?.setups || []).map(item => item.toLocaleLowerCase());
        const invalid = !name ? 'Enter a unique battle setup name before creating it.'
            : known.includes(name.toLocaleLowerCase())
                ? `A battle setup named “${name}” already exists in ${activeCampaign()?.name || campaign}.` : '';
        if (invalid) {
            feedback.publish(validation, {severity: 'error', text: invalid});
            input.focus();
            return;
        }
        feedback.resolve(validation);
        if (!confirm(`Discard the current battle setup and create a new empty setup named “${name}”?`)) return;
        const origin = feedback.encounterContext(), own = revision, ticket = begin(''), refresh = begin('.refresh');
        const disabled = button.disabled;
        let result, scope;
        const relevant = () => {
            if (!feedback.isCurrent(refresh) || campaignData.active !== campaign) return false;
            const now = feedback.encounterContext();
            return (now.epoch === origin.epoch && now.scope === origin.scope) ||
                Boolean(scope && now.epoch === origin.epoch + 1 && now.scope === scope);
        };
        pending = true;
        button.disabled = true;
        try {
            try {
                result = await request('/api/setups/new', {method: 'POST',
                    headers: {'Content-Type': 'application/json'}, body: JSON.stringify({name, campaign})});
            } catch (error) {
                if (relevant()) feedback.publish(ticket, {severity: 'error', text: error.message});
                return;
            }
            const setup = result.name, owner = result.campaign || campaign;
            scope = JSON.stringify([owner, owner, setup]);
            if (!relevant()) return;
            feedback.publish(ticket, {severity: 'success', text: `Created and saved empty battle setup “${setup}”.`});
            try {
                // Newer typing wins; the created setup is still selected and loaded.
                if (own === revision) input.value = setup;
                const list = await request('/api/campaigns');
                if (!relevant()) return;
                campaignData = list;
                renderCampaigns();
                if (list.moved?.length) paneNotification('campaign',
                    `Moved ${list.moved.length} unassigned setup(s) into campaign Default: ` + list.moved.join(', '));
                document.querySelector('#setupSelect').value = setup;
                syncActiveBattleSetupControls();
                renderActiveBattleSetup();
                await load(true, relevant);
                if (relevant()) {
                    if (feedback.encounterContext().scope !== scope) throw new Error('The created setup state was not applied');
                    feedback.resolve(refresh);
                }
            } catch (error) {
                if (relevant()) feedback.publish(refresh, {severity: 'error', text: `Battle setup “${setup}” was created and ` +
                    `saved, but refreshing the view failed: ${error.message}. Reload the page; do not create the setup again to retry the refresh.`});
            }
        } finally {
            button.disabled = disabled;
            pending = false;
        }
    };
})();

const entryFormPending = new WeakSet();
async function submitEntryForm(form, region, operation, prepare) {
    if (entryFormPending.has(form)) return;
    entryFormPending.add(form);
    const feedback = window.scryingAdminFeedback;
    const spec = {region, operation, target: form.id, label: 'Create or import combatants'};
    let controls = [], disabled = [];
    try {
        const validation = feedback.begin({...spec, operation: operation + '.validation'});
        if (!form.reportValidity()) {
            feedback.publish(validation, {severity: 'error', text: 'Review the required fields and valid values before submitting.'});
            return;
        }
        let prepared;
        try { prepared = prepare(); }
        catch (error) {
            feedback.publish(validation, {severity: 'error', text: error.message});
            return;
        }
        if (prepared.error) {
            feedback.publish(validation, {severity: 'error', text: prepared.error});
            prepared.focus?.focus();
            return;
        }
        feedback.resolve(validation);
        const ticket = feedback.begin(spec);
        const refresh = feedback.begin({...spec, operation: operation + '.refresh'});
        controls = [...form.querySelectorAll('input, select, textarea, button')];
        disabled = controls.map(control => control.disabled);
        controls.forEach(control => { control.disabled = true; });
        let result;
        try { result = await prepared.send(); }
        catch (error) {
            feedback.publish(ticket, {severity: 'error', text: error instanceof Error
                ? error.message : 'Unable to create or import combatants.'});
            return;
        }
        if (!feedback.isCurrent(refresh)) return;
        feedback.publish(ticket, {severity: 'success', text: prepared.success(result)});
        try {
            form.reset();
            await load(true);
            feedback.resolve(refresh);
        } catch {
            feedback.publish(refresh, {severity: 'error', text:
                'Changes saved, but updating the view failed. Reload the page; do not repeat the submission.'});
        }
    } finally {
        controls.forEach((control, index) => { control.disabled = disabled[index]; });
        entryFormPending.delete(form);
    }
}

document.querySelector('#characterForm').onsubmit = async event => {
    event.preventDefault();
    const form = event.currentTarget || event.target;
    return submitEntryForm(form, 'characters', 'character.create', () => {
        const payload = new FormData(form);
        const data = {
            name: payload.get('name'), color: payload.get('color'), hp: +payload.get('hp'),
            initiative: payload.get('initiative') === '' ? null : +payload.get('initiative'),
        };
        return {
            send: () => request('/api/characters', {method: 'POST',
                headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)}),
            success: () => `Character “${payload.get('name')}” added to the active campaign.`,
        };
    });
};

document.querySelector('#monsterForm').onsubmit = async event => {
    event.preventDefault();
    const form = event.currentTarget || event.target;
    return submitEntryForm(form, 'monsters', 'monster.create', () => {
        const payload = new FormData(form);
        const start = String(payload.get('hprangestart') ?? '').trim();
        const end = String(payload.get('hprangeend') ?? '').trim();
        const error = validateMonsterHpRange(start, end);
        if (error) {
            const invalidStart = !start || (!isDiceHpExpression(start) && parseNonNegativeInteger(start) === null);
            return {error, focus: invalidStart ? form.elements.hprangestart : form.elements.hprangeend};
        }
        payload.set('hprangestart', start);
        payload.set('hprangeend', end);
        const name = String(payload.get('name') ?? '').trim();
        return {
            send: () => request('/api/monsters', {method: 'POST', body: payload}),
            success: result => {
                const count = Array.isArray(result) ? result.length : 0;
                return count === 1 ? `Monster ${name} added to the battle setup.`
                    : `${count} monsters added to the battle setup.`;
            },
        };
    });
};

document.querySelector('#monsterUpload').onsubmit = async event => {
    event.preventDefault();
    const form = event.currentTarget || event.target;
    return submitEntryForm(form, 'battleSetup', 'monster.import.file', () => {
        const payload = new FormData(form);
        const file = payload.get('monster_file');
        const fileName = file instanceof File && file.name ? file.name : 'the uploaded file';
        const text = String(payload.get('quantity') ?? '1').trim();
        const quantity = Number(text);
        if (!/^\d+$/.test(text) || !Number.isInteger(quantity) || quantity < 1 || quantity > 50) {
            return {error: 'Quantity must be a whole number between 1 and 50.'};
        }
        return {
            send: () => request('/api/monsters/import', {method: 'POST', body: payload}),
            success: result => {
                const count = Array.isArray(result) ? result.length : quantity;
                return count === 1 ? `Monster imported from “${fileName}”.`
                    : `${count} monsters imported from “${fileName}”.`;
            },
        };
    });
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
let battleStatisticsToken = null;
let battleActionsApplying = false;

function activeBattleTargets() {
    if (!latest) {
        return [];
    }

    return [...latest.monsters, ...latest.characters]
        .filter(combatant => combatant.active)
        .sort((left, right) => left.name.localeCompare(right.name));
}

function battleActionFeedback(operation, target, label, outcome) {
    const feedback = window.scryingAdminFeedback;
    const ticket = feedback.begin({region: 'global', operation: `battle.actions.${operation}`,
        target: String(target), label});
    return outcome === undefined ? feedback.resolve(ticket) : feedback.publish(ticket, outcome);
}

function closeBattleActions() {
    if (battleActionsApplying) return;
    battleActionModal.hidden = true;
    battleActionActorId = null;
    battleActionRows.innerHTML = '';
}

function actionAmountRequired(action) {
    return action === 'damage' || action === 'heal' || action === 'reduce-stat';
}

function updateActionRowAmount(row) {
    const action = row.querySelector('[data-action-kind]').value;
    const amountField = row.querySelector('.amount-field');
    const amountInput = row.querySelector('[data-action-amount]');
    const required = actionAmountRequired(action);

    amountField.hidden = !required;
    amountInput.required = required;
    const critical=row.querySelector('[data-action-critical]');
    if(critical){critical.parentElement.hidden=action!=='damage';if(action!=='damage')critical.checked=false;}

    if (!required) {
        amountInput.value = '';
    }
}

function addBattleActionRow(reaction = false) {
    if (battleActionsApplying) return;
    const targets = activeBattleTargets();

    if (!targets.length) {
        battleActionFeedback('targets', 'active', 'Battle-action targets',
            {severity: 'error', text: 'There are no active combatants available as targets.'});
        return;
    }

    battleActionFeedback('targets', 'active', 'Battle-action targets');
    const row = document.createElement('div');
    row.className = 'battle-action-row' + (reaction ? ' battle-reaction-row' : '');

    row.innerHTML = `
    ${reaction ? `<label>Reaction source
        <select data-action-source required>
        <option value="" disabled selected>Select source…</option>
        ${targets.map(source =>
            `<option value="${esc(source.id)}">${esc(source.name)}${source.alive ? '' : ' (down/dead)'}</option>`
        ).join('')}</select></label>` : ''}
    <label>
        Target
        <select data-action-target required>
        <option value="" disabled selected>Select target…</option>
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
        ${reaction ? '' : '<option value="buff">Buff</option><option value="debuff">Debuff</option>'}
        </select>
    </label>

    <label class="amount-field">
        Amount
        <input data-action-amount type="number" min="1" max="99999" value="1">
        <span class="critical-option"><input data-action-critical type="checkbox"> Critical hit</span>
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


    });

    battleActionRows.appendChild(row);
    updateActionRowAmount(row);
}

function addStatisticsReductionRow() {
    if (battleActionsApplying) return;
    const targets = activeBattleTargets().filter(x => x.alive);
    if (!targets.length) {
        battleActionFeedback('targets', 'living', 'Statistics-reduction targets',
            {severity: 'error', text: 'There are no living active targets.'});
        return;
    }
    battleActionFeedback('targets', 'living', 'Statistics-reduction targets');
    const row = document.createElement('div');
    row.className = 'battle-action-row statistics-reduction-row';
    row.innerHTML = `
        <input data-action-kind type="hidden" value="reduce-stat">
        <label>Target <select data-action-target required>
          <option value="" disabled selected>Select target…</option>
          ${targets.map(x=>`<option value="${esc(x.id)}">${esc(x.name)}</option>`).join('')}
        </select></label>
        <label>Statistic <select data-action-stat required>
          <option value="max_hp">Max HP</option><option value="strength">STR</option>
          <option value="dexterity">DEX</option><option value="constitution">CON</option>
          <option value="intelligence">INT</option><option value="wisdom">WIS</option>
          <option value="charisma">CHA</option>
        </select></label>
        <label class="amount-field">Amount to reduce
          <input data-action-amount type="number" required min="1" max="99999" step="1" value="1">
        </label>
        <button data-remove-action-row type="button" class="danger">Remove</button>`;
    row.querySelector('[data-remove-action-row]').addEventListener('click',()=>row.remove());
    battleActionRows.appendChild(row);
}

function openBattleActions(actorId) {
    if (battleActionsApplying) return;
    if ((latest.lairs || []).some(x => x.id === actorId)) {
        window.scryingOpenLairAction?.(actorId);
        return;
    }
    const actor = [...latest.monsters, ...latest.characters]
        .find(combatant => combatant.id === actorId);

    if (!actor || !actor.active || !actor.in_turn) {
        battleActionFeedback('eligibility', actorId, `Battle actions: ${actor?.name || actorId}`,
            {severity: 'error', text: 'Only the current active combatant can perform battle actions.'});
        return;
    }

    battleActionFeedback('eligibility', actorId, `Battle actions: ${actor.name}`);
    document.querySelector('#battleActionNotice').textContent = '';
    battleActionActorId = actorId;
    battleStatisticsToken = latest.statistics_token;
    document.querySelector('#battleActionTitle').textContent =
        `Battle actions: ${actor.name}`;

    battleActionRows.innerHTML = '';
    addBattleActionRow(!actor.alive);
    battleActionModal.hidden = false;
}

