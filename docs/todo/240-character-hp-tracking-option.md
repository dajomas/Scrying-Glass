# 240 - Optional character HP tracking

[Back to TODO index](../../TODO.md)

## Task and status

SG-TODO-024 - proposed, requested by the user 2026-11-20. No owner, priority or
deadline has been agreed.

## Request

Make entering and tracking HP for characters an option. When it is disabled, a
character's HP is not changed when the character takes damage or is healed; the
player manages their own HP.

## Current behaviour (code at 2d506f39260b5658f96479ec5b6f9519609724ae)

- Characters are created with a required HP value, and `max_hp`/`original_hp` are
  derived from it (`python/scrying_glass_admin_characters.py`).
- Damage and healing for every combatant go through `apply_hp` in
  `python/scrying_glass_feature_rules.py`. For characters this also drives temporary
  HP absorption, instant death from excess damage, `down` at 0 HP and death-save
  failures from damage at 0 HP.
- Character current/max HP is shown read-only in the roster and edited through the
  row Edit dialog ([SG-TODO-012](120-character-hp-editors.md)).

## Open decisions (to agree before implementation)

1. Scope of the option: global, per campaign, or per character.
2. Default value. Proposed: enabled, so existing campaigns keep their behaviour.
3. What the Admin shows and asks for when disabled: hide or optionally allow the HP
   fields in Add/Edit character, the roster, Battle Actions and the Client Display.
4. What still happens on damage at 0 HP when disabled: life state, death saves,
   instant death and concentration prompts depend on HP today. Proposed: the DM sets
   life state and death saves manually; no automatic transition from HP.
5. Whether the damage/healing amount is still recorded in the activity log when the
   HP is not changed.
6. What happens to stored HP values when the option is switched off and on again.

## Acceptance criteria (proposed)

- With tracking disabled, damage and healing never change a character's current,
  maximum or temporary HP, from any entry point (Battle Actions, Encounter tools,
  bulk actions, lair actions).
- With tracking enabled, behaviour is unchanged from today.
- Monsters are not affected by the option.
- Characters can be created without entering HP when tracking is disabled.
- The option persists across reloads and restarts.

## Related tasks

[SG-TODO-025](250-max-hp-increase.md) and [SG-TODO-026](260-current-hp-follows-max-increase.md)
apply to characters only when this option is enabled.
[SG-TODO-027](270-temporary-hit-points.md) needs a decision on temporary HP for
untracked characters.

## Validation requirements

Unit tests for `apply_hp` and the character endpoints with the option on and off;
Admin asset/behaviour tests for the changed forms; e2e coverage of damage and
healing on an untracked character. Changes to code or tests run CI normally.
