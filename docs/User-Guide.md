# Scrying Glass User Guide

Scrying Glass lets a game master prepare and run an encounter from the private **Admin** screen while players view a separate, live **Client Display**. The Client Display receives updates through a WebSocket connection.

For installation and configuration, see the [README](../README.md). For architecture, persistence, and route information, see the [Technical Documentation](Technical-Documentation.md).

## Start and sign in

Start the application with a configuration file:

```bash
python3.14 scrying_glass_server.py --config config.yaml
```

| Screen | Address | Login role |
|---|---|---|
| Admin | `http://SERVER:3000/` | `admin` |
| Client Display | `http://SERVER:4000/` or `http://SERVER:4000/display` | `client` or `admin` |

Replace `SERVER` with the server hostname or IP address. For local testing, use `localhost`.

Opening `http://SERVER:4000/` redirects to the Client login page when no valid Client session exists. After a successful Client login, the same root address redirects to the Client Display.

Admin and Client Display logins use separate session cookies, so both screens can remain open in different tabs or windows in the same browser.

## Admin panes

The Admin page is divided into panes. Top-level display controls show or hide the setup, add-monster, add-character, Monster-list, and Character-list panes.

When a battle starts, or when you load a setup that already has a battle order, hideable panes collapse once automatically. A pane reopened manually during that battle remains open until you hide it or the battle ends. **Reset All** restores the normal visible-pane layout.

| Pane | Purpose |
|---|---|
| Battle | Shows battle status, battle controls, and battle order |
| Campaign Setup | Selects, creates, edits, activates, and deletes campaigns; moves or copies setups between campaigns |
| Battle setups | Creates, saves, loads, renames, deletes, and imports setups; imports CSV; configures the current setup background |
| Add monster | Adds monsters manually or imports a `.monster` file |
| Add character | Adds characters manually |
| Monsters | Lists Monsters, rolls initiative, and provides row selection plus Monster bulk actions |
| Characters | Lists Characters and provides row selection plus Character bulk actions |
| Activity log | Displays, exports, and clears logged actions |

### Pane notifications

The **Add character**, **Add monster**, **Campaign Setup**, and **Battle setups** panes display action feedback locally.

- Notifications appear in the pane where the action started.
- A notification disappears automatically after 15 seconds.
- A new notification in the same pane replaces the prior timer.
- Notifications are not stored in battle setups and are not shown on the Client Display.

## Campaigns

A campaign groups related battle setups. Every setup belongs to exactly one campaign, and exactly one campaign is active at a time. The active campaign name and description appear beside the Campaign Setup heading.

Save, Load, Rename, and Delete actions in the Battle setups pane work in the active campaign. The working encounter is replaced when a campaign is activated or a setup is loaded.

### Default campaign

At startup, and while listing campaigns or setups, Scrying Glass checks for setup files from the pre-campaign storage layout. If it finds setup JSON files directly inside `setups/`:

1. It creates a **Default** campaign if needed.
2. It moves the unassigned setups to `setups/default/`.
3. It adds `-2`, `-3`, and later suffixes if a filename would conflict.
4. It reports moved setups in the Admin response and startup log.

A fresh installation also begins with a Default campaign.

### Switch campaign

Select a campaign in the Campaign dropdown. The selection activates after confirmation; the **Switch** button performs the same operation.

When a campaign becomes active, Scrying Glass opens one of its battle setups and replaces the working encounter:

1. The campaign's recorded most recently worked-on setup.
2. If that setup does not exist, the most recently modified setup file.
3. If the campaign has no setup files, no setup is opened and the working encounter remains as it was.

Because switching can replace unsaved working changes, save first when necessary. Cancelling returns the dropdown to the currently active campaign.

### New campaign

Click **New campaign**, enter a name and optional description, then click **Create**. Names are normalized for storage, so two campaigns cannot share the same normalized name.

A new campaign receives an empty `default` setup. It becomes active and that empty setup opens automatically.

### Edit campaign

Use **Edit campaign** to change the active campaign's name or description. Its setups remain with it and the current working encounter does not change.

### Delete campaign

Use **Delete campaign** and choose the campaign that should be deleted. If it contains setups, choose either:

- **Move setups** to another campaign.
- **Delete setups** permanently.

The campaign being deleted is never offered as the move target. The final remaining campaign cannot be deleted. Deleting the active campaign activates another campaign and opens its preferred setup.

### Add setup to campaign

Use **Add setup to campaign** to move or copy a saved setup between campaigns.

| Field | Meaning |
|---|---|
| From campaign | Campaign currently holding the setup |
| Saved setup | Setup to move or copy |
| To campaign | Destination campaign |
| Mode | **Move** removes the source copy; **Copy** keeps the source copy |

