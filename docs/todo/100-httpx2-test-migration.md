# 100 - HTTPX2 test migration

[Back to TODO index](../../TODO.md)

## SG-TODO-010 - Migrate HTTP-client tests to HTTPX2

- Status: in progress; migration delivered at 11835d414d701f0fc6a3a701def29594cab287a3. The three migrated fixture tests passed locally; full-suite validation remains pending after a separate layout-test correction.
- Requested: 2026-11-06, including [skip ci] for the migration push only.
- Priority, owner and deadline: not assigned.
- Scope: direct HTTPX2 ASGI fixtures, shared test requirements and CI/local setup documentation. Runtime requirements and Python 3.10 application support remain unchanged; test environment requires Python 3.11+.
- Dependency: install requirements-test.txt and Playwright Chromium in the selected test environment; CI remains Python 3.14/Node 22.

### Delivered migration

FastAPI TestClient in test_admin_split_runtime.py was replaced with httpx2.AsyncClient/ASGITransport and isolated async unittest methods, retaining existing assertions and adding HTTPX2 type assertions. requirements-test.txt is used for CI dependency installation and cache inputs. No sys.modules patch, alias_httpx call, fallback to legacy httpx, runtime change or separate CI dispatch was introduced.

### Evidence reviewed - 2026-11-06

Evidence commit: 72923ec4e34a6a1065332495015a0a768fe7a98f. Tested source commit: e7b229caa04494ec5a2b4fed7a0d66301359a12e. Run directory: local-tests-e7b229c/run-20261106T103855Z-QWqmWA. Environment: Python 3.14.7, Node 22.23.2, WSL2 kernel; suite=all, completed=1. This is published local evidence, not a CI run.

The available main unittest log explicitly reports all three AdminSplitRuntimeTests methods as ok. Pytest reports 43 passed; all 37 JavaScript commands returned zero. Compilation and server import returned zero. The overall exit code is 1: unittest and the connection audit failed. The complete audit log reports 1,022 tests with two monster-name minimum-width failures (137.265625 versus 137.281 CSS px at 768/375 viewports) and 673 opened connections with zero without explicit close. The main unittest log was truncated by the connector before its final failure summary, so no claim that its only failures were those two is made.

### Corrective preparation and remaining validation

The user requested fixes and a GitHub push after reviewing the failed run. The prepared test-only correction replaces exact minimum-width comparison with a bounded 1/32 CSS px tolerance plus finite/positive measurement guards. Seven added numeric guard tests cover the observed values, exact/wider widths, the tolerance boundary, just-beyond-boundary rejection, real deficits, nonfinite values and zero minimum. They passed in isolation during preparation; the Playwright fixture/full suite were not rerun locally. Production CSS and accepted SG-TODO-007 layout behaviour remain unchanged.

- [ ] Verify fresh-environment requirements installation and resolved versions; existing evidence does not establish absence of an already-installed legacy httpx package.
- [x] Observe all three migrated AdminSplitRuntimeTests methods pass in published local output.
- [ ] Run the corrected name-layout browser fixture at all existing widths and both name/activity cases.
- [ ] Obtain and review a complete successful suite, including the connection audit, against the corrective commit.
- [ ] Review future CI installation and execution results before closing; this corrective push has no [skip ci] marker, unlike the original migration push.

See [testing handover](../handover/020-ci-and-tests.md#local-results-review-and-layout-test-correction---2026-11-06). SG-TODO-009 remains independently proposed; this task is not marked completed from partial success.
