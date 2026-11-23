# Scrying Glass User Guide

## Character HP display and compact initiative inputs

The Characters roster shows read-only current/max HP, such as 12/20, like the
Monsters roster. To change either character HP value, choose that row's Edit,
change Current HP and/or Max HP, then Save character. Cancel makes no change.
Existing validation and HP rules still apply; a rejected save leaves the dialog
and draft available for correction. Refresh after a successful save to check the
stored values. Maximum HP affected by statistics reductions retains its existing
original/base-editor restrictions described below.

Character and monster Initiative inputs remain compact inline editors at 7.5ch.
Tab/Shift+Tab navigation within each roster is described under Participation and
initiative below; initiative values and combat ordering rules are unchanged.
Setup fields and edit modals retain their existing sizes. Restart the correct
server process and hard-refresh the Admin page after installing the matching
HTML/static update.

## Looking Glass companion styling

The preceding presentation-only restyling aligns Scrying Glass with Looking Glass
using shared dark surfaces, gold accents, local font fallbacks and coordinated
controls. It does not merge the applications or change encounter data, permissions,
combatant colours or configured player-display backgrounds. See
`Patch/Restyling-Changes.md`, `Patch/Restyling-Apply.md` and
`Patch/Restyling-Validation.md` from that package for its scope and checks.

## Starting with the launcher scripts

The launchers accept Python 3.10 or newer and require working sqlite3 support.
Use `./run.sh` on Linux, `.\run.ps1` in PowerShell, or `run.bat` on Windows after
preparing configuration as described in the README. Existing compatible environments
are reused. New environments use a compatible interpreter discovered by the launcher.

If startup says the existing environment requires Python 3.10 or newer, it has not
been automatically replaced. The launchers use `~/dnd` on Linux and
`%USERPROFILE%\dnd` on Windows. Back up any files stored there before recreating
that environment with the intended Python. Do not delete campaign or encounter
storage to fix an interpreter problem. Installing a newer Python alone does not
upgrade the interpreter inside an existing environment.

The minimum launcher version is not a statement that all application workflows
have been validated on Python 3.10. Check installation, imports and a copied
encounter after changing interpreters. For systemd deployments, follow the
[deployment guide](Systemd-Deployment.md); the service uses its own virtualenv.

## Accounts and sign-in

