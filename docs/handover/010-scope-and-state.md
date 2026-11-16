# 010 - Scope and current state

[Back to handover index](../../HANDOVER.md)

Last updated: 2026-11-16. Dated sections below retain their historical scope.

## Repository and branch

- Repository: `dajomas/Scrying-Glass`.
- Default working branch: `features/perplexity`.
- SG-TODO-022 explicitly uses `features/perplexity-statblock`; all work for that task stays there.
- Keep changes scoped to the agreed branch unless explicitly requested otherwise.

## Initial workflow record - 2026-11-01

The Branch tests workflow was added at `.github/workflows/tests.yml` in commit
8465afc86d19340a91433f6d4d7c4112de504a23. At the time of that initial handover
the first run had not been verified. Later feature-specific evidence and limits
are recorded in the corresponding numbered sections; this entry is not a complete
application audit.

## Application context

Scrying Glass is a self-hosted encounter manager with separate FastAPI Admin and
Client applications in one process, SQLite persistence and WebSocket updates.
The root entry point is scrying_glass_server.py. Runtime dependencies are in
requirements.txt; Python, Node and browser fixtures are under tests/.

## Documentation and packaging maintenance - 2026-11-03

The user accepted the Admin and Storage refactors as done. The live size audit at
9703102f1929aedd1887c17f1d7b4a8996dfc04b found no code files above the agreed
25,000-byte existing-file allowance. Temporary CI logs are excluded from refactor
targets and are not deleted by this maintenance. SG-TODO-004's subsequent
cancellation is recorded below.

Technical-Documentation.md is an index to three files under docs/technical/, all
below 20,000 bytes. The draft split reconstructed the exact 31,226-byte source
blob 7f9861b62a11c6efeb82fcb286f5abe300f4db2e and checked 25 compatibility links.
The text and historical validation limits are preserved, except for the required
relative-link rebasing; it is not a fresh technical audit. Preservation/link
regressions accompany the split. README and deployment guidance are refreshed as
current entry points; historical detail remains in Git and numbered feature handovers.

Manifest-dependent verification is retired. deployment/check.py now performs
runtime preflight by default, accepting --runtime as a compatibility alias. It
checks Python/sqlite3/dependencies and server import, not package integrity, live
startup or authenticated workflows. Four mocked contract methods passed locally;
this is not real dependency installation/server validation. The split regression
module parsed successfully; full repository CI was not rerun.

The user approved two commits with [skip ci]: first this documentation/preflight/
test delivery, then a separately confirmed deletion of the unused manifest. The
physical presence of any legacy manifest is not a dependency of the new tooling.
No separate workflow is dispatched, and this skip request is limited to those two
maintenance commits. No application runtime or storage behavior is changed.

## SG-TODO-004 cancelled - 2026-11-03

After a user-requested integration-options review, the user concluded that none
of the investigated approaches were viable for this project and explicitly
requested cancellation. [SG-TODO-004](../todo/040-dndbeyond-account-access.md) is
cancelled, not completed; older hold/deferred references are historical and
superseded by that decision. Its archived requirements and unfulfilled acceptance
criteria are preserved. No account-backed implementation or live account
verification was started, and no credentials were collected or account accessed.
Do not resume this work without a new explicit user request.

The delivered public-provider candidate selection, imports and manual entry remain
unchanged. This is a documentation-only cancellation: no code/test/workflow/data
changes, no automated tests executed and no new CI result claimed. The user
explicitly requested [skip ci] for this cancellation push; no workflow is
separately dispatched. The TODO index now contains seven completed tasks and one
cancelled task, with none active or on hold.

## SG-TODO-022 model foundation - 2026-11-15

