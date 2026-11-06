# 090 - Admin usability and visual redesign

[Back to TODO index](../../TODO.md)

## SG-TODO-009 - Professional, task-focused Admin interface

- Status: in progress; SG-TODO-009.1, SG-TODO-009.2 and SG-TODO-009.3 are closed after verified validation and user acceptance. SG-TODO-009.4 increment 1 is included with validation and its HP follow-up pending. Phases 009.5-009.7 remain proposed and are not implemented.
- Requested: 2026-11-06. The user requested recording the design suggestions and processing order, agreed staged delivery, and explicitly requested implementation through 009.4 with SG-TODO-012. The user chose option 2 for character HP and approved the two-commit split described below.
- Priority: incremental usability improvement; no priority relative to other tasks agreed.
- Owner and deadline: not assigned.
- Scope: Admin presentation, navigation and interaction clarity; do not change encounter rules, API semantics, permissions or persistence merely to redesign the interface.
- Later phases and their visual values remain recommendations, not approval of every design decision or authorization to implement them.

## Preparation and compatibility gates

Before implementation, inspect live templates, stylesheets, loaded enhancement modules, source assembly, tests and CI. Capture representative current screenshots and baseline interactions at desktop and narrow widths; the original suggestions were not a fresh visual audit. Record explicitly when these checks are pending rather than claiming they ran.

Retain the dark/gold companion identity. Evaluate quieter neutral surfaces and teal/amber grouping accents against the existing theme. Preserve fixed controls and visible global feedback above the scrolling workspace, active campaign/setup context, manual pane choices, independent lair gating, form values and existing actions across navigation and refresh.

Related accepted work:

- [SG-TODO-005: initial section visibility](050-admin-initial-visibility.md): preserve parent/child controls and per-page initial collapse. Replacing toggles requires an explicit visibility mapping.
- [SG-TODO-007: single-line monster buttons](070-monster-button-layout.md) and [row-layout handover](../handover/250-monster-button-layout.md): preserve 11 monster-row buttons, local scrolling/focus exposure and removed row Damage/Heal controls. Menus/details as alternatives require agreement.
- [SG-TODO-008: source-size refactors](080-source-size-refactors.md): preserve source assembly and code-size constraints; do not overwrite the tracked Admin script failure marker.

## Agreed staged processing order

Process phases 1 through 7 in order, reviewing each coherent increment before structural changes. Dependencies recommend sequence, not delivery of the whole redesign in one commit. Accessibility and responsive checks apply to every phase; phase 7 is consolidation, not permission to defer basic usability.

| Order | Subtask | Deliverable | Dependencies |
|---|---|---|---|
| 1 | SG-TODO-009.1 | Shared visual foundations (closed) | Baseline inspection |
| 2 | SG-TODO-009.2 | Header and action hierarchy (closed) | 009.1 |
| 3 | SG-TODO-009.3 | Consistent panels and forms (closed) | 009.1, 009.2 |
| 4 | SG-TODO-009.4 | Scannable rosters and contextual bulk actions (in progress) | 009.3; agreement for changed row controls |
| 5 | SG-TODO-009.5 | Workflow-based navigation | 009.2-009.4; agreed visibility mapping |
| 6 | SG-TODO-009.6 | Focused live encounter workspace | 009.4, 009.5 |
| 7 | SG-TODO-009.7 | Feedback, responsive and accessibility hardening | 009.1-009.6 |

### SG-TODO-009.1 - Shared visual foundations

Status: closed (completed), 2026-11-06, at the user's explicit request after corrective local/CI verification and acceptance of notification behaviour/foundation consistency on the correct server. Initial implementation e632eba99e00695c7f002148bde8c0aee386d4fe; correction 9a96b5a125c0b22b18218769c9c5cf2508a60ac0. See [full implementation and close-out history](../handover/260-admin-visual-foundations.md).

- Reusable tokens for surfaces, borders, typography, spacing, control heights and radii.
- Quieter panels, subtle borders/minimal shadows and restrained campaign/character teal and battle/monster amber. Preserve appropriate fantasy branding without decorating operational controls excessively.
- Proposed spacing scale 4/8/12/16/24/32 px, coherent UI type and geometry, subject to visual review.
- Consistent primary accent, red destructive operations and non-colour-only grouping/state.

