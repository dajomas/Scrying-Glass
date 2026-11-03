# 240 - SQLite storage source split

[Back to handover index](../../HANDOVER.md)

Last updated: 2026-11-03. Task: [SG-TODO-008](../todo/080-source-size-refactors.md).
Current preparation base: a9da32439b01529ab6deba8242b48593d95be594 on features/perplexity.
Original storage: 39,486 bytes / 527 lines, Git blob
ea80b59cca80c6885f6ba1ba4d32b759beb187b5. The uploaded file matches this identity.

## Delivered foundation and staged architecture

The user approved five Storage commits: fields, schema/migration, records/encounters,
campaign/setup/application-state operations, then facade activation. Commits 1-4
stage unused implementation modules and their tests. Commit 5 changes runtime imports.
Increment 1 was delivered as a9da32439b01529ab6deba8242b48593d95be594, adding the
984-byte fields module and five preparation tests. Its module and test blobs were
verified after pushing. No Storage CI result has been inspected or claimed yet.

Shared fields retain the original assignment expressions, tuple ordering, values
and types. STATE_FIELDS is an independent mutable set during preparation. Neither
the staged fields nor schema mixin is imported by the original storage module or
production consumers yet. Original storage, callers, SQL, schema version 8 and
transactions remain unchanged. These stages do not yet provide a split runtime.

## Increment 2: schema/migration mixin prepared

python/scrying_glass_storage_schema.py is 10,076 bytes, expected Git blob
ea70b84536f7a4918a6923ae5068d34fe9c85674. StorageSchemaMixin contains exactly
_create_schema, static convert_campaign_references and _upgrade. Bodies, signatures,
decorators, SQL strings and call ordering are AST-equivalent to the original methods.
Imports are copy/json/time and shared TEXT_FIELDS/INT_FIELDS/BOOL_FIELDS only.
No facade wiring, constructor changes, new migration or production exec/eval.

Seven new standard-library methods passed locally in test_storage_schema_preparation.py:
AST equivalence, signatures/static descriptor, base-schema parity, empty v1/v2 legacy
upgrade parity, rollback after failed legacy migration, reference conversion/deep-copy
parity, and source-size/dependency/original-blob guards. Both sources compile.
The mixin executes real in-memory SQLite, compared with AST-extracted original schema,
transaction/check helpers and set_value in a fixture harness. The clock is fixed
only for deterministic migration-log comparison; SQL/transaction calls are not mocked.
Rollback fixtures fail on an unknown active setup after old tables were dropped and
the new base schema created, and verify restoration of the old schema/data/version.

Limits: empty v1/v2 success fixtures stop at the original base schema version 3.
They do not run the original constructor, create backup files, migrate populated
rosters/setups or execute later v4-v8 upgrades. Full application/storage CI and
activation integration remain pending. Do not present these limited fixtures as
complete migration validation. Increment-1 tests passed during its preparation;
they were not rerun locally for increment 2. Existing normal CI discovers both
modules without workflow changes. Do not claim increment-1 CI passed without evidence.

## Remaining work and compatibility

Next: records/encounters (3), operations (4), native facade activation (5). Keep
SQLiteStorage in python/scrying_glass_storage.py with constructor, connection lifecycle,
backups/transactions and compatibility field exports. Method-source groups before
headers/imports: connection 3,933 bytes, schema/migration 9,760, records 12,707,
operations 11,924. Measure complete files at every stage; maximum is 20,000 bytes.

FeatureStorage calls underscore methods and imports field constants from the old
module; retain these entry points. Import shared fields in new modules rather than
creating circular facade imports. Preserve lazy feature/lair/setup-lair/statistics
imports, savepoints, rollback, backup ordering and record identity. Check patch and
introspection dependencies before activation. The old Schema v4 docstring does not
change the actual SCHEMA_VERSION=8. Adapt preparation AST/original-monolith guards
at activation, when replacing the monolith is intentional; retain behavioral checks.

README, HANDOVER.md, workflow, existing field tests/module and production consumers
were reviewed and left unchanged in increment 2: runtime/deployment and index links
are unaffected. The existing task/index summarize progress. No archive, package
manifest refresh, workflow dispatch or CI skip. Each write needs bound approval.
SG-TODO-004 remains on hold; SG-TODO-006 labels and other task close-outs are separate.
