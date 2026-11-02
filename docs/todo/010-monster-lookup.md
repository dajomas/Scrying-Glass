# 010 - Monster lookup accounts and candidate selection

[Back to TODO index](../../TODO.md)

## SG-TODO-001 - Monster lookup and explicit candidate selection

- Status: completed for the agreed public-provider candidate-selection scope, 2026-11-02.
- Requested: 2026-11-01. Narrowed delivery agreed: 2026-11-02.
- Priority, owner and deadline: not assigned.
- Account authentication and entitlement filtering: not implemented; preserved as [SG-TODO-004](040-dndbeyond-account-access.md), blocked/deferred.

### Scope and original request

The original request combined adding a D&D Beyond account with provider-first
zero/one/many candidate selection. On 2026-11-02 the user agreed to deliver selection
using existing public providers without credentials or account-access claims.
This completion applies to that agreed scope, not the original account-backed
requirements. Their unfinished requirements and decisions remain in SG-TODO-004.

A usable candidate has parseable AC or HP. Count usable candidates rather than
restricted search hits. Search D&D Beyond first; only successful zero usable results
(or primary disablement) permit searching configured 5e.tools sources. Confirmed
access gates are excluded candidates; genuine provider errors remain errors.

| Primary usable matches | Fallback matches | Delivered behavior |
|---|---|---|
| 1 | Not searched | Use automatically. |
| More than 1 | Not searched | Select from primary popup. |
| 0 | 1 | Use fallback automatically. |
| 0 | More than 1 | Select from fallback popup. |
| 0 | 0 | Report no match; retain manual entry. |

### Completed acceptance criteria

- [x] Provider-order and zero/one/many matrix covered by offline tests in the successful CI run.
- [x] Unusable results, deduplication, independent provider flags and provider-error distinctions covered by automated regressions.
- [x] Actual marketplace category redirect excluded; all-locked fallback and mixed usable-primary priority covered by four new regressions.
- [x] Single-result automatic use, popup selection, Cancel/Escape and manual entry confirmed by the user and corresponding automated fixtures.
- [x] Real typing/debounce and dialog focus transfer/restoration do not repeat lookup; all three new Chromium focus tests passed.
- [x] Existing values and edits made during lookup remain protected; confirmed by the user, with automated edit-preservation coverage.
- [x] Selected-candidate stats and image continuity, including upload precedence, confirmed by the user. Signed-token and no-image/manual behavior have offline coverage.
- [x] Regression CI verified green before documentation close-out; full-suite results and manual evidence recorded separately below.

### Implementation and validation evidence

- Initial implementation: 2c00583fb0c37b940d8580e324816a39960995e8.
- Initial locked-page correction: fe392f77c0080d3ca3540abfbb301fc94ec9655a.
- Actual marketplace redirect and blur-loop fixes: 846971b1ada9b5e44df8b7dca238c092e43efb47.
- Seven regression tests added: 9e5c7bb080fdfda0d5cf157dae083fa9336f0a72.
- Focus-test instrumentation repaired: 1474cde5c4d270c540d7009e5c08770058b40ac5.
- Verified successful Branch tests run: 41509918102, attempt 1, against 1474cde5c4d270c540d7009e5c08770058b40ac5.
- Evidence snapshot: ci-results-41509918102-attempt-1 at 6d9d1a720c4ddcdaf0671fb0271f8f4ef0902d85.

Inspected run.json records completed success for all configured check steps:
syntax/server import, unittest/browser fixtures, pytest regressions, JavaScript,
and standalone browser/audit checks. The unittest log reports 941 tests, OK.
Parts 000054 and 000055 of reader-chunks/file-000007 show all seven new regressions
passing; part 000058 records the unittest summary. Seven is a subset of 941, not
an additional suite total. Some downloaded log labels say UNKNOWN STEP; run.json
provides the workflow-step conclusions.

On 2026-11-02 the user confirmed green CI for 846971b and all requested manual
checks: live Crawling Claw fallback, popup without clicking outside, chosen stats,
automatic single match, Cancel/Escape/manual entry, selected-image continuity,
upload precedence and existing/in-flight edit protection. Manual confirmations
are user-reported, not assistant-run live-provider tests.

Earlier validation-pending statements and failed run 41508781022 are superseded
for close-out by the successful corrective run. That failure was a fixture setup
error, not evidence that the application focus behavior failed.

### Retained limitations

CI provider responses are mocked and browser fixtures intercept HTTP; they do not
constitute full live-provider or full-application end-to-end coverage. Account-backed
access is deferred. Source/edition labels, configured-source limits, unresolved
5e.tools inheritance and unknown gate wording remain documented implementation
limits, not claims of complete provider compatibility. No new application tests
are run by this documentation-only close-out; the requested commit uses [skip ci].

See [handover and validation history](../handover/200-monster-candidate-selection.md)
and [earlier diagnostics](../handover/080-monster-lookup-diagnostics.md).
