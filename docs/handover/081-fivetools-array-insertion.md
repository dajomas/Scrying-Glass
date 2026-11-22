# 081 - SG-TODO-022.04c.3b array insertion

This delivery supplements, and does not replace or close, the requirements in
[224](../history/224-fivetools-statblock-resolution.md) and the history in
[080](080-monster-lookup-diagnostics.md). Baseline:
`bd3100977e56a9e78cade27eb912864ef7a90c41`. Date: 2026-11-17.

## Implementation

The shared ordered executor now supports insertArr. The index helper stays in
the executor, so the bounds module and worker dependency set are unchanged.
OrderedResolver.ADAPTER_VERSION is 04c.3b-1; recreate resolver instances/caches.
The existing ordered graph and worker use this kernel; production provider
preparation, tracker fields, storage and DB behavior are unchanged.

Existing arrays are required, including valid empty arrays. Missing/null/falsey
targets fail explicitly. Scalar, object and null items wrap once; list items
preserve order and duplicates. Missing/null index means zero. ToInt32(index)==-1
appends (including -1.9 and wrapping aliases); otherwise indices truncate and
clamp like splice. Boolean/string/object/list index coercion and unsafe integer
indices are explicitly rejected. Nonfinite indices fail. Dynamic substitutions
remain deferred to 04d. Projected combined-list UTF-8 growth is checked before
copy/insertion. Existing path safety, cancellation, logical instruction limits,
property-major wildcard order and failure/input isolation remain in force.
Byte preflight is not a hard process-memory ceiling. Broad JS coercion and
byte-for-byte numeric serialization compatibility are not claimed.

## Verification and corrections

Fresh verification: Python 3.12.8, command:
`python -m unittest discover -s tests -p 'test_fivetools_insert_array.py' -v`.
12 tests ran, all passed, no skips/errors/failures. Covers index positions,
fractional/default/sentinel aliases, missing/empty targets, typed item wrapping,
dotted/wildcard paths, ordering, isolation, exact/one-over UTF-8 bytes, invalid
indices, payloads, operation budget and cancellation. The executor baseline and
unchanged bounds source were verified against their Git blob hashes before
running. The graph adapter change is the version bump only. Existing tests and
TODO/handover contracts are not rewritten.

Infinity is invalid standard JSON and is tested as a payload error; valid JSON
1e400 separately tests overflow at index validation. Earlier confirmation calls
failed validation and created no write approval; this delivery requires a fresh
confirmation bound to github_mcp_direct/push_files and the exact arguments.

Earlier reported 360 Node comparisons were not rerun or independently recovered
in this verification and are not fresh evidence. No fresh full upstream oracle,
combined graph/worker/provider regression, Python 3.14 or CI pass is claimed.
04c.3c/d, remaining 04c/04a/04d/04e/04f gates and overall 022 remain open; accepted
earlier work stays closed. Formal acceptance is pending. Intermediate commit
uses [skip ci]; no workflow dispatch, merge, deployment or release.
