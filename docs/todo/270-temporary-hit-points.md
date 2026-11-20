# 270 - Temporary hit points option

[Back to TODO index](../../TODO.md)

## Task and status

SG-TODO-027 - proposed, requested by the user 2026-11-20. No owner, priority or
deadline has been agreed. The user asked for the D&D 5e rules to be checked.

## Request

Add an option for temporary HP, following the D&D 5e rules.

## Current behaviour (code at 2d506f39260b5658f96479ec5b6f9519609724ae)

Temporary HP already exists in part:

- Every combatant stores `temp_hp` (0-99,999), reset to 0 by Reset.
- Damage uses temporary HP first (`apply_hp` in
  `python/scrying_glass_feature_rules.py`); an `absorb_temp` flag lets the DM skip it.
- Encounter tools has a "Set temporary HP" field that overwrites the value
  (`static/features.js`).
- Battle Actions and the Client Display show the value.
- There is no temporary HP control in Battle Actions or the bulk actions, and the
  existing control does not apply the no-stacking rule.

## D&D 5e rules to follow (2014 SRD, unchanged in 2024)

- Temporary HP are a buffer, not real HP: damage removes them first and any leftover
  damage carries over to HP.
- Healing cannot restore temporary HP, and gaining them is not healing.
- They do not stack. When a creature with temporary HP gains new ones, it keeps the
  current amount or takes the new amount; it never adds them.
- They cannot be added to HP and are not limited by maximum HP.
- At 0 HP, gaining temporary HP does not restore consciousness or stabilise the
  creature, but the temporary HP can still absorb damage.
- Unless the source gives a duration, they last until used up or until a long rest.

## Open decisions (to agree before implementation)

1. Where the option goes: Battle Actions (per target, next to damage and healing),
   bulk actions, or both. The existing Encounter tools field stays for corrections.
2. Applying the no-stacking rule: ask the DM to keep or replace, or default to the
   higher value with an override.
3. Whether to support a duration (rounds, until end of battle) or leave clearing to
   the DM. There is no long-rest concept in the app today.
4. Characters with HP tracking disabled ([SG-TODO-024](240-character-hp-tracking-option.md)):
   proposed, no temporary HP tracking either.

## Acceptance criteria (proposed)

- The DM can grant temporary HP to one or more targets during battle.
- Granting never adds to existing temporary HP; the agreed keep/replace rule applies.
- Healing never changes temporary HP; damage uses temporary HP first (current behaviour).
- Granting temporary HP to a creature at 0 HP does not change its life state or death saves.
- The change appears in the activity log with the resulting value.

## Validation requirements

Unit tests for granting (empty, higher, lower, at 0 HP, dead) and for damage and
healing with temporary HP; Admin behaviour and e2e tests for the new control.
Changes to code or tests run CI normally.
