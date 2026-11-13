# 020 - CI workflow and test coverage

[Back to handover index](../../HANDOVER.md)

## Trigger and skip behavior

Workflow: `Branch tests`, defined in [tests.yml](../../.github/workflows/tests.yml).

- Trigger: pushes to `features/perplexity` only.
- No path filter: changes to documentation also match the push trigger, but the standing project instruction requires every documentation-only commit to contain `[skip ci]`.
- GitHub's native push-workflow skip behavior honors `[skip ci]` in commit messages. No custom skip job is used.
- Every documentation-only commit must always include `[skip ci]` in its proposed, approved and actual commit message. No separate user skip request is needed. Do not modify or separately dispatch workflows to bypass that skip.
- Mixed commits containing code, scripts, tests, templates, styles, runtime configuration, dependencies or workflow changes are not documentation-only; normal CI applies unless the user explicitly requests otherwise.
- No pull-request, scheduled or manual-dispatch trigger is configured.

Example documentation commit message:

```text
docs: update indexed handover [skip ci]
```

This is a standing authoring rule, not a newly added enforcement mechanism. See [root instructions, section 5](../../PERPLEXITY_INSTRUCTIONS.md#5-ci-execution-and-documentation-only-commits). Historical dated skip/run notes below describe their original deliveries.

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
5. Execute standalone Python files under `tests/` whose names do not match `test_*.py`, excluding `__init__.py`. Since SG-TODO-020 these are the connection audit and the shared browser fixture helper; the browser smoke check and the activity-log/round-three audits are unittest modules ([600](600-test-suite-cleanup.md)).
6. The `patched` argument special case for `tests/audit_log_clear.py` is unused since that script became `tests/test_activity_log_clear.py`.

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

Publication is enabled by default; use --no-publish to prevent staging, committing and pushing. Completed failed-test runs are eligible for publication so diagnostics can be reviewed. Setup failures and interruptions are not published automatically. Publication requires the original checkout to remain on features/perplexity at the tested HEAD with no staged changes. Only the run directory is staged and committed; the result commit message includes [skip ci], then HEAD is pushed to origin features/perplexity. Publication status is logged temporarily outside the committed run directory: the current publication log is removed only after a successful push and retained when publication fails. Log-removal failure after a successful push is reported on stderr and makes the overall process exit nonzero; it does not rewrite already-pushed test evidence. Publication/late cleanup status affects process exit separately from exit-code.txt. Interrupted scratch is retained; completed scratch is removed. Logs can contain application diagnostics and local paths: review sensitive output before choosing publication.

Historical preparation: bash -n and --help execution passed for the supplied adapted file. The complete suites, clone lifecycle, failure paths and Git publication were not executed during preparation. Subsequent successful local evidence is recorded below; unexercised failure paths are not claimed validated. The user explicitly requested [skip ci] for the original runner delivery; no workflow configuration change or separate dispatch was included.

## HTTPX2 test migration - 2026-11-06

The inspected test tree uses FastAPI TestClient only in tests/test_admin_split_runtime.py. That fixture now uses unittest.IsolatedAsyncioTestCase and httpx2.AsyncClient with ASGITransport directly. This avoids requiring a particular Starlette TestClient HTTPX import implementation, installing legacy httpx for that fixture, or using process-wide import aliases. Async client cleanup is registered after adapter cleanup registration so the client closes before its backing temporary files are removed.

GET, HEAD, conditional ETag, byte range, CSS delegation, missing/traversal responses, refresh, unchanged mtime, mount wiring and script inclusion assertions are retained. New assertions check actual HTTPX2 client/response types. Requests remain in-process static-adapter fixtures, without authenticated server startup or lifespan verification, as before. No runtime HTTP client or application behaviour is changed.

Local and CI installation now share requirements-test.txt. Runtime requirements.txt and Python 3.10 runtime support are unchanged; the HTTPX2 test environment requires Python 3.11+. The local runner already accepts --python and invokes unittest discovery, so it needs no code change. Use the interpreter from the environment where test requirements were installed:

```bash
python -m pip install -r requirements-test.txt
python -m playwright install --with-deps chromium
bash runlocaltests.sh --python "$(command -v python)" --no-publish
```

On Rocky Linux 10, the user reported that --with-deps failed because the Ubuntu fallback installer invoked absent apt-get. Installing with python -m playwright install chromium instead and then launching a headless test page succeeded in the user's environment. This is an observed working fallback, not official Rocky support or universal dependency coverage; install missing native libraries through the host distribution when needed.

Historical migration preparation consisted of live source/dependency review and checking proposed changes against existing assertions; no migrated test, clean-environment installation, syntax execution or full suite was run at that stage. The original migration push included [skip ci]. Its pending-validation status is superseded by the verified local/CI results and closure below.

## Local results review and layout-test correction - 2026-11-06

Evidence commit 72923ec4e34a6a1065332495015a0a768fe7a98f publishes run local-tests-e7b229c/run-20261106T103855Z-QWqmWA for source e7b229caa04494ec5a2b4fed7a0d66301359a12e, not the evidence commit itself. Environment metadata records Python 3.14.7, Node 22.23.2 and WSL2. summary.tsv reports successful syntax/import, pytest and all 37 JavaScript commands, with failures in unittest and standalone script 2 (audit_connection_lifetime.py). Pytest output reports 43 passed. completed=1 means processing completed, not tests passed; exit-code.txt is 1.

The main unittest excerpt explicitly shows all three migrated HTTPX2 fixture methods passing. The full log was truncated by the connector before its final failure summary; this review cannot assert that its only failures match the audit. The complete connection audit reports 1,022 tests, two failed name-layout subtests at 768/375 viewport widths for inactive Crawling Claw, and 673 opened connections with zero without explicit close. The two measured widths are 137.265625 versus computed minimum 137.281 CSS px. This evidence supports a subpixel comparison problem rather than an HTTPX2 failure or connection leak.

The correction is confined to tests/test_monster_name_layout.py: allow at most 1/32 CSS px (0.03125px) of numerical slack in the minimum-width assertion, require finite measurements and positive minimum, and keep all nowrap, single-line, vertical-order, text, 11-button, page-error and mutation checks unchanged. Production CSS, the 16ch minimum and browser interactions are untouched. Seven numeric guard tests accept the observed values, exact/wider values and the boundary, while rejecting just-beyond-boundary and real deficits, nonfinite values and a zero minimum. The standalone audit needs no patch because it reruns this corrected unittest.

Preparation executed those seven exact helper/guard definitions in isolation with unittest: seven tests passed, zero failures/errors. This did not import the full browser module or run Playwright. The corrective commit df16cc0ee798a07b5c219c3db06de54c913cb84f omitted [skip ci] so normal push-triggered CI could run. Subsequent fixture/suite validation is recorded below. The historical SG-TODO-007 feature acceptance is unchanged because production layout was not modified.

## Verified local/CI success and SG-TODO-010 close-out - 2026-11-06

The user requested completion after review of both successful evidence sets. [SG-TODO-010](../todo/100-httpx2-test-migration.md) is completed for the delivered HTTPX2 test migration and setup scope. Migration commit: 11835d414d701f0fc6a3a701def29594cab287a3. Exact validated corrective source: df16cc0ee798a07b5c219c3db06de54c913cb84f.

Local evidence commit f584f4394cf155e37d7f8214f7da0afc78d89542 contains local-tests-df16cc0/run-20261106T105201Z-HwuKfD. Every command in summary.tsv returns zero and exit-code.txt is 0. The connection audit reports 1,029 tests, OK, 673 opened connections and zero without explicit close. The reviewed local summary covers syntax/import, unittest, pytest, 37 JavaScript scripts and six standalone checks. Expected mocked provider exception tracebacks appear in the successful audit output; they are not failed tests.

CI run 42205835274, attempt 1, Branch tests, tests exact source df16cc0ee798a07b5c219c3db06de54c913cb84f. Evidence is committed at 715ad2d6e22f88e8708e2cf9e3ae49069f9aa495 under ci-results-42205835274-attempt-1. Reviewed run.json records workflow and tests job completed/success; dependency installation, syntax/import, Python/browser suite, pytest, JavaScript and standalone browser/audit steps all report success.

The reader index maps workflow.log to reader-chunks/file-000007. Part 5 records installation from requirements-test.txt and Python 3.14.10/Node 22.23.4. Part 10 records successful installation including httpx2 2.16.0, httpcore2 2.16.0, playwright 1.64.1, pytest 9.2.0, FastAPI 0.162.0 and Starlette 1.10.0. The installation log is not a complete environment inventory proving absence of every legacy package; closure accepts direct HTTPX2 fixture use without declaring or explicitly installing legacy httpx, not an environment-purity guarantee.

This review verifies local command results, the complete local audit summary, CI workflow/job/step metadata and selected installation logs, not every individual CI assertion. Fixtures do not establish authenticated deployed-server behaviour or a Python-version compatibility matrix. The SQLite connection count is separate from HTTPX2 client-resource cleanup. No such broader claims are part of completion.

This close-out updates TODO.md, the existing task and this handover only. README and HANDOVER.md were reviewed and remain accurate and unchanged; no application, test or workflow code changes, new test execution or separate workflow dispatch are included. The user explicitly requested [skip ci] for this documentation push; its workflow-run state is not inferred from the marker. SG-TODO-009 remains independently proposed.

## Publication-log cleanup - 2026-11-06

The user requested removal of the per-run local-tests-<hash>/publication-run-<UTC>-<unique>.log after evidence is pushed, and explicitly requested [skip ci] for this update. The actual runner filename is runlocaltests.sh. This change removes only the current quoted publication_log path, after publish_results returns success from its commit/push sequence. There is no glob sweep, old-log deletion, evidence-directory deletion or change to branch/index/HEAD publication guards.

A completed run with failed tests still removes its publication log if the evidence push succeeds; its test/process exit remains nonzero. Failed/refused publication retains the log and evidence. --no-publish creates no publication log. If removal fails after a successful push, the runner reports that failure on stderr and returns a nonzero process exit; the already-committed exit-code.txt remains the test/scratch result, not a retrospective publication/late-cleanup result. The normal published-commit stdout message is retained.

New tests/test_local_runner_publication.py exercises the actual runner with real temporary Git repositories and a local bare origin; only the syntax test commands are stubbed. All Git commits/pushes in these fixtures are local filesystem operations, not GitHub publication. Cases cover successful publication cleanup, failed-test evidence successfully pushed, remote hook rejection, --no-publish, staged-change refusal and simulated rm failure after a successful push. Assertions also preserve an unrelated older publication log and verify that only the run directory is committed. Existing unittest discovery includes these six tests without workflow edits.

Executed preparation: verified the reconstructed original runner against live blob d2d76a2a4d8503a7790109faa2e4327089507099 before patching; bash -n and --help passed on the exact updated runner; Python AST parsing passed for the new test module; all six regression tests passed with zero failures/errors/skips. As a negative control, the exact original runner failed the three cleanup-specific checks as expected, with no test errors. Updated runner is 9,483 UTF-8 bytes; test module is 7,359 bytes, below 20,000.

This is publication-lifecycle validation, not execution of the application suites, authenticated server behaviour or a real GitHub push by the runner. Existing historical suite evidence above is unchanged. README, HANDOVER.md and TODO.md were reviewed and left unchanged because this independent runner maintenance change does not alter application behaviour, indexed links or SG-TODO-009.2's pending CI state. No new backlog item is created.

The approved delivery is intended to include [skip ci]; no workflow configuration is changed and no separate workflow is dispatched. Do not infer a checked workflow-run state from the marker. This skip request applies to this update, not subsequent implementation pushes.

## Standing documentation-only skip policy - 2026-11-06

The user instructed that documentation-only commits always contain `[skip ci]`. The active rules above and [root instructions section 5](../../PERPLEXITY_INSTRUCTIONS.md#5-ci-execution-and-documentation-only-commits) now require that marker in proposed, approved and actual messages without a separate request. Mixed executable/configuration/test/workflow changes are not documentation-only. No workflow or enforcement code changes are included. Historical delivery records remain unchanged rather than retroactively altering their skip decisions.

This policy update changes only the root instructions and existing CI/maintenance handover guidance. README, HANDOVER.md and TODO.md were reviewed and remain accurate and unchanged; SG-TODO-009.1/009.2 closure and later proposed stages are unaffected. No automated tests were executed for this documentation-only update, no separate workflow is dispatched, and no run-state claim is inferred from the marker.
