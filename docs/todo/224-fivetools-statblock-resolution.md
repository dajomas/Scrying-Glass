# 224 - SG-TODO-022.04: ordered 5e.tools inheritance and reference resolution

[Back to TODO index](../../TODO.md) · [Controlling parent](220-admin-statblock-viewer.md) · [Handover](../handover/080-monster-lookup-diagnostics.md)

## Current status - 2026-11-17

022.04 remains in progress. The partial 04a/b core is not a usable production
adapter or formal acceptance of either subunit. Accepted 022.01-022.03/lifecycle
and 016/017 remain closed. No merge, deployment, release or overall 022 closure.

The complete original a-f requirements remain required in the
[original addendum](https://github.com/dajomas/Scrying-Glass/blob/dcd55b68210948e1f142ba6c377cdab25e7f384e/docs/todo/224-fivetools-statblock-resolution.md).
[Prior pins, semantic differences, evidence and 04b split](https://github.com/dajomas/Scrying-Glass/blob/485a4532d61c4ce729e8584f45e1becb0841b9b4/docs/todo/224-fivetools-statblock-resolution.md)
are retained by reference without cancelling any unfinished requirement. The
parent's consolidated contract/approved limits override dated pending notes.
SG-TODO-023 is separate; no existing assertions are removed or relaxed.

## 04b increments

- SG-TODO-022.04b.1: delivered at 485a4532d61c4ce729e8584f45e1becb0841b9b4;
  focused 12-test evidence recorded there, CI/formal acceptance still pending.
  Cache ledger includes record bytes and compact UTF-8 full keys, provenance
  identities/roles/path occurrences, logical depth and work. Repeated occurrences
  are charged; timestamps/LRU links/allocator overhead are not content bytes.
- SG-TODO-022.04b.2: implemented, focused validation passed; push/CI pending.
  Strict configuration/callback validation, compact intermediate-size preflight,
  pre-mutation root/template growth checks, instruction charging before payload
  compilation and per-instruction cancellation, cache invalidation on changed
  limits, explicit recursion exhaustion and transactional cache publication.
  Full graph regression review remains a b.3 gate, not inferred from these tests.
- SG-TODO-022.04b.3: ready after b.2 delivery. Implement supported-platform
  isolated worker/deadline enforcement and review remaining graph/provider
  regressions. Terminate over-budget work; fail closed if enforcement unavailable;
  discard expired/cancelled results. Coordinate scheduler/fetch/adapter integration
  with parent units. No hard CPU/memory ceiling or production endpoint exists yet.

## b.2 boundaries and validation

The new internal bounds helper counts exact compact UTF-8 JSON bytes, including
Unicode/control escaping and finite numbers, without serializing a whole expanded
creature. Assignments and template metadata additions are sized before mutation.
Cached results cannot bypass lowered limits: any Limits change clears conversion
cache content and forces dependency/input revalidation. Existing logical cached
depth/work accounting and provenance-inclusive eviction/TTL accounting remain.
False/zero/empty invalid limits no longer fall back to defaults. Deadlines are
absolute and finite; invalid clocks fail explicitly. New completed entries are
published only after final deadline/cancellation checks, never incrementally.

Eleven focused native tests passed on Python 3.12.8 using
`python -m unittest discover -s tests -p 'test_fivetools_resolution_bounds.py' -v`.
They execute actual graph/helper code with synthetic sources. Exact/one-over
measurement includes all ASCII values, non-ASCII and non-BMP text, nested values
and numbers; all Limits fields have invalid-value cases. Growth, compiler budget,
clock/deadline, cache-limit invalidation and late-cancellation cases are included.
An initial test run found numeric overflow diagnostics were incorrectly remapped
to malformed_record; the implementation was corrected, not the assertion.
Existing 22 graph and 12 cache tests are unchanged, not rerun for this increment;
their earlier results remain historical. Full-suite/provider/Python 3.14/current
upstream-oracle/CI validation remains pending. Workflow discovery includes the new
test_*.py file when CI runs; no hosted result follows from that configuration.

## Remaining 04 gates and compatibility

04a: full operation/option/default-source matrix, relevant schema/lock verification,
safe regex/formula/substitution contract and fixture/oracle provenance. Runtime
32ef600fab87a585a61dd1a22e9b02dfc58c728a and inspected schema identities remain
recorded in the code/prior record; the exact schema lock pin remains unverified.
04c/d: execute general/creature operations, substitutions/versions and compatibility.
Recognizing 28 modes plus string removal is not executing them; nonempty mods
still fail explicitly at 04c. Retain the prior recorded runtime spell-removal
discrepancy and source-specific defaults, never invent copies from another edition.
04e: exact supporting-reference BFS, normalization and private production adapter,
including fetch/provider safety outside DB locks. 04f: adversarial/resource, actual
normalized output, persistence and existing-provider integration evidence.

JSON parsing, metadata traversal and transient working data still require b.3
worker memory/time isolation. Source intermediate limits are not normalized
snapshot/node/text/reference measurements. This core changes no existing tracker,
image lookup, six-field SG authority, stored snapshots or lifecycle behavior.
All intermediate 04 pushes retain [skip ci] until its final code push; no workflow
edits/dispatch. Delivery, covering CI and formal acceptance are separate.
