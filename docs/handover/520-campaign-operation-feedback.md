# 520 - Stage 1 campaign-operation feedback

[Back to handover index](../../HANDOVER.md)

## Current: CI asset-version assertion correction - 2026-11-12

1D.2b is published at 742697d86a76a657c92653dd6f1533135399f4b0. Branch tests
43234426795 attempt 1 tested that exact revision and failed; evidence publication:
332cbf05b9903f4b718fe223dca7e5a724497496. The main Python suite ran 1,552 tests
with one failure in test_candidate_review_asset_wiring.py; the audit repeats the
same assertion. JavaScript, pytest, provisioning and syntax/import stages passed.

The assertion incorrectly pins both assets to v2 after candidate selection was
intentionally bumped to v3. The correction expects candidate selection v3 and
refresh review v2, retaining exact-once inclusion, dependency order, bounded review
asset and untyped-call checks, and rejecting obsolete versions/unversioned duplicates.
No runtime asset downgrade, application/pin/workflow change or Stage 2 reopening.

Local targeted suite: all 3 tests pass against the verified published footer.
Four negative controls (candidate v2, review v1, duplicate candidate v3, unversioned
duplicate candidate) fail as expected; restored suite passes. No new full-suite,
hosted CI or acceptance result is claimed. The corrective commit omits the skip
marker for normal push CI; no separate dispatch. Review its actual run before
bounded campaign acceptance. Earlier archive-preparation wording below is historical
and superseded only by the publication/CI facts stated here. Root indexes and README
need no structural/behavior changes for this three-file correction.

## Historical: final 1D.2b implementation archive - 2026-11-12

Base: c729cf5d7a7bcc4d37b7a6e26f7fb82a1ffaa26a, published 1D.2a verified on the live branch.
Archive only: no new GitHub commit/push, workflow dispatch, CI completion,
deployment or acceptance is claimed. This completes the agreed campaign Step 1
implementation preparation, NOT Stage 1/Deliverable 1/009.7 acceptance.
[Current task/remaining validation](../todo/096-campaign-operation-feedback.md).
Full prior scope, identities and evidence remain in the
[pre-1D.2b record](https://github.com/dajomas/Scrying-Glass/blob/c729cf5d7a7bcc4d37b7a6e26f7fb82a1ffaa26a/docs/handover/520-campaign-operation-feedback.md).

### Delivered behavior and compatibility

campaign.delete success is explicit page-lane campaign-ID feedback, published once
after successful DELETE and before view refresh, with the retained campaign/moved/
deleted/setup wording and three-second expiry. A request error remains separate.
The independent campaign.delete.refresh ticket reports a completed deletion plus
failed refresh as a persistent actionable error advising reload, never another
DELETE. Newer matching error records survive old success timers. Successful refresh
resolves only its matching operation/target; unrelated errors remain.

1D.1/1D.2a dialog/session/revision/registry/scope/epoch and refresh-owner safeguards
remain. Expected campaign/setup transition and own modal close/registry update are
recognized. Busy protection spans refresh with original disabled-state restoration.
Setup fields/opening, active/permanent-deletion confirmations, move/delete-setup
choices, encoded endpoint/query, method-only DELETE options, permissions and native
cancel/Escape behavior are preserved. No automatic replay/queued mutation.

The shared setup helper now accepts an OPTIONAL ownership callback. Only deletion
opts in: guarded helper/state loading propagates errors and rejects obsolete work
before state observation/rendering and suppresses obsolete global errors. Default
callers still use legacy load/return behavior. Optional owner callbacks pass through
request(), load() and bootstrap loadState(); two existing request wrappers forward
extra arguments so the callback cannot be silently dropped. This is bounded caller
plumbing for 1D, not reopened accepted Stage 2 scope or new polling/connection work.

Cache URLs: admin-feedback-admin.js v2 -> v3, monster-candidate-selection.js v2 ->
v3, battle-actions-next.js unversioned -> v1. Script count/order stay unchanged;
deploy all replacement files together. No controller/view/CSS/API/auth schema change.
The entire published 080 (1A/1B/1C), 050 content from openCampaignSetup onward,
unrelated fragments and tracked static/admin.js failure marker remain unchanged.

### Verification actually executed on this prepared revision

- 115 Node tests pass through the production assembled-source runner: delete
  request 12, follow-up 8, refresh 8, context/guarded state 13, retained creation 14,
  viewer-font 18, state-load 15, battle-action core 6, next feedback 20, Apply 1.
- 11 distinct full-Admin Chromium scenarios pass with intercepted HTTP: 4 deletion
  refresh, 4 retained deletion request, 3 retained creation. Parameterized cases
  remain single cases. Includes held refresh, success expiry, persistent failure,
  reopened-dialog stale state/error suppression and active deletion with empty setup.
- Four identity/assembly/size/hash/tamper/syntax tests pass; eight fragments remain
  below 20,000 bytes. Whole source is assembled by the production runner.
- Four negative controls detected: state observation ownership, obsolete global
  error suppression, late empty-setup rendering, strict error propagation. Restored
  suites pass. Current legacy assertions were migrated to explicit success/refresh
  outcomes while preserving request/confirmation/stale/busy and resolution checks.

Earlier browser preparation caught the request wrappers dropping the owner argument;
forwarding is included and the complete-page regression now passes. The reported
missing addBattleActionRow/onsubmit failure was caused by invoking a legacy source-
reading fixture directly against the tracked marker. Using run_split_tests.py
passes 6 core, 20 next and 1 Apply tests on this revision. No fixture/application or
workflow workaround was introduced for that invocation error; never overwrite the
tracked marker to make tests pass.

These are scoped fixtures/intercepted HTTP, NOT the full repository suite, hosted
CI, authenticated live-server, human visual or screen-reader acceptance. Existing
CI discovery includes new Node/Python suites and already uses the assembled runner.
The unchanged workflow targets features/perplexity-009.7. Final commit has NO skip
marker; user application/commit/push should trigger normal CI. Trigger/completion/
pass status remain unobserved until actual run evidence is reviewed. No dispatch.

### Source and archive

Bundle: 146,586 bytes. Updated fragments: 010 19,817,
030 19,609, 040 19,377,
050 19,368 UTF-8 bytes. Corresponding four digests and bundle-size pin
updated; eight-fragment inventory/order/20,000-byte guards and other pins retained.
Archive contains complete replacements, full TODO/handover context, exact manifest,
base Git objects, source review, local logs, safe apply helper and COMMIT_MESSAGE.
Patch is archive-only; no deletions/renames or automatic stage/commit/push. Do not
use newzip.sh unchanged. README/current indexes updated; parent plans retained.

Remaining: publish/review archive, review normal push CI and other already-agreed
covering evidence, obtain bounded acceptance, then continue wider Stage 1. Accepted
Stage 2/4A/009.1-009.6 remain closed. Stage 1, Stages 3-4, Deliverable 1 acceptance,
Deliverable 2 and 009.7/009 remain open; cleanup stays deferred. No new gate.
