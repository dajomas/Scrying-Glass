# 370 - Focused live encounter workspace

[Back to handover index](../../HANDOVER.md)

Updated: 2026-11-09. Task: [SG-TODO-009.6](../todo/090-admin-usability-redesign.md#sg-todo-0096---focused-live-encounter-workspace). Status: full-width/dialog revision delivered at 540ab598d65bb7002d3e8184e59cd5c596e2c90f; a subsequent independent-panel increment is prepared for bound approval. Covering CI and renewed acceptance remain pending; revoked Admin-page verification remains revoked. Overall 009 stays in progress; 009.7 stays proposed; 009.5/015 remain closed.

## Revised user workflow

Battle, Characters, Monsters and Activity log keep their original full-width main-page flow. The duplicate participant overview, cards, split grid and sidebar space are gone. Native battleInfo current-turn action access, fixed header context, Next, End and Danger zone/Reset remain. Original roster nodes, selections, actions and local overflow stay in place.

The user's later independent-panel requirement means all controls mapped to Campaign or Battle Preparation remain available regardless of other panels' hidden state. Campaign Input affects only Campaign Setup, Character Input only Add Character, and Character Display only its roster. Battle Setup, Add Monsters and roster controls behave likewise. Lair eligibility still follows has_lair independently; controls excluded by a different workflow tab stay excluded. This explicitly supersedes the old parent/child availability behavior, not permissions or native battle-start collapse.

Successful Start closes the native Campaign/Battle input and roster panes, including an explicit active-battle restart. Rejected Start keeps their visibility. Opening a panel afterwards is independent and survives ordinary refresh/Next; native battle-end/reset restoration remains unchanged. The Battle summary/current-turn controls remain visible.

Encounter tools remains an on-demand Live-view popup opened by the existing button, not automatically by battle transitions. The original section lives outside adminScroll in a named, internally scrolling dialog, retaining controls/IDs/handlers, target/effect drafts/files, disclosures and scoped viewer/Undo/health/effect/checkpoint/backup actions. Close/reopen is not Save/Reset. Sticky Close, focus containment/inertness/return, Escape and busy/nested guards are unchanged; independent lair placement/controllers are retained. The activity disclosure and single visible heading remain.

## Dialog delivery and retained history

540ab598d65bb7002d3e8184e59cd5c596e2c90f delivered the dialog revision. Its controller, responsive CSS and prepared tests/history are retained in the [pre-independent-panel handover](https://github.com/dajomas/Scrying-Glass/blob/540ab598d65bb7002d3e8184e59cd5c596e2c90f/docs/handover/370-live-encounter-workspace.md). That record distinguishes isolated checks from pending full-Admin tests; no covering result is invented here.

Earlier 8228b649c47f5df2b293608bd88e8153248c93bb had successful run 42627843410 attempt 1, published at a9e6b1bc321596eff2d660a80cc7d35f7b5fc9a6, covering the original design only. 110e210e16bcabe002718805443af807f210ef88 added compact connection/campaign-scoped status/log fixes; 73de987ba87fbc63af4766f379bdf366c13db80f corrected roster widths. Earlier screenshots and positive comments are not renewed acceptance after revocation or evidence for subsequent code.

## Independent-panel implementation - 2026-11-09

static/admin-initial-visibility.js retires the native paneDependencies.campaign and .battleSetup entries before existing initial visibility setup. Native onclick handlers consult that map dynamically and therefore call the original setPaneHidden for their own panel only. The six ordinary Campaign/setup/roster buttons are made available once; no lair eligibility flag, workflow filter or pane visibility is forced by that availability pass. Existing initial saved-context collapse, touched-before-first-response handling, delayed-state validation, renderer context/arguments/return and duplicate-install guard remain.

The inspected native startBattle helper submits one POST to /api/battle/start with existing JSON order/headers, awaits load and reports failures through message. The extension mirrors that contract with setAllHideablePanesHidden(true) added only after successful submission and before load. This ensures an explicit restart while already active closes manually reopened panels too. Failed submission does not collapse or refresh. Eligibility and tie selection still call the native UI path and resolve the updated helper dynamically. No global request wrapper or backend action is added.

static/admin-shell.css removes only the parent-hidden selectors that suppressed Character/Monster input buttons. Header, scrolling, colors and modal geometry remain. Matching end template versions initial visibility to 2. Native core fragments and assembled size/hash/failure marker stay unchanged. No replacement inputs/buttons, extra listeners per panel, second hidden-state model, polling, permissions, API payload, persistence or workflow changes.

## Executed checks and prepared regressions

Executed: Node syntax on the complete 3,865-byte initial module; parsing the 1,312-byte shell stylesheet; AST parsing of the 4,981-byte controller regression and 5,583-byte full-page regression. Isolated real Chromium at 1440/375 used the actual proposed module/CSS with representative native-controller and synthetic DOM/state fixtures: independent controls and availability, initial collapse, one-time battle collapse, manual reopen/refresh, end restoration, idempotence and preserved render return passed without page errors. Additional mocked-request Chromium checks passed Start and active restart collapse, preserved endpoint/method/order and failure retaining visible panels with the error reported. These are not actual assembled Admin/authenticated/live-server execution.

Prepared tests/test_admin_dependent_controls.py keeps its stable path but replaces obsolete dependency expectations with five actual-controller-excerpt/CSS methods covering one-panel-only toggles, controls remaining visible, battle collapse/reopen/end, initial saved-context behavior/idempotence and an explicit lair gate surviving setup toggles. Prepared tests/test_independent_panel_controls.py adds two production-Admin/intercepted-HTTP methods for Campaign/Preparation controls/drafts and real Start/restart/failed-request handler behavior with all input/roster collapse and manual reopen. They are not skipped or described as already run. Existing initial-state, dialog, navigation, roster, lair, combat and security tests remain.

The complete prepared modules and full suite were not run locally. Existing unittest discovery runs both with the split runner; no workflow edit is needed. Use normal CI without [skip ci]; review actual covering outcomes before claiming success. Earlier green runs do not validate this increment.

## Remaining gates and deployment

Review covering CI and actual desktop/narrow behavior: all mapped buttons available while parents are hidden, independent forms/rosters and drafts, successful Start/restart collapse, failed Start preservation, manually reopened panels surviving refresh/Next, lair eligibility and unchanged dialog/native combat/history behavior. Real campaign viewer count and renewed task-specific acceptance remain required. No new authenticated live TCP/provider, process restart or exhaustive accessibility verification is claimed.

Deploy matching initial JS, shell CSS and template, restart the process for assembled HTML and reload Admin. No migration/configuration change. README and root indexes were reviewed/reused and left unchanged because generic runtime descriptions, links and in-progress status remain accurate. Task/this section are updated together; no unrelated task is reopened/closed/started and no implementation SHA is invented before delivery.
