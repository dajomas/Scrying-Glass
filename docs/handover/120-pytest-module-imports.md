# 120 - Pytest module imports and execution

[Back to handover index](../../HANDOVER.md)

Last updated: 2026-11-01.

## Baseline and cause

Prepared from working-branch HEAD `d83216cce56c06dca55842471e957b44ddd92cf2`, with source retrieval pinned to that commit. Section 120 did not exist there. The prior chat's unapproved draft was not treated as repository content or authorization.

Retrieved Git blobs match the historical values supplied by the user:

- `.github/workflows/tests.yml`: `05aec3489351d24e85588e8d23a28dc8baecb9b4`.
- `tests/test_death_save_validation_2ba6607.py`: `67fb438b7e9227d5e6524078921bb601025578f9`.
- `tests/test_slug_truncation_82860c4.py`: `d749acd3c36a80d7d3f4eae4888b9461c99dadd0`.

Both test modules import pytest and use pytest parametrization; they rely on fixtures including `encounter` and `tmp_path`. CI installed httpx and Playwright but not pytest. Unittest discovery therefore reported two module-import errors. Installing pytest alone permits imports but does not execute the modules' pytest-style test functions.

## Workflow repair

Add pytest only to the CI dependency installation command. Preserve runtime requirements and every existing workflow step, trigger, permission, timeout and test assertion. After unittest and before JavaScript add:

```yaml
- name: Pytest regression modules
  if: ${{ !cancelled() }}
  run: >-
    python -m pytest -q
    tests/test_death_save_validation_2ba6607.py
    tests/test_slug_truncation_82860c4.py
```

Both modules run without case filtering. Normal push-triggered CI is required; the commit message has no skip marker and no extra workflow dispatch is requested. No application code, test assertions or local import stand-ins belong in this repair.

## Fresh preparation checks

The reconstructed original workflow matched its Git blob. Candidate YAML parsed successfully. Structural comparison confirmed all existing configuration and steps were unchanged except the dependency addition and new pytest step, whose folded command names both complete modules. All six candidate workflow run blocks passed `bash -n`.

Current local Python is 3.12.8. Pytest and Playwright are importable; FastAPI and Starlette are absent. These availability checks do not establish browser binary availability or successful test execution. No fresh collection, regression execution or full CI run was performed during this preparation.

## Historical local results supplied by the user

The previous chat reported these checks; they were not rerun here:

- Missing-pytest imports reproduced with site packages disabled.
- Python 3.12.8 with pytest 8.3.5 collected 43 cases: 32 death-save and 11 slug cases.
- Collection used import-only stand-ins for encounter/storage dependencies. Those were local harness files only and must never be committed.
- Ten canonical-slug cases passed against pinned production slug functions.
- The other 33 database-backed cases were not executed locally.

Collection success is not execution success. Do not claim that all 43 cases pass.

## Outstanding verification and continuity

Python 3.14 execution and full CI remain unverified for this repair. After approved delivery, inspect the actual push-triggered run and record its commit and results; do not infer workflow startup, completion or success from configuration alone. Require both regression modules to execute without filtering and report their actual outcomes. Other Python, JavaScript and browser/audit failures remain separate investigations; see [open validation](030-validation-and-next-steps.md).

README and the indexed TODO documents were reviewed. No runtime documentation change or status change to [SG-TODO-001](../todo/010-monster-lookup.md) or [SG-TODO-002](../todo/020-monster-damage-effects.md) is warranted by this CI repair. The broader source split remains unfinished and the Admin adapter remains inactive.
