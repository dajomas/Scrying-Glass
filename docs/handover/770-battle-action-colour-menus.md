# 770 - Colour markers in the Battle Actions menus; Increase Max HP

[Back to HANDOVER index](../../HANDOVER.md) · [690-710 HP rules](700-max-hp-increase.md)

User request, no TODO ID, 2026-11-23 on `features/claude`: "add the color markers in the
source and target drop down menus in the Battle actions modal … remove the Current HP
notification in the Add Max HP increase pane and rename the Add Max HP increase button to
Increase Max HP". Decision (user, 2026-11-23): a custom menu that shows the dot in the closed
menu and in every entry, since a native menu cannot show it per entry.

## Changes

- `static/battle-action-menus.js` and `.css` (new, loaded after the statistics summaries in
  `templates/admin/190_document_end.html`): every `select[data-action-target]` and
  `select[data-action-source]` in `#battleActionRows` (action, reaction, statistics
  reduction, Max HP and temporary HP rows) gets a select-only combobox in front of it. It
  shows the chosen combatant's colour dot (the battle-order `turn-marker`; `#ffffff` when a
  combatant has no colour, a dashed empty dot before a choice) and lists every entry with
  its dot. Mouse, arrow keys, Home/End, Page Up/Down, Enter/Space and type-ahead work;
  Escape closes only the menu (it stops the event before the dialog's Escape handler).
- The native select stays the source of truth: choosing sets its value and fires `input`
  and `change`, so the apply code, row locking, the statistics summary and the tests are
  unchanged. The menu follows the select's value, options, `disabled` and
  `aria-describedby` (the HP/AC summary), and recolours on every state refresh. The select
  is visually hidden, `aria-hidden` and out of the tab order, so the combobox (with the
  select's name, Target or Reaction source) is the only control a user meets.
- A required menu left empty: the native validation bubble would point at the hidden
  select, so it is suppressed; the menu is marked invalid, focused, and the modal notice
  says "Choose a target for every row." Nothing is sent.
- `static/max-hp-increase.js`: the button is "Increase Max HP"; the row no longer shows
  "Current HP rises by the same amount …". Behaviour is unchanged (current HP still rises).
- Tests: `tests/test_battle_action_menus.py` (new, 5 tests); the layout checks in
  `test_battle_action_alignment.py` and `test_battle_action_statistics.py` measure the
  visible menu instead of the hidden select; `test_max_hp_increase.py` checks the new
  label and the missing note.
- User Guide: the menus and the new button name.

## Evidence

- Full unittest suite here: 2,165 tests, the same known FastAPI failures as before;
  Node: 84 files, all pass; connection audit: 260 modules, the same failures and connection
  counts as before.
- Screenshot check of the modal with a menu open (dark theme): dots in the closed menus and
  the list, the highlighted entry readable.

## Correction - 2026-11-23

Reported by the user after 4d45f0a (CI 45213572798 green): the list disappeared below the
edge of the Battle Actions modal, and scrolling the modal with its scrollbar closed it.

- The list is now fixed to the viewport, so the modal's scrolling box no longer cuts it
  off. It opens below the menu, or above it when there is more room there; its height is
  limited to the room available (at least 80 px, at most 16rem).
- It follows its menu while the modal (or the page) scrolls or the window resizes, and
  closes when the menu scrolls out of the modal's view. Scrolling inside the list itself
  is left alone.
- A press on a scrollbar no longer counts as a click outside the menu.
- `test_list_stays_visible_at_the_modal_edge_and_while_scrolling`: a short window with ten
  extra combatants; the list of the last row opens upwards, lies fully in the window and on
  top; it stays attached while the modal scrolls; a scrollbar press keeps it open (the press
  is dispatched in the scrollbar strip, because Playwright's headless Chromium hides
  scrollbars), a press elsewhere closes it, and scrolling the menu out of view closes it.
  Both faults (no scrollbar check; the list positioned inside the modal) fail this test.
