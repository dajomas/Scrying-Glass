# 130 - Accounts migration fixture repair

[Back to handover index](../../HANDOVER.md)

Last updated: 2026-11-16. Original accounts-fixture record: 2026-11-01.

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

## Native and legacy storage fixture separation - 2026-11-16

This correction 6 record concerns facade copy integration, not reopening the
historical accounts repair above. Baseline: 5109e0c152d99a2e2c9e33101c43e0e0739ced9c
on features/perplexity-statblock. The naming/checkpoint/copy/move test now explicitly
requests the real SQLiteStorage constructor and asserts schema 9. Legacy fixture
callers still receive the unchanged base schema 3; no fake upgrade or relaxed
private-clone version check is introduced. Temporary-directory/database cleanup
is registered in close-before-directory order. Constructor failures retain their
existing self-close behavior.

The current-schema branch does not create the legacy four-column snapshot table.
Checkpoint seeding uses FeatureStorage.save_snapshot with the source setup reference,
so the original checkpoint-rename assertion tests a real recovery record. Original
naming, suffix, stable move identity, deletion, roster rejection and rollback checks
remain. Two new native methods check fixture separation and rollback after the real
clone has produced a matching revision-one snapshot and a persisted destination.
The latter compares the complete SQL dump and original private snapshot after an
injected late failure. Production code, base_storage, other legacy tests, correction
5's unit/guard tests and correction 7's old dispatch expectation are unchanged.

Four changed/added methods compile and AST-parse; all thirteen original assertion/
assert-raises nodes in the copy/move case remain. Four isolated checks passed for
the exact proposed fixture's legacy/native routing and wrong-version rejection,
plus the inspected production transaction body's nested SQL rollback. Constructor/
legacy callbacks were doubles with real constrained SQLite, not actual migrations.
No native constructor, checkpoint writer, graph clone, changed copy/move case or
new native regression was executed. Full-module and final covering CI remain pending.
Inspected facade blob: b67d5d8b360311d1eaa71f49e76422a0d3d8a400; clone kernel:
350764b76bd617aee4f7cbf702d6299c2c908d74; feature storage:
981c10c866218b14dc332edda737800a2162e668. No local doubles are committed.

This intermediate correction uses [skip ci], without workflow edits or manual
dispatch. README, existing indexes and backup/runtime guidance remain applicable.
[Series status and remaining gates](../todo/223-statblock-lifecycle.md#ci-correction-series---2026-11-16).

## Facade dispatch guard correction - 2026-11-16

Correction 7 baseline is c093d772513051f5c88623af1b72c63d89cde19a, the delivered
fixture correction. The obsolete save_setup module expectation now names the
active statblock storage mixin. Added identity assertions require the facade's
save_setup, transfer_setup and set_value to resolve to that mixin, not merely to
functions reporting the same module name. Existing schema, staticmethod and
schema/records dispatch checks remain. The same 20,000-byte and no-exec/eval/compile
loop body still checks the original five modules and now the active storage
statblock module too. No size limit or forbidden-call condition is relaxed.

A new native test spies on the real _save_preserving_statblocks hook with wraps,
requiring one call with the resolved encounter and snapshot, then checking stored
HP, schema 9 and no open transaction. The hook is not replaced by a no-op. Other
fixture, migration, copy/move, rollback and rejection tests are unchanged. No
production code, route, schema or permission changes are included.

Both changed/added methods compile/AST-parse. AST comparison confirms the existing
file-guard loop body is identical and its original five suffixes are retained.
Six isolated guard checks passed with controlled class/file doubles: correct
bindings pass, old pin fails, plain-save bypass fails, same-module counterfeit
fails, 20,000 bytes passes while 20,001 fails, and eval in the new module fails.
These are checks of the proposed assertions, not native method execution or actual
repository file-size results. The native hook regression, complete module, real
source-budget/AST checks and final covering CI remain pending. Inspected statblock
mixin blob: a6d7b16fa0bebfd550ebc7a02d4aa305f7413f21.

This intermediate commit uses [skip ci]; no workflow edit or separate dispatch.
Corrections 8-9 and broader acceptance gates remain open. README/runtime guidance
and root index links remain unchanged. [Series status](../todo/223-statblock-lifecycle.md#ci-correction-series---2026-11-16).

## Save As contract entry-point correction - 2026-11-16

Correction 8 baseline: f2d4fa699e2ef1a56d56332e4c37a0d94057f8d6. The earlier
Stage 2 test invoked raw SQLiteStorage.save_setup, a tracker-only boundary that
preserves a destination's existing content but does not acquire source/private
write authority from a carrier or combatant ID. Save As is the protected admin
save workflow using save_setup_with_private and save_new_setup. This correction
changes that test invocation explicitly, not its four original content/revision/
source-preservation assertions and not production storage's authority contract.

The test now uses transactional_handler around the actual AdminSetupsMixin.save_setup
method, starts from source revision greater than one and checks independent owner,
fresh destination revision one, live metadata/reference refresh and reload. Four
added native cases cover unsaved live edits/source isolation, raw tracker-only
saving plus forged-envelope atomic rejection, inactive-campaign denial and rollback
after a last-setup reference write. The original import-remapping test and every
other original method are AST-unchanged. No assertions are skipped/xfail-marked,
no production entry point changes and no raw private-write channel is added.
These are native service fixtures, not actual actor/HTTP authorization coverage.

Original test source was reconstructed to blob 5de4ff6486d975e564629bcb42db27e444d162cc.
The complete proposed module compiles/AST-parses (fourteen test methods). All four
original Save As assertion nodes remain; other original methods are unchanged.
Five isolated helper/inspected-handler routing checks passed for protected dispatch,
default/foreign campaign handling, operation order and error propagation. Transaction,
private persistence and carrier collaborators were doubles. These checks did not
execute SQLite graphs, native rollback, source ownership, raw-input rejection, full
service integration or HTTP. All changed/added native contracts and final CI remain
unexecuted for this correction. Earlier six 2C.3b passes are baseline evidence only.
Inspected helper/kernel blobs: f519facf8c6f84a479af934a7690c729617ce0dd and
d8be6cd1a7e04bb27ac90ea96e7957d8db7b96d9; admin module:
76de5c4374ab28e458024c9b540598b24a405a38.

Only the contract tests and existing documentation change. This intermediate
commit uses [skip ci], with no workflow edit or dispatch. Correction 9 still
requires private setup-import implementation; broader 2C.3c/2D, bundle, Stage 3
and acceptance gates remain open. README and root index links remain applicable.
[Current status](../todo/223-statblock-lifecycle.md#ci-correction-series---2026-11-16).
