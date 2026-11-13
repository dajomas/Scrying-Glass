# 540 - Stage 3 local-feature feedback

[Back to handover index](../../HANDOVER.md)

Task record: [097](../todo/097-feedback-delivery-plan.md).
Previous stage: [530 Stage 1 close-out](530-setup-operation-feedback.md#stage-1-accepted-close-out---2026-11-12).

## Status - 2026-11-12

Completed and closed for the agreed Stage 3 scope after explicit user acceptance
on 2026-11-12 at 20:48 CET. The user requested acceptance, close-out, documentation
and a GitHub push with [skip ci]. This supersedes the earlier archive-only,
publication/CI/acceptance-pending notes; do not request Stage 3 acceptance again.
Stages 1 and 2 and earlier accepted scopes remain closed.

## Stage 3 accepted close-out - 2026-11-12

Accepted scope: Encounter tools operation/manual-refresh/checkpoint feedback;
lair save/remove/toggle/open/applied feedback; lair-action dialog errors;
typed has-lair setup errors; selected-campaign viewer-access load/save feedback.
Existing endpoints, payloads, confirmations, permissions, busy guards, drafts,
selected-campaign/generation ownership and retained progress/polling roles remain.

Implementation: d17b5885baea02821224d811dffc070d6a7d33a4 on
features/perplexity-009.7. Successful covering Branch tests 43291659600 attempt 1,
job 131439168185; evidence publication db2daf8a473ebf77ff1626a8709a6a745e45b0b7,
directory ci-results-43291659600-attempt-1. Reviewed run.json and jobs.json agree
on branch, tested SHA, attempt, completed status and success. All configured
Chromium provisioning, syntax/import, main Python/browser, pytest, JavaScript and
standalone browser/audit stages succeeded. Completion: 2026-11-12T19:44:42Z
(20:44 CET). Review did not individually re-review every test log/screenshot or
independently recount tests; no new authenticated live-server, human visual,
screen-reader or exhaustive accessibility evidence is claimed. Earlier local
fixture counts/negative controls below remain preparation evidence, not new runs.

The initial archive was prepared on 1aa85334. Stage 1 was closed at 37ea8c99 on
covering run 43279736032 attempt 1 (cc0b67b1, success). Later cancelled run
43284682854 on a5aebc34 remains historical, not covering evidence and not an
outstanding failure. The green Stage 3 run above covers the delivered Stage 3 SHA.

This documentation-only close-out uses [skip ci], executes no new tests and
changes/dispatches no workflow. No application, tests, templates, assets, pins,
permissions or source-assembly changes. No new run result or close-out commit SHA
is invented before publication; no merge/deployment or blanket future write approval.

Stage 4 integration/responsive/accessibility hardening and approved compatibility
retirement is next. Whole Deliverable 1 acceptance, Deliverable 2 connection/recovery/
polling/field association and final 009.7/009 acceptance remain open under
[097](../todo/097-feedback-delivery-plan.md#remaining-scope-and-gates). No optional
scope or new acceptance gates; test-suite cleanup stays deferred until after 009.

## Scope delivered

Remaining Stage 3 producers from the [467 producer dispositions](467-bundle-import-feedback.md#remaining-producer-dispositions)
and [470 retained boundaries](470-global-feedback-close-out.md#retained-boundaries-and-deferred-work) now publish typed records through
`window.scryingAdminFeedback`. Four managed regions were added to
`admin-feedback-admin.js` (served as `?v=4`):

| Region | Element | Lane | Producers |
|---|---|---|---|
| `tools` | new `#featureFeedback` (020) | encounter; checkpoint restore uses page | `features.js` operation outcomes, manual Refresh, import rejection/refresh |
| `lair` | existing `#lairNotice` | encounter | `lairs.js` save/remove/open/applied action, `lair-state-buttons.js` toggles |
| `lairAction` | existing `#lairActionNotice` (dialog) | encounter | lair-action validation/request errors |
| `campaignViewer` | new `#campaignViewerFeedback` (030) | page, keyed by selected campaign | `campaign-viewer-admin.js` load/save |

`setup-has-lair.js` replaces its untyped `paneNotification('battleSetup', …)` with
a typed persistent `setup.has-lair` battleSetup error keyed by [campaign, setup];
success resolves it and shows nothing (the checkbox is the indication).

Policy as approved in 097: pane success expires after 3 s; actionable errors persist
until dismissal, the next success on the same operation/target, or replacement.
A declined confirmation is silent and keeps earlier errors (the legacy `Cancelled.`
text is retired). A completed mutation whose follow-up refresh fails reports a separate
persistent `<operation>.refresh` error that says not to repeat the change; refreshes
use `load(true)`. Encounter-lane records clear on campaign/setup change and stale
tickets cannot publish. Checkpoint restore uses the page lane so its success survives
the setup transition it causes. Campaign-bundle import success stays the accepted
global 5 s record (4A.13); a rejection is a tools-region error with the same key, so a
later success replaces it.

Lair specifics: dialog errors go only to `lairAction` (no double-write to the pane);
reopening the dialog resolves the prior attempt's errors; a successful apply resolves
dialog errors and reports `Applied lair action to N target(s).` in the pane. Viewer
access keeps its selected-campaign scope, generation guard and save controls; the
legacy rule that a save outcome is not reported once another campaign is selected is
kept, and a different campaign being shown drops the earlier save record. A failed
load is one persistent `viewer.load` slot resolved by the next successful load.

## Retained boundaries

- `#featureNotice` remains unmanaged and keeps background-poll status; connection
  status and polling deduplication stay Deliverable 2.
- `#campaignViewerNotice` keeps progress/guidance text (`Loading viewer access…`,
  `Saving viewer access…`, no-assigned-campaign guidance). Ownership guidance,
  previews, read-only status and tools busy-close guidance keep their dedicated roles.
- Core-fragment `paneNotification` callers and the legacy compatibility path remain
  for Stage 4 reconciliation/approved retirement. No admin fragment changed: the
  8-fragment assembly, 20,000-byte limit, bundle size and the tracked
  `static/admin.js` marker are unchanged. No script added (inventory stays 43).
- Endpoints, payloads, confirmations, permissions, busy guards and drafts are
  unchanged.

## Asset versions

`admin-feedback-admin.js?v=4`, `features.js?v=4`, `lairs.js?v=2`,
`lair-state-buttons.js?v=2`, `setup-has-lair.js?v=1`, `campaign-viewer-admin.js?v=1`.
Deploy all changed assets and template references together.

## Validation

Local results for this archive are recorded in its `Patch/CHANGES.md`. New tests:
`tests/encounter-tools-feedback.test.cjs` (7), three added cases in
`tests/setup-has-lair.test.cjs`, one in `tests/campaign-bundle-import-feedback.test.cjs`,
four added lair-button cases, extended `tests/test_lairs.js` and
`tests/test_bughunt_ec8f202.js`, four viewer Chromium cases in
`tests/test_campaign_viewer_admin_selection.py`, and the loaded-Admin Chromium
composition `tests/test_local_feature_feedback_composition.py` (4). Negative controls:
the new/updated Node tests and the composition test fail against the 1aa85334 sources.
Fixtures intercept HTTP; there is no authenticated live-server, human visual,
screen-reader or exhaustive accessibility verification. The successful hosted-CI
review and bounded user acceptance are recorded separately in the close-out above.
