# 090 - Admin usability and visual redesign

[Back to TODO index](../../TODO.md)

## SG-TODO-009 - Professional, task-focused Admin interface

- Status: in progress; SG-TODO-009.1-009.6 are completed/closed on their recorded validation and user acceptance. Coordinated SG-TODO-012 is also closed. 009.7 is in progress for inspection/scoping at the user's 2026-11-09 request; no 009.7 application increment is delivered here.
- Requested: 2026-11-06; incremental redesign with staged deliveries and task-specific agreements. 009.6 renewed sign-off and close/move-on request: 2026-11-09.
- Priority: incremental usability improvement; no priority relative to unrelated work agreed. Owner/deadline not assigned.
- Scope: Admin presentation, navigation and interaction clarity; preserve encounter rules, API semantics, permissions and persistence unless an explicitly reviewed task requires a change.

The original 009.1-009.4 history remains in the [pre-009.5-close-out plan](https://github.com/dajomas/Scrying-Glass/blob/cfc7b0f16f929041bc6107dd1f895d24492261c5/docs/todo/090-admin-usability-redesign.md) and phase handovers. The [pre-009.6-close-out task](https://github.com/dajomas/Scrying-Glass/blob/a7c7614f23acb7a502c3e8c48f579faacfe1fc12/docs/todo/090-admin-usability-redesign.md) retains the detailed dialog, independent-panel preparation and failed-run correction record. Current closure supersedes stale pending wording, not historical evidence.

## Compatibility and processing order

Preserve accepted dark/gold identity, fixed context/actions/feedback, original forms/drafts/files/selections, full-width rosters, local scrolling and source assembly/size constraints. Closed SG-TODO-005 initial collapse is retained, while explicit 009.6 requirements supersede parent-dependent panel controls and inline auto-opening Encounter tools. Lair eligibility remains independent. Closed SG-TODO-007 row-control scope and SG-TODO-008 failure-marker boundaries remain.

| Order | Subtask | Status | Dependencies |
|---|---|---|---|
| 1 | SG-TODO-009.1 | Shared foundations - closed | Baseline inspection |
| 2 | SG-TODO-009.2 | Header/action hierarchy - closed | 009.1 |
| 3 | SG-TODO-009.3 | Panels/forms - closed | 009.1/009.2 |
| 4 | SG-TODO-009.4 | Rosters/bulk actions - closed | 009.3 |
| 5 | SG-TODO-009.5 | Workflow navigation - closed | Agreed navigation/initiative baseline |
| 6 | SG-TODO-009.6 | Full-width workspace, dialog and independent controls - completed/closed 2026-11-09 | Closed 009.5/015 baseline |
| 7 | SG-TODO-009.7 | Feedback/responsive/accessibility - in progress, inspection/scoping | Closed 009.1-009.6 |

The [agreed sequence](115-admin-delivery-sequence.md) remains 018, 009.5, 015, 009.6, 009.7, coordinated 016/017. 018, 009.5, 015 and 009.6 are closed. Overall 009 remains in progress until 009.7 is accepted; 016/017 remain proposed. No owner/deadline is added.

### SG-TODO-009.1 - Shared visual foundations

Closed 2026-11-06 on corrective local/CI evidence and user acceptance. Implementation e632eba99e00695c7f002148bde8c0aee386d4fe; correction 9a96b5a125c0b22b18218769c9c5cf2508a60ac0. [260 handover](../handover/260-admin-visual-foundations.md) retains tokens, surfaces, control/focus treatment and unchanged combatant/display colors.

### SG-TODO-009.2 - Header and action hierarchy

Closed 2026-11-06 after correction/acceptance. Implementation a6b910d94c3b846e128d01bc6baa10b48228770f; test correction aa82b45629cce7b49164d5ad7c1304481f20bbd7. [270 handover](../handover/270-admin-header-hierarchy.md). Retain fixed context/actions/feedback, More, Next emphasis and distinct End/Reset behavior.

### SG-TODO-009.3 - Consistent panels and forms

Closed 2026-11-06 after covering local/CI and user acceptance of 588831fb1ece198fefee3a2422410123a8f1f175. [280 handover](../handover/280-admin-panel-forms.md). Retain original-node grouping, labels, native disclosures, values, validation, IDs and handlers.

### SG-TODO-009.4 - Scannable rosters and contextual bulk actions

Closed 2026-11-06 with coordinated 012. [310 handover](../handover/310-admin-rosters.md). Initial 834c4c3d0a7d963bb44b17dc6346447ec18dc21b; HP option-2 90dcfab919556ac94d05c44c0ec0e775fab32f9d; Turn removal d91f73bfe121870296a1df79f58c58c21bcaeb59. Retain read-only roster HP/Edit-dialog changes, counts/Clear selection, contextual availability and local scrolling. Search/filter, row expansion and replacement action menus were excluded from accepted scope, not unfinished requirements.

### SG-TODO-009.5 - Workflow-based navigation

Closed 2026-11-09 on explicit sign-off/request. [Completed contract](095-admin-workflow-navigation.md) and [350 handover](../handover/350-admin-workflow-navigation.md) retain scope/history. Tabs retain context, forms, drafts/files/selections and lair gating. Later 009.6 requirements supersede inline tools and parent-dependent availability without reopening 009.5.

Historical successful CI 42616924220 attempt 1 covers c7c51725c5ac7724fc78ffd1931173cd1d19e0b8; publication 1c1c6323b119b1a7e71a93571985c214183819de. The accepted later copy cfc7b0f16f929041bc6107dd1f895d24492261c5 had matching template/test text but no separately supplied covering run at that phase's closure. Preserve that historical evidence boundary and the user's copy/bonus/name behavior.

### SG-TODO-009.6 - Focused live encounter workspace

Status: completed and closed, 2026-11-09, after successful corrective CI and explicit renewed user sign-off/close request. The renewed sign-off supersedes the earlier revocation of Admin-page verification. It is overall task acceptance, not an invented record of each manual scenario. [370 close-out](../handover/370-live-encounter-workspace.md#sg-todo-0096-close-out---2026-11-09) records evidence and limits.

Accepted final scope:

- Battle, Characters, Monsters and Activity log retain full-width flow; duplicate participant list, split grid and sidebar space are removed.
- Encounter tools is an on-demand Live-view dialog using original controls/drafts/files, scoped viewer status and existing operations. It is closed by default; transitions do not auto-open it. Internal scrolling, focus/inert/return, Close/Escape and busy/nested guards remain.
- Campaign and Preparation controls remain available independently on their tab. Each toggles only its named panel. Lair eligibility is separate; unrelated workflow controls remain excluded.
- Successful Start/restart closes native input/roster panes, failed Start preserves visibility, and refresh/Next retains manual reopening. Eligibility/tie/API payload/error behavior and native End/Reset restoration remain.
- Existing header, roster actions/local overflow, selections/drafts, independent lairs, Battle Actions/Next, 015 summaries and activity disclosure are retained. Core fragments/assembly/failure marker and permissions/schema/provider/socket/combat rules are unchanged by the UI increments.

Delivery: dialog 540ab598d65bb7002d3e8184e59cd5c596e2c90f; independent controls 85c2cdfa365560d382522865aef41ba2ac65b2bc; fixture correction e512dd24a42dde0141193e860b383125248f2f06. Successful Branch tests 42654298154 attempt 1 covers that final exact SHA on features/perplexity. Publication a7c7614f23acb7a502c3e8c48f579faacfe1fc12 contains ci-results-42654298154-attempt-1; reviewed run.json/jobs.json confirm completed/success and all configured validation stages successful.

Failed run 42649656592 attempt 1 on 85c2cdf remains a failure: its JavaScript VM lacked window. The test-only correction aliases context.window=context and retains all behavioral assertions. Targeted local Node test passed before delivery; the later full corrective run resolves the covering-CI gate, not by relabelling the old run. Earlier initial 8228b649/42627843410 success covered the superseded design only.

No outstanding agreed 009.6 implementation item remains after sign-off. CI fixtures and overall acceptance are not an assistant-performed authenticated live-server/provider/process-restart or exhaustive accessibility audit. The user's actual viewer-count/manual scenarios are not individually claimed verified by the assistant. No fresh tests are run for this documentation-only close-out.

### SG-TODO-009.7 - Feedback and final usability hardening

Status: in progress for inspection/scoping, 2026-11-09, at the user's explicit move-on request. No application implementation or acceptance is claimed by this transition. Preserve the settled 009.6 layout rather than reintroducing the rejected sidebar/list or panel dependencies.

Scope retained from the prior proposal:

- Distinguish brief success feedback from actionable errors. Inspect existing five-second global-message behavior and tests; expiry/persistence changes need explicit review before implementation.
- Near-field validation, including affected combatant/missing initiative context for rejected Join battle, without weakening server validation or changing initiative rules.
- Persistent connection-problem feedback until recovery and target-specific destructive confirmations, with existing authorization and confirmation behavior preserved.
- Consolidated responsive/local-overflow/zoom/labels/contrast/focus/tab/menu/announcement checks, including the tools dialog, nested overlays and independent panels. Avoid message-induced overlap or disruptive movement.

Started inspection: static/admin-notification-layout.js was read from the live branch. It observes text changes on four pane notices and suppresses whitespace-only notices; it explicitly does not alter messages or timers. This is a source inspection finding, not a new audit result or a change to notification timing.

Next preparation: inspect global message setter/timers, near-field/API error handling, Join battle rejection, connection/recovery rendering, destructive confirmations, modal keyboard behavior and existing regression/visual fixtures. Produce concrete proposed behavior and targeted acceptance criteria, resolving timing/persistence decisions before code changes. No placeholder implementation, owner/deadline or unspecified migration commitment is created.

Acceptance/delivery gates: actionable visible feedback independent of color/short timeout, retained drafts/actions/context, desktop/narrow and keyboard-only operation, targeted regressions plus covering CI, and task-specific user acceptance. Each implementation delivery includes proportionate documentation and exact bound GitHub approval and runs normal CI unless explicitly instructed otherwise. Do not infer exhaustive scenarios from a future overall sign-off.

## Documentation transition and validation limits

This close-out/scoping transition changes human-readable documentation only and includes [skip ci]. No application code, tests, dependencies, configuration or workflows change; no fresh tests run and no workflow is dispatched. README was reviewed/reused and remains accurate without edits. Root TODO/HANDOVER and this phase record are updated together. Other closed tasks remain closed; no 016/017 implementation or overall-009 closure is included.