Historical model/preparation details, original test scopes and limitations are
preserved in the [pre-rebuild current-state record](https://github.com/dajomas/Scrying-Glass/blob/1eb80fc389519542daf6f7a2ebfead214347848b/docs/handover/010-scope-and-state.md).
The model-only delivery supplied validation, canonical IDs/content digests and
limits, not a usable viewer. Its schema-8/pending-persistence wording is historical.
022.02 model/storage/startup is now accepted and closed, with reviewed activation
CI 43713643326 attempt 1 for 28d75d08febf5b595afe8145b4097410eb987986 and the
user's 13:48 CET sign-off. [Accepted record](../todo/222-statblock-persistence.md).
The approved display, model, ownership, limit and backup contracts remain binding.

## Activation preparation B - 2026-11-15

Historical preparation B: a44727ef76f810ab593305033947c84eb9af26ae, lair-v5 and
feature-v4 fixtures, backup/account/FK checks, no claimed local production pass.
Full details remain in the linked pre-rebuild record. Later activation evidence
and acceptance supersede its pending status, not its recorded evidence limits.

## Activation preparation C - 2026-11-15

Historical preparation C: 1ccd5c36afb88a99b812b79bacd5a63c7c194654, attack-v7
backup and cleanup fixtures; three isolated resource-lifetime tests passed, not
full startup or hosted CI. Full details remain in the linked pre-rebuild record.
Later accepted activation supersedes its pending status. Existing anchors remain.

## 022.03 counter-only row rebuilds - 2026-11-15

da7654059808795880361ae643e6b5523ffc5c0f corrected 2B.4's CHECK-incompatible
counter encoding and supplied counter-only setup/runtime rebuild preservation.
Supported integer rows use the exact private marker; no schema weakening or DDL.
Eleven isolated constrained-SQLite methods passed; eleven production writer methods
remain pending. The earlier eight incomplete-fixture passes were not production
proof. [Complete pre-2B.9 record](https://github.com/dajomas/Scrying-Glass/blob/a1230d9ebf945ef3f2cdad202bbad68a5f504279/docs/handover/010-scope-and-state.md)
preserves all detailed decisions, evidence limits and previous dated scopes below.
No unfinished requirement or acceptance gate is removed by this consolidation.

## 022.03 trusted clearing - 2026-11-15

f38d7c3a4ba86f45dfbf167b25da189f3825c152 supplies trusted recovery clearing with
scope/highest-revision bindings, durable tombstone counters, preflight and atomic
graph deletion/replacement. Ordinary omission has no clearing authority. Six
isolated SQL methods passed, not full graph/service tests. Twelve kernel and nine
service methods remain unexecuted. See the complete record and current task.

## 022.03 save-decision detection - 2026-11-15

4bf95480f2670adda80d798fa73aefe2a7ed58e7 supplies private-aware save detection
after reconciliation. Six mock-signature/save/authorization routing tests passed
with a SQLite sentinel; actual graph persistence/imports were not established.
Earlier timeout causes were not determined. The notebook-loop harness correction
was not a production change. Full dated limits remain in the archived record.

## 022.03 private save and refresh - 2026-11-15

a1230d9ebf945ef3f2cdad202bbad68a5f504279 adds the protected native private flush
after tracker saves and before history/revision processing, exact encounter/monster
selection, a no-op tracker callback and saved live metadata. Standalone persistence
is not a new private API; caller authorization/preparation and trusted clear rules
remain. Six production-fixture tests remain unexecuted. Their content-mutating
producers are corrected in 2B.9 without relaxing digest validation.

## 022.03 lifecycle integration - 2026-11-15

Baseline: a1230d9ebf945ef3f2cdad202bbad68a5f504279. The wrapper now queues the
existing deferred broadcast when final saved private metadata differs from the
original image, even without a handler notification. Requests coalesce and emit
only after history/revision processing and commit; rollback discards them. Trusted
carry/load preserves explicit empty metadata, fixing absence loss on reload;
plain input does not gain private authority. Model/digest validation is unchanged.

Eight production-fixture regression methods are prepared, unexecuted: committed
history/revision/notification and privacy, sequential undo, no-op behavior, failure
after history writes, clear/reopen/undo counter continuity, lowered preparation
budgets, missing/foreign setup scope and revision exhaustion. The six corrected 2B.8
methods are also unexecuted; existing older suites retain their pending status.
Three exact empty-carrier methods passed in an isolated function-body harness with
an unused budget-policy stub, exercising no graph validation, SQLite/services or
full module imports. The new integration module AST-parses. No covering integration,
authenticated HTTP/WS/browser, CI success or 2B acceptance is inferred.

[Current contracts, delivery order and acceptance gates](../todo/223-statblock-lifecycle.md).
Root README/HANDOVER/TODO and workflow identities match prior complete reads; they
remain unchanged. Existing unittest discovery includes the new module. No workflow
edit/dispatch; intermediate [skip ci] and final Stage 3 covering CI deferral remain.
2B/Stage 1/Stage 2/022.03 are not validated or accepted. 2C/2D, bundles, failure
corrections and acceptance remain; earlier clearing-disabled notes are historical.
Schema remains 9. Deploy matching complete code/data only after validation and
acceptance; do not roll old code alone over ledger-bearing data. Keep matching
storage/config/media/code backups. No viewer/provider/listener, merge/deployment/
release or whole-feature closure is authorized.

## 022.03 clone-kernel foundation - 2026-11-15

Baseline: 68ec127ea8e974ba3cdf582f38d2f5fc4223af6e. After the reported 2C timeout,
the first bounded part supplies only an internal clone helper and four focused
production-fixture tests, not setup transfer or Save As wiring. Existing source/
destination encounters must have matching monster IDs and distinct ownership;
any destination snapshot or counter history rejects. The helper validates stored
source content and copies graphs/references/credits through the existing writer,
starting verified destination revisions at 1 with fresh preparation times. It
copies no source counter history and never writes source tracker rows or metadata.
Caller authorization and outer atomic tracker creation remain caller duties.

Both new Python files AST-parse. The four methods cover independent graph ownership/
source immutability, fresh metadata, target guards, counter-only isolation and
partial/outer rollback; they are prepared, not executed. No constructor/full-import,
actual SQLite/kernel, service/HTTP/browser or CI pass is claimed. Existing discovery
includes the module. [Staged plan and remaining requirements](../todo/223-statblock-lifecycle.md#2c-split-and-first-foundation---2026-11-15):
2C.2 wires setup copy/move; 2C.3 wires Save As/live refresh and combined regressions.
Each needs its own approved delivery. Root README/index/workflow identities remain
unchanged; no workflow edit/dispatch. Intermediate [skip ci], schema 9, code/data
backup rules and pending covering validation/acceptance remain. This foundation
closes neither 2C nor 022.03; earlier 2B validation is not promoted.

## 022.03 stored-setup copy - 2026-11-16

Baseline: d4d286d062e76b891992f01c160216b6786af1af. 2C.2a supplies a copy-only
override in StatblockOperationsMixin. It resolves the source campaign/name binding,
runs the inherited transfer unchanged, resolves its returned destination name and
calls the trusted clone kernel inside an outer transaction. Clone failure therefore
rolls back destination tracker creation and private writes together. Existing roster
checks, name collision handling, cross-campaign effect cleanup and active_setup
normalization remain inherited. Non-copy modes delegate directly; this is not move
verification, protected-service integration or Save As delivery. Caller authorization
remains unchanged. Earlier no-copy-wiring descriptions retain their dated scope.

The prepared module contains six native-fixture methods for independent same/cross-
campaign copies, source immutability, fresh metadata, late graph-write rollback,
roster conflicts, absent/counter-only sources, source-scope failures, effect cleanup
and collision naming. They are unexecuted. Both files AST-parse; the three existing
mixin methods are AST-identical. Five isolated exact-override routing checks passed
with a stub parent transfer/clone and minimal SQLite tables; they do not establish
real transfer/kernel/native-schema success. Workflow discovery includes the new
filename; no complete-module import, service/HTTP/browser or CI pass is claimed.

[Remaining scope and validation gates](../todo/223-statblock-lifecycle.md#2c2a-stored-setup-copy---2026-11-16):
2C.2b move preservation, 2C.2c protected service integration, 2C.3 Save As and earlier
2B/2C validation remain open. README and root indexes were reviewed and left unchanged;
no workflow edit/dispatch or run status check. Intermediate [skip ci], final Stage 3
covering CI, schema 9 and matching code/data backup rules remain. Neither 2C.2a nor
2C/022.03 is accepted merely by supplying this code and its tests.

## 022.03 move-preservation regressions - 2026-11-16

Baseline: e4473d93fcb9f2bf3033442bf70e141e5ce7e9a3. 2C.2b supplies four native-
fixture regression methods, with no production-code change. Static inspection of
transfer_setup, the upsert writer, private adapter's unchanged-content path and
counter mixin found no demonstrated production gap; execution may still reveal one.
The tests assert retained setup/encounter/monster ownership, exact private graph/
counter rows, revision/preparation metadata, canonical stored runtime references,
collision-target isolation, counter-only continuity through reopen at normal and
maximum revisions, and late rollback of graph-bearing/counter-only moves including
source last-setup binding. They also cover source-scope and destination-roster rejection
and fail if a move invokes the clone helper or snapshot writer.

The module AST-parses; all four production-fixture methods remain unexecuted.
No actual move verification, full-module import, service/HTTP/browser or CI pass is
claimed. Existing discovery includes the module; no workflow edit/dispatch or run
status check. README/root indexes remain accurate for this regression-only scope
and are unchanged. [Current gates](../todo/223-statblock-lifecycle.md#2c2b-move-preservation---2026-11-16)
retain 2C.2c/2C.3 and earlier integration execution/corrections/acceptance. No schema,
runtime, permission, release/deployment or acceptance change; intermediate [skip ci]
and final Stage 3 covering CI remain. This delivery does not close 2C.2b or 022.03.

## 022.03 protected-copy regressions - 2026-11-16

Baseline: 0e246ca8b464bc178cdeca6db0be33ca0afdf5fe. Following the reported
2C.2c timeout (cause unconfirmed), delivery is split into protected-copy tests
(2C.2c.1), loaded-move/runtime preservation (2C.2c.2), then cross-cutting rollback,
history/revision/notification/privacy and real actor/HTTP authorization (2C.2c.3).
Save As remains 2C.3; earlier acceptance and validation requirements are retained.

2C.2c.1 supplies three native-fixture methods using the actual campaign handler
through transactional_handler: copy with collision naming, stable source/live
metadata, independent destination ownership and fresh metadata, trusted destination
loading, rollback after the real clone has written, and injected source/target
campaign-gate denial before storage transfer. The existing copy handler already
delegates to 2C.2a storage wiring; no production-code change is included. Gate
injection tests routing, not actual actor authorization or an authenticated request.

The module AST-parses; all three production-fixture methods are unexecuted. Five
isolated exact-handler-body checks passed using stub context/storage for copy,
target/source denial, missing source and transfer failure. They do not execute the
protected wrapper, native persistence or real ownership/HTTP authorization. An
initial notebook event-loop harness error was corrected by running the isolated
harness in a worker thread; no application change was made. Full module/native
execution and any demonstrated fixes remain pending.

[Current split and gates](../todo/223-statblock-lifecycle.md#2c2c1-protected-copy---2026-11-16).
Existing unittest discovery includes the new filename. README and root indexes
remain accurate and unchanged. No workflow edit/dispatch or run-status check;
intermediate [skip ci], final Stage 3 covering CI, schema 9 and matching code/data
backup rules remain. No loaded-move/Save As delivery, new route, permission,
release/deployment or whole-feature acceptance is implied.

## 022.03 loaded-move detachment - 2026-11-16

Baseline: 32252413e88ed97cd51e7b33f747e82a86528eac. 2C.2c.2 wires only the
existing moving_loaded_setup branch to an internal detachment helper before
changed(). Authorization and storage transfer remain inherited. The saved setup
moves with its encounter/monster owners, graphs, counters and metadata intact.
The still-live source-campaign battle becomes unsaved and receives independent
runtime ownership, revision 1 and fresh preparation time; counter-only source
history is not exported. Old same-ID runtime content can otherwise have unrelated
revisions or explicit-absence conflicts, so it is not an ordinary destination save.

The helper requires an outer transaction and active-campaign setup reference,
validates trusted carrier graphs, strips source revision/time for the new writer,
persists fresh runtime tracker/private content, switches the singleton, and retires
the superseded runtime encounter with owned children. It rejects old runtime owners
shared with saved setups or recovery images before allocation/deletion. Plain state
supplies no private snapshots; serialized private input rejects. Live assignment
follows nested success; existing protected rollback restores the transfer, runtime
binding/content and memory after later errors. No ordinary clearing authority is
added. Non-native storage keeps legacy clearing; copies/background moves bypass it.

Helper and test-module AST parsing passed. Nine isolated exact-helper checks passed
with minimal SQLite and stub facade/private writer/capture: trusted/plain/empty
state, no outer transaction, foreign reference, shared setup/recovery, serialized
input and writer failure. A missing-copy-import harness error was corrected, not
production. These checks do not exercise the actual schema/model/graph writer,
service wrapper or full imports. Four native-fixture methods are prepared and
unexecuted for stale same-ID runtime, moved ownership/collision isolation, runtime
edit/reopen independence, absent/MAX_REVISION source history, late rollback, shared
binding rejection and background routing. No native/HTTP/browser/CI pass is claimed.

[Remaining gates](../todo/223-statblock-lifecycle.md#2c2c2-loaded-move-detachment---2026-11-16)
retain 2C.2c.3, Save As 2C.3 and all earlier validation/corrections/acceptance. Earlier
loaded-move-delivery-pending wording is superseded only for this bounded increment.
README/root indexes remain accurate and unchanged; discovery includes the new test
module. No workflow edit/dispatch or run-status check. Intermediate [skip ci], final
Stage 3 covering CI, schema 9 and matching code/data backup rules remain; no viewer,
new route, permissions, merge/deployment/release or whole-feature closure.

## 022.03 transfer-boundary regressions - 2026-11-16

Baseline: 9400b9b60563e679bffe6fdd1cfa710c7bf30ed1. 2C.2c.3 supplies six
regression methods, not an additional production-code change. Static review of
feature boundary processing, protected transactions, the route registrar and real
session/ownership checks found no demonstrated gap requiring another speculative
fix. Execution may still reveal defects; this increment establishes no acceptance.

Four native methods prepare coverage for copy undo-boundary clearing with unchanged
live state/revision/no emission, checkpoint preservation, loaded-move final revision
and saved runtime metadata at one post-commit emission, full rollback after actual
copy/move history processing, missing-source pre-move checkpoint rejection, and
privacy of responses/admin/display/JSON carrier projections. Notification observation
uses a deferred-emitter seam, not actual WebSocket delivery.

Two real-ASGI methods filter AdminAPI.register_routes to the existing transfer route,
using production CampaignSetupAdd, AuthService session/role checks, ownership scope,
transaction wrapper and native SQLite. Seeded in-memory sessions for admin/client/
superadmin users exercise absent session, wrong role, foreign source/destination,
cross-origin and invalid-mode rejection with no transfer/write; owner copy and loaded
move plus superadmin copy assert response privacy and actor cleanup. This prepares
selected authenticated endpoint coverage, not login/password, full server startup,
listeners, browser or socket verification. No test is skipped or weakened to claim
completion.

The module AST-parses. All four native and two ASGI methods are unexecuted; there is
no native, HTTP/authorization, full-import or CI pass. Existing workflow discovery
includes the filename; no workflow edit/dispatch or run-status check. README/root
indexes remain accurate and unchanged. [Current gates](../todo/223-statblock-lifecycle.md#2c2c3-transfer-boundaries---2026-11-16)
retain execution/review/corrections for all earlier increments, Save As 2C.3, bundles
and covering validation/acceptance. Earlier 2C.2c.3-delivery-pending descriptions are
superseded only for regression preparation. Intermediate [skip ci], final Stage 3
covering CI, schema 9 and matching code/data backups remain. Neither 2C.2c, 2C nor
022.03 is accepted or closed by supplying these tests.

## 022.03 Save As kernel - 2026-11-16

Baseline: bfea8bb3ae4234c3fe1689607ac9b6e05e4be1a2. At the user's request,
2C.3 is split into 2C.3a internal new-destination kernel, 2C.3b existing-handler/
live-metadata integration and ordinary-save/overwrite distinctions, then 2C.3c
combined protected regressions and acceptance reconciliation. Earlier gates remain.

2C.3a supplies save_new_setup in python/scrying_glass_statblock_save_as.py for native
schema 9. Caller owns authorization, canonical names and the existing setup projection.
The helper validates trusted live carrier graphs, not potentially stale stored source
content, strips source revision/time, rejects existing destinations and atomically
saves tracker rows plus independent destination-private content. It returns saved
metadata for later service refresh without changing the source/input state. Plain
input contributes no snapshots; serialized private fields reject. The save handler
is not wired in this increment, so this is a foundation, not a complete Save As flow.
Ordinary save/overwrite, roster/service integration and permissions remain unchanged.

Four native-fixture methods prepare coverage for live unsaved tracker/private edits,
fresh independent ownership and return-map isolation, source/input immutability,
existing target rejection, late writer rollback and plain/empty/forged authority.
Both new Python files passed AST parsing; all four native methods are unexecuted.
No full imports, native persistence, service/HTTP/browser or CI success is claimed.
[Split and current gates](../todo/223-statblock-lifecycle.md#2c3a-new-destination-save-as-kernel---2026-11-16)
retain 2C.3b/2C.3c, earlier test execution/corrections, bundles and acceptance.

Existing unittest discovery includes the new test filename. README/root indexes
remain accurate and unchanged; no workflow edit/dispatch or run-status check.
Intermediate [skip ci], final Stage 3 covering CI, schema 9 and matching code/data
backup rules remain; no new route, viewer, merge/deployment/release or feature closure.

## Documentation entry points

- [README](../../README.md)
- [Deployment](../../DEPLOYMENT.md)
- [Technical documentation index](../Technical-Documentation.md)
- [User guide](../User-Guide.md)
- [Systemd deployment](../Systemd-Deployment.md)
- [Refactor task and acceptance](../todo/080-source-size-refactors.md)

Use live branch files as authoritative; older attachments may describe an earlier
architecture or Python requirement.
