# 090 - Admin usability and visual redesign

[Back to TODO index](../../TODO.md)

## SG-TODO-009 - Professional, task-focused Admin interface

- Status: in progress; SG-TODO-009.1-009.5 are closed after their recorded validation and user acceptance. Coordinated SG-TODO-012 is also closed. 009.6 is in progress with full-width sections, an on-demand tools dialog and the user's new independent-panel requirement. 009.7 remains proposed.
- Requested: 2026-11-06; incremental redesign, with staged deliveries and subsequent task-specific agreements. 009.5 close-out/sign-off: 2026-11-09.
- Priority: incremental usability improvement; no priority relative to unrelated work agreed. Owner/deadline not assigned.
- Scope: Admin presentation, navigation and interaction clarity. Do not change encounter rules, API semantics, permissions or persistence merely to redesign the interface.

The original phase proposals and detailed 009.1-009.4 history remain in the [immutable pre-009.5-close-out plan](https://github.com/dajomas/Scrying-Glass/blob/cfc7b0f16f929041bc6107dd1f895d24492261c5/docs/todo/090-admin-usability-redesign.md) and phase handovers. The [pre-dialog 009.6 task](https://github.com/dajomas/Scrying-Glass/blob/73de987ba87fbc63af4766f379bdf366c13db80f/docs/todo/090-admin-usability-redesign.md) retains earlier sidebar/width preparation; those UI requirements are superseded, not silently claimed completed.

## Preparation and compatibility gates

Inspect live templates, stylesheets, loaded modules, source assembly, tests and CI before changes. Preserve dark/gold identity, fixed controls/feedback, context, drafts/manual preferences and action availability across refresh. Responsive/keyboard checks apply to each increment; 009.7 is consolidation, not permission to defer them.

Related accepted boundaries:

- [SG-TODO-005](050-admin-initial-visibility.md): retain one-shot initial input collapse and manual choices. The user's explicit new requirement supersedes Campaign-to-character and Battle Setup-to-monster/lair visibility dependencies; it does not reopen the closed task or remove independent lair eligibility.
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

Closed 2026-11-09 on explicit user sign-off/request. [Completed contract](095-admin-workflow-navigation.md) and [350 handover](../handover/350-admin-workflow-navigation.md) retain scope/history. Tabs retain contexts, original forms, drafts/files/selections, input/roster collapse and independent lair gating. Later explicit 009.6 requirements supersede inline tools visibility and parent-dependent panel availability; they do not reopen 009.5.

Successful CI 42616924220 attempt 1 covers c7c51725c5ac7724fc78ffd1931173cd1d19e0b8; publication 1c1c6323b119b1a7e71a93571985c214183819de. The user's accepted later wording cfc7b0f16f929041bc6107dd1f895d24492261c5 has matching template/test text but no separately supplied covering CI; that boundary remains historical. Preserve the user's copy and accepted bonus/name form behavior.

### SG-TODO-009.6 - Focused live encounter workspace

Status: in progress. Full-width/dialog revision delivered at 540ab598d65bb7002d3e8184e59cd5c596e2c90f; independent controls delivered at 85c2cdfa365560d382522865aef41ba2ac65b2bc. Covering run 42649656592 attempt 1 failed in the JavaScript stage because the active-combatant VM fixture omitted window. A targeted test-only correction is prepared for approval and passes locally; full corrective CI and renewed user acceptance remain pending. [370 handover](../handover/370-live-encounter-workspace.md#vm-fixture-correction---2026-11-09) records evidence and limits. Previously revoked verification remains revoked.

Current contract:

- Original Battle/current-turn action access, Characters, Monsters and Activity log retain full-width flow. No duplicate participant overview, split grid or reserved sidebar space.
- Campaign always exposes its three input/roster panel controls. Campaign Input affects only Campaign Setup; Character Input affects only Add Character; Character Display affects only the Characters roster.
- Battle Preparation exposes all its mapped panel controls independently. Battle Setup no longer closes Add Monsters or hides its button, nor imposes a parent visibility dependency on lair controls. The separate has-lair eligibility gate still applies; workflows still exclude controls belonging to other tabs.
- Successful Start battle closes all native Campaign/Battle input and roster panes, including an explicit restart while active. Failed Start does not collapse them. Native eligibility/tie handling and POST method/headers/order payload/error notice are unchanged. Ordinary refresh/Next does not reclose manually reopened panels; native End/Reset restoration is retained.
- Tools remains an explicit closed-by-default Live-view dialog; transitions never open it automatically. Original controls/drafts/files, scoped status and operations, focus/inert/Close/Escape/busy/nested handling remain unchanged.
- Retain native roster/input toggles, labels/aria-expanded, full-width geometry, local overflow, selections/drafts, independent lairs, header controls, Battle Actions/Next and 015 summaries. No backend, permissions, schema, provider or socket change.

Implementation: admin-initial-visibility.js retires the two paneDependencies entries before its existing one-shot initialization and restores only the six ordinary buttons' availability. Original handlers dynamically consult the map and now affect one panel. It mirrors the inspected native startBattle submit helper with setAllHideablePanesHidden(true) added after a successful POST and before load, not on failed requests or ordinary refresh. admin-shell.css removes the two parent-hidden selectors. The initial-visibility asset is version 2. No core fragment/assembly/failure-marker changes or second panel-state model.

Executed during preparation of that increment: complete 3,865-byte JavaScript Node syntax check, 1,312-byte CSS parse, and AST parsing of both updated/new regression modules. Isolated real Chromium at 1440/375 with actual proposed initial module and representative native-controller/DOM fixtures passed independent buttons, retained availability, initial collapse, one-time battle collapse, manual reopening across refresh, end restoration, idempotence and prior-hook return with no page errors. Further mocked-request Chromium checks passed successful Start/restart collapse, same endpoint/method/order, and failure retaining panels/error reporting. These are not full Admin, real server or authenticated transport checks.

The five native-controller/CSS methods and two full-Admin/intercepted-HTTP panel methods were not run locally during initial preparation. Subsequently, the covering CI Python/browser stage passed on 85c2cdfa365560d382522865aef41ba2ac65b2bc; the overall run nevertheless failed as recorded below. Existing initial-visibility, dialog, navigation, lair, combat and security coverage remains.

VM fixture correction, 2026-11-09: publication 445f5d88dd54998a219974ebf1842a8cd590f6a6 contains ci-results-42649656592-attempt-1. run.json/jobs.json report failure overall, with syntax/import, Python/browser, pytest, standalone audit/browser and artifact upload successful; JavaScript failed. Workflow reader file-000038 part-000121/122 identifies ReferenceError at window.scryingEncounterToolsBusy in tests/encounter-active-combatant.test.cjs. The fixture now aliases context.window=context before VM evaluation and asserts window===globalThis plus busy-accessor initialization. All original selection/turn/draft assertions are retained. No runtime code, assets or workflow changes.

Executed for the test fix: reconstructed full production features.js and old fixture were verified against their live Git blob SHAs 140b87b5f4e55cfbedd33ce59c5780bfd289e732 and 18fbfd5c9b753b1b68d9d614cf3f087071d4c082. The old fixture reproduced window is not defined; the complete corrected 3,353-byte fixture passed node --test: 1 test passed, 0 failed, 0 skipped. This is the existing isolated DOM/HTTP mock fixture, not browser/live-server verification or a full-suite rerun. Normal CI applies to this test-code commit without [skip ci].

Historical delivery: initial 8228b649c47f5df2b293608bd88e8153248c93bb had successful run 42627843410 attempt 1; 110e210e16bcabe002718805443af807f210ef88 added scoped display status; 73de987ba87fbc63af4766f379bdf366c13db80f delivered full-width rosters; 540ab598d65bb7002d3e8184e59cd5c596e2c90f replaced the sidebar/list with the tools dialog. Older green CI and the new targeted local pass do not convert failed run 42649656592 into success.

Remaining gates: successful covering corrective CI; desktop/narrow Campaign/Preparation controls, independent panels/drafts, successful Start/restart collapse, failed Start preservation, refresh reopening, lair eligibility and tools-dialog behavior; real campaign viewer count and renewed task-specific acceptance before closure.

### SG-TODO-009.7 - Feedback and final usability hardening

Status: proposed. Preserve the previously proposed scope: actionable success/error distinctions, reviewed changes to existing five-second global-message behavior, near-field validation and rejected Join battle context, persistent connection problems, target-specific destructive confirmations, responsive/local overflow/zoom/contrast/focus/tab/menu/announcement checks. Completion requires keyboard and desktop/narrow acceptance; no timing/feedback changes are silently included in 009.6.

## Validation and delivery requirements

Keep fixture, mocked, authenticated and live-server evidence distinct. Prepare targeted regressions and retain unrelated coverage. Review actual covering CI and task-specific acceptance before closure. No new authenticated live TCP/provider, process-restart or exhaustive accessibility result is claimed. This test correction uses normal CI without [skip ci]; it does not close overall 009 or start 009.7. README and root indexes were reviewed/reused and left unchanged: generic runtime descriptions, links and in-progress status remain accurate.
