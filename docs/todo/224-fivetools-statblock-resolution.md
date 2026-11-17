# 224 - SG-TODO-022.04: ordered 5e.tools inheritance and reference resolution

[Back to TODO index](../../TODO.md) · [Controlling parent](220-admin-statblock-viewer.md) · [Handover](../handover/080-monster-lookup-diagnostics.md)

## Current status - 2026-11-17

022.04 remains in progress, not a usable production adapter. Accepted 022.01-
022.03/lifecycle and 016/017 stay closed. Bounded 04b implementation is accepted
and closed by user direction; verification remains incomplete as explicitly
recorded below. No merge, deployment, release or overall 022/04 closure.
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
- 022.04b.3: delivered d85c04a5b6f80f324d2998a3be9baa1be8bea69e; isolated
  worker implementation with focused 13-test evidence. All three increments are
  included in the user-directed bounded implementation close-out below; deferred
  verification is not relabelled as completed validation.

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
13 tests OK, no skips/failures/errors at its preparation checkpoint. On unsupported
hosts real Linux tests are explicitly skipped; that is not evidence of supported
memory enforcement. Existing 22 graph, 12 cache and 11 bounds modules were not
rerun for b.3. No new tests are executed by this documentation reconciliation.
Combined/provider/application regression, Python 3.14 and covering CI remain
outstanding under the explicit disposition below. Existing test_*.py workflow
discovery includes these modules when CI runs; no workflow edits/manual dispatch.

04a matrix/schema-lock/safe-expression/oracle gates remain open. Runtime pin
32ef600fab87a585a61dd1a22e9b02dfc58c728a remains in the unchanged graph module;
exact schema lock relation is unverified. 04c/d modifications/substitutions,
04e supporting references/normalization/private adapter and 04f compatibility,
adversarial, persistence and normalized-size evidence remain required. Nonempty
mods still fail at 04c; source byte limits are not normalized snapshot/node limits.
Workers must later encompass conversion/validation too, not just inheritance.
All intermediate 04 pushes include [skip ci] until the last 04 code push.
Delivery, focused checks, covering CI and acceptance remain distinct.

## 04b user-directed implementation close-out - 2026-11-17

At 08:47 CET, after the remaining-validation checklist was disclosed, the user
requested: "Reconcile status and close 04b". Status: accepted/closed for the
delivered bounded implementation scope, including b.1-b.3, with explicit deferral
of the unexecuted verification below to 04f/parent 04 integration validation. This
is a user-directed implementation acceptance, NOT a finding that all original
validation criteria have passed or that 04b is fully validated. No additional
planned 04b implementation increment or repeat acceptance request is created.
Later-discovered defects still require correction; test requirements are not waived.

| Scope | Delivered basis and bounded disposition |
|---|---|
| Exact identity, recursive base/template graph, root/null/preservation semantics, active-path cycle detection, snapshot/cache isolation | Initial core d13a439e28ed0829d2285831e01dab16170776a7; historical 22 synthetic native tests and seven limited upstream comparisons. Implementation accepted; these are not a combined current-head result or full oracle coverage. |
| Provenance-inclusive cache accounting, LRU/TTL and byte boundaries | b.1 485a4532d61c4ce729e8584f45e1becb0841b9b4; 12 focused native tests at preparation. Accepted implementation, integration verification retained below. |
| Input/limit validation, growth preflight, changed-limit revalidation and atomic publication | b.2 ca5cdd94c267395fcada8fe21249ef17acc1bdcc; 11 focused native tests at preparation. Accepted implementation, not proof of every possible resource scenario. |
| Isolated worker, Linux enforced limits, deadline/cancellation and process cleanup | b.3 d85c04a5b6f80f324d2998a3be9baa1be8bea69e; 13 focused tests including real process/kernel cases. Accepted within documented Linux/enforcement limits, not certification of other platforms or a production scheduler. |

### Deferred verification retained under 04f/parent 04

- 04f.V1 - pending: execute/review the four graph/cache/bounds/worker modules
  together against an identified integrated revision (22+12+11+13 = 58 test
  methods currently declared; this is an inventory, NOT 58 combined passes).
- 04f.V2 - pending: relevant existing-provider/application regressions and
  criterion-based review against the original graph/isolation/resource contract;
  resolve any exposed defect or uncovered required case before overall 04 closure.
- 04f.V3 - deferred until final 04 code push: covering Python 3.14 CI and review
  of actual results/run/revision identities. Retain [skip ci] on intermediate
  pushes; do not dispatch CI separately or infer a result from configuration.
- 04f.V4 - pending: record that evidence and failure/correction history, integrate
  later modifications/references/conversion/validation inside the resource boundary
  and complete overall 04 acceptance. Source intermediates are not normalized
  snapshot/node/text/reference measurements.

Only bounded 04b implementation is closed. Overall 04 and 022 stay open; 04a/c-f
and unrelated accepted scopes are unchanged. Root TODO now reflects already
accepted 022.03/Stages 1-3 and the actual 04b deliveries, rather than stale planned
wording. README, HANDOVER index, parent design contract and workflow need no
behavior/path/configuration edits for this status-only change. No production,
test, dependency, permission, schema or CI configuration changes. Documentation
only [skip ci]; no fresh test/CI, dispatch, merge, deployment or release claim.

