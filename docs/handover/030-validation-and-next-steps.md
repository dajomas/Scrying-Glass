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

Latest evidence: `ci-results-41301945996-attempt-1/` at commit `96680deb1d84321043a99bde242b85f4ac18e8e9`.
Run URL: https://github.com/dajomas/Scrying-Glass/actions/runs/41301945996

## Focused repair status

- [WebSocket fixture](060-websocket-regression-fixture.md): 35 module tests passed in run 41297160008.
- [Display connection](070-display-connection-fixture.md): 18 module tests passed in run 41298125937.
- [Lookup diagnostics](080-monster-lookup-diagnostics.md): 17 diagnostic and 15 provider tests passed in run 41298914669.
- [Stats fallback](090-stats-fallback-fixture.md): all 12 class tests passed in run 41301945996, superseding its pending-CI status.
- [Composed campaign router tests](110-composed-campaign-routers.md): seven original unit tests reproduced three failures; the revised ten-test unit module passed locally on Python 3.12.8. CI is pending.

## Remaining validation

The latest three Python assertion failures were the route fixture counting two different composed components as duplicates. The test-only candidate now verifies four unique path/method keys and both initialization lifespans. No production installer was removed or made idempotent.

Inspect normal CI for this candidate after delivery. Separately investigate the seven Python errors, real FastAPI lifespan integration fixtures, JavaScript failures and standalone browser/audit failures. No full-suite passing result is claimed. SG-TODO-001 remains proposed and unrelated. Incomplete Admin source splitting remains inactive. Normal CI remains requested for implementation pushes.
