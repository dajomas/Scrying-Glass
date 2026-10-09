> Account storage update: users now live in SQLite (schema v4). The new `superadmin` role manages users; existing `security.users` is a one-time migration input only. See [User management](User-Management.md) for upgrade instructions. This supersedes older configuration-account instructions below.

# Normalized SQLite schema-v3 migration

## Complete source package

This delivery is built against the latest supplied archive, commit
743df7bc7d0d8768f3b12ffcaf3bde61a0d1fb2f. That archive contains slug-based SQLite v1.
The package contains all differences from that archive, including stable campaign IDs,
updated admin JavaScript, normalized persistence, migrations, tests and documentation.
Apply every included source file together. No source file needs deleting. Existing
configuration, uploaded images and unchanged application code remain in place.

## What is no longer JSON

There are no serialized JSON payload columns in schema v3. Campaign metadata, display,
battle/turn settings and import status use typed scalar columns. Characters, monsters,
battle-order/successor lists and activity logs use separate records, each with an integer
primary-key id. Original combatant IDs and log event IDs are retained in dedicated columns.
Array order uses position. Edits/reordering retain row IDs; copy creates new instance IDs.

Scalar extension attributes and field-presence markers use typed child records. This
preserves absent versus null fields and existing extra scalar attributes without storing
objects or arrays in a text field. Unsupported nested extras/unknown state fields fail,
rather than silently being discarded. JSON remains the API/in-memory format and is read
for old-database/legacy import only. Configuration files are outside this storage change.

## Supported starts

- Empty storage/original JSON: create v3; import original data once, non-destructively.
- SQLite v1: back up, assign campaign IDs and normalize all structured payloads.
- SQLite v2: back up, keep the existing campaign IDs and normalize structured payloads.
- SQLite v3: normal startup, no repeated schema conversion.

Unknown versions/nonempty unversioned databases are rejected. Do not manually set
user_version or rename columns to bypass migration.

## Install and test

1. Stop the application; prevent automatic restart during deployment.
2. Back up its entire configured data directory, configuration and matching code.
3. Extract the complete changed-files archive into the matching checkout root.
4. With the existing Python 3.14 environment active, run:

   ```bash
   python -m compileall -q scrying_glass_server.py python web_html tests
   python -m unittest discover -s tests -v
   python -c 'import sqlite3; print(sqlite3.sqlite_version)'
   python -c 'import scrying_glass_server; print("Route construction OK")'
   ```

   Optional developer checks:

   ```bash
   node --check static/admin.js
   bash -n run.sh
   ```

   sqlite3 is part of the Python installation, not a new pip requirement. Launchers
   now preflight sqlite3 availability. Pip dependencies are unchanged.

5. Test against a COPY of production data using unused ports:

   ```bash
   python scrying_glass_server.py --config config.yaml      --storage-dir /absolute/path/to/copied-data      --admin-port 13000 --client-port 14000
   ```

6. Inspect the startup log and schema. Verify campaign/character/setup counts, original
   combatant IDs, HP, log entries, backgrounds, turn/round/order and font size. Exercise
   campaign rename, setup rename/move/copy/delete and restart. Confirm record IDs are
   stable for unchanged entities and list entries.
7. Deploy against production only after the copied-data smoke test succeeds.
8. Hard-refresh the admin browser; campaign API values now use IDs, not slugs.

## Automatic backup and transaction

An existing v1/v2 database is backed up with SQLite's backup API before schema changes:

```text
scrying-glass.sqlite3.before-normalization.bak
```

If that filename exists, a numbered filename is chosen instead. The backup includes
only the database, not uploaded media/configuration; keep the full manual backup too.
Ensure enough disk space and write permission for backup and SQLite journals.

The upgrade reads all old payloads, allocates/retains campaign IDs, creates normalized
tables/child records, converts references and checks foreign-key integrity inside a
BEGIN IMMEDIATE transaction. user_version becomes 3 only after successful conversion.
Typed/structural validation failures roll back SQL schema and data. Keep the failed
upgrade backup; the application reports the problem instead of overwriting unknown data.

Schema conversion commits before normal domain startup validation. If later domain
validation rejects an encounter, the database is already v3: restore the backup with
matching old code if you need to reverse the upgrade. Unsupported nested extensions,
duplicate explicit IDs, malformed JSON, unknown live references and nonempty embedded
setup characters require resolution rather than silent truncation. Older transition
files with setup-owned characters must be reconciled into a campaign roster first.

Saved setups do not own an active runtime-setup association, so historical copied
active_setup fields are not persisted in saved encounters. Live runtime references are
strict. Existing v2 campaign IDs and valid live associations survive normalization.
Diagnostic legacy maps/migration records are rows, not serialized JSON metadata.

## Relational tables

See Database-Schema.sql for actual generated DDL. The main records are campaigns,
battle_setups, character_rosters, characters, encounters, monsters, ordered_combatants,
activity_log_entries and application_state. Integer storage IDs are distinct from
combatant UUID strings/event IDs used by the application. Logs retain historical actor/
target ID/name fields even when the live combatant no longer exists; those text IDs
are deliberately not deletion-cascading foreign keys. Ownership relationships are
foreign keys with cleanup appropriate to their scope.

Setups now have internal stable IDs. Their API remains campaign ID plus normalized
setup name for compatibility with the existing setup controls. Last-used and active
setup associations are ID-based internally. Rename/move preserves setup identity;
copy creates a separate setup/encounter and child records.

## API changes from supplied v1 source

GET /api/campaigns returns id rather than slug. active is a decimal campaign-ID string.
Campaign paths, setup request campaign/from_campaign and move_to values carry IDs.
Runtime active_setup uses {"campaign_id":"12","name":"fight"}. The included admin.js
handles these changes. External scripts must obtain campaign IDs from the campaigns
endpoint rather than deriving them from names. Database INTEGER IDs remain integers.

## Rollback

Stop the application. Preserve the current normalized database for recovery. Restore
the pre-upgrade database backup under its original filename and the matching old code/
frontend. For a JSON rollback, restore matching original code plus the complete original
JSON/media/config backup. Post-upgrade changes are NOT written back to the old JSON or
old SQLite backups. No reverse converter is included.

## Operating limits and validation

Use one server process per data directory. One event-loop thread owns the database
connection. Existing mutating-request transactions and deferred broadcasting remain.
Nested transactions join the outer unit, not independent savepoints. Media files are
outside SQL rollback and failed mutations can leave orphaned uploads. Synchronous SQL
and slow remote work may delay other mutations. Back up database plus media with the
process stopped; never remove a live journal.

The included unit tests execute actual SQLite upgrades and changed domain/handler code,
not a running HTTP server. See the accompanying validation report for executed tests,
archive completeness checks and limitations. Real FastAPI routing, browser/WebSocket
workflows, Python 3.14 and Windows launchers must be checked in the deployment environment.
