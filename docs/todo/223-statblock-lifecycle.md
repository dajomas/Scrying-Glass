# 223 - Statblock lifecycle integration

[Back to TODO index](../../TODO.md) · [Parent contract](220-admin-statblock-viewer.md) · [Storage handover](../handover/240-sqlite-storage-split.md) · [Validation/history](../handover/030-validation-and-next-steps.md) · [Current counter/rebuild record](../handover/010-scope-and-state.md#02203-counter-only-row-rebuilds---2026-11-15)

## Status and delivery rules - 2026-11-15

SG-TODO-022.03 and overall 022 remain in progress. 022.02 stays accepted/closed.
Stage 1 remains unvalidated/unaccepted. Approved order remains private storage,
recovery/reset/copy, then bundles. Intermediate commits include [skip ci]; only
final Stage 3 code omits it. No workflow edits or separate dispatch. Each external
write requires bound approval, implementation tests and documentation.

## Retained contracts and delivery history

Typed snapshots remain encounter/combatant-scoped and private. Serialized private
input is not trusted. PrivateEncounterState keeps metadata outside ordinary JSON;
deepcopy retains it. Trusted reads use permissive budgets; new preparation/imports
use server limits. Content digests exclude revision/time/self-digest; recovery
fingerprints include metadata. Ordinary omission fails closed; deletion cascades.
No source/provenance promotion, permission change or clearing API is introduced.

- Stage 1: helpers, adapter corrections, ordinary save preservation, private loading
  and response/privacy tests supplied; covering validation/acceptance pending.
- Stage 2 contracts: ten tests at 831c94249de8ef057cdcdbd0ead673d97ef98923,
  not executed, skipped or weakened to claim completion.
- 2A: b1754d78ada3e66780b0b426b8bd70483c4d3f50 captures/loads typed checkpoint
  and undo images with independent ownership, historical metadata and explicit
  empty maps. Ten prepared tests, not executed.
- 2B.1: 1214bed0833ee312f305ce88937dae8f7d60170f adds private-aware recovery
  fingerprints and reconciliation pruning. Nine prepared tests, not executed.
  Full comparison remains unwired; unrelated stale undo digests remain stale.
- 2B.2: 5c8b4776c72a949cbecfef0f00194064a07fdc46 provides a replacement-only
  kernel with exact row/revision binding and atomic writes. Nine prepared tests,
  not executed. Surviving-content clearing remains rejected.
- 2B.3: 8e4d625d7785275c935a3c40b5f45323de329801 wires checkpoint/undo restore
  and live metadata refresh. Seven prepared tests, not executed. Existing protected
  transactions own roster/runtime/audit/history/version persistence and rollback.
  Only a verified immediate undo predecessor may be rebased when restored tracker
  and content checks match; no general stale-history migration exists.
- 2B.4: 1eb80fc389519542daf6f7a2ebfead214347848b adds production writer hooks
  and a ledger prototype. Its custom value_kind is incompatible with the actual
  attribute-table CHECK. Eight earlier isolated passes omitted that constraint and
  are not evidence of a working production ledger. This defect is corrected below;
  the accepted 022.02 schema and its prior CI are not reopened or weakened.
- 2B.5: counter-only encounters now enter guarded setup/runtime preservation.
  Before the plain callback, capture each encounter-local combatant binding/head.
  Stable rows must keep their head; rebuilt destinations must start without private
  ownership. Seed only retained identities, even when no snapshot exists. Unchanged
  reattached content keeps snapshot metadata; changed content advances once from
  the captured head. Reattachment also records the counter atomically. No header
  is invented for counter-only monsters; deletion never transfers counters to new IDs.

## Counter encoding correction

Use existing integer value_kind, integer_value for the counter, and text_value
for the exact private statblock_revision_v1 marker; real_value is null. This fits
the existing CHECK without DDL or migration. The facade hides valid ledger rows,
rejects ordinary reserved-field input, and fails on malformed/colliding markers.
The revised fixture includes the exact allowed value-kind CHECK; a regression
explicitly rejects the old custom kind. Header revisions still bootstrap lazily.
Paired internal read/record hooks are mandatory when either is present. Header-
only legacy protocols remain supported but do not gain durable-counter clearing.

## Validation and remaining work

Executed: eleven exact isolated ledger/rebinding methods against real in-memory
SQLite with the production value-kind constraint. All passed. These exercise
bootstrap/absence, invalid values/decrease/overflow, FK/cascade, hidden decoding/
reserved input, marker corruption, old-kind rejection, rebinding/ownership/partial
protocol guards and rollback. They do not execute the full production adapter save.

Eleven production writer/rebuild methods are prepared, not executed: the original
five writer cases plus setup rebuild/reopen/next revision, runtime/setup isolation,
unchanged/changed snapshot reattachment, late refresh rollback, callback counter
mutation and deleted/new identity separation. Controlled header deletion only
simulates absence; it is not a clear API. All four changed Python sources AST-parse.
Full-package imports, full constructor/model/service, HTTP/WS/browser and covering
CI remain pending. Existing unittest discovery includes the module; workflow read,
not modified or dispatched. Final Stage 3 covering CI remains deferred.

Next 2B: trusted clearing with stale/scope checks and refreshed metadata; arbitrary
private-only transaction comparison/save/refresh; expanded undo/absence/restart/
limits/rollback validation. Explicit-empty recovery still fails closed. All-writer
service integration and 2B/Stage 1/Stage 2 acceptance remain open.

2C: independent setup copy/Save As ownership/revisions, source immutability, move
preservation, canonical references and rollback. 2D: selected/life-filtered import
binding remapping and clone revisions. Stage 3: actual bundle representation,
aggregate/snapshot/member limits, malformed input, untrusted provenance and rollback;
no silent 10 MiB manifest/archive loss. No pending requirement is removed.

Deploy matching complete code/data only after validation/acceptance; schema remains
9. Older code does not apply the new private-attribute filtering/marker rules; do
not roll back code alone. Retain full matching storage/config/media/code backups.
README guidance and existing root index links remain applicable; dated detailed
progress elsewhere is superseded by this lifecycle record, not feature closure.
No viewer/provider/listener, merge/deployment/release or whole-feature acceptance.
