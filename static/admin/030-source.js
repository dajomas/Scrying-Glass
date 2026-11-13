function sortedMonstersForAdmin() {
    const battleOrder = Array.isArray(latest.battle_order)
        ? latest.battle_order
        : [];

    const battleActive = battleOrder.length > 0;

    const battleOrderIndex = new Map(
        battleOrder.map((id, index) => [id, index]),
    );

    function maxHp(monster) {
        const value = Number(monster.max_hp);

        return Number.isFinite(value)
            ? value
            : -Infinity;
    }

    function initiative(monster) {
        const value = monster.initiative;

        return typeof value === 'number' && Number.isFinite(value)
            ? value
            : null;
    }

    function byName(left, right) {
        return String(left.name || '').localeCompare(
            String(right.name || ''),
            undefined,
            { sensitivity: 'base' },
        );
    }

    return [...latest.monsters].sort((left, right) => {
        /*
        * Group 1: Active monsters.
        * Group 2: Inactive monsters.
        */
        if (Boolean(left.active) !== Boolean(right.active)) {
            return left.active ? -1 : 1;
        }

        if (left.active) {
            /*
            * While a battle is active, retain the actual battle order for entries
            * included in it. Active monsters not yet in that order follow.
            */
            if (battleActive) {
                const leftOrder = battleOrderIndex.get(left.id);
                const rightOrder = battleOrderIndex.get(right.id);

                const leftInOrder = leftOrder !== undefined;
                const rightInOrder = rightOrder !== undefined;

                if (leftInOrder !== rightInOrder) {
                    return leftInOrder ? -1 : 1;
                }

                if (leftInOrder && rightInOrder && leftOrder !== rightOrder) {
                    return leftOrder - rightOrder;
                }
            }

            /*
            * Outside battle—or for active entries not present in an existing
            * battle order—sort by Max HP descending.
            */
            if (maxHp(left) !== maxHp(right)) {
                return maxHp(right) - maxHp(left);
            }

            return byName(left, right);
        }

        /*
        * Inactive monsters:
        * numeric initiative first, descending;
        * null/blank initiative after numeric values;
        * then Max HP descending.
        */
        const leftInitiative = initiative(left);
        const rightInitiative = initiative(right);

        const leftHasInitiative = leftInitiative !== null;
        const rightHasInitiative = rightInitiative !== null;

        if (leftHasInitiative !== rightHasInitiative) {
            return leftHasInitiative ? -1 : 1;
        }

        if (
            leftHasInitiative &&
            rightHasInitiative &&
            leftInitiative !== rightInitiative
        ) {
            return rightInitiative - leftInitiative;
        }

        if (maxHp(left) !== maxHp(right)) {
            return maxHp(right) - maxHp(left);
        }

        return byName(left, right);
    });
}

