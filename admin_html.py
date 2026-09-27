ADMIN_HTML = r'''<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Monster Display Admin</title>

  <style>
    body {
      font-family: system-ui, sans-serif;
      background: #111827;
      color: #eef2ff;
      margin: 0;
      padding: 1rem;
    }

    main {
      max-width: 1260px;
      margin: auto;
    }

    section {
      background: #1f2937;
      border-radius: 10px;
      padding: 1rem;
      margin: 1rem 0;
    }

    input,
    button,
    select {
      padding: .55rem;
      margin: .18rem;
      border-radius: 6px;
      border: 1px solid #64748b;
    }

    button {
      cursor: pointer;
      background: #2563eb;
      color: #fff;
    }

    .danger { background: #b91c1c; }
    .on { background: #047857; }
    .battle { background: #7f1d1d; }
    .reset { background: #4c1d95; }
    .edit { background: #0f766e; }
    .import { background: #7c3aed; }
    .roll { background: #b45309; }

    .battle-state {
      display: inline-flex;
      align-items: center;
      min-height: 2.2rem;
      padding: 0 0.75rem;
      border-radius: 999px;
      font-weight: 800;
      letter-spacing: 0.03em;
    }

    .battle-state.active {
      background: #047857;
      color: #ecfdf5;
    }

    .battle-state.inactive {
      background: #475569;
      color: #e2e8f0;
    }

    table {
      width: 100%;
      border-collapse: collapse;
    }

    th,
    td {
      padding: .45rem;
      border-bottom: 1px solid #475569;
      text-align: left;
      vertical-align: top;
    }

    .row {
      display: flex;
      flex-wrap: wrap;
      gap: .4rem;
      align-items: center;
    }

    .message {
      min-height: 1.4rem;
      color: #fbbf24;
    }

    .dead {
      opacity: .55;
      text-decoration: line-through;
    }

    .pane-toggle {
      background: #334155;
    }

    .pane[hidden] {
      display: none;
    }

    .turn-marker {
      display: inline-block;
      width: .85em;
      height: .85em;
      margin-right: .35em;
      border: 1px solid #ffffff99;
      border-radius: 50%;
      vertical-align: -.05em;
      box-shadow: 0 0 5px currentColor;
    }

    .battle-order-combatant {
      margin: 0;
      padding: 0;
      border: 0;
      background: transparent;
      color: inherit;
      font: inherit;
      line-height: inherit;
    }

    .battle-order-combatant.active-turn {
      cursor: pointer;
    }

    .battle-order-combatant.active-turn:hover,
    .battle-order-combatant.active-turn:focus-visible {
      outline: 2px solid #fbbf24;
      outline-offset: 3px;
      border-radius: 3px;
    }

    .battle-action-form {
      display: grid;
      gap: 0.7rem;
    }

    .battle-action-row {
      display: grid;
      grid-template-columns: minmax(10rem, 1fr) minmax(8rem, 10rem) minmax(7rem, 8rem) auto;
      gap: 0.5rem;
      align-items: end;
      border: 1px solid #475569;
      border-radius: 8px;
      padding: 0.65rem;
    }

    .battle-action-row label {
      display: grid;
      gap: 0.25rem;
    }

    .battle-action-row .amount-field[hidden] {
      display: none;
    }

    @media (max-width: 700px) {
      .battle-action-row {
        grid-template-columns: 1fr;
      }
    }

    .modal {
      position: fixed;
      inset: 0;
      background: #000a;
      display: grid;
      place-items: center;
      z-index: 10;
    }

    .modal[hidden] {
      display: none !important;
    }

    .modal > div {
      background: #1f2937;
      padding: 1.25rem;
      border-radius: 10px;
      width: min(700px, 94vw);
      max-height: 94vh;
      overflow: auto;
    }

    .tie {
      display: grid;
      grid-template-columns: minmax(10rem, 1fr) 7rem;
      gap: .45rem;
      align-items: center;
      margin: .35rem 0;
    }

    .tie select {
      width: 100%;
    }

    .tie-title {
      font-weight: 700;
      margin-top: .85rem;
    }

    .monster-bulk-controls {
      margin: 0.5rem 0 1rem;
    }

    .bulk-label {
      color: #cbd5e1;
      font-weight: 700;
    }

    .bulk-monster-toggle {
      background: #3b556f;
    }

    .bulk-monster-toggle:hover {
      background: #4b6680;
    }

    .initiative-edit {
      width: 5ch;
      min-width: 5ch;
    }

    .hp-edit { width: 5.5rem; }
    .setup-name { min-width: 14rem; }

    .edit-form {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: .55rem;
    }

    .edit-form label {
      display: grid;
      gap: .25rem;
    }

    .edit-form .full {
      grid-column: 1 / -1;
    }

    .edit-form .actions {
      grid-column: 1 / -1;
      display: flex;
      gap: .5rem;
      margin-top: .4rem;
    }

    .import-form {
      display: grid;
      gap: .7rem;
    }

    .import-form label {
      display: grid;
      gap: .25rem;
    }

    .import-form .actions {
      display: flex;
      gap: .5rem;
    }

    .activity-log {
      max-height: 24rem;
      overflow: auto;
      border: 1px solid #475569;
      border-radius: 8px;
    }

    .activity-log table {
      min-width: 54rem;
    }

    .activity-state-alive {
      color: #86efac;
      font-weight: 800;
    }

    .activity-state-dead {
      color: #fca5a5;
      font-weight: 800;
    }

    .activity-action-negative {
      color: #fca5a5;
      font-weight: 800;
    }

    .activity-action-positive {
      color: #86efac;
      font-weight: 800;
    }

  </style>
</head>
<body>
  <main>
    <h1>Monster Display — Admin</h1>
    <p id="message" class="message"></p>

    <section>
      <div class="row">
        <button
          id="toggleSetupPane"
          class="pane-toggle"
          type="button"
          aria-controls="setupInputPane"
          aria-expanded="true"
        >
          Hide Setup input
        </button>
        <button
          id="toggleMonsterPane"
          class="pane-toggle"
          type="button"
          aria-controls="monsterInputPane"
          aria-expanded="true"
        >
          Hide monster input
        </button>
        <button
          id="toggleCharacterPane"
          class="pane-toggle"
          type="button"
          aria-controls="characterInputPane"
          aria-expanded="true"
        >
          Hide character input
        </button>
        <button
          id="toggleMonsterDisplayPane"
          class="pane-toggle"
          type="button"
          aria-controls="monsterDisplayPane"
          aria-expanded="true"
        >
          Hide monster display
        </button>
        <button
          id="toggleCharacterDisplayPane"
          class="pane-toggle"
          type="button"
          aria-controls="characterDisplayPane"
          aria-expanded="true"
        >
          Hide character display
        </button>
      </div>
    </section>

    <section>
      <div class="row">
        <h2>Battle</h2>
        <span id="battleState" class="battle-state inactive">
          Inactive
        </span>
      </div>
      <div class="row">
        <button id="startBattle" class="battle">Start battle</button>
        <button id="nextBattle" class="battle">Next</button>
        <button id="resetAll" class="reset">Reset All</button>
      </div>
      <div class="row">&nbsp;</div>
      <div class="row">
        <span id="battleInfo"></span>
      </div>
    </section>

    <section id="setupInputPane" class="pane">
      <div>
        <div class="row">
          <h2>Battle setups</h2>
        </div>
        <input id="setupName" class="setup-name" placeholder="Battle setup name">
        <button id="newSetup" class="reset">New</button>
        <button id="saveSetup">Save</button>
        <select id="setupSelect">
          <option value="">Load saved setup…</option>
        </select>
        <button id="loadSetup">Load</button>
        <button id="openImport" class="import">Import from setup</button>
        <button id="openMonsterCsvImport" class="import">Import monsters CSV</button>
        <button id="openCharacterCsvImport" class="import">Import characters CSV</button>
      </div>
    </section>

    <section id="monsterInputPane" class="pane">
      <div class="row">
        <h2>Add monster</h2>
      </div>

      <div>
        <form id="monsterForm" class="row">
          <input name="name" placeholder="Name" required>
          <input name="monster_type" placeholder="Monster type" required>
          <input name="ac" type="number" placeholder="AC" required>
          <input name="hp" type="number" placeholder="HP" required>
          <input name="quantity" type="number" min="1" max="50" value="1" title="Number of monsters">
          <input name="color" type="color" value="#842029">
          <input name="image" type="file" accept="image/*">
          <button>Add manually</button>
        </form>

        <p>Or import a JSON <code>.monster</code> file:</p>

        <form id="monsterUpload" class="row">
          <input name="monster_file" type="file" accept=".monster,application/json" required>
          <input name="quantity" type="number" min="1" max="50" value="1" title="Number of monsters">
          <input name="color" type="color" value="#842029">
          <input name="image" type="file" accept="image/*">
          <button>Import .monster</button>
        </form>
      </div>
    </section>

    <section id="characterInputPane" class="pane">
      <div class="row">
        <h2>Add character</h2>
      </div>

      <div>
        <form id="characterForm" class="row">
          <input name="name" placeholder="Name" required>
          <input name="color" type="color" value="#1f4e79">
          <input name="hp" type="number" min="0" value="1" required>
          <input name="initiative" type="number" placeholder="Initiative (optional)">
          <button>Add character</button>
        </form>
      </div>
    </section>

    <section id="monsterDisplayPane" class="pane">
      <div class="row">
        <h2>Monsters</h2>
        <button id="rollMonsterInitiative" class="roll">Roll monster initiatives (d20)</button>
      </div>
      <div class="row monster-bulk-controls" aria-label="Bulk monster controls">
        <span class="bulk-label">All monsters:</span>
        <button type="button" class="bulk-monster-toggle" data-bulk-field="active">Active all</button>
        <button type="button" class="bulk-monster-toggle" data-bulk-field="ally">Ally all</button>
        <button type="button" class="bulk-monster-toggle" data-bulk-field="show_ac">AC all</button>
        <button type="button" class="bulk-monster-toggle" data-bulk-field="show_hp">HP all</button>
        <button type="button" class="bulk-monster-toggle" data-bulk-field="show_initiative">Init all</button>
      </div>
      <div id="monsters"></div>
    </section>

    <section id="characterDisplayPane" class="pane">
      <h2>Characters</h2>
      <div id="characters"></div>
    </section>
  </main>

  <section>
    <div class="row">
      <h2>Activity log</h2>

      <button
        id="exportActivityLogCsv"
        type="button"
        class="import"
      >
        Export CSV
      </button>

      <button
        id="exportActivityLogJson"
        type="button"
        class="import"
      >
        Export JSON
      </button>
      <button
        id="clearActivityLog"
        type="button"
        class="danger"
      >
        Clear log
      </button>
    </div>

    <div id="activityLog" class="activity-log">
      No activity recorded.
    </div>
  </section>

  <div id="tieModal" class="modal" hidden>
    <div>
      <h2>Resolve tied initiative</h2>
      <p>Choose a unique position for every combatant in each tied initiative group. Position 1 acts first within that group.</p>
      <div id="tieGroups"></div>
      <button id="confirmOrder">Start battle</button>
      <button id="cancelOrder">Cancel</button>
    </div>
  </div>

  <div id="editModal" class="modal" hidden>
    <div>
      <h2 id="editTitle">Edit combatant</h2>
      <form id="editForm" class="edit-form"></form>
    </div>
  </div>

  <div id="importModal" class="modal" hidden>
    <div>
      <h2>Import combatants from a saved setup</h2>
      <p>Imported combatants receive new IDs and reset runtime state. The current battle order is not changed.</p>

      <form id="importForm" class="import-form">
        <label>
          Saved setup
          <select id="importSetup" name="name" required></select>
        </label>

        <label>
          Import
          <select name="kind">
            <option value="characters">Characters only</option>
            <option value="monsters">Monsters only</option>
            <option value="both">Characters and monsters</option>
          </select>
        </label>

        <div class="actions">
          <button class="import">Import</button>
          <button type="button" id="cancelImport">Cancel</button>
        </div>
      </form>
    </div>
  </div>

  <div id="csvImportModal" class="modal" hidden>
    <div>
      <h2 id="csvImportTitle">Import CSV</h2>

      <p id="csvImportHelp">
        Select a CSV file to add records to the current setup.
      </p>

      <form id="csvImportForm" class="import-form">
        <label>
          CSV file
          <input
            id="csvImportFile"
            name="csv_file"
            type="file"
            accept=".csv,text/csv"
            required
          >
        </label>

        <div class="actions">
          <button class="import">Import CSV</button>
          <button type="button" id="cancelCsvImport">Cancel</button>
        </div>
      </form>
    </div>
  </div>

  <div id="battleActionModal" class="modal" hidden>
    <div>
      <h2 id="battleActionTitle">Battle actions</h2>

      <p id="battleActionHelp">
        Choose one or more targets and actions for the current combatant.
      </p>

      <form id="battleActionForm" class="battle-action-form">
        <div id="battleActionRows"></div>

        <div class="actions">
          <button type="button" id="addBattleActionTarget">
            Add target
          </button>
          <button type="submit" class="battle">
            Apply
          </button>
          <button type="button" id="cancelBattleActions">
            Cancel
          </button>
        </div>
      </form>
    </div>
  </div>

  <script>
    let latest;
    let editing = null;

    const message = text => {
      document.querySelector('#message').textContent = text;
    };

    const all = () => [
      ...latest.monsters,
      ...latest.characters,
    ];

    const editModal = document.querySelector('#editModal');
    const importModal = document.querySelector('#importModal');
    const csvImportModal = document.querySelector('#csvImportModal');

    let csvImportKind = null;

    function closeEdit() {
      editModal.hidden = true;
      editing = null;
      document.querySelector('#editForm').innerHTML = '';
    }

    function closeImport() {
      importModal.hidden = true;
    }

    async function request(url, options = {}) {
      const response = await fetch(url, options);

      if (!response.ok) {
        const error = await response.json().catch(() => ({
          detail: response.statusText,
        }));

        throw new Error(error.detail);
      }

      return response.json().catch(() => null);
    }

    function esc(value) {
      return String(value).replace(/[&<>"']/g, character => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;',
      }[character]));
    }

    function numberValue(form, name, fallback) {
      const value = form.elements[name].value;
      return value === '' ? fallback : +value;
    }

    async function patch(kind, id, data) {
      try {
        await request(`/api/${kind}/${id}`, {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(data),
        });

        await load();
      } catch (error) {
        message(error.message);
      }
    }

    function monsterRow(monster) {
      const displayName = monster.ally
        ? `${monster.name} - Ally`
        : monster.name;

      return `
        <tr class="${monster.alive ? '' : 'dead'}">
          <td>
            ${esc(displayName)}
            <br>
            <small>${esc(monster.monster_type)}</small>
          </td>
          <td>${monster.ac}</td>
          <td>${monster.hp}/${monster.max_hp}</td>
          <td>
            <input
              class="initiative-edit"
              data-mi="${monster.id}"
              type="number"
              value="${monster.initiative ?? ''}"
              placeholder="init"
            >
          </td>
          <td>
            <button data-edit="${monster.id}" data-kind="monsters" class="edit">Edit</button>
            <button class="${monster.active ? 'on' : ''}" data-ma="${monster.id}">${monster.active ? 'Active' : 'Off'}</button>
            <button class="${monster.ally ? 'on' : ''}" data-mally="${monster.id}">Ally</button>
            <button class="${monster.visible ? 'on' : ''}" data-mv="${monster.id}">Visible</button>
            <button data-mt="${monster.id}" class="${monster.in_turn ? 'on' : ''}">Turn</button>
            <button data-t="${monster.id}" data-f="show_ac">AC ${monster.show_ac ? 'on' : 'off'}</button>
            <button data-t="${monster.id}" data-f="show_hp">HP ${monster.show_hp ? 'on' : 'off'}</button>
            <button data-t="${monster.id}" data-f="show_initiative">Init ${monster.show_initiative ? 'on' : 'off'}</button>
            <button data-r="${monster.id}" class="reset">Reset</button>
            <button type="button" class="danger" data-remove="${monster.id}" data-remove-kind="monster">Remove</button>
          </td>
          <td>
            <button data-d="${monster.id}" class="danger">Damage</button>
            <button data-h="${monster.id}">Heal</button>
          </td>
        </tr>
      `;
    }

    function characterRow(character) {
      return `
        <tr class="${character.alive ? '' : 'dead'}">
          <td>${esc(character.name)}</td>
          <td>
            <input class="hp-edit" data-chp="${character.id}" type="number" min="0" value="${character.hp}">
            /
            <input class="hp-edit" data-cmaxhp="${character.id}" type="number" min="0" value="${character.max_hp}">
          </td>
          <td>
            <input
              class="initiative-edit"
              data-ci="${character.id}"
              type="number"
              value="${character.initiative ?? ''}"
              placeholder="init"
            >
          </td>
          <td>
            <button data-edit="${character.id}" data-kind="characters" class="edit">Edit</button>
            <button class="${character.active ? 'on' : ''}" data-ca="${character.id}">${character.active ? 'Active' : 'Off'}</button>
            <button class="${character.alive ? 'on' : ''}" data-cl="${character.id}">${character.alive ? 'Alive' : 'Dead'}</button>
            <button class="${character.visible ? 'on' : ''}" data-cv="${character.id}">Visible</button>
            <button data-ct="${character.id}" class="${character.in_turn ? 'on' : ''}">Turn</button>
            <button data-cr="${character.id}" class="reset">Reset</button>
            <button type="button" class="danger" data-remove="${character.id}" data-remove-kind="character">Remove</button>
          </td>
          <td>
            <button data-cd="${character.id}" class="danger">Damage</button>
            <button data-ch="${character.id}">Heal</button>
          </td>
        </tr>
      `;
    }

    function monsterEdit(monster) {
      return `
        <label>
          Name
          <input name="name" required value="${esc(monster.name)}">
        </label>
        <label>
          Monster type
          <input name="monster_type" required value="${esc(monster.monster_type)}">
        </label>
        <label>
          AC
          <input name="ac" type="number" min="0" value="${monster.ac}">
        </label>
        <label>
          Color
          <input name="color" type="color" value="${esc(monster.color)}">
        </label>
        <label>
          Current HP
          <input name="hp" type="number" value="${monster.hp}">
        </label>
        <label>
          Max HP
          <input name="max_hp" type="number" min="0" value="${monster.max_hp}">
        </label>
        <label>
          Reset HP
          <input name="original_hp" type="number" min="0" value="${monster.original_hp}">
        </label>
        <label>
          Initiative
          <input name="initiative" type="number" min="-100" max="100" value="${monster.initiative ?? ''}">
        </label>
        <label>
          Ally
          <select name="ally">
            <option value="false" ${monster.ally ? '' : 'selected'}>No</option>
            <option value="true" ${monster.ally ? 'selected' : ''}>Yes</option>
          </select>
        </label>
        <label>
          Replace image
          <input name="image" type="file" accept="image/*">
        </label>
        <div class="actions">
          <button>Save monster</button>
          <button type="button" id="cancelEdit">Cancel</button>
        </div>
      `;
    }

    function characterEdit(character) {
      return `
        <label>
          Name
          <input name="name" required value="${esc(character.name)}">
        </label>
        <label>
          Color
          <input name="color" type="color" value="${esc(character.color)}">
        </label>
        <label>
          Current HP
          <input name="hp" type="number" value="${character.hp}">
        </label>
        <label>
          Max HP
          <input name="max_hp" type="number" min="0" value="${character.max_hp}">
        </label>
        <label>
          Initiative
          <input name="initiative" type="number" min="-100" max="100" value="${character.initiative ?? ''}">
        </label>
        <div class="actions">
          <button>Save character</button>
          <button type="button" id="cancelEdit">Cancel</button>
        </div>
      `;
    }

    function openEdit(kind, id) {
      const item = (kind === 'monsters' ? latest.monsters : latest.characters)
        .find(combatant => combatant.id === id);

      if (!item) {
        return;
      }

      editing = {kind, id};

      document.querySelector('#editTitle').textContent =
        `Edit ${kind === 'monsters' ? 'monster' : 'character'}: ${item.name}`;

      document.querySelector('#editForm').innerHTML =
        kind === 'monsters' ? monsterEdit(item) : characterEdit(item);

      document.querySelector('#cancelEdit').onclick = closeEdit;
      editModal.hidden = false;
    }

    async function setups() {
      try {
        const result = await request('/api/setups');

        const setupSelect = document.querySelector('#setupSelect');
        const oldSetupValue = setupSelect.value;

        setupSelect.innerHTML =
          '<option value="">Load saved setup…</option>' +
          result.names
            .map(name => `<option value="${esc(name)}">${esc(name)}</option>`)
            .join('');

        if (result.names.includes(oldSetupValue)) {
          setupSelect.value = oldSetupValue;
        }

        const importSelect = document.querySelector('#importSetup');
        const oldImportValue = importSelect.value;

        importSelect.innerHTML =
          '<option value="">Choose setup…</option>' +
          result.names
            .map(name => `<option value="${esc(name)}">${esc(name)}</option>`)
            .join('');

        if (result.names.includes(oldImportValue)) {
          importSelect.value = oldImportValue;
        }
      } catch (error) {
        message(error.message);
      }
    }

    function updateBattleState(state) {
      const battleState = document.querySelector('#battleState');

      if (!battleState) {
        return;
      }

      const battleOrder = Array.isArray(state?.battle_order)
        ? state.battle_order
        : [];

      const battleActive = battleOrder.length > 0;

      battleState.textContent = battleActive ? 'Active' : 'Inactive';
      battleState.classList.toggle('active', battleActive);
      battleState.classList.toggle('inactive', !battleActive);
    }

    function activityStateClass(state) {
      return state === 'alive'
        ? 'activity-state-alive'
        : state === 'dead'
          ? 'activity-state-dead'
          : '';
    }

    function activityActionClass(action) {
      if (action === 'heal' || action === 'buff') {
        return 'activity-action-positive';
      }

      if (action === 'damage' || action === 'debuff') {
        return 'activity-action-negative';
      }

      return '';
    }

    function activityTime(value) {
      const date = new Date(value);

      return Number.isNaN(date.getTime())
        ? esc(value || '')
        : esc(date.toLocaleString());
    }

    function renderActivityLog(entries) {
      const container = document.querySelector('#activityLog');

      if (!entries.length) {
        container.textContent = 'No activity recorded.';
        return;
      }

      const rows = [...entries]
        .reverse()
        .map(entry => `
          <tr>
            <td>${activityTime(entry.timestamp)}</td>
            <td>${esc(entry.active_combatant || 'System')}</td>
            <td class="${activityStateClass(entry.active_combatant_state)}">
              ${esc(entry.active_combatant_state || 'unknown')}
            </td>
            <td>${esc(entry.target_combatant || '')}</td>
            <td class="${activityStateClass(entry.target_combatant_state)}">
              ${esc(entry.target_combatant_state || 'unknown')}
            </td>
            <td class="${activityActionClass(entry.action)}">
              ${esc(entry.action || '')}
            </td>
            <td>${esc(entry.amount ?? '')}</td>
          </tr>
        `)
        .join('');

      container.innerHTML = `
        <table>
          <tr>
            <th>Time</th>
            <th>Active combatant</th>
            <th>Active state</th>
            <th>Target</th>
            <th>Target state</th>
            <th>Action</th>
            <th>Amount</th>
          </tr>
          ${rows}
        </table>
      `;
    }

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
          {sensitivity: 'base'},
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

    async function load() {
      try {
        latest = await request('/api/state');

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
              const displayName = combatant.monster_type && combatant.ally
                ? `${combatant.name} - Ally`
                : combatant.name;

              const name = esc(displayName);

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
                  title="Apply an action as ${name}"
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
            .join(' → ');

      } catch (error) {
        message(error.message);
      }
    }

    const hideablePanes = [
      {
        button: document.querySelector('#toggleSetupPane'),
        pane: document.querySelector('#setupInputPane'),
        hiddenLabel: 'Hide setup input',
        visibleLabel: 'Show setup input',
      },
      {
        button: document.querySelector('#toggleMonsterPane'),
        pane: document.querySelector('#monsterInputPane'),
        hiddenLabel: 'Hide monster input',
        visibleLabel: 'Show monster input',
      },
      {
        button: document.querySelector('#toggleCharacterPane'),
        pane: document.querySelector('#characterInputPane'),
        hiddenLabel: 'Hide character input',
        visibleLabel: 'Show character input',
      },
      {
        button: document.querySelector('#toggleMonsterDisplayPane'),
        pane: document.querySelector('#monsterDisplayPane'),
        hiddenLabel: 'Hide monster display',
        visibleLabel: 'Show monster display',
      },
      {
        button: document.querySelector('#toggleCharacterDisplayPane'),
        pane: document.querySelector('#characterDisplayPane'),
        hiddenLabel: 'Hide character display',
        visibleLabel: 'Show character display',
      },
    ];

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

    function setAllHideablePanesHidden(hidden) {
      hideablePanes.forEach(control => setPaneHidden(control, hidden));
    }

    hideablePanes.forEach(control => {
      control.button.onclick = () => {
        // This is intentionally only a direct UI change. It does not modify
        // collapsedForBattle, so battle-state refreshes cannot re-hide a pane that
        // the GM manually opened during the battle.
        setPaneHidden(control, !control.pane.hidden);
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
      }

      collapsedForBattle = false;
    }

    document.querySelector('#editForm').onsubmit = async event => {
      event.preventDefault();

      if (!editing) {
        return;
      }

      const form = event.target;
      const data = {
        name: form.elements.name.value.trim(),
        color: form.elements.color.value,
        hp: numberValue(form, 'hp', 0),
        max_hp: numberValue(form, 'max_hp', 0),
        initiative: form.elements.initiative.value === ''
          ? null
          : +form.elements.initiative.value,
      };

      if (editing.kind === 'monsters') {
        data.monster_type = form.elements.monster_type.value.trim();
        data.ac = numberValue(form, 'ac', 0);
        data.original_hp = numberValue(form, 'original_hp', 0);
        data.ally = form.elements.ally.value === 'true';

        const image = form.elements.image.files[0];

        try {
          if (image) {
            const formData = new FormData();

            Object.entries(data).forEach(([key, value]) => {
              formData.append(key, value === null ? '' : String(value));
            });

            formData.append('image', image);

            const response = await fetch(
              `/api/monsters/${editing.id}/edit`,
              {
                method: 'POST',
                body: formData,
              },
            );

            if (!response.ok) {
              const error = await response.json().catch(() => ({
                detail: response.statusText,
              }));

              throw new Error(error.detail);
            }
          } else {
            await request(`/api/monsters/${editing.id}`, {
              method: 'PATCH',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify(data),
            });
          }
        } catch (error) {
          message(error.message);
          return;
        }
      } else {
        if (data.initiative === null) {
          delete data.initiative;
        }

        try {
          await request(`/api/characters/${editing.id}`, {
            method: 'PATCH',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
          });
        } catch (error) {
          message(error.message);
          return;
        }
      }

      closeEdit();
      await load();
    };

    document.querySelector('#openImport').onclick = async () => {
      await setups();
      importModal.hidden = false;
    };

    document.querySelector('#cancelImport').onclick = closeImport;

    document.querySelector('#importForm').onsubmit = async event => {
      event.preventDefault();

      const formData = new FormData(event.target);
      const name = formData.get('name');
      const kind = formData.get('kind');

      if (!name) {
        message('Choose a saved setup to import from');
        return;
      }

      if (!confirm(`Import ${kind} from ${name} into the current setup?`)) {
        return;
      }

      try {
        const result = await request('/api/setups/import', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({name, kind}),
        });

        closeImport();
        await load();

        message(
          `Imported ${result.characters} character(s) and ` +
          `${result.monsters} monster(s) from ${result.name}`,
        );
      } catch (error) {
        message(error.message);
      }
    };

    function closeCsvImport() {
      csvImportModal.hidden = true;
      csvImportKind = null;
      document.querySelector('#csvImportForm').reset();
    }

    function openCsvImport(kind) {
      csvImportKind = kind;

      const isMonster = kind === 'monsters';

      document.querySelector('#csvImportTitle').textContent =
        isMonster ? 'Import monsters from CSV' : 'Import characters from CSV';

      document.querySelector('#csvImportHelp').textContent = isMonster
        ? 'Required columns: name, monster_type (or type), ac, hp. '
          + 'Optional id values are preserved; blank or missing IDs are generated automatically.'
        : 'Required column: name. Optional id values are preserved; blank or missing IDs are generated automatically.';

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

      const form = event.target;
      const submit = form.querySelector('button[type="submit"], button.import');

      submit.disabled = true;

      try {
        const endpoint = csvImportKind === 'monsters'
          ? '/api/monsters/import-csv'
          : '/api/characters/import-csv';

        const result = await request(endpoint, {
          method: 'POST',
          body: new FormData(form),
        });

        closeCsvImport();
        await load();

        message(
          `Imported ${result.count} ${
            csvImportKind === 'monsters' ? 'monster' : 'character'
          }${result.count === 1 ? '' : 's'} from CSV.`,
        );
      } catch (error) {
        message(error.message);
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
          `Cleared ${result.cleared} activity log ${
            result.cleared === 1 ? 'entry' : 'entries'
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

    document.querySelector('#rollMonsterInitiative').onclick = async () => {
      if (!latest.monsters.length) {
        message('There are no monsters to roll initiative for');
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
        message(`Rolled d20 initiative for ${result.count} monster(s)`);
      } catch (error) {
        message(error.message);
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

    });

    document.querySelector('#newSetup').onclick = async () => {
      if (!confirm('Discard the current battle setup and create a new blank setup?')) {
        return;
      }

      try {
        await request('/api/setups/new', {
          method: 'POST',
        });

        document.querySelector('#setupName').value = '';
        document.querySelector('#setupSelect').value = '';
        await load();
      } catch (error) {
        message(error.message);
      }
    };

    document.querySelector('#saveSetup').onclick = async () => {
      const name = document.querySelector('#setupName').value.trim();

      if (!name) {
        message('Enter a battle setup name before saving');
        return;
      }

      try {
        const result = await request('/api/setups/save', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({name}),
        });

        document.querySelector('#setupName').value = result.name;
        await setups();
        document.querySelector('#setupSelect').value = result.name;
        message(`Saved setup: ${result.name}`);
      } catch (error) {
        message(error.message);
      }
    };

    document.querySelector('#loadSetup').onclick = async () => {
      const name = document.querySelector('#setupSelect').value;

      if (!name) {
        message('Choose a saved setup to load');
        return;
      }

      if (!confirm(`Load ${name} and replace the current battle setup?`)) {
        return;
      }

      try {
        const result = await request('/api/setups/load', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({name}),
        });

        document.querySelector('#setupName').value = result.name;
        await load();
        message(`Loaded setup: ${result.name}`);
      } catch (error) {
        message(error.message);
      }
    };

    document.querySelector('#monsterForm').onsubmit = async event => {
      event.preventDefault();

      try {
        const result = await request('/api/monsters', {
          method: 'POST',
          body: new FormData(event.target),
        });

        message(`Added ${result.length} monster${result.length === 1 ? '' : 's'}`);
        event.target.reset();
        await load();
      } catch (error) {
        message(error.message);
      }
    };

    document.querySelector('#monsterUpload').onsubmit = async event => {
      event.preventDefault();

      try {
        const result = await request('/api/monsters/import', {
          method: 'POST',
          body: new FormData(event.target),
        });

        message(`Imported ${result.length} monster${result.length === 1 ? '' : 's'}`);
        event.target.reset();
        await load();
      } catch (error) {
        message(error.message);
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

        event.target.reset();
        await load();
      } catch (error) {
        message(error.message);
      }
    };

    async function bulkToggleMonsters(field) {
      return request('/api/monsters/bulk-toggle', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({field}),
      });
    }

    document.querySelectorAll('.bulk-monster-toggle').forEach(button => {
      button.addEventListener('click', async () => {
        button.disabled = true;

        try {
          await bulkToggleMonsters(button.dataset.bulkField);
          await load();
        } catch (error) {
          console.error(error);
          message(error.message || 'Could not update all monsters.');
        } finally {
          button.disabled = false;
        }
      });
    });

    const battleActionModal = document.querySelector('#battleActionModal');
    const battleActionForm = document.querySelector('#battleActionForm');
    const battleActionRows = document.querySelector('#battleActionRows');
    let battleActionActorId = null;

    function activeBattleTargets() {
      if (!latest) {
        return [];
      }

      return [...latest.monsters, ...latest.characters]
        .filter(combatant => combatant.active && combatant.alive)
        .sort((left, right) => left.name.localeCompare(right.name));
    }

    function closeBattleActions() {
      battleActionModal.hidden = true;
      battleActionActorId = null;
      battleActionRows.innerHTML = '';
    }

    function actionAmountRequired(action) {
      return action === 'damage' || action === 'heal';
    }

    function updateActionRowAmount(row) {
      const action = row.querySelector('[data-action-kind]').value;
      const amountField = row.querySelector('.amount-field');
      const amountInput = row.querySelector('[data-action-amount]');
      const required = actionAmountRequired(action);

      amountField.hidden = !required;
      amountInput.required = required;

      if (!required) {
        amountInput.value = '';
      }
    }

    function addBattleActionRow() {
      const targets = activeBattleTargets();

      if (!targets.length) {
        message('There are no active living combatants available as targets.');
        return;
      }

      const row = document.createElement('div');
      row.className = 'battle-action-row';

      row.innerHTML = `
        <label>
          Target
          <select data-action-target required>
            ${targets.map(target => `
              <option value="${esc(target.id)}">
                ${esc(target.monster_type && target.ally ? `${target.name} - Ally` : (!target.monster_type) ? `${target.name} - Character` : `${target.name} - Monster`)}
              </option>
            `).join('')}
          </select>
        </label>

        <label>
          Action
          <select data-action-kind required>
            <option value="damage">Damage</option>
            <option value="heal">Heal</option>
            <option value="buff">Buff</option>
            <option value="debuff">Debuff</option>
          </select>
        </label>

        <label class="amount-field">
          Amount
          <input data-action-amount type="number" min="1" max="99999" value="1">
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

        if (!battleActionRows.children.length) {
          addBattleActionRow();
        }
      });

      battleActionRows.appendChild(row);
      updateActionRowAmount(row);
    }

    function openBattleActions(actorId) {
      const actor = [...latest.monsters, ...latest.characters]
        .find(combatant => combatant.id === actorId);

      if (!actor || !actor.active || !actor.alive || !actor.in_turn) {
        message('Only the current active combatant can perform battle actions.');
        return;
      }

      battleActionActorId = actorId;
      document.querySelector('#battleActionTitle').textContent =
        `Battle actions: ${actor.name}`;

      battleActionRows.innerHTML = '';
      addBattleActionRow();
      battleActionModal.hidden = false;
    }

    document.querySelector('#addBattleActionTarget').onclick = () => {
      addBattleActionRow();
    };

    document.querySelector('#cancelBattleActions').onclick = closeBattleActions;

    battleActionModal.addEventListener('click', event => {
      if (event.target === battleActionModal) {
        closeBattleActions();
      }
    });

    battleActionForm.onsubmit = async event => {
      event.preventDefault();

      if (!battleActionActorId) {
        return;
      }

      const rows = [...battleActionRows.querySelectorAll('.battle-action-row')];

      const actions = rows.map(row => {
        const action = row.querySelector('[data-action-kind]').value;
        const rawAmount = row.querySelector('[data-action-amount]').value;

        return {
          target_id: row.querySelector('[data-action-target]').value,
          action,
          amount: actionAmountRequired(action) ? Number(rawAmount) : null,
        };
      });

      const applyButton = battleActionForm.querySelector('button[type="submit"]');
      applyButton.disabled = true;

      try {
        const result = await request('/api/battle/actions', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            actor_id: battleActionActorId,
            actions,
          }),
        });

        closeBattleActions();
        await load();
        message(`Applied ${result.applied} battle action${result.applied === 1 ? '' : 's'}.`);
      } catch (error) {
        message(error.message);
      } finally {
        applyButton.disabled = false;
      }
    };

    document.addEventListener('click', async event => {
      const button = event.target.closest('button');

      if (!button) {
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
        patch('monsters', id, {active: !button.classList.contains('on')});
        return;
      }

      if (button.dataset.mally) {
        patch('monsters', id, {ally: !button.classList.contains('on')});
        return;
      }

      if (button.dataset.mv) {
        patch('monsters', id, {visible: !button.classList.contains('on')});
        return;
      }

      if (button.dataset.mt) {
        patch('monsters', id, {in_turn: !button.classList.contains('on')});
        return;
      }

      if (button.dataset.r) {
        request(`/api/combatants/${id}/reset`, {method: 'POST'})
          .then(load)
          .catch(error => message(error.message));
        return;
      }

      if (button.dataset.t) {
        patch('monsters', id, {
          [button.dataset.f]: !button.textContent.endsWith('on'),
        });
        return;
      }

      if (button.dataset.d) {
        const value = +prompt('Damage to remove:', '1');

        if (Number.isFinite(value)) {
          patch('monsters', id, {hp_delta: -Math.abs(value)});
        }

        return;
      }

      if (button.dataset.h) {
        const value = +prompt('Healing to add:', '1');

        if (Number.isFinite(value)) {
          patch('monsters', id, {hp_delta: Math.abs(value)});
        }

        return;
      }

      if (button.dataset.ca) {
        patch('characters', id, {active: !button.classList.contains('on')});
        return;
      }

      if (button.dataset.cl) {
        patch('characters', id, {alive: !button.classList.contains('on')});
        return;
      }

      if (button.dataset.cv) {
        patch('characters', id, {visible: !button.classList.contains('on')});
        return;
      }

      if (button.dataset.ct) {
        patch('characters', id, {in_turn: !button.classList.contains('on')});
        return;
      }

      if (button.dataset.cd) {
        const value = +prompt('Damage to remove:', '1');

        if (Number.isFinite(value)) {
          patch('characters', id, {hp_delta: -Math.abs(value)});
        }

        return;
      }

      if (button.dataset.ch) {
        const value = +prompt('Healing to add:', '1');

        if (Number.isFinite(value)) {
          patch('characters', id, {hp_delta: Math.abs(value)});
        }

        return;
      }

      if (button.dataset.cr) {
        request(`/api/combatants/${id}/reset`, {method: 'POST'})
          .then(load)
          .catch(error => message(error.message));
      }
    });

    document.addEventListener('change', event => {
      const input = event.target;

      if (input.dataset.mi && input.value !== '') {
        patch('monsters', input.dataset.mi, {initiative: +input.value});
      }

      if (input.dataset.ci && input.value !== '') {
        patch('characters', input.dataset.ci, {initiative: +input.value});
      }

      if (input.dataset.chp && input.value !== '') {
        patch('characters', input.dataset.chp, {hp: +input.value});
      }

      if (input.dataset.cmaxhp && input.value !== '') {
        patch('characters', input.dataset.cmaxhp, {max_hp: +input.value});
      }
    });

    function living() {
      return all().filter(combatant => combatant.active && combatant.alive);
    }

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
      const ties = tiedBuckets();

      return ties.map((bucket, bucketIndex) => `
        <div class="tie-title">Initiative ${bucket.initiative}</div>
        ${bucket.members.map((member, memberIndex) => `
          <label class="tie">
            ${esc(member.name)}
            <select data-tie-bucket="${bucketIndex}" data-tie-member="${member.id}">
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
          body: JSON.stringify({order}),
        });

        await load();
      } catch (error) {
        message(error.message);
      }
    }

    document.querySelector('#startBattle').onclick = () => {
      const order = normalOrder();

      if (!order.length) {
        message('Activate at least one living combatant first');
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

    load();
    setups();
  </script>
</body>
</html>'''
