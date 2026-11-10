# 430 - Viewer font adjustment feedback

[Back to handover index](../../HANDOVER.md)

## 4A.10 preparation and delivery - 2026-11-10

Prepared on features/perplexity-009.7 at the user's push request, against live
baseline 9bc8aa2c22a6051fec1bad0a823464e51d936ac0. [4A.10 task/status](../todo/097-feedback-delivery-plan.md#4a10-viewer-font-adjustment-feedback---2026-11-10)
remains in progress pending covering CI/full-Admin validation and acceptance.
No implementation SHA or passing covering run is invented before evidence.

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
Live eight-part inventory sums to 115,942; +248 gives calculated total 116,190.
All inventory sizes are within limit; unchanged 070 retains 88-byte headroom.
Original pin file verified against its Git blob; revised pin AST/digest agreement
passed. AST comparison changes only 080 digest and total size, preserving seven
other pins and all test/guard logic. No full-bundle hash is claimed. Actual eight-
fragment assembly/combined parse, full identity/reader/isolation, combined/browser
suites, covering CI review and bounded acceptance remain pending.

Live instructions/head and target docs/index were checked; verified complete
prior README/TODO/source/config/workflow reads reused. Existing Branch tests
discovers the new .cjs and source contracts; no workflow changes or separate
dispatch. Mixed implementation uses normal CI without a skip marker. Task plan
and handover index updates accompany code/tests/pins. README/TODO root retain
accurate open-phase scope/links without edits. 4A.9 implementation
92183b55707759d57c361cbfe877c44c06af4f02 remains delivered but open pending its
separate CI review/acceptance; this does not close it or alter 420. 4A.1-4A.8
stay closed, 4A.11 onward stays proposed. Deliverable 1, Deliverable 2 and
SG-TODO-009.7 remain open. SG-TODO-019, agreed order and accepted 009.6 gates
are unchanged. No acceptance, merge or deployment is included.
