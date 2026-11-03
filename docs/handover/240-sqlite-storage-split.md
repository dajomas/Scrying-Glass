# 240 - SQLite storage source split

[Back to handover index](../../HANDOVER.md)

Prepared 2026-11-03. Task: [SG-TODO-008](../todo/080-source-size-refactors.md).
Base: f3cfea4a557a02136dbbfd7a4ae73695636d621d on features/perplexity.
Original storage: 39,486 bytes / 527 lines, Git blob
ea80b59cca80c6885f6ba1ba4d32b759beb187b5. The uploaded file matches this identity.

## Increment 1: unused shared fields module

The user approved five Storage commits: fields, schema/migration, records/encounters,
campaign/setup/application-state operations, then facade activation. Commits 1-4
stage unused implementation modules and their tests. Commit 5 changes runtime imports.

This increment adds python/scrying_glass_storage_fields.py (984 bytes), containing
TEXT_FIELDS, INT_FIELDS, BOOL_FIELDS, ENTITY_FIELDS, LOG_FIELDS, LIST_FIELDS and
STATE_FIELDS. Assignment expressions, tuple ordering, values and types match the
original. It has no imports, database work or application initialization. Its mutable
STATE_FIELDS set is independent of the original definitions during preparation.
It is not imported by the original storage module or production consumers yet.
The duplicated definitions are temporary staged material, not a competing runtime
configuration. Original storage, SQL, schema version 8, transactions and callers
remain unchanged; this increment alone does not provide a working split runtime.

## Architecture and remaining work

Keep SQLiteStorage in python/scrying_glass_storage.py, retaining connection lifecycle,
constructor, backup/transaction handling and compatibility field exports. Native
Python mixins/modules hold the extracted method groups; no production exec/eval or
source concatenation. Current method-source groups (before new headers/imports):
connection 3,933 bytes, schema/migration 9,760, records/encounters 12,707, operations
11,924. Measure actual complete files before every stage; maximum is 20,000 bytes.

Preserve public imports, method signatures/static decorators, SQL ordering, savepoint
and rollback behavior, migration backups and stable record identities. FeatureStorage
calls underscore-prefixed methods and imports field constants from the original
module. Keep those entry points available. New modules import shared fields rather
than creating a circular import through the facade. Preserve existing lazy feature,
lair, setup-lair and statistics imports. Check module patch/introspection dependencies
before activation. The opening Schema v4 docstring is historical; do not change the
actual SCHEMA_VERSION=8 or introduce a database migration for this refactor.

## Checks and delivery limits

Five new standard-library unittest methods passed locally: original-storage Git blob
identity, field values/types/order, AST assignment equivalence, mutable-set isolation,
and module size/import/export checks. The proposed module and test source compiled.
The tests execute the real staged module and only the original seven AST-extracted
assignments, not the complete storage/application module. No database, migrations,
authenticated server or full-suite execution is claimed. Normal CI discovery picks
up test_storage_fields_preparation.py without workflow changes. CI remains pending
for this preparation increment. Remove/adapt the original-monolith identity guard
and AST comparison at activation, when the facade deliberately replaces that file.

README, existing Admin handover, workflow and consumers were reviewed and are not
changed by this increment: runtime and deployment behavior are unchanged. HANDOVER.md
adds this section link; TODO tracking adds the agreed Storage stages. No package
manifest refresh, archive, workflow dispatch or CI skip is included. Each external
write still needs complete exact-content approval. SG-TODO-004 remains on hold;
SG-TODO-006 UI labels are outside this refactor. Other task close-outs are separate.
