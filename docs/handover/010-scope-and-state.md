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
budgets, missing/foreign scope and revision exhaustion. The six corrected 2B.8
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

## Documentation entry points

- [README](../../README.md)
- [Deployment](../../DEPLOYMENT.md)
- [Technical documentation index](../Technical-Documentation.md)
- [User guide](../User-Guide.md)
- [Systemd deployment](../Systemd-Deployment.md)
- [Refactor task and acceptance](../todo/080-source-size-refactors.md)

Use live branch files as authoritative; older attachments may describe an earlier
architecture or Python requirement.
