# 070 - Single-line monster buttons

[Back to TODO index](../../TODO.md)

## SG-TODO-007 - Restructure monster buttons into one line

- Status: completed; original closure at the user's request on 2026-11-03 after covering green CI. The 2026-11-06 Turn-control follow-up also has verified local/CI results and user acceptance, recorded below.
- Requested: 2026-11-02. Single-line/local-scroll scope approved: 2026-11-03.
- Scope updated by user on 2026-11-03: remove Damage and Heal from both Character and Monster rows.
- Priority, owner and deadline: not assigned.
- Initial delivery: `da8e7352fee0b504628aeed94aae6687341e2c35`.
- Name-column correction: `49aed0cbf074d63930ce29a8d64ef2d9cc970226`.
- Final row-removal/focus correction: `c19f49b9b5f79093d7bd69768f3eb14eaeabd762`.

### Turn-control follow-up - 2026-11-06

User requested removal of Turn from both roster UIs. Delivered at
d91f73bfe121870296a1df79f58c58c21bcaeb59; verified covering local/CI results
and explicit user acceptance now conclude this follow-up alongside 009.4/012,
independently of the original 007 closure. Scoped roster CSS uses display:none for
monster data-mt and character data-ct buttons, excluding them from visual, keyboard
and accessibility navigation on initial load and refresh. Legacy markup/API
handlers remain; this is UI removal, not deletion of manual-turn API capability.
There are now 10 visible monster-row buttons and 7 visible character-row buttons;
historical 11-button statements below describe the previously accepted version.
Other controls, initiative, Start/Next/End, turn highlighting, progression, HP rules
and persistence are unchanged.

Acceptance covers no accessible roster Turn after refresh at desktop/narrow widths
and retained labels, keyboard order/local focus exposure and handlers without
unintended mutations. Preparation passed CSS parsing and simplified Chromium at
1440/768/375 across three replacements per width. Later covering CI 42276181187
attempt 1 against d91f73b explicitly passed all four row-layout methods; its
main/repeated suites report 1,066 tests OK, pytest 43 passes and audit 681/0
connections. CI evidence: 386beabbcd6e39378014d4a86df24dd4d68f5b75 under
ci-results-42276181187-attempt-1. Completed local suite=all against 386beab has
overall/all 48 exits zero, pytest 43 passes and complete audit 1,066 tests OK/681/0;
evidence 423ab05f08b4ec9f8d5e7c30d1bf600ea07ffb63 under
local-tests-386beab/run-20261106T191207Z-NSLlFY. The user accepted absence of Turn
and related roster workflows and requested 009.4/012 closure on 2026-11-06.
These results supersede the follow-up's pending status, not the original history.
Fixture tests remain distinct from authenticated live-server execution. See
[current implementation, evidence and close-out](../handover/310-admin-rosters.md).

### Accepted scope

Keep the 11 remaining monster-row buttons on one horizontal line. Remove both
per-row HP buttons and their HP change columns from both combatant tables.
Preserve other actions, labels, indicators, accessible names and DOM tab order.
Creation forms and bulk toolbars are unchanged. Other damage/healing workflows,
including Battle Actions, remain available. Character rows otherwise retain
their existing layout.

Keep monster name and species on separate, individually unwrapped lines. Retain
the 16ch name-column minimum and table-local horizontal scrolling. Do not hide
remaining operations, shrink controls excessively or widen the page with the
monster table. Focused monster controls must be fully inside its visible scroller.

### Implementation

The deferred `static/combatant-row-layout.js` is a standalone Admin enhancement,
not an independently loaded Admin source fragment. It removes the obsolete HP
change column from each rendered table and observes direct table replacements
from load(). Removal is from the DOM, not CSS hiding. It validates the column's
buttons before removal, and never mutates encounter data. The legacy core row
templates and delegated HP handlers remain unchanged; the enhancement must be
deployed with the matching template. The same module adjusts only the Monsters
container's scrollLeft on focusin so partially visible controls become fully
visible. Native focus alone did not guarantee that behavior.

No split Admin source, marker, assembly reader, adapter or identity assertion is
modified. The stylesheet targets the remaining display/status action cell.

### Acceptance and closure basis

The agreed scope covers single-line geometry at 1440/768/375 pixels, name/species
readability, removal from both tables after refresh, remaining operations and
alternate HP workflows, forward/reverse keyboard access, local overflow and
existing interaction regressions. The configured CI groups covering the delivered
correction completed successfully. The user accepted closure on 2026-11-03.
This records feature acceptance, not an independently observed manual deployment
runbook or authenticated/live-server browser test.

### Verified successful CI

- Run: `41648384259`, attempt `1`, Branch tests.
- Exact tested SHA: `c19f49b9b5f79093d7bd69768f3eb14eaeabd762`.
- Evidence commit: `0f9b08732648715ebbcfc3675d49572c50032147`.
- Folder: `ci-results-41648384259-attempt-1`.
- Reviewed source: `run.json`; workflow and tests job are completed/success.
- Syntax/import, Python suite including browser fixtures, pytest regressions,
  JavaScript tests and standalone browser/audit steps all report success.

This is verification of workflow/job/step metadata, not review of every individual
test assertion. Local fixtures, CI execution and deployed/authenticated validation
remain distinct. No additional tests were executed for this documentation close-out.
The user explicitly requested [skip ci] for this close-out only; no application,
test or workflow configuration changes or separate workflow dispatch are included.

### Historical failures and preparation

Run 41641117462 attempt 1 tested the earlier name correction. Evidence was
committed at aff0ff459a2aae1e8f4301c40d162097068a711d in
ci-results-41641117462-attempt-1. Its 1,015-test Python suite reported three
viewport failures in the keyboard full-visibility assertion; the connection
audit repeated them, with 673 opened connections and zero without explicit close.
Pytest reported 43 passed, and syntax/import and JavaScript steps succeeded.
That failed run was not acceptance. Run 41642457751 also failed and tested the
earlier Cleanup SHA 571c48ff4814331dd13829dc835eaa56a9b7ffd8, not the final fix;
it is not the evidence used for closure.

Preparation ran Node syntax checking, Python AST parsing and simplified Chromium
fixtures. At 1440/768/375 pixels the exact enhancement removed both HP columns
across three refresh cycles per width and passed 11 forward plus 10 reverse
button checks per width. Document width did not increase; the simplified narrow
fixture retained unrelated Character-table overflow (540px before, 430px after).
An initially overbroad whole-document-width assertion was corrected to measure
introduced overflow; focused-control visibility checks were retained. Those
fixtures were not the assembled application or an authenticated server.

Full-page tests retain geometry, labels, indicators, click targets, Edit/Restore
keyboard checks and strict focused-control visibility; they also cover refresh,
idempotence, reverse traversal and retained Battle Actions damage/heal choices.
The successful CI metadata above supersedes the earlier pending-CI status.

```bash
python tools/run_split_tests.py -- python -m unittest discover -s tests -p 'test_monster*layout.py' -v
python tools/run_split_tests.py -- python -m unittest discover -s tests -p 'test_*.py' -v
```

See [implementation and validation handover](../handover/250-monster-button-layout.md).
