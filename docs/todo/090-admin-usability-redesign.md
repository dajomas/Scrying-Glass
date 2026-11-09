# 090 - Admin usability and visual redesign

[Back to TODO index](../../TODO.md)

## SG-TODO-009 - Professional, task-focused Admin interface

- Status: in progress; SG-TODO-009.1-009.5 are closed after their recorded validation and user acceptance. Coordinated SG-TODO-012 is also closed. 009.6 is in progress; its sidebar/duplicate-list design is superseded by the user's 2026-11-09 full-width/dialog direction. 009.7 remains proposed.
- Requested: 2026-11-06; incremental redesign, with staged deliveries and subsequent task-specific agreements. 009.5 close-out/sign-off: 2026-11-09.
- Priority: incremental usability improvement; no priority relative to unrelated work agreed. Owner/deadline not assigned.
- Scope: Admin presentation, navigation and interaction clarity. Do not change encounter rules, API semantics, permissions or persistence merely to redesign the interface.

The original phase proposals and detailed 009.1-009.4 history remain in the [immutable pre-009.5-close-out plan](https://github.com/dajomas/Scrying-Glass/blob/cfc7b0f16f929041bc6107dd1f895d24492261c5/docs/todo/090-admin-usability-redesign.md) and phase handovers. The [pre-dialog 009.6 task](https://github.com/dajomas/Scrying-Glass/blob/73de987ba87fbc63af4766f379bdf366c13db80f/docs/todo/090-admin-usability-redesign.md) retains the earlier sidebar/width preparation and evidence boundaries; those UI requirements are superseded, not silently claimed completed.

## Preparation and compatibility gates

Inspect live templates, stylesheets, loaded modules, source assembly, tests and CI before changes. Preserve dark/gold identity, fixed controls/feedback, context, drafts/manual preferences and action availability across refresh. Responsive/keyboard checks apply to each increment; 009.7 is consolidation, not permission to defer them.

Related accepted boundaries:

- [SG-TODO-005](050-admin-initial-visibility.md): native input/roster collapse and parent/child controls remain. The user's new dialog requirement explicitly replaces inline Encounter tools automatic visibility, not the independent lair controller.
- [SG-TODO-007](070-monster-button-layout.md): single-line roster controls, local overflow/focus exposure and removed Damage/Heal/Turn controls remain; replacement action menus are not introduced.
- [SG-TODO-008](080-source-size-refactors.md): preserve source assembly/size constraints and tracked Admin failure marker.

## Processing order and phase status

| Order | Subtask | Deliverable/status | Dependencies |
|---|---|---|---|
| 1 | SG-TODO-009.1 | Shared visual foundations - closed | Baseline inspection |
| 2 | SG-TODO-009.2 | Header/action hierarchy - closed | 009.1 |
| 3 | SG-TODO-009.3 | Consistent panels/forms - closed | 009.1/009.2 |
| 4 | SG-TODO-009.4 | Rosters/contextual bulk actions - closed | 009.3 |
| 5 | SG-TODO-009.5 | Workflow navigation - closed 2026-11-09 | Agreed navigation and initiative baseline |
| 6 | SG-TODO-009.6 | Full-width live workspace and tools dialog - in progress | Closed 009.5/015 baseline |
| 7 | SG-TODO-009.7 | Feedback/responsive/accessibility consolidation - proposed | 009.1-009.6 |

The [agreed sequence](115-admin-delivery-sequence.md) remains 018, 009.5, 015, 009.6, 009.7, coordinated 016/017. 018, 009.5 and 015 remain closed. No later task is started by this revision.

### SG-TODO-009.1 - Shared visual foundations

Closed 2026-11-06 on recorded corrective local/CI evidence and user acceptance. Implementation e632eba99e00695c7f002148bde8c0aee386d4fe; correction 9a96b5a125c0b22b18218769c9c5cf2508a60ac0. [260 handover](../handover/260-admin-visual-foundations.md) retains full evidence, accepted tokens, dark/gold surfaces, control/focus treatment and unchanged combatant/display colors.

### SG-TODO-009.2 - Header and action hierarchy

Closed 2026-11-06 after recorded correction/acceptance. Implementation a6b910d94c3b846e128d01bc6baa10b48228770f; test correction aa82b45629cce7b49164d5ad7c1304481f20bbd7. [270 handover](../handover/270-admin-header-hierarchy.md). Preserve fixed context/actions/feedback, More, Next emphasis and distinct End/Reset behavior.

### SG-TODO-009.3 - Consistent panels and forms

Closed 2026-11-06 after covering local/CI and user acceptance of 588831fb1ece198fefee3a2422410123a8f1f175. [280 handover](../handover/280-admin-panel-forms.md). Original-node grouping, labels and native disclosures preserve values, validation, IDs and handlers.

### SG-TODO-009.4 - Scannable rosters and contextual bulk actions

Closed 2026-11-06 with coordinated 012. [310 handover](../handover/310-admin-rosters.md). First increment 834c4c3d0a7d963bb44b17dc6346447ec18dc21b; HP option-2 increment 90dcfab919556ac94d05c44c0ec0e775fab32f9d; Turn removal d91f73bfe121870296a1df79f58c58c21bcaeb59. Retain read-only roster HP, Edit-dialog changes, counts/Clear selection, contextual availability and local scrolling. Search/filter, row expansion and action-menu replacements were excluded from accepted scope, not left as unfinished requirements.

### SG-TODO-009.5 - Workflow-based navigation

Closed 2026-11-09 on explicit user sign-off/request. [Completed contract](095-admin-workflow-navigation.md) and [350 handover](../handover/350-admin-workflow-navigation.md) retain scope/history. Tabs retain contexts, original forms, drafts/files/selections, input/roster collapse and independent lair gating. The later 009.6 dialog intentionally supersedes inline tools visibility; it does not reopen 009.5.

Successful CI 42616924220 attempt 1 covers c7c51725c5ac7724fc78ffd1931173cd1d19e0b8; publication 1c1c6323b119b1a7e71a93571985c214183819de. The user's accepted later wording cfc7b0f16f929041bc6107dd1f895d24492261c5 has matching template/test text but no separately supplied covering CI; that boundary remains historical. Preserve the user's copy and accepted bonus/name form behavior.

### SG-TODO-009.6 - Focused live encounter workspace

Status: in progress. The user revoked Admin-page verification and subsequently requested removal of the Participants in turn order section and sidebar, a full-width Battle section, and on-demand Encounter tools. Code/tests/documentation for that revised direction are prepared for bound approval; covering CI and renewed user acceptance remain pending. [370 handover](../handover/370-live-encounter-workspace.md) records implementation and limits.

Current contract:

- Remove the duplicate participant overview and split workspace completely. Original Battle/current-turn action access, Characters, Monsters and Activity log keep their normal full-width flow, without reserved sidebar space.
- The existing Live-view Encounter tools opener opens a closed-by-default dialog, not an inline panel. Battle start, Next, End and refresh never open it automatically.
- Move the original tools section once; retain IDs, handlers, native details, draft inputs/files, selected target, scoped viewer status, Undo, health/effects/checkpoint/backup operations and existing polling. Closing is not Save or Reset.
- Provide a named modal dialog, internal scrolling, sticky Close, focus containment/background inertness, Escape and focus return. Busy tool operations and visible nested modals block parent dismissal; nested modals remain above it and handle their own Escape.
- Preserve independent lair placement/controller, roster visibility/actions/local overflow, header Next/End/Reset semantics, Battle Actions/Next and SG-TODO-015 summaries. No combat, permissions, schema, provider or socket changes.
- Keep the activity disclosure and a single visible heading. Existing tab selection and native roster/input preferences remain stable.

The inline createEncounterVisibility helper remains available for compatibility, but the Admin shell no longer uses it; updateEncounterToolsVisibility is a non-opening compatibility hook. features.js exposes only a readonly busy-state function for the dialog guard. Matching assets are versioned together.

Executed: complete revised workspace and visibility modules passed Node syntax checks; revised CSS parsed; all four updated Python regression files passed AST parsing. Isolated Chromium at 1440/375 passed closed-by-default/transition behavior, bounded dialog size/scroll, original input retention, focus return/background inertness, busy/nested guards and idempotence, with no page errors. Small Node compatibility-helper checks passed. These fixtures use synthetic DOM/state and a stub busy getter, not the full features module, real saves or authenticated server.

Prepared full-Admin/intercepted-HTTP tests replace deliberately obsolete split-list/inline-auto-open expectations, retaining navigation, lair gates, drafts/selections, equal Battle/roster/log widths, scoped viewer one/zero/unavailable/failure/recovery, native Next/Battle Actions and history assertions. Added dialog keyboard/focus/draft checks and a held real-feature-save fixture for busy dismissal. No tests are skipped to hide obsolete behavior; unrelated suites remain. The full revised modules and existing suite have not run locally; existing CI discovery/visual upload covers them, without workflow changes. Use normal CI, no [skip ci].

Historical delivery: 8228b649c47f5df2b293608bd88e8153248c93bb had successful run 42627843410 attempt 1; 110e210e16bcabe002718805443af807f210ef88 added scoped display status/sidebar fixes; 73de987ba87fbc63af4766f379bdf366c13db80f delivered full-width rosters. The initial green result is not evidence for the new dialog design. Previously revoked verification remains revoked.

Remaining gates: covering CI and fresh main-page/dialog screenshots; real campaign viewer count; desktop/narrow/keyboard review, nested and busy behavior, close/reopen drafts, native roster and combat actions and independent lairs. Require renewed task-specific user acceptance before closure, not an inference from a push, fixtures or older green CI.

### SG-TODO-009.7 - Feedback and final usability hardening

Status: proposed. Preserve the previously proposed scope: actionable success/error distinctions, reviewed changes to existing five-second global-message behavior, near-field validation and rejected Join battle context, persistent connection problems, target-specific destructive confirmations, responsive/local overflow/zoom/contrast/focus/tab/menu/announcement checks. Completion requires keyboard and desktop/narrow acceptance; no timing/feedback changes are silently included in 009.6.

## Validation and delivery requirements

Keep fixture, mocked, authenticated and live-server evidence distinct. Prepare targeted regressions and retain unrelated coverage. Review actual covering CI and task-specific acceptance before closure. No new authenticated live TCP/provider, process-restart or exhaustive accessibility result is claimed. This implementation increment uses normal CI without [skip ci]; it does not close overall 009 or start 009.7.
