# 270 - Admin header and action hierarchy

[Back to handover index](../../HANDOVER.md)

Updated: 2026-11-06. Task: [SG-TODO-009.2](../todo/090-admin-usability-redesign.md). Status: implementation included, full application CI/browser validation and user visual/workflow acceptance pending. 009.1 remains closed; 009.3-009.7 are not implemented.

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

Full-application tests are prepared but not executed during preparation. The new module has six unittest methods: one source contract plus five full-Admin intercepted-HTTP browser methods. Coverage includes active/missing context, draft-name separation, state emphasis, keyboard More/Danger, cancelled reset/end without mutations, original Next request, panel preferences/drafts, local focus scrolling, bounded messages/header geometry, idempotence and preserved monster controls. These are fixtures, not live-server evidence.

Existing CI unittest discovery includes the new module; no workflow change is needed. Screenshot capture writes six 0092-WIDTH-inactive/active/more.png files for 1440/375 to SG_VISUAL_ARTIFACTS, retained in the existing admin-foundations-visual-fixtures artifact. Active screenshot states are explicitly fixture-staged, not evidence of a successful real encounter transition. Existing foundation and shell tests remain unchanged.

## Remaining validation

Review covering CI and desktop/narrow screenshots and obtain user acceptance before completing 009.2. Check real start/next/end/reset workflows, delayed/failed state, campaign/setup switches, lair enabled/disabled, long context labels, viewport/zoom, menu keyboard/focus, messages and modals. Opening/reorganising controls must not create API mutations. Retain accepted pane and encounter-tools restoration behaviour. No authenticated deployment, exhaustive live combat or screen-reader audit has been executed here.

Source module: 5,495 UTF-8 bytes; stylesheet: 2,657 bytes; regression module: 10,872 bytes, all below 20,000. README and User Guide were reviewed and remain accurate without edits; this indexed section documents the new control locations. Normal CI is intended, with no skip marker or separate dispatch. No commit SHA or workflow result is claimed before it exists.
