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
| 41315942451 | 8b2a3fac577522e0860a3fe32bd13443bbac94c1 | 888 | 0 | 5 |
| 41318275558 | f031ccf9185ad0ab0e9ad7b4673adf1f7fb5f7ad | 888 | 0 | 4 |

All listed runs concluded failure. Dependency installation and Python syntax/server import checks passed; Python, JavaScript and standalone browser/audit stages remained failing. Audit rediscovery is not another set of unique tests.

Historical evidence for run 41301945996 was at `ci-results-41301945996-attempt-1/` in commit `96680deb1d84321043a99bde242b85f4ac18e8e9`.

Run 41315942451 evidence was inspected at `6fbe4c1578a7b4f7725a87adb2c1ea2613946e76`, including selected parts 65 through 71. Its complete 101-part log was not reconstructed or hash-verified. Both complete pytest regression modules passed: `43 passed in 0.90s` on Python 3.14.9.

Latest evidence: `ci-results-41318275558-attempt-1/` at `1cfb256cb090ca3834eb2f61d12eca23ce67d4f9`. The preceding inspection read run metadata and selected log parts, including account results in parts 18-19 and the unittest/pytest summary in part 70. All 13 AccountTests passed, including the repaired v3 migration test; pytest reported `43 passed in 1.09s` on Python 3.14.9. The full 100-part log was not reconstructed or hash-verified. Main unittest and pytest counts are separate.

## Historical intermediate result

The continuation request supplied run 41305437829, attempt 1, tested commit `5159b33d3f86f7e9bf027d8b8650970cdce47661`: overall failure; dependency installation and syntax/server import checks passed; 890 main Python tests, zero assertion failures and seven errors; all ten composed-router unit tests passed; JavaScript and standalone checks failed. That historical summary was not independently reconstructed in the pytest repair preparation. Later inspected runs supersede its overall counts.

## Focused repair status

- [WebSocket fixture](060-websocket-regression-fixture.md): 35 module tests passed in run 41297160008.
- [Display connection](070-display-connection-fixture.md): 18 module tests passed in run 41298125937.
- [Lookup diagnostics](080-monster-lookup-diagnostics.md): 17 diagnostic and 15 provider tests passed in run 41298914669.
- [Stats fallback](090-stats-fallback-fixture.md): all 12 class tests passed in run 41301945996.
- [Composed campaign router tests](110-composed-campaign-routers.md): ten unit tests passed locally and in the supplied intermediate CI result. Production routing was not changed or made idempotent.
- [Pytest imports and execution](120-pytest-module-imports.md): verified by 43 passing cases in both latest inspected runs; this supersedes section 120's pending-CI note.
- [Accounts migration fixture](130-accounts-migration-fixture.md): all 13 account tests passed in run 41318275558; this supersedes section 130's pending-CI note.
- [Viewer ownership fixtures](140-viewer-ownership-fixtures.md): targets the remaining four Python errors with browser payload, composed-initializer and ownership-scoped ACL fixture corrections. Focused local checks passed; actual framework/browser and full-checkout CI verification remain outstanding.

## Remaining validation

Inspect normal push-triggered CI for all three changed viewer test modules and the full Python suite. Do not predict a full-suite count or claim the four errors are gone before checking the run. The lifecycle tests must execute with FastAPI installed rather than merely skip; the browser test must execute with Chromium.

Run 41318275558's four errors were the viewer browser timeout, two lifespan tests missing `context.STORAGE`, and the missing `campaign_owners` table in the outdated admin-all-campaigns test. Section 140 records separate reproduction and diagnosis for these paths; production authorization is unchanged.

JavaScript and standalone browser/audit failures remain unresolved. No full-suite passing result is claimed. [SG-TODO-001](../todo/010-monster-lookup.md) and [SG-TODO-002](../todo/020-monster-damage-effects.md) remain proposed and unrelated. Incomplete Admin source splitting remains inactive. Normal CI remains requested for implementation pushes; do not dispatch an extra workflow.