Admin defaults to port 3000; Client defaults to 3100; the statblock viewer to 3200 (see [Statblocks](#statblocks)). Separate cookies allow all three in one browser. Only a regular admin assigned to the active campaign can sign in to and use the statblock listener; superadmin and client accounts are refused, and its page clears when access ends. It shows each monster in battle as a tile; select a tile (or press Enter) to show its full statblock with the current name, species, AC, HP and initiative bonus, press Escape to close it, and use the arrow keys to move between tiles. References open below the statblock. Missing statblocks are loaded automatically from a monster's original lookup source when one is known. To choose a statblock yourself, open Edit monster and use Find statblock (searches the enabled sources for the species in the form) or Upload .monster file, check the preview, choose Use this statblock and save the monster. For several monsters, select them and choose Load statblocks in the Monster bulk menu: pick a statblock per monster (or Keep current), wait until the rows are ready and apply. Imported statblocks never change a monster's name, species, AC, HP or initiative bonus. Logout affects only the current interface; restart clears all sessions. Account edits invalidate that user's sessions and display sockets.

Superadmins manage accounts at /users; regular admins run battles at /. Superadmins authorize battle APIs but are redirected away from root battle HTML. Create a regular admin for interactive use.

Usernames are case-sensitive and unique, 1–64 characters, without surrounding whitespace/control characters. New/reset passwords require 8–1024 characters. Leave the UI edit password empty to preserve it. The last superadmin cannot be deleted or demoted.

## Campaign ownership and shared runtime

Each campaign has at most one regular-admin owner; an admin may own many campaigns. Admin-created/imported campaigns belong to that admin. Superadmin-created campaigns remain unassigned. Superadmins reassign them in Campaign ownership on /users. Removing an admin or changing its role clears ownership, not transfers it.

At first ownership migration, exactly one regular admin receives all existing campaigns. With zero/multiple regular admins they remain unassigned. Superadmins are excluded from this count. Migration does not repeat after later account changes.

Admins with no assignments may log in and create their own campaign. They do not see another owner's encounter. There is ONE shared active campaign: select an owned campaign and press Switch to activate it. Merely choosing the dropdown selection does not activate it. Save/checkpoint before switching; activation can replace the working encounter.

Campaigns own character rosters and group setups. Activation opens the last-used setup, otherwise the newest setup. Names are unique under case-insensitive checks; renaming preserves campaign identity.

Deleting a campaign with setups requires move/delete policy. Moving setups is not a roster merge. The last campaign cannot be deleted. Deleting the active campaign requires a permitted replacement; an admin with no other owned replacement must ask a superadmin.

## Viewer access

Select a permitted campaign, open Viewer access, verify its heading, check client-role users and save. This editor follows the SELECTED campaign, even when not globally active. With no valid selection it falls back to a permitted active/first campaign; with none it shows an assignment message.

Ownership and viewer grants are independent. Reassigning an owner retains client grants. Admins cannot edit grants on another owner's campaign.

Clients with no grants see an access message; one campaign opens automatically; multiple campaigns prompt selection. The campaign heading reopens the switcher. Selection changes the viewer URL, not the shared active campaign. The active campaign supplies live state; inactive campaigns use saved setup/roster data without reviving old turns. Revocation clears denied data on a subsequent scoped update.

## Characters and setups

Characters belong to the campaign, not setup snapshots. Add/edit name, color, HP, maximum HP and initiative. CSV imports append to the roster. Removing a character changes the roster across that campaign's setups. In the roster, HP is read-only; use Edit to change Current HP and Max HP. Initiative remains editable inline.

Track HP (on by default) can be switched off per character in Add character and in Edit, or for several characters with the Bulk actions Track HP and Do not track HP. Use it for players who keep their own HP. For an untracked character the Admin shows "Not tracked" instead of HP and asks for none; damage and healing are still recorded in the activity log, but current, maximum and temporary HP never change. Set its life state and death saves yourself in Encounter tools or with the Alive button; nothing changes automatically from HP. In Battle actions it can still be chosen for a Max HP increase or reduction and for temporary HP: these are recorded in the activity log ("HP not tracked"), and nothing changes. Encounter tools refuse temporary HP for it. The stored HP is kept, so switching Track HP back on continues from it.

| Setup action | Result |
|---|---|
| New | Clears monsters/order/log; retains campaign characters |
| Save | Saves named setup and roster separately |
| Load | Replaces encounter with saved setup plus current roster |
| Rename | Renames; conflicts rejected |
| Delete | Opens next alphabetic setup, wrapping, or creates empty default |
| Import from setup | Appends monster copies only |

Selecting a setup dropdown loads immediately without confirmation. Names normalize to lowercase and are unique per campaign; saving the same name overwrites. Relevant monster/character mutations persist through specialized handlers, so do not assume all changes wait for Save.

Import from setup supports Alive (default), Dead and All. Filtering uses stored alive: Dead can include non-standing, not explicitly dead, monsters. Copies get new IDs, retain HP/max HP, restore original initiative and clear battle/display flags. Effects get fresh IDs with imported links remapped; missing concentration sources discard linked effects, missing timed anchors become manual. Characters/lairs are not imported.

Background accepts color, CSS gradient/background or uploaded image. Apply previews; Save captures it. Uploaded backgrounds are retained because other setups may reference them.

Has lair, below setup name and above imports, exposes the lair pane/toggle subject to parent/manual visibility preferences. Unchecking does not delete, disable or remove the lair's turn. New setups default unchecked; older configured lairs default checked unless explicitly saved otherwise.

## Monster creation and imports

Manual entry supports name, species, AC, color, quantity 1–50 and optional image. HP Range Start accepts fixed 24, range start 18 with end 30, or dice 3d8+9 with empty end. Each copy rolls independently. Uploaded images take precedence over optional best-effort D&D Beyond lookup. Enter stats manually when lookup fails.

The color starts at the first of 12 palette colors that no monster in the battle setup uses yet (the least used one when all 12 are taken); characters do not count. With a quantity above 1, each copy gets the next free color; a color you pick yourself is used for every copy and stays until the form is reset. CSV rows without a color get the next free color the same way. The HP entry help is folded under "How to enter HP" at the end of Combat statistics.

.monster imports are compatible UTF-8 JSON statblocks with usable name/type/AC/HP, not arbitrary archives.

CSV must be UTF-8 (BOM allowed), contain headers and nonblank data. Headers are trimmed/case-insensitive. Monster required fields: name, monster_species (or type), ac, hp. Use monster_species rather than old monster_type. Character name is required; other fields default. HP/max HP must be nonnegative. Blank IDs are generated; duplicate/conflicting encounter IDs fail. Booleans accept true/false, yes/no, y/n, on/off, 1/0.

```csv
name,monster_species,ac,hp,max_hp,initiative,color
Goblin,goblin,15,7,7,14,#842029
```

```csv
name,hp,max_hp,initiative,color
Aelwyn,34,34,16,#1f4e79
```

## Statblocks

The statblock viewer (port 3200) is for the GM only. A regular admin assigned to the
active campaign signs in there; superadmin and client accounts are refused, and
statblocks never appear on the Client Display. Each monster in battle is a tile; select a
tile (or press Enter) to open its statblock: name and type, Armor Class, Hit Points,
Initiative and Speed, an ability table with MOD and SAVE, the property rows, then traits,
actions and the other sections (in a second column on wide screens), and the source and
credits. Name, species, AC, HP and initiative bonus are always the live tracker values.

**Sources.** Statblocks come from D&D Beyond (public pages only: paywalled monsters are
not offered), 5e.tools, Open5e, or a Tetra-cube `.monster` file. Disabled providers are
not used. A statblock whose source could not be resolved completely is marked partial and
lists what is missing; a failure names its cause.

**Add Monster.** After you choose a monster from a source in the lookup, **Show statblock**
in the Appearance group previews that source's statblock with the values in the form
(nothing is saved). When you add the monster, its statblock is collected from the same
source in the background; Import .monster uses the imported file. Without a source, or
when the source has no statblock, the monster is added without one. If a monster changed
meanwhile (species or source edited, or a different statblock chosen), **Replace
statblocks?** asks per monster: Replace, Keep current, or Decide later (the question comes
back after the next add or reload; it expires after 10 minutes).

**Edit Monster.** The Statblock section shows the current state. **Show statblock** opens the
chosen or saved statblock; **Find statblock** searches the enabled sources (the original
source first) and previews a result before you use it; **Upload .monster file** uses a file;
**Keep current statblock** discards the choice. A choice is saved with Save and expires if
not saved in time.

**Several monsters.** Select monsters in the roster and choose **Load statblocks** in the Bulk
dropdown: each row keeps its current statblock unless you pick a source result or a
`.monster` file; Apply statblocks saves the ready rows.

**5e.tools versions.** Some 5e.tools creatures have versions, such as *Battle Familiar
(Flyer)* or *Animal Lord; Forager*. Searching for the creature's name lists its versions
under it: in Edit Monster in a closed "versions of …" block below the creature, in Load
statblocks in a "Versions of …" option group. Searching for a version's own name finds that
version, labelled "version of …". A monster added from a 5e.tools link to a version uses
that version as its original source.

Magic items that 5e.tools generates, such as *+1 Longsword* or *Plate Barding*, now appear
in a statblock's item references with their rarity and text, like any other item.

Item references also show the text 5e.tools adds from the item's type and properties: for
example the Versatile or Heavy property text, a weapon's mastery (such as *Mastery: Sap*),
heavy armor's Stealth and Strength lines, a spellcasting focus's note and a tool's note. If
that text cannot be built, the item shows its own text only and the statblock is marked
partial.

**Automatic loading.** While a statblock viewer is open, monsters in battle that were
added from a source and have no statblock yet get one from that source.

Statblocks are stored with setups and the current encounter, in storage backups and in
campaign bundles. Preparation runs in a resource-limited worker: `prlimit` on Linux, a Job
Object on Windows; on other platforms it reports that it is not available.

## Participation and initiative

Active/Join Battle controls participation; Visible controls the player strip. Pane visibility is presentation only. Monsters additionally support Ally and Show AC/HP/Init. Ally changes the rendered label, not stored name.

Characters/monsters require whole-number initiative before joining. Zero/negative values are valid; unset is not. Mixed bulk joins fail atomically if anyone lacks initiative. Leave before clearing initiative, or deactivate and clear in the same API update. Lair initiative is fixed.

### Initiative keyboard navigation

Within Characters or Monsters, Tab moves to the next available initiative editor
and Shift+Tab to the previous in displayed row order, skipping other row controls.
The last editor wraps to the first, and Shift+Tab at the first wraps to the last.
The loop never jumps between the two rosters. With one editor, either key keeps
focus there. Hidden, disabled and readonly editors are skipped; empty rosters
introduce no navigation interception.

Press Escape from an initiative editor to leave the loop and focus that roster's
scroll region. Tab/Shift+Tab then follow normal page order, including other row
controls, even when you pass through another initiative editor. This normal mode
lasts until you leave and re-enter the roster or use the pointer to interact again.
Thus Escape provides an exit without immediately trapping focus back in the loop.
Other controls and modified shortcuts retain their normal keyboard behaviour.

Existing change/save validation still applies. After a same-campaign/setup refresh,
loop focus follows the destination combatant even if rows reorder, and a draft
typed there while the preceding save completes is retained without replaying an
already emitted save. Escape, moving focus elsewhere or changing campaign/setup
cancels restoration. Initiative values and combat ordering are unchanged.

Select all selects the list and Clear selection, right next to it, clears it; Unselect all in the Bulk list clears too. Select dead replaces selection: characters match explicit death/three failures, monsters also match alive=False. Selection does not mutate. Reset restores baselines/runtime flags; Remove permanently deletes.

Start battle resolves ties. Characters default ahead of monsters within ties; changing a position swaps within that group. Roll shared initiative (d20) gives selected monsters one roll, not a shared turn or running-order reorder.

Next advances eligible participants. Down/stable characters retain turns for manual death saves; dead characters and non-standing monsters do not receive future turns. A dead current participant may retain unresolved ownership until Next.

Round starts at 1, increments on wrap and clears on End, Reset All or no eligible participants. Eligible runtime turn/round survive restart; loading saved setups does not revive old turns. End does not fully reset combatants. End battle hides every monster, character and lair on the Client Display. Dead or downed creatures stay hidden too, until you show them yourself or the next battle starts; after that, a creature that drops is shown again as before.

Viewer A−/A+ changes strip text 2 px at a time, default 16, bounds 12–40. Runtime persists it; setup Save captures display settings.

## Battle actions and reactions

Click the highlighted turn owner. Ordinary actions require a standing actor and active targets. Damage/heal may target down/stable creatures; ordinary explicitly dead targets need recovery. Buff/debuff require standing targets and only log descriptions: use effects for persistent conditions.

Damage/healing amounts must be positive. Enter damage after adjudicating mitigation/critical dice. Critical hit affects failed saves at zero HP, not entered damage.

The Target and Reaction source menus show each combatant's colour dot, in the closed
menu and in every entry of the list. Use the mouse, or the arrow keys, Home, End and
Enter (Escape closes only the menu); typing a name's first letters jumps to it.

Add reaction chooses an independent active source/target. Damage/healing reactions allow down/dead sources/targets for manually adjudicated death bursts. Healing does not resurrect explicit death. Rows validate together and apply top-to-bottom, each attributed to its source.

Apply submits only pending action and reaction rows and keeps the modal open.
Successfully applied rows stay visible, show Applied, and are locked, including
Remove. Subsequent Apply clicks skip these rows; use Add target or Add reaction
for additional entries. Identical new rows are intentional new actions, not duplicates
of an applied row. With no pending rows, Apply makes no request.

Close dismisses the modal without applying pending rows or undoing applied rows.
Clicking the backdrop also closes it. While Apply is submitting or refreshing,
modal controls and backdrop closure are temporarily blocked to protect the batch.
Reopening starts a fresh draft; Applied markers are not saved across modal sessions.

Rejected batches remain editable for correction and retry. A successful submission
is marked applied before refreshing, so a refresh failure does not replay those rows.
If a connection fails before success is confirmed, check the activity log/current HP
before retrying: this browser-level protection does not provide server-side retry
idempotency or protect against duplicate requests from another tab.

Activity log Details for value changes name the affected creature, the changed
property and its resulting value, for example `Goblin - 2: HP 12 → 10/12;
temporary HP 4 → 0`, `Goblin: STR 12 → 10; source: Cleric` or `Cleric: death-save
failures now 1/3; damage at 0 HP`. HP results include the current maximum. Lair
damage keeps the action name first. Entries recorded before this change keep their
original text.


Start-of-turn damage/heal targets the current creature, damage first, ignores empty/zero fields and does not advance. Ordinary self-action eligibility applies, so down/dead actors cannot use it.

## Health and death saves

States: standing, down, stable, dead. Explicit recovery raises HP to at least 1 and clears counters. Healing can recover down/stable but not explicit death.

Temporary HP is a separate nonnegative pool: Set replaces, not stacks. Damage consumes it first unless bypass selected. Healing caps at max HP and does not replenish temporary HP. Absolute HP corrections bypass attack logic.

To grant temporary HP during a battle, choose Temporary HP (keep higher) or Temporary HP (replace) as the Action of a target row in Battle actions. As in the 5e rules temporary HP never stack: keep higher takes the new amount only when it is higher than what the target has; replace always takes it, also when it is lower. Granting is not healing, so a creature at 0 HP keeps its life state and death saves. Temporary HP last until damage uses them up, you change them in Encounter tools or you use Reset; End battle leaves them. Reactions and dead creatures cannot get them; for a character whose HP is not tracked the grant is only recorded in the activity log. The activity log shows, for example, `Goblin: Temporary HP 6 → 6 (kept higher); source: Cleric`.

For character damage events:
- Clamp HP at zero; do not accumulate negative HP.
- Excess damage at least maximum HP causes instant death.
- First drop from positive HP to zero downs without a failed save unless excess is lethal.
- Damage already at zero causes one failure, critical hit two, capped at three.
- Three failures cause death; three manual successes stabilize.
- Damage breaks stability and starts a fresh failure tally.
- Stabilization/healing above zero resets the tally.

Temporary HP does not make a zero-HP character standing or prevent failed saves from an incoming damaging hit, but can reduce excess reaching actual HP. Monsters do not accumulate death saves.

Example max HP 25/current HP 10/no temp HP: damage 34 downs; 35 causes instant death. Dice, saves, proximity-based critical inference and resurrection remain manual.

## Effects and concentration

Encounter tools > Combatant health, conditions and effects adds named effects with optional source/private notes. Private is default. Public exposes name only, not notes/source/counters.

Manual effects remain until removed. Timed effects count actual Next-driven start/end boundaries of an anchor, not rounds. End/1 expires at its next end; Start/1 at next start. Manual turn assignment does not expire effects. Inactive/skipped anchors may need manual cleanup.

Concentration-linked effects require a standing source. End concentration removes loaded linked effects. Down/dead/deleted sources reconcile links. End previous concentration before adding another linked spell. Damage provides a reminder, not an automatic concentration roll.

## Lair actions

One lair per encounter, initiative 20 after tied creatures, without HP/AC/life state/conditions. Configure name/color/private notes and participation/visibility.

On its turn open Resolve lair action, select active non-dead creatures, enter damage/conditions, adjust rows for saves/mitigation, set visibility/expiry and apply. Next advances separately.

Damage 0–99999; every target needs damage and/or conditions. Limits: 1–100 distinct targets, up to 20 new conditions each and total 100 effects. Lair damage is not critical. Expiry: manual, next lair start, target next-turn end.

Removing a lair preserves applied effects, clears source links and makes lair-anchored expiry manual. Disabling preserves anchors without advancing counters. Reset All disables/hides without deleting configuration. Reopen stale action dialogs after revision changes.

## Undo, checkpoints and campaign bundles

Undo retains up to 30 supported active-encounter operations across restart. Bulk action is one step. Health/effect/turn/recovery operations are supported; accounts/uploads/full image edits are not. Campaign/setup boundaries and unsupported structural changes clear history. Top ID/fingerprint rejects stale undo. Restore keeps later audit records and appends an event.

Checkpoints include roster, monsters, health/effects, order, round, display and audit state. Start creates Before battle. Up to 50 per campaign; oldest pruned. Preview and confirm against current revision. Restore retains the current audit trail, appends an event and is undoable. Missing referenced setups are rejected.

Campaign backups lives under Campaign Setup. Bundle export includes campaign, roster, setups, current encounter and referenced local media; external URLs remain URLs. It excludes accounts, other campaigns and accumulated recovery collections.

Import creates a NEW inactive campaign, resolves naming/media collisions and never overwrites. Switch to it and restore Imported encounter to resume runtime. Ownership is installation-local.

Bundle limits: 25 MiB compressed, 100 MiB expanded, 10 MiB manifest, 1000 members, 200 setups. Media: png/jpg/jpeg/gif/webp/avif/bmp. Invalid paths, duplicate members, unsupported content and missing referenced media fail. Treat bundles as private GM data.

## Logs, display and troubleshooting

Logs include UTC time, actor/target and life state, action, amount and Details (note). System is used when direct HP changes lack a current actor. Export before clearing. Clear removes runtime and associated saved-setup log without saving unrelated changes. CSV prefixes formula-like strings with apostrophes; JSON retains originals.

Player cards show active non-dead monsters, muted down/stable. Active visible participants appear in the strip; characters/lairs have no monster cards. Dead visible participants can remain in strip. Public effects and relative ordering are visible. Character stats, private effects, logs and setup references are omitted; monster stats follow visibility flags. Media files themselves are not session-protected.

Display reconnects in place and retains its last screen. Status means contact/revision, not proof someone saw it.

| Symptom | Check |
|---|---|
| Empty campaigns | Ownership, or create a campaign |
| Blank encounter | Select owned campaign and Switch |
| Viewer denied | Grant for exact campaign/client role |
| Cannot join | Whole-number initiative |
| Healing does not revive | Explicit dead requires recovery |
| Effect remains | Anchor eligibility/boundary semantics |
| Stale restore/action | Refresh preview/reopen dialog |
| Old UI | Restart HTML; reload browser assets |
| Missing roster | Campaign characters, not setup snapshot |

Coordinate simultaneous administrators. Back up the whole stopped installation, not just bundles.

## 5e.tools monster fallback

Optional monster suggestions now try D&D Beyond first, then 5e.tools JSON data.
AC accepts numeric entries and AC objects; HP prefers a supported dice formula
and falls back to the numeric average. Names match exactly after case and
punctuation normalization. The UI labels the provider and source. Existing
AC/HP overwrite and in-flight edit protection are unchanged.

Image lookup follows the same provider order when creating a monster without an
uploaded image. 5etools supplies a token URL (explicit `tokenUrl` or a generated
WebP token path when `hasToken` is set), not necessarily a full illustration.
Existing monsters' images are not retroactively updated. Image URLs are remote;
they are not downloaded or cached locally, and availability is not probed.

Configuration under `display`:
```yaml
fivetools_fallback: true
fivetools_sources: ["MM", "XMM"]
fivetools_data_base_url: "https://5e.tools/data/bestiary"
fivetools_image_base_url: "https://5e.tools/img"
```

MM is tried before XMM to retain the older-edition preference. Only configured
sources are searched: add source identifiers from the bestiary index to extend
coverage. D&D Beyond and 5etools are independently controlled: disable both
`dndbeyond_image_lookup` and `fivetools_fallback` to prevent optional provider
lookups. No credentials are sent to 5etools. Remote JSON is bounded to 16 MB per
file, fetched with a five-second socket timeout, and cached in-process for one
hour with at most 32 entries. Restart clears the cache. Source files are loaded
sequentially; configured source count affects cold-lookup latency.

Unresolved `_copy` entries without their own usable values are skipped for stats;
this is not a complete implementation of 5etools inheritance. Special-only AC/HP
is not guessed. Fallback uses a single usable source entry and does not combine
missing fields across providers/editions. Browser access to remote token hosts
and server HTTPS access to data endpoints are required. Use third-party data
and images only where permitted; none are bundled with this patch.

Run offline tests from the repository root:
```bash
python -m unittest discover -s tests -p 'test_fivetools_fallback.py' -v
```

Live validation: enter Crawling Claw and check that the notification identifies
5e.tools after D&D Beyond fails. Add a monster without uploading an image and
check its token in the player view. If no result appears, inspect WARNING logs
and verify index/source URL reachability from the service account. Token paths
and live endpoints could not be verified from the patch-build environment.


## Open5e monster source and provider switches

Monster lookup also searches the [Open5e API](https://open5e.com/api-docs) after
D&D Beyond and 5e.tools, across all Open5e documents. Each choice uses the same
"provider / book [/ legacy]" layout as the other providers, e.g. "Open5e / 5e 2014
Rules / legacy", with publisher and licence attribution. Within each provider the
choices are sorted by book, and each choice ends with whether a monster image is
available. Below each choice are the View source link and, when the provider supplies
it, the source details: book and page for D&D Beyond (for example "Basic Rules (2014),
pg. 148 via D&D Beyond") and 5e.tools ("XMM, page 133 via 5e.tools"), and publisher
and licence attribution for Open5e. Any provider failure still blocks all candidates.
Open5e statistics fill AC, HP range and initiative bonus by the same empty-field and
overwrite rules; most Open5e monsters have no image. When Open5e is enabled, Refresh
also uses it. The lookup message and the help text name only the enabled providers.
D&D Beyond choices show the book named on the monster page (for example "D&D Beyond /
Basic Rules (2014) / legacy") and sort by book. The overwrite checkbox is ticked by
default. When you pick from several monsters and another found monster has a different
image, a "Select monster image" dialog shows thumbnails: the selected monster's image
first, then the others with their provider and book. Click a thumbnail to use that
image, or Cancel to keep the original image (or none). An uploaded image file still
takes precedence. After a lookup with several results, "Choose again" next to Monster
species reopens the list for the same species without typing it again. The current
monster and image stay until you pick another monster; Cancel keeps them, and Cancel in
the image dialog after a new pick keeps the image you had.

Source and Monster dropdowns (SG-TODO-016): the Monster identity row has a Source list (None by default, each configured 5e.tools source and every Open5e document, labelled with its provider and source) and a Monster list with the complete list for that source. Picking a monster fills in the name when it is empty or overwrite is ticked, sets Monster species to the monster name, and fills the statistics by the usual empty-or-overwrite rules. For the image, the monster's name is searched in every enabled lookup source (D&D Beyond, 5e.tools and Open5e): when that finds other images, the "Select monster image" dialog lets you keep the picked monster's own image (or none, for example for Open5e monsters, which have no images) or take one of the others; the statistics always come from the picked monster. An uploaded image file still takes precedence. D&D Beyond is not listed (name search only), and disabled providers are not offered. If a list cannot be loaded completely, it shows that the list is unavailable; retry or type the species instead.

Configuration under `display` (defaults shown):
```yaml
open5e_lookup: true
open5e_base_url: "https://api.open5e.com/v2"
```

A superadmin can turn D&D Beyond, 5e.tools and Open5e search on or off under
Monster lookup providers on the User management page (`/users`). Saved switches
override the configuration keys for every admin until changed again. Open5e content
is published under per-document licences (OGL 1.0a, CC-BY-4.0, CC0); Open5e
illustrations are CC BY-NC 4.0. Run `python3 tools/check_open5e_live.py` for a live
contract check.

## Attack statistics reductions

In the current combatant's Battle actions window, Add statistics reduction adds an
attack row, not an Encounter tools control. Select an active living target, one of
Max HP / STR / DEX / CON / INT / WIS / CHA, and a positive whole-number amount from
1 to 99,999. Rows resolve top to bottom alongside damage and healing in the same
Apply transaction. Invalid reduction rows reject the batch; already-applied rows
stay locked and are skipped on later applies. Close discards pending rows only.
Remove the initial unused damage row when applying only a statistic reduction.
Reactions retain the existing damage/healing-only contract.

Effective values equal original/base minus accumulated reductions, floored at zero.
Full reduction amounts are retained, including at zero. Maximum-HP reduction clamps
current HP only if above the new maximum. It does not cause a second damage event,
consume temporary HP, add failed death saves or invoke massive-damage death.
Special consequences of zero abilities, saves, mitigation and monster-specific
rules stay GM-resolved. Derived AC, initiative and attack modifiers are not
recalculated automatically.

### Max HP increase

Next to Add statistics reduction, Increase Max HP raises a target's maximum HP,
for example for *Aid*. Current HP rises by the same amount. A downed character whose
HP rises above 0 is standing again; dead creatures cannot be chosen. A character whose
HP is not tracked can be, and the increase is then only recorded in the activity log. Increases and reductions add up; the increase lasts until
you remove it with Restore statistics, which lowers the maximum again and only caps
current HP.

Current HP also follows a higher maximum in the Edit dialog when you change only Max
HP (if you type a new current HP as well, your values are used), and when Refresh
from source raises a monster's maximum without its HP: damage already taken stays
taken. Ending a Max HP reduction does not give back HP, as in the 5e rules.

### Restore statistics: affected values only

Restore statistics is next to Reset in each character row and also available for
monsters. It now opens a table with separate columns:

| Statistic | Original/base | Reduction | Effective |
|---|---|---|---|
| Max HP | 1 | 9 | 0 |

Only statistics with active mechanical reductions appear, and Max HP while it has an
increase (shown next to the reduction, for example "0 (increase +5)"). A zero effective value
still appears while its reduction exists. Unknown/unaffected abilities do not
appear, and the table's original values are read-only. Reduction is the full
stacked amount, not a value clipped to the base. The restore selector contains
only affected statistics; All affected statistics is offered when more than one
statistic is reduced.

Choose the statistic(s), click Restore selected statistics and confirm. Restoration
removes their reductions (and, for Max HP, its increases) and restores effective values
to the originals. It never
heals current HP or resurrects and does not reset initiative, temporary HP, battle
membership or unrelated conditions. Cancelling makes no change. Restored rows
and options disappear after refresh. With nothing left, the dialog says No statistic
reductions or increases to restore and disables the restore selector and button.

### Separate original/base editor

The original source has no ability scores, so enter known originals before applying
ability reductions. From Restore statistics, choose Edit original/base statistics…
to switch to a separate editor. Only in this editor are all seven original values
shown. Enter known ability scores (0–30), leave unknown abilities blank, and use
Save original/base statistics. Back to affected statistics returns to the filtered
restore view; it discards unsaved base-editor drafts. Closing also discards drafts.

An ability base cannot be cleared while it has reductions. Editing a base never
heals and does not remove active reductions. Open base drafts are not overwritten
by polling. Changing campaign or setup closes the dialog and discards drafts.
Stale operations are rejected; reopen and review rather than retrying an old state.
The server token, payloads, base storage and reduction mechanics are unchanged by
the layout correction. Base editing in the browser uses safe integers; HP storage
still follows the existing signed-64-bit limit.

### Reset, persistence and privacy

Legacy effective Max HP edits that would change an actively reduced maximum are
rejected: use original/base editing. Submitting its unchanged effective value is
allowed. Without maximum-HP reductions, legacy max-HP edits update the opted-in
base. Ordinary Reset remains distinct: it retains reductions/bases and caps its
normal HP result at the effective maximum. Characters refill to their effective
maximum; monsters use Original HP as the normal reset-HP template. Original HP
is not a replacement for an explicitly edited base. For Original HP 9, base Max HP
20 and reduction 4, Reset yields 9/16; restoring Max HP afterward yields 9/20.

Recovery stays manual: turns, rests, concentration ending and deletion of the
attack source do not expire these reductions. Bases and reductions survive
reload, rosters, setups, setup import, undo/checkpoints and campaign bundles.
An attack batch is one undo operation; restoration and base editing also have
audit/undo records. The player display excludes bases, ability scores and mechanical
payloads, retaining the existing effective-HP visibility policy. No monster presets,
linked healing or special death/recovery automation are included.
