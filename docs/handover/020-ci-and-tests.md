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

## Automatic evidence publisher deployment - 2026-11-07

This publisher-only change is prepared on `features/add_workflow`, based on main
commit `c52e2714dcc6b92ad5d64caa527a5554479dc792`, for the user to merge into `main`
manually. No unrelated feature-branch application changes are included.

[Publish CI results](../../.github/workflows/publish-ci-results.yml) listens for
completed `Branch tests` push runs on `features/perplexity` and
`features/perplexity-018`, including unsuccessful conclusions. GitHub requires
the workflow file on the default branch; it is not operational merely because
this deployment branch contains it. The test workflow is unchanged by this patch;
the working branch's own tests.yml determines whether it triggers Branch tests.

The publisher executes trusted [collector code](../../tools/publish_ci_results.sh)
and the existing chunk helper from main, checks out the tested branch separately,
and uses the runtime-provided GITHUB_TOKEN with actions: read and contents: write.
It collects exact-attempt metadata/jobs/logs and run-scoped artifacts, records
warnings for unavailable logs/artifacts, and builds/verifies lossless reader
chunks. Artifact provenance must be checked: artifacts are not attempt-specific.
Downloaded evidence is never executed, and credential values are not committed.

Evidence goes to ci-results-RUN_ID-attempt-ATTEMPT on the tested branch. Older
tracked root evidence directories are replaced but retained in Git history.
Newer runs/later attempts are not replaced by older completions. Publication is
serialized per branch and retries non-force pushes while preserving remote
changes. Only selected evidence paths are staged. Evidence commits use [skip ci].
The Actions summary records tested and publication SHAs; failed publication
uploads available evidence as a fallback Actions artifact. Branch protection
may still prevent a direct publication push.

Automatic publication removes manual sensitive-data review. Keep sensitive
information out of logs and test artifacts. getworkflow.sh remains unchanged
as a manual fallback.

Validation is pending: no local or live publisher execution is claimed. After
the manual merge, observe a subsequent eligible test completion and verify its
evidence commit, tested SHA/attempt, logs and reader chunks. Exercise failed-test,
rerun and concurrent-publication behavior before treating the feature as
validated. The deployment-branch push does not itself match Branch tests branch
filters; no workflow is separately dispatched. README, HANDOVER index and TODO
index were reviewed and remain unchanged: application behavior/task statuses
and handover links are unaffected.