Acceptance: panels, tables, forms and modals share visual rules; text/focus/state remain readable; theme and combatant/display colours are not accidentally overridden.

### SG-TODO-009.2 - Header and action hierarchy

Status: closed (completed), 2026-11-06, at the user's request after covering corrective local/CI success and visual/workflow acceptance. Initial implementation a6b910d94c3b846e128d01bc6baa10b48228770f; test-only correction aa82b45629cce7b49164d5ad7c1304481f20bbd7. See [full implementation and close-out history](../handover/270-admin-header-hierarchy.md).

- Compact fixed header: product, active campaign, saved setup and encounter state/round.
- Predictable context/navigation/global-actions/feedback areas; infrequent global actions in labelled More where appropriate.
- Entity-local setup and backup operations remain local.
- One dominant current-task action, quieter secondary actions, separated End and Reset All in a labelled danger section.

Acceptance: context/feedback remain visible while scrolling; wrapped controls/messages do not overlap the workspace; global/local actions are distinct and keyboard accessible.

### SG-TODO-009.3 - Consistent panels and forms

Status: closed (completed), 2026-11-06, after verified successful local and CI validation of implementation 588831fb1ece198fefee3a2422410123a8f1f175 and the user's explicit desktop/narrow visual and workflow acceptance. See [implementation, verification and close-out](../handover/280-admin-panel-forms.md).

- Standardize anatomy: concise title, optional description, related fields, main action and secondary actions.
- Task-oriented labels: Add character for entry; Characters for the roster.
- Labels above inputs, clear mandatory fields and related control groups.
- Keep common actions visible; use clearly named expandable import/export, backup or advanced sections where appropriate, not concealment merely to reduce button counts.

The increment groups entry/setup controls using existing nodes, adds descriptions/action areas and native background/.monster disclosures initially open. Existing viewer/backup disclosure defaults and visible CSV/setup import controls remain. It does not implement roster restructuring, tabs, encounter-workspace restructuring or revised feedback timing.

Acceptance: purposes/required values are clear; disclosures expose accurate accessible state; forms retain values, validation, existing IDs/handlers and submit behaviour. These phase gates are accepted on covering local/CI evidence and user visual/workflow confirmation, not on syntax checks alone. Retained fixture/live-server limitations are documented in the handover.

### SG-TODO-009.4 - Scannable rosters and contextual bulk actions

Status: in progress, 2026-11-06; increment 1 is included with covering CI and acceptance pending. Alternative action-menu design still requires agreement against SG-TODO-007. See [roster delivery record](../handover/310-admin-rosters.md).

- Structured rows with clear names, aligned numeric values, concise textual status and immediately visible relevant HP/initiative/combat state.
- Consider search/filter and collection-level Add; separate table-wide and row controls.
- Show selected counts/contextual bulk actions, retaining Select all/Clear selection.
- Evaluate row expansion/details for secondary information. A frequent visible action plus overflow is an option, not approval to replace accepted single-line controls.

Approved two-commit delivery: (1) roster presentation, selected counts/Clear selection, contextual mutation availability and local scrolling, preserving current HP editing; (2) SG-TODO-012 option 2, read-only character current/max HP like Monsters, with both values editable through the existing Edit dialog, save/reload coverage and corrected README/User Guide instructions. The user explicitly selected option 2 and approved this split. Increment 1 does not remove inline HP inputs or implement 012. No character HP mechanics, provider/API/persistence behaviour or SG-TODO-013 keyboard remapping is changed by it.

Search/filter, collection Add relocation, row expansion and action menus were considered but not added in increment 1; existing access and original row controls are retained. No filtered selection scope is introduced. Selection commands remain available at zero selected while mutation options are disabled. Both task acceptance and remaining work must be reviewed before 009.4/012 closure; this partial delivery is not completion.

Acceptance: scan/select/edit/bulk workflows remain without accidental mutations; selection survives or resets predictably on refresh/filter; keyboard focus is exposed within local scrollers; removed row HP-change controls stay removed.

### SG-TODO-009.5 - Workflow-based navigation

Status: proposed; tabs and visibility replacement require agreement.

- Proposed Campaign (selection, characters, backups), Battle preparation (setups, monsters, initiative, lair) and Live encounter (order, participants, tools, log) views.
- Prefer compact tabs over a large sidebar initially; active campaign/setup context visible in every view.
- Reduce global toggle clutter only after explicitly mapping manual visibility and automatic battle behaviour.

