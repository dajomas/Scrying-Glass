# 250 - Maximum HP increase during battle

[Back to TODO index](../../TODO.md)

## Task and status

SG-TODO-025 - decided 2026-11-21, implementation group 3 (with SG-TODO-026). Requested
by the user 2026-11-20.

## Request

Besides lowering maximum HP, allow maximum HP to be increased during battle. This
applies to monsters, and to characters only when character HP tracking
([SG-TODO-024](240-character-hp-tracking-option.md)) is enabled.

## Current behaviour (code at 2d506f39260b5658f96479ec5b6f9519609724ae)

- Maximum HP can only be lowered in battle, as a manual "Max HP reduction"
  mechanical effect ([SG-TODO-002](020-monster-damage-effects.md)). Reductions are
  stored as effects against `base_max_hp`, and `max_hp = max(0, base_max_hp - total)`
  in `python/scrying_glass_statistics.py`. Restore statistics removes them.
- Lowering the maximum caps current HP at the new maximum.
- `legacy_max_edit` rejects editing the maximum in the Edit dialog while reductions
  are active.

## Decisions (2026-11-21)

1. Model: a separate "Max HP increase" mechanical effect, so the reduction validation
   stays unchanged; reductions and increases combine against `base_max_hp`.
2. Offered in Battle Actions statistics, next to Max HP reduction (not in Encounter tools
   or bulk actions). For characters only while HP tracking is on.
3. An increase lasts until removed by hand or by Restore statistics, like reductions.
   Removing it lowers the maximum and caps current HP, as reductions do.
4. Upper limit: `MAX_STORED_HP`.

## Open decisions as proposed (2026-11-20)

1. Model: a signed mechanical effect (reductions and increases netted against
   `base_max_hp`) or a separate increase effect. Proposed: a separate "Max HP
   increase" effect, so the existing reduction validation stays unchanged.
2. Where it is offered: next to the reduction in Battle Actions statistics, in
   Encounter tools, in bulk actions, or all of these.
3. Whether an increase recovers manually only (like reductions) or can have a
   duration (for example *Aid*: 8 hours).
4. Upper limit (the stored-HP limit `MAX_STORED_HP`).

## Acceptance criteria (proposed)

- The DM can raise a monster's maximum HP during battle and undo it again.
- The same works for a character only while character HP tracking is enabled; the
  control is not offered otherwise.
- Increases and reductions combine correctly, and Restore statistics handles both.
- Current HP follows the increase as described in
  [SG-TODO-026](260-current-hp-follows-max-increase.md).
- The change appears in the activity log with the resulting maximum.

## Validation requirements

Unit tests for the statistics model (increase, reduction, both, restore, limits);
API tests for monsters and for characters with tracking on and off; Admin
behaviour tests and e2e coverage of the new control. Changes to code or tests run
CI normally.
