# 660 - Plain message when the ports are already in use

[Back to HANDOVER index](../../HANDOVER.md)

User request, 2026-11-14, delivered on `features/perplexity` (no TODO ID assigned). User instruction: "I got this message when starting Scrying Glass when Scrying Glass was already running on the same ports. Can you make the message more user friendly and not look like a Python error".

## Cause

`scrying_glass_server.py` started both uvicorn servers without checking the ports. When a port was taken, uvicorn logged `[Errno 98] ... address already in use` for each server and exited with `SystemExit(3)` inside an asyncio task, which printed a long traceback.

## Change

- New `python/scrying_glass_port_check.py`: `port_problems()` tries to open each port on the bind address and returns the ports that cannot be opened (in use, permission needed, or address not on this machine); `port_message()` turns them into a short text.
- `scrying_glass_server.py` runs the check right after the command-line options are applied, before the database is opened, and exits with status 1 and this message:

```
Scrying Glass cannot start on 0.0.0.0:
  - port 3002 (Admin) is already in use
  - port 4002 (Client Display) is already in use
Scrying Glass (or another program) may already be running. Stop it first, or choose other ports with --admin-port and --client-port or network.admin_port/client_port in the config file.
```

- Limit: if another program takes a port in the moment between the check and the server start, the old uvicorn output can still appear.

## Validation (local, this sandbox)

- Started one instance, then a second on the same ports: the second printed the message above (both ports), exited with status 1 and created no storage directory. With only the Admin port taken, only that port was listed.
- Through `tools/run_split_tests.py`: new `tests/test_port_check.py` (3 tests) with `test_launcher_python310`, `test_launcher_runtime_82860c4` and `test_admin_split_runtime`: 18 tests OK.
- User run and acceptance pending.

## Acceptance

- The user tested and accepted the port-in-use message (`93ffbd0e`) on 2026-11-14. The earlier "User run and acceptance pending" note is superseded.
- CI: run 43636503802 on `93ffbd0e` failed only on the unrelated flaky `test_edit_rejects_a_tampered_token` (fixed in `b157aef8`); the later runs on `features/perplexity` that include this change (43637464939, 43638272866, 43639327765) concluded success.
- Status: completed and closed.
