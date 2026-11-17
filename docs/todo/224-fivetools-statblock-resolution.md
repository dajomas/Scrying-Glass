# 224 - SG-TODO-022.04: ordered 5e.tools inheritance and reference resolution

[Back to TODO index](../../TODO.md) · [Controlling parent](220-admin-statblock-viewer.md) · [Handover](../handover/080-monster-lookup-diagnostics.md)

## Current status - 2026-11-17

022.04 remains in progress, not a usable production adapter. Accepted 022.01-
022.03/lifecycle and 016/017 stay closed. No merge, deployment or release.
The [original a-f requirements](https://github.com/dajomas/Scrying-Glass/blob/dcd55b68210948e1f142ba6c377cdab25e7f384e/docs/todo/224-fivetools-statblock-resolution.md)
and [prior pins, semantics, evidence and b.1/b.2 history](https://github.com/dajomas/Scrying-Glass/blob/ca5cdd94c267395fcada8fe21249ef17acc1bdcc/docs/todo/224-fivetools-statblock-resolution.md)
remain required/retained by reference. The parent's final approved contract and
limits override dated pending notes; consolidation cancels no unfinished gate.
SG-TODO-023 is separate. No existing test/assertion is removed or relaxed.

<a id="04b-delivery-increments---2026-11-17"></a>
## 04b increments

- 022.04b.1: delivered 485a4532d61c4ce729e8584f45e1becb0841b9b4; full-key/
  provenance/path/depth/work content-byte cache ledger, focused 12-test evidence.
- 022.04b.2: delivered ca5cdd94c267395fcada8fe21249ef17acc1bdcc; strict limits,
  intermediate-growth preflight, changed-limit invalidation and atomic cache
  publication; focused 11-test evidence. Neither delivery is covering CI.
- 022.04b.3: isolated worker implemented, focused validation passed; push/CI and
  broader regression/acceptance review pending. Do not mark whole 04b completed.

## b.3 worker contract and operations

`python/scrying_glass_fivetools_worker.py` exposes internal blocking
`resolve_isolated(selected, records, deadline=..., limits=..., worker_memory_bytes=...)`.
Use one immutable tuple of exact Identity/bytes pairs for one dataset generation;
duplicates remain visible to ambiguity checks. Caller supplies the original finite
absolute monotonic acceptance deadline, including elapsed queue/fetch time. Invoke
outside the event loop and DB lock; the global scheduler/provider gates remain
parent-integration obligations, not features of this synchronous helper.

Supported enforcement: Linux plus executable /usr/bin/prlimit or /bin/prlimit
(util-linux). The launcher sets RLIMIT_AS and RLIMIT_FSIZE before Python starts,
plus bounded CPU seconds and disabled core dumps. The child verifies inherited
limits and observes refusal of a cap-sized anonymous mapping before reading source
data. No unverified/unsupported platform runs preparation in-process instead.
Default worker_memory_bytes is the approved 268435456; configured positive integer
values are accepted. Address-space accounting includes interpreter/mappings and is
stricter than RSS, NOT a server-wide memory cap or malicious-code sandbox.

Fresh -I Python, fixed entry point, no shell/pickle/source code execution. Exact
bytes travel through anonymous temporary files, with each transport file bounded
by worker_memory_bytes; transport overflow is an explicit error, not truncation or
snapshot-size validation. This is an additional internal transport allowance, not
a guarantee that every payload fitting it fits Python's decoded memory. Parsing,
indexing and graph resolution run inside the limited process. Parent-side trusted
metadata staging/result decoding and existing dataset storage are not a total
server-memory ceiling. Process startup/resource exits are sanitized errors.

The supervisor checks the same deadline/cancellation before staging, while waiting
and before returning results; it kills the session process group and reaps the
child on exit/error/cancellation. Late output is discarded. No child/cache survives
a call; no provider fallback, saved snapshot, tracker field or DB write occurs.

## Evidence and remaining gates

Thirteen tests passed on Linux/Python 3.12.8, including a repeat with ResourceWarning
as error: actual subprocess graph/in-process content, ordering and provenance
comparison, duplicate/missing/cycle/mode diagnostics, source/intermediate limits,
real 128 MiB allocation rejected under a 64 MiB worker cap, successful next job,
noncooperative infinite-loop deadline kill, in-flight cancellation and waitpid
confirmation of reaping. Fail-closed platform/launcher/unverified-child cases,
invalid/expired work, start failure and UTF-8 transport equality/overflow also ran.
Tests use synthetic records. Modified temporary core copies simulate blocked and
memory-hungry workers; ordinary comparison uses the hash-verified unchanged core.

`python -m unittest discover -s tests -p 'test_fivetools_worker.py' -v`:
13 tests OK, no skips/failures/errors here. On unsupported hosts real Linux tests
are explicitly skipped; that is not evidence of supported memory enforcement.
Existing 22 graph, 12 cache and 11 bounds modules are unchanged, not rerun here.
Full provider/application regression, Python 3.14, covering CI and formal 04b
acceptance remain outstanding. Existing test_*.py workflow discovery includes
this module when CI runs; no workflow edits or manual dispatch.

04a matrix/schema-lock/safe-expression/oracle gates remain open. Runtime pin
32ef600fab87a585a61dd1a22e9b02dfc58c728a remains in the unchanged graph module;
exact schema lock relation is unverified. 04c/d modifications/substitutions,
04e supporting references/normalization/private adapter and 04f compatibility,
adversarial, persistence and normalized-size evidence remain required. Nonempty
mods still fail at 04c; source byte limits are not normalized snapshot/node limits.
Workers must later encompass conversion/validation too, not just inheritance.
All intermediate 04 pushes include [skip ci] until the last 04 code push.
Delivery, focused checks, covering CI and acceptance remain distinct.
