# 240 - SQLite storage source split

[Back to handover index](../../HANDOVER.md)

Updated 2026-11-03. Task: [SG-TODO-008](../todo/080-source-size-refactors.md).

**Reversed 2026-11-22** by SG-TODO-035 ([handover 760](760-remove-file-size-splitting.md)):
fields, schema, records and operations are back in `scrying_glass_storage.py`. This page is
history.
Corrective preparation base: 2e5d1d4ecedc3e88fa5bd3a565e49fbaa11660fb, features/perplexity.

## Delivery and architecture

The five stages were delivered:
1. Fields: a9da32439b01529ab6deba8242b48593d95be594.
2. Schema/migration: 2a651004a7870de461cce32f5dcffd56b91a2aa6.
3. Records/encounters: 8ed072c3cd3be53474a77cc9267bd7708f0d7638.
4. Operations: 0c8f1c9a95763bf8729d775f4596de68835cabf6.
5. Activation: 266487f8d8b605610db11e837f3f26fcdfc7f7f3.

Stages 1-4 were unused preparations; stage 5 activates native mixins behind the
4,710-byte SQLiteStorage facade. Five lifecycle, three schema, ten record and twenty
operation methods retain their original bodies/signatures/decorators/SQL. Seven
field expressions retain their values/types/order. Reference: original 39,486-byte
blob ea80b59cca80c6885f6ba1ba4d32b759beb187b5. SCHEMA_VERSION=8, transactions,
savepoints, backups, lazy migrations, compatibility exports and callers remain.
STATE_FIELDS is the shared runtime export. Stage-module staging comments are
historical provenance; the facade activates their methods. All five source files
are below 20,000 bytes (records is actually 13,068 bytes, including final whitespace).

## Manual validation and inspected CI

On 2026-11-03 the user reported the Admin click-by-click runbook completed
successfully. This is user-reported manual evidence, not an assistant execution or
a claim about unspecified optional checks. Final task closure still requires CI.

Evidence at ci-results-41602398857-attempt-1, committed in
2e5d1d4ecedc3e88fa5bd3a565e49fbaa11660fb, identifies Branch tests run
41602398857 attempt 1, head 266487f8d8b605610db11e837f3f26fcdfc7f7f3, completed/failure.
Setup/dependencies and syntax/server import passed. Main unittest ran 1,004 tests
with 12 failures, all at Storage reference AST pins before the guarded fixture
bodies. The inspected v1/v2 upgrade tests and new file-backed v8 persistence/reopen
and constructor-cleanup tests passed. Pytest and JavaScript steps report success.
Standalone connection audit reran 1,004 tests with the same 12 failures; it reported
652 connections and zero without explicit close. Log-clear and round-3 audits
reported passes; browser smoke reported no page errors with mocked HTTP/WS and real
Chromium rendering. These are not full authenticated live-server browser checks.

## AST fixture correction prepared

The test oracle used ast.dump formatting to calculate fixed hashes. Python 3.14 CI
omits optional empty lists that the local 3.12 format included. This was reproduced
locally with an available 3.14 interpreter on the verified original source. Both
method and field hashes differed despite unchanged AST semantics. This explains
why the manual run and runtime tests passed while reference guards failed.

Replace only the test helper canonical serializer with explicit recursive AST/list
serialization matching the original format. Preserve optional empty lists, semantic
values and nonempty type parameters; omit location attributes, optional None
defaults and empty type_params as before. METHOD_PIN and FIELD_PIN remain unchanged;
no accepted hashes, production code, schema, workflow or assertions are weakened.

Four new regression methods passed on Python 3.12 and 3.14 (eight test executions):
original 38-method/seven-field pins and reference class with real base SQLite,
independence from ast.dump/line numbers, semantic-value/nonempty-type-parameter
sensitivity, and rejection of deliberately changed SQL/field definitions in copied
fixtures. They used methods reconstructed from the verified original source, not a
full application checkout. Full corrected workflow has not run or passed locally.
Normal CI discovers the new test automatically; no workflow changes or skip.

Historical activation preparation: eleven consolidated fixture tests plus native
dispatch and constructor cleanup passed locally on 3.12, not proof of cross-version
pins. Fixtures use base v3, limited rename tables and mocked effect boundaries;
complete migrations/services/feature coverage belongs to the configured CI suites.

## Deployment and remaining acceptance

Deploy the complete matching python/ tree with facade, all four support modules and
__init__.py, and restart the single process; do not deploy the facade alone. Existing
README deployment/backup instructions remain applicable. No new migration or special
conversion was introduced. This corrective draft changes tests/documentation only.

