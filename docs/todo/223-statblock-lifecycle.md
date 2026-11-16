# 223 - Statblock lifecycle integration

[Back to TODO index](../../TODO.md) · [Parent contract](220-admin-statblock-viewer.md) · [Storage history](../handover/240-sqlite-storage-split.md) · [Current handover](../handover/010-scope-and-state.md#02203-lifecycle-integration---2026-11-15)

## Status and delivery rules - 2026-11-15

SG-TODO-022.03, 2B and overall 022 remain in progress, not validated or accepted.
022.02 stays accepted/closed. Stage 1 remains unvalidated/unaccepted. Approved
order remains private storage, recovery/reset/copy, then bundles. Intermediate
commits include [skip ci]; final Stage 3 code omits it. No workflow edit/dispatch.
Every external write needs bound approval, relevant tests and documentation.

## Retained contracts and archived detail

Snapshots stay encounter/combatant-scoped and private. Serialized private input
has no authority. PrivateEncounterState keeps metadata outside JSON and through
deepcopy. Trusted stored reads use permissive budgets; new preparation/imports
use server limits. Content digests exclude revision/time/self-digest; recovery
fingerprints include metadata. Ordinary omission fails closed; deletion cascades.
No provenance promotion, public clear flag, new HTTP route or permission change.

[Complete pre-2B.9 lifecycle record](https://github.com/dajomas/Scrying-Glass/blob/a1230d9ebf945ef3f2cdad202bbad68a5f504279/docs/todo/223-statblock-lifecycle.md)
and [earlier validation/history](../handover/030-validation-and-next-steps.md)
preserve detailed historical scopes, counts, failures and acceptance gates.
This consolidation removes no pending requirement and promotes no earlier result.

- Stage 1 helpers/adapter/save/loading/privacy wiring: supplied, not accepted.
- Stage 2 ten contracts at 831c94249de8ef057cdcdbd0ead673d97ef98923: unchanged,
  unexecuted, not skipped or weakened to claim completion.
- 2A b1754d78ada3e66780b0b426b8bd70483c4d3f50: typed independent recovery
  capture, historical metadata and explicit absence; ten prepared tests pending.
- 2B.1 1214bed0833ee312f305ce88937dae8f7d60170f: private fingerprints/pruning;
  nine prepared tests pending. Full save-decision wiring followed in 2B.7.
- 2B.2 5c8b4776c72a949cbecfef0f00194064a07fdc46 and 2B.3
  8e4d625d7785275c935a3c40b5f45323de329801: replacement kernel, exact bindings,
  service restore/live refresh. Original nine/seven methods unexecuted at delivery;
  current kernel/service suites have twelve/nine pending methods. Only a proven
  immediate undo predecessor may be rebased; unrelated stale history stays stale.
- 2B.4 1eb80fc389519542daf6f7a2ebfead214347848b had a CHECK-incompatible
  custom value_kind; eight incomplete-fixture passes were not production evidence.
- 2B.5 da7654059808795880361ae643e6b5523ffc5c0f corrected the encoding to
  supported integer kind, integer_value counter, exact text marker and null real.
  Hidden decoding/reserved-input/corruption guards and counter-only row rebuild/
  reattachment preservation are supplied. Eleven isolated constrained-SQLite
  ledger/rebinding methods passed; eleven production writer methods remain pending.
  Accepted 022.02 schema/CI was not weakened or reopened.

## 2B.6 trusted clearing

f38d7c3a4ba86f45dfbf167b25da189f3825c152 supplies internal-recovery-only clearing.
Exact row/highest-revision bindings include counter-only absence, preventing stale
clear/re-add/clear tokens. Scope, durable hooks and overflow preflight all clears;
each consumes one verified counter revision before conditional header/graph delete.
Already-absent content is a no-op; removed monsters cascade; re-addition advances
beyond the tombstone, including after row rebuilds. Legacy header-only protocols
cannot clear. Six isolated SQL clear tests passed; full facade/service tests did not.
Caller authorization, confirmation, roster/runtime/history and outer rollback remain.

## 2B.7 save-decision detection - 2026-11-15

4bf95480f2670adda80d798fa73aefe2a7ed58e7 wires private-aware state_changed after
reconciliation, preserving character/setup/runtime save order. Six mock-signature/
save/authorization routing methods passed with a SQLite sentinel, not real private
persistence. Full imports/integration remain pending. Reported earlier timeouts
were not diagnosed. The earlier notebook-loop harness was corrected, not production.

## 2B.8 private save and refresh - 2026-11-15

a1230d9ebf945ef3f2cdad202bbad68a5f504279 flushes private changes after protected
tracker saves and before history/revision processing. Native SQLite resolves the
active-campaign setup or unsaved runtime, checks identities and uses a no-op plain
callback to avoid rewriting tracker rows. Live metadata is assigned after success.
Non-native storage keeps its path; standalone persistence is not a new private-write
API. Caller authorization/preparation and separate trusted clearing remain.
Six production-fixture methods remain unexecuted. 2B.9 corrects their mutation
producers to remove obsolete self-digests; validation itself is not weakened.

## 2B.9 lifecycle integration - 2026-11-15

Status: code and regression preparation supplied; functional validation/acceptance
pending. Final saved private signatures now queue the existing deferred broadcast,
even when the handler made no notification request. This merges with an already
pending request and emits only after commit and history/revision processing.
No-op final metadata does not request an extra broadcast; rollback discards it.
Trusted loading retains an explicit empty carrier instead of dropping absence on
reload. Plain sources still gain no private authority, and invalid maps reject.

New coverage: eight unexecuted production-fixture methods for fresh history/digest/
revision plus committed notification/privacy, sequential private undo, no-op
history/revision/notification, failure after history writes, clear/reopen/undo and
counter history, lowered preparation defaults, missing/foreign setup scope and
revision exhaustion. Together with the six 2B.8 methods, fourteen production
methods in these two modules await execution; older suites remain separately pending.

Executed: three exact empty-carrier boundary methods in an isolated function-body
harness. All passed. It used the carrier/carry/empty-map validation bodies and an
unused budget-policy stub; it did not execute graph validation, native imports or
SQLite/services. The new integration module AST-parses. No complete-module import,
production integration, authenticated HTTP/WS/browser or covering CI pass is claimed.
Existing unittest discovery includes the module. Earlier passes are historical,
not rerun or relabelled. [Current evidence](../handover/010-scope-and-state.md#02203-lifecycle-integration---2026-11-15).

## 2C split and first foundation - 2026-11-15

The user requested splitting 2C after a timeout and starting the first part. The
cause of the timeout is not established. Each following delivery still needs its
own complete approval payload, relevant tests and documentation.

- 022.03-2C.1: clone-kernel foundation supplied, validation pending. Internal helper
  only; not called by public setup copy/move or Save As in that increment. Source/
  destination must be distinct schema-9 encounters with matching monster IDs.
  Destination snapshots and counter-only history are rejected. Source graphs/
  counters remain unchanged; copies get independent rows, revision 1 and fresh
  preparation time. Counter-only source history is not exported. Caller authorizes
  both encounters and wraps tracker creation with this transaction for an atomic copy.
- 022.03-2C.2: in progress, split further after reported timeouts. 2C.2a supplies
  storage-copy wiring; 2C.2b supplies move-regression preparation, with functional
  verification pending. 2C.2c supplies protected-copy tests, loaded-move detachment
  and cross-cutting regression preparation below. Covering validation and acceptance
  remain pending. Preserve roster/campaign validation, canonical references, source
  immutability and rollback throughout. No partial delivery establishes acceptance.
- 022.03-2C.3: planned, follows 2C.2. Wire Save As and destination live-metadata
  refresh, then test combined copy/move/Save As flows and reconcile acceptance.

Four focused production-fixture methods are prepared, not executed: graph/reference/
credit independence and fresh metadata, same/mismatched/owned target rejection,
counter-only source isolation, and partial-write/outer-tracker-creation rollback.
Both new Python files AST-parse. No full imports, actual kernel test pass, public
service/HTTP/browser validation or CI run is claimed. Existing discovery includes
the new module. [Scope/limits](../handover/010-scope-and-state.md#02203-clone-kernel-foundation---2026-11-15).

## 2C.2a stored-setup copy - 2026-11-16

Status: implementation and six production-fixture methods supplied; functional
validation and acceptance pending. StatblockOperationsMixin now overrides only
copy routing: resolve campaign-scoped source, call the inherited tracker transfer,
resolve the returned destination name, and invoke the 2C.1 clone helper inside one
outer transaction. Existing naming, roster validation, cross-campaign effect cleanup
and active_setup normalization remain inherited. Non-copy modes delegate unchanged.
Caller authorization remains required; no new route, permission or clear authority.

Prepared coverage: same/cross-campaign independent graphs and fresh revisions/time,
source immutability after destination edits, complete rollback after graph writes,
roster conflicts, plain/counter-only sources, missing/wrong-campaign source, effect
cleanup and destination-name collisions. Tests reuse the native encounter and 2C.1
reference-graph fixtures. Both Python files AST-parse; the three pre-existing mixin
methods are AST-identical. Five isolated exact-override routing checks passed with
a stub parent/clone and minimal SQLite tables, not the real transfer, clone kernel
or native schema. The six production-fixture methods are unexecuted. Workflow
unittest discovery covers the filename; no workflow changes, dispatch or run claim.
[Handover](../handover/010-scope-and-state.md#02203-stored-setup-copy---2026-11-16).

## 2C.2b move preservation - 2026-11-16

Status: regression implementation supplied; functional verification and acceptance
pending. Static review of the inherited transfer, upsert writer, private adapter and
counter mixin found no demonstrated gap requiring a production-code change. Moves
reparent the existing setup binding; unchanged snapshots take the adapter's no-write
path and counter attributes are preserved. This audit is not a runtime test pass.

Four native-fixture methods are prepared in test_statblock_setup_move.py: same/cross-
campaign moves with stable setup/encounter/monster IDs, raw graph/counter rows and
complete metadata; canonical stored runtime references and unaffected collision
target/last-setup binding; counter-only moves through reopen including MAX_REVISION;
late post-save rollback for graph-bearing and counter-only sources, including source
last-setup restoration; missing/wrong-campaign source and roster-conflict rejection.
Guards fail if a move calls the clone helper or snapshot writer. The module AST-parses;
the four methods are unexecuted. Discovery includes the filename. No native functional,
full-import, protected service, HTTP/browser or CI success is claimed. Schema, runtime,
permissions and workflow are unchanged. [Handover](../handover/010-scope-and-state.md#02203-move-preservation-regressions---2026-11-16).

## 2C.2c.1 protected copy - 2026-11-16

Status: regression implementation supplied; native validation and acceptance pending.
After the reported 2C.2c timeout, the user requested a split and the first delivery.
The cause remains unconfirmed. The protected handler already delegates copy to
2C.2a storage wiring; inspection does not justify a speculative production change.

- 2C.2c.1: three native-fixture methods in test_statblock_protected_setup_copy.py
  exercise the actual campaign handler through transactional_handler: collision
  naming, stable source/live metadata, independent destination ownership and fresh
  metadata, trusted destination loading, rollback after the real clone writes, and
  injected denial at either campaign gate before storage transfer.
- 2C.2c.2: loaded-setup moves and detached runtime private ownership/metadata,
  binding safeguards and focused rollback implementation are supplied below;
  functional validation remains pending.
- 2C.2c.3: cross-cutting transfer/history/notification/privacy and selected real-ASGI
  authorization regression implementation is supplied below; execution, corrections
  and acceptance remain pending. Save As stays in 2C.3. No earlier gate is removed.

The new module AST-parses; all three native-fixture methods are unexecuted. Five
isolated exact-handler-body checks passed with stub context/storage for copy,
target/source denial, missing source and transfer failure. These checks execute no
protected wrapper, native persistence or real ownership/HTTP authorization. Existing
workflow unittest discovery includes the filename; intermediate [skip ci] defers
covering CI to final Stage 3. No workflow edit/dispatch or observed run result.
[Handover and limits](../handover/010-scope-and-state.md#02203-protected-copy-regressions---2026-11-16).

## 2C.2c.2 loaded-move detachment - 2026-11-16

Status: implementation and four native-fixture methods supplied; functional
validation and acceptance pending. The existing authorized loaded-move branch calls
an internal helper before changed(). The moved setup retains its encounter, monster
owners, graphs, metadata and counters. The live battle stays in the active source
campaign but becomes unsaved, with a newly allocated runtime encounter and independent
private rows at revision 1/fresh preparation time. Source counter-only history is not
exported. This avoids comparing source revisions with obsolete same-ID runtime data.

The helper requires the protected outer transaction and an active-campaign reference.
It validates trusted carrier content; plain state supplies no snapshots and serialized
private input rejects. The singleton binding is switched only after fresh runtime
persistence; the superseded runtime encounter is deleted with owned child rows.
Shared setup/recovery ownership rejects before allocation/deletion. Live assignment
follows helper success; the existing wrapper rolls back move, runtime replacement
and memory on later failure. This is an internal ownership transition, not ordinary
snapshot clearing or a public replacement API. Non-native storage keeps legacy
reference clearing; copy and background moves do not call the helper.

Prepared tests cover stale same-ID runtime history, collision naming, moved-owner
preservation, independent runtime editing/reopen, absent/MAX_REVISION source counters,
late rollback, shared binding rejection and background-move routing. Helper and
native-test module AST-parse. Nine isolated exact-helper checks passed using minimal
SQLite tables and stub facade/private writer/capture for trusted/plain/empty state,
missing outer transaction, foreign reference, shared setup/recovery, serialized
input and writer failure. They are not native graph/schema/service validation; all
four native methods remain unexecuted. No full imports, authenticated HTTP/browser
or CI success is claimed. Existing discovery includes the new module; no workflow
edit/dispatch. [Handover](../handover/010-scope-and-state.md#02203-loaded-move-detachment---2026-11-16).

## 2C.2c.3 transfer boundaries - 2026-11-16

Status: six regression methods supplied; native/ASGI execution and acceptance pending.
No production-code change is justified by the present static review. Four native
methods exercise the actual protected transfer handler and feature processing for:
copy boundary undo clearing without live-state/revision/notification changes;
checkpoint preservation; loaded-move final revision and saved runtime metadata at
one post-commit emission; copy/move rollback after real history processing; and
409 rejection of pre-move checkpoints whose source setup is now missing. Private
source labels, reference text and serialized private fields must stay out of
responses, admin/display projections and JSON-encoded carrier state.

Two selected-route ASGI methods use real FastAPI, AdminAPI.register_routes filtered
to the existing transfer route, the production request model, AuthService, ownership
checks, transaction wrapper and SQLite. In-memory sessions are seeded, not obtained
through login. Cases cover missing sessions, client roles, source/target ownership
denials, cross-origin requests, invalid mode, owner copies/loaded moves, superadmin
copy, actor cleanup and response privacy. Denials assert no storage transfer or
persistent/live-state change. This is not a full-server/login/password/listener,
browser or WebSocket fixture; the native notification test uses a deferred-emitter
seam rather than real socket delivery.

The module AST-parses. All four native and two ASGI methods are unexecuted; no
functional, HTTP, authorization or covering CI pass is claimed. Existing unittest
discovery covers the new filename. No workflow edit/dispatch; intermediate [skip ci]
retains final Stage 3 covering CI deferral. Execute/review these and earlier suites,
correct failures and reconcile acceptance; supplying tests does not close 2C.2c,
2C or 022.03. [Handover](../handover/010-scope-and-state.md#02203-transfer-boundary-regressions---2026-11-16).

## Remaining gates and delivery order

For 2B: execute/review the relevant suites and outstanding scope/restart/limits/
undo/rollback/privacy checks, correct failures and reconcile acceptance evidence.
2B.9 does not establish 2B completion merely by supplying code/tests. Stage 1/2
and 022.03 are also not accepted. Covering CI stays deferred to final Stage 3 code;
no separate dispatch or observed workflow-run status is claimed here.

2C: execute/review 2C.1/2C.2a/2C.2b/2C.2c.1/2C.2c.2/2C.2c.3 tests, correct any
failures, finish Save As 2C.3 and covering validation of independent copy/Save As
ownership and destination revisions, source immutability, move preservation,
canonical references and rollback. Partial delivery closes none of these wider gates.
2D: selected/life-filtered import remapping and independent clone revisions. Stage 3:
actual bundle format/roundtrip, aggregate/snapshot/member limits, malformed/untrusted
input, provenance and rollback; no silent 10 MiB manifest/archive loss. Retain every
parent criterion.

Schema stays 9, no migration/DDL. Deploy matching complete code/data only after
validation/acceptance. Older code lacks marker/filter handling: do not roll code
back alone. Keep matching storage/config/media/code backups. README/root index
links remain applicable. No viewer/provider/listener, merge/deployment/release or
whole-feature closure is implied.
