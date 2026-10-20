# Scrying Glass User Guide

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

Admin defaults to port 3000; Client defaults to 3100. Separate cookies allow both in one browser. Logout affects only the current interface; restart clears all sessions. Account edits invalidate that user's sessions and display sockets.

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

Characters belong to the campaign, not setup snapshots. Add/edit name, color, HP, maximum HP and initiative. CSV imports append to the roster. Removing a character changes the roster across that campaign's setups.

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

## Participation and initiative

Active/Join Battle controls participation; Visible controls the player strip. Pane visibility is presentation only. Monsters additionally support Ally and Show AC/HP/Init. Ally changes the rendered label, not stored name.

Characters/monsters require whole-number initiative before joining. Zero/negative values are valid; unset is not. Mixed bulk joins fail atomically if anyone lacks initiative. Leave before clearing initiative, or deactivate and clear in the same API update. Lair initiative is fixed.

Select all selects the list; Unselect all clears. Select dead replaces selection: characters match explicit death/three failures, monsters also match alive=False. Selection does not mutate. Reset restores baselines/runtime flags; Remove permanently deletes.

Start battle resolves ties. Characters default ahead of monsters within ties; changing a position swaps within that group. Roll shared initiative (d20) gives selected monsters one roll, not a shared turn or running-order reorder.

Next advances eligible participants. Down/stable characters retain turns for manual death saves; dead characters and non-standing monsters do not receive future turns. A dead current participant may retain unresolved ownership until Next.

Round starts at 1, increments on wrap and clears on End, Reset All or no eligible participants. Eligible runtime turn/round survive restart; loading saved setups does not revive old turns. End does not fully reset combatants.

Viewer A−/A+ changes strip text 2 px at a time, default 16, bounds 12–40. Runtime persists it; setup Save captures display settings.

## Battle actions and reactions

Click the highlighted turn owner. Ordinary actions require a standing actor and active targets. Damage/heal may target down/stable creatures; ordinary explicitly dead targets need recovery. Buff/debuff require standing targets and only log descriptions: use effects for persistent conditions.

Damage/healing amounts must be positive. Enter damage after adjudicating mitigation/critical dice. Critical hit affects failed saves at zero HP, not entered damage.

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


Start-of-turn damage/heal targets the current creature, damage first, ignores empty/zero fields and does not advance. Ordinary self-action eligibility applies, so down/dead actors cannot use it.

## Health and death saves

States: standing, down, stable, dead. Explicit recovery raises HP to at least 1 and clears counters. Healing can recover down/stable but not explicit death.

Temporary HP is a separate nonnegative pool: Set replaces, not stacks. Damage consumes it first unless bypass selected. Healing caps at max HP and does not replenish temporary HP. Absolute HP corrections bypass attack logic.

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

## Troubleshooting monster-stat suggestions

When adding a monster, species lookup can find a name but still fail to obtain
stats. D&D Beyond may redirect the server request to a marketplace page even
when the GM's signed-in browser displays the monster.

The notification now distinguishes:
- No exact monster links: the search response contained no accepted exact match.
- Page could not be retrieved as a monster stat page: a request failed or the
  downloader rejected a redirect/oversized response; consult server logs.
- Monster page returned but AC/HP could not be parsed: the parser found neither
  value; this is not proof of a markup change or accessible stat content.
- Lookup could not be completed: failure outside an individual candidate,
  including search-request errors; consult server logs.

Candidates are tried in existing order, legacy first. A failed candidate does
not prevent trying the next one. Enter AC/HP manually when suggestions are
unavailable. This update does not grant access to restricted D&D Beyond content.
