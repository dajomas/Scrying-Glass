# 060 - WebSocket regression fixture repair

[Back to handover index](../../HANDOVER.md)

Last updated: 2026-11-01.

## Scope and root cause

This change repairs `tests/test_bughunt_711881a.py` only; no production endpoint, authorization, heartbeat, database or workflow behavior is changed. README was reviewed and needs no application-facing change. TODO.md is absent; this change does not create a backlog.

The fixture AST-extracts `ClientAPI.ws` into a synthetic module named `regression_ws`. The production method now imports `.scrying_glass_campaign_viewers` while sending its first snapshot. The synthetic scope had no `__package__`, so that relative import raised `ImportError: attempted relative import with no known parent package`. The production handler caught and logged it, then cleaned up without sending a snapshot. The fixture's later empty-message assertions obscured the actual setup failure.

## Repair

- Give the extracted scope `__package__='python'`.
- Supply a scoped campaign-viewer module fixture through `patch.dict(sys.modules, ...)`; its service returns the projected snapshot used by protocol tests.
- Keep the real extracted WebSocket method and all existing assertions unchanged.
- Add five tests covering viewer-projected initial state, disallowed roles, cross-origin rejection, allowed admin roles, and logging/cleanup when projection fails.
- Keep raw context state distinct from viewer state so the projection test detects an accidental bypass.

The module fixture is limited to these protocol unit tests. It does not replace or claim coverage of real campaign grants/filtering, and it is restored after each run. Dedicated viewer/authorization tests remain necessary.

## Local validation

Source baseline: `8d3fdf5f27a924d81aee561383c4ed7984c15954`. The original test file matched Git blob `7a776b77dcd4835021787e9cbd5eed4fc5f7189d`.

A local focused tree used the pinned production WebSocket method and FeatureStorage class, copied as AST-extraction inputs, not the full application checkout. The unchanged original test module reproduced 30 tests with 11 failures and 2 errors. Exposing the captured logger exception confirmed the relative-import failure.

After the fixture repair: 35 tests passed (19 WebSocket tests and 16 real in-memory SQLite snapshot-ID tests) on Python 3.12.8. Repeated runs with ResourceWarning and DeprecationWarning treated as errors also passed. AST comparison confirmed existing test methods remained unchanged; the generated malformed-message tests and entire snapshot-test section are unchanged.

Commands:

```bash
python -m unittest discover -s tests -p 'test_bughunt_711881a.py' -v
python -Werror::ResourceWarning -m unittest discover -s tests -p 'test_bughunt_711881a.py'
python -Werror::DeprecationWarning -m unittest discover -s tests -p 'test_bughunt_711881a.py'
```

## CI confirmation and remaining scope

Run `41297160008`, attempt 1, tested commit `aefa5457fcfa84bf918890660ab2f782901a1679`. All 35 tests in this module passed in the Python 3.14.9 CI environment. The full Python suite ran 866 tests with 24 failures and 8 errors, compared with 861 tests, 35 failures and 10 errors before this repair. The five additional tests and reduction of 11 failures and 2 errors match this module's change.

Evidence was inspected under `ci-results-41297160008-attempt-1/` at commit `d9f4b54bb8d80d5f6435491b6d074752803896de`.

This confirms the focused fixture repair, not the full suite or real transport/campaign ACL behavior. The overall workflow still failed. Display-connection and other failing modules remain separate repairs; see [current validation status](030-validation-and-next-steps.md).
