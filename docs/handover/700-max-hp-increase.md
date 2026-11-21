# 700 - Max HP increase; current HP follows (SG-TODO-025 and 026)

[Back to HANDOVER index](../../HANDOVER.md)

Implementation group 3, second item, on `features/claude`, 2026-11-21. Decisions:
[250](../todo/250-max-hp-increase.md#decisions-2026-11-21) and
[260](../todo/260-current-hp-follows-max-increase.md#decisions-2026-11-21).
SG-TODO-024 before it: CI 44932574915 green on d1fbf41.

## Model (`python/scrying_glass_statistics.py`)

- New mechanical kind `max_hp_increase` (`MAX_HP_INCREASE`), stored in the existing effect
  columns (`reduction_stat`/`reduction_amount`, no constraint, no migration). Reductions keep
  their validation unchanged.
- `normalize_statistics`: `max_hp = min(MAX_STORED_HP, max(0, base - reductions + increases))`.
- `increase_max_hp(item, amount, source_id)`: refuses untracked characters, dead creatures
  (a monster at 0 HP is dead) and results above `MAX_STORED_HP`; adds the "Max HP increase"
  effect and raises current HP by the amount. A downed character above 0 HP is standing again
  (death saves cleared) through `normalize_features`.
- `restore_stat('max_hp')` (and `'all'`) also removes increases; current HP is only capped.
  Removing a reduction still never raises current HP (5e).
- `legacy_max_edit`: with active reductions or increases, the Edit dialog must keep the
  effective maximum (message now "Active Max HP reductions or increases: ...").
- `follow_max_increase(before, candidate, hp_given)`: when the maximum rises and current HP
  was not set, current HP rises by the same amount (capped). Skipped for dead creatures and
  untracked characters.

## Paths

- Battle Actions: new row action `increase-max-hp` (`BattleActionRow`), validated on a copy
  in the validation pass like reductions (so a refused row applies nothing), allowed on a
  downed target, logged as `max-hp-increased` with the statistics note
  ("Goblin: Max HP 12 → 17; HP 12 → 17; source: Cleric"). A raised target re-enters the
  battle order.
- Edit dialogs: `update_character`, `update_monster`, the multipart `edit_monster` and the
  active `InitiativeEditMonstersMixin.edit_monster` call `follow_max_increase`; "current HP
  given" means it differs from the stored value (the dialogs always send it).
- Refresh from source (`scrying_glass_monster_refresh_review.apply_monster_refresh`): max-only
  refresh counts as an increase; the health reconciliation check uses the followed value.
  The unused `prepare_refresh` in `scrying_glass_monster_refresh.py` is unchanged.
- Statblock import/apply does not change a monster's maximum HP (the Edit form carries the
  live values), so it is covered by the Edit dialog path.

## Admin

- New `static/max-hp-increase.js`: "Add Max HP increase" after "Add statistics reduction";
  targets are active, not dead and HP-tracked; `actionAmountRequired` is extended.
- `static/statistics.js` (v=3): Max HP is listed while it has an increase, shown as
  "0 (increase +5)" in the Reduction column; texts mention increases.

## Validation (local)

- New `tests/test_max_hp_increase.py`: 7 rule tests, 3 endpoint tests (real SQLite: Battle
  Actions with persistence and log note, downed target and refused mixed batch, Edit
  dialogs), 2 refresh tests through the secured route (skip without FastAPI, run in CI) and
  1 browser test of the Battle Actions row.
- Full unittest suite: 2,124 tests, no new failures against the baseline in this sandbox;
  Node tests for the touched scripts as before; connection check clean.
- CI and the user's check are pending; e2e runs at the end of group 3.
