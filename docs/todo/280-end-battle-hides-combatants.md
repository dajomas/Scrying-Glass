# 280 - End battle hides combatants

[Back to TODO index](../../TODO.md)

## Task and status

SG-TODO-028 - proposed, requested by the user 2026-11-20. No owner, priority or
deadline has been agreed.

## Request

When the End battle button is clicked, visibility is switched off for all monsters
and characters.

## Current behaviour (code at 2d506f39260b5658f96479ec5b6f9519609724ae)

- `battle_end` in `python/scrying_glass_admin_battle.py` clears turns, the round and
  the battle order, and saves the campaign characters. It does not change visibility.
- Reset all already sets lairs to not visible.
- `sync_health` in `python/scrying_glass_feature_rules.py` forces a creature that is
  not alive to `visible = True`. A later health update could make a hidden dead or
  downed creature visible again, so the implementation has to take this into account.

## Open decisions (to agree before implementation)

1. Whether lairs are hidden too. Proposed: yes, matching Reset all.
2. Whether dead or downed creatures stay hidden after End battle until the DM shows
   them, despite the `sync_health` rule.

## Acceptance criteria (proposed)

- After End battle, no monster or character is visible in the Admin or on the Client
  Display, and the visibility change is saved for the campaign characters.
- Nothing else about End battle changes.
- The Client Display updates without a reload.

## Validation requirements

Unit/API test of `battle_end` with visible, hidden, dead and downed combatants;
an e2e check of the Client Display after End battle. Changes to code or tests run
CI normally.
