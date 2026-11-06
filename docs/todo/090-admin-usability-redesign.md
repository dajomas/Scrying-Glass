# 090 - Admin usability and visual redesign

[Back to TODO index](../../TODO.md)

## SG-TODO-009 - Professional, task-focused Admin interface

- Status: in progress; 009.1 visual foundations implementation included, with CI and visual acceptance pending. No later redesign phase is implemented.
- Requested: 2026-11-06. The user requested recording the preceding design suggestions and a processing order in the TODO list, then agreed staged delivery and requested starting 009.1.
- Priority: incremental usability improvement; no priority relative to other tasks agreed.
- Owner and deadline: not assigned.
- Scope: Admin presentation, navigation and interaction clarity; do not change encounter rules, API semantics, permissions or persistence merely to redesign the interface.
- Later phases and their visual values remain recommendations, not approval of every design decision or authorization to implement them.

## Preparation and compatibility gates

Before implementation, inspect the live templates, stylesheets, loaded enhancement modules, source assembly, tests and CI configuration. Capture representative current screenshots and baseline interactions at desktop and narrow widths; the original suggestions were not a fresh visual audit of the current screen.

Retain the established dark/gold companion identity where appropriate. A quieter neutral surface system and teal/amber grouping accents must be evaluated against that existing theme rather than introducing a conflicting theme by assumption.

Preserve fixed controls and visible global feedback above a shared scrolling workspace. Preserve campaign/setup context, manual pane choices, independent lair gating, form values and existing action availability across navigation and refresh.

Related accepted work:

- [SG-TODO-005: initial section visibility](050-admin-initial-visibility.md): parent/child controls and per-page initial collapse must not regress. Replacing pane toggles with views requires an explicit behaviour mapping.
- [SG-TODO-007: single-line monster buttons](070-monster-button-layout.md) and [row-layout handover](../handover/250-monster-button-layout.md): the accepted 11 monster-row buttons, local horizontal scrolling, focus exposure and removal of row Damage/Heal controls must not be silently reversed. Moving actions into menus or details is a proposed alternative requiring explicit agreement.
- [SG-TODO-008: source-size refactors](080-source-size-refactors.md): preserve source assembly and code-size constraints; do not overwrite the tracked Admin script failure marker.

## Agreed staged processing order

Process phases 1 through 7 in order. Each phase has a stable subtask ID. Stage 009.1 is in progress; later stages remain proposed. Review the result of each coherent increment before proceeding to structural changes. Dependencies indicate the recommended sequence, not a requirement to implement the entire redesign in one commit.

| Order | Subtask | Deliverable | Dependencies |
|---|---|---|---|
| 1 | SG-TODO-009.1 | Shared visual foundations | Baseline inspection |
| 2 | SG-TODO-009.2 | Header and action hierarchy | 009.1 |
| 3 | SG-TODO-009.3 | Consistent panels and forms | 009.1, 009.2 |
| 4 | SG-TODO-009.4 | Scannable rosters and contextual bulk actions | 009.3; agreement for changed row controls |
| 5 | SG-TODO-009.5 | Workflow-based navigation | 009.2-009.4; agreed visibility mapping |
| 6 | SG-TODO-009.6 | Focused live encounter workspace | 009.4, 009.5 |
| 7 | SG-TODO-009.7 | Feedback, responsive and accessibility hardening | 009.1-009.6 |

Accessibility and responsive checks apply to every phase; phase 7 is final consolidation, not permission to postpone basic usability.

### SG-TODO-009.1 - Shared visual foundations

Status: in progress; implementation included, CI/browser execution and user visual acceptance pending. See [implementation and validation record](../handover/260-admin-visual-foundations.md).

- Establish reusable tokens for surfaces, borders, typography, spacing, control heights and corner radii.
- Use quieter panels with subtle borders and minimal shadows; use campaign/character teal and battle/monster amber as restrained accents rather than dominant panel fills. Retain appropriate fantasy branding without decorating operational controls excessively.
- Proposed spacing scale: 4, 8, 12, 16, 24 and 32 px. Use one coherent UI type system and consistent button/input geometry. Values remain subject to visual review.
- Reserve a consistent accent for primary actions and red for destructive operations; do not rely on colour alone for grouping or status.

Acceptance: representative panels, tables, forms and modals share the same visual rules; text, focus and state indicators remain readable; existing theme and combatant/display colours are not accidentally overridden.

### SG-TODO-009.2 - Header and action hierarchy

Status: proposed.

- Keep a compact fixed header with product identity, active campaign, active battle setup and explicit encounter state.
- Separate context, navigation, global actions and feedback into predictable areas. Move infrequent global actions into a labelled More menu where appropriate.
- Keep entity-specific actions local: campaign backups with campaign management, setup actions with setup management.
- Give the current task one dominant action; visually quiet secondary actions. Separate End encounter from routine controls and put Reset all in a clearly labelled danger section.

Acceptance: context and feedback remain visible while scrolling; wrapped controls/messages never overlap the workspace; global and local actions are distinguishable and keyboard accessible.

### SG-TODO-009.3 - Consistent panels and forms

Status: proposed.

- Standardize panel anatomy: concise title, optional description, related fields, main action and secondary actions.
- Use task-oriented labels such as Add character for an entry form and Characters for a roster.
- Keep labels consistently above inputs, clarify mandatory fields and group related controls.
- Keep common actions visible; place import/export, backups and advanced settings in clearly named expandable areas when appropriate. Do not hide frequently needed controls merely to reduce button counts.

