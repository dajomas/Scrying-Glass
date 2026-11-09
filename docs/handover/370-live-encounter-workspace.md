# 370 - Focused live encounter workspace

[Back to handover index](../../HANDOVER.md)

Updated: 2026-11-09. Task: [SG-TODO-009.6](../todo/090-admin-usability-redesign.md#sg-todo-0096---focused-live-encounter-workspace). Status: implementation, regression and documentation payload prepared for bound GitHub delivery; covering full-Admin/CI and user acceptance pending. Overall 009 remains in progress; 009.7 remains proposed. 015 and 009.5 closure remain intact.

## User workflow and implementation

Live encounter retains its existing tab and fixed header context/actions/feedback. Above 1000px, existing battle/order and roster panels plus a read-only participant overview occupy a larger main column; encounter and independently gated lair tools sit alongside. At 1000px and below the tools follow the main column, in matching DOM/keyboard order. Setup/Add forms stay outside this combat layout and remain accessible through existing tabs. Existing Next emphasis, End and Danger zone/Reset separation remain authoritative.

The participant overview follows state.battle_order without calculating initiative, advancing turns or filtering by player visibility. It marks active in_turn entries with text and aria-current, reports round/current participant through a small status region and shows current/max/temp HP, initiative, life state, concentration and nonmechanical effect names. Numeric zero remains visible and missing numeric fields display an em dash rather than invented zeroes. Lairs are explicitly shown without HP/AC. Names/effects are textContent, not interpolated HTML. The original battleInfo active-turn button remains available for Battle Actions/lair resolution; no duplicate combat mutation controls are introduced.

static/admin-live-workspace.js is loaded after navigation and selector-statistics enhancements. Installation is guarded and checks required roots. Original battle/roster/tools/lair sections are moved only while Live is selected; comment anchors restore their original parents/positions when leaving. Native hidden, workflow filter, collapse/lair gating, controllers, IDs, event handlers, input values, drafts and original node identities remain owned by existing modules. No replacement native controls, polling, requests, selected-value writes or API/backend/schema changes are added. The scryingLairsRender wrapper preserves prior context/arguments/return and catches up from latest. The layout observer watches only workflow-view changes.

Activity log remains below the workspace in its original section. A native details/summary disclosure wraps the existing log/export/clear controls, initially open to preserve accepted visibility. Closing it is optional; refresh and view changes do not reset its open state or rebuild the disclosure. Existing log mutation/export semantics and confirmation remain unchanged.

## Preparation actually executed

- Node --check passed for the complete 6,171-byte new JavaScript module.
- CSS parsing passed for the complete 2,356-byte new stylesheet.
- Python AST parsing passed for the complete 8,239-byte four-method regression module.
- Isolated real Chromium checks at 1440/375 passed larger main/side geometry versus single-column stacking, no page overflow, original-node/parent/hidden-state restoration, draft retention, disclosure persistence, idempotence, prior-hook context/return, actual zero HP, safe literal effect names and lair representation, with no page errors.

The isolated fixtures use the actual proposed assets but synthetic DOM/state and representative layout, not full Admin, authenticated server, provider, real Next/Apply or persistence execution. They are not substituted for the full regressions or covering CI. Actual encounter-tools CSS and the settled navigation/header/lair/state modules were inspected; sidebar controls are stacked within the narrower column.

## Prepared full-Admin regressions and CI

tests/test_admin_live_workspace.py reuses the assembled production Admin/assets and intercepted-HTTP browser harness. Four methods prepare desktop/mobile geometry, fixed-header boundary, history keyboard toggling and refresh persistence/screenshots, original control identity/Next handler, draft/hidden-state restoration, idempotence, authoritative order/zero/effect-text/lair/empty/end snapshots, and a native Next single-POST followed by Battle Actions access. Screenshots 0096-WIDTH-live.png use SG_VISUAL_ARTIFACTS. Existing navigation, lair/tools restoration, End/Reset, roster, Battle Actions/Next and security tests are retained, not replaced or claimed newly executed.

The complete new full-Admin module and existing suite were not executed locally. The reviewed .github/workflows/tests.yml discovers test_*.py via the split runner and uploads the visual directory; no workflow update is needed. Use normal push CI without [skip ci] and review published results before claiming a covering pass. Artifact capture/upload is not user visual acceptance.

## Remaining gates and deployment

Review covering CI and fixture screenshots and correct any failures. Obtain task-specific desktop/narrow workflow acceptance, including order/current/upcoming readability, roster actions, Next/End/Reset, Battle Actions/Next and alternate health/statistics paths, manual panes, independent lair/tools restoration, history and keyboard operation. Preserve accepted initiative, 015 summaries and manual copy. Do not close this task merely because code is pushed. No password-login, live TCP/provider, process-restart or exhaustive accessibility audit was performed during preparation.

Deploy the new assets and matching end template, restart the correct process for assembled HTML and reload Admin. No migration/configuration change. The eight Admin source fragments, adapter and tracked failure marker remain untouched. README, existing indexed handovers and sequence were reviewed/reused; README runtime contracts remain accurate without edits. Root TODO/HANDOVER and parent task statuses are updated in this proposal; no unrelated task is started or closed. No commit SHA or workflow outcome is invented before delivery.
