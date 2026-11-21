# 690 - Optional character HP tracking (SG-TODO-024)

[Back to HANDOVER index](../../HANDOVER.md)

Implementation group 3, first item, on `features/claude`, 2026-11-21. Decisions are in
[240](../todo/240-character-hp-tracking-option.md#decisions-2026-11-21).

## Rule (server)

- `track_hp` is a per-character boolean, stored like other entity fields in
  `characters_attributes` (no migration). Missing means on. Monsters and lairs always track.
- `python/scrying_glass_feature_rules.py`: `tracks_hp(item)`. For an untracked character
  `apply_hp` changes nothing and returns `untracked: True`, and `normalize_features` no longer
  derives life state from HP (no standing at HP > 0, no down at 0, stored HP kept when dead).
- Every damage and healing path goes through `apply_hp`, so Battle Actions, both Edit
  dialogs, Encounter tools and lair actions are covered. Battle Actions and the Edit dialog
  already log the amount; Encounter tools now logs `damage`/`heal` with the note
  "<name>: HP not tracked".
- Encounter tools: setting life state to standing/down/stable no longer moves HP for an
  untracked character; changing its temporary HP is refused (422).
- `reduce_stat`: a Max HP reduction on an untracked character is refused (422 from the
  Battle Actions validation pass, before any row is applied); ability reductions still work.
- `CharacterCreate.track_hp` (default true; HP stays optional, default 1) and
  `CharacterUpdate.track_hp`; the Edit dialog's Alive toggle makes an untracked character
  standing whatever its HP. Bulk actions `track-hp` and `untrack-hp`.
- The Client Display never showed character HP (only life state), so nothing changes there.

## Admin

- Add character: "Track HP" checkbox (on) in Starting statistics; off hides Starting HP and
  leaves `hp` out of the request. New `static/character-hp-tracking.js` also adds the
  checkbox to the character Edit dialog, before Current HP; off hides Current/Max HP and
  `character-edit-feedback.js` sends neither.
- `window.scryingTracksHp(item)` is used by the roster HP cell ("Not tracked"), the damage
  preview, the Battle Actions turn header and target statistics (AC only), and the
  Encounter tools health line ("HP not tracked").
- Bulk list: Track HP and Do not track HP before Remove.
- Cache busting: `admin-panel-forms.js?v=3`, `battle-action-statistics.js?v=2`,
  `battle-turn-actions.js?v=2`, `character-edit-feedback.js?v=2`,
  `character-hp-display.js?v=2`, `character-hp-tracking.js?v=1` (new), `damage-preview.js?v=2`,
  `features.js?v=7`.
- The HP field is hidden and made optional rather than disabled, because the entry forms
  restore saved disabled states after a submit.

## Validation (local)

- New: `tests/test_character_hp_tracking.py` (11: rules, persistence, create, Edit,
  Encounter tools, Battle Actions, bulk) and `tests/test_character_hp_tracking_admin.py`
  (4 browser tests). Version expectations updated in four tests.
- Full unittest suite: 2,111 tests; failures are the same 92 as the unchanged HEAD in this
  sandbox (FastAPI and other runtime parts missing), none new. Node tests for the touched
  scripts pass apart from two that fail on HEAD as well. Connection check clean.
- `edit_features` checks tracking inline, because legacy tests run it extracted from its
  module.
- CI and the user's check are pending; e2e runs at the end of group 3.
