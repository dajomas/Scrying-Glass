CLIENT_HTML = r'''<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Battle Display</title>

  <style>
    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      min-height: 100vh;
      background: #080b14;
      color: #fff;
      font-family: system-ui, sans-serif;
      overflow: hidden;
    }

    #initiative {
      height: 10vh;
      min-height: 54px;
      background: #111827e8;
      display: flex;
      align-items: center;
      gap: .6rem;
      padding: .5rem 1vw;
      overflow-x: auto;
      position: relative;
      z-index: 5;
    }

    .token {
      white-space: nowrap;
      border-radius: 999px;
      padding: .45rem .75rem;
      border: 3px solid #fff;
      font-weight: 800;
      text-shadow: 0 1px 2px rgba(0, 0, 0, .55);
    }

    .token.dead {
      border-color: #000;
      filter: grayscale(1);
      opacity: .6;
    }

    .token.turn {
      border-color: #ef4444;
      box-shadow: 0 0 15px #ef4444;
    }

    #stage {
      height: 90vh;
      position: relative;
      display: grid;
      grid-auto-flow: row;
      gap: .7vh .7vw;
      padding: .7vh .7vw;
      overflow: hidden;
      align-items: stretch;
      justify-items: stretch;
      align-content: start;
    }

    #initiative[hidden] {
      display: none;
    }

    body:has(#initiative[hidden]) #stage {
      height: 100vh;
    }

    .monster {
      min-width: 0;
      min-height: 0;
      position: relative;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      text-align: center;
      padding: 1vh 1vw;
      border-radius: 12px;
      background: linear-gradient(
        135deg,
        rgba(0, 0, 0, .58),
        rgba(0, 0, 0, .2)
      );
      border: 2px solid currentColor;
      box-shadow: 0 6px 18px rgba(0, 0, 0, .45);
      overflow: hidden;
      transition: transform .7s ease, opacity .7s ease;
    }

    .monster img {
      max-height: 53%;
      max-width: 92%;
      object-fit: contain;
      border-radius: 12px;
      filter: drop-shadow(0 7px 14px #000);
    }

    .monster .text-panel {
      max-width: 94%;
      padding: 0.45em 0.7em 0.55em;
      border-radius: 10px;
      background: var(--text-panel-background, #111827);
      color: var(--text-panel-color, #ffffff);
      box-shadow: 0 3px 10px rgba(0, 0, 0, 0.55);
    }

    .monster .text-panel h1 {
      color: inherit;
      margin: 0;
      text-shadow: none;
    }

    .monster .text-panel .type {
      color: inherit;
      margin-top: 0.22em;
    }

    .monster .text-panel .stats {
      color: inherit;
      margin-top: 0.38em;
    }

    h1 {
      font-size: clamp(
        1rem,
        calc(5vmin / var(--grid-scale, 1)),
        5.7rem
      );
      margin: .25rem;
      text-shadow: 0 3px 8px #000;
      line-height: 1.05;
    }

    .type {
      font-size: clamp(
        .75rem,
        calc(2.1vmin / var(--grid-scale, 1)),
        2.5rem
      );
    }

    .stats {
      font-size: clamp(
        .72rem,
        calc(1.9vmin / var(--grid-scale, 1)),
        2.5rem
      );
      margin-top: .45rem;
    }

    .enter-bottom {
      transform: translateY(120%);
      opacity: 0;
    }

    .enter-top {
      transform: translateY(-120%);
      opacity: 0;
    }

    .exit-bottom {
      transform: translateY(120%);
      opacity: 0;
    }

    .exit-top {
      transform: translateY(-120%);
      opacity: 0;
    }

    .empty {
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
    }
  </style>
</head>
<body>
  <div id="initiative"></div>
  <div id="stage"></div>

  <script>
    let previous = new Map();

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
        ? {background: '#111827', color: '#ffffff'}
        : {background: '#f8fafc', color: '#111827'};
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

      const battleOrdered = state.battle_order
        .map(id => combatantsById.get(id))
        .filter(Boolean);

      const additionalVisibleCombatants = [...combatantsById.values()]
        .filter(combatant =>
          combatant.active &&
          combatant.visible &&
          !battleOrdered.some(existing => existing.id === combatant.id),
        )
        .sort((left, right) =>
          (right.initiative ?? -999) - (left.initiative ?? -999),
        );

      const initiativeCombatants = [
        ...battleOrdered.filter(combatant => combatant.visible),
        ...additionalVisibleCombatants,
      ];

      const initiative = document.querySelector('#initiative');

      initiative.hidden = initiativeCombatants.length === 0;

      initiative.innerHTML = initiativeCombatants.map(combatant =>
        `<span class="token ${combatant.alive ? '' : 'dead'} ${combatant.in_turn ? 'turn' : ''}"
          style="background:${esc(combatant.color)};color:${readableText(combatant.color)}">
          ${esc(combatant.name)}
        </span>`
      ).join('');

      const activeMonsters = state.monsters.filter(monster =>
        monster.active && monster.alive,
      );

      const stage = document.querySelector('#stage');

      if (!activeMonsters.length) {
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

        if (oldCard) {
          oldCard.classList.add(exitClass(state.display));
          setTimeout(() => oldCard.remove(), 750);
        }
      }

      activeMonsters.forEach((monster, index) => {
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
            <h1>${esc(monster.name)}${monster.in_turn ? ' ◀' : ''}</h1>
            <div class="type">${esc(monster.monster_type)}</div>
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
  </script>
</body>
</html>'''
