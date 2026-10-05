# Scrying Glass User Guide

Scrying Glass lets a game master prepare and run encounters from the private **Admin** screen while players view a separate live **Client Display**.

For installation and configuration, see the [README](../README.md). For internals and API details, see the [Technical Documentation](Technical-Documentation.md).

## Start and sign in

```bash
python3.14 scrying_glass_server.py --config config.yaml
```

| Screen | Address | Login role |
|---|---|---|
| Admin | `http://SERVER:3000/` | `admin` |
| Client Display | `http://SERVER:4000/` or `http://SERVER:4000/display` | `client` or `admin` |

Admin and Client Display use separate session cookies, so both screens can remain open in one browser.

## Campaigns and setups

A campaign owns its character roster and groups its battle setups. One campaign is active at a time.

- A new campaign receives an empty `default` setup.
- Activating a campaign opens its recorded last-used setup where possible.
- Existing pre-campaign setup files are migrated into the Default campaign.
- **New** creates and immediately saves an empty named setup.
- **Load** replaces the working encounter with the chosen setup.
- **Save** explicitly saves the complete working setup under the entered name.
- **Import from setup** adds reset runtime copies of monsters without replacing the current encounter.

### Automatic saving

You do not need to click Save after ordinary combatant changes:

- Adding, editing, damaging, healing, resetting, bulk-updating, or removing a **Character** automatically saves that character roster to the active campaign.
- Adding, editing, damaging, healing, resetting, bulk-updating, or removing a **Monster** automatically saves the currently loaded battle setup.
- Battle actions, battle start/end, and turn advancement save the affected campaign and setup data as needed.

If the encounter is intentionally unsaved—shown as no saved battle setup loaded—monster changes remain in the working encounter until you use **Save**. Switching campaign or loading another setup can replace unsaved work, so save it first when it matters.

## Add monster manually

The Add monster pane accepts a local display name and a canonical **Monster species**.

| Field | Meaning |
|---|---|
| Name | Name displayed in this encounter, such as `Mimic 1` |
| Monster species | Canonical D&D Beyond creature name/type, such as `Mimic` |
| AC | Armor Class |
| HP Range start | Fixed HP, numeric range start, or dice expression |
| HP Range end | Numeric range end; leave blank for fixed HP or dice notation |
| Quantity | 1 through 50 independent copies |
| Color | Monster card outline, initiative token, and Admin color marker |
| Image | Optional PNG, JPG/JPEG, GIF, or WebP upload |

### HP modes

| HP Range start | HP Range end | Result |
|---|---|---|
| `17` | blank | Each copy starts with 17 HP |
| `10` | `20` | Each copy independently receives 10 through 20 HP |
| `3d8+9` | blank | Each copy independently rolls 3d8 and adds 9 |

Numeric ranges include both endpoints. Each monster gets its own result, including when you create many copies at once. The result becomes its current HP, maximum HP, and reset HP.

### Dice notation

Use:

```text
<count>d<sides>[+|-<modifier>]
```

Spaces around `+` or `-` are optional. These are identical:

```text
3d8+9
3d8 +9
3d8+ 9
3d8 + 9
```

Common supported dice include `d4`, `d6`, `d8`, `d10`, `d12`, `d20`, and `d100`.

Examples:

```text
1d8
2d10+4
3d20 + 5
1d100-10
```

Rules:

- Dice count must be positive.
- Dice must have at least two sides.
- Dice notation requires an empty HP Range end field.
- HP Range end must not be lower than a numeric HP Range start.
- Invalid expressions are rejected before the request where possible, and always by the server.

### Images

An uploaded image takes precedence over automatic lookup. If no image is uploaded, Scrying Glass may look up a D&D Beyond image using **Monster species**. Enter the canonical creature name for this feature; custom encounter names belong in **Name**.

The lookup is best effort. It prefers an exact D&D Beyond result marked Legacy when one is available, otherwise it tries an exact current result. If there is no usable dedicated monster image, the monster is still created normally without one.

After successful creation, the monster list updates immediately and the Add monster pane shows a short confirmation.

### Edit a monster

Click **Edit** in a Monster row to change name, species, AC, color, HP values, initiative, ally state, or image.

- The current monster image appears at the top of the dialog as a thumbnail no larger than 300px wide or high.
- Select a file in **Replace image** to preview it immediately in the dialog.
- The selected replacement exists only in the browser until **Save monster** is clicked.
- **Cancel** leaves the saved image unchanged.

## Import monsters and characters

### `.monster` files

Scrying Glass accepts compatible UTF-8 JSON `.monster` files. It reads:

| Imported value | JSON field search order |
|---|---|
| Name | `name` |
| Monster species | `type` |
| HP | `hpText`, then `hp` |
| AC | `ac`, `armorClass`, `otherArmorDesc`, then `natArmorBonus` |

Quantity, color, and an optional replacement image are chosen in the import form. Use the **?** button beside the importer for in-page format help.

### CSV files

Monster CSV files require:

```text
name,monster_species,ac,hp
```

Character CSV files require:

```text
name
```

`type` may be used instead of `monster_species` in Monster CSV imports. CSV files must be UTF-8 and include a header row.

## Monster and character controls

Each row provides Edit, battle participation, turn, reset, removal, and HP controls. Monster rows also provide ally status and Client card AC/HP/initiative visibility controls.

Use the checkboxes and **Bulk** menu to apply actions to selected rows. Monster and Character selections are independent and remain browser-local.

A combatant at zero or lower HP is dead and cannot take the turn. Reset restores original HP and original initiative values.

## Run a battle

1. Add or load combatants and set initiative.
2. Mark living participants **Join Battle**.
3. Click **Start battle** and resolve ties if prompted.
4. Use **Next** to advance among active living combatants.
5. Click the underlined current combatant in the battle order to open the action dialog.

Damage and Heal require an amount; Buff and Debuff do not. Actions are validated together before they are applied and are recorded in the activity log.

## Client Display

Active living monsters render as cards. Characters appear in the initiative bar. Monster cards show name and species, plus AC, HP, or initiative only when enabled by the Admin.

Each setup can have a separate display background. In **Battle setups**, choose a color, enter a CSS value such as a gradient, or upload an image. Apply it for immediate display; automatic monster persistence does not replace the need to save an intentionally unsaved setup.

## Troubleshooting

| Problem | Check |
|---|---|
| Old Admin behavior after an update | Restart if required and hard-refresh with `Ctrl+Shift+R` on Linux/Windows or `Cmd+Shift+R` on macOS |
| Add monster does not update immediately | Confirm the current `admin.js` is deployed; successful creation should be followed by a state reload and pane notification |
| Dice expression rejected | Check the syntax, use at least `d2`, and leave HP Range end empty |
| No remote monster image | Use canonical Monster species spelling; lookup is optional, so upload an image if needed |
| Changed monster disappears after switching setup | Confirm you were working in a loaded saved setup; save an unsaved encounter before switching |
| Character change appears lost after campaign switch | Confirm the intended campaign was active before the change |
| CSV import fails | Check UTF-8 encoding, required headers, numeric fields, and unique IDs |

## Backups

Back up the complete `storage_dir`, including `campaigns.json`, `characters/`, `setups/`, `state.json`, and `uploads/`. Uploaded files may be referenced by saved setup backgrounds and monster records.
