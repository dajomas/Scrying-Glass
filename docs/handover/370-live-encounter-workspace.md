# 370 - Focused live encounter workspace

[Back to handover index](../../HANDOVER.md)

Updated: 2026-11-09. Task: [SG-TODO-009.6](../todo/090-admin-usability-redesign.md#sg-todo-0096---focused-live-encounter-workspace). Status: dialog and independent-panel code delivered; covering run 42649656592 attempt 1 failed in a Node VM fixture. A targeted fixture correction is prepared for approval and passes locally. Full corrective CI and renewed acceptance remain pending; revoked Admin-page verification remains revoked. Overall 009 stays in progress; 009.7 stays proposed; 009.5/015 remain closed.

## Revised user workflow

Battle, Characters, Monsters and Activity log keep their original full-width main-page flow. The duplicate participant overview, cards, split grid and sidebar space are gone. Native battleInfo current-turn action access, fixed header context, Next, End and Danger zone/Reset remain. Original roster nodes, selections, actions and local overflow stay in place.

The user's later independent-panel requirement means all controls mapped to Campaign or Battle Preparation remain available regardless of other panels' hidden state. Campaign Input affects only Campaign Setup, Character Input only Add Character, and Character Display only its roster. Battle Setup, Add Monsters and roster controls behave likewise. Lair eligibility still follows has_lair independently; controls excluded by a different workflow tab stay excluded. This explicitly supersedes the old parent/child availability behavior, not permissions or native battle-start collapse.

Successful Start closes the native Campaign/Battle input and roster panes, including an explicit active-battle restart. Rejected Start keeps their visibility. Opening a panel afterwards is independent and survives ordinary refresh/Next; native battle-end/reset restoration remains unchanged. The Battle summary/current-turn controls remain visible.

Encounter tools remains an on-demand Live-view popup opened by the existing button, not automatically by battle transitions. The original section lives outside adminScroll in a named, internally scrolling dialog, retaining controls/IDs/handlers, target/effect drafts/files, disclosures and scoped viewer/Undo/health/effect/checkpoint/backup actions. Close/reopen is not Save/Reset. Sticky Close, focus containment/inertness/return, Escape and busy/nested guards are unchanged; independent lair placement/controllers are retained. The activity disclosure and single visible heading remain.

## Dialog delivery and retained history

540ab598d65bb7002d3e8184e59cd5c596e2c90f delivered the dialog revision. Its controller, responsive CSS and prepared tests/history are retained in the [pre-independent-panel handover](https://github.com/dajomas/Scrying-Glass/blob/540ab598d65bb7002d3e8184e59cd5c596e2c90f/docs/handover/370-live-encounter-workspace.md). Independent panels were delivered at 85c2cdfa365560d382522865aef41ba2ac65b2bc; its covering evidence is recorded below.

Earlier 8228b649c47f5df2b293608bd88e8153248c93bb had successful run 42627843410 attempt 1, published at a9e6b1bc321596eff2d660a80cc7d35f7b5fc9a6, covering the original design only. 110e210e16bcabe002718805443af807f210ef88 added compact connection/campaign-scoped status/log fixes; 73de987ba87fbc63af4766f379bdf366c13db80f corrected roster widths. Earlier screenshots and positive comments are not renewed acceptance after revocation or evidence for subsequent code.

## Independent-panel implementation - 2026-11-09

static/admin-initial-visibility.js retires the native paneDependencies.campaign and .battleSetup entries before existing initial visibility setup. Native onclick handlers consult that map dynamically and therefore call the original setPaneHidden for their own panel only. The six ordinary Campaign/setup/roster buttons are made available once; no lair eligibility flag, workflow filter or pane visibility is forced by that availability pass. Existing initial saved-context collapse, touched-before-first-response handling, delayed-state validation, renderer context/arguments/return and duplicate-install guard remain.

The inspected native startBattle helper submits one POST to /api/battle/start with existing JSON order/headers, awaits load and reports failures through message. The extension mirrors that contract with setAllHideablePanesHidden(true) added only after successful submission and before load. This ensures an explicit restart while already active closes manually reopened panels too. Failed submission does not collapse or refresh. Eligibility and tie selection still call the native UI path and resolve the updated helper dynamically. No global request wrapper or backend action is added.

static/admin-shell.css removes only the parent-hidden selectors that suppressed Character/Monster input buttons. Header, scrolling, colors and modal geometry remain. Matching end template versions initial visibility to 2. Native core fragments and assembled size/hash/failure marker stay unchanged. No replacement inputs/buttons, extra listeners per panel, second hidden-state model, polling, permissions, API payload, persistence or workflow changes.

## Executed checks and prepared regressions

During initial preparation: Node syntax on the complete 3,865-byte initial module; parsing the 1,312-byte shell stylesheet; AST parsing of the 4,981-byte controller regression and 5,583-byte full-page regression passed. Isolated real Chromium at 1440/375 with representative native-controller and synthetic DOM/state fixtures passed independence, availability, initial/battle collapse, manual reopen/refresh, end restoration, idempotence and preserved render return. Mocked-request checks passed Start/restart collapse, unchanged endpoint/method/order and failed Start preservation. These were not actual assembled Admin/authenticated/live-server execution.

The five controller/CSS and two full-page/intercepted-HTTP regression methods were prepared without local full-module execution. Subsequently, covering CI's Python suite including browser fixtures passed on 85c2cdfa365560d382522865aef41ba2ac65b2bc, but the overall run failed in the JavaScript stage. Those facts remain distinct; no full green CI is claimed.

## VM fixture correction - 2026-11-09

Published evidence: ci-results-42649656592-attempt-1 at publication SHA 445f5d88dd54998a219974ebf1842a8cd590f6a6. run.json matches features/perplexity and tested SHA 85c2cdfa365560d382522865aef41ba2ac65b2bc and reports completed/failure. jobs.json reports successful syntax/import, Python/browser suite, pytest, standalone browser/audit and artifact upload, with JavaScript failed. Post setup-node/setup-python cleanup steps were skipped; these are not skipped test suites.

Workflow log reader-chunks/file-000038/part-000121.txt and part-000122.txt identify tests/encounter-active-combatant.test.cjs stopping at window.scryingEncounterToolsBusy with ReferenceError: window is not defined. Its VM context supplied document/fetch/FormData/Option but omitted the browser global. Production browser behavior is not corrected by removing the accessor or weakening assertions.

The fixture now sets context.window=context before VM execution and explicitly asserts window===globalThis, the busy getter is a function and it initially returns false. Every original active-combatant selection, manual override, monster/downed turn, dirty-field, lair-transition, scope-change and no-turn assertion is unchanged. Existing source isolation/early return is unchanged. No production code, assets, permissions or workflow changes are included.

Executed targeted validation: reconstructed complete features.js and old fixture exactly matched verified Git blob SHAs 140b87b5f4e55cfbedd33ce59c5780bfd289e732 and 18fbfd5c9b753b1b68d9d614cf3f087071d4c082. In a temporary repository-relative directory, node --test reproduced the original window error, then the complete corrected 3,353-byte fixture passed: 1 TAP test, 0 failures, 0 skipped, exit code 0, with all original assertions and new global/accessor assertions. This is a Node DOM/HTTP mock fixture, not browser, actual busy-save gating, authenticated/live-server or full-suite verification.

No new full suite or CI run was executed for this correction during preparation. Normal push CI applies because a test file changes, without [skip ci]. Failed run 42649656592 remains historical failure; the targeted pass does not relabel it. Full corrective covering CI and renewed user acceptance remain gates.

## Remaining gates and deployment

Review corrective covering CI and actual desktop/narrow behavior: mapped buttons available while parents are hidden, independent forms/rosters/drafts, successful Start/restart collapse, failed Start preservation, manual reopen surviving refresh/Next, lair eligibility and unchanged tools/native combat/history behavior. Real campaign viewer count and renewed task-specific acceptance remain required. No new authenticated live TCP/provider, process restart or exhaustive accessibility verification is claimed.

This correction changes only the test fixture and task/handover records; it requires no runtime deployment, migration or restart. README and root indexes were reviewed/reused and left unchanged because generic runtime descriptions, links and in-progress status remain accurate. Existing indexed paths and unrelated task statuses are retained; no corrective SHA or workflow result is invented before delivery.
