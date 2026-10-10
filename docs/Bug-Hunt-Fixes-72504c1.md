# Bug-hunt fixes for source archive 72504c1

This is a changed-files overlay, not a complete application or a database backup.
It is based on the supplied scrying-glass-source-72504c1-base64.txt archive.

## Included application changes

- python/scrying_glass_storage.py: rename the setup and all matching checkpoint
  references within the same transaction, scoped to the campaign. Uses the existing
  schema; no schema-version change. Setup boundaries still invalidate undo history.
- python/scrying_glass_admin_battle.py: end concentration and remove its linked
  effects immediately when a damage row downs a concentrating source, before a
  later healing row can restore positive HP. Non-downing damage retains the normal
  manual concentration-reminder behavior.
- python/scrying_glass_campaign_bundle.py: collect/rewrite media only in combatant
  image_url fields and display.background, across the roster, saved setups and live
  encounter. Names, descriptions, effect notes and activity text are not rewritten.
  CSS backgrounds retain local media support; external media URLs stay external.

## New tests

- tests/test_bughunt_fixes.py: 10 regressions covering checkpoint rename/restore,
  campaign scope, transaction rollback, restart, concentration transitions,
  concentration undo, free-text preservation and local/external media handling.

## Apply

1. Stop the running application and back up the code and storage directory.
2. Extract the archive into the repository root, preserving its python/, tests/
   and docs/ paths. Replace only the included application files. Review local
   changes before overwriting: these replacements target source archive 72504c1.
3. Run the tests from the repository root:

   python -m unittest discover -s tests -v

   for test in tests/test_*.js; do node "$test" || exit 1; done

4. Restart the application and smoke-test checkpoint restoration after renaming,
   a down-then-heal action batch, and campaign export/import with media and notes.

## Limitations

The rename fix preserves references for renames performed after applying this
update. It cannot infer the intended setup of checkpoints already orphaned by
previous renames. No automatic historical repair is performed.

Tests exercise service/transaction/SQLite behavior and the existing Node tests;
no full-browser or deployed HTTP integration run was performed.

See the bundled validation log for executed tests and their results.
