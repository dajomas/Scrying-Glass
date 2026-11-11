# 460 - Global feedback reconciliation

[Back to handover index](../../HANDOVER.md)

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
