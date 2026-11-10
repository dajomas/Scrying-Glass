function openBattleActions(actorId) {
    if (battleActionsApplying) return;
    if ((latest.lairs || []).some(x => x.id === actorId)) {
        window.scryingOpenLairAction?.(actorId);
        return;
    }
    const actor = [...latest.monsters, ...latest.characters]
        .find(combatant => combatant.id === actorId);

    if (!actor || !actor.active || !actor.in_turn) {
        message('Only the current active combatant can perform battle actions.');
        return;
    }

    document.querySelector('#battleActionNotice').textContent = '';
    battleActionActorId = actorId;
    battleStatisticsToken = latest.statistics_token;
    document.querySelector('#battleActionTitle').textContent =
        `Battle actions: ${actor.name}`;

    battleActionRows.innerHTML = '';
    addBattleActionRow(!actor.alive);
    battleActionModal.hidden = false;
}

document.querySelector('#addBattleActionTarget').onclick = () => {
    addBattleActionRow();
};

document.querySelector('#addBattleReaction').onclick = () => addBattleActionRow(true);
document.querySelector('#addStatisticsReduction').onclick = addStatisticsReductionRow;

document.querySelector('#closeBattleActions').onclick = closeBattleActions;

battleActionModal.addEventListener('click', event => {
    if (event.target === battleActionModal) {
        closeBattleActions();
    }
});

battleActionForm.onsubmit = async event => {
    event.preventDefault();

    if (!battleActionActorId || battleActionsApplying) {
        return;
    }

    // Also enforce native validation when the handler is invoked directly.
    if (!battleActionForm.reportValidity()) {
        return;
    }

    const rows = [...battleActionRows.querySelectorAll('.battle-action-row')]
        .filter(row => row.dataset.applied !== 'true');

    const actions = rows.map(row => {
        const action = row.querySelector('[data-action-kind]').value;
        const rawAmount = row.querySelector('[data-action-amount]').value;

        return {
            source_id: row.querySelector('[data-action-source]')?.value || null,
            target_id: row.querySelector('[data-action-target]').value,
            action,
            amount: actionAmountRequired(action) ? Number(rawAmount) : null,
            critical_hit: action==='damage'&&Boolean(row.querySelector('[data-action-critical]')?.checked),
            ...(action === 'reduce-stat' ? {stat: row.querySelector('[data-action-stat]').value} : {}),
        };
    });

    if (!actions.length) { message('No pending actions or reactions. Add a new row to apply more.'); return; }
    const applyButton = battleActionForm.querySelector('button[type="submit"]');
    if (applyButton.disabled) return;
    battleActionsApplying = true;
    // Freeze this batch and the separate start-of-turn form until refresh ends.
    const controls = [...battleActionModal.querySelectorAll('input, select, button')];
    const previousDisabled = controls.map(control => control.disabled);
    controls.forEach(control => { control.disabled = true; });
    battleActionModal.setAttribute('aria-busy', 'true');
    let applied = false;

    try {
        const result = await request('/api/battle/actions', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                actor_id: battleActionActorId,
                actions,
                ...(actions.some(x=>x.action==='reduce-stat') ? {statistics_token: battleStatisticsToken} : {}),
            }),
        });

        // Record success before refreshing: a failed refresh must not replay HP changes.
        applied = true;
        for (const row of rows) {
            row.dataset.applied = 'true';
            const status = document.createElement('span');
            status.className = 'battle-action-applied-status';
            status.textContent = 'Applied';
            row.appendChild(status);
        }
        document.querySelector('#battleActionNotice').textContent =
            `Applied ${result.applied} battle action${result.applied === 1 ? '' : 's'}. ` +
            'Add targets or reactions to continue, or Close when finished.';
        await load(true);
        if (typeof battleStatisticsToken !== 'undefined') battleStatisticsToken = latest.statistics_token;
    } catch (error) {
        document.querySelector('#battleActionNotice').textContent = applied
            ? `Actions were applied, but refresh failed: ${error.message}. Refresh before continuing.`
            : error.message;
    } finally {
        controls.forEach((control, index) => {
            control.disabled = previousDisabled[index] ||
                control.closest('.battle-action-row')?.dataset.applied === 'true';
        });
        battleActionsApplying = false;
        battleActionModal.removeAttribute('aria-busy');
    }
};

