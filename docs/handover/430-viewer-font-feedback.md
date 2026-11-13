# 430 - Viewer font adjustment feedback

[Back to handover index](../../HANDOVER.md)

## 4A.10 preparation and delivery - 2026-11-10

Delivered as ca4ec4ec64c47d8b865c292e97f01ed4599108f2 on
features/perplexity-009.7, prepared against baseline
9bc8aa2c22a6051fec1bad0a823464e51d936ac0 at the user's push request.
[4A.10 task/status](../todo/097-feedback-delivery-plan.md#4a10-viewer-font-adjustment-feedback---2026-11-10)
is completed/closed for its bounded scope after reviewed successful covering CI
and the user's explicit close-out request; see acceptance below. Earlier pending
CI/acceptance notes are historical, not new manual validation evidence.

Only adjustBattleOrderFont in 080-source.js changes. Explicit persistent errors
use encounter-scoped display.battle-order-font and stable target battle-order for
both directions. Matching confirmed success silently resolves only its related
error; no new success toast. Preserve POST /api/display/battle-order-font, JSON
direction, Content-Type, Error/non-Error wording, pending early return and both
disabled controls. Success must be current before applying its font value to
latest/display controls; old-scope/superseded results cannot overwrite newer
feedback or font state. Finally always releases pending and renders controls
from the current latest display, not a stale response. Request-only catch avoids
mislabeling UI failures as failed POSTs; confirmed success resolves before UI
updates. Initial control rendering is inside try/finally to avoid a stuck pending
flag on a rendering exception. No automatic retry, new concurrency policy, server,
client-display, helper, startup, color-preview or neighboring changes. Guards
cannot revoke sent mutations. Existing two-pixel server step, 12-40 bounds,
16px control fallback and missing-display behavior remain unchanged.

Executed preparation: complete modified 080 and regression syntax passed;
18 Node regressions passed with zero failures/skips. Five negative controls were
detected: wrong error severity, removed matching resolution, removed stale guard,
removed pending guard, removed pending cleanup. Restored draft passed all 18.
Tests execute full 080 and the production-derived 070 control helper with the
real feedback controller, scoped test adapter and mocked DOM/network. They do
not execute the actual Admin bootstrap, full Admin browser/runtime or server.
No authenticated live-server, manual or exhaustive accessibility evidence.

Integration reconstructed original 080 against Git blob
8a6faa11845b8263686e12104342bd47b93f4b36. Full-fragment node --check passed;
reverse comparison preserves the whole post-function tail, including listeners,
color previews and load/setups calls. Prepared SHA-256 matches the earlier tested
draft. Behavioral regressions were not rerun during integration. New size 1,987
UTF-8 bytes leaves 18,013 below 20,000. SHA-256:
0a3c9cdbd979f859afe0d571288cc5afedbbdc5dc453b751c8bc8ab033d23b94.
Live eight-part inventory summed to 115,942; +248 gave calculated total 116,190.
All inventory sizes were within limit; unchanged 070 retained 88-byte headroom.
Original pin file verified against its Git blob; revised pin AST/digest agreement
passed. AST comparison changed only 080 digest and total size, preserving seven
other pins and all test/guard logic. No full-bundle hash was claimed. Actual eight-
fragment assembly/combined parse, full identity/reader/isolation and combined/
browser suites were unexecuted locally during preparation. Covering CI review and
acceptance were then pending. Later configured-CI success is recorded below;
individual test-log and visual-artifact review was not performed.

Live instructions/head and target docs/index were checked; verified complete
prior README/TODO/source/config/workflow reads reused. Existing Branch tests
discovers the new .cjs and source contracts; no workflow changes or separate
dispatch. Mixed implementation used normal CI without a skip marker. Task plan
and handover index updates accompanied code/tests/pins. README/TODO root retain
accurate open-phase scope/links without edits.

### Related-unit status reconciliation - 2026-11-10

4A.9 implementation 92183b55707759d57c361cbfe877c44c06af4f02 is completed/closed
for its bounded scope after reviewed successful covering CI and the user's
explicit close-out request; see [420 acceptance](420-activity-log-clear-feedback.md#4a9-bounded-acceptance-and-close-out---2026-11-10).
Its close-out is 47e0ef56334d5561f6e63e37f041693f9b1e1c5e. The separate 4A.9 run
covers 4A.9, not 4A.10. The earlier 4A.10-pending-CI note in that close-out was
historically accurate and is superseded by the independent 4A.10 review below.
4A.1-4A.9 stay closed. The later 4A.10 bounded acceptance is recorded separately.

## 4A.10 covering CI review - 2026-11-10

Branch tests run 42865982880 attempt 1 was triggered by push on
features/perplexity-009.7 and completed with conclusion success. Its head SHA is
ca4ec4ec64c47d8b865c292e97f01ed4599108f2, the delivered viewer-font implementation,
not the earlier activity-log commit or later documentation-only 4A.9 close-out.
Created/started 2026-11-10T17:32:22Z; updated/completed 2026-11-10T17:39:30Z
(18:39:30 CET).

- [Covering run](https://github.com/dajomas/Scrying-Glass/actions/runs/42865982880)
- Publication SHA: 7ac35d78e4c1a34c1599737c2c4ccb5865b21c6d.
- Published directory: ci-results-42865982880-attempt-1.
- [Run metadata](https://github.com/dajomas/Scrying-Glass/blob/7ac35d78e4c1a34c1599737c2c4ccb5865b21c6d/ci-results-42865982880-attempt-1/run.json)
- [Job/step metadata](https://github.com/dajomas/Scrying-Glass/blob/7ac35d78e4c1a34c1599737c2c4ccb5865b21c6d/ci-results-42865982880-attempt-1/jobs.json)

The tests job and every listed step succeeded; no listed step failed or skipped.
Successful configured validation stages were Python syntax/server imports, Python
suite including browser fixtures, pytest regression modules, JavaScript tests,
and standalone Python browser/audit checks. Review read run/job/step metadata,
not individual test logs or visual artifacts. This verifies covering configured-
CI success, not new per-test counts, manual/authenticated live-server results,
exhaustive accessibility coverage or completion of all full-deliverable criteria.
The historical 18-test focused preparation pass remains separate evidence, not a
newly reviewed CI test count.

At the CI-status documentation checkpoint the user requested updating docs and
pushing with skip ci, not closing 4A.10. That update was delivered as
f9b4fa72625dc8eb3a2536d5a91c59fa910a2e7a, prepared against
7ac35d78e4c1a34c1599737c2c4ccb5865b21c6d, and correctly retained pending bounded
acceptance. It changed only this handover/task plan, ran no tests, modified or
dispatched no workflow, and used [skip ci]. Those then-open status notes are
superseded only by the subsequent explicit close-out below.

## 4A.10 bounded acceptance and close-out - 2026-11-10

After reviewed successful covering CI and the CI-status documentation update,
the user explicitly requested closing out 4A.10 and pushing the changes. Mark
4A.10 completed/closed for viewer-font adjustment feedback only. This is bounded
acceptance, not acceptance of remaining feedback producers, Deliverable 1,
Deliverable 2 or SG-TODO-009.7. The implementation and covering run identities,
configured-stage results and evidence limits remain as recorded above; no new
manual/authenticated live-server or exhaustive accessibility test is claimed.

Documentation-only close-out prepared against live head
f9b4fa72625dc8eb3a2536d5a91c59fa910a2e7a. Live instructions and head were re-read;
complete current contents and verified earlier README/TODO/index/source/config
reads reused. Update this existing handover and task plan with matching completed
status, stable anchors and evidence links. Root indexes retain accurate paths and
parent open scope; no new section/path/index entry or README edit is required.
No application, tests, source pins, workflows or CI evidence change. No new tests
execute. Message includes [skip ci]; no workflow is modified or separately
dispatched, and no new workflow-run state is claimed.

4A.1-4A.10 are closed for their bounded scopes. 4A.11 battle-action global notices
is the next proposed unit and is not started by this close-out. Deliverable 1,
Deliverable 2 and SG-TODO-009.7 remain open. SG-TODO-019, agreed order and accepted
009.6 compatibility gates are unchanged. No merge, deployment or broader
acceptance is authorized or performed.
