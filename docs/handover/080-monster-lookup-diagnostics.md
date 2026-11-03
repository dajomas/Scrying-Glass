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
