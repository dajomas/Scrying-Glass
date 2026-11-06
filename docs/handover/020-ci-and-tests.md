# 020 - CI workflow and test coverage

[Back to handover index](../../HANDOVER.md)

## Trigger and skip behavior

Workflow: `Branch tests`, defined in [tests.yml](../../.github/workflows/tests.yml).

- Trigger: pushes to `features/perplexity` only.
- No path filter: documentation changes also trigger it unless skipped.
- GitHub's native push-workflow skip behavior honors `[skip ci]` in commit messages. No custom skip job is used.
- For documentation-only pushes explicitly requested without CI, include `[skip ci]` in the commit message.
- No pull-request, scheduled or manual-dispatch trigger is configured.

Example documentation commit message:

```text
docs: update indexed handover [skip ci]
```

GitHub skip-workflow documentation: https://docs.github.com/en/actions/how-tos/manage-workflow-runs/skip-workflow-runs

## Execution environment

- Runner: `ubuntu-latest`.
- Python: 3.14, with pip caching.
- Node.js: 22.
- Dependencies: `requirements.txt`, plus `httpx`, `playwright` and `pytest`.
- Browser: Playwright Chromium, installed with operating-system dependencies.
- Repository and tests directories are included in `PYTHONPATH`.
- Workflow token permission: `contents: read`.
- Job timeout: 30 minutes.

This is one selected CI environment, not a compatibility matrix. Dependency specifications are not a lockfile. Pytest is a CI test dependency; application runtime requirements are unchanged.

## Checks configured

1. Compile Python source and tests, then import `scrying_glass_server`.
2. Run `python -m unittest discover -s tests -p 'test_*.py' -v`, including unittest-based browser fixtures.
3. Run `python -m pytest -q tests/test_death_save_validation_2ba6607.py tests/test_slug_truncation_82860c4.py` without case filtering.
4. Find every `.js` and `.cjs` file under `tests/` and run each with `node --test`.
5. Execute standalone Python files under `tests/` whose names do not match `test_*.py`, excluding `__init__.py`. This includes browser smoke checks and audit scripts.
6. Pass `patched` to `tests/audit_log_clear.py` to enable its persistence and rollback assertions.

The unittest, pytest, JavaScript and standalone test steps use `if: ${{ !cancelled() }}` so later test groups still run after earlier failures unless the job is cancelled. File loops accumulate failures and return a nonzero exit code after processing the remaining files.

Installing pytest fixes the two module imports but does not make unittest execute their pytest-style functions. The separate pytest step follows unittest and precedes JavaScript; see [diagnosis and validation limits](120-pytest-module-imports.md).

## Coverage limitations

The workflow is configured to cover the existing test categories; successful execution has not yet been confirmed. Browser fixtures and smoke scripts do not imply full live-server end-to-end coverage. The connection-lifetime audit runs unittest discovery again, so some tests are intentionally repeated. Future helper files under `tests/` may require refining standalone discovery rather than treating helpers as executable checks.

## Local test runner - 2026-11-06

The root [runlocaltests.sh](../../runlocaltests.sh) adapts the supplied Looking Glass runner to Scrying Glass. Invoke it with Bash; executable file mode is not required. It uses a disposable detached local clone of committed HEAD, excluding accumulated local-tests-* and ci-results-* evidence from the working tree. Uncommitted changes are not tested. The original checkout and tracked Admin script marker are not overwritten; relevant test commands use tools/run_split_tests.py.

```bash
bash runlocaltests.sh --no-publish
bash runlocaltests.sh --suite javascript --python .venv/bin/python --no-publish
bash runlocaltests.sh
```

Groups are syntax, python (unittest, including browser fixtures), pytest (the two configured modules), javascript and standalone. all runs those five groups; browser aliases standalone and is not a browser-only filter. There are no separate live or recovery groups. No Looking Glass workspace helper or container dependency is introduced.

Install requirements.txt plus httpx, playwright and pytest, Node and Playwright Chromium before running. The script does not install dependencies. SG_LOCAL_TEST_TMPDIR selects the scratch parent, default /tmp. Later groups continue after test-command failures. Each run records environment metadata, command logs and exit codes, script inventories and summary.tsv under local-tests-<short-hash>/run-<UTC>-<unique>/. Pytest also writes JUnit XML. Exit codes do not certify that tests ran without skips. Browser fixtures are not authenticated live-server verification.

Publication is enabled by default; use --no-publish to prevent staging, committing and pushing. Completed failed-test runs are eligible for publication so diagnostics can be reviewed. Setup failures and interruptions are not published automatically. Publication requires the original checkout to remain on features/perplexity at the tested HEAD with no staged changes. Only the run directory is staged and committed; the result commit message includes [skip ci], then HEAD is pushed to origin features/perplexity. Publication status is logged outside the committed run directory and affects the process exit separately from exit-code.txt. Interrupted scratch is retained; completed scratch is removed. Logs can contain application diagnostics and local paths: review sensitive output before choosing publication.

Validation during script preparation: bash -n and --help execution passed for the supplied adapted file. The complete suites, clone lifecycle, failure paths and Git publication were not executed. These remain pending local validation; no passing suite or end-to-end result is claimed. The user explicitly requested [skip ci] for this delivery; no workflow configuration change or separate dispatch is included, and workflow-run state is not inferred from the marker. README and the handover/TODO indexes were reviewed and remain unchanged because their existing descriptions, links and task statuses are unaffected. The Admin redesign task is unrelated and remains proposed.
