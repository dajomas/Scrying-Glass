# Encounter features: deployment, usage and limitations

Documented baseline: `features/development` at `4f401b4adfca92e9c9599aea8924c14efb49aea4`.

This is current functionality documentation, not a sequence of overlays. Install the complete matching revision using the [README](../README.md). Keep configuration and live storage separate from source updates.

## Database migration and rollback

The schema upgrades automatically from v4/v5 to v6 on startup. Supported older schemas still
follow the existing upgrade path first. Existing installations receive a SQLite backup via
SQLite's backup API before upgrade. The existing storage.migration_backup/startup message
reports its location. No backup is needed when creating a fresh database.

New tables store encounter-owned lairs, effects, encounter snapshots (including their own character rows), and a
monotonic state revision. Live and archived combatant/effect data remain normalized relational
records; this patch does not introduce JSON database columns. Campaign bundle manifests use
JSON inside the portable ZIP, not as the canonical live persistence format.

Code targeting v4/v5 does NOT support schema v6. To roll back, stop the service, restore the previous
source AND the pre-upgrade database backup, and restore the corresponding uploads if they
changed. Changes made after that backup will be lost. Do not merely change PRAGMA user_version.
Retain the full deployment backup as well as the automatically generated database backup.

## 1. Undo

The Encounter tools section shows a descriptive Undo button. History is persistent and limited
to 30 operations for the active encounter. Supported operations include HP/temporary HP edits,
condition edits, concentration changes, start/next/end, reset, selected bulk actions, and
checkpoint restore. A bulk operation is a single undo step.

Undo restores encounter state plus the affected campaign character roster and active setup
atomically. Later audit events are retained, and an undo event is appended. Undo requests bind
to the current top history ID and verify an encounter fingerprint to reject stale requests.
History survives restart. Campaign/setup switches and unsupported structural mutations clear
history. Account changes and image uploads/full monster image edits are not undoable.

Undo restores the recorded state; it does not retroactively roll dice or reverse outside actions.

## 2. Conditions, effects and concentration

Open Encounter tools > Combatant health, conditions and effects. Select a target and add an
effect with a name, optional source and private notes. Names are private by default. Check
Show name to players to expose only the effect name: notes, source IDs and counters are not
included in the player payload. Existing buff/debuff action rows still log generic actions;
use the new effect form to create a persistent condition.

Manual effects last until removed. Timed effects name an anchor combatant and count start/end
boundaries of that anchor's turn when Next is used. The UI calls this Occurrences remaining,
not rounds. Applying an effect during a turn with End/1 expires at that turn's next end; Start/1
expires when that anchor next receives a turn. Manual turn assignments do not expire effects.
An inactive or skipped anchor does not receive an automatic start boundary; remove or manage
such an effect manually. Undo restores effect counters and removal.

Concentration-linked effects require an existing standing source. End concentration removes
all currently loaded effects linked to that source, not independent conditions. A downed/dead
or deleted source loses linked effects. Only one concentration flag exists per source; the GM
must end previous concentration before creating a different concentration-linked spell.
Damage records a concentration reminder, but the check itself is manually adjudicated.
There is no complete spell/rule automation.

## 3. Down / stable / dead

Health states are standing, down, stable and dead. New and legacy zero/nonpositive-HP combatants
become down rather than automatically being labelled dead. Legacy alive=False with positive HP
is retained as dead. The older alive field remains a compatibility flag meaning standing for
turn eligibility; actual death is determined by life_state.

Set state can down, stabilize, mark dead or explicitly recover a combatant. Recovery raises HP
to at least 1 and clears death-save counters. Healing may recover down/stable combatants when HP
becomes positive, but does not automatically resurrect an explicitly dead combatant. For down/stable combatants, three manual
successes stabilize and three failures mark dead. Damage also updates character failures at zero HP and applies excess-damage instant death; see [Damage logic](Corrected-Damage-Logic.md). Counters are entered manually; automatic die
roll handling and complete edition-specific rules are not implemented.

Active down/stable characters retain initiative turns for manually resolved death saves; dead characters and non-standing monsters are excluded from future turns. The current turn can remain owned after death until Next resolves advancement. The admin pane shows a
manual death-save reminder for active downed characters. Down/stable visible combatants are
labelled distinctly on the viewer; their active monster cards remain visible with muted styling.
Dead cards retain the existing removal behaviour.

## 4. Temporary HP

Temporary HP is a distinct nonnegative pool. Set replaces the pool rather than stacking it.
Damage deltas and battle damage consume temporary HP before normal HP. Positive healing caps at maximum HP and does
not replenish temporary HP. The feature pane offers a damage-bypass checkbox and preview.
Absolute HP edits remain direct corrections and bypass temporary HP. Reset clears the pool.
The viewer receives a monster's temporary HP only when Show HP is enabled.
The preview uses the last fetched state; refresh first if another admin is changing that target.

## 5. Viewer synchronization

Persistent state revisions and render acknowledgements let the admin distinguish live, behind and stale displays. The server sends heartbeats after 15 seconds without an incoming application message; the browser replies with PONG. Lack of application replies alone does not close a viable transport. The viewer reconnects in place with bounded backoff and keeps the last rendered encounter visible. Status is a last-contact/revision metric, not proof a human saw the screen. See [Display connections](Display-Connection-Stability.md).

## 6. Checkpoints and campaign bundles

Save a named encounter checkpoint or use the automatic Before battle checkpoint created on
Start. Up to 50 checkpoints per campaign are retained; oldest entries are pruned. Checkpoints
contain the character roster as well as monsters, HP, effects, turn order, round, display state
and audit history. Restore previews the counts and round and requires explicit confirmation
against the current revision. Restore replaces current encounter/roster state but retains the
current audit trail and adds a restore event. The restore itself is undoable. References to
missing setups are rejected rather than silently recreating a deleted setup.

Export campaign bundle includes the active campaign metadata, roster, saved setups, current
encounter and referenced local media. External image URLs remain URLs and are not downloaded.
Accounts/password hashes, other campaigns and the accumulated undo/checkpoint collection are
not exported. The current encounter is preserved in the bundle.

Import always creates a NEW campaign, resolves name collisions, renames imported media and
rewrites references. It never overwrites an existing campaign or activates the imported one.
Switch to that new campaign and restore its Imported encounter checkpoint to resume runtime
state. Imported effect source and anchor IDs remain scoped to that campaign. Import supports
only this versioned Scrying Glass bundle format, not arbitrary archives.

Limits: 25 MiB compressed, 100 MiB expanded total, 10 MiB manifest, 1000 members, 200 setups.
Media allowlist: png, jpg, jpeg, gif, webp, avif, bmp. Referenced media must exist. Paths,
duplicate members, unsupported formats and missing media are rejected. Imported files are
removed when a transaction fails. Runtime JSON snapshots are not extracted onto the filesystem.
Campaign bundles are private backups containing GM data; do not distribute them to players.

## Validation and limitations

Run tests for the checked-out revision; historical patch test counts are not current execution evidence:

```bash
python -m unittest discover -s tests -p 'test_*.py'
node --check static/features.js
node --check static/client.js
node tests/test_display_reconnect.js
```

Smoke-test health/effects, undo across restart, stale checkpoint confirmations, bundle import/media, lair ordering/actions and both role-specific interfaces on copied data. Unit tests do not replace live browser, HTTP/WebSocket, proxy or systemd validation. Concurrent administrators share one encounter without optimistic edit-conflict resolution.
