# 190 - Activity log affected unit and resulting value

[Back to TODO index](../../TODO.md)

## SG-TODO-019 - Include the affected unit and new value in Activity log lines

Status: in progress - implemented on `features/perplexity` 2026-11-13 at the user's request; CI validation and user acceptance pending. Requested by the user on 2026-11-10 as a backlog addition. No priority, owner or deadline has been assigned. Implementation detail, preserved behavior and limits: [580 handover](../handover/580-activity-log-result-details.md).

### Requested behavior

In each Activity log line describing a value change, identify the affected unit/combatant and include the resulting new value. Make clear which property changed; retain the measurement unit where applicable. Here, affected unit means the character, monster or other encounter entity impacted, not merely the numeric unit of measurement.

### Acceptance criteria and planned validation

- Relevant value-change entries identify the affected unit/combatant, the changed property and its resulting value in the same line.
- Report the actual resulting value after the operation, not just the requested change or delta.
- Entries remain distinguishable when similar units or multiple affected combatants are involved.
- Preserve combat behavior, permissions and existing log history; the logging enhancement must not apply an operation again.
- Before implementation, inspect the actual log producers and agree any unresolved coverage details. Add focused regressions for the affected producers and verify readable Activity log output for representative changes, including multiple affected units.

The original 2026-11-10 entry recorded requested work only. The coverage details it left open were settled during implementation (below) and are open for the user to review at acceptance.

### Coverage decisions - 2026-11-13

- Covered value changes: HP and temporary HP from Battle Actions damage/heal, inline character/monster HP deltas, lair damage and encounter-features edits; life-state and death-save changes; death-save failures; attack statistic reductions; and statistic restore/base edits.
- Details are written into the existing `note` field (Details column, CSV/JSON export) as `Unit: Property old → new`. HP results include the new maximum. The Target column and IDs are unchanged.
- Not covered, because no value changes: buff/debuff, effects, concentration events, lair create/update/remove, undo and checkpoint restore. The instant-death note already states excess and maximum HP and is unchanged.
- Existing log entries are not rewritten.

### Acceptance status

| Criterion | Status |
| --- | --- |
| Unit, property and resulting value in the same line | Implemented; covered by producer and render tests |
| Actual resulting value, not only the delta | Implemented; before/after snapshots are taken around the existing operation |
| Distinguishable similar/multiple units | Implemented; multi-goblin batch test and render test |
| Combat, permissions and history preserved; no re-application | Implemented; HP assertions, untouched-history test and full suites |
| Focused regressions and readable output | Added; loaded-Admin render with intercepted HTTP only |
| CI and user acceptance | Pending |

### Validation - 2026-11-13

Observed locally in this environment on the uncommitted change (base `d20c3910`), not CI:

- `tools/run_split_tests.py -- python3 -m unittest discover -s tests -p 'test_*.py'`: Ran 1,600 tests, OK.
- `tools/run_split_tests.py -- python3 -m pytest -q`: 1,643 passed, 507 subtests passed.
- Node tests (`tests/*.test.cjs`, each run with `node --test`): 638 pass, 0 fail.
- Standalone browser/audit scripts: 7 PASS, plus 43 passed in the bundled pytest selection.
- Negative control at `d20c3910` with only the formatter module added: 8 of the 17 new tests fail (all producer/render behavior tests).

CI has not been checked; record the workflow run and attempt here once the user supplies them.