If the destination already has that name, Scrying Glass adds a `-2`, `-3`, or later suffix. A copied or moved setup retains its complete snapshot, including the saved Client Display background.

## Battle setups

All setup actions operate in the active campaign unless a dialog explicitly lets you choose another campaign.

### New

Enter a unique name in **Battle setup name**, then click **New**.

After confirmation, Scrying Glass:

1. Discards the current working encounter.
2. Creates a new empty working setup.
3. Immediately saves that empty setup under the entered name in the active campaign.
4. Selects and loads the newly saved setup.

The New action uses the existing blank-setup and save workflow: it first creates the empty working state, then saves it using the supplied name.

The name is normalized for storage. A setup with the same normalized name cannot be created in the active campaign. Existing named setups remain unchanged.

### Save

Enter a setup name and click **Save**. Save writes the complete working state under that name in the active campaign.

Saving the same normalized name in the same campaign overwrites that saved setup. Setups in different campaigns may share a name.

Setup names are normalized for storage. For example:

```text
Throne Room — Lytharia
```

becomes a safe slug similar to:

```text
throne-room-lytharia
```

### Load

Load replaces the complete working state, including combatants, HP, battle order, activity log, and display background.

Select a setup from the dropdown and confirm. Selecting a setup can load it immediately; **Load** can also reload the selected setup.

### Rename and Delete

- **Rename** changes a saved setup name when the resulting normalized name is not already used in the active campaign. Renaming does not load or modify the working encounter.
- **Delete** permanently removes a selected saved setup. Scrying Glass opens the next setup alphabetically, wrapping to the first. If the deleted setup was the only one, Scrying Glass creates and opens an empty `default` setup.

Deleting a setup can replace the working encounter. Save first if you need to preserve unsaved changes.

### Import from setup

**Import from setup** appends copies of Monsters from a saved setup without replacing the current encounter. Select a source campaign first; it defaults to the active campaign, but can be another campaign.

| Property | Imported Monsters |
|---|---|
| ID | New unique ID |
| Current HP | Preserved |
| Maximum HP | Preserved |
| Initiative | Restored from original initiative |
| Active | Off |
| Visible | Off |
| In turn | Off |
| Alive | Calculated from current HP |
| Monster AC/HP/Init display flags | Off |
| Current battle order | Unchanged |

The source setup is not modified.

### View screen background

The **View screen background** controls belong to the working setup. Choose a color, supply a CSS background value such as a gradient, or upload a PNG, JPG/JPEG, GIF, or WebP image.

| Control | Result |
|---|---|
| Color | Chooses a plain background color |
| Background value | Accepts a CSS color, gradient, or image value |
| Background image | Uploads an image and uses it as the working setup background |
| Apply background | Updates the Client Display immediately |
| Use color | Stops using the current image and uses the selected color |

Apply changes for immediate display output, then click **Save** to retain them in a named setup. Background image files remain in `storage_dir/uploads/`; they are not automatically deleted because another setup may reference the same upload.

## Add and import combatants

### Add monster manually

| Field | Meaning |
|---|---|
| Name | Base display name |
| Monster species | Creature type or description |
| AC | Armor Class |
| HP Range start | Lowest possible initial HP |
| HP Range end | Highest possible initial HP; it may not be lower than HP Range start |
| Quantity | Number of independent copies, from 1 to 50 |
| Color | Client card outline, initiative token, and Admin color marker |
| Image | Optional PNG, JPG, JPEG, GIF, or WebP image |

Every copy gets a unique ID and independent state.

For every created Monster, Scrying Glass assigns a random integer HP value between **HP Range start** and **HP Range end**, including both values.

- If start is `7` and end is `7`, every created Monster receives 7 HP.
- If start is `7` and end is `12`, every created Monster independently receives a value from 7 through 12.
- The assigned HP initializes current HP, maximum HP, and reset HP.
- A range start higher than range end is rejected.

When Quantity is greater than one, copies receive a numeric suffix in creation order:

```text
Goblin - 1
Goblin - 2
Goblin - 3
```

A quantity of one keeps the entered name unchanged.

A manually uploaded image takes precedence over remote image lookup.

### Import `.monster`

