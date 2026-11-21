# 270 - Temporary hit points option

[Back to TODO index](../../TODO.md)

## Task and status

SG-TODO-027 - implemented 2026-11-21 on `features/claude` ([handover 710](../handover/710-temporary-hp-grant.md)); CI and user check pending. Decided 2026-11-21, implementation group 3 (last item). Requested by the
user 2026-11-20; the user asked for the D&D 5e rules to be checked.

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

## Decisions (2026-11-21)

1. Granting temporary HP is offered in Battle Actions, per target, next to damage and
   healing (not in bulk actions). The Encounter tools "Set temporary HP" field stays for
   corrections.
2. No stacking: by default the creature keeps the higher value; a "replace" option takes
   the new value even when it is lower (assumed: the user left this question unanswered and the recommended option was taken; open to change).
3. No duration: temporary HP last until damage uses them up or the DM clears them; End
   battle leaves them.
4. Characters with HP tracking off get no temporary HP tracking.

## Open decisions as proposed (2026-11-20)

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
