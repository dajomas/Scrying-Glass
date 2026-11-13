# 550 - Stage 4 integration reconciliation and accessibility hardening

[Back to handover index](../../HANDOVER.md)

Task record: [097](../todo/097-feedback-delivery-plan.md).
Previous stage: [540 Stage 3 close-out](540-local-feature-feedback.md#stage-3-accepted-close-out---2026-11-12).

## Status - 2026-11-12

Completed and closed for the agreed Stage 4 scope after explicit user acceptance
on 2026-11-12 at 21:49 CET: "Accept and close stage 4, update documentation and
push with skip ci". This supersedes the earlier archive-only, publication/CI/
acceptance-pending notes. Do not reopen Stage 4 or request acceptance again.
Stages 1-3 and earlier accepted scopes remain closed; whole Deliverable 1 acceptance,
Deliverable 2 and final 009.7/009 close-out remain open.

## Stage 4 accepted close-out - 2026-11-12

Accepted scope: typed-feedback integration reconciliation and approved compatibility
retirement, superseded-handler removal, document language/main landmark, legacy
dialog semantics/focus/keyboard behavior and target-specific destructive
confirmations. Endpoints, payloads, combat, permissions and existing cancellation
behavior remain unchanged.

Implementation: 535af6f350fdcb0a473d4d43133e0d8ac7c0b50e on
features/perplexity-009.7. Successful covering Branch tests 43302214845 attempt 1,
job 131476065294; evidence publication 3bfa218c1ecd0b93c3a7278f88dd811ea4380540,
directory ci-results-43302214845-attempt-1. Reviewed run.json and jobs.json agree
on branch, tested SHA, attempt, completed status and success. All configured
Chromium provisioning, syntax/import, main Python/browser, pytest, JavaScript and
standalone browser/audit stages succeeded. Completion: 2026-11-12T20:47:35Z
(21:47 CET). Review did not individually re-review every test log/screenshot or
recount tests; no new authenticated live-server, human visual, screen-reader or
exhaustive accessibility verification is claimed. Local audit/fixtures below are
preparation evidence, not new executions or an exhaustive hosted-CI audit.

The implementation was prepared on 93be54ac and delivered as
SG-TODO-009.7-S4.zip. The user's earlier request "Stage 3 is closed, now please
implement Stage 4 and provide an archive" authorized the compatibility retirement
reserved by 097; the 21:49 CET request now explicitly accepts its delivered scope.

This documentation-only close-out uses [skip ci], executes no new tests and
changes/dispatches no workflow. No application/test/template/asset/pin/permission
or assembly change, merge, deployment or blanket future write approval. No new
run result or close-out commit SHA is invented before publication.

No Stage 4 implementation, publication, covering-CI or acceptance action remains.
Next is the existing whole Deliverable 1 integrated evidence review and acceptance,
then Deliverable 2 connection/recovery/polling/field association and final 009.7/009
acceptance under [097](../todo/097-feedback-delivery-plan.md#remaining-scope-and-gates).
No optional scope or new acceptance gate; test-suite cleanup stays deferred until
after 009. Earlier implementation details and limits below are preserved.

## Integration reconciliation and compatibility retirement

- Untyped pane delivery is retired. `scryingAdminFeedback.deliver(region, text)`
  without an explicit ticket for that region and a severity now throws for every
  region, as global delivery already did. `legacyRegions()` and the internal
  `legacy.<region>` publication were removed (admin-feedback-admin.js?v=5).
- The last live untyped callers were migrated to typed page-lane tickets in the
  campaign region (020 `campaignListNotice`/`announceMovedSetups`):
  - `campaign.setups.load` (target `campaign-list`): a campaign-list load error
    persists until dismissal or the next successful load, which resolves it.
  - `campaign.setups.moved`: the server's moved-setups notice is information that
    persists until dismissed or replaced. Used by `setups()`, the 060 new-setup
    follow-up and setup-switch.js (`?v=3`) refreshes.
- Superseded handler bodies that later owners always replace were removed from the
  fragments: 010 non-roster `patch()` branch; 030 Edit base submit and setup-import
  handlers (040 owns them); 040 campaign edit/submit/switch bodies (080 owns them);
  050 setup transfer/new/save/load/rename/delete (setup-switch.js and 060 own them);
  070 Start/tie/Next/End/Reset All handlers (admin-start-validation.js,
  admin-initial-visibility.js, battle-actions-next.js, admin-end-feedback.js and
  admin-reset-all-feedback.js own them). The install points the later owners guard
  on (`#campaignForm.onsubmit`, `switchCampaign`, `#newSetup.onclick`, `startBattle`)
  are kept as documented minimal functions. 070 `startBattle` keeps the request and
  reload; errors propagate to the owning wrapper. `#cancelOrder`,
  `#campaignSetupFrom.onchange` and every other binding are unchanged.
- The eight-fragment assembly is preserved; the bundle shrinks from 148,660 to
  130,882 bytes (010: 19,502; fragment 070: 19,250 is unchanged). No ninth
  fragment; static/admin.js stays the tracked marker.

## Accessibility hardening

- `templates/admin/000_document_start.html`: `<html lang="en">`.
- admin-workflow-navigation.js?v=2: `<main id="adminScroll">` keeps its implicit
  main landmark (it was given `role="tabpanel"`). The selected tab still names it via
  `aria-labelledby`, and tabs keep `aria-controls`, `aria-selected` and roving
  `tabIndex`.
- New admin-dialog-accessibility.js?v=1 (loaded after admin-live-workspace.js;
  44 Admin scripts) for the 11 legacy `.modal` overlays:
  - Gives each dialog `role="dialog"`, `aria-modal="true"`, a name from its
    heading (`aria-labelledby`) and `tabindex="-1"`, unless already present.
  - On open, it moves focus into the dialog unless the opener already placed it
    there. On close, it returns focus to the opener, but only when focus was lost
    with the overlay. It never takes focus back from elsewhere.
  - Tab and Shift+Tab are contained in the topmost open overlay.
  - Escape on the tie, lair-action and battle-action dialogs activates their
    existing Cancel/Close button. Other dialogs keep their earlier Escape owners.
  - The Encounter tools dialog keeps its own owner. With an overlay above it, only
    the topmost overlay handles Tab and Escape, and focus returns inside the tools
    dialog.
- Destructive or overwriting confirmations now name their target or scope:
  - Reset All shows the battle setup and the monster/character counts.
  - End shows the battle setup.
  - Roll-all initiative shows the monster count.
  - Mark dead, statistics restore and statistics save show the combatant.
  - Remove lair shows the lair.
  - Delete checkpoint shows the checkpoint label.
  - Bundle import shows the file name.

  Cancelling a confirmation still makes no request and publishes nothing.
  Scripts changed: admin-end-feedback.js?v=2, admin-reset-all-feedback.js?v=2,
  features.js?v=5, lairs.js?v=3 and statistics.js?v=2.
- Audit inputs that informed the scope (local, axe-core 4.x run ad hoc and not
  added to the repository):
  - Fixed: html-has-lang, plus the landmark-one-main, region and aria-allowed-role
    findings caused by the tabpanel role.
  - No other findings: no color-contrast violations with error records present,
    no unnamed visible controls, and no violations inside any of the 12 modals.
  - Narrow-width overflow appears only in the intentional horizontal strips
    (`#adminWorkflowTabs`, `.sg-pane-strip`).

## Tests

- New tests/test_admin_accessibility_composition.py (loaded Admin, intercepted HTTP).
  It covers:
  - the document language and the single main landmark;
  - named modal dialogs;
  - focus moving in, being contained and returning;
  - nested overlays above the tools dialog, using both this layer's Escape and the
    earlier 040 Escape owner;
  - untyped delivery rejected in every region;
  - the typed campaign-list error and moved notice;
  - named confirmations with silent cancellation.

  Negative control: against unmodified 93be54ac, 8 of its 9 tests fail. The
  focus-retention guard passes on both by design.
- Updated tests:
  - Pins: fragment digests and bundle size, the 44-script inventory, asset versions
    and confirmation texts.
  - The retired-compatibility tests now assert rejection.
  - The `legacyRegions()` assertions were replaced with a "no `legacy.*` records"
    check.
  - Marker-based fixtures were moved to the remaining owners. The setup-import
    life-filter test now drives the 040 owner.
- Local preparation results are listed in the archive's Patch/CHANGES.md; they
  precede the successful covering CI and explicit bounded acceptance above. No
  additional local test execution is claimed by this close-out.

## Limits

No authenticated live-server, human visual, screen-reader or exhaustive
accessibility verification is claimed. Deliverable 2 (connection-loss/recovery,
background-polling deduplication, field association) is untouched and remains open.
`lairActionModal` still lives inside `<main>` and is therefore inert while the
Encounter tools dialog is open; it cannot be opened from inside that dialog, so
behaviour is unchanged.
