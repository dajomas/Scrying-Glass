# 520 - Stage 1 campaign-operation feedback

[Back to handover index](../../HANDOVER.md)

## Current: 1B edit archive - 2026-11-12

Base: 02c7e12d3242da4545abb5cdd333e54e1e99335b, matching the uploaded source
snapshot and live branch when preparation began. Archive only; no new commit,
push or hosted CI outcome is claimed. 1A creation implementation was delivered at
3c144a2279adf9446bf0f0c082df9aa3065961c4. This status supersedes older index and
foundation wording without reopening accepted scopes.

Only 1B is added: campaign.edit.open selection validation; campaign.edit.validation,
campaign.edit and campaign.edit.render with stable campaign-ID targets, separate
modal-session/input-revision guards and page-lane feedback. Metadata PATCH retains
encoded ID, trimmed name/description, existing authorization/request transport and
success wording. It adds no confirmation, state fetch or mutation replay. Errors
persist until dismissal/matching resolution; pane success expires after 3 seconds.

Capture registry reference, selection and encounter scope/epoch before await;
obsolete results cannot overwrite a newer registry/selection or close reopened
forms. Edit/revert and newer drafts survive. Save success is independent of a
subsequent render failure, which advises reloading rather than saving again.
The shared pending flag spans edit request/render and still protects creation;
original button-disabled state is restored. 040 and switch/delete/setup-opening
helpers are unchanged. No 1C/1D, D2, workflows or deferred test cleanup.

Only 080 changes among eight fragments. Its size is 12,426 UTF-8 bytes; SHA-256
72d754040bd46ea0d531c1b3c997842340fcb51db095e483275630f09f55219f.
Calculated and locally verified bundle size: 136,945 bytes. Only the corresponding
080 digest and bundle-size pin change; inventory/order/20,000-byte guards and
tracked failure marker remain intact.

Executed locally against the extracted repository:
- Edit Node: 11 tests pass; retained creation: 14; viewer-font: 18; context: 9.
- Source preparation: all 4 identity/assembly/tamper/syntax tests pass.
- Production runner + complete-Admin Chromium: 6 pass (3 edit, 3 retained creation).
- Four negative controls (session owner, draft revision, registry, render identity)
  fail as expected; restored edit suite passes. An initially redundant owner-only
  negative control exposed a missing same-target reopen scenario; that scenario
  was added and now detects removal of the owner guard.
- Browser draft initially used textarea instead of the real description input,
  then a late fake-clock installation failed expiry coverage. The fixture now
  uses the actual input and observes real deadline expiry; final 6-case run passes.

Creation tests share a scoped fixture helper with edit tests. The retained busy
case now asserts migration to PATCH after creation completes, rather than legacy
edit delegation; its duplicate/busy assertions remain. This is bounded fixture
plumbing, not the deferred suite audit. Existing CI discovery includes the new
suites; no workflow edit. Full-suite/hosted CI, human visual, live-server and
screen-reader evidence remain pending, not inferred from these scoped fixtures.

Archive includes all TODO/handover context, an exact changed-file manifest,
review diff, local logs and Patch/COMMIT_MESSAGE.txt with [skip ci]. Patch is
archive-only and must not be staged. The base newzip.sh indiscriminately stages
archive entries and uses commit -a; use Patch/README.md's exact-file commands
instead. No deletions/renames. README/index status updated proportionately.
Publication, covering validation and bounded acceptance remain pending; 1C/1D
and wider gates remain open, previously accepted scopes (including Stage 2) stay
closed. The historical sections below retain their own evidence boundaries.

## 1A creation implementation checkpoint - 2026-11-12

Current status: creation migration implemented by this second checkpoint;
covering validation and bounded acceptance remain pending. This supersedes the
foundation's then-pending creation wording, including foundation index labels,
not wider gates. [Task/scope](../todo/096-campaign-operation-feedback.md).

Foundation delivered at 64e9873f2def145cbd133f1008b69e05d71e14c8. Its full
scope, nine-test preparation evidence, two negative controls, blob identities and
limits remain in the [preserved foundation record](https://github.com/dajomas/Scrying-Glass/blob/64e9873f2def145cbd133f1008b69e05d71e14c8/docs/handover/520-campaign-operation-feedback.md).
The accessor/bootstrap asset from that commit remain unchanged. No new commit or
covering-run identity is invented here.

080 installs the create-only submit owner after legacy handlers. Page-lane
campaign.create.validation, campaign.create and campaign.create.refresh use modal
session targets; encounter scope/epoch guards permit expected activation and
reject unrelated transitions/leave-return. Success precedes refresh and expires
in three seconds; refresh errors persist with no-replay guidance. Newer input,
edit/revert, reopened sessions and unrelated/newer feedback are preserved.
POST /api/campaigns, trimmed name/description, activate:true, replacement
confirmation and setup-opening behavior are retained.

Shared plumbing: wrap modal open/close for session identity, rebind cancel's
captured close callback, track input revisions and block shared-form duplicates
through creation refresh. Other edit submissions delegate unchanged. 040 and
shared applyOpenedSetup are untouched; switch/delete behavior and options remain.
An installation guard preserves isolated fragment readers without campaign owners.

Preparation: complete 080 syntax and pin-file/browser-module compilation passed.
Fourteen Node tests passed, zero failures/cancellations/skips, using complete 080
and production controller with mocked DOM, transport, feedback-context adapter
and legacy owners. Four negative controls (obsolete result, newer input, refresh
identity, scope epoch) failed; restored run passed 14/14. Earlier 24-test draft
counts are separate. Three loaded-Admin intercepted-HTTP scenarios are prepared,
not executed here; existing 43-script inventory is unchanged. Retained font
fixture was inspected, not claimed fully executed. Full reader/runner/pin/tamper,
repository/browser execution and published covering evidence remain pending.
No live-server, human visual, screen-reader or exhaustive accessibility evidence.

Only 080 changes among the eight fragments: 8,020 UTF-8 bytes, SHA-256
86d0adedfbb5c2c1b0c4c50d3794820bf742aa16d49c3d8a066a652952510540.
Its original body is retained verbatim. Only its digest and calculated bundle-size
pin (132,539 bytes) change; other pins/order, 20,000-byte guards, reader and marker
are unchanged. No asset is added. Root indexes retain foundation-history links;
current status is here and in 096. README and parent records remain unchanged.

This mixed commit uses user-directed [skip ci]; no workflow edit/dispatch or
inferred CI outcome. No automatic mutation replay or D2 near-field/connection/
polling work. Prior accepted scopes, including Stage 2, stay closed. 1A acceptance,
1B-1D and wider open gates remain open. Test-suite cleanup stays deferred.
