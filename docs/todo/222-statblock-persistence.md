# 222 - Statblock persistence delivery

[Back to TODO index](../../TODO.md) · [Parent contract](220-admin-statblock-viewer.md) · [Storage handover](../handover/240-sqlite-storage-split.md#statblock-storage-foundation---2026-11-15)

## Task and status - 2026-11-15

SG-TODO-022.02b is in progress. The user approved two implementation commits
on 2026-11-15 at 12:25 CET. This addendum governs staging/progress only; the
parent's model, typed-table, migration and lifecycle requirements remain.
All writes stay on features/perplexity-statblock. No owner/deadline assigned.

1. Storage foundation: code and eight automated tests included in this delivery;
   covering CI pending. Seven typed relations, callable backed-up 8-to-9 upgrade,
   atomic save/load/replacement, revisions, references, optional-field presence
   and constraints. No application-startup migration or runtime callers.
2. Startup activation: pending, after foundation CI review. Wire the migration
   into SQLiteStorage; update all applicable version guards and version-pinned
   storage/attack-statistics fixtures. Test actual production initialization
   from fresh and supported legacy databases, reopen, backup retention and
   injected migration failure. Earlier schema migrations must remain intact.

## Acceptance and validation

Foundation: inspect successful covering CI for all eight new tests and existing
suites. Four SchemaTests passed locally against real SQLite protocol fixtures;
four RepositoryTests are prepared but have not been run locally. Fixtures do
not represent the complete production schema or its constructor. Model-level
validation and content digest checks must succeed on repository save/load.

Stage two must verify complete production databases and constructor cleanup,
matching pre-upgrade backups, transactional DDL rollback, no backup on ordinary
reopen, legacy no-statblock compatibility and future-version rejection. Do not
mark 022.02b complete before both stages and their covering CI are verified.

The normal constructor remains schema 8 during stage one and cannot reopen a
database manually upgraded to 9. Do not run the callable upgrade on deployed
storage until stage-two matching code and a full storage/config/media backup
are available. Rollback restores matching pre-upgrade code/data, never merely
lowers user_version. No end-user statblock import/read/write UI is available.

Runtime/setup/recovery/undo/checkpoint/copy/bundle integration and remapped
identities remain 022.03. Saved reference content must not enter public Client
Display payloads or overwrite SG-owned fields. 022.02a has green covering run
43707384985 attempt 1 at 0ed81a834d0973179c2c030eb84bb36b35c7e325;
that result is not validation of this new foundation delivery.
