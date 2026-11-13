# 620 - Character and Monster Edit modal layout

[Back to HANDOVER index](../../HANDOVER.md)

User-reported fix, 2026-11-13, delivered on `features/perplexity-021` (not part of SG-TODO-021; no TODO ID assigned). User instruction: "I found some layout issues (not related to 021 but I would still liked them fixed here) in the Character edit and Monster edit modals".

## Requested

1. The asterisk that marks a required field was on the next line instead of directly after the label.
2. The initiative bonus help text in the Monster Edit modal can be removed.
3. The Initiative bonus label should read "Initiative bonus (Leave blank for 0)".

## Changes

- `static/admin/020-source.js` (`monsterEdit`, `characterEdit`): each required label's text and its `.required-marker` are wrapped in one `<span>`. Edit labels are CSS grids, so the bare text and the marker used to become two grid rows. The fragment is 18,770 bytes (limit 20,000); the 8 fragments are unchanged in number and order.
- `static/monster-initiative-edit.js` (cache version `?v=2` to `?v=3` in `templates/admin/190_document_end.html` and the README asset list):
  - the label is now "Initiative bonus (Leave blank for 0)";
  - the `#editMonsterBonusHelp` paragraph and the `aria-describedby` links to it are removed;
  - behaviour change to match the new label: a blank bonus is now saved as 0. Before, blank kept the assigned bonus. An unchanged value is still omitted from the request, so the assigned bonus and its origin are kept. If the assigned bonus is already 0, a blank field is treated as unchanged.
- `static/admin.css` (`.edit-form label`): a single `minmax(0, 1fr)` column, `align-content: start` and `min-width: 0`; inputs and selects are limited to `max-width: 100%`. At 375 px, the longer label was cut off and the text inputs (Name, Monster species, Initiative bonus) extended past their column. That overflow already existed before this change. Wide layouts look the same.

## Tests changed

- `tests/test_monster_bonus_edit_ui.py`: the cache version is `v=3`. An unchanged bonus is not sent, and a blank bonus is sent as `0`. The new label exists and the help paragraph is gone. With `static/admin.css` loaded, each required marker sits on the same line as its label text in both modals at 375 and 1440 px. Against the old markup, this check fails.
- `tests/monster-edit-feedback.test.cjs`: the transport test expects blank to be sent as `0` and an unchanged value to be omitted.

## Validation (local, this sandbox)

- Passed: `tests/test_monster_bonus_edit_ui.py`, `tests/test_admin_source.py`, `tests/test_admin_asset_wiring.py`, `tests/test_compact_combatant_inputs.py`, `tests/test_asset_cache_busting.py`, `tests/test_statistics_layout.py`; `node --test` for `monster-edit-feedback`, `character-edit-feedback`, `setup-new-feedback`, `setup-operations-feedback`; e2e `test_rosters.py` in Chromium (8 passed).
- Not passing locally, with or without this change (sandbox environment, not caused by it): `tests/test_admin_global_feedback_composition.py` (5 tests time out in `wait_for_function`) and `tests/test_lair_pane_visibility.js` (exit 1). CI is the reference for these.
- Screenshots of both modals at 375 and 1440 px were checked by eye.
- No CI runs on `features/perplexity-021`. User acceptance pending.
