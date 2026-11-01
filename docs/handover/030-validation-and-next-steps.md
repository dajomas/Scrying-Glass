# 030 - Open validation and next steps

[Back to handover index](../../HANDOVER.md)

Last updated: 2026-11-01.

## Inspected CI evidence

| Run, attempt 1 | Tested commit | Main Python tests | Failures | Errors |
|---|---|---:|---:|---:|
| 41295839260 | 72e1ae7023bb33e47aee3fe8b554786717d1fb1f | 861 | 35 | 10 |
| 41297160008 | aefa5457fcfa84bf918890660ab2f782901a1679 | 866 | 24 | 8 |

Both runs concluded failure. Dependency installation and Python syntax/server import checks passed. Python, JavaScript and standalone browser/audit steps failed. Repeated discovery by the connection-lifetime audit is not another set of unique tests.

Latest evidence: `ci-results-41297160008-attempt-1/` at commit `d9f4b54bb8d80d5f6435491b6d074752803896de`.
Run URL: https://github.com/dajomas/Scrying-Glass/actions/runs/41297160008

## First repair confirmed in CI

All 35 tests in `tests/test_bughunt_711881a.py` passed in run 41297160008, including the five added regressions. The main-suite failure/error reduction matches the original module's 11 failures and 2 errors. Details: [WebSocket regression fixture repair](060-websocket-regression-fixture.md).

## Display-connection repair

`tests/test_display_connection.py` had a separate extracted scope missing both module name and package context. Its viewer import raised `KeyError: "'__name__' not in globals"` before the first snapshot. The focused test-only repair reproduced 8 failures and 1 error in the original 11 tests, then passed 18 tests locally on Python 3.12.8. Details and limits: [Display-connection fixture repair](070-display-connection-fixture.md).

## Remaining validation

- Inspect normal push-triggered CI for the display-connection repair after delivery; no result for it is claimed yet.
- Investigate the D&D Beyond diagnostic failures next as a separate change.
- Do not silently skip tests or relax production authorization to make fixtures pass.
- Keep incomplete Admin source splitting separate from CI-baseline repairs; its helpers are not activated.
- Record results against actual tested commits and runs. Fixture tests are not full application, transport or campaign-ACL integration tests.

Normal CI is requested for implementation pushes. Do not carry an earlier documentation-only skip request forward.
