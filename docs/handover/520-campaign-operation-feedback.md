# 520 - Stage 1 campaign-operation feedback

[Back to handover index](../../HANDOVER.md)

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
