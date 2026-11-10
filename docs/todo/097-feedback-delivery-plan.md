# 097 - SG-TODO-009.7 feedback delivery plan

[Back to TODO index](../../TODO.md)

## 4A.5 End-battle feedback - 2026-11-10

Status: completed and closed for the bounded End-battle feedback scope at the user's explicit acceptance request on 2026-11-10, after successful covering CI. Implementation 2b358c7b963640b393fa91875bcfc574c9885ab3 on features/perplexity-009.7 is covered by successful Branch tests 42833154095 attempt 1; evidence publication b545b2749d1ccf2390b63ce9d3731570db54710e under ci-results-42833154095-attempt-1. Reviewed run.json and jobs.json match the exact implementation SHA and report all configured validation stages successful. The earlier pre-implementation acceptance intent did not close the task; this later explicit request follows delivered implementation and reviewed CI. See [bounded acceptance and evidence limits](../handover/380-feedback-delivery-plan.md#4a5-bounded-acceptance-and-close-out---2026-11-10).

The deferred admin-end-feedback.js overrides only End after core/Start validation loading. Separate encounter-scoped battle.end.validation and battle.end identities keep actionable errors persistent. Confirmed valid attempts resolve only End validation; matching POST success replaces only End request feedback with the existing non-resetting success message before load(). load() owns refresh errors. Cancellation preserves errors; refresh alone and unrelated success do not clear End errors. Old-scope/superseded responses cannot publish or refresh a new encounter. Preserve the empty-order gate, exact confirmation, one POST per confirmed invocation and unchanged server semantics. No reset, automatic retry, new concurrency policy or neighboring producer migration.

