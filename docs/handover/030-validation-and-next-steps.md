# 030 - Open validation and next steps

[Back to handover index](../../HANDOVER.md)

Last updated: 2026-11-01.

## Inspected CI evidence

Run `41295839260`, attempt 1, tested commit `72e1ae7023bb33e47aee3fe8b554786717d1fb1f` on `features/perplexity` and concluded failure. Evidence was read from `ci-results-41295839260-attempt-1/` at commit `8d3fdf5f27a924d81aee561383c4ed7984c15954`.

Run URL: https://github.com/dajomas/Scrying-Glass/actions/runs/41295839260

Dependency installation and Python syntax/server import checks passed. The Python, JavaScript and standalone browser/audit steps failed. Main Python discovery reported 861 tests, 35 failures and 10 errors. The connection-lifetime audit reran discovery and reported the same counts; do not count these as another set of unique failing tests.

## First focused repair

The AST-extracted WebSocket fixture in `tests/test_bughunt_711881a.py` lacked package context and a fixture for its campaign-viewer dependency. Local reproduction exposed `ImportError: attempted relative import with no known parent package` before the first snapshot.

The test-only repair, scope, validation results and limitations are recorded in [WebSocket regression fixture repair](060-websocket-regression-fixture.md). Its local 35-test module passed on Python 3.12.8. This is not a claim that the full CI suite or Python 3.14 run now passes.

## Remaining validation

- Inspect the normal push-triggered CI result for this repair once delivered.
- Investigate the display-connection fixture failures next, then the other reported failure categories separately.
- Do not silently skip tests or relax production authorization to make fixtures pass.
- Keep the incomplete Admin JavaScript split separate from CI-baseline repairs; its helper modules are not activated yet.
- Record each observed result against the actual tested commit and run. A successful import is not a complete application, browser or authorization test.

The current user direction is normal CI on implementation pushes. Do not carry the earlier documentation-only skip request forward.
