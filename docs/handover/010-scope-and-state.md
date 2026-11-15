# 010 - Scope and current state

[Back to handover index](../../HANDOVER.md)

Last updated: 2026-11-15. Dated sections below retain their historical scope.

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

Delivered as da7654059808795880361ae643e6b5523ffc5c0f. [Full dated record](https://github.com/dajomas/Scrying-Glass/blob/da7654059808795880361ae643e6b5523ffc5c0f/docs/handover/010-scope-and-state.md#02203-counter-only-row-rebuilds---2026-11-15)
retains the encoding defect/correction, exact eleven isolated constrained-SQLite
passes, eleven pending production tests and deployment limits. It corrected
2B.4's CHECK-incompatible custom kind to supported integer kind with a validated
private text marker. Counter-only setup/runtime row rebuild preservation and
reattachment are supplied, not fully validated. No DDL/schema change. Its earlier
clearing-disabled status is superseded only by the following bounded increment.

## 022.03 trusted clearing - 2026-11-15

Baseline: da7654059808795880361ae643e6b5523ffc5c0f. [Current task, retained
contracts and unfinished work](../todo/223-statblock-lifecycle.md). 022.02 stays
accepted/closed; 022.03 and Stage 1/2 remain unvalidated/unaccepted.

The recovery kernel now interprets absence only from an internal recovery carrier.
It compares row IDs and highest revisions, including counter-only history, under
its transaction. Counter-only binding tokens therefore cannot become valid again
after clear/re-add/clear. Campaign/reference/roster authorization and global
confirmation remain service responsibilities; no public route or clear flag is
added. Ordinary omission/serialized private fields still have no clearing authority.

All clears preflight scope, durable hooks and overflow before mutation. Each
surviving-content clear records/verifies the next counter and conditionally deletes
the header/cascading graph, then verifies the counter survived. Already-absent
content does not bump again. Later content starts beyond that tombstone. Plain
row rebuild preservation carries counter-only history forward. Removing a monster
still cascades normally without seeding unrelated IDs.

Existing service wiring already replaces live private metadata with the saved
map, including empty maps. Existing protected outer transactions retain rollback
of memory, tracker/content/counters, roster/runtime, history/audit/revision and
broadcast deferral. Mixed replacement and clearing is atomic under that boundary.
No generic private-only transaction-save fix is claimed by this bounded change.

Executed: six exact isolated SQL clear methods passed using real SQLite, native
ledger helpers/read-allocation-record methods, representative headers/child FKs
and the production value-kind CHECK. This does not exercise the full model,
constructor, actual graph tables or services. Twelve kernel and nine production
service methods are prepared, unexecuted: positive clear/reload/undo, stale absence
cycles, ordinary omission/raw input rejection, unsupported counters, mixed failure,
late full rollback and unsaved-runtime/setup isolation. Three changed Python files
AST-parse. Full imports and covering repository/HTTP/WS/browser validation remain
pending; no fresh CI result is claimed. Previous rejection assertions are replaced
with positive required behavior, not skipped or suppressed.

README, HANDOVER/TODO root identities and unchanged workflow tree match prior
complete reads; relevant source/persistence/transaction and task records were
reviewed. Existing discovery includes both test modules. This intermediate commit
uses [skip ci]; no workflow change/dispatch. Final Stage 3 covering CI remains
deferred. Earlier dated clearing-disabled notes in 030/240 are historical, not
current gates. All remaining 2B/private-only integration, 2C/2D, bundle limits/
representation and acceptance requirements remain in the lifecycle task.

Schema remains 9. Deploy matching complete code/data only after validation and
acceptance; old code lacks private marker/filter rules, so do not roll code back
alone over ledger-bearing data. Retain full storage/config/media/code backups.
No viewer/provider/listener, merge/deployment/release or whole-feature closure.

## 022.03 save-decision detection - 2026-11-15

Baseline: f38d7c3a4ba86f45dfbf167b25da189f3825c152. 2B.7 wires the existing
private-aware state_changed comparison into the transaction save decision after
reconciliation. Character/setup/runtime save order and surrounding rollback,
after-transaction and broadcast handling are retained. No private graph writer,
refresh, clear authority, schema or route change is added. This is detection only;
2B.8 must implement private-content save/refresh and 2B.9 integration/acceptance.
[Current task and retained gates](../todo/223-statblock-lifecycle.md#2b7-save-decision-detection---2026-11-15).

Six exact focused test methods passed in an isolated function-body harness with
signature, save and authorization test doubles plus a real SQLite sentinel. The
initial notebook-loop harness could not use asyncio.run; rerunning on a worker
thread passed all six without changing production code for the harness. These
passes prove routing/order, unchanged/tracker/private/combined decisions and
sentinel/memory rollback on comparison/save failure, not model validation, actual
private graph persistence, full imports or authenticated services. Both changed
Python files AST-parse. Existing canonical fingerprint/production suites and
covering CI remain pending; no earlier evidence is relabelled as a fresh run.

README and root indexes were read and remain applicable, so are unchanged. The
workflow was read; unittest discovery includes the new test module. No workflow
edit/dispatch; [skip ci] remains on intermediate deliveries. 2B/022.03 stay in
progress, not validated or accepted. Matching code/data backup guidance remains.

## 022.03 private save and refresh - 2026-11-15

Baseline: 4bf95480f2670adda80d798fa73aefe2a7ed58e7. 2B.8 adds a native SQLite
private flush after protected tracker saves and before history/revision processing.
It requires the caller's outer transaction, resolves the active-campaign setup or
unsaved runtime encounter, verifies monster identities and writes through the
existing private adapter with a no-op tracker callback. Fresh saved metadata is
assigned only after success. Plain state preserves stored graphs; explicit private
omission still rejects clearing. No standalone persistence API, route, schema or
permission change is introduced. Preparation limits and authorization remain
caller duties; copy/import and 2B.9 acceptance are not closed by this wiring.
[Task and validation gates](../todo/223-statblock-lifecycle.md#2b8-private-save-and-refresh---2026-11-15).

Six production-fixture tests are prepared, not executed, for setup/private-only
replacement and reload, unchanged/tracker-only revisions, runtime isolation,
stale/omission rejection, late refresh rollback and rebuilt rows. Three changed
Python files AST-parse; no new functional pass or full-import/service/HTTP/browser
validation is claimed. Earlier isolated passes are not rerun or promoted. Root
README/index and workflow identities match prior complete reads; no cosmetic root
edits, workflow edits or dispatch. Intermediate [skip ci] and deferred final Stage 3
covering CI remain. 2B.9, 2C/2D, bundles and overall acceptance remain pending.

## Documentation entry points

- [README](../../README.md)
- [Deployment](../../DEPLOYMENT.md)
- [Technical documentation index](../Technical-Documentation.md)
- [User guide](../User-Guide.md)
- [Systemd deployment](../Systemd-Deployment.md)
- [Refactor task and acceptance](../todo/080-source-size-refactors.md)

Use live branch files as authoritative; older attachments may describe an earlier
architecture or Python requirement.
