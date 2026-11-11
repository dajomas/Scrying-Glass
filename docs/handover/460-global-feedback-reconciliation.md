# 460 - Global feedback reconciliation

[Back to handover index](../../HANDOVER.md)

Current status: checkpoint CI reviewed; template-loaded source census recorded below.
4A.13 is still in progress. Historical pending notes are superseded only where
the later evidence entry explicitly says so; compatibility remains unchanged.

## 4A.13 audit and regression checkpoint - 2026-11-11

In progress on features/perplexity-009.7; baseline
f68e40872e8f3657f6d203f372565c01531f4a68. This change set supplies two test guards
and documentation, not runtime migration, compatibility retirement or acceptance.
No new commit SHA or covering CI result is invented.

The core literal-call audit guard expects eight untyped message() calls in
070-source.js: Start request (1), Start eligibility (1), tie confirmation (1),
Next (1), End (3), Reset All (1). It checks their known source blocks, relative
header/tail asset order and explicit replacement assignments. Start is replaced by
admin-initial-visibility and admin-start-validation; Next by battle-actions-next;
End/Reset by their feedback scripts. Static source presence is not an active-call
count. These regex/source contracts do not establish a complete call graph or
prove all handlers installed at runtime. Dynamic aliases, injected assets, other
entry points and partial fixtures remain audit work.

The new Node suite uses the existing real-controller/Admin-bootstrap fixture,
without mounting views. It checks 136 unordered pairs of 17 selected operation
identities, matching resolution with persistent independent errors, target
isolation, five-second success expiry, supersession, away/back scope epochs and
retained pane/global compatibility isolation. The matrix tests API identities,
not 136 actual handler combinations or unique acceptance requirements. A separate
case composes the actual End and Reset All scripts with the bootstrap/loadState,
mock transport/buttons and fake clock: explicit End retry and success expiry
cannot clear Reset's failure or cause automatic replay.

## Executed preparation

New Node syntax passed. Corrected suite: 8 passed, zero failures/skips; four
negative controls detected (operation-key collision, actual producer operation
collision, shortened success deadline, omitted matching resolution); production
inputs restored and the full eight-case suite passed again. Draft assertions
initially compared VM-created legacyRegions arrays directly with host arrays and
failed despite equal contents; Array.from normalizes those new assertions across
realms. No production correction or weakened existing assertion was needed.
Test draft is 6,372 UTF-8 bytes, SHA-256
06bbd345c9f369120dd376e26ba23f13b57486a2485ee908900c67ea8a94cc9a.
Python guard compilation passed; its three repository-dependent tests were not
executed locally. The complete checkout/eight-part source was not reconstructed.

Five exact production inputs were verified against Git blobs before local tests:
controller c4a82d73b21f4657da651ce45f76003c3348a6ef;
bootstrap 59553fdd9fc93ac8d23f3ea54536aded1a945ab5;
fixture 6c46e1011354e031ccef26b3d823bf547736c4e2;
End d616c96cb77d8ad23f2aed29edaa580c1ed1841c;
Reset All 3f5e1a1f7d6fe1a087abfb0e97bc8c289356bc1f.
Live directory metadata also verified identities of all eight core fragments
against prior complete reads. Unchanged verified documentation/configuration
reads were reused. These focused tests are not full-Admin/browser, mounted view,
authenticated live-server, human visual or screen-reader evidence.

## Remaining inventory and delivery boundaries

Global and pane compatibility remain intact and observable. The global-compatibility
test records the current baseline, not a permanent requirement to keep that route;
change it deliberately when the completed inventory supports retirement. Pane
compatibility must survive until its separate migrations finish.

Already observed dependencies: monster candidate selection uses an untyped pane
notice while lookup blocks submission; features, lairs, statistics and viewer
access have direct local notices. Statistics-open failure and bundle-import result
also use alert(). Classify these by actual destination and agreed scope rather
than silently migrating or excluding them. Complete remaining loaded/injected
caller and direct-writer inventory, actual handler composition and cross-operation
coverage before any compatibility retirement. Existing 4A.1-4A.12 stay closed;
this checkpoint does not reopen their accepted behavior.

