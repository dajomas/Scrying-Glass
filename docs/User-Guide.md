> Account storage update: users now live in SQLite (schema v4). The new `superadmin` role manages users; existing `security.users` is a one-time migration input only. See [User management](User-Management.md) for upgrade instructions. This supersedes older configuration-account instructions below.

# Scrying Glass User Guide

The game master prepares and runs combat in the Admin interface. Players watch
a separate Client Display that receives live updates. The code split changes
file organization, not the intended encounter workflow.

See [README](../README.md) for installation and configuration,
[Technical Documentation](Technical-Documentation.md) for internals, and
[Systemd Deployment](Systemd-Deployment.md) for a managed Linux service.

## Start and sign in

Use your existing shell launcher if it activates the virtual environment, or
run from the repository root:

```bash
.venv/bin/python scrying_glass_server.py --config config.yaml
```

| Screen | Default address | Account role |
|---|---|---|
| Admin | http://SERVER:3000/ | admin |
| Client Display | http://SERVER:4000/display | client or admin |

Replace SERVER with the host/IP. Separate cookies allow both interfaces in one
browser. Restart clears sessions; sign in again afterward.

## Admin panes

Top controls show/hide campaign input, character input, battle setup input,
monster input, character display and monster display. Battle controls and the
activity log provide turn management and recorded actions. Pane visibility is
presentation state, not combatant activation or deletion.

## Campaigns

A campaign owns a character roster and groups related battle setups. There is
one active campaign and one shared working encounter. Save before switching if
you need to retain encounter changes that may be replaced.

Selecting/activating a campaign opens its last-worked-on setup if still present,
otherwise its newest setup by modification time. A campaign with no setups has
no setup to open. New campaigns receive an empty default setup. Fresh installs
start with Default; older unassigned setups are imported there, with numeric
suffixes on naming collisions.

Create/edit campaigns using their name and optional description. Normalized
names must be unique. To delete a campaign with setups, explicitly choose to
move its setups elsewhere or permanently delete them. The last campaign cannot
be deleted. Deleting the active campaign selects another one and can replace
the working encounter. Campaign deletion also removes that campaign's roster;
moving its setups is not a character-roster merge.

Add setup to campaign offers move or copy from another campaign. Colliding
setup names receive numeric suffixes. The copied/moved setup retains its saved
background and monster data; characters come from the target campaign's roster.

## Campaign characters

Add characters to the active campaign with name, color, HP and optional
initiative. Edit their HP, maximum HP, initiative and runtime flags from the
character controls. Max HP provides the character reset baseline.

Characters are stored separately from battle setups. A new setup retains the
active campaign's roster. Loading a setup uses that campaign's current roster,
not an old character copy from its snapshot. Character CSV imports append to
the active campaign. Removing a character updates the campaign roster; it is
not merely a removal from one setup.

## Battle setups

| Action | Result |
|---|---|
| New | Clears the working monster encounter/order/log and retains the active campaign's characters |
| Save | Writes the named monster/setup snapshot and saves the campaign roster separately |
| Load | Replaces encounter data with the saved setup and current campaign roster |
| Rename | Renames a saved setup; conflicts are rejected |
| Delete | Permanently deletes it and opens the next alphabetic setup, wrapping to the first |
| Import from setup | Appends new copies of monsters from a selected saved setup |

Battle setup names are normalized into lowercase storage names; saving the same name in the
same campaign overwrites it. Different campaigns can use the same setup name.
When deletion leaves no setups, an empty default setup is created and opened.
Loading/deleting can replace the working battle, log and background: save first.

Monster changes to an associated active setup are persisted through relevant
mutation handlers. Character changes persist to the campaign roster. Do not
assume every change remains isolated from saved data until pressing Save.
Use Save to explicitly name/associate the encounter and retain its background.

### Import from setup

Choose source campaign/setup. Only monsters are imported; campaign characters
are not imported from battle setups. Copies get new IDs, retain source current
HP and max HP, restore original initiative, and clear active/visible/turn and
stat-display flags. Alive derives from retained HP. The current battle order
and source setup are not changed by the import itself.

### View background

Use the setup controls to choose a color, CSS background/gradient, or an uploaded
PNG/JPG/JPEG/GIF/WebP image. Apply for immediate display feedback; save the setup
to store that choice with it. New/legacy setups use the configured fallback
until they carry a saved background. Uploaded background files are retained
because other setups may reference them. Images are centered and cover the
player display without tiling.

## Add monsters

Manual entry uses name, monster species, AC, HP Range Start, optional HP Range
End, color, quantity (1..50) and optional image. Species identifies the creature
for optional D&D Beyond suggestions; the display name can distinguish copies.

| HP input | Start | End |
|---|---|---|
| Fixed HP | 24 | Empty |
| Inclusive random range | 18 | 30 |
| Dice expression | 3d8+9 | Empty |

Each generated monster receives an independent ID and HP roll. Dice can include
a positive or negative modifier; spaces around the modifier are accepted.
Invalid/oversized expressions are rejected. Uploaded images take precedence
over remote lookup. D&D Beyond lookup is optional and best effort: enter stats
and upload an image manually if it fails.

### .monster files

