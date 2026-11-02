# 130 - Accounts migration fixture repair

[Back to handover index](../../HANDOVER.md)

Last updated: 2026-11-01.

## Diagnosis

Preparation baseline: `6fbe4c1578a7b4f7725a87adb2c1ea2613946e76`. Original `tests/test_accounts.py` Git blob: `fc21e2bd5655ab6723d626da8b9751497d46aebe`. CI run 41315942451, attempt 1, reported `duplicate column name: has_lair` in `test_upgrade_v3_preserves_data_and_creates_backup`.

The fixture started from a fully migrated v7 database, dropped account and feature tables, then set `user_version=3`. It retained the v7 `encounters.has_lair` column and the v6 lairs table. The normal migration chain reached v7 and attempted to add the already-present column. The test also expected version 6 even though `SQLiteStorage.SCHEMA_VERSION` is 7. This inconsistent fixture is not evidence that a genuine v3 database needs duplicate-column tolerance.

Inspection of the constructor and base schema showed that `_create_schema` creates the pre-account v3 schema; account, feature, lair and pane-availability migrations run afterward. Production migration code is unchanged.

## Test repair

Replace the partially downgraded database with a clean database built using `_create_schema`, set version 3 and seed a campaign plus its application-state reference. Assert account/feature/lair additions are absent before opening through the real `SQLiteStorage` constructor.

Check the current declared schema version, campaign values and ID, application-state row/reference, empty users and account-migration marker, and foreign-key integrity. Open the backup independently and verify it remains v3 with the seeded data and without users or `has_lair`. Reopen the upgraded database and verify no additional migration backup is created and campaign data remains intact. All other account tests are unchanged.

## Local validation and limitations

Python 3.12.8 with SQLite 3.46.1: a focused real-SQLite harness reproduced the original duplicate-column error. A clean v3 fixture migrated through the inspected account, feature, lair and pane-availability steps to v7 with preservation and backup checks passing. The exact candidate test method also passed in that harness, including the reopen assertions. The candidate module compiled; AST comparison excluding the repaired method confirmed other code was unchanged. The reconstructed original test file matched its Git blob.

This was not execution against the complete production storage module or the full AccountTests class. The connector truncated the oversized storage response; only complete visible methods needed for this investigation were copied into the local harness, with an adapter for constructor/auth access. No complete storage-file hash verification is claimed. No harness files or substitutes are committed. The real constructor and auth service will be used by the repository test in normal CI.

## Outstanding verification

Full-checkout execution, the complete accounts module, Python 3.14 and full CI remain unverified for this repair. Inspect the actual push-triggered run after approved delivery; no skip marker or extra dispatch is requested. Other viewer, lifespan, JavaScript and standalone failures are not repaired here; see [open validation](030-validation-and-next-steps.md).

README and TODO index were reviewed; no application behavior or unrelated feature-task status changes are needed. The unfinished broader source split remains inactive.