async function resetCombatantWithFeedback(kind, id) {
    const feedback = window.scryingAdminFeedback;
    const name = latest?.[kind]?.find(combatant => combatant.id === id)?.name || id;
    const noun = kind === 'monsters' ? 'monster' : 'character';
    const ticket = feedback.begin({region: 'global', operation: 'combatant.reset',
        target: JSON.stringify([kind, id]), label: `Reset ${noun}: ${name}`});
    try {
        await request(`/api/combatants/${encodeURIComponent(id)}/reset`, {method: 'POST'});
    } catch (error) {
        feedback.publish(ticket, {severity: 'error', text: error.message});
        return;
    }
    if (!feedback.isCurrent(ticket)) return;
    feedback.resolve(ticket);
    // Reset succeeded; refresh failures remain owned by load(), not the mutation.
    await load();
}

document.addEventListener('click', async event => {
    const button = event.target.closest('button');

    if (!button) {
        return;
    }

    if (button.dataset.removeKind && button.dataset.removeId) {
        await removeCombatant(
            button.dataset.removeKind,
            button.dataset.removeId,
        );
        return;
    }

    if (button.dataset.remove) {
        const id = button.dataset.remove;
        const kind = button.dataset.removeKind || 'combatant';
        const row = button.closest('tr');
        const name = row?.querySelector('td')?.textContent.trim() || kind;

        if (!confirm(`Remove ${kind} “${name}” from the current encounter?`)) {
            return;
        }

        button.disabled = true;

        try {
            const result = await request(`/api/combatants/${encodeURIComponent(id)}`, {
                method: 'DELETE',
            });

            await load();
            message(`Removed ${result.name}.`);
        } catch (error) {
            message(error.message);
            button.disabled = false;
        }

        return;
    }

    if (button.dataset.battleActor) {
        openBattleActions(button.dataset.battleActor);
        return;
    }

    if (button.dataset.edit) {
        openEdit(button.dataset.kind, button.dataset.edit);
        return;
    }

    const id =
        button.dataset.ma ||
        button.dataset.mally ||
        button.dataset.mv ||
        button.dataset.mt ||
        button.dataset.t ||
        button.dataset.d ||
        button.dataset.h ||
        button.dataset.r ||
        button.dataset.ca ||
        button.dataset.cl ||
        button.dataset.cv ||
        button.dataset.ct ||
        button.dataset.cd ||
        button.dataset.ch ||
        button.dataset.cr;

    if (!id) {
        return;
    }

    if (button.dataset.ma) {
        patch('monsters', id, { active: !button.classList.contains('on') });
        return;
    }

    if (button.dataset.mally) {
        patch('monsters', id, { ally: !button.classList.contains('on') });
        return;
    }

    if (button.dataset.mv) {
        patch('monsters', id, { visible: !button.classList.contains('on') });
        return;
    }

    if (button.dataset.mt) {
        patch('monsters', id, { in_turn: !button.classList.contains('on') });
        return;
    }

    if (button.dataset.r) {
        await resetCombatantWithFeedback('monsters', id);
        return;
    }

    if (button.dataset.t) {
        patch('monsters', id, {
            [button.dataset.f]: !button.textContent.endsWith('on'),
        });
        return;
    }

    if (button.dataset.d) {
        const entered = prompt('Damage to remove:', '1');
        if (entered === null || entered.trim() === '') {
            return;
        }
        const value = Number(entered);

        if (Number.isSafeInteger(value) && value > 0) {
            patch('monsters', id, { hp_delta: -Math.abs(value) });
        }

        return;
    }

    if (button.dataset.h) {
        const entered = prompt('Healing to add:', '1');
        if (entered === null || entered.trim() === '') {
            return;
        }
        const value = Number(entered);

        if (Number.isSafeInteger(value) && value > 0) {
            patch('monsters', id, { hp_delta: Math.abs(value) });
        }

        return;
    }

    if (button.dataset.ca) {
        patch('characters', id, { active: !button.classList.contains('on') });
        return;
    }

    if (button.dataset.cl) {
        patch('characters', id, { alive: !button.classList.contains('on') });
        return;
    }

    if (button.dataset.cv) {
        patch('characters', id, { visible: !button.classList.contains('on') });
        return;
    }

    if (button.dataset.ct) {
        patch('characters', id, { in_turn: !button.classList.contains('on') });
        return;
    }

    if (button.dataset.cd) {
        const entered = prompt('Damage to remove:', '1');
        if (entered === null || entered.trim() === '') {
            return;
        }
        const value = Number(entered);

        if (Number.isSafeInteger(value) && value > 0) {
            patch('characters', id, { hp_delta: -Math.abs(value) });
        }

        return;
    }

    if (button.dataset.ch) {
        const entered = prompt('Healing to add:', '1');
        if (entered === null || entered.trim() === '') {
            return;
        }
        const value = Number(entered);

        if (Number.isSafeInteger(value) && value > 0) {
            patch('characters', id, { hp_delta: Math.abs(value) });
        }

        return;
    }

    if (button.dataset.cr) {
        await resetCombatantWithFeedback('characters', id);
    }
});

