# 224 - SG-TODO-022.04: ordered 5e.tools inheritance and reference resolution

[Back to TODO index](../../TODO.md) · [Parent contract](220-admin-statblock-viewer.md) · [Handover](../handover/080-monster-lookup-diagnostics.md)

## Current status - 2026-11-17

Overall 04/022 remains in progress, not a usable provider/viewer feature. Accepted
022.01-022.03/lifecycle, bounded 04b and 016/017 remain closed for their documented
scopes. [Original a-f requirements](https://github.com/dajomas/Scrying-Glass/blob/dcd55b68210948e1f142ba6c377cdab25e7f384e/docs/todo/224-fivetools-statblock-resolution.md)
and [complete prior status, pins, contracts, tests and close-out](https://github.com/dajomas/Scrying-Glass/blob/333183af118d68e5f71c18de7a3b89c3cc2516cc/docs/todo/224-fivetools-statblock-resolution.md)
remain required/retained by reference. This delivery-size consolidation removes
no unfinished requirement or historical evidence. The parent's approved contract
and limits override dated pending notes. No merge/deployment/release.

<a id="04b-delivery-increments---2026-11-17"></a>
<a id="04b-user-directed-implementation-close-out---2026-11-17"></a>
## Retained 04b disposition

04b.1 485a4532d61c4ce729e8584f45e1becb0841b9b4; 04b.2
ca5cdd94c267395fcada8fe21249ef17acc1bdcc; 04b.3
d85c04a5b6f80f324d2998a3be9baa1be8bea69e. Implementation acceptance/close-out
3cb3f7568558c88e562725fde6ee1fe8df815579 retains incomplete verification under
04f.V1-V4: combined graph/cache/bounds/worker run (58 methods, not 58 combined
passes), relevant provider/application/criterion regressions, covering Python 3.14
CI at the final 04 code push, and evidence/corrections plus later conversion/
validation inside the worker. Those obligations are not waived or marked passed.

<a id="04c-split-and-first-component---2026-11-17"></a>
## 04c plan

- 04c.1: delivered 333183af118d68e5f71c18de7a3b89c3cc2516cc; pure literal
  appendStr/setProp/prefixSuffixStringProp executor, 12 focused tests and 17 limited
  operation-level upstream comparisons. No graph/worker integration was delivered.
- 04c.2: in progress under the three-commit delivery proposal below.
- 04c.3: pending c.2; appendIfNotExistsArr/insertArr/replaceArr/replaceOrAppendArr/
  removeArr/renameArr, selector/no-match/duplicate behavior and expansion checks.
- 04c.4: pending c.3 and applicable 04a contracts; scalarAddProp/scalarMultProp and
  restricted calculateProp, numeric-string/sign/rounding/adversarial evidence.
- 04c.5: pending prior items and safe-regex contract; replaceTxt/replaceName,
  deliberate supported JS regex/tag behavior and combined compatibility/oracles.
04a matrix/schema-lock/formula/regex work, 04d creature/substitution work, 04e
references/normalization/private adapter and 04f validation remain required.

## 04c.2 staged delivery - 2026-11-17

The user requested implementing/pushing 04c.2. Full-file approval size motivates
a three-commit proposal, not a claim of an observed GitHub connector failure:

1. 04c.2a: executor remove shorthand, appendArr/prependArr, focused tests and
   documentation. Implementation included here; focused checks passed, CI and
   formal acceptance pending. Graph/worker behavior remains unchanged.
2. 04c.2b: after a, an explicit ordered-graph entry point and compiler/template
   grouping integration, local-to-selected/dependency diagnostic wrapping, correct
   cached logical work without double charging, and actual graph fixtures. Preserve
   legacy entry-point compatibility and existing unique assertions. Not delivered
   by a; implementation and its own complete push approval remain necessary.
3. 04c.2c: after b, isolated-worker entry integration, actual end-to-end tests,
   failure/cleanup/limit checks and status evidence. Not delivered by a.

Each commit includes its tests/docs and requires separate bound approval. Approval
of the first payload agrees to this delivery split and authorizes only that write.
Original 04c.2 scope remains required; do not call it complete after a or b, and
do not require another generic implement/proceed/push instruction between stages.

### 04c.2a semantics and evidence

String remove deletes a dictionary property, including through existing lists,
without pruning empty parents. Missing object paths are no-ops. Pinned unscoped
_ removal targets the literal root key null; wildcard removal expands the fixed
13 entry properties. Direct array-slot deletion is rejected explicitly rather
than splicing or inventing sparse holes. appendArr/prependArr wrap scalar/object/
null items as single elements, preserve list ordering, and handle missing/falsey
existing values. Truthy non-array coercions, malformed/missing items, unsafe paths
and dynamic substitutions remain explicit errors/deferred constructs. Full JS
coercion and numeric-key enumeration compatibility remain unestablished.

Concatenation size is projected before allocating the combined list; per-operation
compact UTF-8 preflight, cancellation checks, independent payloads/results and
logical instruction budgets remain. These are not a hard CPU/memory ceiling; the
executor must be connected inside the supported limited worker in later stages.
No SG live-field, normalization, persistence or existing lookup behavior changes.

Python 3.12.8: `python -m unittest discover -s tests -p
 'test_fivetools_modifications*.py' -v` ran 21 native component tests, all OK,
no skips/errors/failures. All original c.1 assertions remain: only the two deferred
fixture mode names changed from newly supported appendArr/remove to still-deferred
replaceArr/removeArr. Nine new methods cover deletion semantics, scalar/null items,
falsey/empty targets, order-sensitive compositions, isolation, UTF-8 equality/
overflow, instruction limits and explicit failure cases. No unique coverage removed.

Forty-one additional controlled operation-level comparisons match content and root
property order in Node 20.20.1 using unmodified pinned utils.js, blob
80c10d0439a5179b7d7f6e1220b9efb535a626d2, SHA-256
67c28c64fa7cc98139923d7cfdbe4faa6807b6583a54451962a988567de1a172, from commit
32ef600fab87a585a61dd1a22e9b02dfc58c728a, plus the previously identified captured
Parser slice. These are synthetic bounded comparisons, not full getCopy, graph,
worker, schema or live-provider evidence. No full suite/3.14/CI claim. Existing
workflow discovery includes the new test file when run; no workflow edit/dispatch.
README/root indexes remain accurate for active behavior and stable indexed paths.
All intermediate 04 commits retain [skip ci] until the final 04 code push.