Upload compatible UTF-8 JSON .monster files with usable name, type, armor class
and hit points. Choose quantity/color and an optional image. The external
[Tetra-cube statblock generator](https://tetra-cube.com/dnd/dnd-statblock.html)
can produce compatible files; it is not bundled or required at runtime.

## CSV imports

Use the monster/character CSV import dialogs. CSV must be UTF-8 (BOM accepted),
include headers and contain at least one nonblank row. Headers are trimmed and
case-insensitive. IDs are generated when absent/blank; duplicates or IDs already
used by any combatant in the encounter are rejected.

Monster example:

```csv
name,monster_species,ac,hp,max_hp,initiative,color
Goblin,goblin,15,7,7,14,#842029
Goblin captain,goblin,16,21,21,17,#4c1d95
```

Required monster columns are name, monster_species (or type), ac and hp.
Use monster_species in new CSVs; do not rely on the old monster_type header.
Optional columns include id, original_hp, image_url, ally, runtime flags,
original_initiative and show_ac/show_hp/show_initiative.

Character example:

```csv
name,hp,max_hp,initiative,color
Aelwyn,34,34,16,#1f4e79
Brom,48,48,11,#0f766e
```

Character name is required; other fields have defaults. Boolean fields accept
true/false, yes/no, y/n, on/off or 1/0. Correct invalid rows and retry; keep a
backup of important rosters before bulk changes.

## Combatant controls

| Control | Meaning |
|---|---|
| Active / Off | Participation in battle eligibility; active living monsters can appear as cards |
| Visible | Presence in the initiative bar, distinct from Active |
| Turn | Current turn; requires an active living combatant |
| Edit | Update identity, stats and applicable display/image fields |
| Damage / Heal | Change HP and write an activity-log record |
| Reset | Restore HP/initiative baselines and clear runtime flags |
| Remove | Permanently remove the combatant and its battle-order ID |

Monster-only controls include Ally and AC/HP/Init card visibility. Ally affects
the rendered label, not the stored name. Color markers match the combatant color.
Monsters at zero/lower HP become dead, visible in the initiative bar and out of
turn. Character controls additionally allow manual Alive/Dead status.

Bulk controls operate on selected IDs. Monster bulk actions include joining or
leaving battle, ally flags, stat visibility, reset and remove. Character bulk
actions include joining/leaving battle, reset and remove. Check selection and
confirmation prompts before destructive actions. Bulk and individual activation
may update battle order differently; review the order after bulk changes.

## Run a battle

1. Add/load monsters and verify the active campaign roster.
2. Set initiative and activate living participants.
3. Click Start battle and resolve tied initiatives as prompted.
4. Use Next to advance through active living combatants.
5. Use End to clear turns/order, or Reset All to reset combatants and order.

Individual activation during an existing battle can insert a combatant according
to initiative: before lower initiatives and after existing equals. Combatants
without numeric initiative follow numeric entries. Next skips dead/inactive
entries and adds eligible participants omitted from order. With none eligible,
order and turn state clear. End does not perform the full combatant reset.

## Current-turn actions

Click the marked/underlined current combatant to open battle actions. Add one or
more target rows. Actor and targets must be active and alive, and the actor must
currently have the turn.

- Damage subtracts HP; a positive amount is required.
- Heal adds HP; a positive amount is required.
- Buff and Debuff log an action without changing HP or supplying an amount.

All rows are validated before changes are applied. Every applied row is logged.
Buff/debuff records are descriptive log entries, not an automatic conditions
or duration engine.

## Activity log and display

The log records UTC timestamp, actor, actor life state, target, target life state,
action and amount. Direct HP changes without a current actor use System.
Export CSV/JSON before clearing; clearing permanently removes current records.

The Client Display shows active living monster cards and visible combatants in
an initiative bar. Characters participate in the bar, not full monster cards.
Monster AC/HP/initiative values appear when enabled. Ally labels append - Ally.
The bar hides when empty. Backgrounds follow the working encounter.

Treat Client login as access to encounter state, not a secure redaction of all
hidden card values. Use only trusted players/devices.

## Updates, backups and troubleshooting

The split Admin HTML loads fragments once when the server imports the loader.
Restart for markup changes; hard-refresh after browser asset changes. Players
and GMs do not need to know the internal file layout to use the interface.

Back up the whole configured storage_dir, including scrying-glass.sqlite3 and uploads/,
plus configuration, with the process stopped. Database values and list entries now use
relational columns/records. Campaign rename preserves its ID and relationships. Legacy
JSON files remain archival. See [migration instructions](SQLite-Migration.md).

| Symptom | What to check |
|---|---|
| Missing uvicorn during a terminal check | Activate the environment or use .venv/bin/python |
| Missing HTML fragment at startup | Complete templates/admin tree and correct loader path |
| Old page | Restart after HTML changes and hard-refresh |
| Client does not update | Port/access and WebSocket reconnection by refreshing |
| Login fails after restart | Sessions cleared; sign in again with the correct role |
| CSV rejected | Headers, UTF-8, numbers, boolean values and unique IDs |
| No suggested stats/image | Remote lookup is best effort; enter/upload manually |
| Older setups missing | Check Default and migration logs |
| Characters differ between setups | Campaign roster is authoritative; characters are not snapshot-owned |
| Encounter unexpectedly replaced | Campaign activation or setup load/delete can open another setup |
| Last campaign cannot be deleted | Create/retain another campaign; choose setup move/delete policy |

Keep credentials/configuration separate from source and limit reachability to a
trusted network. Coordinate multiple Admin users: there is no conflict/version
resolution for simultaneous changes.
