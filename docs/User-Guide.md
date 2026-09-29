# Scrying Glass User Guide

Scrying Glass lets a game master prepare and run an encounter from the **Admin** screen while players watch a separate, live **Client Display**. The Client Display receives encounter changes through a WebSocket connection.

For installation and configuration, see the repository [README](../README.md). For architecture and API details, see [Technical Documentation](Technical-Documentation.md).

## Start and sign in

Start the application with a configuration file:

```bash
python3.14 scrying_glass_server.py --config config.yaml
```

| Screen | Address | Login role |
|---|---|---|
| Admin | `http://SERVER:3000/` | `admin` |
| Client Display | `http://SERVER:4000/display` | `client` or `admin` |

Replace `SERVER` with the server hostname or IP address. For local testing, use `localhost`.

Admin and Client Display logins use separate session cookies, so both pages can remain open in different tabs or windows of the same browser.

## Admin panes

The Admin page is organized into panes. The top controls can show or hide the setup pane (Campaign and Battle setups), add-monster, add-character, Monster list, and Character list panes.

When a battle starts, or when you load a setup with a battle order, hideable panes automatically collapse once. If you manually reopen a pane during that battle, it remains open until you hide it or the battle ends. **Reset All** restores the normal visible-pane layout.

| Pane | Purpose |
|---|---|
| Battle | Shows Active/Inactive status, battle controls, and battle order |
| Campaign | Select, switch, create, edit, and delete campaigns; add setups to a campaign |
| Battle setups | New, Save, Load, Rename, Delete, setup import, and CSV imports, per-setup View screen background controls |
| Add monster | Manual monster entry and `.monster` import |
| Add character | Manual character entry |
| Monsters | Monster controls, d20 initiative roll, and bulk controls |
| Characters | Character controls |
| Activity log | View, export, and clear recorded actions |

## Campaigns

A campaign groups related battle setups, for example all encounters of one adventure. Every battle setup belongs to exactly one campaign, and exactly one campaign is **active** at a time. The active campaign's name and description are shown next to the **Campaign** heading.

Save, Load, Rename, and Delete in the Battle setups row always work on the active campaign. The working encounter (the battle on screen) is not stored per campaign; it is replaced when a campaign is activated, as described below.

### The Default campaign

At startup, and whenever the Admin page refreshes the campaign list, Scrying Glass checks for battle setups that are not connected to a campaign. These are setups saved by a version before campaigns existed. If any are found:

1. A campaign named **Default** is created, if it does not exist yet.
2. The unconnected setups are moved into **Default**. If a name is already taken, the moved setup gets a `-2`, `-3`, … suffix.
3. The Admin page shows a message listing the moved setups.

A fresh installation also starts with a **Default** campaign.

### Switch campaign

Select a campaign in the **Campaign** dropdown. The switch happens immediately after you confirm; the **Switch** button does the same for the selected campaign.

When a campaign becomes active, one of its battle setups is opened automatically and replaces the working encounter:

1. The campaign's **most recently worked on** setup, which is the setup last saved, loaded, or opened in that campaign.
2. If none is recorded, the setup file that was changed most recently.
3. If the campaign has no setups, nothing is loaded and the working encounter stays.

Because the working encounter is replaced, the confirmation warns that unsaved changes are lost. Save first if you want to keep them. If you cancel, the dropdown returns to the active campaign.

### New campaign

Click **New campaign**, enter a name and an optional description, and click **Create**. Campaign names are normalized for storage in the same way as setup names. Two campaigns cannot share a normalized name.

A new campaign automatically contains an empty battle setup called **default**. The new campaign becomes active, and its empty **default** setup is opened.

### Edit campaign

Click **Edit campaign** to change the name or description of the active campaign. Its battle setups stay with the campaign, and the working encounter is not changed.

### Delete campaign

Click **Delete campaign**. In the dialog:

1. Choose the **Campaign to delete**. The first campaign that is not active is preselected; the active campaign is marked **(active)** and can be chosen explicitly.
2. If that campaign contains battle setups, choose what happens to them:
   - **Move them to another campaign**, then choose the target campaign. The campaign being deleted is never offered as a target.
   - **Delete them**. The setups are permanently deleted.
3. Click **Delete** and confirm. The confirmation lists what happens to the setups.

Deleting a campaign that is not active does not change the working encounter. Deleting the active campaign makes another campaign active and opens its most recently worked on setup. The last remaining campaign cannot be deleted.

