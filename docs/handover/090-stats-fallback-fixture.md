# 090 - Stats fallback fixture repair

[Back to handover index](../../HANDOVER.md)

Last updated: 2026-11-01.

## Scope and root cause

This is a test-only repair of the extracted lookup namespace and StatsFallbackTests fixture in `tests/test_bughunt_210aac8.py`. Production lookup, provider, model, lair and authorization code is unchanged. README was reviewed and remains accurate. TODO.md is absent and is not created.

Baseline: `188bc2d82caeb39fa12a6bba59ac598d19edd75c`. Original test Git blob: `f9e578fc4f643f602f53dce13945ed06f608e141`.

The handler was compiled into an empty globals dictionary. Its relative import of the 5e.tools module raised `KeyError: "'__name__' not in globals"` before visiting D&D Beyond candidates. Four positive tests failed. Two negative tests happened to pass because the outer error handler returned found=False, not because their intended lookup paths ran.

## Repair

- Give the extracted handler a module name and `__package__='python'`.
- Disable 5e.tools explicitly in D&D-only contexts; independently enabled fallback behavior is tested separately.
- Mock secondary lookup and guard its HTTP opener; restore patches with unittest cleanup.
- Reject the generic outer-handler error response in the call helper so setup errors cannot satisfy negative tests silently.
- Preserve all six original StatsFallbackTests methods and assertions.
- Add six tests for primary success, ordered secondary fallback, independent provider flags, no-provider behavior, actual visitation of both failed candidates and cancellation propagation.

The module's ModelTests, LairTests and CandidateTests classes and their existing test methods are unchanged.

## Local validation and limits

A focused AST harness executed the module's actual lookup-extraction statements and StatsFallbackTests class with the pinned production handler as its input. The secondary-provider module copy matched Git blob `e262538874b335a8455358a45d9f6bcc7e45969a`.

Original: six focused tests, four failures. Candidate: all 12 focused tests passed on Python 3.12.8; repeats treating ImportWarning, ResourceWarning and DeprecationWarning as errors passed. The entire candidate test file compiled. AST comparison verified all original test methods and the other test classes remained unchanged.

This harness did not execute the module's Pydantic/model, lair or HTML-candidate classes, the full application, real FastAPI transport or live providers. CI must run the complete module and full suite on Python 3.14. No passing CI result or full-suite failure-count reduction is claimed before that run.

Normal CI is requested for the approved push; no skip marker or workflow change is included. Other failure categories and source splitting are outside this commit.