## 04c split and first component - 2026-11-17

User requested splitting 04c and implementing/pushing the first item at 09:21 CET,
then explicitly requested completing the 04c.1 push at 09:33 CET. The coherent
first item is a pure executable kernel, not graph/provider integration. The
preceding documentation-only wording describes the 04b close-out, not this mixed
code/test/documentation delivery. Accepted 04b and earlier lifecycle work stay closed.

- 022.04c.1 - implementation included in this delivery; focused component checks
  passed, CI/formal acceptance pending. Ordered executor for appendStr, setProp
  and prefixSuffixStringProp with dotted/root/wildcard targets, independent results,
  contextual local errors and pre-concatenation/per-operation byte checks. Gate:
  declared literal subset executes deterministically, input/payloads remain
  independent, ordering and no-op/limit behavior have focused evidence.
- 022.04c.2 - ready after c.1 delivery: integrate compiler/graph/template grouping
  and worker execution, wrap local errors in selected/dependency diagnostics,
  implement string remove shorthand and basic prependArr/appendArr. Verify
  selected/template instructions merge per property before tail groups, preserve
  logical cached accounting without double charging, and add actual graph/worker
  fixtures without weakening existing unique assertions.
- 022.04c.3 - pending c.2: appendIfNotExistsArr, insertArr, replaceArr,
  replaceOrAppendArr, removeArr and renameArr; selectors, absent/no-match/duplicate
  behavior, ordering and expansion/resource boundaries against pinned runtime.
- 022.04c.4 - pending c.3 and applicable 04a contracts: scalarAddProp/scalarMultProp
  and calculateProp with a restricted expression evaluator, explicit numeric-string/
  sign/rounding semantics and adversarial bounds. Never eval/import source code.
- 022.04c.5 - pending earlier items and safe-regex contract: replaceTxt/replaceName,
  deliberate supported JavaScript regex/tag semantics, bounded execution and
  combined order-sensitive compatibility/oracle evidence. No silent approximation.

### c.1 contract, limits and evidence

New scrying_glass_fivetools_modifications.apply_modifications consumes compiler-
shaped records with property/mode/payload_json and requires the caller's check
callback. Ordinary groups keep first-seen order, then _, then *; groups merge in
supplied selected/template append order. Wildcards are property-major over the
13 pinned COPY_ENTRY_PROPS. Logical input instructions (including no-ops) count
once; the fixed wildcard expansion does not multiply the source instruction count.
Payloads are decoded independently per application. Returned content is independent
of input; failures return no partially modified record. Nested dictionary paths
and existing canonical list indices are supported. Prototype-related/empty paths,
array holes, coercive truthy non-string appends and dynamic <$...$> payloads fail
explicitly. Optional string options accept string/null; broad JS coercion and
numeric-key enumeration compatibility are not established by this component.
No-property setProp remains a no-op, and non-string prefix/suffix targets remain
no-ops. Other modes, including remove, remain explicitly deferred.

Graph Resolver, compiler, worker and all existing tests are unchanged: nonempty
graph modifications still fail pending 04c.2, even for these three kernel modes.
The local diagnostic intentionally lacks selected/dependency provenance until
that adapter wraps it. The check callback and intermediate-byte preflight are
not a standalone hard CPU/memory ceiling. c.2 must execute this kernel inside the
existing limited worker; source calculations still precede later normalization.

The exact reconstructed code/tests were rerun on Python 3.12.8:
`python -m unittest discover -s tests -p 'test_fivetools_modifications.py' -v`
reported 12 tests OK, no skips/errors/failures. These execute the actual new module
with compiler-shaped fixtures, NOT the integrated compiler/graph/worker pipeline.
Earlier preparation corrected a fixture parameter-name collision and the executor's
incorrect inclusion of the opcode envelope in the creature-byte allowance; the
byte-boundary assertion was retained. No existing assertion changed.

Seventeen controlled operation-level comparisons on Node 20.20.1 now match the
Python executor's records and top-level property order. They cover append falsey/
missing values, dotted/list paths, setProp/prefix/suffix/no-ops, group merging and
wildcards, not full getCopy or creature/provider compatibility. Oracle used the
unmodified recovered utils.js, blob 80c10d0439a5179b7d7f6e1220b9efb535a626d2,
SHA-256 67c28c64fa7cc98139923d7cfdbe4faa6807b6583a54451962a988567de1a172,
from runtime commit 32ef600fab87a585a61dd1a22e9b02dfc58c728a. Captured Parser
slice: 178960 bytes, SHA-256 e2a1828e524727332ce9c3a9f2d0b7a5bc98ea92a0e7d4731a478c0506ca93b8.
These are bounded synthetic comparisons, not a full schema/mode matrix or live
provider check; broad upstream oracle coverage remains 04a/c.5/04f work.

No full repository/provider regression, new combined 04b suite, Python 3.14 or
covering CI run is claimed. Existing workflow discovery includes the new test file
when CI runs; no workflow changes/dispatch. README/root indexes remain accurate
for the active application and unchanged indexed paths. [skip ci] remains in
intermediate 04 pushes until the final code push. Overall 04c/04/022 remain open.
