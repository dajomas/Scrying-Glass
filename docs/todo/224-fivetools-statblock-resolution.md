# 224 - SG-TODO-022.04: ordered inheritance and reference resolution

[TODO index](../../TODO.md) · [Parent contract](220-admin-statblock-viewer.md) · [Handover](../handover/080-monster-lookup-diagnostics.md)

## Status - 2026-11-17

04/022 remains open; accepted 022.01-022.03/lifecycle, bounded 04b and 016/017
remain closed. [Original a-f requirements](https://github.com/dajomas/Scrying-Glass/blob/dcd55b68210948e1f142ba6c377cdab25e7f384e/docs/todo/224-fivetools-statblock-resolution.md)
and [complete preceding contracts, pins and evidence](https://github.com/dajomas/Scrying-Glass/blob/97369c5a551c59af24313cf6e022795c096b1278/docs/todo/224-fivetools-statblock-resolution.md)
remain controlling/required by reference. Consolidation waives no unfinished gate.

<a id="04b-delivery-increments---2026-11-17"></a>
<a id="04b-user-directed-implementation-close-out---2026-11-17"></a>
04b closure 3cb3f7568558c88e562725fde6ee1fe8df815579 retains 04f.V1-V4:
combined 58-method foundation verification (not combined passes), broader
regression/criterion review, final Python 3.14 covering CI and integrated resource/
normalized-output evidence/corrections. These obligations remain outstanding.

<a id="04c-split-and-first-component---2026-11-17"></a>
<a id="04c2-staged-delivery---2026-11-17"></a>
## 04c.2 implementation delivery

04c.1 333183af118d68e5f71c18de7a3b89c3cc2516cc; 04c.2a executor
6a30b8d00b838071878647375f749397de45c1ce; 04c.2b ordered graph
97369c5a551c59af24313cf6e022795c096b1278. 04c.2c is included in this delivery:
all three planned implementation stages are now represented, with focused
validation; combined regressions, covering CI and formal acceptance remain pending.
This is not complete 04c, full 5e.tools compatibility or a usable import endpoint.

New private blocking resolve_ordered_isolated selects OrderedResolver through a
fixed server-controlled boolean in the internal transport header. The child
validates that flag, never imports a source-supplied module/callable, and echoes
the mode on success; the parent rejects mismatched/missing success-mode metadata.
Existing resolve_isolated keeps the foundation Resolver behavior. Both share
the original limits, original absolute deadline, temporary-file byte allowance,
Linux/prlimit enforcement, process-group termination/reaping and late-result
rejection. No in-process fallback. Caller still supplies bounded exact records
and invokes outside event loop/DB locks; global scheduling/provider gates and
normalization/validation/private preparation endpoints remain later parent work.

Ten native tests passed on Linux/Python 3.12.8 with ResourceWarning as error:
`python -W error::ResourceWarning -m unittest discover -s tests -p 'test_fivetools_ordered_worker.py' -v`.
No skips/errors/failures here. They exercise real ordered subprocesses against
the direct graph for all six modes and ordering/provenance, legacy compatibility,
template diagnostic transport, resource/dynamic rejection, independent jobs,
actual 128 MiB allocation refusal under a 64 MiB cap, recovery, noncooperative
loop deadline kill, in-flight cancellation and waitpid reaping verification, plus
unsupported/expired, unverified-enforcement and mode-downgrade fail-closed cases.
Faults use modified temporary copies at the ordered execution hook, not production
test hooks. Records are synthetic; this is not browser/provider HTTP evidence.

Existing tests are unchanged, not rerun here. No fresh oracle, full suite, Python
3.14 or covering CI claim. Linux-specific tests skip explicitly elsewhere; skips
are not enforcement proof. Prior runtime/schema/oracle limitations and coercive/
sparse-array/dynamic unsupported constructs remain as recorded in linked history.
04c.3 array selectors, 04c.4 numeric/restricted formulas, 04c.5 deliberate regex/
tag compatibility, 04a contracts, 04d creature/substitutions, 04e reference BFS/
normalization and 04f integration/normalized-size gates remain required. Source
JSON limits are not normalized snapshot/node/text limits. No tracker/SG live-field,
persistence, permission or existing-provider change. README/root indexes/workflow
remain unchanged for stable active behavior and paths. [skip ci] on intermediate
04 pushes until final code push; no workflow edit/dispatch, merge or deployment.