Acceptance: discoverable destination for every capability; changing views does not submit/lose edits/mutate encounters; active tab/focus accessible; initial collapse, dependent controls, lair gating and tools restoration preserved or replaced under explicit agreement.

### SG-TODO-009.6 - Focused live encounter workspace

Status: proposed.

- Turn order/participants get the largest area; tools alongside on wide screens and below on narrow.
- Identify round/active participant, emphasize Next and keep HP/conditions/upcoming turns scannable.
- Collapsible activity log below; setup forms outside the primary combat view without losing access.
- Preserve Next from Battle Actions and alternate damage/healing/statistics workflows.

Acceptance: efficient/correctly scoped combat; cover advancement, end/reset, lair behaviour, tools restoration and activity history; narrow layouts retain essential controls.

### SG-TODO-009.7 - Feedback and final usability hardening

Status: proposed.

- Distinguish brief success from actionable errors. Proposed success expiry and persistent errors require explicit review of the current five-second global-message rule.
- Near-field validation; rejected Join battle identifies missing initiative and the affected combatant/field.
- Persistent connection problems until resolved; destructive confirmations identify affected targets.
- Check responsive stacking, local overflow, zoom, labels, contrast, focus/order, tab/menu semantics and announcements; avoid disruptive movement when feedback appears.

Acceptance: actionable visible feedback without colour/short-timeout dependence or overlap; keyboard-only and desktop/narrow usability.

## Validation and delivery requirements

Prepare targeted regressions, retain existing tests and verify actual CI coverage. Fixtures are not authenticated live-server evidence. Review campaign/setup active/inactive; initial/delayed state; manual panes; start/end/reset; lair enabled/disabled; refresh/rerender; row selection/filter/bulk; missing initiative; successful/failed saves; connection loss/recovery; destructive confirmations; keyboard/narrow layouts.

Separate executed results from pending/manual checks. Obtain user visual/workflow acceptance before closing; commits alone do not complete phases. Update user documentation, TODO and handover proportionally with each increment.

## Retained delivery and verification history

This section consolidates duplicated narrative; the linked 260/270 handovers retain detailed preparation checks, failures, corrective reasoning, reviewed log locations and limits. Earlier statements that 009.3-009.7 were proposed describe the state at 009.1/009.2 delivery, not current phase status.

Original planning on 2026-11-06 changed documentation only and explicitly used [skip ci]. It did not implement the design or validate a browser. The generated final-interface impression remained a concept, not an approved specification. The standing documentation-only skip rule was adopted later; historical deliveries follow their then-applicable instructions.

009.1 initial CI run 42209803055 attempt 1 covered e632eba99e00695c7f002148bde8c0aee386d4fe; evidence 21aa823a6381768c7f2a081597262b7b57d0bfc5 under ci-results-42209803055-attempt-1 reported 1,033 unittest tests OK, 43 pytest passes and four uploaded screenshots. Review identified blank notice strips and ambiguous scroll position. The correction collapses whitespace-only notices without changing timers/ARIA and resets screenshot scroll/asserts header separation; it did not establish a production header-overlap bug.

009.1 corrective source 9a96b5a125c0b22b18218769c9c5cf2508a60ac0 passed local-tests-9a96b5a/run-20261106T122845Z-ogPIRn at 01bd4b232c51aefb7ee185c4099b0e3c381692c7 and CI 42216373147 attempt 1, evidence 7adfe04748b300a3f6686af6714121ea8a0853bb under ci-results-42216373147-attempt-1: configured steps successful, six foundations and four notice Node tests passed, 1,035 unittest tests OK and 43 pytest passes. User confirmed correct-server notification behaviour and foundation consistency. The earlier persistent-strip report came from viewing the wrong server; no extra correction was needed. Closure implied neither a full screen-reader nor exhaustive live-combat audit.

009.2 delivered fixed-header context, original moved Start/Next/End, state-dependent primary emphasis, More, a single-line pane scroller and a closed Reset All danger section. Local evidence eeff8880bceb9e63b2e8a4f8ad9ab40f48878abe and original CI 42227065090 attempt 1 at 42deda5a3f884a9e480b6d37808da59eb7bb5d48 showed a test visibility-precondition error, not an application defect. The correction conditionally opens Campaign/Character based on aria-expanded, verifies visibility, then retains the draft/feedback/layout assertions rather than forcing fields or changing visibility semantics.

