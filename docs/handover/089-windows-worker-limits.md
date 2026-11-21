# 089 - Statblock preparation workers on Windows (Job Object limits)

[Back to handover index](../../HANDOVER.md) · [Correction round 1](088-statblock-correction-round-1.md) · [TODO 220](../todo/220-admin-statblock-viewer.md)

Date: 2026-11-20. Baseline `c055cf1` on `features/claude-statblock`. Requested by the user
after the open-items review: preparation needed Linux `prlimit`, so on Windows every
statblock preparation (Find statblock, automatic loading, collection on Add Monster, the
Add Monster preview) failed with `worker_enforcement_unavailable`.

## Delivered

- `python/scrying_glass_worker_windows.py` (imported only on Windows): the worker is
  started normally (no console window, own process group) and assigned at once to a new
  Job Object (ctypes, no new dependency) with
  - `ProcessMemoryLimit` = the worker memory limit (Linux: RLIMIT_AS);
  - `PerProcessUserTimeLimit` = the seconds left before the job's deadline (Linux: RLIMIT_CPU);
  - `ActiveProcessLimit` = 1 (the worker cannot start processes);
  - `KILL_ON_JOB_CLOSE` (also when the server exits) and `DIE_ON_UNHANDLED_EXCEPTION`.

  Before reading any input the child waits at most 5 s until its innermost job carries
  exactly these limits and then proves the memory cap by failing a cap-sized allocation;
  otherwise it reports `worker_enforcement_unavailable`, as on Linux. A job that cannot be
  created, configured or assigned is never run (the process is killed). Windows has no
  per-process file-size limit (Linux: RLIMIT_FSIZE); the workers write no files.
- Windows pipes do not work with `select`: `ThreadChannel` gives the parent the same
  non-blocking interface as the Linux selector channel (`PosixChannel`, unchanged
  behaviour) with one reader and one writer thread, the same deadline, cancellation and
  size checks.
- `scrying_glass_fivetools_worker.py`: `_launcher()` returns a Job Object marker on
  Windows; the shared `_start_worker` starts the fixed entry point with prlimit (Linux) or
  the Job Object (Windows); `_memory_guard` and `_kill_and_reap` gain the Windows branch.
  The 5e.tools preparation and source (Open5e, D&D Beyond, `.monster`) workers use
  `_start_worker` and `open_channel`. Other platforms still fail closed.
- Technical documentation: preparation limits per platform and the three Add Monster
  statblock routes of handover 088.

## Validation

- Linux (real prlimit, nothing skipped): `test_fivetools_worker` 13, `test_fivetools_ordered_worker`
  10, `test_fivetools_preparation_worker` 5, `test_statblock_import_workers` 5,
  `test_statblock_source_adapters` 16 pass, unchanged.
- `tests/test_worker_windows.py`: structure layout (144 bytes on 64-bit), limit values,
  `launch` and `guard_child` against a fake kernel32 (fail-closed cases, waiting for the
  assignment, an unenforced cap), platform selection, and the real 5e.tools and source
  workers with the Windows `ThreadChannel` (a `.monster` file, a D&D Beyond fetch round
  trip, a 5e.tools preparation identical to the in-process result, an adapter error): 9
  pass on Linux. Two Windows-only tests: a real worker in a real job; a 192 MiB
  allocation refused under a 128 MiB cap.
- **Windows, user-run 2026-11-20 22:14 CET** (the user's Windows machine, 64-bit Python
  3.15, checkout `D:\GIT\Scrying-Glass`): all 11 tests of `test_worker_windows` pass,
  including both Windows-only tests. Run from the `tests` folder with the repository root
  and `tests` on `PYTHONPATH` (as CI does):
  `$env:PYTHONPATH = "<repo>;<repo>\tests"` then `python -m unittest test_worker_windows -v`.
  The exact commit of that checkout was not reported; it contained this change (`dc56c5d`).
- CI: run 44817232724 attempt 1 for `dc56c5d` **succeeded**: 2283 main-suite tests OK,
  pytest 43 passed; the Linux worker tests ran with real prlimit and 9 of the 11 Windows
  worker tests ran (the 2 Windows-only tests are skipped on Linux). Evidence
  `ci-results-44817232724-attempt-1`, publication `1fc7c2a`.

## Follow-up - workers started from the virtual environment (2026-11-20)

With the server running through `run.bat` on Windows, every preparation (Find statblock,
the Add Monster preview) failed with only "Preparation failed.". `run.bat` runs the server
with the venv's `python.exe`, which on Windows is a launcher that starts the real
interpreter as a second process; the Job Object allows one process, so the worker could
not start. The Windows test run above used the system Python directly and did not hit
this (diagnosis by reasoning; not reproduced by Claude on Windows).

- `_worker_python()` (`scrying_glass_fivetools_worker.py`): on Windows the worker uses
  `sys._base_executable` when it is a different, existing file (the base interpreter
  behind the venv launcher). The workers import only the standard library and this
  project, so the venv's packages are not needed. Linux is unchanged.
- Worker failure codes now have messages (`worker_start_failed`,
  `worker_resource_or_start_failure`, `worker_protocol_error`, ...); an unknown code shows
  as "Preparation failed (<code>)."; a preparation that fails without any code is logged
  with its traceback in the server console.
- Tests: `_worker_python` choices (Windows venv, missing base, Linux) on every platform;
  a Windows-only test that starts a worker from a fresh virtual environment's
  `python.exe`.
- **User-run 2026-11-20**: with the venv's `python.exe` (as `run.bat` uses), all 13 tests
  of `test_worker_windows` pass on Windows, including the new virtual-environment test.
  With the server started by `run.bat`, Find statblock and the Show statblock preview in
  Add Monster work on Windows; a short regression check with `run.sh` on Linux (WSL2 on
  the same machine) also works. (A first WSL2 start reported port 3000 in use just after
  the Windows server stopped; it started normally a few seconds later.)
- CI: run 44821132281 attempt 1 for `9503255` **succeeded**: 2285 main-suite tests OK,
  pytest 43 passed. Evidence `ci-results-44821132281-attempt-1`, publication `b3c0155`.

## Limitations

- On Windows the user checked Find statblock and the Add Monster preview with the real
  server; automatic loading for the viewer and the collection after an add were not
  checked separately (they use the same workers).
- Resource isolation only, as on Linux: not a filesystem or network sandbox.