### Add setup to campaign

Click **Add setup to campaign** to copy or move a saved battle setup from one campaign into another:

| Field | Meaning |
|---|---|
| From campaign | Campaign that currently holds the setup |
| Saved setup | Setup to add |
| To campaign | Campaign that receives the setup |
| Mode | **Move** removes it from the source campaign; **Copy** keeps it in both |

If the name already exists in the target campaign, the added setup gets a `-2`, `-3`, … suffix.

A copied setup remains a complete snapshot, including its saved View screen background. Moving a setup preserves that background as well.

## Battle setups

All actions in this section work on setups of the **active** campaign.

### New

Click **New** and confirm to discard the working encounter. Existing named setups remain unchanged.

### Save

Enter a setup name and click **Save**. The setup is saved in the active campaign. Names are normalized for storage; for example, `Throne Room — Lytharia` is stored under a slug similar to `throne-room-lytharia`.

Saving the same normalized name in the same campaign overwrites that saved setup. Setups in different campaigns may share a name.

### Load

Select a setup in the dropdown and confirm. The setup loads as soon as you select it; the **Load** button does the same and can be used to reload the selected setup. If you cancel, the dropdown returns to the setup that is currently loaded.

Loading replaces the complete working state: monsters, characters, HP, battle order, activity log, and the View screen background.

### Rename

Select a setup and click **Rename**, then enter the new name. The rename is refused if the new normalized name already exists in the active campaign. Renaming does not change the working encounter.

### Delete

Select a setup, click **Delete**, and confirm. The setup file is permanently removed, and the next setup in alphabetical order is opened; after the last setup, the first one is opened. If you delete the only setup in the campaign, an empty **default** setup is created and opened.

Opening the next setup replaces the working encounter, so save unsaved changes first.

### Import from setup

The import buttons (**Import from setup**, **Import monsters CSV**, **Import characters CSV**) are on their own row below the setup controls.

**Import from setup** appends copies of monsters, characters, or both from another setup without replacing the current encounter. Choose the **Campaign** first; it defaults to the active campaign, so you can also import combatants from a setup in another campaign.

Imported entries:

| Property | Monsters | Characters |
|---|---|---|
| ID | New unique ID | New unique ID |
| Current HP | Retained from source setup | Retained from source setup |
| Max HP | Retained from source setup | Retained from source setup |
| Initiative | Restored to original initiative | Restored to original initiative |
| Active | Off | Off |
| Visible | Off | Off |
| In turn | Off | Off |
| Alive | Derived from retained current HP | Derived from retained current HP |
| Monster AC/HP/Init display flags | Off | Not applicable |
| Current battle order | Unchanged | Unchanged |

The source setup is not changed.

### View screen background

The **View screen background** controls belong to the working battle setup. Use them to select a background color, enter a CSS background value such as a gradient, or upload a PNG, JPG/JPEG, GIF, or WebP image.

| Control | Result |
|---|---|
| Color | Selects a plain background color |
| Background value | Accepts a CSS color, gradient, or image value |
| Background image | Uploads an image and makes it the current setup's background |
| Apply background | Sends the chosen value to the Client Display immediately |
| Use color | Removes the current image selection from the working setup and uses the selected color |

The Client Display updates immediately when you apply a background. Click **Save** to store it in the named battle setup. The background is loaded with the rest of that setup whenever you load it, switch to a campaign that opens it, or copy the setup to another campaign.

A new setup starts with the configured default background. Setups saved by versions before per-setup backgrounds use the configuration default until you save them; saving adds the setup-specific background without changing their existing combatants or battle state.

Background images are stored in the configured `storage_dir/uploads/` directory. They are not deleted automatically when a setup changes background or is deleted, because another saved setup may still reference the same upload.

## Add and import combatants

### Add monster manually

| Field | Meaning |
|---|---|
| Name | Display name |
| Monster type | Creature type or description |
| AC | Armor Class |
| HP | Initial current, maximum, and reset HP |
| Quantity | Number of independent copies, from 1 to 50 |
| Color | Card outline, initiative-token color, and the color marker in the Admin Monster list |
| Image | Optional PNG, JPG, JPEG, GIF, or WebP image |

Each copy receives a unique ID and independent runtime values. Uploaded images take precedence over remote lookup.

### Import `.monster`

