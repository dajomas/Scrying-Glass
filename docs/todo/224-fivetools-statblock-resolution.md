# 224 - SG-TODO-022.04: ordered inheritance and reference resolution

[TODO index](../../TODO.md) · [Parent contract](220-admin-statblock-viewer.md) · [Handover](../handover/080-monster-lookup-diagnostics.md)

## Status - 2026-11-17

04/022 stays open. Accepted 022.01-022.03/lifecycle, bounded 04b and 016/017 stay
closed. [Original a-f requirements](https://github.com/dajomas/Scrying-Glass/blob/dcd55b68210948e1f142ba6c377cdab25e7f384e/docs/todo/224-fivetools-statblock-resolution.md)
and [complete preceding contracts, pins, limitations and evidence](https://github.com/dajomas/Scrying-Glass/blob/ab9cf3dbea6ce67f7b1e1cdcb664affe43a7945a/docs/todo/224-fivetools-statblock-resolution.md)
remain required/controlling by reference. Consolidation waives no unfinished gate.

## Stage A delivery - 2026-11-17

All remaining 04 subunits (04c.3b recorded at 1e78d75; 04c.3c/d, 04c.4, 04c.5,
04a contract, 04d, 04e, 04f) are implemented in the Stage A archive delivery;
details, decisions and evidence in
[handover 082](../handover/082-fivetools-statblock-stage-a.md). Status:
implementation delivered, validation pending CI (Stage A uses `[skip ci]`) and
user acceptance. Not marked completed.

| Unit | Status |
|---|---|
| 04a pinned contract | delivered; every runtime mode executes, oracle-verified |
| 04b graph/isolation | accepted earlier; 04f.V1-V4 obligations below |
| 04c.3a-d arrays, 04c.4 numeric/formulas, 04c.5 regex/text | delivered, oracle-verified |
| 04d creature modes, templates, substitutions | delivered, oracle-verified |
| 04e reference collection and normalization | delivered except 04e.2 |
| 04e.2 generated magic-item variants and item enhancement | **moved to [SG-TODO-033](330-fivetools-variants.md)** by the user 2026-11-20 (not required to close SG-TODO-022); variants delivered there 2026-11-22 ([730](../handover/730-fivetools-magic-item-variants.md)), item enhancement split off as [SG-TODO-034](340-fivetools-item-enhancement.md); before that: `magicvariants.json` specific/generic variants are not generated; references to them are explicit `reference_unavailable` partial warnings (55 of 4,683 real monsters) |
| 04f integration evidence | local evidence recorded in 082; CI (Python 3.14) and acceptance pending |

Acceptance for 04e.2: generated variants match the pinned
`Renderer.item._createSpecificVariants` output for every referenced item
(oracle comparison), item text includes the runtime's property/type entries,
and the partial count drops accordingly. Proposed new limit `dataset_files`
(64) awaits user agreement.

<a id="04b-delivery-increments---2026-11-17"></a>
<a id="04b-user-directed-implementation-close-out---2026-11-17"></a>
04b closure 3cb3f7568558c88e562725fde6ee1fe8df815579 retains 04f.V1-V4: combined
58-method foundation verification (not combined passes), broader regression/
criterion review, final Python 3.14 CI and integrated resource/normalized-output
evidence/corrections. No tests are waived by that implementation acceptance.

<a id="04c-split-and-first-component---2026-11-17"></a>
<a id="04c2-staged-delivery---2026-11-17"></a>
04c.1 333183af118d68e5f71c18de7a3b89c3cc2516cc and 04c.2a/b/c
6a30b8d00b838071878647375f749397de45c1ce / 97369c5a551c59af24313cf6e022795c096b1278 /
ab9cf3dbea6ce67f7b1e1cdcb664affe43a7945a are delivered implementations, not formal
fully validated whole-04c acceptance. Existing ordered graph and limited worker
consume the declared kernel subset; legacy foundation APIs remain compatible.

## 04c.3 split - 2026-11-17

User requested splitting 04c.3 and implementing/pushing the first item. Each
delivery includes focused tests/docs and its own exact-payload push confirmation.

1. 04c.3a: appendIfNotExistsArr and checked JSON equality. Implementation included
   here; 12 focused tests and bounded upstream comparisons passed, CI/formal
   acceptance pending. Gate: original-array membership semantics, preserved order/
   duplicates, independent values, typed equality and resource/error checks.
2. 04c.3b: pending a; insertArr with pinned index handling, absent/empty targets,
   ordered insertion, malformed values and expansion/boundary evidence.
3. 04c.3c: pending b and applicable 04a safety contracts; replaceArr and
   replaceOrAppendArr, verified name/index/regex selectors, missing/no-match/
   duplicate behavior, safe regex restrictions and order-sensitive fixtures.
4. 04c.3d: pending c; removeArr/renameArr, verified selectors/no-match/duplicates
   and combined array/compiler/graph/worker/resource regressions.

### First-item semantics and evidence

The pinned runtime filters new items only against the pre-operation existing
array, not against earlier accepted items: [1] + [1,2,2] becomes [1,2,2]. Existing
duplicates also remain. Objects compare by keys/values independent of key order;
arrays compare in order; booleans differ from numbers, strings differ from numbers,
and Object.is signed-zero distinctions are preserved for represented floats.
Scalar/object/null items wrap once. Missing/falsey/empty targets keep incoming
duplicates. Later instructions compare against earlier instructions' results.

The comparison helper checks cancellation/work callbacks during traversal. Input
and candidate JSON trees are validated for the declared comparison domain; unsafe
integers outside +/-9007199254740991 and hasOwnProperty-shadowing object keys
fail explicitly, as do non-finite numbers, rather than silently rounding or
approximating upstream coercions. Those conservative unsupported boundaries and
pre-existing coercive/sparse/dynamic limitations remain open compatibility work,
not proof that every valid upstream construct is handled. General numeric/regex
contracts remain 04a/04c.4/04c.5 obligations. No broad numeric serialization claim.

Projected retained additions are checked before allocating a combined array;
matching duplicate payloads are not wrongly counted as added creature content.
Logical instructions include no-ops and fixed wildcards once. Source bytes are
not normalized snapshot/node limits. The existing graph/worker already calls this
kernel and uses the same bounds module; no new worker dependency file is needed.
OrderedResolver ADAPTER_VERSION is bumped to 04c.3a-1. Recreate resolver/worker
instances after code changes; do not hot-reuse conversion caches across adapters.

Python 3.12.8: `python -m unittest discover -s tests -p 'test_fivetools_append_if_absent.py' -v`
ran 12 actual component tests, all OK, no skips/errors/failures. They cover the
above semantics, nested/wildcard paths, isolation, byte equality/one-over, no-op
operation budgets, malformed/dynamic/unsupported cases and cancellation. Existing
test files are unchanged and were not rerun here. No fresh graph/worker end-to-end,
full provider/application suite, Python 3.14 or covering CI result is claimed.

Ninety-six additional controlled Node 20.20.1 comparisons match normalized JSON
structure and root property order against unmodified recovered utils.js from
32ef600fab87a585a61dd1a22e9b02dfc58c728a: blob
80c10d0439a5179b7d7f6e1220b9efb535a626d2; SHA-256
67c28c64fa7cc98139923d7cfdbe4faa6807b6583a54451962a988567de1a172, with the prior
captured Parser slice. The inspected source includes CollectionUtil.deepEquals.
These are synthetic operation-level comparisons over the supported domain, not
full getCopy/schema/worker/provider or byte-for-byte numeric serialization proof.

04c.3b-d, 04c.4 numeric/formulas, 04c.5 regex/tag compatibility, 04a contracts,
04d creature/substitutions, 04e reference BFS/normalization/private preparation
and 04f validation remain required. No tracker/SG live-field, persistence,
permission or active-provider change. README/root indexes/workflow remain
unchanged for stable active behavior and paths. Intermediate 04 [skip ci] remains
required until the last code push; no dispatch, merge or deployment.
