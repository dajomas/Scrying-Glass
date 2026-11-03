# 240 - SQLite storage source split

[Back to handover index](../../HANDOVER.md)

Last updated: 2026-11-03. Task: [SG-TODO-008](../todo/080-source-size-refactors.md).
Preparation base: 2a651004a7870de461cce32f5dcffd56b91a2aa6 on features/perplexity.
Original storage: 39,486 bytes / 527 lines, Git blob
ea80b59cca80c6885f6ba1ba4d32b759beb187b5; the uploaded source matches.

## Architecture and delivery

The user approved five commits: fields, schema/migration, records/encounters,
campaign/setup/application-state operations, then native facade activation.
Commits 1-4 stage unused modules and tests; only commit 5 changes runtime imports.

Increment 1 was delivered as a9da32439b01529ab6deba8242b48593d95be594: 984-byte
fields module and five preparation methods, with post-push blob verification.
The original assignment expressions, ordering, values and scalar types remain;
STATE_FIELDS is an independent mutable set during preparation.

Increment 2 was delivered as 2a651004a7870de461cce32f5dcffd56b91a2aa6:
10,076-byte StorageSchemaMixin, blob ea70b84536f7a4918a6923ae5068d34fe9c85674.
_create_schema, static convert_campaign_references and _upgrade are AST-equivalent.
Seven preparation methods passed locally: AST/signatures, base-schema parity,
empty v1/v2-to-v3 upgrade parity, post-DDL rollback, reference deep copy/errors,
and size/dependency/original-source guards. Real SQLite was used with a fixed
clock for migration-log comparison. Constructor, backups, populated legacy data
and later v4-v8 upgrades were not executed. Increment-1 tests were not rerun for 2.
No Storage CI result has been inspected for either delivered increment.

## Increment 3: unused records/encounter mixin

python/scrying_glass_storage_records.py is 13,067 bytes, expected Git blob
c0632d7c34ceac8089f54e541299df396dc4af62. StorageRecordsMixin contains the original
ten methods: _typed, _attributes, _read_attributes, _save_entities, _load_entities,
_save_log, _load_log, _save_lists, _save_encounter and _load_encounter. AST bodies,
signatures, _typed static descriptor, SQL and call ordering remain unchanged.
Top-level dependencies are uuid and shared fields; lazy feature/lair imports stay
in their original methods. No constructor changes, runtime wiring or production
exec/eval. Original storage and all callers remain authoritative and unchanged.

Eight methods in tests/test_storage_records_preparation.py passed locally against
the proposed module (9,396 bytes; expected test blob
5564bcb16b97a591a71ae37f833e3fee7986158d). Tests cover AST/signatures/descriptor,
scalar tags and rejection, entity presence/NULL/order/IDs/deletion, log updates and
IDs, repeated ordered IDs/occurrences, runtime reference/marker round trips,
partial-write rollback and validation, and size/dependency/original-blob guards.

Fixtures use the original AST-extracted base-schema/transaction/check helpers and
real in-memory SQLite with foreign keys enabled and user_version=3. Existing lair
modules are imported unchanged, not stubbed; their v6 persistence branch is not
executed. No feature/lair mocks, fabricated schema or global sys.modules changes.
These checks do not execute the constructor, file backups, effects/lair persistence,
later migrations or full application integration. Full suite/CI remains pending.
The earlier malformed empty-bound approval was not executed; this corrected draft
supersedes it, including replacement of the earlier limited test draft.

## Remaining work and compatibility

Next: operations (4), native facade activation (5). Keep SQLiteStorage in
python/scrying_glass_storage.py with constructor, lifecycle, backups/transactions
and compatibility field exports. Complete new files must stay <=20,000 bytes.
Original method-group sizes before headers/imports: connection 3,933, schema 9,760,
records 12,707, operations 11,924 bytes. Measure complete modules at each stage.
FeatureStorage imports old field constants and calls underscore methods: retain
these entry points. Avoid circular facade imports. Preserve lazy feature/lair/
setup-lair/statistics imports, savepoints, rollback, backup ordering and record IDs.
Check patch/introspection dependencies before activation. The old v4 docstring
never changed actual SCHEMA_VERSION=8. Adapt monolith/AST guards at activation
while retaining behavioral tests. Obtain final validation/acceptance before closure.

README, HANDOVER.md and workflow were reviewed and left unchanged for increment 3:
runtime/deployment, index links and test discovery are unaffected. Relevant task
and TODO index statuses are updated. No archive, manifest refresh, workflow dispatch
or CI skip. Each write needs exact bound approval. SG-TODO-004 stays on hold;
SG-TODO-005 and SG-TODO-006 work and acceptance remain separate.