document.addEventListener('change', event => {
    const input = event.target;

    if (input.dataset.mi) {
        patch('monsters', input.dataset.mi, { initiative: input.value === '' ? null : +input.value });
    }

    if (input.dataset.ci) {
        patch('characters', input.dataset.ci, { initiative: input.value === '' ? null : +input.value });
    }

    if (input.dataset.chp && input.value !== '') {
        patch('characters', input.dataset.chp, { hp: +input.value });
    }

    if (input.dataset.cmaxhp && input.value !== '') {
        patch('characters', input.dataset.cmaxhp, { max_hp: +input.value });
    }
});

document.addEventListener('change', event => {
    const checkbox = event.target.closest('input[data-select-kind][data-select-id]');

    if (!checkbox) {
        return;
    }

    updateRowSelection(
        checkbox.dataset.selectKind,
        checkbox.dataset.selectId,
        checkbox.checked,
    );
});

function characterPermanentlyDead(character) {
    return character.life_state==='dead'||(character.death_failures??0)>=3;
}
function turnEligible(combatant) {
    if(!combatant.active||combatant.life_state==='dead')return false;
    return !('monster_species' in combatant)?!characterPermanentlyDead(combatant):Boolean(combatant.alive);
}
function living(){return all().filter(x => x.kind !== 'lair' && turnEligible(x));}

function initiativeOf(combatant) {
    return typeof combatant.initiative === 'number' &&
        Number.isFinite(combatant.initiative)
        ? combatant.initiative
        : null;
}

function initiativeBuckets() {
    const buckets = new Map();

    for (const combatant of living()) {
        const initiative = initiativeOf(combatant);
        const key = initiative === null ? 'blank' : `n:${initiative}`;
        const bucket = buckets.get(key) || {
            initiative,
            members: [],
        };

        bucket.members.push(combatant);
        buckets.set(key, bucket);
    }

    return [...buckets.values()].sort((left, right) => {
        if (left.initiative === null && right.initiative === null) {
            return 0;
        }

        if (left.initiative === null) {
            return 1;
        }

        if (right.initiative === null) {
            return -1;
        }

        return right.initiative - left.initiative;
    });
}

function tiedBuckets() {
    return initiativeBuckets().filter(bucket =>
        bucket.initiative !== null && bucket.members.length > 1,
    );
}

function normalOrder() {
    return initiativeBuckets().flatMap(bucket =>
        bucket.members.map(combatant => combatant.id),
    );
}

function tieUI() {
    const characterIds = new Set(latest.characters.map(character => character.id));
    const ties = tiedBuckets().map(bucket => ({
        ...bucket,
        members: bucket.members.slice().sort((left, right) =>
            Number(characterIds.has(right.id)) - Number(characterIds.has(left.id)),
        ),
    }));

    return ties.map((bucket, bucketIndex) => `
    <div class="tie-title">Initiative ${bucket.initiative}</div>
    ${bucket.members.map((member, memberIndex) => `
        <label class="tie">
        ${esc(member.name)}
        <select data-tie-bucket="${bucketIndex}" data-tie-member="${esc(member.id)}" data-tie-position="${memberIndex + 1}">
            ${bucket.members.map((_, position) => `
            <option value="${position + 1}" ${position === memberIndex ? 'selected' : ''}>
                ${position + 1}
            </option>
            `).join('')}
        </select>
        </label>
    `).join('')}
    `).join('');
}

