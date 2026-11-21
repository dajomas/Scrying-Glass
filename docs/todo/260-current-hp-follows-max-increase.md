# 260 - Current HP follows a maximum HP increase

[Back to TODO index](../../TODO.md)

## Task and status

SG-TODO-026 - proposed, requested by the user 2026-11-20. No owner, priority or
deadline has been agreed. Depends on [SG-TODO-025](250-max-hp-increase.md) for the
in-battle increase; the other paths below can be done independently.

## Request

Whenever maximum HP increases, however this happens, current HP increases by the
same amount. This applies to monsters, and to characters when character HP
tracking ([SG-TODO-024](240-character-hp-tracking-option.md)) is enabled.

## Paths that increase maximum HP (code at 2d506f39260b5658f96479ec5b6f9519609724ae)

- The new in-battle increase from SG-TODO-025.
- Raising maximum HP in the character or monster Edit dialog.
- Removing a Max HP reduction through Restore statistics
  (`restore_stat` in `python/scrying_glass_statistics.py`). Today current HP stays
  as it is.
- Monster refresh from a source (`python/scrying_glass_monster_refresh.py`), which
  can change `max_hp`.
- Statblock import or apply that changes a monster's maximum HP (SG-TODO-022).

## Open decisions (to agree before implementation)

1. Restoring a reduction: the user's "regardless of how" includes it, but in the
   D&D 5e rules ending a maximum-HP reduction does not restore lost HP. Confirm
   whether current HP should rise here too.
2. Edit dialog when both current and maximum HP are changed in one save: proposed,
   the values the DM typed win and no extra increase is added.
3. A creature at 0 HP: whether the increase brings a downed character or a monster
   at 0 HP back to standing. Proposed: yes for current HP above 0, except for a
   creature that is permanently dead, which stays dead.
4. Whether monster refresh and statblock import count as an increase or as a
   replacement of the monster's values.

## Acceptance criteria (proposed)

- For each agreed path, current HP rises by exactly the increase in maximum HP,
  never above the new maximum.
- Lowering maximum HP keeps today's behaviour (current HP capped at the maximum).
- Characters with HP tracking disabled are not changed.
- The activity log shows the resulting current and maximum HP.

## Validation requirements

Unit tests for each agreed path, including 0 HP and dead creatures; regression tests
for reductions. Changes to code or tests run CI normally.
