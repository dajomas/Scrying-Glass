# 410 - Global removal fallback feedback

[Back to handover index](../../HANDOVER.md)

## 4A.8 preparation and delivery - 2026-11-10

Delivered as 7996f81994c989c66e7e34d28791930ea41b65eb on
features/perplexity-009.7, prepared against baseline
b36ed511e33980448ed0162802d1baee48371007 at the user's finish/push request.
[4A.8](../todo/097-feedback-delivery-plan.md#4a8-global-removal-fallback-feedback---2026-11-10)
is now completed/closed for its bounded scope; see the acceptance below.
Preparation-time pending notes are historical, superseded by the covering CI
and explicit user-requested close-out, not evidence of new manual validation.

Only the legacy data-remove branch changes. Modern data-remove-kind/data-remove-id
routing keeps priority and pane-based removeCombatant stays unchanged. Current
monster/character row renderers use that modern route; this unit does not migrate
pane roster removal. Preserve named confirmation and encoded bodyless DELETE.
After confirmation, capture encounter-scoped combatant.remove.fallback targeting
the endpoint ID; kind/name are display metadata. Cancel leaves feedback/control
state intact. Current request errors persist and reenable the original button.
Stale/superseded failures cannot publish or reenable a newer pending attempt.
Matching success replaces only its error with explicit success before load(),
using server name or confirmed name when JSON is absent, and existing five-second
global expiry. Refresh failure stays load-owned; confirmed deletion must not be
relabeled failed or reenabled for replay. Scope guards do not revoke sent mutations.
No automatic retry, new concurrency policy, pane/bulk-removal or server changes.

Historical preparation: slice and regression syntax passed; 20 Node regressions
passed with zero failures/skips; five negative controls were detected (error
severity, collapsed targets, missing stale guards, success after refresh, missing
failure-button restoration); restored draft passed all 20. Real controller and
complete bootstrap execute with production-derived delegated prefix, mocked DOM/
network and actual loadState handling of a rejected mock fetch. Not full Admin/
rendering/browser, authenticated live-server or manual evidence. Behavioral tests
were not rerun during final integration.

Final integration reconstructed complete original 070 against Git blob
1b8a2c9e53e6a9ae6f1faeb963b6c2dd411337f6. Complete modified fragment passed
node --check and reverse comparison verified all surrounding source, including
4A.7, unchanged. Size 19,912 UTF-8 bytes leaves 88 below the 20,000 limit. SHA-256:
d426d21ad53c79eed2c6944697b835337c9073c0862dd3a5085e63c6173750d1.
Calculated assembled size 115,481 bytes is 475 above the prior baseline; only 070's
digest/total-size expectations change. Updated pin file passed AST parsing/digest
agreement; size/order/tamper guards remain intact. At that preparation checkpoint,
full assembled-bundle/reader/isolation tests, browser/combined suites and covering
CI were pending. Other fragments/pins, eight-part order and tracked admin.js
failure marker are unchanged. Later covering CI is recorded below.

Live instructions/read/write schemas and branch head were checked. Complete prior
docs/source/config reads reused against the unchanged baseline. README and TODO
index retain accurate open-phase scope/links without edits. Task plan summarizes
closed 4A.7 with retained anchor/evidence; no open work/history is deleted. This
new section is linked from the existing handover index. Existing CI discovers the
new .cjs and source contracts; no workflow changes/dispatch. Mixed commit used
normal CI without a skip marker. 4A.1-4A.7 stay closed; 4A.9 onward stays proposed.
Deliverable 1, Deliverable 2, SG-TODO-009.7 stay open. SG-TODO-019 and agreed order
are unchanged. No broader acceptance, merge or deployment is implied.

## 4A.8 bounded acceptance and close-out - 2026-11-10

The user explicitly requested closing 4A.8 and updating documentation after
review of its successful covering CI status. Mark 4A.8 completed/closed for the
legacy global removal fallback only. This is bounded acceptance, not acceptance
of pane roster removal, the remaining feedback producers, either full feedback
deliverable or SG-TODO-009.7.

Covering Branch tests run 42858349138, attempt 1, was triggered by push on
features/perplexity-009.7 and completed with conclusion success. Its head SHA is
7996f81994c989c66e7e34d28791930ea41b65eb, the delivered implementation, not an
earlier baseline. Run created/started 2026-11-10T16:48:40Z and updated/completed
2026-11-10T16:55:47Z (17:55:47 CET).

- [Covering run](https://github.com/dajomas/Scrying-Glass/actions/runs/42858349138)
- Evidence publication commit: 28ecb45d3c8dd3f610b74c258240a3ce3215aaf1.
- [Run metadata](https://github.com/dajomas/Scrying-Glass/blob/28ecb45d3c8dd3f610b74c258240a3ce3215aaf1/ci-results-42858349138-attempt-1/run.json)
- [Job/step metadata](https://github.com/dajomas/Scrying-Glass/blob/28ecb45d3c8dd3f610b74c258240a3ce3215aaf1/ci-results-42858349138-attempt-1/jobs.json)

The tests job and every listed step completed successfully, with no listed failed
or skipped step. Successful validation stages were Python syntax/server imports,
Python suite including browser fixtures, pytest regression modules, JavaScript
tests, and standalone Python browser/audit checks. This establishes covering CI
success for the configured stages. The review read run/job/step metadata, not
individual test logs or visual artifacts; it does not invent per-test counts,
manual/authenticated live-server results, exhaustive accessibility checks or
coverage of all remaining deliverable acceptance criteria. The historical 20-test
focused preparation pass is separate evidence, not a newly reviewed CI test count.

This documentation-only close-out changes this handover and the existing task
plan. Live instructions and target documents/indexes/README were reviewed against
28ecb45d3c8dd3f610b74c258240a3ce3215aaf1. README's incomplete-phase warning and
historical baseline, and the root handover/TODO indexes' existing links and parent
open statuses, remain unchanged; no new section/path/index entry is required.
No application, tests, source pins, workflows or CI evidence files change. No new
tests are executed. Commit message includes [skip ci]; no workflow is modified
or separately dispatched and no new workflow-run state is claimed.

4A.1-4A.8 are closed; 4A.9 activity-log clear remains the next proposed unit,
not started by this close-out. Deliverable 1, Deliverable 2 and SG-TODO-009.7
remain open. SG-TODO-019, accepted 009.6 compatibility gates and the agreed
sequence are unchanged. No merge or deployment is authorized or performed.
