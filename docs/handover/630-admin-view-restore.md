# 630 - Keep the Admin view after a page reload

[Back to HANDOVER index](../../HANDOVER.md)

User-reported request, 2026-11-14, delivered on `features/perplexity-021` (not part of SG-TODO-021; no TODO ID assigned). User instruction: "When I refresh the admin screen, it loads as if I just logged in, instead of refreshing the page I am working on as is. Can you make it so that after a refresh, the panels that were open remain open? Modals can be closed after a refresh."

## Cause

Every Admin page load ran the start-up layout rules:
- the workflow tabs start on Campaign (`admin-workflow-navigation.js`);
- the first state hides the campaign and character inputs when a campaign is active, and the setup, lair and monster inputs when a setup is active (`admin-initial-visibility.js`);
- an active battle collapses all panels once per page (`updatePaneVisibilityForBattle` in `static/admin/030-source.js`).

Nothing remembered the previous view.

## Change

New `static/admin-view-restore.js?v=1`, loaded last in `templates/admin/190_document_end.html`:

- It saves the selected workflow tab, the open or closed state of the seven panel toggles (campaign, character, battle setup, lair, monster input, character display, monster display) and the workspace scroll position. Saving happens on every change, in `sessionStorage` (key `scryingGlass.adminView.v1`), so the view is kept per browser tab.
- It restores only when the navigation type is `reload` or `back_forward`. A new login, or opening the Admin page by link or URL, still starts with the default view.
- The restore runs right after the first state's `updatePaneVisibilityForBattle`, so it is applied after the start-up and battle collapse rules. Panels are changed through their own toggle buttons; their labels and hidden state stay owned by the existing code. Selecting the tab does not move keyboard focus.
- Dialogs are not saved: Encounter tools, Edit, statistics, battle actions and the other modals are closed after a reload.
- No admin fragment changed (the 8 fragments and the 20,000-byte limit are untouched).

## Tests

`e2e/test_view_restore.py` (3 tests per browser):
- a reload keeps the Battle preparation tab, with the battle setup and monster inputs open and the character display closed;
- during a battle, a reload keeps the Live tab, a reopened character display and a closed monster display, and closes the open Encounter tools dialog;
- opening the Admin page again (not a reload) starts with the default view.

Without the new script, the first two tests fail (checked in Chromium).

## Validation (local, this sandbox)

- `e2e/test_view_restore.py`: 6 passed (Chromium and Firefox).
- E2E files that reload the page (`test_access.py`, `test_campaigns.py`, `test_rosters.py`, `test_initiative.py`, `test_feedback.py`), both browsers, run together with `test_view_restore.py`: 83 passed.
- `tests/test_admin_initial_visibility.py`, `tests/test_admin_asset_wiring.py`, `tests/test_asset_cache_busting.py`, `tests/test_admin_split_runtime.py` and the other wiring tests passed. `node --test` passed for the start, end, reset-all, select-dead and character-edit feedback tests.
- Several full-admin fixture tests time out in `wait_for_function` in this sandbox, with and without this change, and with the same counts:
  - `test_admin_workflow_navigation.py`, `test_admin_panel_forms.py`, `test_admin_rosters.py`, `test_initiative_keyboard_navigation.py`;
  - `test_battle_action_statistics.py` and `test_monster_image_previews.py` together: 11 failed and 4 passed both ways.
  
  CI is the reference for these.
- No CI runs on `features/perplexity-021`. User acceptance pending.
