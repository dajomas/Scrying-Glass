# 220 - Initial Admin input visibility

[Back to handover index](../../HANDOVER.md)

## Current close-out - 2026-11-03

[SG-TODO-005](../todo/050-admin-initial-visibility.md) is completed at the user's
explicit request. The dependent-button correction was delivered in
e7b3d96ce428ce4022bb3930a8c660f02f12b765. CSS blob
d89a094bfd42b2f0e126038e4aebb75f41c31670 is identical at tested commit
75b870ef9a204981bc778ccbaaea23f96b3fcb56 and current preparation base
f2f63c1fc28238fb2c32b27ce180c54863b30fa5.

Inspected ci-results-41608182802-attempt-1/run.json confirms run 41608182802,
attempt 1, head 75b870ef9a204981bc778ccbaaea23f96b3fcb56, workflow/tests job
completed/success. Syntax/import, unittest, pytest, JavaScript and standalone
browser/audit steps report success. This is metadata verification, not a new test
execution or review of every assertion. No new authenticated per-control live test
report accompanies closure; retain that distinction rather than inferring it from
other runbooks. User acceptance and the delivery/CI basis are recorded in the task.

This close-out changes only the task section, TODO index and this handover. The
user requested [skip ci] for this push; no workflow edit/dispatch, code/test change
or new test execution. It does not close SG-TODO-006 or change its pending CI/live
acceptance. README and HANDOVER index remain applicable and unchanged.

The reopening/preparation record below is historical; its pending-delivery/CI
statements are superseded by the delivery and close-out above.

## Historical reopened corrective increment - 2026-11-03

SG-TODO-005 was reopened after the user reported Show character input and Show
monster input remaining visible beneath hidden Campaign input and Battle setup
parents. Historical preparation base:
430574c584162099c61168cd680b0422479c1541 on features/perplexity.

### Diagnosis and prepared change

Individual parent handlers hide dependent buttons and save child preferences.
However, setAllHideablePanesHidden resets every button.hidden flag to false while
collapsing all panes for battle. This exposes child controls under hidden parents.
The original assembled-page regression checked pane hidden/aria states, not the
rendered visibility of these buttons; earlier green CI did not cover the invariant.

Two scoped :has() selectors in static/admin-shell.css enforce rendered unavailability:
- Campaign input [hidden] -> toggleCharacterPane display:none.
- Battle setup [hidden] -> toggleMonsterPane display:none.

The rules respond to the actual parent DOM state, including direct/global collapse,
without adding a second JavaScript state model, polling, observers or wrappers.
Reopening a parent removes this CSS constraint; the existing child preference and
button.hidden restoration still apply. Independent lair gating and display controls
are untouched. This retains the modern-browser requirement (including :has()).
No source fragments or bundle bytes change; split identity tests remain valid.

### Historical preparation checks and limitations

Five local real-Chromium methods in test_admin_dependent_controls.py passed against
the correction. Three failed against the original CSS. They use the production
reader, actual extracted pane-controller block, real stylesheet and original
initial-visibility controller, with minimal DOM/state fixtures. Tests assert
is_visible()/computed display, not merely hidden flags; they cover manual hiding,
child preference restoration, automatic battle collapse, repeated renders, initial
collapse and unaffected lair/display controls. No API requests or authenticated
server/browser checks were performed during that preparation.

The user-supplied evidence in ci-results-41584927496-attempt-1/run.json at the
historical preparation base identified databaseId 41584927496, attempt 1,
completed/success, head SHA 9f1b14ae99d3b297f4557f05f7f72485ab674d56. Syntax/import,
pytest, unittest, JavaScript and standalone browser/audit steps reported success.
That verified the previous Admin split CI, not the then-new CSS correction, and
did not prove authenticated live behavior or undelivered SG-TODO-006 UI labels.

### Delivery and continuity

The proposed corrective increment included CSS, regressions and existing task/index
updates, normal CI and bound approval. It was subsequently delivered in e7b3d96.
Deploy the stylesheet and reload Admin; no server restart, markup, config or schema
change is required for the CSS-only runtime correction. README and HANDOVER.md were
reviewed and left unchanged because deployment/index descriptions remained accurate.
SG-TODO-004 stays on hold. Current acceptance and later CI are recorded above.

## Historical completion - 2026-11-02

The user previously accepted the initial related-group scope after their green-CI
confirmation at 22:37 CET. Implementation: ee9a4bd56439d8a5e7d5a94e5d9d1c1788c4c9e4,
prepared against 6637a39ef21e0e035b849a7848ad0302c7ac7c33. No run identifier was
provided then; that closure recorded user-reported CI, not independently inspected
logs. Eight focused mocked-handler Chromium methods passed locally; a separate
assembled-page fixture was prepared but not executed by the assistant locally.
The controller initializes once per page from valid active_campaign_id/active_setup,
preserves prior manual choices, chains scryingLairsRender and catches up from latest.
There are no persistent preferences, added API mutations or polling. False initial
conditions preserve defaults. Missing/malformed data waits for an authoritative
snapshot. The new rendered-button invariant supplements this original scope.
