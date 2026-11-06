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
- Dependencies: `requirements-test.txt`, including runtime requirements plus `httpx2>=2.0.0`, `playwright` and `pytest`.
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

The workflow is configured to cover the existing test categories; this section is not evidence that a particular commit passed. Browser fixtures and smoke scripts do not imply full live-server end-to-end coverage. The connection-lifetime audit runs unittest discovery again, so some tests are intentionally repeated. Future helper files under `tests/` may require refining standalone discovery rather than treating helpers as executable checks. Historical covering results are recorded in the relevant feature handover sections.

## Local test runner - 2026-11-06

The root [runlocaltests.sh](../../runlocaltests.sh) adapts the supplied Looking Glass runner to Scrying Glass. Invoke it with Bash; executable file mode is not required. It uses a disposable detached local clone of committed HEAD, excluding accumulated local-tests-* and ci-results-* evidence from the working tree. Uncommitted changes are not tested. The original checkout and tracked Admin script marker are not overwritten; relevant test commands use tools/run_split_tests.py.

```bash
bash runlocaltests.sh --no-publish
bash runlocaltests.sh --suite javascript --python .venv/bin/python --no-publish
bash runlocaltests.sh
```

Groups are syntax, python (unittest, including browser fixtures), pytest (the two configured modules), javascript and standalone. all runs those five groups; browser aliases standalone and is not a browser-only filter. There are no separate live or recovery groups. No Looking Glass workspace helper or container dependency is introduced.

Install requirements-test.txt using Python 3.11+ (CI uses 3.14), Node and Playwright Chromium before running. The script does not install dependencies. SG_LOCAL_TEST_TMPDIR selects the scratch parent, default /tmp. Later groups continue after test-command failures. Each run records environment metadata, command logs and exit codes, script inventories and summary.tsv under local-tests-<short-hash>/run-<UTC>-<unique>/. Pytest also writes JUnit XML. Exit codes do not certify that tests ran without skips. Browser fixtures are not authenticated live-server verification.

Publication is enabled by default; use --no-publish to prevent staging, committing and pushing. Completed failed-test runs are eligible for publication so diagnostics can be reviewed. Setup failures and interruptions are not published automatically. Publication requires the original checkout to remain on features/perplexity at the tested HEAD with no staged changes. Only the run directory is staged and committed; the result commit message includes [skip ci], then HEAD is pushed to origin features/perplexity. Publication status is logged outside the committed run directory and affects the process exit separately from exit-code.txt. Interrupted scratch is retained; completed scratch is removed. Logs can contain application diagnostics and local paths: review sensitive output before choosing publication.

Validation during script preparation: bash -n and --help execution passed for the supplied adapted file. The complete suites, clone lifecycle, failure paths and Git publication were not executed. These remain pending local validation; no passing suite or end-to-end result is claimed. The user explicitly requested [skip ci] for that delivery; no workflow configuration change or separate dispatch was included.

## HTTPX2 test migration - 2026-11-06

The inspected test tree uses FastAPI TestClient only in tests/test_admin_split_runtime.py. That fixture now uses unittest.IsolatedAsyncioTestCase and httpx2.AsyncClient with ASGITransport directly. This avoids requiring a particular Starlette TestClient HTTPX import implementation, installing legacy httpx for that fixture, or using process-wide import aliases. Async client cleanup is registered after adapter cleanup registration so the client closes before its backing temporary files are removed.

GET, HEAD, conditional ETag, byte range, CSS delegation, missing/traversal responses, refresh, unchanged mtime, mount wiring and script inclusion assertions are retained. New assertions check actual HTTPX2 client/response types. Requests remain in-process static-adapter fixtures, without authenticated server startup or lifespan verification, as before. No runtime HTTP client or application behaviour is changed.

Local and CI installation now share requirements-test.txt. Runtime requirements.txt and Python 3.10 runtime support are unchanged; the HTTPX2 test environment requires Python 3.11+. The local runner already accepts --python and invokes unittest discovery, so it needs no code change. Use the interpreter from the environment where test requirements were installed:

```bash
python -m pip install -r requirements-test.txt
python -m playwright install --with-deps chromium
bash runlocaltests.sh --python "$(command -v python)" --no-publish
```

Preparation consisted of live source/dependency review and checking the proposed changes against existing assertions; no migrated test, clean-environment installation, syntax execution or full suite was run. The user requested [skip ci] for this migration. The workflow installation and cache inputs are updated for future runs, not disabled; no separate workflow is dispatched. Validation remains pending as recorded in [SG-TODO-010](../todo/100-httpx2-test-migration.md). README and HANDOVER.md retain accurate runtime descriptions and index links and remain unchanged. No workflow-run outcome or test success is claimed.

## Local results review and layout-test correction - 2026-11-06

Evidence commit 72923ec4e34a6a1065332495015a0a768fe7a98f publishes run local-tests-e7b229c/run-20261106T103855Z-QWqmWA for source e7b229caa04494ec5a2b4fed7a0d66301359a12e, not the evidence commit itself. Environment metadata records Python 3.14.7, Node 22.23.2 and WSL2. summary.tsv reports successful syntax/import, pytest and all 37 JavaScript commands, with failures in unittest and standalone script 2 (audit_connection_lifetime.py). Pytest output reports 43 passed. completed=1 means processing completed, not tests passed; exit-code.txt is 1.

The main unittest excerpt explicitly shows all three migrated HTTPX2 fixture methods passing. The full log was truncated by the connector before its final failure summary; this review cannot assert that its only failures match the audit. The complete connection audit reports 1,022 tests, two failed name-layout subtests at 768/375 viewport widths for inactive Crawling Claw, and 673 opened connections with zero without explicit close. The two measured widths are 137.265625 versus computed minimum 137.281 CSS px. This evidence supports a subpixel comparison problem rather than an HTTPX2 failure or connection leak.

The correction is confined to tests/test_monster_name_layout.py: allow at most 1/32 CSS px (0.03125px) of numerical slack in the minimum-width assertion, require finite measurements and positive minimum, and keep all nowrap, single-line, vertical-order, text, 11-button, page-error and mutation checks unchanged. Production CSS, the 16ch minimum and browser interactions are untouched. Seven numeric guard tests accept the observed values, exact/wider values and the boundary, while rejecting just-beyond-boundary and real deficits, nonfinite values and a zero minimum. The standalone audit needs no patch because it reruns this corrected unittest.

Preparation executed those seven exact helper/guard definitions in isolation with unittest: seven tests passed, zero failures/errors. This did not import the full browser module or run Playwright; the corrected page fixture, assembled suite, audit and covering CI remain pending. The current request did not repeat [skip ci], so the corrective commit omits the marker and normal push-triggered CI is expected; no run outcome is claimed in advance. Follow-up requirements and HTTPX2 partial success are tracked in [SG-TODO-010](../todo/100-httpx2-test-migration.md). The historical SG-TODO-007 feature acceptance remains unchanged because production layout is not modified. README, HANDOVER.md and TODO.md indexes remain accurate and unchanged.
