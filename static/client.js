let previous = new Map();
const removalTimers = new Map();

function esc(value) {
    return String(value).replace(/[&<>"']/g, character => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;',
    }[character]));
}

function readableText(hex) {
    const value = String(hex || '').replace('#', '');

    if (!/^[0-9a-fA-F]{6}$/.test(value)) {
        return '#fff';
    }

    const red = parseInt(value.slice(0, 2), 16);
    const green = parseInt(value.slice(2, 4), 16);
    const blue = parseInt(value.slice(4, 6), 16);

    const luminance = (
        .2126 * red +
        .7152 * green +
        .0722 * blue
    ) / 255;

    return luminance > .55 ? '#111827' : '#fff';
}

function textPanelStyle(hex) {
    const value = String(hex || '').replace('#', '');

    if (!/^[0-9a-fA-F]{6}$/.test(value)) {
        return {
            background: '#111827',
            color: '#ffffff',
        };
    }

    const red = parseInt(value.slice(0, 2), 16);
    const green = parseInt(value.slice(2, 4), 16);
    const blue = parseInt(value.slice(4, 6), 16);

    const brightness = (
        0.2126 * red +
        0.7152 * green +
        0.0722 * blue
    );

    return brightness > 150
        ? { background: '#111827', color: '#ffffff' }
        : { background: '#f8fafc', color: '#111827' };
}

function entryClass(display) {
    return display.entry_direction === 'from_top'
        ? 'enter-top'
        : 'enter-bottom';
}

function exitClass(display) {
    return display.exit_direction === 'to_top'
        ? 'exit-top'
        : 'exit-bottom';
}

function gridSize(count) {
    if (count <= 1) {
        return [1, 1];
    }

    let rows = 1;
    let columns = 1;

    while (rows * columns < count) {
        if (columns === rows) {
            columns++;
        } else {
            rows++;
        }
    }

    return [rows, columns];
}

function render(state) {
    const background = String(state.display.background || '').trim();

    if (background.startsWith('url(')) {
        document.body.style.backgroundImage = background;
        document.body.style.backgroundPosition = 'center center';
        document.body.style.backgroundSize = 'cover';
        document.body.style.backgroundRepeat = 'no-repeat';
        document.body.style.backgroundAttachment = 'fixed';
        document.body.style.backgroundColor = '#080b14';
    } else {
        document.body.style.background = background || '#080b14';
        document.body.style.backgroundImage = '';
        document.body.style.backgroundPosition = '';
        document.body.style.backgroundSize = '';
        document.body.style.backgroundRepeat = '';
        document.body.style.backgroundAttachment = '';
    }

    const combatantsById = new Map(
        [...state.characters, ...state.monsters]
            .map(combatant => [combatant.id, combatant]),
    );

    const displayOrder = state.display_order ?? state.battle_order;

    const initiativeCombatants = displayOrder
        .map(id => combatantsById.get(id))
        .filter(combatant =>
            combatant && combatant.active && combatant.visible,
        );

    const initiative = document.querySelector('#initiative');

    initiative.hidden = initiativeCombatants.length === 0;

    function displayCombatantName(combatant) {
        return combatant.monster_species && combatant.ally
            ? `${combatant.name} - Ally`
            : combatant.name;
    }

    initiative.innerHTML = initiativeCombatants.map(combatant =>
        `<span class="token ${combatant.alive ? '' : 'dead'} ${combatant.in_turn ? 'turn' : ''}"
        style="background:${esc(combatant.color)};color:${readableText(combatant.color)}">
        ${esc(displayCombatantName(combatant))}
    </span>`
    ).join('');

    const activeMonsters = state.monsters.filter(monster =>
        monster.active && monster.alive && monster.visible,
    );

    const stage = document.querySelector('#stage');

    if (!activeMonsters.length) {
        for (const timer of removalTimers.values()) {
            clearTimeout(timer);
        }
        removalTimers.clear();
        stage.style.gridTemplateColumns = '';
        stage.style.gridTemplateRows = '';
        stage.innerHTML = '<div class="empty"></div>';
        previous.clear();
        return;
    }

    const [rows, columns] = gridSize(activeMonsters.length);

    stage.style.gridAutoFlow = 'row';
    stage.style.gridTemplateColumns =
        `repeat(${columns}, minmax(0, 1fr))`;
    stage.style.gridTemplateRows =
        `repeat(${rows}, minmax(0, 1fr))`;
    stage.style.setProperty(
        '--grid-scale',
        String(Math.max(rows, columns)),
    );

    const current = new Map(
        activeMonsters.map(monster => [monster.id, monster]),
    );

    for (const [id] of previous) {
        if (current.has(id)) {
            continue;
        }

        const oldCard = document.getElementById(`m-${id}`);

        if (oldCard && !removalTimers.has(id)) {
            oldCard.classList.add(exitClass(state.display));

            const timer = setTimeout(() => {
                oldCard.remove();
                removalTimers.delete(id);
            }, 750);

            removalTimers.set(id, timer);
        }
    }

    activeMonsters.forEach((monster, index) => {
        if (removalTimers.has(monster.id)) {
            clearTimeout(removalTimers.get(monster.id));
            removalTimers.delete(monster.id);
        }

        let card = document.getElementById(`m-${monster.id}`);

        if (!card) {
            card = document.createElement('article');
            card.id = `m-${monster.id}`;
            card.className = `monster ${entryClass(state.display)}`;
            stage.appendChild(card);

            requestAnimationFrame(() => {
                card.classList.remove('enter-bottom', 'enter-top');
            });
        }

        card.classList.remove("exit-top", "exit-bottom");

        const row = Math.floor(index / columns) + 1;
        const column = (index % columns) + 1;

        card.style.gridRow = String(row);
        card.style.gridColumn = String(column);
        card.style.color = monster.color;

        const panel = textPanelStyle(monster.color);
        card.style.setProperty('--text-panel-background', panel.background);
        card.style.setProperty('--text-panel-color', panel.color);

        const stats = [];

        if (monster.show_ac) {
            stats.push(`AC ${monster.ac}`);
        }

        if (monster.show_hp) {
            stats.push(`HP ${monster.hp}/${monster.max_hp}`);
        }

        if (monster.show_initiative && monster.initiative !== null) {
            stats.push(`Initiative ${monster.initiative}`);
        }

        card.innerHTML = `
        ${monster.image_url ? `<img src="${esc(monster.image_url)}" alt="">` : ''}
        <div class="text-panel">
        <h1>${esc(displayCombatantName(monster))}${monster.in_turn ? ' ◀' : ''}</h1>
        <div class="type">${esc(monster.monster_species)}</div>
        <div class="stats">${stats.join(' · ')}</div>
        </div>
    `;

    });

    previous = current;
}

async function initial() {
    const response = await fetch('/api/state');

    if (response.ok) {
        render(await response.json());
    }
}

initial();

const websocket = new WebSocket(
    `${location.protocol === 'https:' ? 'wss://' : 'ws://'}${location.host}/ws`,
);

websocket.onmessage = event => {
    const message = JSON.parse(event.data);

    if (message.type === 'state') {
        render(message.state);
    }
};

websocket.onclose = () => {
    setTimeout(() => location.reload(), 1500);
};
