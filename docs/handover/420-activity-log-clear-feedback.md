# 420 - Activity-log clear feedback

[Back to handover index](../../HANDOVER.md)

## 4A.9 preparation and delivery - 2026-11-10

Prepared against features/perplexity-009.7 baseline
2acd6a67fc76c770dcb6993e0abcf328295298d1 at the user's push request.
[4A.9 task/status](../todo/097-feedback-delivery-plan.md#4a9-activity-log-clear-feedback---2026-11-10)
remains in progress, with covering CI/full-Admin validation and acceptance pending.
No implementation SHA or covering success is invented before delivery/evidence.

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
Live eight-part inventory sums to baseline 115,481; a 461-byte delta gives calculated
bundle size 115,942. All inventory sizes remain within limit; unchanged 070 keeps
88-byte headroom. Prepared pin file passed AST parsing/digest agreement; AST
comparison changes only 040 digest and bundle size, preserving the other seven
pins and every test/guard. No full-bundle hash is claimed. Actual eight-fragment
assembly/combined parsing, full identity/reader/isolation and combined/browser
suites remain unexecuted here, pending covering CI review and bounded acceptance.

Live instructions, head, workflow and existing tests/audit_log_clear.py were read;
verified complete prior docs/source/config reads reused. The server-only audit's
runtime/saved-setup persistence, other-setup/background isolation and rollback
assertions stay unchanged; review is not execution. Branch tests discovers the new
.cjs and source contracts through run_split_tests.py, and invokes the audit with
patched. No workflow changes/dispatch; mixed implementation uses normal CI with
no skip marker. Necessary task/index updates are included. README/TODO root
retain accurate open-phase scope/links without edits. 4A.8 detail is summarized
in the task plan with retained anchor, handover and revision links; no open work
or history is removed. 4A.1-4A.8 stay closed; 4A.10 onward remains proposed.
Deliverable 1, Deliverable 2, SG-TODO-009.7 remain open. SG-TODO-019, agreed order
and accepted 009.6 gates remain unchanged. No acceptance, merge or deployment.
