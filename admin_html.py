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

        <p
          id="campaignNotification"
          class="pane-notification-campaign"
          role="status"
          aria-live="polite"
        > </p>

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
        <div class="row">
          <label class="field">
          <div class="row">
            <button id="openCharacterCsvImport" class="import">
              Import characters CSV
            </button>
          </div>
        </div>
      </div>
    </section>

    <section id="characterInputPane" class="pane pane-campaign-group">
      <div class="row">
        <h2>Add character to active campaign</h2>
      </div>

      <p
        id="characterAddNotification"
        class="pane-notification-campaign"
        role="status"
        aria-live="polite"
      > </p>

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
              <span class="color-picker-control"><input
                id="characterColor"
                name="color"
                type="color"
                value="#1f4e79"
              >
              <span
                id="characterColorPreview"
                class="turn-marker color-picker-preview"
                style="background-color: #1f4e79"
                aria-hidden="true"
              ></span>
            </span>
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

        <p
          id="battleSetupNotification"
          class="pane-notification-battleSetup"
          role="status"
          aria-live="polite"
        > </p>

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
              <span class="color-picker-control">
                <input
                  id="backgroundColor"
                  type="color"
                  value="#080b14"
                  title="Background color"
                >
                <span
                  id="backgroundColorPreview"
                  class="turn-marker color-picker-preview"
                  style="background-color: #080b14"
                  aria-hidden="true"
                ></span>
              </span>
            </span>
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

      <p
          id="monsterAddNotification"
          class="pane-notification-battleSetup"
          role="status"
          aria-live="polite"
        > </p>

      <div>

        <p id="monsterHpRangeHelp" class="field-help">
          In the HP Range Start and HP Range end fields:
          <ul>
            <li>enter a fixed HP value in the start field and leave the end field empty, or</li>
            <li>enter a numeric HP range from which a random HP value will be chosen (start and end fields inclusive), or</li>
            <li>enter a dice expression in the start field, such as <code>3d8+9</code>, and leave the end field empty.</br> 
              The dice expression can be a simple roll such as <code>2d6</code> or dice notation such as <code>3d8+9</code>.</br>
              Spaces around <code>+</code> or <code>-</code> are optional.</li>
          </ul>
          If no image is provided, an attempt is made to find an image on D&D Beyond based on the monster species (against Monster Name on D&D Beyond).
        </p>

        <label class="monster-species-lookup-option">
          <input
            id="monsterSpeciesLookupOverwrite"
            type="checkbox"
          >
          <span>
            Overwrite Armor Class and HP Range with found D&amp;D Beyond values
          </span>
        </label>

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
              Monster species <span class="required-marker" aria-hidden="true">*</span>
            </span>
            <input
              id="monsterSpecies"
              name="monster_species"
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
              HP Range start <span class="required-marker" aria-hidden="true">*</span>
            </span>
            <input
              id="monsterHpRangeStart"
              name="hprangestart"
              class="hp-range-input"
              type="text"
              inputmode="text"
              placeholder="15 or 3d8+9"
              required
              aria-describedby="monsterHpRangeHelp"
            >
          </label>

          <label class="field field-compact">
            <span class="field-label">HP Range end</span>
            <input
              id="monsterHpRangeEnd"
              name="hprangeend"
              class="hp-range-input"
              type="number"
              min="0"
              placeholder="Optional"
              aria-describedby="monsterHpRangeHelp"
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
            <span class="color-picker-control">
              <input
                id="monsterColor"
                name="color"
                type="color"
                value="#842029"
              >
              <span
                id="monsterColorPreview"
                class="turn-marker color-picker-preview"
                style="background-color: #842029"
                aria-hidden="true"
              ></span>
            </span>
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

        <div class="row monster-file-help-row">
          <p>Or import a JSON <code>.monster</code> file:</p>

          <button
            id="openMonsterFileHelp"
            class="help-button"
            type="button"
            aria-haspopup="dialog"
            aria-controls="monsterFileHelpModal"
            title="Help with .monster files"
          >
            ?
            <span class="sr-only">Help with .monster files</span>
          </button>
        </div>

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
            <span class="color-picker-control">
              <input
                id="monsterFileColor"
                name="color"
                type="color"
                value="#842029"
              >
              <span
                id="monsterFileColorPreview"
                class="turn-marker color-picker-preview"
                style="background-color: #842029"
                aria-hidden="true"
              ></span>
            </span>
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
      <div class="row display-pane-heading">      
        <h2>Characters</h2>

        <label class="bulk-control" for="characterBulkAction">
          <span class="bulk-label">Bulk</span>
          <select id="characterBulkAction" class="bulk-action-select">
            <option value="">Choose action…</option>
            <option value="select-all">Select all</option>
            <option value="unselect-all">Unselect all</option>
            <option value="join-battle">Join Battle</option>
            <option value="leave-battle">Leave Battle</option>
            <option value="reset">Reset</option>
            <option value="remove">Remove</option>
          </select>
        </label>
      </div>

      <div id="characters"></div>
    </section>

    <section id="monsterDisplayPane" class="pane">
      <div class="row display-pane-heading">
        <h2>Monsters</h2>
        <button id="rollMonsterInitiative" class="roll">Roll monster initiatives (d20)</button>

        <label class="bulk-control" for="monsterBulkAction">
          <span class="bulk-label">Bulk</span>
          <select id="monsterBulkAction" class="bulk-action-select">
            <option value="">Choose action…</option>
            <option value="select-all">Select all</option>
            <option value="unselect-all">Unselect all</option>
            <option value="join-battle">Join Battle</option>
            <option value="leave-battle">Leave Battle</option>
            <option value="set-ally">Set Ally</option>
            <option value="unset-ally">Unset Ally</option>
            <option value="show-ac">Show AC</option>
            <option value="hide-ac">Hide AC</option>
            <option value="show-hp">Show HP</option>
            <option value="hide-hp">Hide HP</option>
            <option value="show-initiative">Show Initiative</option>
            <option value="hide-initiative">Hide Initiative</option>
            <option value="reset">Reset</option>
            <option value="remove">Remove</option>
          </select>
        </label>
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

  <div
    id="monsterFileHelpModal"
    class="modal"
    role="dialog"
    aria-modal="true"
    aria-labelledby="monsterFileHelpTitle"
    hidden
  >
    <div class="monster-file-help-modal">
      <div class="modal-title-row">
        <h2 id="monsterFileHelpTitle">Importing .monster files</h2>

        <button
          id="closeMonsterFileHelp"
          class="modal-close"
          type="button"
          aria-label="Close .monster file help"
          title="Close"
        >
          ×
        </button>
      </div>

      <p>
        A <code>.monster</code> file is a JSON monster-export file. A good place to create a <code>.monster</code> file is at
        <a href="https://tetra-cube.com/dnd/dnd-statblock.html" target="_blank">Tetra-cube D&D 5e Statblock Generator</a>.
        Save or download the monster data as a file with the <code>.monster</code>
        extension, then select it using the <strong>Monster file</strong>
        chooser and click <strong>Import .monster</strong>.
      </p>

      <h3>Fields used from the file</h3>

      <table class="help-table">
        <thead>
          <tr>
            <th>Imported value</th>
            <th>Accepted JSON field</th>
            <th>Notes</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Monster name</td>
            <td><code>name</code></td>
            <td>Required.</td>
          </tr>
          <tr>
            <td>Monster type</td>
            <td><code>type</code></td>
            <td>Required.</td>
          </tr>
          <tr>
            <td>Hit points</td>
            <td><code>hpText</code>, then <code>hp</code></td>
            <td>The first integer in the value is used.</td>
          </tr>
          <tr>
            <td>Armor Class</td>
            <td>
              <code>ac</code>, <code>armorClass</code>,
              <code>otherArmorDesc</code>, then <code>natArmorBonus</code>
            </td>
            <td>The first available value containing a number is used.</td>
          </tr>
        </tbody>
      </table>

      <h3>Example supported file</h3>

      <pre class="monster-file-example">{
    "name": "Goblin",
    "type": "humanoid",
    "ac": 15,
    "hp": 7
  }</pre>

      <p>
        The import form controls the number of copies, display color, and an
        optional replacement image. Other JSON fields in the file are not used
        by this importer.
      </p>

      <div class="actions">
        <button id="closeMonsterFileHelpBottom" type="button">
          Close help
        </button>
      </div>
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
