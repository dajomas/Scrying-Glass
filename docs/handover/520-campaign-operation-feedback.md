# 520 - Stage 1 campaign-operation feedback

[Back to handover index](../../HANDOVER.md)

## Current: 1D.1 delete validation/request archive - 2026-11-12

Base: 3f3621ab3fae5b82bfcfe5be5545ca0a46352f32, the published 1C.2 implementation verified on GitHub.
Only 1D.1 is prepared here. No GitHub write, new commit, hosted CI, deployment or
bounded acceptance is claimed. Current publication supersedes prior pending-
publication wording only; wider covering validation/acceptance remain separate.
[Task and remaining scope](../todo/096-campaign-operation-feedback.md).

Full prior foundation/1A/1B/1C criteria, code/evidence identities and limits remain
in the [pre-1D.1 record](https://github.com/dajomas/Scrying-Glass/blob/3f3621ab3fae5b82bfcfe5be5545ca0a46352f32/docs/handover/520-campaign-operation-feedback.md).
This split replaces the single 1D delivery without adding scope or acceptance gates.

### Implemented in 1D.1

050 migrates existing last-campaign opening, campaign-selection and move-destination
validation into persistent explicit page-lane feedback: campaign.delete.open and
campaign.delete.validation use an action target. DELETE request errors use
campaign.delete with stable JSON campaign-ID targets, resolving only on matching
successful request completion. Independent target/operation feedback is retained.

Dialog-open/cancel generations and input/change/reset revisions distinguish
sessions and edit/revert. Request outcomes check dialog visibility, session,
revision, target/action/destination values, campaign registry reference, feedback
ownership and encounter scope/epoch. The single expected result transition may
arrive before the response. Obsolete errors/results cannot close reopened dialogs,
replace newer data or overwrite current feedback. Native Escape remains unchanged;
visibility/reopen guards cover that path. No mutation replay or queued submission.

Duplicate submissions are blocked through the retained follow-up and the prior
submit-disabled state is restored. Reopening a dialog while pending does not send
a second DELETE. Existing dialog markup, non-active default target, move-versus-
delete setup options, confirmations (including active/permanent-deletion warnings),
encoded ID/query, method-only DELETE options and authorization transport remain.
No new client/server deletion rules, fields or confirmation redesign.

Successful DELETE resolves its matching request error, then retains the original
registry update, modal close, setup-opening and legacy success/error follow-up.
That follow-up is deliberately NOT migrated here: explicit three-second success,
applied-deletion versus failed-refresh guidance and late-follow-up guards belong
to 1D.2. A settled request ticket is not reused as a later context guard.
1D is not complete or accepted merely because request handling is prepared.

### Scope and validation

Only 050 changes among eight source fragments: 18,593 UTF-8 bytes, SHA-256
8e32077e877f98cb763885deb23a3e72783e9b637953025ca0e0ebf9bf5608b1.
Bundle: 145,415 bytes. Only corresponding 050 digest and bundle-size pins change.
Everything from openCampaignSetup onward in 050, renderCampaignDeleteDialog itself,
040/shared applyOpenedSetup, the full published 080 (including 1A/1B/1C), templates,
other pins/order/20,000-byte guards and tracked failure marker remain unchanged.

Executed: 12 delete-request Node cases, 14 retained creation Node, 18 retained
viewer-font Node, 9 encounter-context Node, 4 source/identity/assembly/tamper/syntax
checks, and 7 complete-Admin Chromium cases (4 delete, 3 retained creation) pass.
The query browser case contains permanent-delete and empty-campaign subcases;
it is counted as one case, not two. Whole assembled JavaScript syntax also passes.
Four negative controls (session, revision, registry, epoch) fail as expected;
restored delete suite passes. Node uses the production 050 deletion section and
controller with mocked DOM/transport/context/follow-up. Chromium uses full Admin
and actual dialog/helpers with intercepted HTTP. These are not full-suite/hosted
CI, authenticated live-server, human visual, screen-reader or exhaustive
accessibility acceptance. New suites follow existing discovery; no workflow edits.

README and parent plans reviewed/retained: completed 1C implementation and wider
open scope remain accurate. Root campaign indexes and current records are updated;
prior history is preserved by immutable links. Archive supplies all TODO/handover
context, complete replacements, exact manifest/base Git objects, safe apply helper,
source review, logs and Patch/COMMIT_MESSAGE.txt. Patch is archive-only; no automatic
stage/commit/push and no deletions/renames. Do not use newzip.sh unchanged.

Intermediate 1D.1 includes [skip ci]; final 1D.2 omits it for normal push CI under
the approved split. No separate dispatch. Publish/review this archive, continue
1D.2, and review covering evidence/acceptance under the existing sequence. Previously
accepted Stage 2/global/009.1-009.6 stay closed; Stage 1/wider gates stay open and
test-suite cleanup stays deferred. No new acceptance gate or workflow is introduced.
