# 710 - Temporary HP in Battle Actions (SG-TODO-027)

[Back to HANDOVER index](../../HANDOVER.md)

Implementation group 3, last item, on `features/claude`, 2026-11-21. Decisions:
[270](../history/270-temporary-hit-points.md#decisions-2026-11-21). SG-TODO-025/026 before it:
CI 44936112445 green on eb8f91e.

## Rule

- `grant_temp_hp(item, amount, replace=False)` in `python/scrying_glass_feature_rules.py`:
  5e no stacking. By default the higher of the current and new value is kept; `replace` takes
  the new amount. Not healing: HP, life state and death saves are untouched, also at 0 HP.
  Refused for untracked characters (SG-TODO-024) and dead creatures; amount 1-99,999.
- Unchanged: damage uses temporary HP first; healing never changes them; a hit at 0 HP still
  fails a death save even when temporary HP absorb it (documented in the User Guide); the
  Encounter tools "Set pool" field still overwrites for corrections; Reset clears them; End
  battle leaves them (no duration, as decided).

## Battle Actions

- `BattleActionRow.action` accepts `temp-hp` (keep higher) and `temp-hp-replace`. The
  validation pass checks each row on a copy, so a refused row applies nothing; reactions keep
  damage/healing only; an amount is required. Allowed on a downed target.
- Logged as `temp-hp` with the note "Goblin: Temporary HP 6 → 6 (kept higher); source: Cleric"
  (`granted`, `kept higher` or `replaced`).
- New `static/temp-hp-grant.js` adds "Temporary HP (keep higher)" and "Temporary HP (replace)"
  to target rows (not reaction rows) and extends `actionAmountRequired`; the existing payload
  builder sends them unchanged.

## Validation (local)

- New `tests/test_temp_hp_grant.py`: 4 rule tests, 3 endpoint tests (real SQLite: keep higher
  then replace with log notes and persistence; downed target and refused mixed batch; missing
  amount; reactions) and 1 browser test of the Action choices and request.
- Full unittest suite: 2,132 tests, no new failures against the baseline in this sandbox;
  Node tests for the touched scripts as before; connection check clean.
- CI 44937558587 green on f794d67.

## Close-out

Group 3 completed and closed 2026-11-21: CI 44937558587 green on f794d67 (both jobs);
the user's e2e run 20261121T184951Z on f794d67: 137 passed, 0 failed, 0 skipped
(Chromium and Firefox). The results push was first rejected because a CI publish commit
had landed during the run; the user merged and pushed them (9825ea5).
