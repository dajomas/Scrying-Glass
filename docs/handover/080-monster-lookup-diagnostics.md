# 080 - Monster lookup diagnostics repair

[Back to handover index](../../HANDOVER.md)

## Retained history

[Complete preceding handover](https://github.com/dajomas/Scrying-Glass/blob/6a30b8d00b838071878647375f749397de45c1ce/docs/handover/080-monster-lookup-diagnostics.md)
retains the diagnostics repair, failures/corrections, pins and graph/cache/bounds/
worker/component evidence, accepted close-outs and operational limitations.
Consolidation is for delivery size, not deletion of unfinished obligations.

<a id="02204ab-core-graph-preparation---2026-11-17"></a>
<a id="02204b1-cache-content-accounting---2026-11-17"></a>
<a id="02204b2-resource-boundaries---2026-11-17"></a>
<a id="02204b3-isolated-worker---2026-11-17"></a>
<a id="04b-user-directed-implementation-close-out---2026-11-17"></a>
<a id="02204c1-standalone-operation-kernel---2026-11-17"></a>

Accepted 022.01-022.03/lifecycle, bounded 04b and 016/017 remain closed; deferred
04f.V1-V4 obligations remain required. Overall 04/022 and 04c.2 remain open.

## 04c.2b ordered graph - 2026-11-17

Baseline 6a30b8d00b838071878647375f749397de45c1ce. [224 status and contract](../todo/224-fivetools-statblock-resolution.md)
records new OrderedResolver and the compatible Resolver execution seam, compiler
origin tagging, merged template/selected ordering and contextual diagnostics.
Core raw/cached graph work remains charged once; per-call results stay independent
and failed resolution publishes no new success entries. The ordered entry carries
ADAPTER_VERSION and is private, not a new public preparation/apply endpoint.

Ten native graph/compiler/executor tests passed on Python 3.12.8, no skips/errors/
failures. Synthetic datasets exercise real modules, including merged template
error index/origin/path, cache budget equality/overflow, repeated templates, base
modifications and isolation/growth failures. Existing suites are unchanged, not
rerun here; no fresh oracle, full provider, 3.14 or CI validation is claimed.

The worker is unchanged and still uses Resolver, so ordered isolated execution
remains 04c.2c, with end-to-end and resource/cleanup evidence. Other 04c/04a/d-f
gates remain as documented; no complete adapter/normalization or hard in-process
memory guarantee. README/root indexes/workflow reviewed/reused and unchanged for
active behavior/paths. [skip ci] until final 04 code push; no dispatch, merge,
deployment or release.
