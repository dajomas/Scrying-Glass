# 096 - Stage 1 campaign-operation feedback

[Back to TODO index](../../TODO.md)

## SG-TODO-009.7 Stage 1 Step 1 - 2026-11-12

Status: 1A implementation delivered; 1B edit implementation prepared as an
archive-only delivery. Publication, covering validation and bounded acceptance
pending. Foundation delivered at 64e9873f2def145cbd133f1008b69e05d71e14c8.
1A creation delivered at 3c144a2279adf9446bf0f0c082df9aa3065961c4. This archive
implements 1B only; no GitHub write or acceptance is claimed.
[Parent plan](097-feedback-delivery-plan.md) and
[evidence/remaining work](../handover/520-campaign-operation-feedback.md).

The agreed four deliveries replace combined Step 1 without expanding scope:
- 1A Create: validation/request/success, completed creation versus refresh failure,
  form preservation, focused tests and documentation; implemented here.
- 1B Edit: validation/request/success, correct campaign/edit-session association,
  newer-input preservation and obsolete feedback suppression; implemented in this
  archive, publication/covering validation/acceptance pending.
- 1C Switch: request/success, intentional campaign/setup transition, applied switch
  versus refresh failure; retain setup-opening rules; not implemented here.
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