Historical preparation passed both JavaScript syntax checks, all 15 Node regressions with zero failures/skips and three detected temporary negative controls; the restored draft passed all 15 again. Real controller/bootstrap and full End asset executed with mocked DOM/transport/refresh, not full Admin/browser or authenticated server. Covering configured CI stages subsequently passed as recorded above. No new local execution, individual-test log/assertion review, authenticated live-server or manual test is claimed by this close-out. See [delivery history](../handover/380-feedback-delivery-plan.md#4a5-end-battle-feedback-delivery---2026-11-10). 4A.2/4A.3/4A.4 remain closed; 4A.1's formal status, SG-TODO-019 and agreed delivery order are unchanged. Deliverable 1, Deliverable 2 and SG-TODO-009.7 remain open. 4A.6 Reset-all feedback is the next proposed bounded unit, not started here; later units remain proposed. No whole-deliverable/phase acceptance, merge or deployment is implied. This documentation-only acceptance/close-out includes [skip ci], runs no tests and changes/dispatches no workflow. The skip marker alone does not establish workflow state.

## 4A.4 stage 2 shared Next feedback - 2026-11-10

Status: completed and closed for the bounded shared main/modal Next-turn feedback scope at the user's explicit acceptance request on 2026-11-10. Stage 2 implementation baf7ddf4dc9059b11c9df06cd85d5e3e0f81fdcf is covered by successful Branch tests 42818381973 attempt 1 on features/perplexity-009.7, evidence cf43f0373617b3b2a07f0207bc7143adc4ad3bad under ci-results-42818381973-attempt-1. Reviewed run and job/step metadata match that exact SHA and report all configured validation stages successful. Stage 1 is delivered at e07d5eb832ba8d80e02c9d9933ad7c0f5038936d with successful covering Branch tests 42814023791 attempt 1, evidence 50e52f692b1d08eb059a785b6937426229cf9934. Both staged deliveries are reconciled; acceptance is limited to 4A.4. See [bounded acceptance and evidence limits](../handover/380-feedback-delivery-plan.md#4a4-bounded-acceptance-and-close-out---2026-11-10).

The existing shared main/modal next() uses battle.next errors and silent matching-success resolution, with an encounter-scoped lifetime guard permitting related report replacement after failed reconciliation without publishing into a new scope. Retain preparation/uncertain/confirmed-advancement wording, one POST, concurrency guards, control restoration and actor-reopening checks. No-active-participant feedback is explicit info and resolves the earlier related error. Refresh alone and unrelated success do not clear a Next error. Stage 1 browser fixtures are retained unchanged after compatibility review; the new Node fixture adds 20 focused regressions.

Executed during preceding preparation: two JavaScript syntax checks, 20 passing Node regressions (zero failed/skipped), four detected negative controls and 20 passing restored-draft tests. No full browser/combined suites ran locally for stage 2; the later covering configured CI stages passed as recorded above. No new local execution, individual-test log review, authenticated live-server or manual test is claimed by this close-out. See [delivery evidence](../handover/380-feedback-delivery-plan.md#4a4-stage-2-shared-next-feedback---2026-11-10). Deliverable 1 and 009.7 remain open; subsequent 4A.5 completion is recorded above. 4A.1's formal status, 4A.2/4A.3 closures, SG-TODO-019 and agreed delivery order remain unchanged. No whole-phase acceptance, merge or deployment is implied.

## 4A.4 Next-turn feedback - stage 1 fixture preparation - 2026-11-10

Status: stage 1 delivered at e07d5eb832ba8d80e02c9d9933ad7c0f5038936d; covering CI verified successful as recorded above. The stage changed only the two isolated Next browser fixtures and task/handover documentation. Production battle-actions-next.js was unchanged in stage 1. Stage 1 did not itself deliver new Next feedback behavior; the subsequent stage 2 delivery and bounded 4A.4 close-out are recorded above.

Load the real controller/view/bootstrap, route fixture messages through the production adapter and observe complete valid campaign/setup snapshots during initialization, state fetch and refresh. Preserve all existing Next behavior assertions; add a dependency/scope-retirement regression without mutations. The deferred-boot fixture serves real feedback assets before its stub Admin and real Next script. Other transport/helpers remain mocked.

Historical preparation checks: AST parsing of the added Python test method and JavaScript syntax checking of the added scope observer/notice snippet passed. Neither complete fixture ran locally. Subsequent stage 1 run and job/step metadata verified successful configured Python/browser, JavaScript, pytest and standalone browser/audit stages. See [stage 1 evidence and boundaries](../handover/380-feedback-delivery-plan.md#4a4-stage-1-fixture-preparation---2026-11-10). No retroactive local or individual-log result is claimed.

Stage 2 was separately requested, approved and delivered after stage 1 CI. Bounded 4A.4 acceptance now covers the staged result as recorded above, not Deliverable 1 or phase closure. 4A.2/4A.3 stay closed; 4A.1's formal status and SG-TODO-019 are unchanged.

## 4A.3 Start validation feedback - 2026-11-10

Status: completed and closed for the bounded Start eligibility/tie-order feedback scope at the user's explicit acceptance and close-out request on 2026-11-10. Implementation 64101f24e624e1cb7a7f1ea2cea2c933b100fb72 is covered by successful Branch tests 42808219579 attempt 1 on features/perplexity-009.7. Run and job/step metadata were verified in publication e70419875322239b3d70373110a7538948a70097 under ci-results-42808219579-attempt-1; all configured test stages completed successfully. No individual-test log review, new local execution, live-server or manual test is claimed. See [acceptance and evidence limits](../handover/380-feedback-delivery-plan.md#4a3-acceptance-and-close-out---2026-11-10).

A small deferred admin-start-validation.js asset replaces only the Start and tie-confirmation validation handlers after the accepted 4A.2 override. The original core-fragment draft is superseded; core fragments and bundle identity pins remain unchanged. Explicit encounter-scoped battle.start.eligibility and battle.start.tie-order errors persist until related resolution/dismissal. Passing eligibility resolves only its error; valid tie confirmation or a subsequent valid no-tie Start resolves only the tie error. Opening/cancelling ties does not resolve it. Request/refresh errors remain separate. Eligibility, ordering, payloads and near-field scope are unchanged.

Two syntax checks passed during preparation after correcting a malformed test regex. Thirteen focused Node regressions were prepared but not executed locally; the later covering CI has successful configured JavaScript, Python/browser, pytest and standalone browser/audit stages. That evidence supersedes delivery-time pending-CI statements without inventing a local or per-test result. See [delivery history](../handover/380-feedback-delivery-plan.md#4a3-start-validation-delivery---2026-11-10). Deliverable 1 and 009.7 remain open; 4A.4 is now completed for its bounded scope as recorded above. 4A.2 stays closed; 4A.1's formal status and SG-TODO-019 remain unchanged. No broader phase acceptance or deployment is implied.

## 4A.2 Start/restart request feedback - 2026-11-10

Status: completed and closed for the bounded Start/restart request-feedback scope at the user's explicit 2026-11-10 close-out request. Implementation: b73908e1368cb38f9ad5f5eb028bcb638a8fbbba. Covering Branch tests 42800259474 attempt 1 completed/success for that exact SHA; run and job/step metadata were verified in publication 31b6401daeb93085e131bf144f147330046466b1 under ci-results-42800259474-attempt-1. The Python/browser suite, JavaScript tests, pytest regressions and standalone browser/audit stages all completed successfully. No separate live-server/manual check or per-test log review is claimed. Deliverable 1 and SG-TODO-009.7 remain open; 4A.3/4A.4/4A.5 are completed for their bounded scopes, and 4A.6-4A.13 remain proposed. 4A.1's formal status is unchanged.

The effective startBattle override in static/admin-initial-visibility.js uses a pre-request encounter-scoped battle.start ticket. Persistent request failures leave panels unchanged; a matching successful POST silently resolves its request error before collapse and refresh. Superseded/old-scope outcomes cannot publish or collapse/refresh another encounter. load() continues to own state refresh errors; no automatic POST retry, payload/permission changes or eligibility/tie-order migration is included. See [close-out evidence and limits](../handover/380-feedback-delivery-plan.md#4a2-close-out---2026-11-10) and [preparation/compatibility history](../handover/380-feedback-delivery-plan.md#4a2-preparation-and-baseline-reconciliation---2026-11-10).

Prior preparation passed two JavaScript syntax checks, 12 focused Node regressions and four detected negative controls; the restored draft passed all 12 again. These execute the complete visibility asset and real feedback controller with mocked DOM, transport and bootstrap adapter. They are not full-Admin browser or live-server evidence and were not rerun during the final compatibility review or this close-out. Existing CI discovers the .cjs file and page-level Start/restart/failed-Start fixtures; the covering configured stages subsequently passed as recorded above. Final combined producer-specific validation, remaining phase work and SG-TODO-019 are unchanged.

## 4A.1 implementation checkpoint - 2026-11-10

Status: implementation delivered at 22b0a6f756c04d9ccda9ed763adb3abed5ab93e6; covering workflow success verified, most recently run 42796273382 attempt 1 testing ca1600003ac4de0809a348dec7cef18cc6875fc9. This supersedes the earlier pending-CI status, not historical failures or acceptance limits. 4A.1 remains open with implementation/CI verified; no formal close-out or live/manual acceptance is inferred. Deliverable 1 and SG-TODO-009.7 remain open.

The change adds encounter-scoped state.load errors and silent matching-success resolution. Shared state-request sequencing plus an encounter epoch reject stale state before assigning latest or rendering. Accepted campaign/setup transitions rebinds the load ticket. Ordinary load() returns undefined and handles errors; only literal load(true) rethrows the original error, including stale errors whose feedback is suppressed. Current malformed scope responses produce an actionable reload error instead of being rendered as success. No mutation retry or neighboring producer migration is included.

Preparation passed two JavaScript syntax checks and 15 focused Node regressions. Four temporary negative controls were detected. These mocked network/DOM source-slice checks are not full-Admin browser or live-server evidence. See the [4A.1 handover evidence and limits](../handover/380-feedback-delivery-plan.md#4a1-implementation-checkpoint---2026-11-10). Historical preparation and the later successful baseline are separate evidence; neither establishes phase acceptance. Final combined producer-specific Admin validation remains outstanding.

## Status and authority - 2026-11-09

SG-TODO-009.7 remains in progress and open. The user approved two independently usable feedback deliverables and requested that the seven Deliverable 1 steps and Deliverable 2 target be retained for future reference. This is the current execution plan for the [parent phase](090-admin-usability-redesign.md#sg-todo-0097---feedback-and-final-usability-hardening). It supersedes that section's earlier statements that expiry policy still needs agreement and that only inspection/scoping is authorized. No phase acceptance is claimed by this planning record. No owner or deadline is assigned.

See the [continuity record](../handover/380-feedback-delivery-plan.md) for preparation state and evidence limits. Steps are preparation/delivery activities within Deliverable 1, not seven separately approved implementation commits. The user subsequently approved two work-in-progress checkpoints on features/perplexity-009.7; these do not complete Deliverable 1. The bounded group-4A suggestions below are execution units, not new deliverables or blanket GitHub write approvals.

## Approved feedback policy

1. Global success messages expire after five seconds.
2. Pane success messages expire after three seconds.
3. Actionable request and validation errors do not expire automatically; retain them until dismissed, resolved or replaced by a relevant result.
4. A successful retry clears only the related error. Unrelated success must not erase it.
5. Connection warnings persist while the problem exists and clear on recovery.
6. Repeated identical polling failures update one warning rather than duplicating notices or announcements.
7. Near-field validation identifies the affected field/combatant and clears when resolved.
8. Stale responses, recovery events and timers must not overwrite or clear newer feedback or feedback for another campaign/setup.
9. Use explicit severity and operation identity, never message-wording heuristics.
10. Preserve drafts, selected values, authorization, API semantics and combat behavior.

## Deliverable 1 - integrated global and pane feedback

Status: in progress; controller/rendering and incomplete Admin-wiring checkpoints are saved, but complete Deliverable 1 is not delivered or validated. Checkpoints: 51e3e3bfcc8e56176b8bcc2559e74bee46e5f493 and 8ba97701a76328909b9570a8bfbf523e80abf4f6. Complete all seven steps below. This must be working Admin behavior, not only a standalone controller, renderer, API design or test scaffold.

### 1. Finish the integration inventory

Inspect the live working branch, relevant documentation, implementation, tests and actual CI configuration. Verify prior complete reads against live identity and re-read changed, truncated or newly relevant files. Finish inspecting enhancement-script feedback producers, including Encounter tools; actual timeout/feedback asset inclusion order; notification layout, live regions, header/modal behavior; and source-identity, asset-loading, Node and full-Admin browser contracts.

Produce a caller inventory recording each operation's destination, explicit severity, operation identity, campaign/setup scope and retry-resolution behavior. Identify direct DOM writers, competing timers and intentionally deferred paths. Distinguish mutation failure from subsequent refresh failure: applied operations must not be presented as safe to repeat merely because refresh failed. Do not label a partial inventory complete.

### 2. Implement the feedback controller and accessible rendering

Use explicit severity, operation identity, scope and ordering metadata. Implement five-second global and three-second pane success timers, persistent actionable errors, related-result resolution and accessible keyboard-operable dismissal without stealing focus. Allow unrelated errors and successes to coexist. Reject stale results and prevent superseded timers from clearing newer notices. Preserve layout and existing live-region behavior without repeated announcements caused by unrelated updates.

### 3. Wire it into the actual Admin loading path

Load the implementation before migrated consumers and replace the global/pane entry points. Remove competing unconditional global expiry and migrate direct pane writers, including lookup status handling, so they cannot bypass the controller or clear another operation's feedback. Preserve eight ordered Admin fragments, per-fragment source-size limits, assembled /static/admin.js and its tracked failure marker. Retain notification visibility/layout handling, original controls, drafts, selections and event handlers.

### 4. Migrate actual feedback producers

Pair failures with successful retry/resolution paths for campaign creation/edit/switch/delete/setup transfer; setup create/save/load/rename/delete/import; character/monster creation/edit/bulk/removal/initiative; background and activity-log operations; battle controls; and relevant enhancement-script global/pane feedback. Add explicit related-error resolution to silently successful operations without unnecessary success messages. Record exact coverage and intentionally unmigrated paths. Do not classify severity from wording.

Connection warning/recovery integration and field/combatant-associated near-field validation belong to Deliverable 2. Preserve existing validation and initiative Join battle gates; existing global/pane errors still need persistent handling where applicable in Deliverable 1.

### 5. Add unit and full-Admin regressions

Controller coverage: exact success timeouts; persistent errors; accessible dismissal; related retry resolution; unrelated-success isolation; independent operations; stale results; superseded timers; scope changes; safe text rendering.

Integrated coverage must exercise actual loaded assets and handlers: pane errors beyond three seconds; global errors beyond five seconds; related retry clearing only its own error; direct lookup updates not erasing unrelated errors; old-scope responses not replacing current feedback; keyboard dismissal/focus; and preservation of accepted 009.6 workspace, independent panels and Start/restart behavior. Update assertions that intentionally encode the replaced unconditional timeout policy, retaining unrelated assertions. Fixtures are not authenticated live-server verification.

### 6. Prepare documentation and review the complete payload

In the same proposed implementation commit, document implemented behavior, caller coverage, intentionally unmigrated paths, executed checks and pending validation. Update relevant handover/TODO records, keeping 009.7 open and remaining work explicit. Review the entire diff for omissions, compatibility, source-size and assembly/identity contracts, asset ordering and accepted behavior. Execute available checks. Follow the repository's CI-first workflow when local full-Admin execution is unavailable; do not claim unexecuted checks passed or stop solely for that limitation.

### 7. Request exact-content approval, then deliver

After the complete nonempty payload is reviewed, request bound GitHub confirmation for dajomas/Scrying-Glass, features/perplexity-009.7, exact commit message and complete file contents. Push only after approval and exactly as approved. Report the actual commit SHA and truthful validation status. Run normal CI for implementation/test commits; do not include [skip ci] without a specific user instruction. A push is delivery, not evidence of passing CI or acceptance. Review supplied covering CI evidence and obtain fresh approval for corrective writes. No merge into another branch is implied.

## Bounded group 4A sub-tasks - 2026-11-09

At the user's request, retain the following suggestions for future reference. These were originally proposed execution units within step 4 of Deliverable 1, not completed by that planning update. Subsequent 4A.1/4A.2/4A.3/4A.4/4A.5 status is recorded above. Exact files and effective handlers must be verified against the live branch before each change. Do not treat interrupted or disappeared output as saved implementation or test evidence.

| ID | Bounded scope | Completion criteria |
|---|---|---|
| 4A.1 | State-load feedback | Give state loading its own operation identity. A matching successful reload resolves only its load error; stale responses cannot publish feedback or restore an old scope. Preserve the existing return/rethrow contract. |
| 4A.2 | Start/restart request feedback (completed) | Migrate the effective startBattle wrapper. Capture identity before the request, retain persistent failure feedback and resolve it on matching success. Preserve successful collapse and failed-Start visibility. |
| 4A.3 | Start eligibility and tie-order rejection (completed) | Migrate the related global validation producers without changing eligibility, tie ordering or request payloads. Keep these errors distinct from transport and refresh failures. Near-field association remains Deliverable 2. |
| 4A.4 | Next-turn feedback (completed) | Migrate the shared main/modal Next handler. Preserve mutation-versus-refresh distinctions, uncertain-outcome wording, concurrency guards and no automatic POST retry. |
| 4A.5 | End-battle feedback (completed) | Pair End's validation/request failures with its matching successful result. Preserve the existing confirmation and non-resetting behavior. |
| 4A.6 | Reset-all feedback | Add explicit failure identity and successful resolution for Reset All. Preserve its confirmation, payload and combat behavior. |
| 4A.7 | Individual combatant reset | Migrate the global reset-error paths for characters and monsters. Scope resolution to the affected combatant; resetting another combatant must not clear the error. |
| 4A.8 | Global combatant-removal fallback | Migrate the global removal handler separately from pane-based roster removal. Preserve its named confirmation and button-state handling. |
| 4A.9 | Activity-log clear | Migrate Clear's request error, successful result and already-empty result with explicit severity. Leave navigation-based exports unchanged. |
| 4A.10 | Viewer font-size adjustment | Give font adjustment its own error/resolution identity. Preserve bounds and pending-control behavior. |
| 4A.11 | Battle-action global notices | Migrate global action-eligibility/no-target/no-pending messages and the start-of-turn completion notice. Do not redesign modal-local feedback or change action application. |
| 4A.12 | Join-reporting coordination | Reconcile the fetch gate and core caller so one rejected join does not produce duplicate feedback. A matching successful join resolves only its related error. Preserve both client and server gates. |
| 4A.13 | Global-feedback reconciliation | Audit remaining global callers, test cross-operation isolation and identify dependencies on later groups. Retire the global compatibility route only when no relevant producer still needs it; keep the pane route until its migrations are complete. |

### Execution boundary for each sub-task

1. Verify and read only the relevant live source, dependencies and tests; reuse verified complete reads rather than restarting the entire inspection.
2. Prepare the narrowly scoped change. Do not expand into neighboring operations merely because they share a file. State-load feedback, for example, does not include background uploads or character editing.
3. Run focused checks actually available, with honest results and limitations. Unavailable local checks follow the repository's CI-first workflow rather than blocking an otherwise prepared delivery.
4. Review the complete diff and record unresolved dependencies and remaining work.
5. Reach a concise, reviewable result before starting another sub-task; do not rely on a long response or generated attachments as the sole continuation point.

### Saving and validation boundaries

- These are execution units within Deliverable 1, not new deliverables, a mandatory one-commit-per-row plan or automatic phase-completion gates.
- Every GitHub write requires its own complete bound approval, including exact target, message and file contents. Saving this plan does not approve future write payloads. Necessary implementation, tests and documentation/status updates belong together in each proposed write.
- Intermediate saves remain explicitly work in progress on features/perplexity-009.7. Do not present partial caller migration as completed feedback behavior or deployment-ready code.
- The previous one-off [skip ci] instruction applied to checkpoint 2 only. Subsequent implementation/test commits use normal CI unless the user specifies otherwise. Documentation-only commits always retain the standing [skip ci] rule.
- Focused passing tests do not replace final combined full-Admin regressions, covering CI review or task-specific acceptance.
- No owner/deadline, new priority or wider scope is assigned. Deliverable 2 and accepted 009.6 behavior are unchanged.

## Deliverable 2 - connection warnings and near-field validation

Status: explicit remaining work after Deliverable 1; not implemented. Integrate persistent connection-failure/recovery warnings, identical-polling-failure deduplication and announcement suppression; field/combatant-associated near-field validation; campaign/setup scope and retry handling; and combined keyboard/responsive regressions. Recovery must not clear unrelated/newer feedback. Preserve the existing initiative gate and server validation rather than rebuilding or weakening them. Do not implement this deliverable merely to enlarge Deliverable 1.

## Remaining phase scope and compatibility gates

Destructive-confirmation review and broader responsive/accessibility hardening remain within 009.7. Completing both feedback deliverables does not automatically close the phase. Cover relevant local overflow/zoom, labels/contrast, focus/tab/menu/announcements, tools dialog/nested overlays and independent-panel interactions; retain correct existing name/scope confirmations. Require covering regressions/CI and task-specific user acceptance before closure.

Preserve accepted 009.6: full-width Battle, Characters, Monsters and Activity log; no duplicate Participants, sidebar or split workspace; on-demand Encounter tools using original controls/drafts and keyboard/focus/busy/nested-dialog behavior; independent Campaign and Preparation controls; successful Start/restart collapse, failed-Start visibility and refresh/Next manual-reopening retention; independent lair eligibility, campaign-scoped viewer status, native roster actions/local scrolling, permissions and combat rules. Historical references never authorize overwriting newer work.

## Historical 4A.4 documentation-only validation

Historical implementation/test deliveries used normal CI. The bounded 4A.4 acceptance/close-out changed only human-readable documentation and included [skip ci]. No tests were executed, workflows changed or separately dispatched for that close-out. README and root index links/open phase descriptions remained accurate without edits. SG-TODO-019, agreed delivery order and 4A.1's formal status remained unchanged. The skip marker alone does not establish workflow state. Acceptance was limited to 4A.4, not Deliverable 1 or SG-TODO-009.7. The later mixed 4A.5 implementation used normal CI; its documentation-only close-out follows the standing [skip ci] rule.
