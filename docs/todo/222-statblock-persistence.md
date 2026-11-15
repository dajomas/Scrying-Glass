# 222 - Statblock persistence delivery

[Back to TODO index](../../TODO.md) · [Parent contract](220-admin-statblock-viewer.md) · [Storage handover](../handover/240-sqlite-storage-split.md#statblock-storage-foundation---2026-11-15)

## Task and status - 2026-11-15

SG-TODO-022.02b is in progress. The initial foundation/activation split was
approved at 12:25 CET. At 13:00 CET the user authorized smaller direct-GitHub
preparatory commits with [skip ci] until the final startup-activation commit.
This addendum governs staging/progress only; the parent's model, typed-table,
migration and lifecycle requirements remain. All writes stay on
features/perplexity-statblock. No owner/deadline assigned.

## Foundation - delivered with covering CI verified

Implementation 4a3f930cb4a0df109b06259bd9ca9a23f01638ee has successful
Branch tests 43709292836 attempt 1. Main unittest ran 1,704 tests OK, including
all eight new storage tests. All configured validation stages succeeded and
evidence was published under ci-results-43709292836-attempt-1. This verifies
the foundation, not startup activation or complete lifecycle integration.

Seven typed relations, callable backed-up 8-to-9 upgrade, atomic save/load/
replacement, revisions, references and optional-field presence are delivered.
Foundation fixtures use a SQLite storage protocol, not the complete production
constructor; stage-two tests below must cover that distinction.

## Startup activation - in progress, not enabled

Preparatory sequence (each write requires its own bound approval):

1. A delivered at 6f8e44dfe7e1d9de166e21d61b697d34e3c89679: shared
   pre-statblock fixture helper, five regression tests and setup-lair v6 fixture.
   Four isolated helper tests passed locally; production-constructor helper
   test and changed setup-lair tests remain pending final covering CI.
2. B delivered at a44727ef76f810ab593305033947c84eb9af26ae: lair v5 and
   encounter-feature v4 fixtures construct pre-statblock databases and reopen
   with the unpatched production constructor. V4 removes the later lairs table;
   backup/account/FK assertions are retained or strengthened. Tests have not
   been run locally; final covering CI is pending.
   [B handover](../handover/010-scope-and-state.md#activation-preparation-b---2026-11-15).
3. C: attack-statistics v7 backup and AST-extracted cleanup changes are included
   in this preparation delivery. Initial construction uses the shared helper;
   reopen is unpatched. The upgraded version must equal the storage class's
   SCHEMA_VERSION; the backup must remain v7 without statblock tables. Both
   reader and storage close on assertion failure. Three isolated resource-
   lifetime checks passed locally; real production migration and the complete
   attack suite remain pending final CI.
   [C handover](../handover/010-scope-and-state.md#activation-preparation-c---2026-11-15).
4. Final activation remains pending: wire upgrade_statblocks into SQLiteStorage,
   update every applicable version guard and version-pinned storage fixture,
   and add actual production-constructor fresh/legacy/reopen/backup/failure
   tests. Omit [skip ci] from the final code commit and review its full run.

Intermediate commits explicitly use [skip ci]. Do not dispatch separate CI
or alter workflows to achieve skipping. Their full validation is deferred,
not claimed passed. Startup remains schema 8 during all preparatory commits.

## Acceptance and validation

The test-only helper suppresses just the statblock migration while constructing
a disposable fixture. It verifies version 8 and absence of statblock tables,
restores the patched function before returning or propagating construction
failure, and closes invalid returned storage. It never removes statblock data
from a newer database. It is for single-threaded tests, not deployed storage.

Stage two must verify complete production databases and constructor cleanup,
matching pre-upgrade backups, transactional DDL rollback, no backup on ordinary
reopen, legacy no-statblock compatibility and future-version rejection. Earlier
migrations must remain intact. Do not mark 022.02b complete before all agreed
activation work and its covering CI are verified.

The normal constructor still rejects schema 9. Do not run the callable upgrade
on deployed storage until matching activation code and a full storage/config/
media backup are available. Rollback restores matching pre-upgrade code/data,
never merely lowers user_version. No end-user statblock UI is available.

Runtime/setup/recovery/undo/checkpoint/copy/bundle preservation and identity
remapping remain 022.03; private saved content must not enter public Client
Display payloads or overwrite SG-owned fields. 022.02a's earlier green run
43707384985 attempt 1 at 0ed81a834d0973179c2c030eb84bb36b35c7e325 is retained
as model history, not relabelled activation evidence.
