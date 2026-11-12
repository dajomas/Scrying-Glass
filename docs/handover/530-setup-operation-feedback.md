# 530 - Stage 1 setup-operation feedback

[Back to handover index](../../HANDOVER.md)

Task record: [097](../todo/097-feedback-delivery-plan.md).
Accepted campaign Step 1 history: [520](520-campaign-operation-feedback.md).

## Stage 1 accepted close-out - 2026-11-12

Status: completed and closed for all agreed Stage 1 scope. At 19:45 CET on
2026-11-12, after the covering-CI review, the user explicitly requested "Accept
and close Stage 1 now, finish documentation and push to github". This includes
Step 2 (2A-2E) and Step 3 acceptance; neither needs another acceptance request.
Earlier archive/preparation/publication/CI/acceptance-pending notes are superseded
for Stage 1 only. Stage 2 and earlier accepted units remain closed.

Accepted scope: campaign create/edit/switch/delete; setup create/save/load/switch/
rename/delete; setup copy/move between campaigns; background apply/clear/image
upload. Persistent actionable errors, matching resolution, three-second pane
successes, operation/target/campaign/setup/scope identity, obsolete-result/timer/
session/draft/selection protection, busy guards through refresh and separate
completed-mutation/failed-refresh no-replay reporting remain. Existing endpoints,
payloads, confirmations, permissions, server rules and setup behavior are preserved.

### Covering evidence and limits

| Scope | Implementation / evidence |
|---|---|
| Campaign Step 1 | Accepted close-out 7eecdc7adc5873c671e70389feed30333cc37002; tested 4f0127b56550cacb821ae2c62cb2057265eaea2a, green run 43237771405 attempt 1. |
| Setup Step 2, 2A-2E | Published 3adf212646aa8956ca6a42870c23075d5c482c9b; green run 43272584707 attempt 1; evidence 1a6e562474fe3fb82d2a9f37b6d5493a70d2307c. |
| Final Step 3 / integrated Stage 1 | cc0b67b177772e314b608817f6f51cecc322a065; Branch tests 43279736032 attempt 1; job 131397505642; publication 97eedc6da52abcfa94526fee25a3c321f0626844. |

Final evidence lives under ci-results-43279736032-attempt-1. Reviewed run.json and
jobs.json agree on branch features/perplexity-009.7, tested SHA, attempt 1 and
completed/success. All configured provisioning, syntax/import, Python/browser,
pytest, JavaScript and standalone browser/audit stages succeeded. The run finished
2026-11-12T18:34:43Z (19:34 CET). This review did not individually re-review every
test log or screenshot or independently recount every test. Earlier local counts/
negative controls are preparation evidence, not new executions or universal coverage.

The user accepted the bounded feature scope on that evidence. No new authenticated
live-server, human visual/manual, screen-reader or exhaustive accessibility evidence
is inferred. This close-out changes documentation only, uses [skip ci], runs no
new tests and modifies/dispatches no workflow. No new run outcome or close-out
commit SHA is invented before publication. No application/test/template/pin or
workflow changes, merge, deployment or blanket future write approval.

### Continuation

