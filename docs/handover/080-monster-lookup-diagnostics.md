# 080 - Monster lookup diagnostics repair

[Back to handover index](../../HANDOVER.md)

Last updated: 2026-11-01.

## Scope and diagnosis

Baseline: `68adc77e6e0fc53e5db3b09853088f9f57ee3d46`. Original test blob: `648552b050c9a402d708e2aa46f2195d85ae975c`; original handler module blob: `7d6a94bddc96ffd248f917f45c0edd88a242176a`.

All nine original diagnostics tests failed locally. The AST-extracted handler lacked package context, so importing the 5e.tools fallback failed before lookup. Fixing that fixture and isolating D&D-only cases left four failures: detailed diagnostics had also been lost from the production endpoint.

## Changes

The fixture now supplies `__package__='python'`, explicitly disables fallback for D&D-only cases, mocks fallback lookup, and asserts that no real fallback HTTP request occurs. Original test methods and assertions remain unchanged; eight additional tests cover provider priority/order, independent flags, fallback success/errors, blank species and sanitized parser errors.

The production handler restores safe reasons for empty searches, failed searches, per-legacy/current page failures and unusable AC/HP, plus a warning for unusable pages. Raw exception details remain in server logs, not response reasons. D&D Beyond priority, partial-stat success, 5e.tools fallback, cancellation propagation, response structure and unrelated display handlers remain unchanged. Diagnostic text is intentionally more informative; this is not a production-code-free repair.

## Verification and limitations

On Python 3.12.8: 17 diagnostics tests and all 15 unchanged tests in `test_fivetools_fallback.py` passed together. Repeats with ImportWarning, ResourceWarning and DeprecationWarning treated as errors passed. Candidate Python files compile. Original diagnostic test methods and unrelated display-handler ASTs were checked unchanged.

The focused local tree used the hash-verified display and 5e.tools modules, the original provider tests, and the pinned production image-lookup method as an AST-extraction input. It was not a full checkout or real FastAPI/browser integration run. All remote providers were mocked; live endpoints, full CI and Python 3.14 remain unverified for this repair.

README was reviewed and remains accurate: provider selection and configuration did not change. TODO.md is absent and is not created. Source splitting, other failure categories and workflow changes are outside this commit. Normal CI should verify the approved push.

## 022.04a/b core graph preparation - 2026-11-17

Separate partial private-statblock graph work adds contextual dependency errors,
exact-source loading, recursive inheritance/templates and immutable results.
[224](../todo/224-fivetools-statblock-resolution.md) records pins, current evidence,
unfinished matrix/resource gates and all remaining a-f requirements. This does
not complete/accept 04a, 04b or the adapter or alter existing lookup behavior.

Baseline: dcd55b68210948e1f142ba6c377cdab25e7f384e, features/perplexity-statblock.
Current reconstructed payload: 22 native graph tests passed on Python 3.12.8,
synthetic sources, no skips/errors/failures. Prior seven upstream comparisons
were not rerun on this payload. No full suite, live-provider or covering CI claim.
Intermediate 022.04 commits use [skip ci] by user instruction; no workflow edits/
dispatch. Accepted lifecycle/016/017 scopes remain closed. Root README/index links
remain accurate and unchanged; current 224 status supersedes dated pending notes.

## 022.04b.1 cache content accounting - 2026-11-17

Baseline: d13a439e28ed0829d2285831e01dab16170776a7, same working branch.
User requested 04b splitting and delivery of its first increment;
[224 increments](../todo/224-fivetools-statblock-resolution.md#04b-delivery-increments---2026-11-17)
records gates and the exact content-ledger definition. b.1 replaces record-only
cache accounting with key/provenance/path/depth/work-inclusive UTF-8 charges,
consistently across staging, publication, eviction and expiry. No physical memory
ceiling, worker, provider endpoint or modification execution is claimed.

Twelve new actual resolver tests passed on Python 3.12.8, synthetic sources, no
skips/errors/failures. Existing graph tests/assertions are unchanged, not rerun;
full-suite/provider/3.14/oracle/CI validation remains pending. b.2/b.3 and 04a/c-f
remain open. This is implementation with focused evidence, not formal acceptance.
README, root indexes and workflow reviewed; no runtime user behavior or indexed
paths changed, so unchanged. [skip ci] remains required until the final 04 code
push. No manual dispatch, merge, deployment or release.

## 022.04b.2 resource boundaries - 2026-11-17

Baseline 485a4532d61c4ce729e8584f45e1becb0841b9b4. Implementation adds exact
compact-JSON preflight before growth/output allocation, strict limit validation,
instruction-budget preflight, changed-limit cache invalidation and atomic cache
publication after cancellation/deadline checks. [224](../todo/224-fivetools-statblock-resolution.md)
records scope, remaining gates and retained source/semantic history. The prior
04b increments anchor is retained there for historical links.

Eleven focused native tests passed on Python 3.12.8. The initial numeric-limit
diagnostic failure was corrected in implementation; assertions were not weakened.
Earlier 22 graph and 12 cache tests remain unchanged, not rerun here. No full
provider suite, fresh oracle, Python 3.14, hosted CI or hard memory/CPU validation
is claimed. Worker isolation and remaining regression review are 04b.3, not
provided by byte preflight. No user-facing runtime or index-path changes; README,
root indexes and workflow remain unchanged. [skip ci] until final 04 code push.
No dispatch, merge, deployment, release or accepted-scope reopening.
