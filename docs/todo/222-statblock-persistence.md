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

1. A: shared pre-statblock fixture helper, its five regression tests and the
   setup-lair v6 migration fixture are included in this preparation delivery.
   Four isolated helper tests passed locally; production-constructor helper
   test and changed setup-lair tests remain pending final covering CI.
2. Prepare lair v5 and encounter-feature v4 migration fixtures in bounded
   follow-up commits. Construct pre-statblock databases before removing older
   additions; reopen using the unpatched production constructor.
3. Prepare attack-statistics v7 backup and its AST-extracted resource-cleanup
   fixture without changing their assertions into weaker migration coverage.
4. Final activation: wire upgrade_statblocks into SQLiteStorage, update every
   applicable version guard and version-pinned storage fixture, and add actual
   production-constructor fresh/legacy/reopen/backup/failure tests. Omit
   [skip ci] from this final code commit; review its complete covering run.

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
