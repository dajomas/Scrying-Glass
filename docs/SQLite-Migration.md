# SQLite migration

## Scope

This change replaces structured JSON-file persistence with a single
`scrying-glass.sqlite3` file under the configured `storage_dir`. Configuration,
monster/background images, static assets and templates remain filesystem files.
The frontend and API route contracts are unchanged. No SQL server, ORM or new pip
dependency is required. Python's sqlite3 support must be available.

## Install safely

1. Stop Scrying Glass and prevent automatic restart while replacing files.
2. Back up the complete configured data directory and configuration. Retain the
   exact pre-migration code revision too.
3. Apply every file in the changed-files package at its repository-relative path.
   Do not replace just the persistence module; handlers and service wiring changed too.
4. With the existing virtual environment active, validate from the repository root:

   ```bash
   python -m compileall -q scrying_glass_server.py python web_html tests
   python -m unittest discover -s tests -v
   python -c 'import scrying_glass_server; print("Route construction OK")'
   ```

5. Test first against a COPY of your data directory, using unused ports:

   ```bash
   python scrying_glass_server.py --config config.yaml      --storage-dir /absolute/path/to/copied-data      --admin-port 13000 --client-port 14000
   ```

6. Confirm campaigns, rosters, encounter counts, backgrounds and images. Exercise
   rename, move/copy, delete, battle turns and font controls. Restart and verify the
   active campaign/setup, HP, battle round, turn and display settings.
7. Stop the test server. Start the production service against its normal data directory,
   check its log for the import summary, and repeat the smoke tests.

## First startup

The importer reads campaigns.json, discovered campaign folders, setups, character
rosters and state.json. Registry-only campaigns remain represented. Loose setups are
copied into Default campaign records with numeric collision suffixes. Missing character
rosters are seeded from last_setup, otherwise the newest imported setup. Setups are
validated; missing identifiers are normalized into persisted records. Original file
modification times are imported for newest-setup selection. Empty campaigns receive
an empty default setup.

The importer never renames, overwrites or deletes legacy source files. Import,
restoration validation, order cleanup and initial state saving run inside the startup
transaction. Invalid JSON, invalid state, incompatible active-campaign references,
and missing referenced setups stop startup and roll back the import. Fix the source
problem and retry; an uncommitted import does not leave a completed-import marker.
If a database already contains campaigns but lacks the marker, startup refuses to
blindly merge/overwrite it. Inspect or restore that database explicitly.

Once the completion marker is committed, subsequent startups read SQLite only.
Archived JSON edits have no effect. Copying new JSON files into setups/ is no longer
an import mechanism. Monster/character CSV and setup-to-setup imports in the UI remain.

## Backups and rollback

For a consistent backup of the database PLUS images, stop the application and copy
its complete data directory together with the configuration. The directory must be
writable for SQLite's journal as well as uploads. This version uses the normal SQLite
rollback journal, not an explicitly enabled WAL configuration. Do not delete a live
journal or copy only the main database while writes are in progress.

To roll back, stop the service, preserve the current SQLite database for recovery,
restore the pre-migration code AND its full pre-migration data/configuration backup,
and restart. Original JSON files remain on disk but become stale as soon as database
writes occur. Merely switching code back will not carry post-migration changes into
those JSON files. No reverse exporter is included.

## Operational boundaries

Run one application process per data directory. SQLite does not make the application's
in-memory STATE distributed across workers. The database connection is owned by the
server event-loop thread. Mutating admin calls are serialized and transactional;
HTTP reads and viewer WebSockets retain the existing application architecture.
Slow remote image requests inside a mutating call can delay other mutations.
Uploaded media is not transactionally rolled back with SQL. A failure after an upload
may leave an unreferenced image file; do not garbage-collect images without checking
all saved setups and working state.

## Validation delivered with this change

The included tests exercise actual SQLite operations, domain services and handler
methods without requiring a running web server. A small test-only context provides
configuration and HTTP exception/slug helpers. This is not FastAPI HTTP integration
or browser testing. See the accompanying validation report for actual executed checks
and environment limitations. Run route construction and browser smoke tests in your
Python 3.14 deployment environment before merging.
