# 680 - CI: connection audit as a parallel job (SG-TODO-023 first half)

[Back to HANDOVER index](../../HANDOVER.md)

Implementation group 2 on `features/claude`, 2026-11-21. Measurements, the evidence that
both passes are needed, the options and the user's decision are in
[230 - First half](../todo/230-test-suite-necessity-review.md#first-half-measurements-and-decision-2026-11-21).

## Change

- `.github/workflows/tests.yml`: new job `connection-audit` (checkout, Python 3.14, Node 22,
  test dependencies, Chromium preflight, then `tests/audit_connection_lifetime.py`). No
  `needs`, so it runs in parallel with `tests`.
- Job `tests`: the step formerly named "Standalone Python browser and audit checks" is now
  "Standalone Python browser checks" and skips `audit_connection_lifetime.py`; everything
  else is unchanged.
- `tests/test_ci_browser_provisioning.py`: reads both jobs; checks that the audit job is
  parallel, has the same environment, setup actions, dependency and Chromium steps and
  prerequisites, and runs the complete audit; and that the standalone loop leaves out only
  the audit script.
- `tools/publish_ci_results.sh` already collects every job and the whole run log, so
  publishing is unchanged.

## Validation

- Local: `test_ci_browser_provisioning` passes (12 tests); the new standalone loop finds
  `feedback_browser_fixture.py` and `storage_migration_fixtures.py`, as CI 44888887657 did.
- First run with both jobs, CI 44926301833 on d2262b1: both green. `tests` took 7 min 26 s
  (combined pass: 2,310 tests in 345 s), `connection-audit` 5 min 44 s (254 modules,
  0 failed). Wall time 7.5 minutes instead of about 13.5 before.