README, HANDOVER index/maintenance rules and workflow were reviewed or identity-
verified unchanged; paths and runtime commands remain valid. No archive, manifest
refresh, workflow dispatch or CI skip. Keep SG-TODO-008 open until corrected exact-SHA
CI is reviewed and remaining Admin/oversized-source acceptance is addressed.

## Statblock storage foundation - 2026-11-15

[022.02b staged task](../todo/222-statblock-persistence.md) · [Parent contract](../todo/220-admin-statblock-viewer.md).
The user approved foundation then startup activation as separate commits. This
section supersedes progress notes saying all 022.02b work is pending; it does
not reopen the historical SG-TODO-008 task or change approved statblock scope.

New python/scrying_glass_statblock_storage.py contains the seven typed relations,
upgrade_statblocks(storage, backup=True), and internal StatblockStorage.save/load.
Storage is a protocol providing connection, transaction, backup and FK-check
helpers. IDs here are stored monsters.id integers, not public combatant IDs.
Future callers must resolve campaign/encounter identity and authorization.
Validation/canonicalization and complete metadata-size checking happen before
the save transaction. Expected revision 0 means missing; replacements increment
the current matching revision and are atomic, including nested rollback. Six SG
display fields are never written by this API. Optional-field presence uses a
scalar bitmask; provenance credits are separate ordered rows, not JSON columns.
Local IDs are canonicalized; same-snapshot definition and same-owner node-parent
constraints use composite deferred FKs, with null-safe unique ordering indexes.
Flat reference cycles remain supported. Load validates integrity/digest using
permissive read budgets so lowered preparation defaults do not erase accepted
saved content. Private read/API response budgets and authorization remain future
integration responsibilities, not guarantees made by this internal layer.

No imports/callers were added to SQLiteStorage, services, runtime state, public
projections or UI. Normal application startup still creates/opens schema 8;
only an explicit call on an existing schema-8 connection creates schema 9. It
reuses an earlier upgrade-chain backup when present, checks FKs, and rolls back
the new DDL/version on failure. Do not manually upgrade deployed storage before
stage-two matching constructor code and full storage/config/media backups are
available: the current constructor rejects schema 9. A database-only automatic
backup is not a complete installation backup. Rollback restores matching code
and data, not a lowered PRAGMA. Existing facade/runtime behavior is unchanged.

Validation: four SchemaTests in tests/test_statblock_storage.py passed during
preparation against real file-backed SQLite protocol fixtures. They cover v8
backup, v9 reopen/idempotence, invalid versions, injected DDL rollback, null-owner
uniqueness, cascades and cross-owner/snapshot constraints. Four RepositoryTests
are prepared for model-integrated round trips, revisions, references, lowered
limits, tracker independence and replacement/outer rollback; these have not been
run locally. Neither fixture class is the production SQLiteStorage constructor
or a complete legacy database. Both classes are discoverable by configured CI;
full CI and its connection audit remain pending for this new delivery. No live
server, browser, provider or migration-on-deployed-data test is claimed.

Previously reviewed 022.02a covering Branch tests 43707384985 attempt 1 succeeded
at 0ed81a834d0973179c2c030eb84bb36b35c7e325; that is not a run for this foundation.
Next review foundation CI, then deliver startup activation/version guards and
real fresh/legacy/reopen/backup/failure fixtures. 022.03 retains runtime, setup,
recovery, undo/checkpoint, copy and bundle preservation. The parent remains in
progress; no whole-feature or migration activation completion is claimed.
README runtime/backup guidance and HANDOVER index links remain accurate and are
unchanged. TODO index/addendum record the approved split in this same commit.
Normal push CI applies; no skip marker or separate workflow dispatch.

## Activation preparation A - 2026-11-15

Foundation CI is now reviewed: Branch tests 43709292836 attempt 1 completed
successfully for 4a3f930cb4a0df109b06259bd9ca9a23f01638ee. Main Python ran
1,704 tests OK including all eight statblock-storage methods, and all configured
stages passed. Evidence exists at ci-results-43709292836-attempt-1. This
supersedes foundation-CI-pending notes above, not their coverage limitations.

At 13:00 CET the user authorized direct GitHub fixture-preparation commits with
[skip ci] until the final code activation commit. The activation task is now
delivered as bounded preparations followed by one final startup change, rather
than the originally proposed single large second commit. See the staged task
for outstanding lair/feature, attack-backup and final activation work.

