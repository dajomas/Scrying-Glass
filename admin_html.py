ADMIN_HTML = r'''<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Scrying Glass Admin</title>
  <link rel="stylesheet" href="/static/admin.css">
</head>
<body>
  <main>
    <h1>Scrying Glass — Admin</h1>
    <p id="message" class="message"></p>

    <section>
      <div class="row">
        <button
          id="toggleCampaignPane"
          class="pane-toggle"
          type="button"
          aria-controls="campaignInputPane"
          aria-expanded="true"
        >
          Hide campaign input
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
          id="toggleBattleSetupPane"
          class="pane-toggle"
          type="button"
          aria-controls="battleSetupInputPane"
          aria-expanded="true"
        >
          Hide battle setup input
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
          id="toggleCharacterDisplayPane"
          class="pane-toggle"
          type="button"
          aria-controls="characterDisplayPane"
          aria-expanded="true"
        >
          Hide character display
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
        <button id="endBattle" class="danger">End battle</button>
        <button id="resetAll" class="reset">Reset All</button>
      </div>
      <div class="row">&nbsp;</div>
      <div class="row">
        <span id="battleInfo"></span>
      </div>
    </section>

    <section id="campaignInputPane" class="pane pane-campaign-group">
      <div>
        <div class="row">
          <h2>Campaign Setup</h2>
          <span id="activeCampaignInfo" class="campaign-info"></span>
        </div>

        <div class="row">
          <label class="field">
            <span class="field-label">Active campaign</span>
            <select
              id="campaignSelect"
              class="campaign-select"
            ></select>
          </label>
          <label class="field"><span class="field-label">&nbsp;</span><button id="switchCampaign">Switch</button></label>
          <label class="field"><span class="field-label">&nbsp;</span><button id="newCampaign">New campaign</button></label>
          <label class="field"><span class="field-label">&nbsp;</span><button id="editCampaign">Edit campaign</button></label>
          <label class="field"><span class="field-label">&nbsp;</span><button id="deleteCampaign" class="danger">Delete campaign</button></label>
          <label class="field"><span class="field-label">&nbsp;</span><button id="openCampaignSetup" class="import">
            Add setup to campaign
          </button>
        </div>
      </div>
    </section>

    <section id="characterInputPane" class="pane pane-campaign-group">
      <div class="row">
        <h2>Add character to active campaign</h2>
      </div>

      <div>
        <form id="characterForm" class="row">
          <label class="field">
            <span class="field-label">
              Character name <span class="required-marker" aria-hidden="true">*</span>
            </span>
            <input
              id="characterName"
              name="name"
              placeholder="For example: Aelwyn"
              required
            >
          </label>

          <label class="field field-color">
            <span class="field-label">Color</span>
            <input
              id="characterColor"
              name="color"
              type="color"
              value="#1f4e79"
            >
          </label>

          <label class="field field-compact">
            <span class="field-label">
              Starting HP <span class="required-marker" aria-hidden="true">*</span>
            </span>
            <input
              id="characterHp"
              name="hp"
              type="number"
              min="0"
              value="1"
              required
            >
          </label>

          <label class="field field-compact">
            <span class="field-label">Initiative</span>
            <input
              id="characterInitiative"
              name="initiative"
              type="number"
              placeholder="Optional"
            >
          </label>

          <label class="field"><span class="field-label">&nbsp;</span><button>Add character</button></label>
        </form>
        <div class="row">
          <button id="openCharacterCsvImport" class="import">
            Import characters CSV
          </button>
        </div>

      </div>
    </section>

    <section id="battleSetupInputPane" class="pane pane-battle-group">
      <div>
        <div class="row">
          <h2>Manage active campaign Battle setups</h2>
          <span
            id="activeBattleSetupInfo"
            class="battle-setup-info"
            aria-live="polite"
          >
            No saved battle setup loaded
          </span>
        </div>

        <label class="field field-inline">
          <span class="field-label">Battle setup name</span>
          <input
            id="setupName"
            class="setup-name"
            placeholder="For example: goblin-ambush"
          >
        </label>

        <label class="field field-inline"><span class="field-label">&nbsp;</span><button id="newSetup" class="reset">New</button></label>
        <label class="field field-inline"><span class="field-label">&nbsp;</span><button id="saveSetup">Save</button></label>

        <label class="field field-inline">
          <span class="field-label">Battle setup name</span>
          <select id="setupSelect">
            <option value="">Load saved setup…</option>
          </select>
        </label>

        <label class="field field-inline"><span class="field-label">&nbsp;</span><button id="loadSetup">Load</button></label>
        <label class="field field-inline"><span class="field-label">&nbsp;</span><button id="renameSetup">Rename</button></label>
        <label class="field field-inline"><span class="field-label">&nbsp;</span><button id="deleteSetup" class="danger">Delete</button></label>

        <div class="row">
          <button id="openImport" class="import">Import from setup</button>
          <button id="openMonsterCsvImport" class="import">
            Import monsters CSV
          </button>
        </div>

        <div class="row">
          <h3>View screen background</h3>
        </div>

        <div class="row">
          <label class="field field-color">
            <span class="field-label">Background color</span>
            <input
              id="backgroundColor"
              type="color"
              value="#080b14"
              title="Background color"
            >
          </label>

          <label class="field field-inline">
            <span class="field-label">Background value</span>
            <input
              id="backgroundValue"
              class="setup-name"
              placeholder="Color, CSS gradient, or image URL"
            >
          </label>

          <label class="field field-inline">
            <span class="field-label">Background image</span>
            <input
              id="backgroundImage"
              type="file"
              accept="image/png,image/jpeg,image/gif,image/webp"
            >
          </label>

          <label class="field"><span class="field-label">&nbsp;</span><button id="applyBackground" type="button">Apply background</button></label>
          <label class="field"><span class="field-label">&nbsp;</span><button id="clearBackgroundImage" type="button">Use color</button></label>
        </div>

        <p class="campaign-info">
          Choose a color, enter a CSS background value, or upload a background
          image. Save the battle setup to retain it.
        </p>
      </div>
    </section>

    <section id="monsterInputPane" class="pane pane-battle-group">
      <div class="row">
        <h2>Add monster to Battle setup</h2>
      </div>

      <div>
        <form id="monsterForm" class="row">
          <label class="field">
            <span class="field-label">
              Monster name <span class="required-marker" aria-hidden="true">*</span>
            </span>
            <input
              id="monsterName"
              name="name"
              placeholder="For example: Goblin"
              required
            >
          </label>

          <label class="field">
            <span class="field-label">
              Monster type <span class="required-marker" aria-hidden="true">*</span>
            </span>
            <input
              id="monsterType"
              name="monster_type"
              placeholder="For example: humanoid"
              required
            >
          </label>

          <label class="field field-compact">
            <span class="field-label">
              Armor Class <span class="required-marker" aria-hidden="true">*</span>
            </span>
            <input
              id="monsterAc"
              name="ac"
              type="number"
              min="0"
              placeholder="AC"
              required
            >
          </label>

          <label class="field field-compact">
            <span class="field-label">
              Hit points <span class="required-marker" aria-hidden="true">*</span>
            </span>
            <input
              id="monsterHp"
              name="hp"
              type="number"
              placeholder="HP"
              required
            >
          </label>

          <label class="field field-compact">
            <span class="field-label">Quantity</span>
            <input
              id="monsterQuantity"
              name="quantity"
              type="number"
              min="1"
              max="50"
              value="1"
              title="Number of monsters"
            >
          </label>

          <label class="field field-color">
            <span class="field-label">Color</span>
            <input
              id="monsterColor"
              name="color"
              type="color"
              value="#842029"
            >
          </label>

          <label class="field">
            <span class="field-label">Image</span>
            <input
              id="monsterImage"
              name="image"
              type="file"
              accept="image/*"
            >
          </label>

          <button>Add manually</button>
        </form>

        <p>Or import a JSON <code>.monster</code> file:</p>

        <form id="monsterUpload" class="row">
          <label class="field">
            <span class="field-label">
              Monster file <span class="required-marker" aria-hidden="true">*</span>
            </span>
            <input
              id="monsterFile"
              name="monster_file"
              type="file"
              accept=".monster,application/json"
              required
            >
          </label>

          <label class="field field-compact">
            <span class="field-label">Quantity</span>
            <input
              id="monsterFileQuantity"
              name="quantity"
              type="number"
              min="1"
              max="50"
              value="1"
              title="Number of monsters"
            >
          </label>

          <label class="field field-color">
            <span class="field-label">Color</span>
            <input
              id="monsterFileColor"
              name="color"
              type="color"
              value="#842029"
            >
          </label>

          <label class="field">
            <span class="field-label">Replace image</span>
            <input
              id="monsterFileImage"
              name="image"
              type="file"
              accept="image/*"
            >
          </label>

          <button>Import .monster</button>
        </form>

      </div>
    </section>

    <section id="characterDisplayPane" class="pane">
      <h2>Characters</h2>
      <div id="characters"></div>
    </section>

    <section id="monsterDisplayPane" class="pane">
      <div class="row">
        <h2>Monsters</h2>
        <button id="rollMonsterInitiative" class="roll">Roll monster initiatives (d20)</button>
      </div>
      <div class="row monster-bulk-controls" aria-label="Bulk monster controls">
        <span class="bulk-label">All monsters:</span>
        <button type="button" class="bulk-monster-toggle" data-bulk-field="active">Join battle all</button>
        <button type="button" class="bulk-monster-toggle" data-bulk-field="ally">Ally all</button>
        <button type="button" class="bulk-monster-toggle" data-bulk-field="show_ac">AC all</button>
        <button type="button" class="bulk-monster-toggle" data-bulk-field="show_hp">HP all</button>
        <button type="button" class="bulk-monster-toggle" data-bulk-field="show_initiative">Init all</button>
      </div>
      <div id="monsters"></div>
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
      <h2>Import monsters from a saved setup</h2>
      <p>
        Imported monsters receive new IDs and reset runtime state.
        Characters belong to campaigns and are not part of battle setups.
        The current battle order is not changed.
      </p>

      <form id="importForm" class="import-form">
        <label>
          Campaign
          <select id="importCampaign" name="campaign"></select>
        </label>

        <label>
          Saved setup <span class="required-marker" aria-hidden="true">*</span>
          <select id="importSetup" name="name" required></select>
        </label>

        <label>
          Import
          <select name="kind">
            <option value="monsters">Monsters only</option>
          </select>
        </label>

        <div class="actions">
          <button class="import">Import</button>
          <button type="button" id="cancelImport">Cancel</button>
        </div>
      </form>
    </div>
  </div>

  <div id="campaignModal" class="modal" hidden>
    <div>
      <h2 id="campaignModalTitle">New campaign</h2>
      <form id="campaignForm" class="import-form">
        <label>
          Name <span class="required-marker" aria-hidden="true">*</span>
          <input name="name" maxlength="100" required>
        </label>

        <label>
          Description
          <input name="description" maxlength="2000">
        </label>

        <div class="actions">
          <button id="campaignSubmit" class="import">Create</button>
          <button type="button" id="cancelCampaign">Cancel</button>
        </div>
      </form>
    </div>
  </div>

  <div id="campaignSetupModal" class="modal" hidden>
    <div>
      <h2>Add battle setup to campaign</h2>
      <p>Move or copy a saved battle setup from one campaign into another.</p>
      <form id="campaignSetupForm" class="import-form">
        <label>
          From campaign <span class="required-marker" aria-hidden="true">*</span>
          <select id="campaignSetupFrom" name="from_campaign" required></select>
        </label>

        <label>
          Saved setup <span class="required-marker" aria-hidden="true">*</span>
          <select id="campaignSetupName" name="setup" required></select>
        </label>

        <label>
          To campaign <span class="required-marker" aria-hidden="true">*</span>
          <select id="campaignSetupTo" name="to_campaign" required></select>
        </label>

        <label>
          Mode
          <select name="mode">
            <option value="move">Move</option>
            <option value="copy">Copy</option>
          </select>
        </label>

        <div class="actions">
          <button class="import">Add</button>
          <button type="button" id="cancelCampaignSetup">Cancel</button>
        </div>
      </form>
    </div>
  </div>

  <div id="campaignDeleteModal" class="modal" hidden>
    <div>
      <h2 id="campaignDeleteTitle">Delete campaign</h2>
      <p id="campaignDeleteText"></p>
      <form id="campaignDeleteForm" class="import-form">
        <label>
          Campaign to delete
          <select id="campaignDeleteTarget" name="campaign"></select>
        </label>

        <label id="campaignDeleteActionLabel">
          Its battle setups
          <select id="campaignDeleteAction" name="setup_action">
            <option value="move">Move them to another campaign</option>
            <option value="delete">Delete them</option>
          </select>
        </label>

        <label id="campaignDeleteMoveLabel">
          Move its battle setups to
          <select id="campaignDeleteMoveTo" name="move_to"></select>
        </label>

        <div class="actions">
          <button class="danger">Delete</button>
          <button type="button" id="cancelCampaignDelete">Cancel</button>
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
          CSV file <span class="required-marker" aria-hidden="true">*</span>
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

  <script src="/static/admin.js" defer></script>
</body>
</html>'''
