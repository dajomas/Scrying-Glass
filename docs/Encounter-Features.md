# Encounter features: deployment, usage and limitations

## Baseline and scope

This changed-files-only overlay targets the latest attached scrying-glass-source-base64.txt
(218724 bytes), not the earlier single-port experiment. The original two FastAPI applications,
admin/client ports, session cookie separation and account-role landing pages are unchanged.
No actual config.yaml, SQLite database, uploaded media, credentials, or unrelated source files
are included in the overlay.

## Install

1. Check out the intended development branch and ensure your working tree is clean.
2. Stop the service. Back up the existing source AND the complete storage directory.
3. Extract the ZIP into the application root, preserving the relative paths and overwriting
   only included files. Review with git diff before starting the service.
4. Keep your existing config.yaml and two-port configuration.
5. Start normally with run.sh or your existing systemd service.
6. Hard-refresh both the admin and display browsers so the updated JavaScript is loaded.

The application dependencies do not change. No dependency-install script was modified.

## Database migration and rollback

The schema upgrades automatically from v4 to v5 on startup. Supported older schemas still
follow the existing upgrade path first. Existing installations receive a SQLite backup via
SQLite's backup API before upgrade. The existing storage.migration_backup/startup message
reports its location. No backup is needed when creating a fresh database.

New tables store effects, encounter snapshots (including their own character rows), and a
monotonic state revision. Live and archived combatant/effect data remain normalized relational
records; this patch does not introduce JSON database columns. Campaign bundle manifests use
JSON inside the portable ZIP, not as the canonical live persistence format.

Older code does NOT support schema v5. To roll back, stop the service, restore the previous
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
becomes positive, but does not automatically resurrect an explicitly dead combatant. Three manual
successes stabilize and three failures mark dead. Counters are entered manually; automatic die
roll handling and edition-specific death-save/damage rules are not implemented.

Downed combatants remain skipped in normal initiative advancement. The admin pane shows a
manual death-save reminder for active downed characters. Down/stable visible combatants are
labelled distinctly on the viewer; their active monster cards remain visible with muted styling.
Dead cards retain the existing removal behaviour.

## 4. Temporary HP

Temporary HP is a distinct nonnegative pool. Set replaces the pool rather than stacking it.
Damage deltas and battle damage consume temporary HP before normal HP. Positive healing does
not replenish temporary HP. The feature pane offers a damage-bypass checkbox and preview.
Absolute HP edits remain direct corrections and bypass temporary HP. Reset clears the pool.
The viewer receives a monster's temporary HP only when Show HP is enabled.
The preview uses the last fetched state; refresh first if another admin is changing that target.

## 5. Viewer synchronization

Every state message carries a persistent monotonic revision. The viewer acknowledges successful
rendering and sends periodic pings. The server revalidates sessions and records acknowledgement
and last contact per socket. The admin pane distinguishes live, behind and stale displays.
The viewer displays Live, waiting-for-latest-state, reconnecting, or stale/disconnected status.
Unresponsive connections are closed and the existing reload-based reconnect behaviour is retained.
Acknowledgements establish that the browser processed the snapshot, not that a human saw it.
An old viewer tab must be refreshed to load the new ping/ack code.

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

## Validation

The build environment ran 99 unit/regression tests successfully, including real SQLite tests
for v4 upgrade backup, temporary HP, health-state changes, private effect filtering, timed effects,
linked concentration removal, undo and restart persistence, rollback, campaign scoping,
checkpoint confirmation, bounded snapshot cleanup, revision status and safe bundle imports.
Existing migration/account/logout/domain tests passed. Python compile checks and Node syntax
checks for both changed/new JavaScript files passed. ZIP integrity is checked after packaging.

These results are NOT a live browser, HTTP/WebSocket, TLS-proxy or systemd deployment test.
FastAPI/Uvicorn are unavailable in this execution environment. The test report is included.
Test first on a copy of your database/development instance, not during an active game.

Run the regression suite from the application root:

    python -m unittest discover -s tests -p 'test_*.py'
    node --check static/features.js
    node --check static/client.js

Manual smoke checks before merging:
- Sign in independently on admin/client ports and confirm account-role behaviour is unchanged.
- Damage a temporary-HP target through inline edits and battle actions; undo and restart.
- Add public/private effects; inspect the viewer WebSocket payload for private information.
- Advance through start/end anchor turns; undo across round wrap and confirm effects/turn state.
- Down, stabilize, mark dead and recover both a character and monster.
- End concentration, delete its source, and undo supported changes; verify linked effects.
- Disconnect/reconnect a display and verify the admin and viewer synchronization indicators.
- Save/preview/restore a checkpoint; confirm an old preview is rejected after another edit.
- Export/import a media-bearing campaign; confirm original data is unchanged and images resolve.
- Verify backup location and rollback on a disposable copy before production deployment.
