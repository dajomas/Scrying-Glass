# 240 - Optional character HP tracking

[Back to TODO index](../../TODO.md)

## Task and status

SG-TODO-024 - implemented 2026-11-21 on `features/claude` ([handover 690](../handover/690-character-hp-tracking.md)); CI and user check pending. Decided 2026-11-21, implementation group 3 (first item). Requested by the
user 2026-11-20.

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

## Decisions (2026-11-21)

1. Scope: per character. A "Track HP" checkbox in Add character and in the Edit dialog,
   on by default (existing characters keep today's behaviour), plus "Track HP" and
   "Do not track HP" in the character bulk actions. Stored per character, no migration.
2. Default: enabled.
3. Display: for an untracked character the HP fields and bars are hidden in the Admin and
   on the Client Display, and HP is not required in Add character. Stored HP values are
   kept, so switching tracking back on resumes from them.
4. Damage and healing on an untracked character never change current, maximum or
   temporary HP; the DM sets life state and death saves by hand, with no automatic
   transition from HP (assumed: the user left this question unanswered and the recommended option was taken; open to change).
5. The damage or healing amount is still recorded in the activity log (assumed: the user left this question unanswered and the recommended option was taken; open to change).
6. Switching off and on again keeps the stored values (see 3).
7. Temporary HP is not tracked for untracked characters either (see SG-TODO-027).

## Open decisions as proposed (2026-11-20)

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
