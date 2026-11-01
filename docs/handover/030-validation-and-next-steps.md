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

All listed runs concluded failure. Dependency installation and Python syntax/server import checks passed; Python, JavaScript and standalone browser/audit stages remained failing. Audit rediscovery is not another set of unique tests.

Historical evidence for run 41301945996 was at `ci-results-41301945996-attempt-1/` in commit `96680deb1d84321043a99bde242b85f4ac18e8e9`.

Latest inspected evidence: `ci-results-41315942451-attempt-1/` at `6fbe4c1578a7b4f7725a87adb2c1ea2613946e76`. Run metadata and selected log parts were read, including parts 65 through 71 for the unittest errors and pytest result. The full 101-part log was not reconstructed or hash-verified.

Run 41315942451 executed both complete regression modules on Python 3.14.9: `43 passed in 0.90s`. This supersedes section 120's outstanding CI verification for the pytest repair, without turning its historical collection checks into execution evidence. The main unittest count is separate from those 43 pytest cases.

## Historical intermediate result

The continuation request supplied run 41305437829, attempt 1, tested commit `5159b33d3f86f7e9bf027d8b8650970cdce47661`: overall failure; dependency installation and syntax/server import checks passed; 890 main Python tests, zero assertion failures and seven errors; all ten composed-router unit tests passed; JavaScript and standalone checks failed. That historical summary was not independently reconstructed in the pytest repair preparation. The latest run above supersedes its overall counts.

## Focused repair status

- [WebSocket fixture](060-websocket-regression-fixture.md): 35 module tests passed in run 41297160008.
- [Display connection](070-display-connection-fixture.md): 18 module tests passed in run 41298125937.
- [Lookup diagnostics](080-monster-lookup-diagnostics.md): 17 diagnostic and 15 provider tests passed in run 41298914669.
- [Stats fallback](090-stats-fallback-fixture.md): all 12 class tests passed in run 41301945996.
- [Composed campaign router tests](110-composed-campaign-routers.md): ten unit tests passed locally and in the supplied intermediate CI result. Production routing was not changed or made idempotent.
- [Pytest imports and execution](120-pytest-module-imports.md): verified by 43 passing CI cases in run 41315942451.
- [Accounts migration fixture](130-accounts-migration-fixture.md): corrected v3 fixture and stronger preservation/backup checks; focused local harness passed, full-checkout CI remains outstanding.

## Remaining validation

Inspect normal push-triggered CI for the accounts fixture repair. Do not predict a full-suite count or claim its account module passes before checking that run.

The five errors in run 41315942451 were the duplicate `has_lair` column in the accounts migration test, the campaign viewer browser timeout, two lifespan tests missing `context.STORAGE`, and the missing `campaign_owners` table. Only the accounts fixture is addressed by the current repair. Reproduce and investigate each other error before deciding whether fixtures or production code need changes.

JavaScript and standalone browser/audit failures remain unresolved. No full-suite passing result is claimed. [SG-TODO-001](../todo/010-monster-lookup.md) and [SG-TODO-002](../todo/020-monster-damage-effects.md) remain proposed and unrelated. Incomplete Admin source splitting remains inactive. Normal CI remains requested for implementation pushes; do not dispatch an extra workflow.
