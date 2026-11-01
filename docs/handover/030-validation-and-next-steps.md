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
| 41319342579 | 7b0967c06913272856e83eb0d675850f3c430ae5 | 889 | 0 | 0 |

All listed workflows concluded failure. Dependency installation and syntax/server import checks passed. In run 41319342579, main unittest discovery also passed (`889 tests in 25.476s`, `OK`); JavaScript and standalone Python browser/audit stages still failed. Audit rediscovery is not another set of unique tests. Main unittest and separate pytest counts must not be conflated.

Historical evidence for run 41301945996 was at `ci-results-41301945996-attempt-1/` in commit `96680deb1d84321043a99bde242b85f4ac18e8e9`. Run 41315942451 was inspected at `6fbe4c1578a7b4f7725a87adb2c1ea2613946e76`; selected parts included 65-71, not a full reconstruction of its 101-part log. Both pytest modules passed 43 cases in 0.90s on Python 3.14.9.

Run 41318275558 evidence was inspected at `1cfb256cb090ca3834eb2f61d12eca23ce67d4f9`, including account results in parts 18-19 and the summary in part 70. All 13 AccountTests passed; pytest passed 43 cases in 1.09s on Python 3.14.9. Its full 100-part log was not reconstructed or hash-verified.

Latest evidence: `ci-results-41319342579-attempt-1/` at `8f07bbf8a936794c9aa46ac234625a760b845231`. The prior result inspection read metadata and selected parts 46-49 and 65-66. All eight viewer browser tests, both real FastAPI lifespan tests and all 19 CampaignViewerTests passed; neither lifespan test skipped. Pytest passed 43 cases in 1.03s on Python 3.14.9.

The subsequent JavaScript investigation read numbered parts 67-88 in order, supplementing the preceding part 66. It identified two failing files: `tests/test_bughunt_985b4b2.js` and `tests/test_lair_presentation.js`, both failing because their renderer VM lacked `window`. This is selected-region inspection, not reconstruction or SHA-256 verification of the entire 91-part workflow log.

## Historical intermediate result

The continuation request supplied run 41305437829, attempt 1, tested commit `5159b33d3f86f7e9bf027d8b8650970cdce47661`: overall failure; dependency installation and syntax/server import checks passed; 890 main Python tests, zero assertion failures and seven errors; all ten composed-router unit tests passed; JavaScript and standalone checks failed. That summary was not independently reconstructed in the pytest repair preparation. Later inspected runs supersede its overall counts.

## Focused repair status

- [WebSocket fixture](060-websocket-regression-fixture.md): 35 module tests passed in run 41297160008.
- [Display connection](070-display-connection-fixture.md): 18 module tests passed in run 41298125937.
- [Lookup diagnostics](080-monster-lookup-diagnostics.md): 17 diagnostic and 15 provider tests passed in run 41298914669.
- [Stats fallback](090-stats-fallback-fixture.md): all 12 class tests passed in run 41301945996.
- [Composed campaign router tests](110-composed-campaign-routers.md): ten unit tests passed in the latest inspected run; production routing was not changed or made idempotent.
- [Pytest imports and execution](120-pytest-module-imports.md): verified by 43 passing cases in the latest three inspected runs; supersedes section 120's pending-CI note.
- [Accounts migration fixture](130-accounts-migration-fixture.md): all 13 account tests passed in run 41318275558; supersedes section 130's pending-CI note.
- [Viewer ownership fixtures](140-viewer-ownership-fixtures.md): verified in run 41319342579, including actual browser and FastAPI execution; supersedes section 140's pending-CI note.
- [Renderer VM window](150-renderer-vm-window.md): two one-line test-fixture changes; local targeted checks passed, normal CI remains outstanding.

## Remaining validation

Inspect normal push-triggered CI for both repaired JavaScript files and the entire JavaScript stage on Node 22. Preserve all existing cases and fail on assertion errors; do not infer a clean stage from the two focused local runs. Continue checking the previously clean unittest and pytest stages.

Standalone Python browser/audit failures remain a separate investigation. A passing main unittest stage does not imply every Python-based check passed. No full-workflow passing result is claimed.

[SG-TODO-001](../todo/010-monster-lookup.md) and [SG-TODO-002](../todo/020-monster-damage-effects.md) remain proposed and unrelated. Incomplete Admin source splitting remains inactive. Normal CI remains requested for implementation pushes; do not dispatch an extra workflow.
