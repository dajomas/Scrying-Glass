# 520 - Stage 1 campaign-operation feedback

[Back to handover index](../../HANDOVER.md)

## Current: 1D.2a follow-up feedback guards archive - 2026-11-12

Base: 478d8dacd1de282ab2ad919af9459345ab507526, published 1D.1 verified on GitHub.
Implementation archive only; no GitHub write, new commit, hosted CI, deployment
or acceptance is claimed. [Current task](../todo/096-campaign-operation-feedback.md).
Full prior scope, criteria and evidence remain in the
[pre-1D.2a record](https://github.com/dajomas/Scrying-Glass/blob/478d8dacd1de282ab2ad919af9459345ab507526/docs/handover/520-campaign-operation-feedback.md).
1D.1 publication is verified; its covering validation/acceptance remain separate.

The user requested smaller remaining deliveries and skip CI until the last part.
- 1D.2a (this archive): applied-result/own-modal-close context, independent refresh
  ownership and obsolete success/error publication guards after the shared helper.
- 1D.2b (final, pending): explicit three-second success, persistent applied-deletion
  versus failed-refresh guidance, error propagation, guarded setup/refresh internals
  and focused integration/regressions. No new scope, requirements or acceptance gate.

### Implemented

campaign.delete.refresh has its own page-lane campaign-ID ticket. The deletion
request ticket can settle without invalidating the follow-up's live identity.
The relevance predicate recognizes its own applied registry and modal close while
retaining session/revision, target/action/destination, registry, scope/epoch and
refresh-owner guards. One expected campaign/setup transition remains allowed;
unrelated and leave-return transitions cannot revive an obsolete outcome.

After applyOpenedSetup returns, stale success is not published. Caught helper
errors are also suppressed if the originating context/refresh owner is obsolete.
Matching successful follow-up resolves only its refresh identity; unrelated targets
and operations remain. Busy protection and original disabled-state restoration
span the helper, including reopening a dialog. No second/queued DELETE or replay.
Existing selection validation, DELETE request errors, endpoint/query/options,
permissions, confirmations, dialog, setup choices and normal legacy follow-up
wording remain. 040/shared helper and 080/1A/1B/1C are not changed by this archive.

Boundary: this guards publication/resolution around the shared helper, NOT its
internal fetch/render work. The helper still has legacy load/error handling;
success and helper-error feedback are still legacy, not completed typed three-
second success or persistent applied-delete/refresh-failure guidance. Those and
internal late-render protection remain 1D.2b. No completed 1D/Stage 1 claim.

### Checks and delivery

Executed: eight new focused Node component cases pass using production 050 delete
code/controller and the unchanged 1D.1 fixture with mocked DOM, request, context
and setup helper. Four negative controls detected (refresh owner, success guard,
error guard, applied registry); restored eight-case suite passes. Updated 050
passes node --check; updated pin Python parses. Existing request/browser suites,
full assembly/pin/tamper checks, full-suite/hosted CI and live-server/human visual/
screen-reader acceptance are NOT rerun or claimed here. Prior evidence remains
historical, not re-labelled as covering this revision. Final integration is pending.

050: 19,056 UTF-8 bytes, SHA-256
7295ac2a9d12343827ee1464020fd8bf1a20caca68a70e70b2e5e72500e5c866.
Calculated bundle pin: 145,878 bytes, from verified base 145,415 plus the
exact 050 byte delta. Only 050 digest and bundle-size pins change; other digest
pins/order/20,000-byte guards and marker remain. No new fragment or workflow edit.
All 050 content from openCampaignSetup onward is byte-identical to the base.

README and parent plans reviewed/retained; their wider open scope stays accurate.
Indexes/current records updated; complete TODO/handover context supplied. Patch is
archive-only: manifest, source review, logs, safe apply helper and COMMIT_MESSAGE.
No deletions/renames or automatic stage/commit/push. Do not use newzip.sh unchanged.
1D.2a uses [skip ci]; only final 1D.2b omits it for normal push CI. No separate
dispatch. Publication, covering validation and bounded acceptance remain pending.
Accepted Stage 2/global/009.1-009.6 stay closed; wider gates remain open and test
cleanup stays deferred. Continue the existing sequence without adding gates.
