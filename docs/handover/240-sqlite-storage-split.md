# 240 - SQLite storage source split

[Back to handover index](../../HANDOVER.md)

Updated 2026-11-03. Task: [SG-TODO-008](../todo/080-source-size-refactors.md).
Preparation base: 8ed072c3cd3be53474a77cc9267bd7708f0d7638, features/perplexity.
Original storage remains 39,486 bytes / 527 lines, blob
ea80b59cca80c6885f6ba1ba4d32b759beb187b5; uploaded source matches.

## Agreed architecture and delivered stages

Five commits: shared fields, schema/migration, records/encounters, operations,
then native facade activation. Stages 1-4 are unused preparations; only 5 changes
production imports. No SQL, schema version, backup or behavior change is authorized.

1. a9da32439b01529ab6deba8242b48593d95be594: 984-byte fields module and five local
   preparation tests. Assignment expressions, types, order and values retained;
   STATE_FIELDS remains independently mutable during staging. Blobs verified.
2. 2a651004a7870de461cce32f5dcffd56b91a2aa6: 10,076-byte schema mixin, blob
   ea70b84536f7a4918a6923ae5068d34fe9c85674; _create_schema, static reference
   conversion and _upgrade unchanged. Seven local tests: AST/signatures, base
   schema, empty v1/v2-to-v3 upgrades, rollback after DDL, deep copy/errors and
   source guards. Real SQLite, fixed migration clock. No populated migration,
   constructor, file backups or later upgrades. Field tests were not rerun for 2.
3. 8ed072c3cd3be53474a77cc9267bd7708f0d7638: unused 13,067-byte records mixin;
   ten original methods. Eight local tests cover AST/descriptor, typed fields,
   NULL/presence, IDs/order/deletion, logs/occurrences, runtime setup/turn markers,
   rollback and source guards. Real original base schema, SQLite/FKs, version 3;
   unchanged lair imports, but no v6 persistence branch or effects persistence.
   Original methods were AST-extracted in fixtures. Delivery and five changed paths
   verified after push. Stage 3 superseded an unexecuted malformed approval draft.

No Storage CI result for stages 1-3 has been inspected. Their local checks are not
full application or v8 migration/backup validation.

## Stage 4: unused operations mixin

python/scrying_glass_storage_operations.py: 12,218 bytes, expected blob
9f16de18019464def7e5bea811b711f0dfd7ceda. StorageOperationsMixin contains 20 original
methods for campaigns, rosters, setups and application state. All AST bodies,
signatures, SQL and transaction boundaries match. Dependencies are time and the
existing validate_roster_setup_ids; no circular facade imports, runtime wiring,
constructor changes or production exec/eval. Original storage/callers unchanged.

Eight tests in test_storage_operations_preparation.py passed locally (11,740 bytes;
expected blob 8179a7d80d50a17a45348fb92391b01042ddde4f): method/source guards,
campaign metadata and atomic failure, rosters and nested rollback, setup names/
ordering/updates/deletion, checkpoint rename/conflict rollback, empty setup copy/
move and identity conflict, effect-reference rewriting, and runtime/import-map state.

Fixtures use native original SQLiteStorage methods and a staged test subclass,
bypassing __init__, with original base schema, FKs and user_version=3. The actual
encounter_snapshots CREATE TABLE statement from upgrade_features is added solely
for rename checks; the full v5 upgrade is not run. Empty transfers exercise real
SQLite. The effects rewrite test mocks load_setup/save_setup boundaries and does
not prove effects persistence or full v8 transfer integration. Constructor, backups,
populated migrations, full v8, server/service and combined-facade tests remain pending.
Existing CI unittest discovery includes this test without workflow edits.

## Activation requirements

Next is stage 5. Preserve SQLiteStorage at python/scrying_glass_storage.py with
constructor/lifecycle/backups/transactions and compatibility field exports.
Preserve underscore entry points used by FeatureStorage, lazy feature/lair/
setup-lair/statistics imports, savepoints, backup ordering and stable record IDs.
Keep actual SCHEMA_VERSION=8 despite the old v4 docstring. Check patch/introspection
dependencies; adapt original-monolith/AST guards when activation deliberately
replaces it while retaining behavior checks. Complete code files <=20,000 bytes.
Pre-header group estimates: lifecycle 3,933; schema 9,760; records 12,707;
operations 11,924 bytes. Measure complete final files, not group estimates.

README, HANDOVER index, maintenance rules and workflow were reviewed/reused unchanged:
no runtime/deployment, linked-path or discovery change. Task section and TODO index
reflect progress; SG-TODO-008 stays open. No archive, manifest refresh, CI skip or
workflow dispatch. Each write needs bound approval. Other tasks remain separate:
SG-TODO-004 on hold, SG-TODO-005 reopened, SG-TODO-006 labels not delivered here.
