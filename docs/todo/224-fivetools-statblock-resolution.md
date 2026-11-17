# 224 - SG-TODO-022.04: ordered inheritance and reference resolution

[TODO index](../../TODO.md) · [Parent contract](220-admin-statblock-viewer.md) · [Handover](../handover/080-monster-lookup-diagnostics.md)

## Current status - 2026-11-17

Overall 04/022 stays open. Accepted 022.01-022.03/lifecycle, bounded 04b and 016/017
stay closed. [Original a-f requirements](https://github.com/dajomas/Scrying-Glass/blob/dcd55b68210948e1f142ba6c377cdab25e7f384e/docs/todo/224-fivetools-statblock-resolution.md)
and [complete preceding contracts, pins, evidence and delivery plan](https://github.com/dajomas/Scrying-Glass/blob/6a30b8d00b838071878647375f749397de45c1ce/docs/todo/224-fivetools-statblock-resolution.md)
remain controlling/required by reference. This delivery-size consolidation waives
no unfinished requirement or evidence limit. No merge/deployment/release.

<a id="04b-delivery-increments---2026-11-17"></a>
<a id="04b-user-directed-implementation-close-out---2026-11-17"></a>
04b implementation closure 3cb3f7568558c88e562725fde6ee1fe8df815579 retains
04f.V1-V4: combined 58-method graph/cache/bounds/worker verification (not combined
passes), broader regressions/criterion review, final Python 3.14 covering CI, and
later integrated resource/normalized-output evidence plus required corrections.

<a id="04c-split-and-first-component---2026-11-17"></a>
<a id="04c2-staged-delivery---2026-11-17"></a>
## 04c delivery

04c.1 delivered 333183af118d68e5f71c18de7a3b89c3cc2516cc; 04c.2a delivered
6a30b8d00b838071878647375f749397de45c1ce. The approved a/b/c delivery split
remains: a executor, b ordered graph, c isolated worker, each with its own exact
push approval. No generic implement/proceed/push repetition is required.

04c.2b implementation is included here, focused validation passed; CI/formal
acceptance pending. New OrderedResolver explicitly composes the actual graph,
compiler and six-mode executor. Resolver remains the compatible foundation entry
point and still rejects nonempty mods. A narrow protected execution hook avoids
changing that contract or weakening old pending-mode assertions. Compiler-created
instructions carry their active selected/base or resolved-template origin chain.
Local executor errors become graph Diagnostic values with original selected
identity, originating chain, merged per-property operation index and source path;
template execution paths use $/apply/_mod. This is logical resolved-entity origin,
not a claim of per-leaf attribution to an inherited template's original raw blob.

Base modifications execute before selected inheritance; selected/template groups
merge per property before _/* tail execution. Core counts all raw instructions/
null removals across the graph and cached logical work; the executor validates
its local list without charging it again. Immutable result/provenance caching and
failure publication rules remain. ADAPTER_VERSION identifies the ordered entry;
instances/caches stay bound to one immutable configured dataset generation.

Ten native tests passed on Python 3.12.8 using
`python -m unittest discover -s tests -p 'test_fivetools_ordered_resolution.py' -v`.
They run actual compiler/graph/executor code, synthetic exact-source datasets:
legacy compatibility, all six supported modes, recursive bases/provenance, repeated
template grouping and tail order, exact/cached operation budgets, template/base
error context, wildcard identity, dynamic rejection, isolation and growth failure
without publication. Existing test files are unchanged, not rerun for this stage.
No fresh upstream oracle, isolated-worker, full-provider/application/3.14/CI result
is claimed. Earlier 12/21 component and 17/41 operation-level comparison evidence
remains historical in the linked records, not new graph-oracle evidence.

04c.2c remains required: integrate the explicit ordered entry in the limited
worker, actual end-to-end/failure/cleanup/resource tests and evidence. Existing
worker still invokes Resolver; it does NOT yet execute modifications. Neither
pure interpreter is a production preparation endpoint or a hard process-memory
boundary. Do not close 04c.2 after b.

04c.3 array selectors, 04c.4 numeric/restricted formulas, 04c.5 deliberate safe JS
regex/tag compatibility, 04a matrix/schema-lock/expression contracts, 04d creature/
substitutions, 04e reference BFS/normalization/private adapter and 04f integration/
normalized-size evidence all remain required. Six supported operations do not
mean every upstream mode/coercion is supported; unsafe/coercive/dynamic constructs
retain explicit errors. No existing lookup, SG live fields, persistence or source
selection changes. Source JSON bounds are not normalized snapshot/node limits.
README/root indexes/workflow remain unchanged for stable behavior and indexed
paths. Intermediate 04 [skip ci] remains required; no workflow edit/dispatch.
