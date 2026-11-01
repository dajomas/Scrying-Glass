# 030 - Open validation and next steps

[Back to handover index](../../HANDOVER.md)

Last updated: 2026-11-01.

## Inspected CI evidence

| Run, attempt 1 | Tested commit | Main Python tests | Failures | Errors |
|---|---|---:|---:|---:|
| 41295839260 | 72e1ae7023bb33e47aee3fe8b554786717d1fb1f | 861 | 35 | 10 |
| 41297160008 | aefa5457fcfa84bf918890660ab2f782901a1679 | 866 | 24 | 8 |
| 41298125937 | 897f07907ea9c2e3ddf17f992827590cd3af724a | 873 | 16 | 7 |
| 41298914669 | 0c55cabb37002c4424c46adeacc3b91a00cb2ca4 | 881 | 7 | 7 |
| 41301945996 | 0bbdecc5f7c5e7d5dcb70ea2448f01324e0974bd | 887 | 3 | 7 |

All five runs concluded failure. Dependency installation and Python syntax/server import checks passed. Python, JavaScript and standalone browser/audit stages remained failing. Audit rediscovery is not another set of unique tests.

Historical evidence for run 41301945996 was at `ci-results-41301945996-attempt-1/` in commit `96680deb1d84321043a99bde242b85f4ac18e8e9`.
Run URL: https://github.com/dajomas/Scrying-Glass/actions/runs/41301945996

## Latest historical result supplied for this repair

The continuation request reports run 41305437829, attempt 1, tested commit `5159b33d3f86f7e9bf027d8b8650970cdce47661`: overall failure; dependency installation and syntax/server import checks passed; main Python discovery ran 890 tests with zero assertion failures and seven errors; JavaScript and standalone browser/audit stages remained failing. All ten campaign-router composition unit tests passed. This supersedes the pending-CI note in section 110 for those unit tests, not its integration limitations.

Evidence directory: `ci-results-41305437829-attempt-1/`, retrieved at preparation baseline `d83216cce56c06dca55842471e957b44ddd92cf2`. During this preparation only the reader README and index were read, not the full log or its numbered parts. The result summary above is historical information supplied by the user, not a fresh full-log reconstruction or hash verification.

## Focused repair status

- [WebSocket fixture](060-websocket-regression-fixture.md): 35 module tests passed in run 41297160008.
- [Display connection](070-display-connection-fixture.md): 18 module tests passed in run 41298125937.
- [Lookup diagnostics](080-monster-lookup-diagnostics.md): 17 diagnostic and 15 provider tests passed in run 41298914669.
- [Stats fallback](090-stats-fallback-fixture.md): all 12 class tests passed in run 41301945996, superseding its pending-CI status.
- [Composed campaign router tests](110-composed-campaign-routers.md): revised ten-test unit module passed locally; latest historical CI outcome is recorded above. Production routing was not changed or made idempotent.
- [Pytest imports and execution](120-pytest-module-imports.md): CI dependency and explicit two-module runner repair; normal CI verification remains outstanding.

## Remaining validation

Verify that normal push-triggered CI installs pytest, imports both regression modules during unittest discovery, and executes both modules in the separate pytest step without filtering. Historical collection found 43 cases, not 43 passing tests. See section 120 for local checks and their limitations.

The historical seven Python errors comprise the two missing-pytest imports addressed here and five other errors: duplicate `has_lair` column in the accounts migration test; the campaign viewer browser timeout; two real FastAPI lifespan tests whose context lacks `STORAGE`; and a missing `campaign_owners` table in the campaign viewers test. Reproduce and investigate each remaining error before deciding whether fixture or production changes are appropriate. Do not assume they are all fixture defects.

JavaScript and standalone browser/audit failures also remain unresolved. No full-suite passing result is claimed. [SG-TODO-001](../todo/010-monster-lookup.md) and [SG-TODO-002](../todo/020-monster-damage-effects.md) remain proposed and unrelated. Incomplete Admin source splitting remains inactive. Normal CI remains requested for implementation pushes; do not dispatch an extra workflow.
