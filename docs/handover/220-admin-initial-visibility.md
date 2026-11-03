# 220 - Initial Admin input visibility

[Back to handover index](../../HANDOVER.md)

## Reopened corrective increment - 2026-11-03

[SG-TODO-005](../todo/050-admin-initial-visibility.md) is reopened after the user
reported Show character input and Show monster input remaining visible beneath
hidden Campaign input and Battle setup parents. Preparation base:
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

### New checks and limitations

Five local real-Chromium methods in test_admin_dependent_controls.py passed against
the correction. Three failed against the original CSS. They use the production
reader, actual extracted pane-controller block, real stylesheet and original
initial-visibility controller, with minimal DOM/state fixtures. Tests assert
is_visible()/computed display, not merely hidden flags; they cover manual hiding,
child preference restoration, automatic battle collapse, repeated renders, initial
collapse and unaffected lair/display controls. No API requests or authenticated
server/browser checks were performed. Full corrective CI remains pending.

The user-supplied evidence in ci-results-41584927496-attempt-1/run.json at the
preparation base identifies databaseId 41584927496, attempt 1, completed/success,
head SHA 9f1b14ae99d3b297f4557f05f7f72485ab674d56. Syntax/import, unittest,
pytest, JavaScript and standalone browser/audit steps all report success.
This verifies the previous Admin split CI, not the new CSS correction, and does
not prove authenticated live behavior or undelivered SG-TODO-006 UI labels.

### Delivery and continuity

One proposed commit includes CSS, regressions and existing task/index updates.
Use normal CI and bound approval. Deploy the stylesheet and reload Admin; no
server restart, markup, config or schema change is required for this CSS-only
runtime change. README and HANDOVER.md were reviewed and left unchanged because
their deployment/index descriptions remain accurate. Do not close the reopened
task until corrective evidence and acceptance. SG-TODO-004 stays on hold.

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
