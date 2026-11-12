# 096 - Stage 1 campaign-operation feedback

[Back to TODO index](../../TODO.md)

## SG-TODO-009.7 Stage 1 Step 1 - 2026-11-12

Status: 1A/1B implementations published; 1C.1 switch-request archive prepared.
1B publication: 385ad5690f2783c1bb22767cba80b2bae5dff0db. Covering validation and bounded
acceptance remain separate/pending. This delivery implements only 1C.1; no new
GitHub write or acceptance is claimed. The approved 1C split does not add scope.
[Parent plan](097-feedback-delivery-plan.md) and
[evidence/remaining work](../handover/520-campaign-operation-feedback.md).

The agreed four deliveries replace combined Step 1 without expanding scope:
- 1A Create: validation/request/success, completed creation versus refresh failure,
  form preservation, focused tests and documentation; implemented here.
- 1B Edit: validation/request/success, correct campaign/edit-session association,
  newer-input preservation and obsolete feedback suppression; implemented in this
  archive, publication/covering validation/acceptance pending.
- 1C Switch: request/success, intentional campaign/setup transition, applied switch
  versus refresh failure; retain setup-opening rules. Split into 1C.1 request/validation
  (this archive) and 1C.2 success/refresh (pending).
- 1D Delete: validation/request/success, completed deletion versus refresh failure;
  retain confirmations and move/delete-setup options/dialog; not implemented here.

Retain three-second pane successes, persistent actionable errors, explicit
operation/target/scope identities, matching resolution and unrelated/newer feedback.
Guard obsolete results/timers; preserve endpoints, payloads, authorization, drafts,
selections and behavior. Busy protection spans refresh. Never replay mutations
automatically. No D2 near-field/connection/polling work.

Fourteen focused creation Node preparation tests pass. Three loaded-Admin browser
scenarios are prepared but not executed here; covering repository validation and
bounded 1A acceptance remain pending. Each write requires exact-content approval.
User-directed intermediate 1A/1B/1C pushes and corrections include [skip ci]; final
1D uses normal push-triggered CI unless subsequently directed otherwise. No
workflow edit or separate dispatch. Prior accepted 009.1-009.6, 4A.1-4A.13 and
Stage 2 stay closed. Stage 1, Stages 3-4, D1 acceptance, D2 and 009.7/009 stay open.
Test-suite cleanup remains deferred until after 009; no new acceptance gate.

## 1B archive validation and remaining work - 2026-11-12

Base: 02c7e12d3242da4545abb5cdd333e54e1e99335b. Local snapshot checks pass:
11 edit Node tests, 14 retained creation Node tests, 18 retained viewer-font Node
tests, 9 encounter-context Node tests, 4 source/pin/tamper/syntax tests and 6
complete-Admin Chromium scenarios (3 edit, 3 creation). These are scoped fixture
checks, not a full-suite, authenticated live-server or accessibility sign-off.
Four edit negative controls were detected and the restored source passed.

Remaining: publish/review this archive, review covering integrated evidence under
the agreed validation sequence, obtain bounded acceptance, then implement 1C and
1D. No new acceptance gate or test-cleanup prerequisite is added. New Node/Python
files match existing CI discovery; no workflow changes or dispatch. The archive
message includes [skip ci] for intermediate 1B; final 1D retains normal push CI.

## 1C.1 request/validation archive - 2026-11-12

1C.1 implementation prepared; publication/covering validation/acceptance pending.
10 switch-request Node tests and 3 complete-Admin switch Chromium scenarios pass;
retained creation (14 Node/3 browser), font (18), context (9) and source checks (4)
also pass. Three negative controls detected. Scoped fixtures are not full-suite
or live-server/accessibility evidence. See current 520 handover for exact base,
identities and limits. Existing success/setup/refresh behavior remains legacy for
1C.2; no false claim of complete 1C. Intermediate message includes [skip ci].
Next: publish/review this archive, then implement 1C.2 under the existing sequence;
1D remains excluded. Final 1D normal push CI and deferred test cleanup unchanged.
