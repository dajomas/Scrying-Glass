# 670 - Implementation group 1: quick wins (SG-TODO-028 to 032)

[Back to HANDOVER index](../../HANDOVER.md)

User request, 2026-11-21, on `features/claude`: "start with group 1". Decisions for 028 and
029 are in their task files ([280](../todo/280-end-battle-hides-combatants.md),
[290](../todo/290-distinct-monster-color.md)).

## SG-TODO-028 - End battle hides combatants

- `battle_end` (`python/scrying_glass_admin_battle.py`) sets `visible = False` on every
  monster, character and lair and marks each monster and character with
  `hidden_at_battle_end` (stored in the generic `<table>_attributes`, no migration).
- New helpers in `python/scrying_glass_feature_rules.py`: `reveal_if_down` (the old "not alive
  is visible" rule, skipped while the mark is set), `hide_at_battle_end` and
  `release_battle_end_hiding`. `sync_health`, `update_alive_state`, the HP edit paths in
  `scrying_glass_statistics_service.py` and `scrying_glass_service_features.py`, and both edit
  handlers use `reveal_if_down` instead of forcing `visible = True`.
- So dead or downed creatures stay hidden after End battle. The mark is removed when the GM
  changes visibility by hand (edit or bulk), on Reset, and when the next battle starts; from then
  on the usual rule applies. Before the first battle nothing changes.

## SG-TODO-029 - Distinct default monster color

- New `python/scrying_glass_monster_palette.py`: 12 colours (all at least 4.9:1 with white
  text), `next_monster_color` (first colour no monster uses, else the least used one, palette
  order breaks ties; characters do not count) and `fill_missing_colors`.
- CSV import: rows without a colour get the next default, counting the rows before them
  (`csv_monster` no longer falls back to `#842029`).
- Admin: new `static/monster-default-color.js` with the same palette sets the Add Monster and
  Import .monster colour after every state load (hook `window.scryingMonsterColorState` in
  `static/admin/030-source.js`), so after page load, every add and every setup change. A colour
  picked by hand is kept until that form is reset; reset restores the computed default.
- Quantity > 1 (user finding 2026-11-21, after the first push): while the form shows the
  computed default it sends `color_auto=true` (hidden field kept by the script). Then the first
  copy keeps the shown colour and each further copy gets the next palette colour
  (`spread_copy_colors`, in `create_monster` of both mixins and in `import_monster`). A
  hand-picked colour sends no flag and stays on every copy.
- Unchanged: the `#842029` fallback in `scrying_glass_service_state.py` for stored monsters
  without a colour, and existing monsters keep their colours.

## SG-TODO-030 - HP help folded

`#monsterHpRangeHelp` is now a `div` (the old `p` around a `ul` was invalid HTML) and
`static/admin-panel-forms.js` moves it into a closed "How to enter HP" disclosure as the last
item of the Combat statistics group. Text and `aria-describedby` are unchanged.

## SG-TODO-031 - Refresh from source above Remove

`static/monster-refresh-review.js` inserts Refresh from source before Remove;
`monster-source-image.js` and `monster-statblock-bulk.js` insert their actions before Refresh
from source, so Remove stays last and Refresh from source sits directly above it.

## SG-TODO-032 - Clear selection next to Select all

`static/admin-rosters.js` places Clear selection right after Select all in both rosters:
count, Select all, Clear selection, Bulk.

## Cache busting

`admin-panel-forms.css?v=3`, `admin-panel-forms.js?v=2`, `admin-rosters.js?v=2`,
`monster-default-color.js?v=2` (new), `monster-refresh-review.js?v=3`,
`monster-source-image.js?v=5`, `monster-statblock-bulk.js?v=2`.

## Validation (local, this sandbox)

- New tests: `tests/test_end_battle_visibility.py` (7), `tests/test_monster_default_color.py`
  (11, includes the CSV import and quantity adds through the handlers), `tests/test_group1_admin_ui.py` (4 browser
  tests for 029-032). Version expectations updated in `test_admin_rosters.py` and
  `test_admin_panel_forms.py`.
- Full suite through `tools/run_split_tests.py`: 2090 tests; the same 92 failures/errors as the
  unchanged baseline (2072 tests) in this sandbox, which lacks FastAPI and other runtime parts;
  no new failures.
- `begin_battle` removes the mark inline (no import), because legacy tests run that method
  extracted from its module.
- First push 9491da6: CI 44885862376 failed only the connection audit of
  `test_statblock_import_workers.py`: on `features/claude` (no `monsters_examples`)
  `CapturedProviderWorkerTests.setUp` skipped after the fixture opened SQLite, so tearDown never
  closed it. The skip now comes first.
- User finding after the first push: copies of a quantity add all got one colour; fixed in
  13d36ef (see SG-TODO-029 above).
- CI 44888887657 green on 13d36ef. E2E 20261121T150318Z on 2cf5bc6: 133 passed, 0 failed,
  4 skipped (the statblock-import tests, because `monsters_examples` was briefly off the
  branch; the user has put it back).
- User checked 028, 030, 031, 032 and the 029 fix. Group 1 completed and closed 2026-11-21.
