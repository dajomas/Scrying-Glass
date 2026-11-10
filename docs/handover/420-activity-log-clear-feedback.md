# 420 - Activity-log clear feedback

[Back to handover index](../../HANDOVER.md)

## 4A.9 preparation and delivery - 2026-11-10

Delivered as 92183b55707759d57c361cbfe877c44c06af4f02 on
features/perplexity-009.7, prepared against baseline
2acd6a67fc76c770dcb6993e0abcf328295298d1 at the user's push request.
[4A.9 task/status](../todo/097-feedback-delivery-plan.md#4a9-activity-log-clear-feedback---2026-11-10)
is now completed/closed for its bounded scope; see acceptance below.
Preparation-time pending notes are historical, superseded by reviewed covering CI
and explicit user-requested close-out, not new manual validation evidence.

Only the clear handler in 040-source.js changes. Preserve count confirmation,
bodyless POST /api/activity-log/clear, return-count wording and existing empty
fallback for non-array activity data. Encounter-scoped activity-log.clear has
stable target activity-log, not the changing count. Request errors persist;
matching confirmed success replaces related error/info only and precedes load(),
with normal five-second global success expiry. Refresh failure stays load-owned,
not a failed clear or a reason to replay POST. No automatic retry, new concurrency
lock/control policy, server, export, CSV-import, campaign or neighboring changes.
Stale/superseded results cannot publish or refresh newer scope; guards cannot
revoke a sent mutation. Already-empty is info, not confirmed server success: no
confirmation/request/refresh, one replacement info notice, and no erasure of an
existing clear error. A newer empty observation supersedes the pending operation
identity; it does not establish server success or resolve the retained error.
The unchanged server clears runtime and active saved-setup logs without saving
other edits. CSV/JSON exports keep their original navigation URLs.

Executed preparation: handler-slice/test syntax passed; 21 Node regressions passed
with zero failures/skips; five faults detected (empty severity, error severity,
missing stale guard, count-dependent target, success delayed until after refresh);
restored draft passed all 21. Tests execute real controller/bootstrap with a
production-derived export/clear slice and mocked DOM/network, including real
loadState handling of rejected mock fetch. Not full Admin rendering/browser,
authenticated live-server, manual or exhaustive accessibility evidence.

Complete-fragment integration reconstructed original 040 against Git blob
81ae5d291e6453ec024372de80d10a6b3b752bde. Full modified fragment passed
node --check. Reverse comparison preserves all surrounding source byte-for-byte;
the integrated export/clear slice equals the previously tested draft. Behavioral
tests were not rerun during integration. New size 11,797 UTF-8 bytes, headroom
8,203 below 20,000. SHA-256:
5b2767608e8337545e9c012f065ada62d1ddf87ffa84941df6c314f4bb16c13b.
Live eight-part inventory summed to baseline 115,481; a 461-byte delta gave the
calculated 4A.9 delivery bundle size 115,942. All inventory sizes remained within
limit; unchanged 070 kept 88-byte headroom. Prepared pin file passed AST parsing/
digest agreement; AST comparison changed only 040 digest and bundle size,
preserving the other seven pins and every test/guard. No full-bundle hash was
claimed. Actual eight-fragment assembly/combined parsing, full identity/reader/
isolation and combined/browser suites were unexecuted during preparation; covering
CI review and bounded acceptance were then pending. Later CI is recorded below.
The subsequent 4A.10 delivery has its own bundle expectation in 430.

Live instructions, head, workflow and existing tests/audit_log_clear.py were read;
verified complete prior docs/source/config reads reused. The server-only audit's
runtime/saved-setup persistence, other-setup/background isolation and rollback
assertions stay unchanged; preparation review is not execution. Branch tests
discovers the new .cjs and source contracts through run_split_tests.py, and invokes
the audit with patched. No workflow changes/dispatch; mixed implementation used
normal CI without a skip marker. Task/index updates accompanied delivery.
Preparation-time 4A.10-proposed status was later superseded by its delivery in
ca4ec4ec64c47d8b865c292e97f01ed4599108f2; see [430](430-viewer-font-feedback.md).

## 4A.9 bounded acceptance and close-out - 2026-11-10

After the successful covering-CI review, the user explicitly requested updating
documentation, pushing with skip ci and closing 4A.9. Mark 4A.9 completed/closed
for activity-log clear feedback only. This is bounded acceptance, not acceptance
of 4A.10, the remaining feedback producers, either full feedback deliverable or
SG-TODO-009.7.

Covering Branch tests run 42863235975 attempt 1 was triggered by push on
features/perplexity-009.7 and completed with conclusion success. Its head SHA is
92183b55707759d57c361cbfe877c44c06af4f02, the delivered 4A.9 implementation.
Created/started 2026-11-10T17:16:26Z; updated/completed 2026-11-10T17:23:28Z
(18:23:28 CET). It does not validate the later 4A.10 implementation.

- [Covering run](https://github.com/dajomas/Scrying-Glass/actions/runs/42863235975)
- Evidence publication SHA: 9bc8aa2c22a6051fec1bad0a823464e51d936ac0.
- Published directory: ci-results-42863235975-attempt-1.
- [Run metadata](https://github.com/dajomas/Scrying-Glass/blob/9bc8aa2c22a6051fec1bad0a823464e51d936ac0/ci-results-42863235975-attempt-1/run.json)
- [Job/step metadata](https://github.com/dajomas/Scrying-Glass/blob/9bc8aa2c22a6051fec1bad0a823464e51d936ac0/ci-results-42863235975-attempt-1/jobs.json)

The tests job and every listed step succeeded, with no listed failed/skipped step.
Successful configured validation stages: Python syntax/server imports, Python
suite including browser fixtures, pytest regression modules, JavaScript tests,
and standalone Python browser/audit checks. Review read run/job/step metadata,
not individual test logs or visual artifacts. This establishes covering CI
success for the configured stages, not new per-test counts, manual/authenticated
live-server results, exhaustive accessibility checks or completion of all full-
deliverable criteria. The historical 21-test preparation pass is separate evidence,
not a newly reviewed CI count. No new tests execute during this close-out.

Documentation-only close-out prepared against live head
ca4ec4ec64c47d8b865c292e97f01ed4599108f2. Update this handover, task plan and
430's stale 4A.9 pending-status reference without closing 4A.10. Verified complete
README/TODO/index and target-document reads reused; live instructions/head and
this handover re-read. Root indexes retain accurate paths and parent open scope;
no new section/path/index entry or README edit is needed. No application, tests,
pins, workflows or CI evidence change. Message includes [skip ci]; no workflow
is modified or separately dispatched, and no new workflow-run state is claimed.

4A.1-4A.9 are closed for their bounded scopes. 4A.10 remains delivered but open
pending its own covering CI review/full-Admin validation and acceptance; 4A.11
onward stays proposed. Deliverable 1, Deliverable 2 and SG-TODO-009.7 remain open.
SG-TODO-019, accepted 009.6 gates and agreed order remain unchanged. No merge,
deployment or broader acceptance is authorized or performed.
