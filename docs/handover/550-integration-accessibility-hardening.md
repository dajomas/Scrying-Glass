# 550 - Stage 4 integration reconciliation and accessibility hardening

[Back to handover index](../../HANDOVER.md)

Task record: [097](../todo/097-feedback-delivery-plan.md).
Previous stage: [540 Stage 3 close-out](540-local-feature-feedback.md#stage-3-accepted-close-out---2026-11-12).

## Status - 2026-11-12

Implemented locally on top of 93be54ac for the agreed Stage 4 scope and delivered
as archive SG-TODO-009.7-S4.zip. Not yet committed, pushed, CI-covered or accepted.
Do not treat Stage 4, Deliverable 1, Deliverable 2, 009.7 or 009 as closed. The
user's 2026-11-12 request "Stage 3 is closed, now please implement Stage 4 and
provide an archive" is recorded as the approval for the compatibility retirement
that the 097 plan reserved for Stage 4; no other approval is implied.

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
  130,882 bytes (010: 19,502; largest fragment 070: 19,250 is unchanged). No ninth
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
- Local results are listed in the archive's Patch/CHANGES.md. CI has not run for
  this change.

## Limits

No authenticated live-server, human visual, screen-reader or exhaustive
accessibility verification is claimed. Deliverable 2 (connection-loss/recovery,
background-polling deduplication, field association) is untouched and remains open.
`lairActionModal` still lives inside `<main>` and is therefore inert while the
Encounter tools dialog is open; it cannot be opened from inside that dialog, so
behaviour is unchanged.
