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

## Outstanding evidence

The full suite, real FastAPI/Starlette transport, real campaign-viewer ACL integration and Python 3.14 have not been rerun locally. CI must verify the committed repair. No passing CI result or reduction in the full-suite failure count is claimed here. Display-connection and other failing modules are outside this repair.
