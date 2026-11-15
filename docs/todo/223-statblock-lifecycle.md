# 223 - Statblock lifecycle integration

[Back to TODO index](../../TODO.md) · [Parent contract](220-admin-statblock-viewer.md) · [Storage history](../handover/240-sqlite-storage-split.md) · [Earlier validation/history](../handover/030-validation-and-next-steps.md) · [Current clearing record](../handover/010-scope-and-state.md#02203-trusted-clearing---2026-11-15)

## Status and delivery rules - 2026-11-15

SG-TODO-022.03 and overall 022 remain in progress. 022.02 stays accepted/closed.
Stage 1 remains unvalidated/unaccepted. Approved order remains private storage,
recovery/reset/copy, then bundles. Intermediate commits include [skip ci]; only
final Stage 3 code omits it. No workflow edits or separate dispatch. Every external
write requires bound approval, implementation tests and documentation.

## Retained contracts and history

Snapshots stay encounter/combatant-scoped and private. Serialized private input
is not trusted. PrivateEncounterState keeps metadata outside ordinary JSON and
retains it through deepcopy. Trusted stored reads use permissive budgets; new
preparation/imports use server limits. Digests exclude revision/time/self-digest;
recovery fingerprints include metadata. Ordinary omission fails closed; deletion
cascades. No provenance promotion, new HTTP route or permission policy is added.

Earlier detailed scopes, counts and limits remain in the [pre-clear lifecycle
record](https://github.com/dajomas/Scrying-Glass/blob/da7654059808795880361ae643e6b5523ffc5c0f/docs/todo/223-statblock-lifecycle.md)
and linked handovers. No outstanding requirement is removed by consolidation.

- Stage 1 helpers, adapter/save/loading/privacy wiring are supplied, not accepted.
- Stage 2 contracts at 831c94249de8ef057cdcdbd0ead673d97ef98923 remain unchanged,
  unexecuted, not skipped or weakened to claim completion.
- 2A b1754d78ada3e66780b0b426b8bd70483c4d3f50: typed independent checkpoint/
  undo capture, historical metadata and explicit absence; ten tests unexecuted.
- 2B.1 1214bed0833ee312f305ce88937dae8f7d60170f: private-aware fingerprints/
  pruning; nine tests unexecuted. General private-only comparison remains unwired.
- 2B.2 5c8b4776c72a949cbecfef0f00194064a07fdc46: replacement-only kernel,
  exact bindings and atomic writes; nine original tests unexecuted at delivery.
- 2B.3 8e4d625d7785275c935a3c40b5f45323de329801: production checkpoint/undo
  restoration and live refresh; seven original tests unexecuted at delivery.
  Only a proven immediate undo predecessor can be rebased; unrelated stale history
  stays stale. Existing protected transactions own all surrounding state/DB writes.
- 2B.4 1eb80fc389519542daf6f7a2ebfead214347848b: counter prototype had an
  invalid custom value_kind. Its eight incomplete-fixture passes did not establish
  production compatibility; accepted 022.02 schema/CI was not reopened or weakened.
- 2B.5 da7654059808795880361ae643e6b5523ffc5c0f: fixes encoding using supported
  integer kind, integer_value counter, exact text_value version marker and null
  real_value. Private decoding/input/corruption guards remain. Counter-only setup/
  runtime rebuild preservation and reattachment are supplied. Eleven isolated
  constrained-SQLite ledger/rebinding tests passed; eleven production tests pending.

## 2B.6 trusted clearing

Only restore_encounter with an internal recovery carrier interprets a missing
snapshot for a retained monster as explicit absence. Ordinary adapter/public saves
still reject omission of existing private content; raw JSON cannot grant clearing.
The service still owns campaign/reference/roster authorization and confirmation.

Binding tokens remain two-tuples but now compare stored row ID and highest revision
max(header,counter), including absent content. They are comparison tokens, not
historical snapshot revisions. A clear/re-add/clear cycle therefore invalidates an
old absence token. Row/encounter/combatant scope and the complete binding map are
checked inside the transaction before clearing or tracker changes.

All required clears are preflighted for durable read/allocate/record support and
signed-64-bit overflow. Each clear consumes exactly one revision, records and
verifies its counter, then conditionally deletes the header and cascading typed
children. Counter verification also follows deletion. Missing content is a no-op;
removed monsters use ordinary cascade. Legacy header-only protocols do not clear.
Re-addition allocates beyond the tombstone counter, including after row rebuilds.

Clearing, tracker edits and replacement of other graphs share the existing outer
restoration transaction. The existing service refreshes live metadata from the
saved private map, including empty maps, and protected rollback/broadcast handling
remains. General private-only transaction save integration is not delivered here.

## Validation and remaining work

Executed: six exact isolated ClearSqlTests against real in-memory SQLite and the
native ledger helpers/read-allocation-record methods, with representative headers,
child cascades and the production value-kind CHECK. All passed. They cover counter
advance/idempotence, scope isolation, stale heads, missing hooks, all-clear overflow
preflight, failed-delete rollback and invalid allocator/corrupt-marker rejection.
This is not the real model/facade/service or complete typed-graph integration suite.

Prepared, unexecuted: twelve kernel and nine service methods. Earlier rejection
cases become positive clear/refresh/reload/undo assertions; new tests cover stale
absence cycles, missing allocation, mixed clear/replace rollback, late service
rollback of memory/graph/counter/history without broadcast, and runtime/setup
isolation. The Stage 2 absence contract is unchanged. Three changed Python modules
AST-parse; full package imports, constructor/model/service, HTTP/WS/browser and
covering CI remain pending. Existing unittest discovery includes both test modules.
Workflow identity and README/root index identities were verified against prior
complete reads; no workflow changes or dispatch. Final Stage 3 CI stays deferred.

Next 2B: arbitrary private-only transaction comparison/save/refresh, expanded
scope/restart/limits/undo/rollback validation and covering acceptance. Stage 1/2,
2B and 022.03 are not complete or accepted. 2C independent copy/Save As ownership/
revisions, source immutability, move preservation, references and rollback remain.
2D selected/life-filtered import remapping and clone revisions remain. Stage 3
bundles still need representation, aggregate/snapshot/member limits, malformed/
untrusted input/provenance and rollback; no silent 10 MiB manifest/archive loss.

Schema remains 9 with no DDL/migration. Deploy matching complete code/data only
after validation/acceptance. Older code lacks private-marker/filter handling; do
not roll code back alone. Keep full matching storage/config/media/code backups.
README and root index links remain applicable and unchanged. No viewer/provider/
listener, merge/deployment/release or whole-feature acceptance is implied.
