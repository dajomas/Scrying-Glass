# 097 - SG-TODO-009.7 feedback delivery plan

[Back to TODO index](../../TODO.md)

## Status and authority - 2026-11-09

SG-TODO-009.7 remains in progress and open. The user approved two independently usable feedback deliverables and requested that the seven Deliverable 1 steps and Deliverable 2 target be retained for future reference. This is the current execution plan for the [parent phase](090-admin-usability-redesign.md#sg-todo-0097---feedback-and-final-usability-hardening). It supersedes that section's earlier statements that expiry policy still needs agreement and that only inspection/scoping is authorized. No implementation, validation or phase acceptance is claimed by this planning record. No owner or deadline is assigned.

See the [continuity record](../handover/380-feedback-delivery-plan.md) for preparation state and evidence limits. Steps are preparation/delivery activities within Deliverable 1, not seven separately approved implementation commits. Prefer one coherent implementation commit containing code, tests and necessary documentation.

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

Status: authorized for preparation; not implemented or delivered. Complete all seven steps below. This must be working Admin behavior, not only a standalone controller, renderer, API design or test scaffold.

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

After the complete nonempty payload is reviewed, request bound GitHub confirmation for dajomas/Scrying-Glass, features/perplexity, exact commit message and complete file contents. Push only after approval and exactly as approved. Report the actual commit SHA and truthful validation status. Run normal CI for implementation/test commits; do not include [skip ci] without a specific user instruction. A push is delivery, not evidence of passing CI or acceptance. Review supplied covering CI evidence and obtain fresh approval for corrective writes.

## Deliverable 2 - connection warnings and near-field validation

Status: explicit remaining work after Deliverable 1; not implemented. Integrate persistent connection-failure/recovery warnings, identical-polling-failure deduplication and announcement suppression; field/combatant-associated near-field validation; campaign/setup scope and retry handling; and combined keyboard/responsive regressions. Recovery must not clear unrelated/newer feedback. Preserve the existing initiative gate and server validation rather than rebuilding or weakening them. Do not implement this deliverable merely to enlarge Deliverable 1.

## Remaining phase scope and compatibility gates

Destructive-confirmation review and broader responsive/accessibility hardening remain within 009.7. Completing both feedback deliverables does not automatically close the phase. Cover relevant local overflow/zoom, labels/contrast, focus/tab/menu/announcements, tools dialog/nested overlays and independent-panel interactions; retain correct existing name/scope confirmations. Require covering regressions/CI and task-specific user acceptance before closure.

Preserve accepted 009.6: full-width Battle, Characters, Monsters and Activity log; no duplicate Participants, sidebar or split workspace; on-demand Encounter tools using original controls/drafts and keyboard/focus/busy/nested-dialog behavior; independent Campaign and Preparation controls; successful Start/restart collapse, failed-Start visibility and refresh/Next manual-reopening retention; independent lair eligibility, campaign-scoped viewer status, native roster actions/local scrolling, permissions and combat rules. Historical references never authorize overwriting newer work.

## Planning-commit validation

This record and its indexed continuity links are documentation only. No application/test/workflow files change, no automated tests were executed for this planning update, and no workflow is dispatched. The commit message must contain [skip ci]. README was reviewed against its unchanged live blob and needs no planning-only edit. Subsequent implementation commits require fresh relevant documentation and validation records.