async function load(rethrowErrors = false, current = () => true) {
    return window.scryingAdminFeedback.loadState(
        () => request('/api/state', {}, current), state => {
        latest = state;
        window.scryingStatisticsState?.(latest);
        window.scryingLairsRender?.(latest);
        window.updateEncounterToolsVisibility?.(latest);

        updateBattleOrderFontControls(latest.display?.battle_order_font_size);
        updateBattleRound(latest);

        syncActiveBattleSetupControls();
        renderActiveBattleSetup();

        setBackgroundInputs();

        renderActivityLog(
            Array.isArray(latest.activity_log)
                ? latest.activity_log
                : [],
        );

        updateBattleState(latest);

        updatePaneVisibilityForBattle();

        document.querySelector('#monsters').innerHTML =
            '<table>' +
            '<tr>' +
            '<th scope="col" class="bulk-selection-cell">Select</th>' +
            '<th>Monster</th>' +
            '<th>AC</th>' +
            '<th>HP</th>' +
            '<th>Initiative</th>' +
            '<th>Display/status</th>' +
            '<th>HP change</th>' +
            '</tr>' +
            sortedMonstersForAdmin().map(monsterRow).join('') +
            '</table>';

        document.querySelector('#characters').innerHTML =
            '<table>' +
            '<tr>' +
            '<th scope="col" class="bulk-selection-cell">Select</th>' +
            '<th>Character</th>' +
            '<th>Current / Max HP</th>' +
            '<th>Initiative</th>' +
            '<th>Display/status</th>' +
            '<th>HP change</th>' +
            '</tr>' +
            latest.characters.map(characterRow).join('') +
            '</table>';

        const battleInfo = document.querySelector('#battleInfo');

        if (!latest.battle_order.length) {
            battleInfo.textContent = 'No battle order set';
            return;
        }

        battleInfo.innerHTML =
            'Order: ' +
            latest.battle_order
                .map(id => all().find(combatant => combatant.id === id))
                .filter(Boolean)
                .map(combatant => {
                    const displayName = combatant.monster_species && combatant.ally
                        ? `${combatant.name} - Ally`
                        : combatant.name;

                    const name = '<span style="white-space: nowrap">' + esc(displayName) + '</span>';

                    if (!combatant.in_turn) {
                        return name;
                    }

                    const color = esc(combatant.color || '#ffffff');
                    const combatantId = esc(combatant.id);

                    return `
            <button
                type="button"
                class="battle-order-combatant active-turn"
                data-battle-actor="${combatantId}"
                title="Apply an action as ${esc(displayName)}"
            >
                <strong><u>
                <span
                    class="turn-marker"
                    style="background:${color};color:${color}"
                    aria-label="Current turn"
                    title="Current turn"
                ></span>${name}
                </u></strong>
            </button>
            `;
                })
                .join(' ⇒ ');

    }, rethrowErrors, current);
}

const hideablePanes = [
    {
        key: 'campaign',
        button: document.querySelector('#toggleCampaignPane'),
        pane: document.querySelector('#campaignInputPane'),
        hiddenLabel: 'Hide campaign input',
        visibleLabel: 'Show campaign input',
    },
    {
        key: 'characterInput',
        button: document.querySelector('#toggleCharacterPane'),
        pane: document.querySelector('#characterInputPane'),
        hiddenLabel: 'Hide character input',
        visibleLabel: 'Show character input',
    },
    {
        key: 'battleSetup',
        button: document.querySelector('#toggleBattleSetupPane'),
        pane: document.querySelector('#battleSetupInputPane'),
        hiddenLabel: 'Hide battle setup input',
        visibleLabel: 'Show battle setup input',
    },
    {
        key: 'lairInput',
        button: document.querySelector('#toggleLairPane'),
        pane: document.querySelector('#lairTools'),
        hiddenLabel: 'Hide lair input',
        visibleLabel: 'Show lair input',
    },
    {
        key: 'monsterInput',
        button: document.querySelector('#toggleMonsterPane'),
        pane: document.querySelector('#monsterInputPane'),
        hiddenLabel: 'Hide monster input',
        visibleLabel: 'Show monster input',
    },
    {
        key: 'characterDisplay',
        button: document.querySelector('#toggleCharacterDisplayPane'),
        pane: document.querySelector('#characterDisplayPane'),
        hiddenLabel: 'Hide character display',
        visibleLabel: 'Show character display',
    },
    {
        key: 'monsterDisplay',
        button: document.querySelector('#toggleMonsterDisplayPane'),
        pane: document.querySelector('#monsterDisplayPane'),
        hiddenLabel: 'Hide monster display',
        visibleLabel: 'Show monster display',
    },
];

const paneControlByKey = new Map(
    hideablePanes.map(control => [control.key, control]),
);

/*
* Parent pane -> dependent child pane.
*
* A child pane has two independent pieces of state:
* - whether the pane itself was hidden by its own toggle;
* - whether its own toggle button was visible.
*
* When a parent hides, save both values. When it reopens, restore both values
* exactly as they were. This means:
*
* - Child visible before parent hide -> child and button visible after restore.
* - Child hidden before parent hide -> child remains hidden, but its "Show"
*   button becomes visible again after parent restore.
*/
const paneDependencies = {
    campaign: {
        children: ['characterInput'],
        saved: null,
    },
    battleSetup: {
        children: ['lairInput', 'monsterInput'],
        saved: null,
    },
};

