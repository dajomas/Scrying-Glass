# 070 - Single-line monster buttons

[Back to TODO index](../../TODO.md)

## SG-TODO-007 - Restructure monster buttons into one line

- Status: in progress; corrective delivery prepared; new CI and deployed acceptance pending.
- Requested: 2026-11-02. Single-line/local-scroll scope approved: 2026-11-03.
- Scope updated by user on 2026-11-03: remove Damage and Heal from both Character and Monster rows.
- Priority, owner and deadline: not assigned.
- Initial delivery: `da8e7352fee0b504628aeed94aae6687341e2c35`.
- Name-column correction: `49aed0cbf074d63930ce29a8d64ef2d9cc970226`.

### Current scope

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
modified. The stylesheet now targets the remaining display/status action cell.

### Acceptance and validation

- [ ] All 11 remaining monster buttons are on one line at 1440, 768 and 375 pixels.
- [ ] Name/species remain readable, including long names and the Ally suffix.
- [ ] Neither combatant table contains row Damage/Heal controls or an HP change column, including after refresh.
- [ ] Other operations, indicators and damage/healing workflows remain available.
- [ ] Forward/reverse keyboard focus fully exposes each remaining monster control.
- [x] Narrow-screen policy agreed: Monsters-table-local scrolling.
- [ ] Monster table does not widen its ancestors.
- [ ] Full configured CI and existing interaction regressions pass.
- [ ] Deployed-interface acceptance.

### Evidence and remaining checks

Run 41641117462 attempt 1 tested 49aed0cbf074d63930ce29a8d64ef2d9cc970226.
Evidence: `aff0ff459a2aae1e8f4301c40d162097068a711d`, folder
`ci-results-41641117462-attempt-1`. The 1,015-test Python suite reported three
failing viewport subtests in the keyboard method's full-visibility assertion.
The connection audit reran discovery and repeated those failures; its 673 opened
connections had zero without explicit close. Pytest reported 43 passed; syntax/
import and JavaScript steps reported success. This is failed CI, not acceptance.

Corrective preparation ran Node syntax checking of the new module, Python AST
parsing of the updated browser module and simplified Chromium fixtures. At
1440/768/375 pixels the exact module removed both tables' obsolete columns across
three refresh cycles per width and passed 11 forward plus 10 reverse button
checks per width. Document width did not increase; the simplified 375px fixture
retained unrelated Character-table overflow (540px before, 430px after). These
are not assembled-page or authenticated-server results. An initial overly broad
whole-document-width assertion failed on that fixture and was corrected to
measure whether this change introduced overflow; focus checks were retained.

The full-page tests retain geometry, labels, indicators, click targets, Edit and
Restore statistics keyboard checks and the strict focused-control visibility
assertion. They add removal-after-refresh, idempotent installation, reverse
traversal and retained Battle Actions damage/heal choices. Full-page execution,
new CI and authenticated/deployed validation remain pending. No CI skip.

```bash
python tools/run_split_tests.py -- python -m unittest discover -s tests -p 'test_monster*layout.py' -v
python tools/run_split_tests.py -- python -m unittest discover -s tests -p 'test_*.py' -v
```

The user collects evidence with getworkflow.sh and supplies its run, tested SHA,
evidence commit and folder. See [handover](../handover/250-monster-button-layout.md).