This preparation adds tests/storage_migration_fixtures.py and five regression
methods in tests/test_storage_migration_fixtures.py. The helper temporarily
suppresses only upgrade_statblocks during disposable legacy-fixture construction,
verifies schema 8 with no statblock tables, restores the function and closes
invalid results. It neither deletes statblock data nor changes production
migrations. Use it only in single-threaded tests. The setup-lair v6 test now
recreates a pre-statblock fixture before removing v7/v8 additions; its later
reopen is unpatched and still exercises production upgrades. Backup checks now
assert version 6 and absence of statblock tables in the pre-upgrade copy.

Local checks executed: AST parsing of the new helper/test modules and four
FixtureHelperTests passed with real SQLite in-memory connections and an isolated
stub migration target. These verify helper control flow, rejection/close and
patch restoration only. The fifth production-constructor test and changed
setup-lair tests have not been run locally. No full-checkout, actual startup-
activation, browser, provider or fresh hosted CI execution is claimed.

This intermediate commit includes the exact [skip ci] marker by user instruction;
no workflow is changed or separately dispatched. Full validation is deferred to
the final activation commit, whose message must omit [skip ci]. Application
startup and SCHEMA_VERSION remain 8. TODO status stays in progress; no activation
or whole-feature completion is claimed. README and HANDOVER index links remain
accurate; TODO's existing persistence entry links to the updated staging record.

## 022.03 Stage 1 private adapter - 2026-11-15

[Lifecycle task and approved staging](../todo/223-statblock-lifecycle.md).
022.02 remains accepted/closed at 30b8dc0885eb8445189a3520330c4f88e1da00ec;
its schema-9 activation and green run 43713643326 attempt 1 are not changed or
relabelled validation of this new work. Earlier schema-8 notes above are history.

This first Stage 1 increment adds an opt-in PrivateEncounterStorage adapter and
recursive public_payload utility, plus six tests. It uses a private `_statblocks`
map keyed by encounter-scoped monster combatant IDs, canonical typed snapshots,
transactionally captured old bindings and metadata-preserving reattachment when
rows are rebuilt. Plain callbacks permit later nonrecursive hooks. Ordinary
saves preserve revisions; actual replacements increment them. Graph validation
precedes writes; failures roll back tracker edits and content. Explicit omission
of a surviving snapshot fails closed; deletion of its monster still cascades.

The adapter is trusted internal tooling, not an authorization/import budget
boundary. Defaults allow stored content accepted under earlier larger operator
limits; untrusted preparation/import callers must supply validated server limits.
Projection tests verify the utility, not existing HTTP/WebSocket privacy wiring.
No ordinary storage/service/API/transport caller is changed yet. Stage 1 wiring,
service-path/privacy regression coverage and covering CI remain pending. Neither
Stage 1, 022.03 nor the viewer/import feature is complete. Schema remains 9.

Tests were prepared/reviewed but have not been executed locally. Normal configured
CI applies to this code commit, without [skip ci], workflow changes or separate
dispatch. Runtime behavior and README descriptions remain unchanged; existing
HANDOVER index links remain valid. TODO index and the new indexed lifecycle task
record this partial delivery and all remaining stages rather than claiming closure.

## 022.03 helper restaging - 2026-11-15

This increment adds opt-in normalization/projection helpers and four focused
repository tests. It validates separately supplied private snapshots against
normalized monster IDs and keeps them outside tracker records. Ordinary input
cannot supply the reserved envelope. Response projection recursively strips it
without mutating source payloads. These utilities are not production wiring,
authorization, trusted stored-state policy, or adapter corrections. See the
[lifecycle task](../todo/223-statblock-lifecycle.md) for remaining Stage 1 gates.

The four tests are prepared, not executed; earlier stub experiments do not
validate these exact tests or the live model. Prior conversation overstated that
evidence. Adapter revision/digest and row-ownership concerns still require
verification against the real repository before fixes or integration are claimed.

The user's 14:14 instruction supersedes earlier normal-CI wording for remaining
intermediate 022.03 pushes: include [skip ci] until the final Stage 3 code push,
which must omit it. No workflow modification or separate dispatch. Validation
and acceptance remain pending. Earlier blocked helper writes changed no files.
README runtime guidance and existing index links remain applicable and unchanged.

## 022.03 adapter correction preparation - 2026-11-15

Helper delivery: 34d9d417246ebff4c3481056d425ef2bbd54f6a7. The next increment
removes the adapter's save-then-UPDATE revision repair after monster-row rebuilds.
A private reattachment routine now validates and inserts final metadata and typed
children under the existing transaction after combatant ownership checks. Unchanged
rebuilt content uses the original snapshot metadata; changed content advances the
logical revision once. Explicit stale revisions fail before tracker writes.

