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
- Dependencies: `requirements.txt`, plus `httpx` and `playwright`.
- Browser: Playwright Chromium, installed with operating-system dependencies.
- Repository and tests directories are included in `PYTHONPATH`.
- Workflow token permission: `contents: read`.
- Job timeout: 30 minutes.

This is one selected CI environment, not a compatibility matrix. Dependency specifications are not a lockfile.

## Checks configured

1. Compile Python source and tests, then import `scrying_glass_server`.
2. Run `python -m unittest discover -s tests -p 'test_*.py' -v`, including unittest-based browser fixtures.
3. Find every `.js` and `.cjs` file under `tests/` and run each with `node --test`.
4. Execute standalone Python files under `tests/` whose names do not match `test_*.py`, excluding `__init__.py`. This includes browser smoke checks and audit scripts.
5. Pass `patched` to `tests/audit_log_clear.py` to enable its persistence and rollback assertions.

The Python, JavaScript and standalone test steps use `if: ${{ !cancelled() }}` so later test groups still run after earlier failures unless the job is cancelled. File loops accumulate failures and return a nonzero exit code after processing the remaining files.

## Coverage limitations

The workflow is configured to cover the existing test categories; successful execution has not yet been confirmed. Browser fixtures and smoke scripts do not imply full live-server end-to-end coverage. The connection-lifetime audit runs unittest discovery again, so some tests are intentionally repeated. Future helper files under `tests/` may require refining standalone discovery rather than treating helpers as executable checks.
