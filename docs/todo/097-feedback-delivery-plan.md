# 097 - SG-TODO-009.7 feedback delivery plan

[Back to TODO index](../../TODO.md)

## 4A.1 implementation checkpoint - 2026-11-10

Status: implementation prepared for this commit; covering CI and final combined Admin validation remain pending. This supersedes the proposed-only status below for 4A.1, not the historical planning record. 4A.1, Deliverable 1 and SG-TODO-009.7 remain open; 4A.2-4A.13 remain proposed.

The change adds encounter-scoped state.load errors and silent matching-success resolution. Shared state-request sequencing plus an encounter epoch reject stale state before assigning latest or rendering. Accepted campaign/setup transitions rebind the load ticket. Ordinary load() returns undefined and handles errors; only literal load(true) rethrows the original error, including stale errors whose feedback is suppressed. Current malformed scope responses produce an actionable reload error instead of being rendered as success. No mutation retry or neighboring producer migration is included.

Preparation passed two JavaScript syntax checks and 15 focused Node regressions. Four temporary negative controls were detected. These mocked network/DOM source-slice checks are not full-Admin browser or live-server evidence. See the [4A.1 handover evidence and limits](../handover/380-feedback-delivery-plan.md#4a1-implementation-checkpoint---2026-11-10). The existing JavaScript CI discovery includes the new test file. This mixed implementation/test/documentation commit uses normal CI, not the checkpoint-2 skip instruction. No passing CI, commit SHA or phase acceptance is claimed before evidence exists.

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

At the user's request, retain the following suggestions for future reference. These are proposed execution units within step 4 of Deliverable 1. All remain proposed/not completed by this documentation update. The first bounded unit is 4A.1. Exact files and effective handlers must be verified against the live branch before each change. Do not treat interrupted or disappeared output as saved implementation or test evidence.

| ID | Bounded scope | Completion criteria |
|---|---|---|
| 4A.1 | State-load feedback | Give state loading its own operation identity. A matching successful reload resolves only its load error; stale responses cannot publish feedback or restore an old scope. Preserve the existing return/rethrow contract. |
| 4A.2 | Start/restart request feedback | Migrate the effective startBattle wrapper. Capture identity before the request, retain persistent failure feedback and resolve it on matching success. Preserve successful collapse and failed-Start visibility. |
| 4A.3 | Start eligibility and tie-order rejection | Migrate the related global validation producers without changing eligibility, tie ordering or request payloads. Keep these errors distinct from transport and refresh failures. Near-field association remains Deliverable 2. |
| 4A.4 | Next-turn feedback | Migrate the shared main/modal Next handler. Preserve mutation-versus-refresh distinctions, uncertain-outcome wording, concurrency guards and no automatic POST retry. |
| 4A.5 | End-battle feedback | Pair End's validation/request failures with its matching successful result. Preserve the existing confirmation and non-resetting behavior. |
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

## Documentation-only validation

This update retains the suggested bounded 4A breakdown and reconciles checkpoint/working-branch references. It changes human-readable documentation only. No application, tests, dependencies, configuration or workflows change; no automated tests were executed and no workflow is dispatched. The message must contain [skip ci]. Reviewed links point to the existing task/handover indexes and sections. README and root TODO/HANDOVER remain accurate for this planning-only update and need no unrelated edits. No new implementation, passing CI or sub-task completion is claimed.