function swapTiePosition(event) {
    const select = event.target;

    if (!select.matches('select[data-tie-bucket][data-tie-member]')) {
        return;
    }

    const previous = select.dataset.tiePosition;
    const chosen = select.value;

    if (chosen === previous) {
        return;
    }

    const other = [...event.currentTarget.querySelectorAll(
        'select[data-tie-bucket][data-tie-member]',
    )].find(candidate =>
        candidate !== select &&
        candidate.dataset.tieBucket === select.dataset.tieBucket &&
        candidate.value === chosen,
    );

    if (other) {
        other.value = previous;
        other.dataset.tiePosition = previous;
    }

    select.dataset.tiePosition = chosen;
}

document.querySelector('#tieGroups').addEventListener('change', swapTiePosition);

function readTieOrder() {
    const ties = tiedBuckets();
    const orderedBuckets = [];

    for (let index = 0; index < ties.length; index++) {
        const bucket = ties[index];
        const selections = [
            ...document.querySelectorAll(`[data-tie-bucket="${index}"]`),
        ];

        if (selections.length !== bucket.members.length) {
            throw new Error('Tie selection data is incomplete');
        }

        const positions = selections.map(select => Number(select.value));

        if (new Set(positions).size !== positions.length) {
            throw new Error(
                'Each combatant in an initiative tie must have a unique position',
            );
        }

        const positionsByMember = new Map(
            selections.map(select => [
                select.dataset.tieMember,
                Number(select.value),
            ]),
        );

        orderedBuckets.push(
            bucket.members
                .slice()
                .sort((left, right) =>
                    positionsByMember.get(left.id) - positionsByMember.get(right.id),
                )
                .map(combatant => combatant.id),
        );
    }

    return orderedBuckets;
}

async function startBattle(order) {
    try {
        await request('/api/battle/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ order }),
        });

        await load();
    } catch (error) {
        message(error.message);
    }
}

document.querySelector('#startBattle').onclick = () => {
    const order = normalOrder();

    if (!order.length && !(latest.lairs || []).some(x => x.active)) {
        message('Activate at least one turn-eligible participant first');
        return;
    }

    if (!tiedBuckets().length) {
        startBattle(order);
        return;
    }

    document.querySelector('#tieGroups').innerHTML = tieUI();
    document.querySelector('#tieModal').hidden = false;
};

document.querySelector('#confirmOrder').onclick = () => {
    try {
        const orderedTies = readTieOrder();
        let tieIndex = 0;
        const order = [];

        for (const bucket of initiativeBuckets()) {
            if (bucket.initiative !== null && bucket.members.length > 1) {
                order.push(...orderedTies[tieIndex++]);
            } else {
                order.push(...bucket.members.map(combatant => combatant.id));
            }
        }

        document.querySelector('#tieModal').hidden = true;
        startBattle(order);
    } catch (error) {
        message(error.message);
    }
};

document.querySelector('#cancelOrder').onclick = () => {
    document.querySelector('#tieModal').hidden = true;
};

document.querySelector('#nextBattle').onclick = async () => {
    try {
        await request('/api/battle/next', {
            method: 'POST',
        });

        await load();
    } catch (error) {
        message(error.message);
    }
};

document.querySelector('#endBattle').onclick = async () => {
    if (!latest?.battle_order?.length) {
        message('There is no active battle to end.');
        return;
    }

    if (!confirm('End the battle without resetting combatants?')) {
        return;
    }

    try {
        await request('/api/battle/end', {
            method: 'POST',
        });

        await load();
        message('Battle ended. Combatants were not reset.');
    } catch (error) {
        message(error.message);
    }
};

document.querySelector('#resetAll').onclick = async () => {
    if (!confirm('Reset every monster and character?')) {
        return;
    }

    try {
        await request('/api/battle/reset-all', {
            method: 'POST',
        });

        await load();
    } catch (error) {
        message(error.message);
    }
};

let battleOrderFontAdjustmentPending = false;

function updateBattleOrderFontControls(fontSize) {
    const numericSize = Number(fontSize);
    const size = Number.isInteger(numericSize)
        ? Math.max(12, Math.min(40, numericSize))
        : 16;

    const label = document.querySelector('#battleOrderFontSize');
    const decrease = document.querySelector('#battleOrderFontDecrease');
    const increase = document.querySelector('#battleOrderFontIncrease');

    if (label) {
        label.textContent = `${size} px`;
    }

    if (decrease) {
        decrease.disabled = (
            battleOrderFontAdjustmentPending || size <= 12
        );
    }

    if (increase) {
        increase.disabled = (
            battleOrderFontAdjustmentPending || size >= 40
        );
    }
}

