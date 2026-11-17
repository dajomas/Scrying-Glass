# 080 - Monster lookup diagnostics repair

[Back to handover index](../../HANDOVER.md)

[Complete preceding handover](https://github.com/dajomas/Scrying-Glass/blob/97369c5a551c59af24313cf6e022795c096b1278/docs/handover/080-monster-lookup-diagnostics.md)
retains diagnostics/graph/worker failures, pins, evidence, operational limits and
accepted close-outs. No unfinished requirement or evidence limit is waived.

<a id="02204ab-core-graph-preparation---2026-11-17"></a>
<a id="02204b1-cache-content-accounting---2026-11-17"></a>
<a id="02204b2-resource-boundaries---2026-11-17"></a>
<a id="02204b3-isolated-worker---2026-11-17"></a>
<a id="04b-user-directed-implementation-close-out---2026-11-17"></a>
<a id="02204c1-standalone-operation-kernel---2026-11-17"></a>

## 04c.2c ordered worker - 2026-11-17

Baseline 97369c5a551c59af24313cf6e022795c096b1278. [224 contract and remaining
gates](../todo/224-fivetools-statblock-resolution.md) records the dedicated ordered
worker entry, unchanged legacy entry, fixed validated mode selection and rejection
of downgraded success frames. Both use the existing enforced Linux process
boundary and original deadline/cancellation/cleanup semantics. No new public API,
scheduler, provider fetch or persistence path.

Ten real-process/boundary tests passed on Linux/Python 3.12.8, ResourceWarning as
error, no skips/errors/failures. They compare actual ordered process results with
the direct graph and exercise diagnostics, budgets, real memory refusal/recovery,
blocked execution kill, cancellation and reaping, unsupported/expired work and
fail-closed enforcement/mode checks. Faults use temporary modified ordered-hook
copies; ordinary comparisons execute the actual production modules. Earlier
suites are unchanged, not rerun; no fresh oracle/full-provider/3.14/CI claim.

04c.2 a/b/c implementation stages are represented by this delivery, not formal
fully validated closure or complete 04c/provider support. Remaining requirements
and 04f.V1-V4 persist. Accepted 04b/earlier lifecycle/016/017 stay closed; overall
04/022 stays open. README/root indexes/workflow unchanged for stable behavior/
paths. Intermediate 04 [skip ci] rule remains; no dispatch, merge or deployment.
