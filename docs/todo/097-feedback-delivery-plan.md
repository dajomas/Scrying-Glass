# 097 - SG-TODO-009.7 feedback delivery plan

[Back to TODO index](../../TODO.md)

## Current status - 2026-11-10

SG-TODO-009.7, Deliverable 1 and Deliverable 2 remain open. 4A.1-4A.10 are completed and closed for their bounded scopes after reviewed covering CI and explicit acceptance. 4A.10 closes after successful Branch tests 42865982880 attempt 1 covering ca4ec4ec64c47d8b865c292e97f01ed4599108f2 and the user's explicit close-out request. 4A.11 battle-action global notices is the next proposed unit, not started here; 4A.11 onward remains proposed. No owner/deadline or new priority is assigned; SG-TODO-019 and the agreed delivery sequence are unchanged.

## 4A.10 viewer font adjustment feedback - 2026-11-10

Completed/closed for its bounded scope after reviewed successful covering CI and the user's explicit close-out request. Delivered as ca4ec4ec64c47d8b865c292e97f01ed4599108f2 on features/perplexity-009.7 with normal CI. Scope: adjustBattleOrderFont in 080-source.js, 18 regressions, matching digest/size expectations and docs. Use encounter-scoped display.battle-order-font with stable battle-order target shared across directions, persistent explicit request errors and silent matching-success resolution. Preserve endpoint/JSON/header, existing error wording, pending early return, disabled controls, bounds and default behavior. Stale/superseded success cannot overwrite current display or feedback; finally releases pending and renders current latest state. Separate request failures from subsequent UI errors, with no automatic retry, new lock, server, client-display, helper or neighboring changes.

Preparation passed complete-fragment/test syntax, 18 regressions with zero failures/skips, five detected negative controls and restored-draft 18 passes. Tests use full 080, production-derived control helper, real controller, scoped test adapter and mocked DOM/network, not actual Admin bootstrap/full browser/server. Integration verified original 080 Git blob, whole tail unchanged, full-fragment syntax and same tested draft digest. Size 1,987 bytes; calculated eight-part total 116,190 (+248). Revised pin AST/digest agreement passed with only 080 digest/total changed and all guard/test logic retained. Behavioral tests were not rerun during integration. Actual eight-part assembly/combined parse, full identity/reader/isolation and combined/browser suites were not executed locally during preparation; no full-bundle hash is claimed. Those preparation limits are not a claim that later CI was unexecuted.