Acceptance: field purposes and required values are clear; expand/collapse exposes accurate accessible state; forms retain values, validation, existing IDs/handlers and expected submit behaviour.

### SG-TODO-009.4 - Scannable rosters and contextual bulk actions

Status: proposed; alternative action-menu design requires agreement against SG-TODO-007.

- Present characters and monsters as structured rows with clear names, aligned numeric values and concise textual status indicators. Keep HP, initiative and combat state immediately visible where relevant.
- Consider search/filter and a collection-level Add action. Keep table-wide controls separate from row actions.
- Show selected counts and contextual bulk actions after selection, retaining clear Select all and Clear selection behaviour.
- Evaluate row expansion or a details panel for secondary information. A frequent visible action plus an overflow menu is a design option, not an approved replacement for accepted single-line controls.

Acceptance: scan, select, edit and bulk workflows remain available without accidental mutations; selection survives or resets predictably on refresh/filter changes; keyboard focus is exposed within local scrollers; removed row HP-change controls do not reappear.

### SG-TODO-009.5 - Workflow-based navigation

Status: proposed; tab model and visibility replacement require design agreement.

- Proposed views: Campaign (campaign selection, characters, backups), Battle preparation (setups, monsters, initiative, lair configuration) and Live encounter (turn order, participants, encounter tools, log).
- Prefer compact tabs initially over a large sidebar; keep active campaign/setup context visible in every view.
- Reduce global pane-toggle clutter through workflow views and local disclosure, after explicitly mapping existing manual visibility and automatic battle-related behaviour.

Acceptance: every existing capability has a discoverable destination; changing views does not submit forms, lose edits or mutate encounters; active tab and focus state are accessible; initial collapse, dependent controls, lair gating and encounter-tools restoration are preserved or intentionally replaced by an explicitly agreed specification.

### SG-TODO-009.6 - Focused live encounter workspace

Status: proposed.

- Give turn order/participants the largest area, with encounter tools beside it on wide screens and below it on narrow screens.
- Clearly identify round and active participant, emphasize Next turn and keep HP/conditions and upcoming turns scannable.
- Place a collapsible activity log below the main workspace and remove setup forms from the primary combat view without removing access to them.
- Preserve the existing Next from Battle Actions workflow and all alternate damage/healing/statistics workflows.

Acceptance: combat operations remain efficient and correctly scoped; turn advancement, end/reset, lair behaviour, tools visibility restoration and activity history regressions are covered; narrow layouts do not conceal essential controls.

### SG-TODO-009.7 - Feedback and final usability hardening

Status: proposed.

- Distinguish brief success notices from actionable errors. Proposed change: success messages may expire, while actionable errors persist until corrected or dismissed; review the existing five-second global-message rule explicitly.
- Show field validation near the field. A rejected Join battle should explain the missing initiative and identify the affected combatant/field, not merely display a generic failure.
- Show connection problems persistently until resolved and confirm destructive operations with specific affected targets.
- Check responsive stacking, local table overflow, zoom, labels, contrast, focus visibility/order, tab/menu semantics and appropriate announcement of feedback. Avoid disruptive page movement when messages appear.

Acceptance: feedback is visible and actionable without depending solely on colour or a short timeout; messages do not overlap content; keyboard-only operation and representative desktop/narrow layouts remain usable.

## Validation and delivery requirements

For implementation increments, prepare targeted automated regressions for the affected behaviours and retain existing tests. Verify actual CI coverage before delegating checks to it. Browser fixtures are not authenticated live-server evidence.

Required review scenarios include: campaign/setup active and inactive; initial/delayed state; manual pane changes; battle start/end/reset; lair enabled/disabled; refresh and rerender; row selection/filter/bulk actions; missing initiative; successful/failed saves; connection loss/recovery; destructive confirmations; keyboard traversal and narrow screens.

Record executed checks and observed results separately from unexecuted, pending or manual checks. Obtain user visual/workflow acceptance before closing the redesign. Do not mark phases completed merely because code is committed. Update relevant user documentation, TODO status and handover with implementation deliveries.

## Planning-only change - 2026-11-06

The original addition recorded suggestions and a recommended processing order only. No application, test or workflow code was changed by that addition; no redesign or browser validation was claimed. README and relevant indexed handover/TODO documentation were reviewed. README and handover remained unchanged because current delivered behaviour had not changed.

The user explicitly requested [skip ci] for that documentation push. The skip request does not apply to later implementation pushes.

## Stage 009.1 implementation - 2026-11-06

The user agreed seven-stage delivery and explicitly requested starting 009.1. This increment adds Admin-scoped foundation tokens and styling without moving controls, changing navigation or modifying JavaScript, API, encounter state or persistence. Existing action classifications are retained; stage 009.2 remains responsible for action hierarchy.

Preparation executed CSS parsing, selected nominal colour-contrast calculations, Python AST parsing and the two new source-contract tests against drafted files. Full browser/suite execution is pending. The new fixture prepares before/after screenshots at 1440 and 375 pixels by disabling only the foundation stylesheet for the baseline; no baseline screenshot has yet been executed or visually reviewed. CI is configured to retain those fixture screenshots. This is not authenticated live-server evidence or a full accessibility audit.

Do not close 009.1 before reviewing covering CI, representative visual results and user acceptance. Review header/workspace geometry, compact inputs, roster scrolling/focus, modals and unchanged colour semantics. See the linked handover for exact preparation results and outstanding checks.
