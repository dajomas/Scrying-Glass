# 070 - Display-connection fixture repair

[Back to handover index](../../HANDOVER.md)

Last updated: 2026-11-01.

## Scope and root cause

This change repairs `tests/test_display_connection.py`; production endpoints, authorization, heartbeat behavior, assets and workflow configuration remain unchanged. README was reviewed and needs no application-facing change. TODO.md is absent and no backlog is created.

The fixture AST-extracts `ClientAPI.ws` into an execution scope without `__name__` or `__package__`. The handler's relative campaign-viewer import emits an ImportWarning and raises `KeyError: "'__name__' not in globals"` before the initial snapshot. Production error handling logs and cleans up, leaving empty message lists. This is a fixture setup defect, not evidence that heartbeat or authorization rules need weakening.

## Repair and safeguards

- Give the extracted handler a module name and `__package__='python'`.
- Supply a scoped campaign-viewer module fixture returning viewer state; restore any previous module afterward.
- Use one context-owned real asyncio operation lock instead of a new lock for every lookup.
- Keep raw context state distinct from viewer-projected state.
- Fail tests immediately on unexpected handler exception logs, rather than hiding setup errors behind later message assertions.
- Retain all 11 original test methods and assertions unchanged.
- Add seven checks: projected initial state; fresh projection on resync; both locks held during projection; session revocation before resync; disallowed role rejection; projection-error logging and cleanup; and restoration of an existing module after fixture patching.

The viewer service is mocked to isolate protocol tests from campaign storage. This does not test real campaign grants/filtering; dedicated viewer tests remain necessary.

## Local validation

Baseline: `d9f4b54bb8d80d5f6435491b6d074752803896de`; original test Git blob `a3f57967c544549bfb5abdbe950f9660546f1e26`.

A focused local tree used a copy of the pinned production WebSocket method as the AST-extraction input, not a full application checkout. Original: 11 tests, 8 failures and 1 error, with the captured import failure visible. Candidate: all 18 tests passed on Python 3.12.8. Runs treating ImportWarning, ResourceWarning and DeprecationWarning as errors also passed. AST comparison confirmed all original test methods were unchanged.

```bash
python -m unittest discover -s tests -p 'test_display_connection.py' -v
python -Werror::ImportWarning -m unittest discover -s tests -p 'test_display_connection.py' -v
python -Werror::ResourceWarning -m unittest discover -s tests -p 'test_display_connection.py' -v
python -Werror::DeprecationWarning -m unittest discover -s tests -p 'test_display_connection.py' -v
```

## Outstanding verification

Full-suite CI, Python 3.14, real FastAPI/Starlette transport and real campaign ACL integration have not been rerun for this repair. Normal CI must verify the delivered commit. No full-suite failure-count reduction or passing CI result is claimed in advance. Other failure categories and Admin source splitting are outside this change.
