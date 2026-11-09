# 090 - Admin usability and visual redesign

[Back to TODO index](../../TODO.md)

## SG-TODO-009 - Professional, task-focused Admin interface

- Status: in progress; SG-TODO-009.1-009.5 are closed after their recorded validation and user acceptance. Coordinated SG-TODO-012 is also closed. 009.6 is in progress at the user's 2026-11-09 implementation request; 009.7 remains proposed.
- Requested: 2026-11-06; incremental redesign, with staged deliveries and subsequent task-specific agreements. 009.5 close-out/sign-off: 2026-11-09.
- Priority: incremental usability improvement; no priority relative to unrelated work agreed. Owner/deadline not assigned.
- Scope: Admin presentation, navigation and interaction clarity. Do not change encounter rules, API semantics, permissions or persistence merely to redesign the interface.

The original phase proposals, detailed 009.1-009.4 delivery/verification chronology, numerical evidence, failures and close-out notes remain in the [immutable pre-009.5-close-out plan](https://github.com/dajomas/Scrying-Glass/blob/cfc7b0f16f929041bc6107dd1f895d24492261c5/docs/todo/090-admin-usability-redesign.md) and linked phase handovers below. This current consolidation supersedes stale phase-status wording, not historical evidence or outstanding proposed scope.

## Preparation and compatibility gates

Inspect live templates, stylesheets, loaded modules, source assembly, tests and CI before changes. Capture representative desktop/narrow behavior and report checks not executed rather than inventing a visual audit. Retain dark/gold identity, fixed controls and feedback above the scrolling workspace, active campaign/setup context, drafts/manual preferences and action availability across refresh. Accessibility/responsive checks apply to each phase; 009.7 is consolidation, not permission to defer them.

Related accepted boundaries:

- [SG-TODO-005](050-admin-initial-visibility.md): preserve initial collapse and parent/child controls; replacing visibility behavior needs explicit mapping. 009.5 retains native controllers under a separate workflow filter.
- [SG-TODO-007](070-monster-button-layout.md) / [250 handover](../handover/250-monster-button-layout.md): accepted single-line row controls, local overflow/focus exposure and removed Damage/Heal/Turn controls stay. Subsequent accepted presentation leaves 10 visible monster and 7 character controls; menus/details as replacements need agreement.
- [SG-TODO-008](080-source-size-refactors.md): preserve source assembly/size constraints and tracked Admin failure marker.

## Processing order and phase status

| Order | Subtask | Deliverable/status | Dependencies |
|---|---|---|---|
| 1 | SG-TODO-009.1 | Shared visual foundations - closed | Baseline inspection |
| 2 | SG-TODO-009.2 | Header/action hierarchy - closed | 009.1 |
| 3 | SG-TODO-009.3 | Consistent panels/forms - closed | 009.1/009.2 |
| 4 | SG-TODO-009.4 | Rosters/contextual bulk actions - closed | 009.3; agreed row-control scope |
| 5 | SG-TODO-009.5 | Workflow navigation - closed 2026-11-09 | 009.2-009.4; agreed visibility mapping; merged 018 baseline |
| 6 | SG-TODO-009.6 | Focused live encounter workspace - in progress | 009.4/009.5 and closed 015 baseline |
| 7 | SG-TODO-009.7 | Feedback/responsive/accessibility consolidation - proposed | 009.1-009.6 |

The [agreed cross-task sequence](115-admin-delivery-sequence.md) is 018, 009.5, 015, 009.6, 009.7, coordinated 016/017. 018, 009.5 and 015 are closed; the user explicitly requested starting and implementing 009.6. Sequencing alone is not approval of unspecified designs or later external writes.

### SG-TODO-009.1 - Shared visual foundations

Closed 2026-11-06 on verified corrective local/CI evidence and user acceptance. Original implementation e632eba99e00695c7f002148bde8c0aee386d4fe; correction 9a96b5a125c0b22b18218769c9c5cf2508a60ac0. [260 handover](../handover/260-admin-visual-foundations.md) retains full evidence. Accepted tokens/surfaces/borders/type/spacing/control geometry, restrained teal/amber and dark/gold identity, readable focus/states, and unchanged combatant/display colors. The proposed 4/8/12/16/24/32 spacing scale remains part of that historical design record, not a new requirement.

### SG-TODO-009.2 - Header and action hierarchy

Closed 2026-11-06 after verified correction and user acceptance. Implementation a6b910d94c3b846e128d01bc6baa10b48228770f; test correction aa82b45629cce7b49164d5ad7c1304481f20bbd7. [270 handover](../handover/270-admin-header-hierarchy.md) retains full history. Compact fixed context/actions/feedback, More disclosure, local entity operations, state-dependent primary emphasis and separate End/Reset danger behavior are accepted; preserve keyboard access and workspace separation.

### SG-TODO-009.3 - Consistent panels and forms

Closed 2026-11-06 after covering local/CI and desktop/narrow user acceptance of 588831fb1ece198fefee3a2422410123a8f1f175. [280 handover](../handover/280-admin-panel-forms.md). Accepted anatomy, task labels, labels/required markers, original-node grouping and accessible native disclosures preserve values/validation/IDs/handlers. Common import controls remain discoverable. This phase did not itself deliver tabs or focused live layout.

### SG-TODO-009.4 - Scannable rosters and contextual bulk actions

Closed 2026-11-06 with coordinated 012 after covering local/CI, user desktop/narrow acceptance and explicit closure. [310 handover](../handover/310-admin-rosters.md). First roster increment 834c4c3d0a7d963bb44b17dc6346447ec18dc21b; 012 option-2 HP increment 90dcfab919556ac94d05c44c0ec0e775fab32f9d; Turn removal d91f73bfe121870296a1df79f58c58c21bcaeb59. Accepted read-only current/max character HP with existing Edit-dialog editing, structured/scannable rows, counts/Clear selection, contextual mutation availability and local scrolling. Selection commands stay available at zero selected. Search/filter, Add relocation, row expansion and action menus were considered but excluded from the closed agreed scope; do not manufacture unfinished requirements. HP mechanics/provider/API/persistence and later 013 keyboard mapping were not changed by these deliveries.

### SG-TODO-009.5 - Workflow-based navigation

Closed 2026-11-09 on the user's explicit sign-off and request to close/move on. [Current completed contract](095-admin-workflow-navigation.md) and [350 close-out](../handover/350-admin-workflow-navigation.md) retain scope/evidence. Campaign/preparation/live tabs use a separate view filter, native pane controls and independent lair/tools behavior, retained context/drafts/files/selections, keyboard semantics and local scrolling. Accepted follow-ups cover bonus placement/help removal, species-to-blank-name default, missing-bonus overwrite/default zero and concise lookup copy.

Successful CI 42616924220 attempt 1 covers c7c51725c5ac7724fc78ffd1931173cd1d19e0b8; publication 1c1c6323b119b1a7e71a93571985c214183819de. The user's later accepted wording revision cfc7b0f16f929041bc6107dd1f895d24492261c5 changes template and matching test constant; no separate covering CI for that revision is supplied or claimed. Closure records user acceptance of that copy revision, not invented post-edit test execution.

### SG-TODO-009.6 - Focused live encounter workspace

Status: in progress. Initial implementation 8228b649c47f5df2b293608bd88e8153248c93bb has verified successful covering CI 42627843410 attempt 1 (publication a9e6b1bc321596eff2d660a80cc7d35f7b5fc9a6). Sidebar/viewer/log corrections were delivered in 110e210e16bcabe002718805443af807f210ef88; covering results for that correction have not been supplied. On 2026-11-09 the user revoked Admin-page verification and explicitly required full-width Characters and Monsters panels matching Activity log. A roster-width correction is prepared for bound approval; covering CI and renewed user acceptance remain pending. [370 handover](../handover/370-live-encounter-workspace.md) records evidence and limits.

- Only battle/order and read-only participant overview share the upper two-column area with encounter/lair tools; tools stack below the overview at 1000px and narrower.
- Characters and Monsters are full-width panels below that entire area, before Activity log, with the same left/right edges and available width as the log whether tools are open or hidden. On other tabs they retain their original full-width parents and native visibility.
- Round/current participant, HP/current max/temp values, initiative, life state, concentration and nonmechanical effect names are read-only snapshots of authoritative state/order. Missing numbers are not invented zeroes; lairs have no HP/AC.
- Existing fixed Next emphasis, End/Reset separation, Battle Actions/Next and alternate health/statistics workflows remain. Setup forms remain accessible through existing tabs outside the primary combat view.
- Original sections use comment anchors for restoration when leaving Live; no cloned native controls or pane-hidden writes. Native roster actions, selections and table-local horizontal scrolling are preserved.
- Activity history uses a native keyboard-operable disclosure, initially open to preserve existing visibility; its choice survives state refresh and view changes.

The earlier corrective delivery fixed ID-selector precedence for natural connection height/stacked tools, hid the redundant log heading and replaced regular-admin display suppression with current-authorized campaign-scoped connection metadata. Counts are socket connections, not granted accounts or unique users; session/role/grants/selection/socket membership are checked and unavailable/mismatched/failed reads are not zero. No grants/schema/protocol/combat semantics change. Existing polling frequency is unchanged. Its isolated logic/formatter/layout checks passed during preparation; SQLite/seeded-auth and full-Admin coverage remains subject to covering CI, not inferred from the initial green run.

For the width correction, only the original roster sections' Live placement changes: workspace.after(characters, monsters) instead of primary.append. Existing home anchors restore original parents/positions. The matching JS asset version becomes 2; prior feature-JS/live-CSS version-2 fixes are retained. Executed: Node --check on the complete 6,256-byte module, Python AST parsing on the new 4,787-byte regression module, and isolated Chromium at 1440/768/375 proving equal roster/log widths and edges with tools open/hidden/open, local table overflow, no page overflow, original parent/position/hidden-state restoration and draft retention, with no page errors. These use synthetic DOM/state and representative grid CSS, not full Admin or a live server.

Prepared tests/test_live_roster_widths.py has two full-Admin/intercepted-HTTP methods covering both panel edges/width against the real log, placement outside the tools grid, DOM order, refresh with tools open/hidden, local overflow, original nodes/preferences/selections/drafts and view round trips. It captures 0096-WIDTH-full-width-rosters.png at 1440/768/375 for existing artifact upload. The module and full suite were not run locally. Normal CI applies without [skip ci]; no workflow changes.

Remaining gates: review covering CI/screenshots for all corrective changes; verify the actual connected campaign display; require renewed user acceptance after the explicit revocation, including equal Characters/Monsters/log width, tools toggles, desktop/narrow/keyboard operation and retained combat/roster/history behavior. Earlier positive feedback and initial green CI are not current Admin-page acceptance. Do not close on push alone.

### SG-TODO-009.7 - Feedback and final usability hardening

Status: proposed.

- Distinguish brief success from actionable errors; proposed expiry/persistence changes need explicit review of existing five-second global-message behavior.
- Near-field validation, including affected combatant/missing initiative for rejected Join battle.
- Persistent connection problems until resolved and target-specific destructive confirmations.
- Responsive/local overflow/zoom/labels/contrast/focus/tab/menu/announcement checks; avoid message-induced overlap or disruptive movement.

Acceptance: actionable visible feedback independent of color/short timeout, keyboard-only and desktop/narrow usability.

## Validation and delivery requirements

Prepare targeted regressions, retain existing coverage and inspect actual CI. Fixtures are not authenticated/live-server evidence. Record executed checks separately from pending/manual checks, and obtain user acceptance before closing a phase. Review absent/active campaign/setup, initial/delayed state, manual panes, battle transitions, lair gating, refresh/rerender, selection/bulk, missing initiative, saves/failures, connection loss/recovery, destructive confirmations and keyboard/narrow operation as relevant. Do not infer exhaustive per-scenario execution from overall acceptance.

The earlier 009.5 close-out was documentation-only and ran no fresh tests. This 009.6 proposal includes application assets and regressions and therefore uses normal CI, without [skip ci]. No workflow modification/dispatch or overall-009 closure is included. Earlier detailed numerical results and failures remain in the immutable history and indexed handovers, not silently relabelled.