Review of the real model corrects an earlier claim: its digest excludes revision,
prepared_at and content_digest, so revision patching alone did not corrupt it. The
existing adapter is encounter-scoped already; separate setup/runtime rows require
careful integration, not a guessed shared owner. Existing ownership guards remain.

Six added tests target final metadata without UPDATE, changed rebuild revision,
stale rejection, equal combatant IDs in separate encounters, tracker-only metadata
preservation, and reattachment rollback. Both proposed Python modules passed AST
parsing (adapter 7,769 bytes; tests 4,145 bytes). These tests were not executed; no
SQLite/model/service/HTTP/WebSocket/browser or CI pass is claimed. CI remains
deferred by user instruction until the final Stage 3 code push.

This increment is still opt-in: no application/service/response/transport wiring,
new schema, migration, viewer or provider work. Stage 1 and 022.03 remain open.
README runtime guidance and existing handover/TODO index links remain unchanged.

## 022.03 production save wiring - 2026-11-15

The adapter correction was delivered as 7c721a5586bdc7a582edbb6467d1b0d0f1c4c6dc.
This increment activates StatblockOperationsMixin in SQLiteStorage. Ordinary
setup and runtime saves preserve existing encounter-bound snapshots, including
row rebuilds, under the existing transaction. The plain records callback remains
unchanged, avoiding adapter recursion; schemas before 9 bypass private handling.
The no-content path retains plain storage behavior. Legacy missing monster IDs
are allocated in a private copy when preservation requires adapter validation.

Read API shapes remain plain. Reserved _statblocks input is rejected by ordinary
setup/runtime saves, so untrusted imports cannot acquire a new private-write path.
No service private-state loading, authoritative setup fallback, restart integration,
copy/restore/bundle behavior, response-boundary activation or UI is claimed.
Normal monster deletion still cascades within the selected encounter.

Six prepared production-storage regression methods exercise setup/runtime rebuilds,
private-input rejection, legacy IDs, rollback and encounter-local deletion. AST
parsing passed for the new mixin (3,544 bytes) and test file (5,172 bytes). These
tests were not executed; no full-constructor/migration/service/HTTP/WebSocket or
CI success is claimed. Final Stage 3 CI remains pending under the user's deferral.
No workflow change, separate dispatch, schema change, deployment or merge.

Deploy the matching complete python tree: the facade now imports the new storage
mixin as well as the existing adapter/model/storage modules. README already
requires the complete tree and remains accurate; index links remain unchanged.
Stage 1 and 022.03 remain in progress. Earlier unwired notes are historical and
superseded only for ordinary setup/runtime save preservation by this increment.

## 022.03 production private loading - 2026-11-15

Save-preservation baseline: c76f2e1a6ccf85b3a172418839ba8db7c6104d45.
PersistenceService now uses trusted setup/runtime loaders and carries validated
private metadata through its normalization paths. Setup authorization precedes
reads. SQLite resolves the exact owner and checks tracker/private consistency
inside a transaction. Empty-runtime setup fallback takes both monsters and
metadata from that setup; nonempty runtime retains runtime metadata. Failed
restoration does not replace STATE. Loading an import source has no live-state
side effect. Non-SQLite test doubles retain the plain storage protocol.

PrivateEncounterState is dict-compatible with a private _statblocks attribute,
not a serialized dictionary key or monster field. Deepcopy retains this metadata,
ordinary JSON and existing public/display projections do not expose it. This
loading-only representation differs from the opt-in adapter's explicit map; it
is not a new untrusted write channel or complete lifecycle serialization format.
Trusted read validation uses permissive stored-content budgets, not current
untrusted preparation defaults. No provider/network fallback or new auth policy.

Seven service tests are prepared for setup/privacy/deepcopy, fallback, runtime
precedence, unsaved restart/save, reduced-default compatibility, failed reads,
and source-load isolation. The helper and test source AST-parse. Tests were not
executed; no real service/model/SQLite/HTTP/WebSocket/browser/CI pass is claimed.
Existing JSON recovery, copy/Save As, out-of-path normalization and bundles do
not yet preserve this attribute; Stage 2/3 must explicitly handle those cases.
Do not describe the feature or Stage 1 as complete or ready for deployment.

The lifecycle TODO is consolidated with explicit retained remaining gates and
commit history. Existing handover history, README runtime guidance and index
links remain unchanged. Deploy matching complete python files only after the
staged feature's required validation/acceptance. This intermediate commit uses
[skip ci]; final Stage 3 covering CI and acceptance remain pending.
