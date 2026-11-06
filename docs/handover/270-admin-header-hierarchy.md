# 270 - Admin header and action hierarchy

[Back to handover index](../../HANDOVER.md)

Updated: 2026-11-06. Task: [SG-TODO-009.2](../todo/090-admin-usability-redesign.md). Status: implementation included; first local run failed in a pane-visibility test precondition, test correction included, covering validation and user visual/workflow acceptance pending. 009.1 remains closed; 009.3-009.7 are not implemented.

## User workflow

The stationary header retains product identity and adds active campaign, saved setup, encounter state and round context. Context mirrors the existing rendered active labels, not dropdown drafts or an unsaved setup name. Loading and absent/unavailable context are not replaced with invented selections. Existing battle-state semantics are retained: active comes from the original battle-order-based badge, not round number alone.

Start battle and Next move to the header. Once state loads, Start is the gold primary action while inactive and Next while active; neither is newly hidden or disabled. End battle remains available in a separated group and retains its original confirmation and no-active-battle check. Reset All moves to a closed Danger zone in the Battle panel, with explicit explanatory text and its existing confirmation. No operation is triggered by layout changes or disclosure navigation.

More is a native details/summary disclosure containing the existing viewer battle-order font controls and POST logout form. Enter/Space use native disclosure behaviour; Escape within More closes it and returns focus to the summary. Clicking outside closes it. Its content has viewport-bounded width/height and local overflow. It is not assigned ARIA menu semantics that would require a separate menu keyboard model.

The existing pane toggles remain in their original order in a one-line horizontal scroller labelled Panels, rather than wrapping into a large mobile header. Tab focus exposes off-screen controls locally. Labels, IDs, handlers, manual/parent-child preferences and independent lair gating remain owned by existing code. This is not workflow-tab navigation and does not replace the accepted visibility mapping. Campaign backups and setup operations stay local. The global message remains above the shared scrolling workspace.

## Implementation and compatibility

New assets: static/admin-header-hierarchy.js and static/admin-header-hierarchy.css. The script moves the actual button/form/row nodes, preserving handlers, identity, form fields and availability. It observes active-label/badge text and attributes, not input drafts, and does not change server state. Installation is guarded and missing prerequisites leave the legacy layout intact. Matching CSS activation follows successful construction. Existing core scripts, eight fragments, assembly adapter/failure marker, API, permissions, persistence, combatant colours and accepted 11 monster controls are unchanged.

The stylesheet follows admin-foundations.css; the deferred script follows admin-notification-layout.js and precedes combatant-row-layout.js. Deploy matching template fragments and the complete static tree; restart the correct serving process because HTML assembles at import, then reload the browser. An older running process can serve old markup even when files on disk are current.

## Preparation evidence and limits

Executed: node --check for the new module; tinycss2 stylesheet/declaration parsing; Python AST parsing for tests/test_admin_header_hierarchy.py; one source-contract test against drafted assets/templates in a temporary fixture. Simplified real Chromium 134.0.6998.35 fixtures passed at 1440/768/375 widths for active context, moved control identity/handler retention, gold primary styling, state changes, More opening/Escape/focus restoration, viewport-bounded disclosure, hidden/reset disclosure, idempotence, unsaved-field retention, pane-strip focus exposure and header/workspace separation. A further simplified case passed loading/absent context updates and outside-click closure.

These simplified fixtures used representative DOM/CSS, not the full application or authenticated server. Their header heights were about 169.55 px at 1440/768 and 239.02 px at 375 in a 1000 px viewport; these measurements are fixture observations, not promises for the real page, long names, fonts or zoom. An initial attempt to use synchronous Playwright inside the execution environment's asyncio loop was rejected; the executed Chromium checks used its asynchronous API.

Full-application tests were prepared but not executed during initial preparation. The new module has six unittest methods: one source contract plus five full-Admin intercepted-HTTP browser methods. Coverage includes active/missing context, draft-name separation, state emphasis, keyboard More/Danger, cancelled reset/end without mutations, original Next request, panel preferences/drafts, local focus scrolling, bounded messages/header geometry, idempotence and preserved monster controls. These are fixtures, not live-server evidence.