// Tracks whether this page has already performed the automatic collapse for
// the current battle. Once set, a manually opened pane remains untouched.
let collapsedForBattle = false;

function setPaneHidden(control, hidden) {
    control.pane.hidden = hidden;
    control.button.textContent = hidden
        ? control.visibleLabel
        : control.hiddenLabel;
    control.button.setAttribute('aria-expanded', String(!hidden));
}

function hideDependentPane(parentKey) {
    const dependency = paneDependencies[parentKey];
    if (!dependency) return;

    // Preserve each child's independent preference once per hide cycle.
    if (dependency.saved === null) dependency.saved = {};
    for (const key of dependency.children) {
        const child = paneControlByKey.get(key);
        if (!child) continue;
        if (!(key in dependency.saved)) {
            dependency.saved[key] = {
                paneHidden: child.pane.hidden,
                buttonHidden: child.button.hidden,
            };
        }
        setPaneHidden(child, true);
        child.button.hidden = true;
    }
}

function restoreDependentPane(parentKey) {
    const dependency = paneDependencies[parentKey];
    if (!dependency || dependency.saved === null) return;

    for (const key of dependency.children) {
        const child = paneControlByKey.get(key);
        const saved = dependency.saved[key];
        if (!child || !saved) continue;
        setPaneHidden(child, saved.paneHidden);
        child.button.hidden = saved.buttonHidden;
    }
    dependency.saved = null;
}

function setParentPaneHidden(parentKey, hidden) {
    const parent = paneControlByKey.get(parentKey);

    if (!parent) {
        return;
    }

    setPaneHidden(parent, hidden);

    if (hidden) {
        hideDependentPane(parentKey);
    } else {
        restoreDependentPane(parentKey);
    }
}

function setAllHideablePanesHidden(hidden) {
    // A global layout transition supersedes saved parent/child toggle state.
    Object.values(paneDependencies).forEach(dependency => {
        dependency.saved = null;
    });
    hideablePanes.forEach(control => {
        control.button.hidden = false;
        setPaneHidden(control, hidden);
    });
}

hideablePanes.forEach(control => {
    control.button.onclick = () => {
        /*
        * This is intentionally only a direct UI change. It does not modify
        * collapsedForBattle, so battle-state refreshes cannot re-hide a pane
        * that the GM manually opened during the battle.
        */
        const hidden = !control.pane.hidden;

        if (paneDependencies[control.key]) {
            setParentPaneHidden(control.key, hidden);
            return;
        }

        setPaneHidden(control, hidden);
    };
});

function updatePaneVisibilityForBattle() {
    const battleActive = Boolean(
        latest &&
        Array.isArray(latest.battle_order) &&
        latest.battle_order.length,
    );

    if (battleActive) {
        // Collapse once when a battle begins or an active setup is loaded.
        // Subsequent load() calls from Next, edits, bulk actions, etc. do nothing.
        if (!collapsedForBattle) {
            setAllHideablePanesHidden(true);
            collapsedForBattle = true;
        }

        return;
    }

    // A non-battle setup, a new setup, or Reset All restores the normal admin
    // layout and prepares automatic collapse for the next battle.
    if (collapsedForBattle) {
        setAllHideablePanesHidden(false);
        collapsedForBattle = false;

        /*
        * Battle end/reset restores the standard normal layout. Any temporary
        * parent-child hiding state from before the battle is no longer applied.
        */
        Object.values(paneDependencies).forEach(dependency => {
            dependency.saved = null;
        });
    }
}

// Character and monster saves are owned by character-edit-feedback.js and
// monster-initiative-edit.js, which delegate only unsupported kinds here.
document.querySelector('#editForm').onsubmit = event => {
    event.preventDefault();
};

// Setup import (#openImport, #importCampaign, #cancelImport, #importForm) is bound in 040.

function closeCsvImport() {
    csvImportModal.hidden = true;
    csvImportKind = null;
    document.querySelector('#csvImportForm').reset();
}

