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
        message('There are no active combatants available as targets.');
        return;
    }

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
    if (!targets.length) { message('There are no living active targets.'); return; }
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