009.2 corrective source aa82b45629cce7b49164d5ad7c1304481f20bbd7 passed local evidence 1fcf6f726ccdad8b6315ca2f24cd91fc94d206d0, folder local-tests-aa82b45/run-20261106T141733Z-jal8gK, with overall/full-run summary exits zero, all six header methods passed, repeated suite 1,041 tests OK, 675 connections/zero without explicit close and 43 pytest passes. CI 42232501137 attempt 1 covered that exact source; evidence b4d1f5f69519066ccab88709f93aa1eef643c42f under ci-results-42232501137-attempt-1 reports workflow/job/configured-step success, six header methods passed, 1,041 unittest tests OK, 43 pytest passes and ten uploaded screenshots. Upload/collection is not assistant visual inspection. User visual/workflow acceptance was already given and was not requested again. Original failed results are historical diagnosis, not closure evidence. Later runner cleanup d0a1f3c2781e882cb651a4cf9f6a2b85e22ebc71 is outside that corrective run's coverage. Original close-outs were documentation-only, executed no fresh tests and did not request a skip under the then-applicable policy; no new run outcome was inferred.

009.3 preparation on 2026-11-06 passed enhancement JavaScript syntax, CSS stylesheet parsing and regression Python AST parsing. Full application/browser execution and visual baseline/after review were not performed during preparation. Existing CI discovery/upload covers the new regression module and screenshot paths. The user requested implementation and subsequently a commit with CI. That mixed delivery omitted [skip ci]; its later verified results and acceptance are recorded below and in the 280 handover.

## SG-TODO-009.3 verified close-out - 2026-11-06

Implementation: 588831fb1ece198fefee3a2422410123a8f1f175. Successful local evidence: b000d0fc753ce6b6d430b10b6e32f07c6c8482bd, folder local-tests-588831f/run-20261106T152634Z-3P6S1l. Completed full run and overall exit are zero; all six panel/forms methods explicitly passed; repeated connection-audit suite reports 1,053 tests OK, 676 connections and zero without explicit close; pytest reports 43 passes. Main unittest log was truncated before its final summary, so that count comes from the complete repeated audit log.

Successful CI: Branch tests run 42242916048 attempt 1, covering the exact implementation SHA on features/perplexity. Evidence: 6f57c24e37e65b15675548d1cd411be0f3a69ea7 under ci-results-42242916048-attempt-1. Workflow/job/configured steps succeeded; six panel/forms methods explicitly passed; main unittest reports 1,053 tests OK, pytest 43 passes and repeated connection audit 1,053 tests OK with 676/0 connections. Four new 009.3 screenshots were included in 14 uploaded/collected fixture images. See the handover for reviewed log locations and limits.

The user explicitly accepted SG-TODO-009.3 in response to desktop/narrow visual and workflow acceptance on 2026-11-06. This is user acceptance, not an assistant-executed authenticated live-server or exhaustive accessibility/combat audit. Only 009.3 closed in that update; 009.1/009.2 stayed closed and overall SG-TODO-009 stayed in progress. Statements at that close-out that 009.4-009.7 and SG-TODO-011 were proposed describe that historical point; subsequent task records supersede them.

That close-out changed documentation only, ran no new tests and left application/tests/workflows unchanged. README.md and HANDOVER.md remained accurate without edits. Its commit included [skip ci], with no separate workflow dispatch or inferred new outcome.

## SG-TODO-009.4 increment 1 - 2026-11-06

The first of two user-approved commits includes roster presentation and selection context only, retaining inline character HP. New assets, source/browser regressions, template wiring and the indexed handover accompany it. Preparation passed JavaScript syntax, stylesheet parsing, regression AST and simplified Chromium checks of native option availability, selected count, underlying selection clearing, focus return, inline HP and existing Edit handler/idempotence. The full new module/suite, covering CI, fresh full-Admin screenshots and user visual/workflow acceptance remain pending. README/User Guide inline-HP descriptions remain correct for increment 1; they must change with the second increment. No SG-TODO-012 completion or SG-TODO-013 implementation is claimed. See the 310 handover for exact checks, fixture limitations and remaining work.