Normal configured CI discovers both new files via unittest test_*.py and CJS test
loops. This test/docs commit uses normal CI, not [skip ci]; no workflow edit or
separate dispatch. Covering CI for the actual checkpoint SHA, further inventory,
necessary corrections/migrations and explicit bounded acceptance remain pending.
No application/core/pin/markup/shared-fixture changes, archive/Patch/, merge or
deployment. README/TODO root reviewed and unchanged; indexes/task detail updated.
Deliverables 1/2, Deliverable 2 near-field/connection work and phase 009.7 remain
open under preserved criteria. [Task](../todo/097-feedback-delivery-plan.md#4a13-global-reconciliation---2026-11-11).

## Checkpoint CI and template-loaded source inventory - 2026-11-11

This entry supersedes the earlier pending-checkpoint-CI and incomplete-template
source census notes, not their historical local-execution limits. 4A.13 remains
in progress; no runtime or compatibility retirement is supplied by this update.

Checkpoint a82e17146aae53a89710c054460f352415b7b45f is covered by successful
Branch tests 42952443028 attempt 1, job 130299650206; immutable publication
80891f360bedc572cce753b5187f4fd27e581939. Run/job metadata match that SHA.
Direct workflow reader file-000038 parts 131-132 confirms all eight new Node
cases passed, zero failures/cancellations/skips, including the API pair matrix
and actual End/Reset composition. Parts 022-023 confirms all three Python
inventory methods report ok. These CI results resolve the checkpoint execution
gates, not whole-unit runtime/inventory acceptance. No new local test execution
or visual/live-server/accessibility pass is claimed.

Source census snapshot: 91dde45ccc305dfc69dfe8020260dd3670ac17a4. All 21
Admin HTML fragments have complete reads; no fragment remains unchecked for
embedded script includes. Six fragments include 42 distinct deferred JS assets:
010 has 4; 030 has 2; 050, 185 and 180 each have 1; 190 has 33. The other 15
fragments introduce no script include or inline script. Expanding served admin.js
to its eight fragments gives 41 standalone assets plus eight core fragments:
49 JS source files reviewed, not 49 independent feedback producers. The tracked
admin.js marker is not runtime source. Complete previous reads were reused only
with unchanged source/template identities verified against the snapshot.

Rows 1-4 below load from 010; 5-6 from 030; 7 from 050; 8 from 185; 9 from 180;
10-42 from 190. Order follows web_html/admin_html.py's explicit assembly order,
including 185 before 060. This is a manually reviewed source census with checked
manifest counts/uniqueness, not a newly executed whole-repository scanner or proof
that every runtime installer succeeds.

| # | Asset under static/ | Destination / effective role |
|---|---|---|
| 1 | admin-feedback-controller.js | Controller infrastructure; no request producer. |
| 2 | admin-feedback-view.js | Managed region renderer, including global; not an untyped producer. |
| 3 | admin-feedback-admin.js | Explicit API/state.load owner plus temporary global/pane compatibility. |
| 4 | initiative-join-gate.js | Explicit roster.join; standalone fetch and late core wrappers. |
| 5 | campaign-ownership-notice.js | Dedicated persistent ownership guidance. |
| 6 | campaign-viewer-admin.js | Dedicated selected-campaign viewer-access notice. |
| 7 | setup-switch.js | Effective setup-load override; untyped battleSetup pane. |
| 8 | lair-status.js | Read-only lair status; late renderer wrapper. |
| 9 | battle-turn-actions.js | Explicit global turn completion; other outcomes modal-local. |
| 10 | encounter-visibility.js | Tools visibility helper; no action notice producer. |
| 11 | admin.js | Served eight-fragment bundle, not tracked marker; eight known replaced core message calls. |
| 12 | monster-candidate-selection.js | Lookup request wrapper; pending-submit untyped monsters pane. |
| 13 | campaign-backups.js | Moves original controls; feature handlers remain owners. |
| 14 | damage-preview.js | Pure confirmation-text helper; caller owns confirmation. |
| 15 | statistics.js | Modal statistics notice; open-error alert is an open global migration candidate. |
| 16 | features.js | Local feature/polling notices; import-success alert is an open global migration candidate. |
| 17 | bulk-select-all.js | Select-dead bulk wrapper; untyped pane result. |
| 18 | lairs.js | Lair configuration/action local notices and renderer. |
| 19 | setup-has-lair.js | Untyped battleSetup pane request error; renderer wrapper. |
| 20 | lair-color-preview.js | Color preview only; renderer wrapper. |
| 21 | lair-state-buttons.js | Lair toggles write local lairNotice; renderer wrapper. |
| 22 | battle-actions-next.js | Explicit global Next; wraps request and replaces both Next handlers. |
| 23 | admin-initial-visibility.js | Explicit global Start request; replaces startBattle and wraps renderer. |
| 24 | admin-start-validation.js | Explicit global Start eligibility/tie validation; replaces two onclick handlers. |
| 25 | admin-end-feedback.js | Explicit global End validation/request; replaces End onclick. |
| 26 | admin-reset-all-feedback.js | Explicit global Reset All; replaces Reset All onclick. |
| 27 | admin-notification-layout.js | Pane visibility observer; no message/timer replacement. |
| 28 | admin-header-hierarchy.js | Reparents original controls; context/menu layout, not handler replacement. |
| 29 | combatant-row-layout.js | Removes old HP-change columns; focus/layout only. |
| 30 | admin-panel-forms.js | Original-control grouping/default name; no action reporting. |
| 31 | monster-image-previews.js | Preview-local status/alt text; input/token submission unchanged. |
| 32 | admin-rosters.js | Read-only roster/selection status; fixed-label click delegates to patch. |
| 33 | character-hp-display.js | Read-only HP presentation; Edit remains mutation path. |
| 34 | initiative-keyboard-navigation.js | Focus/draft navigation; emits native change, no independent action report. |
| 35 | monster-initiative-edit.js | Monster Edit override; untyped monsters pane, character handler delegated. |
| 36 | monster-initiative-roster.js | Read-only bonus/origin presentation. |
| 37 | monster-initiative-roll.js | Captured raw-roll mutation; untyped monsters pane request/refresh reporting. |
| 38 | monster-refresh-selection.js | Pure review selection model; throws to its dialog owner. |
| 39 | monster-refresh-review.js | Bulk review wrapper; dialog preview/retry, untyped pane Apply/refresh reporting. |
| 40 | admin-workflow-navigation.js | Tab/view filtering and focus only. |
| 41 | battle-action-statistics.js | Read-only modal selector summaries; renderer wrapper. |
| 42 | admin-live-workspace.js | Original tools controls reparented into dialog; busy-close guidance is dialog-local. |

### Loading and delegation findings

Reviewed server entry, AdminPagesMixin/AdminAPI, viewer/ownership/features/lair/
users/logout/monster-refresh installers and asset-cache middleware introduce no
additional GM Admin script include in those inspected files. admin_home returns
context.ADMIN_HTML; web_html assembles the explicit fragment list. Cache busting
changes URL query tokens, not script bodies/order or the number of includes.
This is not an exhaustive dynamic Python call-graph or authenticated-page test.

Source delegation to preserve: candidate selection and Next wrap request; select-
dead and monster source review wrap runBulkAction. Join installs at DOMContentLoaded
and captures the then-current patch/runBulkAction bindings, delegating non-Join
actions. Setup switch replaces setup-load controls late. The lair render chain
is extended by lairs/setup/preview/buttons/initial visibility/action summaries
and late lair status. Header/forms/workspace reparent original controls rather
than authorizing replacement of their action handlers. Runtime composition of
these interactions remains to be exercised before retirement.

No additional untyped core-global helper invocation was identified in this
source census beyond the eight known replaced 070 calls and the compatibility
infrastructure itself. This does not prove zero runtime legacy.global use.
The two browser alert paths below are separate global-notice candidates, not
callers of message()/deliver(global), and are not silently counted as migrated.

### Disposition and remaining work

- Open global migration/disposition candidates: statistics.js open(id,button)
  failure alert, and features.js successful campaign-bundle import alert. Prepare
  narrow controller-backed handling with appropriate operation/target/scope and
  ordering, or document an explicitly agreed exclusion before 4A.13 closure.
  Preserve the bundle's recovery instructions and all existing mutation semantics.
- Retain pane compatibility: candidate pending submission, setup switching, bulk
  selection/non-Join actions, monster Edit/raw rolls/source-review Apply and the
  existing campaign/setup/roster form operations. These remain later pane/producer
  integration obligations, not evidence that Deliverable 1 is complete.
- Dedicated feature/lair/viewer notices still need their agreed integration
  disposition. Preview status, read-only roster/lair/action summaries, ownership
  guidance and tools busy-close text are not blanket success toasts. Connection
  persistence/polling deduplication and near-field association remain Deliverable 2.
- The separate /users template loads users.js and campaign-ownership-admin.js;
  its userMessage/campaignOwnerNotice are not GM Admin #message callers. This
  loading boundary does not assert acceptance of that separate page's behavior.
- Next runtime gate: exercise actual full-page loading/late-wrapper composition,
  monitor legacyRegions for unintended global traffic, test cross-operation
  outcomes and the two alert dispositions, and check stale-scope/no-replay/draft
  preservation. Only then decide and implement global compatibility retirement;
  change its deliberate baseline test while keeping pane compatibility.

This inventory/evidence update is documentation only with [skip ci]; no application,
test, pin, markup or workflow changes and no new workflow dispatch. README/TODO
root links remain accurate. No 4A.13, deliverable or phase acceptance, merge or
deployment is implied. Earlier 29-row draft CSV was a partial working artifact;
this table is the repository review record for the stated template source scope.