Scrying Glass imports compatible JSON `.monster` files. The [Tetra-cube D&D 5e Statblock Generator](https://tetra-cube.com/dnd/dnd-statblock.html) is a convenient external authoring tool.

1. Create or edit a statblock in the external generator.
2. Export a compatible `.monster` JSON file.
3. Choose the file in the Add monster pane.
4. Optionally choose quantity, color, and an image.
5. Click **Import .monster**.

Use the **?** button beside the `.monster` import area to open the in-page help popup. It explains how to obtain a compatible file and which fields are used.

Scrying Glass imports these values:

| Imported value | JSON field search order |
|---|---|
| Name | `name` |
| Monster species | `type` |
| HP | `hpText`, then `hp` |
| AC | `ac`, `armorClass`, `otherArmorDesc`, then `natArmorBonus` |

The first usable number in an accepted HP or AC field is used. Name, species/type, HP, and AC must all be usable for the import to succeed.

The import form supplies quantity, color, and an optional replacement image. Other fields in the JSON file are not used by the importer.

When Quantity is greater than one, imported copies receive numbered names in creation order. A quantity of one retains the imported name unchanged.

The external generator is not affiliated with or controlled by Scrying Glass.

### Add character

Characters require a name, color, and HP. Initiative is optional. New Characters begin inactive, alive, hidden from the initiative bar, and out of turn.

### CSV imports

Monster CSV files require:

```text
name,monster_species,ac,hp
```

`type` may be used instead of `monster_species`.

Character CSV files require:

```text
name
```

Both imports accept UTF-8 CSV with a header row. A non-empty supplied `id` is retained; a blank or absent ID is generated. Duplicate IDs in the CSV or IDs already used by the working encounter are rejected. Booleans accept `true`/`false`, `yes`/`no`, `on`/`off`, and `1`/`0`.

Example Monster CSV:

```csv
id,name,monster_species,ac,hp,max_hp,initiative,color,ally,show_ac,show_hp,show_initiative
,Ice Guard,humanoid,16,45,45,14,#842029,false,true,true,true
ice-mage-1,Ice Mage,humanoid,13,52,52,17,#4c1d95,false,true,true,true
```

Example Character CSV:

```csv
id,name,hp,max_hp,initiative,color,active,visible
,Aelwyn,34,34,16,#1f4e79,false,false
brom-1,Brom,48,48,11,#0f766e,false,false
```

## Combatant controls

A small colored dot appears before every Monster and Character name. It corresponds to the combatant color and matches the current-turn marker style. Hover over it to see the color code.

### Individual controls

| Control | Monsters | Characters |
|---|---|---|
| Edit | Name, species, AC, HP values, color, initiative, ally state, and image | Name, color, HP values, and initiative |
| Active / Off | Enables or disables battle eligibility and Monster card visibility | Enables or disables battle eligibility |
| Visible | Shows/hides initiative-bar token | Shows/hides initiative-bar token |
| Turn | Makes an active, living combatant current turn | Makes an active, living combatant current turn |
| Reset | Restores reset HP, reset initiative, and default runtime state | Restores reset HP, reset initiative, and default runtime state |
| Remove | Permanently removes the combatant after confirmation | Permanently removes the combatant after confirmation |
| Damage / Heal | Changes HP and records an activity-log entry | Changes HP and records an activity-log entry |
| Other | Ally; AC, HP, and Init card-field visibility | Alive / Dead; inline HP, Max HP, and initiative edits |

A combatant at zero or lower HP is dead. Dead combatants cannot receive the turn. Dead Monsters leave the Client card stage and remain represented in the initiative bar when visible.

### Selected Monster actions

Each Monster row has a checkbox. The **Bulk** menu affects only selected Monsters.

| Action | Result |
|---|---|
| Select all | Selects all Monsters in the current encounter |
| Unselect all | Clears the Monster selection |
| Join Battle | Activates selected living Monsters and inserts them into an active battle order by initiative |
| Leave Battle | Deactivates selected Monsters and removes them from battle participation |
| Ally / Not ally | Sets or clears ally classification |
| Show/Hide AC | Shows or hides Armor Class on selected Monster cards |
| Show/Hide HP | Shows or hides HP on selected Monster cards |
| Show/Hide Init | Shows or hides initiative on selected Monster cards |
| Reset | Restores selected Monsters to reset values and default runtime state |
| Remove | Permanently removes all selected Monsters after one confirmation |

Selections remain after successful state-changing actions while the selected Monsters still exist. Select all and Unselect all deliberately replace the selection. Removal is only saved into a named setup after you save the working encounter.

### Selected Character actions

Each Character row has a checkbox. Character selection is independent from Monster selection.

| Action | Result |
|---|---|
| Select all | Selects all Characters in the current encounter |
| Unselect all | Clears the Character selection |
| Join Battle | Activates selected living Characters and inserts them into an active battle order by initiative |
| Leave Battle | Deactivates selected Characters and removes them from battle participation |
| Reset | Restores selected Characters to reset values and default runtime state |
| Remove | Permanently removes all selected Characters after one confirmation |

Removed combatants are removed from the battle order and disappear from browser selection after state refresh. Browser selections are local to the Admin page and are neither saved in a setup nor sent to the Client Display.

### Monster display order

The Monster list has a presentation-only sort order:

1. Active Monsters first.
2. During battle, active Monsters in exact battle-order sequence.
3. Outside battle, active Monsters by maximum HP descending.
4. Inactive Monsters with numeric initiative, highest first.
5. Remaining inactive Monsters by maximum HP.
6. Name as final tie-breaker.

This does not alter stored Monster order or the actual battle order.

## Run a battle

### Prepare and start

1. Add or load combatants and set initiative.
2. Mark participating living combatants Active, individually or through bulk actions.
3. Click **Start battle**.
4. Resolve initiative ties when prompted.

Active living combatants are ordered by descending numeric initiative. Combatants without initiative are placed after numeric initiatives. A tie dialog requires a unique ordering for members of the same numeric initiative group.

### Activate during battle

Activating a living inactive combatant after a battle has started inserts it into the existing battle order:

- Before lower numeric initiatives.
- After existing combatants with equal initiative.
- Before initiative-less entries when the combatant has a numeric initiative.
- After numeric initiatives when the combatant has no initiative.

The current turn does not change.

### Advance and reset

**Next** advances cyclically to the next active living combatant. Dead and inactive entries are skipped.

**Reset All** resets every combatant, clears `battle_order`, changes status to Inactive, and restores panes automatically hidden at battle start.

## Current-turn actions

The current combatant is underlined and marked in Battle order. Click it to open the action popup.

Each action row contains a target selector, an action selector, and an amount field for Damage or Heal. Add additional rows with **Add target**, then select **Apply** to validate and apply them together.

- Damage subtracts HP.
- Heal adds HP.
- Buff and Debuff do not alter HP and do not record an amount.
- Each action writes an Activity Log entry.

The popup closes after successful application.

## Activity log

The Activity Log contains timestamp, acting combatant, actor state, target, target state after action, action, and amount.

Actions are `damage`, `heal`, `buff`, and `debuff`. Buff and Debuff have no amount. Direct HP changes outside a current turn are logged with `System` as actor.

Use **Export CSV**, **Export JSON**, or **Clear log**. Clearing is permanent after confirmation.

## Client Display

Active living Monsters render as cards in an adaptive grid. Characters appear in the initiative bar but do not receive full Monster cards.

Monster cards always show name and species. AC, HP, and initiative appear only when enabled. Ally Monsters display as `Name - Ally` without changing the stored name. Card text uses an opaque contrast-aware panel for readability over images.

| Initiative state | Border |
|---|---|
| Current turn | Red |
| Dead | Black |
| Other visible combatant | White |

The initiative bar hides automatically when empty, giving the Monster stage the full viewport. Each setup has an independent background; image backgrounds are centered, do not repeat, and cover the viewport.

## Backups and troubleshooting

Back up the configured `storage_dir`, including `campaigns.json`, all campaign setup folders, and `uploads/`.

| Issue | What to check |
|---|---|
| Old Admin or Client behavior after an update | Restart the service and hard-refresh with `Ctrl+Shift+R` on Linux/Windows or `Cmd+Shift+R` on macOS |
| Client root returns `Not Found` | Confirm the deployed server includes the Client `GET /` redirect route and restart the service |
| Client Display does not update | Confirm port 4000 is reachable and refresh the display to reconnect its WebSocket |
| Sign-in fails | Use the correct role and port; server restarts remove in-memory sessions |
| Manual monster creation fails | Check that HP Range start is not greater than HP Range end and that the deployed UI/server agree on `monster_species`, `hp_range_start`, and `hp_range_end` |
| `.monster` import fails | Confirm the filename ends in `.monster` and that usable name, type, AC, and HP fields are present |
| CSV import fails | Check UTF-8 encoding, a header row, required fields, valid numbers, and ID uniqueness |
| Remote image lookup fails | D&D Beyond lookup is best effort; upload an image directly |
| Saved setups seem missing | Switch to the Default campaign; pre-campaign setups are migrated there |
| Working encounter changed unexpectedly | Switching campaigns, loading/deleting setups, creating campaigns, or deleting the active campaign can open another setup; save first |
| Bulk action rejects an ID | Refresh the Admin page; browser selection may include a combatant removed by another action or Admin session |
| Bulk action affected the wrong group | Monster and Character selections are independent; check the selected rows in the relevant pane |
| Cannot delete a campaign | The final campaign cannot be deleted; choose whether its setups should move or be deleted |