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

All four runs concluded failure. Dependency installation and Python syntax/server import checks passed. Python, JavaScript and standalone browser/audit stages remained failing. Audit rediscovery is not another set of unique tests.

Latest evidence: `ci-results-41298914669-attempt-1/` at commit `188bc2d82caeb39fa12a6bba59ac598d19edd75c`.
Run URL: https://github.com/dajomas/Scrying-Glass/actions/runs/41298914669

## Focused repair status

- [WebSocket fixture](060-websocket-regression-fixture.md): 35 module tests passed in run 41297160008.
- [Display-connection fixture](070-display-connection-fixture.md): 18 module tests passed in run 41298125937.
- [Lookup diagnostics](080-monster-lookup-diagnostics.md): all 17 diagnostic and 15 provider/fallback tests passed in run 41298914669, superseding its earlier pending-CI status.
- [Stats fallback fixture](090-stats-fallback-fixture.md): original six focused tests reproduced four failures; repaired class passed 12 focused tests locally on Python 3.12.8. CI is pending for this repair.

## Remaining validation

Inspect normal push-triggered CI for the StatsFallbackTests repair after delivery. Investigate campaign-viewer route/router duplication separately, and inventory the remaining Python errors and JavaScript/browser failures before changing them. No full-suite passing result is claimed. Do not skip tests or weaken authorization to make fixtures pass. Incomplete Admin source splitting remains separate and inactive. Normal CI remains requested for implementation pushes.
