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
  pass on Linux. Two Windows-only tests (a real worker in a real job; a 192 MiB
  allocation refused under a 128 MiB cap) are skipped here: **not yet run on Windows.**
  Run them on the Windows machine from the `tests` folder with
  `python -m unittest test_worker_windows`.

## Limitations

- Not verified on Windows by Claude; the real Job Object behaviour needs the Windows test
  run above. Until then, treat Windows preparation as unverified.
- Resource isolation only, as on Linux: not a filesystem or network sandbox.
