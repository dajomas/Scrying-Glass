# 190 - Activity log affected unit and resulting value

[Back to TODO index](../../TODO.md)

## SG-TODO-019 - Include the affected unit and new value in Activity log lines

Status: completed and closed for the agreed scope on `features/perplexity`, final
user acceptance 2026-11-13 at 09:04 CET: "Proceed with final acceptance and close
out SG-TODO-019". Requested 2026-11-10; implemented 2026-11-13. No priority,
owner or deadline assigned. Implementation, scope and evidence limits:
[580 accepted close-out](../handover/580-activity-log-result-details.md#sg-todo-019-accepted-close-out---2026-11-13).
Earlier CI/acceptance-pending notes are superseded; do not request acceptance again.

### Requested behavior

In each Activity log line describing a value change, identify the affected unit/combatant and include the resulting new value. Make clear which property changed; retain the measurement unit where applicable. Here, affected unit means the character, monster or other encounter entity impacted, not merely the numeric unit of measurement.

### Acceptance criteria and planned validation

- Relevant value-change entries identify the affected unit/combatant, the changed property and its resulting value in the same line.
- Report the actual resulting value after the operation, not just the requested change or delta.
- Entries remain distinguishable when similar units or multiple affected combatants are involved.
- Preserve combat behavior, permissions and existing log history; the logging enhancement must not apply an operation again.
- Before implementation, inspect the actual log producers and agree any unresolved coverage details. Add focused regressions for the affected producers and verify readable Activity log output for representative changes, including multiple affected units.

The original 2026-11-10 entry recorded requested work only. Its open coverage details
were settled in implementation below and are now accepted for this bounded scope,
not a claim of unperformed manual verification or a new coverage expansion.

### Coverage decisions - 2026-11-13

- Covered value changes: HP and temporary HP from Battle Actions damage/heal, inline character/monster HP deltas, lair damage and encounter-features edits; life-state and death-save changes; death-save failures; attack statistic reductions; and statistic restore/base edits.
- Details are written into the existing `note` field (Details column, CSV/JSON export) as `Unit: Property old → new`. HP results include the new maximum. The Target column and IDs are unchanged.
- Existing event notes not expanded by this task: buff/debuff, effects, concentration events and lair create/update/remove; undo and checkpoint restore do not gain per-value difference reports. The instant-death note already states excess and maximum HP and is unchanged. This is an explicit coverage boundary, not a claim that undo/restore can never change values.
- Existing log entries are not rewritten.

### Acceptance status

| Criterion | Status |
| --- | --- |
| Unit, property and resulting value in the same line | Completed/accepted; implemented with producer and render coverage |
| Actual resulting value, not only the delta | Completed/accepted; before/after snapshots around the existing operation |
| Distinguishable similar/multiple units | Completed/accepted; multi-goblin batch and render coverage |
| Combat, permissions and history preserved; no re-application | Completed/accepted on stated tests/evidence limits; historical entries unchanged |
| Focused regressions and readable output | Completed/accepted; loaded-Admin render uses intercepted HTTP |
| Covering CI | Successful Branch tests 43386246710 attempt 1, tested 4a1feb47654ea6665862ec44b3f52dc6a27458b8 |
| Final user acceptance | Explicit close-out request, 2026-11-13 at 09:04 CET |

### Covering CI and close-out - 2026-11-13

Implementation: 4a1feb47654ea6665862ec44b3f52dc6a27458b8 on features/perplexity.
Successful Branch tests 43386246710 attempt 1, job 131755311158; evidence
publication 5b1a0a6270adea9e67ca9ffd1def534b875f1317, directory
ci-results-43386246710-attempt-1. Reviewed run.json/jobs.json agree on tested SHA,
branch, attempt and completed/success. All configured Chromium provisioning,
syntax/import, main Python/browser, pytest regression, JavaScript and standalone
browser/audit stages succeeded. No failed stage requires correction.

Review covered run/job outcomes, not individual re-review of every test log or
screenshot. Local counts below are not verified hosted-CI counts. No new tests,
authenticated live-server, human visual or screen-reader review is claimed. This
close-out changes documentation only with [skip ci]; no code/test/workflow changes
or separate dispatch, merge or deployment. No new close-out commit SHA is invented
before publication. No SG-TODO-019 implementation, CI or acceptance action remains;
009 and 009.7 remain closed. No new scope, priority or future blanket write approval.

### Validation - 2026-11-13

Historical local preparation on the then-uncommitted change, base `d20c3910`, not
hosted CI and not rerun for this close-out:

- `tools/run_split_tests.py -- python3 -m unittest discover -s tests -p 'test_*.py'`: Ran 1,600 tests, OK.
- `tools/run_split_tests.py -- python3 -m pytest -q`: 1,643 passed, 507 subtests passed.
- Node tests (`tests/*.test.cjs`, each run with `node --test`): 638 pass, 0 fail.
- Standalone browser/audit scripts: 7 PASS, plus 43 passed in the bundled pytest selection.
- Negative control at `d20c3910` with only the formatter module added: 8 of the 17 new tests fail (all producer/render behavior tests).

The successful hosted run and final acceptance above supersede the old unchecked-CI
note. The User Guide's delivered behavior remains unchanged by this close-out.
