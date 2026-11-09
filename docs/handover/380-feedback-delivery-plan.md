# 380 - Feedback delivery plan and continuity

[Back to handover index](../../HANDOVER.md)

## Decision and current state - 2026-11-09

The user approved two independently usable feedback deliverables for SG-TODO-009.7, then requested persistence of the seven Deliverable 1 steps and Deliverable 2 target before starting Deliverable 1 step 1. The authoritative execution details and approved ten-point feedback policy are in the [delivery plan](../todo/097-feedback-delivery-plan.md). That plan supersedes earlier pending-policy/inspection-only wording in the parent phase; 009.7 remains open.

Deliverable 1 is integrated global/pane feedback, actual producer migration, accessible rendering/dismissal, operation-related resolution, tests and documentation. Deliverable 2 is connection failure/recovery/deduplication and near-field validation integration with scope/retry and combined keyboard/responsive regressions. Destructive-confirmation review and broader accessibility/responsive hardening remain beyond those feedback deliverables. No application implementation was produced or committed by the preceding chat; no drafts or temporary execution files may be assumed to exist.

## Preparation continuity

Prior live reads covered root instructions, README and indexes, maintenance/CI/source-split documentation, all eight Admin source fragments, templates/admin/190_document_end.html and static/admin-message-timeout.js. These are source inspection, not executed validation. Complete reads may be reused only after live identity verification.

Source findings to carry into step 1: the global timeout observes text and clears after five seconds without severity discrimination; paneNotification clears all pane notices after three seconds; lookup status also writes directly to the pane and manipulates its timer; some successful operations are silent and require related-error resolution; mutation and refresh outcomes need distinct handling. The remaining inventory must inspect enhancement scripts, actual asset loading, accessible/layout interactions and relevant test/CI contracts. Do not describe that inventory or caller migration as complete yet.

Next after this documentation write succeeds: start Deliverable 1 step 1 and produce the concrete caller/integration inventory. Preserve the [closed 009.6 baseline](370-live-encounter-workspace.md#sg-todo-0096-close-out---2026-11-09). No new implementation, test, CI, deployed-server or accessibility success is claimed here.

## Documentation validation and limitations

The current instructions were re-read from live features/perplexity (blob 559999f85828f8320b3e40e083047f5c78c0115b). Root README, HANDOVER and TODO plus relevant previously read task/maintenance/CI/source-split records were identity-verified against live listings before reuse. New section numbers 097 and 380 were checked against live directory listings. The proposed documentation and relative links were reviewed; no automated tests were executed.

This documentation-only commit includes [skip ci], changes no application/test/configuration/workflow files and dispatches no workflow. No commit SHA or observed workflow result is invented. README remains accurate and unchanged. Implementation delivery, covering CI and user acceptance remain separate pending gates.

## User-approved checkpoint 1 of 2 - 2026-11-09

The preceding sections record the original planning-only transition, not the current checkpoint's validation. The user subsequently requested saving preparation before step 4 to features/perplexity-009.7 and explicitly approved two checkpoint commits plus normal CI on that branch. This first checkpoint saves the step-2 controller, view, CSS and their Node/Chromium tests. They are not included in production Admin HTML yet; existing Admin behavior and the accepted 009.6 baseline remain unchanged by this checkpoint. This is an explicit work-in-progress exception to waiting for the whole Deliverable 1, not its completion or a changed Deliverable 2 boundary.

The controller implements explicit severity/operation/target/scope tickets, related retry resolution, persistent errors, success-only 5/3-second timers and stale-result/timer guards. The view supplies textual severity, safe text rendering, stable unrelated nodes, native dismissal and deterministic focus recovery. The source files remain below 20,000 bytes.

Preparation evidence from this conversation: both JavaScript syntax checks passed; 25 Node controller tests and 14 isolated real Chromium rendering tests passed with zero failures/skips; Python AST parsing passed. Four temporary negative controls detected error expiry, unrelated clearing, stale-attempt acceptance and unsafe HTML rendering. These historical focused checks were executed during step 2, not rerun or relabelled as full-Admin tests for this approval. Full repository suites, actual screen-reader/live-server verification and covering CI remain pending.

The Branch tests push filter now includes features/perplexity-009.7, preserving existing targets and all test steps. The new tests are picked up by existing Node and unittest discovery. This implementation/test/workflow checkpoint omits [skip ci]. No workflow dispatch is requested and no triggered/completed/passing run is claimed before evidence exists. The older single-branch wording in 020-ci-and-tests.md is superseded by the live workflow's explicit branch list; its detailed historical evidence remains unchanged.

Checkpoint 2 still needs to save the prepared bootstrap, header/core/lookup/Join-gate/timeout wiring and its 15-test loading fixture. That preparation passed six JavaScript syntax checks and 15 Chromium integration-slice tests, not the full assembled Admin suite. Its temporary neutral compatibility route, unmigrated tools/lair/viewer roots, candidate outcome distinctions, duplicate Join reporting and legacy fixture/bundle-identity updates remain explicit step-4-and-later work. Do not activate or deploy the partial checkpoint as complete feedback behavior.

The [seven-step plan](../todo/097-feedback-delivery-plan.md) remains authoritative and SG-TODO-009.7 remains in progress/open. After both separately approved checkpoint writes, resume step 4. README and root HANDOVER were reviewed against the unchanged baseline and need no component-only edit: production assembly, runtime behavior and indexed links do not change here. The TODO index records checkpoint status in this same proposed commit. No SHA for either checkpoint is invented before its write succeeds.