Scrying Glass imports compatible JSON `.monster` files. A recommended tool for creating or editing these files is the [Tetra-cube D&D 5e Statblock Generator](https://tetra-cube.com/dnd/dnd-statblock.html).

1. Open the Tetra-cube generator.
2. Create or edit the monster statblock.
3. Save or export the compatible `.monster` JSON file.
4. In Scrying Glass, choose the file in the Add monster pane.
5. Optionally select quantity, color, and an image.
6. Click **Import .monster**.

Scrying Glass reads the monster name, type, Armor Class, and Hit Points from the imported file. A manually selected image takes precedence over the optional D&D Beyond image lookup.

> The Tetra-cube generator is an external website and is not affiliated with Scrying Glass. Its availability and file-export behavior are controlled by that site.

### Add character

Characters require a name, color, and HP. Initiative is optional. New characters begin inactive, alive, hidden from the initiative bar, and out of turn.

### Import monster CSV

Use **Import monsters CSV**. Required fields are:

```text
name,mosnter_species,ac,hp
```

`type` may be used instead of `mosnter_species`.

Example:

```csv
id,name,mosnter_species,ac,hp,max_hp,initiative,color,ally,show_ac,show_hp,show_initiative
,Ice Guard,humanoid,16,45,45,14,#842029,false,true,true,true
ice-mage-1,Ice Mage,humanoid,13,52,52,17,#4c1d95,false,true,true,true
```

Optional fields include `id`, `max_hp`, `original_hp`, `color`, `image_url`, `active`, `alive`, `visible`, `ally`, `initiative`, `original_initiative`, `show_ac`, `show_hp`, and `show_initiative`.

### Import character CSV

Use **Import characters CSV**. The only required field is:

```text
name
```

Example:

```csv
id,name,hp,max_hp,initiative,color,active,visible
,Aelwyn,34,34,16,#1f4e79,false,false
brom-1,Brom,48,48,11,#0f766e,false,false
```

Optional fields include `id`, `hp`, `max_hp`, `original_hp`, `initiative`, `original_initiative`, `color`, `active`, `alive`, and `visible`.

For either CSV type, a provided non-empty ID is retained. If the `id` field is absent or blank, Scrying Glass generates a unique ID. Duplicate IDs in the CSV or conflicts with the active encounter are rejected. Boolean values accept `true`/`false`, `yes`/`no`, `on`/`off`, or `1`/`0`.

## Color markers

In the Monsters and Characters panes, each name has a small colored dot in front of it. It shows the color chosen for that combatant and uses the same style as the current-turn marker in the battle order line. Hover over the dot to see the color code. The marker updates as soon as you change the color with **Edit**.

## Monster controls

| Control | Result |
|---|---|
| Edit | Edit name, type, AC, current/max/reset HP, color, initiative, Ally, and image |
| Active / Off | Enables/disables active battle eligibility and Client card visibility |
| Ally | Sets ally classification; ally monsters display as `Name - Ally` |
| Visible | Shows/hides the monster in the initiative bar |
| Turn | Sets the monster as current turn when active and alive |
| AC / HP / Init | Shows/hides each stat on the Client monster card |
| Reset | Restores reset HP, reset initiative, and default runtime state |
| Remove | Permanently removes the monster from the current encounter after confirmation |
| Damage / Heal | Prompts for HP change and writes an activity-log entry |

A monster at zero or lower HP is dead, leaves the Client stage, becomes visible in the initiative bar, and cannot receive the turn.

### Bulk controls

The Monster pane provides **Active all**, **Ally all**, **AC all**, **HP all**, and **Init all**.

A control enables its property for all monsters when any monster does not have it enabled. When every monster already has it enabled, it disables the property for all monsters. **Active all** activates living monsters only and inserts newly activated monsters into an active battle order according to initiative.

### Monster display order in Admin

The Admin Monster table is presentation-sorted as follows:

1. Active monsters first.
2. When a battle is active, active monsters in the battle order’s exact sequence.
3. Outside a battle, active monsters by Max HP descending.
4. Inactive monsters with numeric initiative first, highest initiative first.
5. Inactive monsters with no initiative after that, with Max HP as the secondary order.
6. Name as the final tie-breaker.

This does not modify the actual server monster list or stored battle order.

## Character controls

| Control | Result |
|---|---|
| Edit | Edit name, color, HP, max HP, and initiative |
| Current HP / Max HP | Inline edits; a Max HP update becomes the reset baseline |
| Initiative | Inline initiative edit |
| Active / Off | Enables/disables battle eligibility |
| Alive / Dead | Changes life state |
| Visible | Shows/hides the character in the initiative bar |
| Turn | Sets current turn when active and alive |
| Reset | Restores current HP, initiative, and default runtime state |
| Remove | Permanently removes the character from the current encounter after confirmation |
| Damage / Heal | Prompts for HP change and writes an activity-log entry |

Removing any combatant removes its ID from the current battle order. Saved setups are not affected until you explicitly save the edited working encounter.

## Run a battle

### Prepare and start

1. Add/load combatants and set initiatives.
2. Mark participating living combatants **Active**.
3. Click **Start battle**.
4. Resolve ties when prompted.

Active living combatants are ordered by descending numeric initiative. Combatants with no initiative are placed after numeric initiatives. Within an equal numeric initiative group, the tie dialog requires a unique order for every member.

### Activate during battle

Activating a living inactive combatant after battle start inserts it into the existing order:

- Before lower numeric initiatives.
- After existing combatants with equal initiative.
- Before initiative-less combatants when it has a numeric initiative.
- After numeric initiatives when it has no initiative.

The current turn does not change.

### Advance and reset

**Next** advances cyclically to the next active living combatant. Dead and inactive entries are skipped.

**Reset All** resets all combatants, clears `battle_order`, changes the status marker to **Inactive**, and restores panes that were automatically hidden at battle start.

## Current-turn actions

The current combatant in the Battle order is underlined and marked. Click that entry to open the action popup.

Every row contains:

- A target selector containing active living monsters and characters.
- An action selector: Damage, Heal, Buff, or Debuff.
- An amount field required for Damage and Heal.

Click **Add target** to add more action rows. Click **Apply** to validate every row and apply them together:

- Damage subtracts HP.
- Heal adds HP.
- Buff and Debuff do not alter HP and do not record an amount.
- Every row is added to the Activity Log.

The popup closes after successful application.

## Activity log

The Activity Log contains timestamp, active combatant, active state, target, target state after the action, action, and amount.

Actions are `damage`, `heal`, `buff`, or `debuff`. The amount is blank for Buff/Debuff. Direct HP changes outside a current turn are recorded with `System` as the acting combatant.

Use **Export CSV**, **Export JSON**, or **Clear log**. Clearing is permanent after confirmation.

## Client Display

Active living monsters appear as cards in an adaptive grid. Characters appear in the initiative bar but do not render as full monster cards.

Monster cards show name and type by default. AC, HP, and initiative appear only when the corresponding Monster controls are enabled. Ally monsters use the display name `Name - Ally`. Text is placed on a solid contrast-aware panel for readability over images.

The initiative bar uses:

| State | Border |
|---|---|
| Current turn | Red |
| Dead | Black |
| Other visible combatant | White |

The initiative bar automatically hides when empty, giving the monster stage the full browser viewport.

Each battle setup has its own Client Display background. In the Admin **View screen background** controls, choose a color, enter a CSS gradient/value, or upload an image. Apply the background for an immediate Client Display update, then save the setup to retain it. Image backgrounds are centered, do not repeat, and cover the viewport.

## Backups and troubleshooting

Back up the whole configured `storage_dir`, including `campaigns.json`, `setups/` (one folder per campaign), and `uploads/`. Setup files store per-setup background choices and may reference uploaded background images.

| Issue | What to check |
|---|---|
| Old Admin/Client page after an update | Hard-refresh: `Ctrl+Shift+R` on Linux/Windows or `Cmd+Shift+R` on macOS |
| Client Display does not update | Confirm port 4000 is reachable; refresh to reconnect the WebSocket |
| Sign-in failure | Use the correct role and port; log in again after a server restart |
| CSV import error | Verify UTF-8 encoding, header row, required fields, valid numbers, and unique IDs |
| Missing remote image | D&D Beyond lookup is best effort; upload an image manually |
| Saved setups missing after an update | Setups saved before campaigns existed were moved into the **Default** campaign; switch to it |
| Working encounter changed unexpectedly | Switching, creating, or deleting the active campaign, and deleting a setup, open another setup; save before doing so |
| Cannot delete a campaign | The last remaining campaign cannot be deleted; if it has setups, choose to move or delete them |