Successful covering Branch tests 42865982880 attempt 1 explicitly identifies implementation ca4ec4ec64c47d8b865c292e97f01ed4599108f2, published at 7ac35d78e4c1a34c1599737c2c4ccb5865b21c6d under ci-results-42865982880-attempt-1. Run/job/step metadata confirms all listed steps succeeded, including configured Python syntax/import, Python suite with browser fixtures, pytest, JavaScript and standalone browser/audit stages; no listed failed/skipped step. Individual test logs and visual artifacts were not inspected; no new per-test counts, manual/authenticated live-server or exhaustive accessibility result is claimed. Historical 18-test preparation evidence is separate from CI evidence. See [430 covering CI review/limits](../handover/430-viewer-font-feedback.md#4a10-covering-ci-review---2026-11-10).

The CI-status-only documentation update f9b4fa72625dc8eb3a2536d5a91c59fa910a2e7a correctly retained pending acceptance at that checkpoint. The user's subsequent 2026-11-10 close-out/push request now supplies bounded acceptance of 4A.10 only. See [430 bounded acceptance](../handover/430-viewer-font-feedback.md#4a10-bounded-acceptance-and-close-out---2026-11-10). This documentation-only close-out includes [skip ci], executes no new tests and modifies/dispatches no workflow. 4A.9 remains closed. Final combined producer/full-Admin acceptance remains a Deliverable 1 gate; Deliverable 2 and the wider phase remain open.

## 4A.9 activity-log clear feedback - 2026-11-10

Completed/closed for its bounded scope after reviewed successful covering CI and explicit user-requested documentation close-out with skip ci. Delivered as 92183b55707759d57c361cbfe877c44c06af4f02 on features/perplexity-009.7 with normal CI. Scope: clear handler in 040-source.js, 21 regressions, matching digest/size expectations and docs. Use encounter-scoped activity-log.clear with stable activity-log target, explicit persistent request errors, matching confirmed success before refresh and normal five-second global success expiry. Preserve confirmation/count wording, bodyless POST and exports. Already-empty is info and cannot erase a prior clear error; repeated empty notices replace one info record. Newer observations/attempts supersede old tickets; no stale publishing or refresh. Refresh failure stays load-owned, never a failed clear or automatic replay. No new concurrency policy, server or neighboring-handler migration.

Preparation passed slice/test syntax, 21 regressions with zero failures/skips, five detected negative controls and restored-draft 21 passes. Complete-fragment syntax/reverse comparison passed; original 040 verified against its Git blob, integrated tested slice unchanged. Modified 040 is 11,797 bytes; calculated eight-part total at delivery 115,942 (+461). Updated pin AST/digest agreement passed with only 040 digest/total changed and all guard/test AST retained. Behavioral tests were not rerun during integration. Preparation-time pending CI notes are superseded by successful covering Branch tests 42863235975 attempt 1, published at 9bc8aa2c22a6051fec1bad0a823464e51d936ac0 under ci-results-42863235975-attempt-1. Run/job/step metadata confirms all listed steps succeeded, including configured Python syntax/import, Python suite with browser fixtures, pytest, JavaScript and standalone browser/audit stages; no listed step failed or skipped. This review did not inspect individual test logs or visual artifacts and claims no new per-test counts, manual/authenticated live-server or exhaustive accessibility result. Historical preparation counts remain separate from CI evidence. See [420 bounded acceptance/evidence limits](../handover/420-activity-log-clear-feedback.md#4a9-bounded-acceptance-and-close-out---2026-11-10).

The user's 2026-11-10 request closes only 4A.9, not 4A.10 or whole-deliverable/phase validation. This documentation-only close-out includes [skip ci], executes no new tests and modifies/dispatches no workflow. Final combined producer/full-Admin acceptance remains a Deliverable 1 gate; Deliverable 2 and the wider phase stay open.

## 4A.8 global removal fallback feedback - 2026-11-10

Completed/closed for its bounded scope after reviewed successful covering CI and the user's explicit close-out request. Implementation 7996f81994c989c66e7e34d28791930ea41b65eb is covered by successful Branch tests 42858349138 attempt 1, published at 28ecb45d3c8dd3f610b74c258240a3ce3215aaf1; documentation close-out 2acd6a67fc76c770dcb6993e0abcf328295298d1. This does not migrate pane roster removal or imply whole-deliverable acceptance. Detailed behavior, preparation, metadata-only review and limits remain in [410 bounded acceptance](../handover/410-global-removal-fallback-feedback.md#4a8-bounded-acceptance-and-close-out---2026-11-10) and the [pre-4A.9 task-plan revision](https://github.com/dajomas/Scrying-Glass/blob/2acd6a67fc76c770dcb6993e0abcf328295298d1/docs/todo/097-feedback-delivery-plan.md). The close-out was documentation only with [skip ci] and no new test execution.

## Completed bounded units - 2026-11-10

Detailed delivery, failed-run history, acceptance and limitations remain in linked handovers and the [pre-4A.7 task-plan revision](https://github.com/dajomas/Scrying-Glass/blob/502cfafa24658cd2b6ca75c9cdbf202a8f51647d/docs/todo/097-feedback-delivery-plan.md). Closed narratives are summarized, not open work or evidence deleted. Incoming anchors are retained; 4A.7 detail is also preserved in its accepted [pre-4A.8 revision](https://github.com/dajomas/Scrying-Glass/blob/b36ed511e33980448ed0162802d1baee48371007/docs/todo/097-feedback-delivery-plan.md).

<a id="4a1-implementation-checkpoint---2026-11-10"></a>
<a id="4a2-startrestart-request-feedback---2026-11-10"></a>
<a id="4a3-start-validation-feedback---2026-11-10"></a>
<a id="4a4-stage-2-shared-next-feedback---2026-11-10"></a>
<a id="4a4-next-turn-feedback---stage-1-fixture-preparation---2026-11-10"></a>
<a id="4a5-end-battle-feedback---2026-11-10"></a>
<a id="4a6-reset-all-feedback---2026-11-10"></a>
<a id="4a7-individual-combatant-reset-feedback---2026-11-10"></a>

| Unit | Status | Implementation / covering Branch tests (attempt 1) | Evidence and acceptance limits |
|---|---|---|---|
| 4A.1 State-load | Completed/closed | Original 22b0a6f; repaired baseline ca160000 / 42796273382; later integrated 13ec059 / 42842153909 | [385 acceptance](../handover/385-state-load-feedback.md); 15 historical focused tests, not a new manual run |
| 4A.2 Start/restart requests | Completed/closed | b73908e / 42800259474 | [380 close-out](../handover/380-feedback-delivery-plan.md#4a2-close-out---2026-11-10) |
| 4A.3 Start eligibility/tie validation | Completed/closed | 64101f2 / 42808219579 | [380 acceptance](../handover/380-feedback-delivery-plan.md#4a3-acceptance-and-close-out---2026-11-10) |
| 4A.4 Shared main/modal Next | Completed/closed | Stage 1 e07d5eb / 42814023791; stage 2 baf7ddf / 42818381973 | [380 bounded acceptance](../handover/380-feedback-delivery-plan.md#4a4-bounded-acceptance-and-close-out---2026-11-10) |
| 4A.5 End | Completed/closed | 2b358c7 / 42833154095 | [380 bounded acceptance](../handover/380-feedback-delivery-plan.md#4a5-bounded-acceptance-and-close-out---2026-11-10) |
| 4A.6 Reset All | Completed/closed | 13ec059 / 42842153909 | [390 bounded acceptance](../handover/390-reset-all-feedback.md#4a6-bounded-acceptance-and-close-out---2026-11-10) |
| 4A.7 Individual reset | Completed/closed | ffcca4e / 42852710398 | [400 bounded acceptance](../handover/400-individual-reset-feedback.md#4a7-bounded-acceptance-and-close-out---2026-11-10) |
| 4A.8 Global removal fallback | Completed/closed | 7996f81 / 42858349138 | [410 bounded acceptance](../handover/410-global-removal-fallback-feedback.md#4a8-bounded-acceptance-and-close-out---2026-11-10) |
| 4A.9 Activity-log clear | Completed/closed | 92183b5 / 42863235975 | [420 bounded acceptance](../handover/420-activity-log-clear-feedback.md#4a9-bounded-acceptance-and-close-out---2026-11-10) |
| 4A.10 Viewer font adjustment | Completed/closed | ca4ec4e / 42865982880 | [430 bounded acceptance](../handover/430-viewer-font-feedback.md#4a10-bounded-acceptance-and-close-out---2026-11-10) |

Closures are scoped, explicitly user-accepted and separate from whole-deliverable/phase acceptance. Successful run/job metadata is not an invented individual-test log review, authenticated live-server/manual test or exhaustive accessibility result. Failed earlier runs remain failed. Earlier then-open status notes are historical, superseded by the later acceptances.

## Status and authority - 2026-11-09

The user approved two independently usable feedback deliverables and asked that the seven Deliverable 1 steps and Deliverable 2 target be retained. This plan supersedes earlier pending-expiry-policy/inspection-only wording in the [parent phase](090-admin-usability-redesign.md#sg-todo-0097---feedback-and-final-usability-hardening). The seven steps are preparation/delivery activities, not seven separately approved commits. User-approved WIP checkpoints 51e3e3bfcc8e56176b8bcc2559e74bee46e5f493 and 8ba97701a76328909b9570a8bfbf523e80abf4f6 do not complete Deliverable 1; bounded group-4A units are not new deliverables or blanket write approvals. See [380 continuity](../handover/380-feedback-delivery-plan.md).

## Approved feedback policy

1. Global success expires after five seconds.
2. Pane success expires after three seconds.
3. Actionable request/validation errors persist until dismissed, resolved or replaced by a relevant result.
4. Successful retry clears only its related error; unrelated success must not erase it.
5. Connection warnings persist while the problem exists and clear on recovery.
6. Identical polling failures update one warning, without duplicate notices/announcements.
7. Near-field validation identifies the field/combatant and clears when resolved.
8. Stale responses, recovery events and timers cannot overwrite/clear newer feedback or another campaign/setup's feedback.
9. Use explicit severity and operation identity, never message-wording heuristics.
10. Preserve drafts, selected values, authorization, API semantics and combat behavior.

## Deliverable 1 - integrated global and pane feedback

Status: in progress, not fully delivered or validated. The controller/rendering and incomplete Admin-wiring checkpoints are saved. Complete all seven steps; deliver working Admin behavior, not only a controller/renderer/API/test scaffold.

### 1. Finish the integration inventory

Inspect live instructions, docs, implementation, dependencies, test/CI configuration and identities; reuse verified complete reads, re-read changed/truncated/relevant files. Finish enhancement-script producers (including Encounter tools), actual timeout/feedback asset order, notification layout/live regions/header/modal behavior and source-identity, loading, Node/full-Admin contracts. Inventory each operation's destination, explicit severity, identity, campaign/setup scope and retry resolution. Identify direct DOM writers, competing timers and deferred paths. Distinguish applied mutation from subsequent refresh failure; never imply safe replay because refresh failed. Do not call a partial inventory complete.

### 2. Implement the feedback controller and accessible rendering

Use explicit severity, operation/scope/ordering metadata; five-second global and three-second pane success deadlines; persistent actionable errors; related-result resolution; keyboard-operable dismissal without stealing focus; independent errors/successes. Reject stale results/superseded timers. Preserve layout/live regions without repeated announcements on unrelated updates.

### 3. Wire it into the actual Admin loading path

Load feedback before migrated consumers, replace global/pane entry points, remove competing unconditional global expiry and migrate direct pane/lookup writers so they cannot bypass the controller or clear unrelated feedback. Preserve eight ordered UTF-8 Admin fragments, per-fragment size limits, assembled /static/admin.js and tracked failure marker. Retain notification visibility/layout, original controls/drafts/selections/handlers.

### 4. Migrate actual feedback producers

Pair failures and matching retry/resolution for campaign create/edit/switch/delete/setup transfer; setup create/save/load/rename/delete/import; character/monster create/edit/bulk/removal/initiative; background/activity-log operations; battle controls; relevant enhancement-script global/pane notices. Add silent success resolution where appropriate; record exact coverage/deferred paths; never infer severity from wording. Deliverable 2 owns connection/recovery and field/combatant-associated near-field validation. Preserve existing validation and initiative Join gates while making applicable Deliverable 1 global/pane errors persistent.

### 5. Add unit and full-Admin regressions

Controller: exact deadlines, persistence, accessible dismissal, related retry/unrelated-success isolation, independent operations, stale results, superseded timers, scope changes, safe text. Actual loaded Admin assets/handlers: pane errors beyond three seconds/global beyond five; related retry clears only its error; direct lookup preserves unrelated errors; old-scope suppression; keyboard dismissal/focus; retained accepted 009.6 workspace/panels/Start behavior. Update replaced timeout-policy assertions without weakening unrelated ones. Fixtures are not authenticated live-server verification.

### 6. Prepare documentation and review the complete payload

Include behavior, caller coverage/deferred paths, actual executed checks/pending validation and relevant TODO/handover changes in the proposed implementation commit. Keep 009.7 open; review complete diff for omissions, compatibility, source-size/assembly/identity, asset order and accepted behavior. Execute available checks, using CI-first delivery when full local execution is unavailable; never substitute static review/syntax/mocks for unexecuted checks or stop solely for that limitation.

### 7. Request exact-content approval, then deliver

Request complete nonempty bound GitHub confirmation for dajomas/Scrying-Glass, features/perplexity-009.7, exact message/files. Push exactly as approved, report actual SHA and truthful validation. Implementation/test commits use normal CI unless explicitly instructed otherwise; every documentation-only message includes [skip ci]. A push is not CI success or acceptance. Review covering evidence and obtain fresh approval for each correction. No merge into another branch is implied.

## Bounded group 4A sub-tasks - 2026-11-09

Retained execution units within Deliverable 1 step 4; original suggestions were not implementation. Verify effective live handlers/files before each change. Interrupted/disappeared output is not saved implementation or test evidence.

| ID | Bounded scope | Completion criteria |
|---|---|---|
| 4A.1 | State-load (completed) | Own operation identity; matching reload resolves only its error; stale results cannot restore old scope; preserve return/rethrow contract. |
| 4A.2 | Start/restart requests (completed) | Effective wrapper; pre-request identity, persistent failure/matching resolution; preserve success collapse/failed-Start visibility. |
| 4A.3 | Start eligibility/tie rejection (completed) | Distinct validation/request/refresh errors; preserve gates/order/payloads; near-field association remains Deliverable 2. |
| 4A.4 | Shared Next (completed) | Main/modal handler; mutation/refresh distinction, uncertainty wording, concurrency guards, no automatic POST retry. |
| 4A.5 | End (completed) | Pair validation/request errors and matching success; preserve confirmation/non-resetting behavior. |
| 4A.6 | Reset All (completed) | Explicit failure/matching resolution; preserve confirmation/payload/combat behavior. |
| 4A.7 | Individual reset (completed) | Character/monster global errors; target-specific resolution; resetting another combatant cannot clear the first error. |
| 4A.8 | Global removal fallback (completed) | Separate from pane roster removal; preserve named confirmation and button-state handling. |
| 4A.9 | Activity-log clear (completed) | Explicit failure/success/already-empty severity; exports unchanged. |
| 4A.10 | Viewer font adjustment (completed) | Own error/resolution identity; preserve bounds and pending controls. |
| 4A.11 | Battle-action global notices | Eligibility/no-target/no-pending and start-of-turn completion; no modal-local redesign/action changes. |
| 4A.12 | Join reporting | One rejection notice across fetch gate/core; matching success resolves only related error; preserve client/server gates. |
| 4A.13 | Global reconciliation | Audit remaining callers/cross-operation isolation/later dependencies; retire global compatibility only after relevant producers migrate; pane route remains until its migrations finish. |

### Execution boundary for each sub-task

Verify relevant live source/dependencies/tests using complete-read reuse; prepare narrowly without pulling in neighboring operations from shared files; execute available focused checks with limitations/CI-first fallback; review full diff and unresolved dependencies; reach a concise reviewable result before another unit. Do not rely on a long response or generated attachments as the sole recovery point.

### Saving and validation boundaries

Units are not separate deliverables, mandatory one-commit-per-row or automatic phase gates. Each external write needs complete bound approval and appropriate implementation/tests/docs/status together. Intermediate topic-branch saves remain WIP, not deployment-ready full feedback behavior. Checkpoint 2's one-off skip does not carry to later implementation commits; standing documentation-only [skip ci] does. Focused passes do not replace final combined full-Admin regressions, covering CI review or task-specific acceptance. No owner/deadline/new priority/wider scope; Deliverable 2 and accepted 009.6 stay unchanged.

## Deliverable 2 - connection warnings and near-field validation

Status: remaining work after Deliverable 1, not implemented. Persistent connection failure/recovery warnings, identical-polling-failure deduplication/announcement suppression, field/combatant-associated near-field validation, campaign/setup scope/retry handling and combined keyboard/responsive regressions. Recovery cannot clear unrelated/newer feedback. Preserve existing initiative/server gates rather than weakening/rebuilding them; do not enlarge Deliverable 1 with this work.

## Remaining phase scope and compatibility gates

Destructive-confirmation review and broader responsive/accessibility hardening remain in 009.7. Both feedback deliverables do not automatically close the phase. Cover local overflow/zoom, labels/contrast, focus/tab/menu/announcements, tools dialog/nested overlays and independent-panel interactions; retain correct name/scope confirmations. Require covering regressions/CI and task-specific acceptance.

Preserve accepted 009.6: full-width Battle/Characters/Monsters/Activity log; no duplicate Participants/sidebar/split workspace; on-demand tools using original controls/drafts/files and keyboard/focus/busy/nested-dialog behavior; independent Campaign/Preparation controls; successful Start/restart collapse, failed-Start visibility and refresh/Next manual-reopening retention; independent lair eligibility, campaign-scoped viewer status, native roster/local scrolling, permissions and combat rules. Historical references never authorize overwriting newer work.

## Documentation and evidence boundaries

Closed-unit narrative detail is cross-linked rather than duplicated; incoming anchors/open work/acceptance criteria are retained. No old failed run is relabelled. Closed 4A.8 runtime/acceptance detail is retained in 410 and the linked pre-4A.9 revision; earlier closed evidence links remain. Mixed 4A.9/4A.10 implementations used normal CI. The bounded 4A.9 close-out and 4A.10 CI-status update included [skip ci]; this documentation-only bounded 4A.10 close-out also includes [skip ci]. No deliverable/phase acceptance, merge or deployment is included.