Existing CI unittest discovery includes the new module; no workflow change is needed. Screenshot capture writes six 0092-WIDTH-inactive/active/more.png files for 1440/375 to SG_VISUAL_ARTIFACTS, retained in the existing admin-foundations-visual-fixtures artifact. Active screenshot states are explicitly fixture-staged, not evidence of a successful real encounter transition. Existing foundation and shell tests remain unchanged.

## Remaining validation

Review covering CI and desktop/narrow screenshots and obtain user acceptance before completing 009.2. Check real start/next/end/reset workflows, delayed/failed state, campaign/setup switches, lair enabled/disabled, long context labels, viewport/zoom, menu keyboard/focus, messages and modals. Opening/reorganising controls must not create API mutations. Retain accepted pane and encounter-tools restoration behaviour. No authenticated deployment, exhaustive live combat or screen-reader audit has been executed here.

Initial source module: 5,495 UTF-8 bytes; stylesheet: 2,657 bytes; original regression module: 10,872 bytes, all below 20,000. The test-only correction below expands the regression module without changing application assets. README and User Guide were reviewed and remain accurate without edits; this indexed section documents the new control locations. Normal CI is intended, with no skip marker or separate dispatch.

## First local result and fixture correction - 2026-11-06

Evidence commit eeff8880bceb9e63b2e8a4f8ad9ab40f48878abe publishes local-tests-a6b910d/run-20261106T134219Z-eZ3glD for exact implementation a6b910d94c3b846e128d01bc6baa10b48228770f. environment.txt records suite=all, Python 3.14.7, Node 22.23.2, WSL2 and completed=1. Overall exit code is 1: completion is not success. summary.tsv shows failed unittest and standalone script-2 commands, with zero exits for syntax/import, pytest, all 38 JavaScript scripts and the other five standalone commands. No individual pytest count or every JavaScript assertion was reviewed for this run.

The reviewed main unittest excerpt explicitly reports the other five header methods passing and errors in test_header_scrolling_feedback_and_pane_preferences at widths 1440, 768 and 375. Its full final summary was truncated by the connector. The complete standalone audit repeats the suite and reports 1,041 tests, FAILED (errors=3), all at characterName.fill because the input is not visible. It records 675 opened connections and zero without explicit close: its failure repeats the test errors, not an observed connection leak. Mocked provider tracebacks in that log are not the reported test errors.

Live static/admin/030-source.js confirms that hiding Campaign saves child pane/button preferences and reopening restores them. Initial collapse can therefore leave a saved visible character preference. The failed test clicked Campaign open, which already restored the character pane, then unconditionally clicked the character toggle, hiding it before fill. This is a fixture precondition error, not evidence requiring changed application visibility semantics. Assertions after fill in that subtest were not reached and are not claimed validated.

The corrective change is restricted to the test method: click each Campaign/Character toggle only when aria-expanded is false, then explicitly assert both pane hidden flags are false and the character input is visible before normal fill. Retain the existing parent-cycle draft retention, feedback, fixed-boundary, scroll, roster count, page-error and mutation assertions. Do not use forced input, direct hidden-flag writes, sleeps, skips or weakened visibility assertions to bypass the defect.

Executed corrective preparation: Python AST parsing passed for the exact corrected method. No corrected full-module/browser/suite execution or new CI result is claimed during this preparation. Application JavaScript/CSS, templates, source assembly and workflows are unchanged. Existing CI discovery still covers the test. Corrective verification and visual/workflow acceptance remain pending; SG-TODO-009.2 remains in progress.

The corrective commit updates this handover, the existing test module and the concise TODO index summary. README, User Guide, HANDOVER.md and the detailed TODO section were reviewed and left unchanged: their feature description and pending-validation status remain accurate, with the existing header-handover link providing the detailed diagnosis. No skip marker or separate workflow dispatch is included, and no corrective SHA is invented before delivery.
