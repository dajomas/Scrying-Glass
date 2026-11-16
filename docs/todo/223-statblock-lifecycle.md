# 223 - Statblock lifecycle integration

[Back to TODO index](../../TODO.md) · [Parent contract](220-admin-statblock-viewer.md) · [Current handover](../handover/010-scope-and-state.md#02203-save-as-handler-integration---2026-11-16)

## Status and delivery rules - 2026-11-16

SG-TODO-022.03, 2B, 2C and overall 022 remain in progress, not validated or
accepted. 022.02 stays accepted/closed. Stage 1/2 are not accepted. Approved order
remains private storage, recovery/reset/copy, then bundles.

2C.3b was delivered with CI enabled at 812de5ae6717f8a7f34892e0031858a0a3e089c6.
Run 43846424270 attempt 1 failed overall; all six new native save-handler methods
passed. The user now requests one issue per corrective commit, [skip ci] on every
intermediate correction and no skip marker on the final corrective code commit.
No workflow edit or separate dispatch is included. Each write still needs complete
bound approval. Review the final run before claiming corrected integration passes.
Final Stage 3 covering validation remains required; this corrective series is not
Stage 3 or feature acceptance. Documentation-only commits retain [skip ci].

## Retained contracts and archived detail

Snapshots stay encounter/combatant-scoped and private. Serialized private input has
no authority. PrivateEncounterState keeps metadata outside JSON and through deepcopy.
Trusted stored reads use permissive budgets; new preparation/imports use server
limits. Content digests exclude revision/time/self-digest; recovery fingerprints
include metadata. Ordinary omission fails closed; removed combatants cascade. No
provenance promotion, public clear flag, new route or permission is introduced.

[Complete pre-2C.3b lifecycle record](https://github.com/dajomas/Scrying-Glass/blob/13cc61b95fa3e62ec9e1f2a6a85ec0dcff981e5d/docs/todo/223-statblock-lifecycle.md)
and [pre-2C.3b scope/evidence](https://github.com/dajomas/Scrying-Glass/blob/13cc61b95fa3e62ec9e1f2a6a85ec0dcff981e5d/docs/handover/010-scope-and-state.md)
retain full dated implementations, commit identifiers, test counts, failed fixtures,
limits and acceptance gates. [Earlier validation/history](../handover/030-validation-and-next-steps.md)
and [storage history](../handover/240-sqlite-storage-split.md) remain applicable.
This consolidation promotes no result and removes no unfinished requirement.
Earlier CI-deferral wording is historical; the current delivery rule above controls.

Stage 1 helpers/adapter/application/privacy wiring is supplied only in parts, not
accepted. The ten Stage 2 contracts at 831c94249de8ef057cdcdbd0ead673d97ef98923
were unchanged and unexecuted at their recorded delivery, without skips or weakened
preservation assertions. Later CI and caller correction 8 are recorded below; its
Save As invocation now uses the protected workflow and gains four native cases.
No covering green result is inferred from configured discovery or test preparation.

## 2A and 2B retained scope

- 2A: typed independent recovery capture, historical metadata and explicit absence;
  ten prepared production methods pending at delivery.
- 2B.1: private fingerprints/pruning; nine prepared production methods pending.
- 2B.2/2B.3: replacement kernel, exact bindings, service restore/live refresh; current
  kernel/service suites have twelve/nine unexecuted methods in the archived record.
  Only a proven immediate undo predecessor may be rebased; unrelated history stays stale.
- 2B.4/2B.5: CHECK-compatible counter ledger uses integer kind/integer_value, exact
  text marker and null real. Hidden decoding, reserved-input/corruption guards and
  counter-only row rebuild/reattachment preservation remain required. The earlier
  eight incomplete-fixture passes were not production evidence. Eleven isolated
  constrained-SQLite methods passed; eleven production writer methods were pending.

## 2B.6 trusted clearing

Internal recovery-only clearing uses exact row/highest-revision bindings including
counter-only absence, durable tombstones, scope/hooks/overflow preflight, and atomic
graph replacement/deletion. Actual clearing consumes one verified revision; absent
content is a no-op; re-addition advances beyond the tombstone. Header-only protocols
cannot clear. Six isolated SQL methods passed, not full facade/service validation.
Caller authorization, confirmation, roster/runtime/history and outer rollback remain.

## 2B.7 save-decision detection - 2026-11-15

Private-aware state_changed runs after reconciliation with the established character/
setup/runtime save order. Six mock-signature/save/authorization routing methods passed
with a SQLite sentinel, not production graph persistence. Full integration remained
pending. Earlier timeout causes were unconfirmed; the notebook-loop harness fix was
not an application fix. Full dated details remain in the archive above.

## 2B.8 private save and refresh - 2026-11-15

Protected native private flush follows tracker saves and precedes history/revisions.
It resolves the active-campaign setup or unsaved runtime, checks identities, avoids
another tracker write and assigns saved live metadata only after success. Non-native
storage retains its path; standalone persistence is not a public private-write API.
Six production-fixture methods remained unexecuted, with mutation producers corrected
in 2B.9 to remove obsolete self-digests without relaxing validation.

## 2B.9 lifecycle integration - 2026-11-15

Final private signatures queue/coalesce the deferred broadcast, emitted after commit
and history/revision processing. No-op metadata requests no extra emission; rollback
discards it. Trusted loading retains explicit empty metadata; plain input gains no
private authority and invalid maps reject. Eight new production-fixture methods plus
the six 2B.8 methods were unexecuted; older pending suites remain separate. Three
isolated exact empty-carrier boundary methods passed, not native graph/SQLite/service
validation. History, sequential undo, no-op, late rollback, clear/reopen/counter history,
lowered budgets, foreign/missing setup scope, exhaustion and privacy remain gates.

## 2C split and first foundation - 2026-11-15

The user split 2C after reported timeouts; causes remain unconfirmed. Each bounded
delivery retains its own tests/documentation/approval and wider validation duties.
2C.1 is a private clone kernel; 2C.2 is storage copy/move plus protected integration;
2C.3 is Save As. No foundation or prepared suite establishes feature completion.

2C.1 requires distinct schema-9 encounters, matching monster IDs and no destination
snapshots/counter history. Graph/reference/credit rows are independent; destination
revision/time are fresh; source content/counters are unchanged and counter-only
source history is not exported. Caller authorization and outer tracker-creation
atomicity remain required. Four native methods were prepared, unexecuted.

## 2C.2a stored-setup copy - 2026-11-16

Copy-only storage override wraps inherited tracker transfer and clone kernel in one
outer transaction, resolving the actual returned destination name. Existing roster/
campaign checks, naming, effect cleanup and active-reference normalization remain
inherited; non-copy modes delegate. Six native methods were prepared, unexecuted.
Two Python files AST-parsed, existing methods were AST-identical and five isolated
stub routing checks passed, not native transfer/kernel/schema validation.

## 2C.2b move preservation - 2026-11-16

Four native methods were supplied without a production change after static review:
stable setup/encounter/monster ownership, exact graph/counter rows and metadata,
canonical stored runtime references, collision/last-setup isolation, counter-only
reopen/MAX_REVISION, late rollback and source/roster rejection. The module AST-parsed;
all four methods were unexecuted. Static audit is not proof that no fix is needed.

## 2C.2c.1 protected copy - 2026-11-16

Three native-fixture methods were supplied for the actual protected campaign copy
handler, collision naming, live/source isolation, independent destination metadata,
trusted loading, post-clone rollback and injected campaign-gate denial. Five isolated
handler-body checks passed; the native methods remained unexecuted. Injected gates
are not real actor/HTTP authorization. The split continues through 2C.2c.2/2C.2c.3.

## 2C.2c.2 loaded-move detachment - 2026-11-16

The authorized loaded-move branch creates independent unsaved runtime ownership
before changed(), preserving the moved saved setup's owners/content/metadata/counters.
Runtime content starts at revision 1/fresh time; source counter-only history is not
exported. The helper requires an outer transaction and active-campaign reference,
validates trusted state, switches the singleton after fresh persistence and retires
only the superseded exclusively owned runtime encounter. Shared setup/recovery
ownership rejects. Serialized private input rejects; plain state supplies no graphs.
Copy/background paths bypass it; non-native storage keeps legacy reference clearing.
This internal ownership transition adds no ordinary clearing authority.
Four native methods were unexecuted. Nine isolated exact-helper checks passed with
minimal SQLite/stub dependencies, not native graph/schema/service execution.

## 2C.2c.3 transfer boundaries - 2026-11-16

Six methods were supplied, not executed: four native boundary/history/revision/
notification/rollback/checkpoint/privacy methods and two selected-route ASGI methods.
ASGI fixtures use production request models, route registration, AuthService,
ownership and SQLite, with seeded sessions rather than login. Cases cover missing
sessions, wrong roles, source/target ownership, origin/mode rejection, owner and
superadmin copies, loaded moves, actor cleanup and response privacy. Notification
observation uses a deferred-emitter seam, not actual socket delivery. The module
AST-parsed; no native/HTTP/authorization pass was claimed. Earlier pending integration,
full-server/browser/socket and acceptance requirements remain.

## 2C.3a new-destination Save As kernel - 2026-11-16

save_new_setup is internal/native schema-9 only. Caller authorizes canonical campaign/
name and supplies the existing setup projection. Trusted live content, including
unsaved edits, is used rather than older stored source data. Existing destinations
reject; source revision/time are stripped; tracker/private writes are atomic and
saved independent metadata is returned. Plain input contributes no graphs; serialized
private fields reject. Source/input state is not changed. Four native methods were
supplied, unexecuted; both Python files AST-parsed. The original kernel-only delivery
had no handler wiring; 2C.3b below supplies it without promoting earlier validation.

## 2C.3b save-handler integration - 2026-11-16

Status: delivered at 812de5ae6717f8a7f34892e0031858a0a3e089c6; six native methods
passed in the failed CI run below. Wider validation and acceptance remain pending. save_setup_with_private is called by the existing save handler
after authorization/active-campaign checks. New native destinations use 2C.3a.
Existing same-owner saves retain source revision/stale checks; different-owner
overwrites remove incoming revision/time so the existing destination's owner and
durable counter history govern the write. Surviving private omission rejects rather
than clears. Plain state preserves existing destination metadata without importing
source private authority. Non-native storage retains its legacy save path.

The native helper requires the protected outer transaction and active campaign.
The handler saves the roster, updates active/last-setup references, then refreshes
live private metadata from the destination result before changed() and final flush.
Existing wrapper rollback covers later roster/reference/live failures. No new route,
permission, schema, import or clearing authority is added.

Six native methods cover saved/unsaved-source Save As with live edits/reload, ordinary
no-op/stale saves, overwrite revision continuity/source isolation, omission rejection
and rollback after roster writes or live refresh. They passed in run 43846424270
attempt 1; they were unexecuted at preparation. Helper,
changed handler method and native module AST-parsed. Ten isolated exact-helper checks
with simplified SQLite/JSON bindings and stub facade/capture/kernel/private adapter,
plus five stub handler routing/order checks passed. These fifteen passes are not
native graph/schema, full-module, protected integration or HTTP validation. An initial
handler harness failed for a missing asyncio import; the corrected harness passed.

At preparation the execution environment lacked checkout/test files and FastAPI;
GitHub exposed no runner/dispatch tool here. Existing workflow discovery covered
the new test filename. Later published CI establishes six native method passes,
not an overall passing run or acceptance. Corrective execution is tracked below. [Handover](../handover/010-scope-and-state.md#02203-save-as-handler-integration---2026-11-16).

## CI correction series - 2026-11-16

In progress. Baseline HEAD 355598a1a571095b7f2bde58637a1fe2249bfd05 publishes
Branch tests 43846424270 attempt 1 for implementation 812de5ae6717f8a7f34892e0031858a0a3e089c6.
Main unittest: 1,896 tests, three failures, fourteen errors. Workflow reader parts
135-146 contain the failures; part 130 explicitly records all six 2C.3b methods OK.
The standalone connection audit reports 211 modules, six failed; observed duplicate
test failures do not by themselves establish leaks. Existing historical pending
notes describe delivery-time execution, not a claim that no CI has since run.

Planned separate corrective commits; no assertion skipping or validation weakening:

1. Request forwarding: delivered at 4935fddbcdf14fe241ed052f4f81ff63275b4370,
   validation pending. Reuse an existing Request parameter for post-lock auth and
   ownership rather than exposing a second injected Request. Preserve requestless
   injection, positional/keyword invocation and unchanged transaction processing.
   Eight isolated exact-wrapper checks passed with Request/ownership doubles;
   old duplicate-injection failure reproduced. AST checks passed. The first notebook
   runner hit an already-running-loop error; the same checks passed in a thread.
   FastAPI is absent locally; no native/ASGI or corrected CI pass is claimed.
   [Diagnosis, scope and evidence](../handover/140-viewer-ownership-fixtures.md#client-request-forwarding-correction---2026-11-16).
2. Service AST extraction harness: delivered at 293376ea594eadb8077f97c1b076f7b36b3d1cd1.
   Restored module/package globals and added two regressions, retaining all nineteen
   original tests. Twenty-one checks passed in a selected-method/extracted-dependency
   reconstruction; original harness reproduced seven errors and disabled pruning
   failed the new pruning check. Native package imports and CI remain pending.
   [Evidence and limits](../handover/140-viewer-ownership-fixtures.md#service-ast-harness-correction---2026-11-16).
3. Snapshot AST extraction harness: delivered at d68cccc128c8444d7fd6b917d7970820e857a17f.
   Corrected module/package context and transaction fixture. Original sixteen snapshot
   checks reproduced two context errors; context alone exposed two transaction errors.
   Nineteen corrected checks passed against four inspected method bodies and an unused
   decoder double; disabling the row guard made the added invalid-load check error.
   Three new regressions preserve original assertions and test rollback/seed retention.
   WebSocket tests are AST-unchanged, not rerun here. Native imports, graph/transaction
   integration and CI remain pending.
   [Evidence and limits](../handover/140-viewer-ownership-fixtures.md#snapshot-ast-harness-correction---2026-11-16).
4. Revision-test mutation producer: delivered at c69db3b112cf675ac9ba0c6c08afcc2fa2b7e904.
   Removed obsolete content_digest before mutation, retained all four original rebuild
   assertions and added label/digest checks plus a native stale-digest rejection test
   for unchanged SQL, tracker HP and counter/header revisions. Both changed methods
   compile/AST-parse; four isolated digest calculations passed, not production
   validation/persistence. Native tests and final CI remain pending; strict production
   digest validation is unchanged.
   [Evidence and limits](../handover/140-viewer-ownership-fixtures.md#revision-test-digest-mutation-correction---2026-11-16).
5. Facade mocked-copy boundary: delivered at 5109e0c152d99a2e2c9e33101c43e0e0739ced9c.
   Explicit plain-mixin effect-cleanup unit retains both original assertions and adds
   exact call/name/input checks. Separate private-facade missing-binding rejection
   regression checks zero clone calls, unchanged SQL, no destination and closed
   transaction. Two isolated checks passed; old failure reproduced and bypassing
   the guard failed the new regression. Native facade/graph/schema and CI remain
   pending; production guards and dispatch expectations were not changed.
   [Evidence and limits](../handover/140-viewer-ownership-fixtures.md#mocked-copy-boundary-correction---2026-11-16).
6. Facade copy fixture: delivered at c093d772513051f5c88623af1b72c63d89cde19a.
   Opt-in real schema-9 constructor branch leaves base/legacy schema-3 callers unchanged.
   Copy/move checkpoint seeding uses the real snapshot writer, retaining original
   assertions. Added native fixture-separation and post-private-clone rollback methods.
   Four changed/added methods compile/AST-parse; four isolated routing/version/nested-
   SQL-rollback checks passed with constructor/legacy doubles. Native constructor,
   checkpoint capture, graph copy/rollback, complete module and CI remain unexecuted.
   Production guards and dispatch pin were unchanged by correction 6.
   [Evidence and limits](../handover/130-accounts-migration-fixture.md#native-and-legacy-storage-fixture-separation---2026-11-16).
7. Facade dispatch expectation: delivered at f2d4fa699e2ef1a56d56332e4c37a0d94057f8d6.
   Current statblock module and save/transfer/runtime identities are asserted; native
   real-hook spy regression added. Original five source guards and exact loop body/
   20,000-byte limit remain, extended to the active statblock storage module. Both
   changed/added methods compile/AST-parse; six controlled class/file guard checks
   passed. Native hook, actual repository budgets/AST, full module and CI remain pending.
   No production code or behavior changed.
   [Evidence and limits](../handover/130-accounts-migration-fixture.md#facade-dispatch-guard-correction---2026-11-16).
8. Save As contract: prepared explicit change from raw tracker save to the protected
   admin save workflow; no new lower-level private-write authority. All four original
   content/revision/source assertions remain, with owner/live-reference/reload checks
   and four new native cases for live edits, raw/forged-input boundaries, inactive
   campaign denial and late-reference rollback. Other original methods, including
   the still-required import-remapping assertion, are AST-unchanged. Complete proposed
   module compiles (fourteen methods). Five isolated helper/handler routing checks
   passed with transaction/private doubles, not native graphs, rollback or real auth.
   All changed/added native contracts and final CI remain unexecuted for this correction.
   [Decision and evidence limits](../handover/130-accounts-migration-fixture.md#save-as-contract-entry-point-correction---2026-11-16).
9. Private setup-import remapping: imported monster lacks its new private binding;
   pending implementation with selected/life-filtered mapping, independent revisions,
   rollback and privacy coverage. Planned final corrective commit enables CI.

Issues 1-7 are delivered; only issue 8 is prepared in this delivery. Correction 9
is not supplied. The final corrective push will omit [skip ci] and its run must
be reviewed. No manual dispatch, workflow edit, 2C.3c/2D completion, bundle work,
final Stage 3 validation or feature acceptance is implied by this sequence or by
a future green configured suite. New failures need diagnosis and fresh approval.

## Remaining gates and delivery order

- 2B: execute/review relevant suites; retain scope/restart/limits, sequential undo,
  rollback, private projections, clear/reopen/tombstones, late notifications and
  exhaustion checks. Correct failures; reconcile acceptance. 2B.9 did not close 2B.
- 2C: execute/review all clone, copy, move, protected-transfer and Save As suites;
  correct failures in 2C.1/2C.2a/2C.2b/2C.2c.1-3/2C.3a-b. 2C.3c still requires combined
  protected Save As/copy/move, recovery/history/revision/notifications/privacy,
  authorization and acceptance reconciliation. Verify independent ownership,
  destination revisions, source immutability, canonical references and rollback.
- 2D: selected/life-filtered import remapping and independent clone revisions remain.
- Stage 3: actual bundle format/roundtrip, aggregate/snapshot/member limits,
  malformed/untrusted input, provenance and rollback; no silent 10 MiB manifest/
  archive loss. Final covering validation and every parent criterion remain required.
- Stage 1/2, 022.03 and the overall viewer/import feature remain unaccepted. CI may
  expose known unfinished later-scope contracts; do not skip/weaken them for a pass.

Schema stays 9; no migration/DDL. Deploy matching complete code/data only after
validation/acceptance. Older code lacks marker/filter handling: do not roll code
back alone over ledger-bearing data. Keep matching storage/config/media/code backups.
README/root index links remain applicable. No viewer/provider/listener, merge,
deployment, release or whole-feature closure is implied.
