# Lair actions

Implemented against the supplied features/development snapshot caa4b47.

## Using a lair

1. In the Lair section below the battle controls, enter a name, color and optional private DM notes.
2. Choose In battle and Visible to players, then Add lair.
3. Start the encounter normally. The server inserts the lair at initiative 20 after every tied creature.
4. At the lair turn, click Resolve lair action or click the highlighted lair in the admin initiative order.
5. Select any combination of active characters and monsters (including ally monsters). Permanently dead creatures and the lair itself are excluded.
6. Enter damage and comma-separated condition names. Copy defaults to selected targets, then adjust individual rows for saves, resistance or immunity.
7. Choose condition visibility and expiry, then Apply to selected targets and review the confirmation.
8. Click Next Turn normally. Resolving an action does not advance the turn automatically.

One lair is supported per encounter. The lair has no HP, AC, death state or condition list, and cannot receive damage/healing/conditions. Initiative is server-owned and fixed at 20. Effects use the existing combatant-effects model; names are labels/reminders, not automated rules.

## Damage and conditions

Damage must be an integer from 0 through 99999. A target may receive damage, conditions, or both. At least one is required per selected target. Each target may receive up to 20 new conditions, subject to the existing total limit of 100 effects. The batch supports 1-100 distinct targets.

Saving throws, damage types, resistances, vulnerabilities and immunities are adjudicated by the DM before entry. Existing temporary HP, zero-HP death-save and instant-death behavior is reused. Lair damage is not treated as a critical hit. Damage to a concentrating creature produces a reminder; losing its standing state triggers existing concentration reconciliation.

Conditions default to private. Public conditions appear on the player display; DM notes and effect notes are not exposed there. Remove or edit conditions using the existing encounter effect tools.

UI expiry choices:
- Manual removal.
- Start of the next lair turn (one start boundary at the lair).
- End of the target's next turn (one end boundary at that target).

The API also accepts existing start/end anchor counters. Turn-boundary counters follow the application's existing semantics; manually selecting a turn does not itself expire effects.

Removing a lair leaves already-applied conditions in place, clears their lair source, and converts lair-anchored expiry to manual. Disabling a lair preserves its source and anchors; those counters do not expire while that lair has no turns. Remove or adjust them manually if appropriate.

## Ordering and lifecycle

Creature initiative ties remain in the DM-selected order. With a lair present in battle order, stable initiative sorting enforces descending initiative and places the lair after all creatures at 20. This also repairs placement after initiative edits. Creature-only encounters retain their previous manual ordering behavior.

Adding or enabling a lair mid-battle inserts it without changing the current turn. If initiative 20 has already passed, the entry is reached in the next round. Disabling or removing the current lair preserves successor information for the next turn. A lair can be the only active participant, allowing an environmental encounter.

Ending battle clears its current turn without removing the lair. Reset All disables and hides the lair without deleting its configuration. The generic single-combatant reset endpoint rejects lairs. As with existing participants, entering a turn makes that participant visible.

## Storage and recovery

Schema version 6 introduces a typed lairs table owned by encounters, not campaign character rosters. Startup upgrades existing databases, using the existing migration backup mechanism. IDs and fields survive runtime restart, setup saves/loads, undo, checkpoints and campaign bundles. Saved-setup loading clears historical current-turn flags and resets the round as before.

Lair creation, updates, removal and action application participate in existing transaction rollback, revision tracking, undo and post-commit broadcasts. Action submissions require a current revision. If another operation changes the encounter while the action modal is open, reopen it before submitting.

## API

All routes are admin-port-only and use existing admin authentication, same-origin checks and serialized database transactions.

- POST /api/lairs — name, optional notes/color/active/visible.
- PATCH /api/lairs/{id} — name/notes/color/active/visible; initiative updates are rejected.
- DELETE /api/lairs/{id}.
- POST /api/lairs/{id}/actions — action name, current revision and target rows.

Example action body:

```json
{
  "name": "Tremor",
  "revision": 42,
  "targets": [
    {"id": "character-id", "damage": 12, "effects": [{"name": "Prone", "public": true}]},
    {"id": "monster-id", "damage": 6, "effects": []}
  ]
}
```

Condition fields: name, notes, public, timing, turns, anchor_id. Source is forced to the acting lair and concentration is forced false. Manual conditions omit turns/anchor_id. Timed conditions require timing=start/end, a positive integer turns counter and an existing active anchor. The lair must currently own the turn. Every target is validated before any target changes are committed.