Stage 3 local-feature/lair/selected-campaign viewer feedback integration is next.
Stage 4 integration/responsive/accessibility hardening and approved compatibility
retirement, Deliverable 1 acceptance, Deliverable 2 connection/recovery/polling/
field association, and final 009.7/009 acceptance remain open under [097](../todo/097-feedback-delivery-plan.md#remaining-scope-and-gates).
No optional requirements or new acceptance gates are added. Test-suite cleanup
stays deferred until after 009; source-selection/Open5e are not prerequisites.

## Historical delivery records

The [complete pre-close-out handover](https://github.com/dajomas/Scrying-Glass/blob/97eedc6da52abcfa94526fee25a3c321f0626844/docs/handover/530-setup-operation-feedback.md)
preserves all delivered behavior, source digests/sizes, tests/counts, negative
controls, packaging decisions and evidence limitations verbatim. The headings below
retain incoming links; their former pending wording is historical and superseded.

## SG-TODO-009.7-S1-2A - create a new empty setup - 2026-11-12

Completed and accepted within Stage 1. Initially prepared on
1b54a2c4c47644c9ac0f72939043652d818cf337; subsequently published with 2B-2E.

### Delivered behavior

The guarded New setup handler in 060 replaces the 050 legacy owner. Exact
POST /api/setups/new {name, campaign}, name/duplicate checks and confirmation are
preserved. Detailed identities, guards and refresh behavior remain in the
[original delivery record](https://github.com/dajomas/Scrying-Glass/blob/97eedc6da52abcfa94526fee25a3c321f0626844/docs/handover/530-setup-operation-feedback.md#delivered-behavior).

### Source identity

[Original source identity](https://github.com/dajomas/Scrying-Glass/blob/97eedc6da52abcfa94526fee25a3c321f0626844/docs/handover/530-setup-operation-feedback.md#source-identity).
Historical bundle pins are not substituted for the later Step 3 identity.

### Verification executed locally on the prepared files

[Original preparation results and limitations](https://github.com/dajomas/Scrying-Glass/blob/97eedc6da52abcfa94526fee25a3c321f0626844/docs/handover/530-setup-operation-feedback.md#verification-executed-locally-on-the-prepared-files).
No additional local execution is claimed by close-out.

## SG-TODO-009.7-S1-2B-2E - save, load/switch, rename, delete - 2026-11-12

Completed and accepted within Stage 1. The user explicitly requested cumulative
2A-2E packaging rather than one operation per archive for this delivery only.

### Delivered behavior

The late setup-switch.js owner replaces the legacy Save/Load/Rename/Delete handlers.
Exact endpoints/payloads, no-confirmation/already-loaded load behavior, prompt and
delete/default behavior remain. [Original behavior/guards](https://github.com/dajomas/Scrying-Glass/blob/97eedc6da52abcfa94526fee25a3c321f0626844/docs/handover/530-setup-operation-feedback.md#delivered-behavior-1).

### Source identity

[Original identities and version history](https://github.com/dajomas/Scrying-Glass/blob/97eedc6da52abcfa94526fee25a3c321f0626844/docs/handover/530-setup-operation-feedback.md#source-identity-1).
Step 3 subsequently advances the asset URL to ?v=2.

### Verification executed locally on the prepared files

[Original preparation, negative controls and limits](https://github.com/dajomas/Scrying-Glass/blob/97eedc6da52abcfa94526fee25a3c321f0626844/docs/handover/530-setup-operation-feedback.md#verification-executed-locally-on-the-prepared-files-1).

### Remaining

No Step 2 work remains after whole-Stage-1 acceptance. Wider continuation is above.

### Publication and covering CI (recorded 2026-11-12)

Published as 3adf212646aa8956ca6a42870c23075d5c482c9b, successful run 43272584707
attempt 1, evidence 1a6e562474fe3fb82d2a9f37b6d5493a70d2307c. Earlier review recorded
1,559 Python tests OK, 631 Node passes across 79 files and 43 pytest passes, with
10 archive files matching publication; screenshots were not inspected. These are
that earlier review's counts, not a new recount. The prior pending-acceptance note
is superseded by the explicit whole-Stage-1 acceptance above.

## SG-TODO-009.7-S1-3 - setup copy/move and background controls - 2026-11-12

Completed and accepted within Stage 1. Prepared on
1a6e562474fe3fb82d2a9f37b6d5493a70d2307c, published as the final tested revision
cc0b67b177772e314b608817f6f51cecc322a065 with green covering CI identified above.

### Delivered behavior

setup-switch.js ?v=2 owns transfer open/submit and background apply/clear/upload;
030 no longer rebinds the legacy background handlers on each state load. Copy/move
retains source/target/mode and conditional unloaded-setup refresh; background
operations share busy protection. [Full behavior and identities](https://github.com/dajomas/Scrying-Glass/blob/97eedc6da52abcfa94526fee25a3c321f0626844/docs/handover/530-setup-operation-feedback.md#delivered-behavior-2).

### Source identity

030 is 17,529 bytes; bundle pin 148,660; setup-switch.js is 19,346 bytes; script
inventory remains 43. Eight-fragment order, pins/size guards and the tracked failure
marker are preserved. [Complete identities and prior sizes](https://github.com/dajomas/Scrying-Glass/blob/97eedc6da52abcfa94526fee25a3c321f0626844/docs/handover/530-setup-operation-feedback.md#source-identity-2).

### Verification executed locally on the prepared files

[Original eight-Node/three-Chromium preparation cases, negative controls and limits](https://github.com/dajomas/Scrying-Glass/blob/97eedc6da52abcfa94526fee25a3c321f0626844/docs/handover/530-setup-operation-feedback.md#verification-executed-locally-on-the-prepared-files-2).
Final hosted-CI review and its limits are stated separately above.

### Remaining

No Stage 1 implementation, publication, CI or acceptance action remains. Continue
with the existing Stage 3/4 and whole-deliverable/final gates; do not reopen Stage 2.
