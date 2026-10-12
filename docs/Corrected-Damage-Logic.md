# Damage and death-save logic

Documented baseline: `features/development` at `4f401b4adfca92e9c9599aea8924c14efb49aea4`.

Current behavior of the shared HP helper, battle rows, inline HP deltas and encounter health tools. Schema v6 is documented in [SQLite Migration](SQLite-Migration.md).

## Damage events

HP is never retained below 0. Each incoming damage event is resolved independently:

- Consume temporary HP first unless the explicit bypass is selected.
- Calculate excess damage beyond current HP before clamping current HP to 0.
- For characters, excess damage equal to or greater than maximum HP causes instant death.
- Dropping from positive HP to 0 without lethal excess causes downing, not a failed save.
- Damage received when already at 0 HP causes one failed death save.
- A critical hit at 0 HP causes two failed saves instead; counts cap at 3.
- Three failures mark the character dead and exclude the character from future turns. An unresolved current turn can remain owned until Next, allowing applicable reactions.
- Damage to a stable character ends stability and starts a fresh failure tally.
- Healing is capped at maximum HP; healing above 0 and stabilization reset the death-save tally.
- Explicitly dead characters are not resurrected by ordinary healing.
- Monsters do not accumulate death saves and are excluded from turns at 0 HP.

Temporary HP does not make a zero-HP character standing/stable or prevent a failed save from
an incoming damaging hit. It can reduce the excess damage reaching real HP for the massive-
damage calculation. Damage values must already incorporate resistance, mitigation and any
critical-hit damage dice; the Critical hit flag does not double the number entered.

Example, maximum HP 25, no temporary HP:

| Current HP | Damage | Stored HP | Outcome |
|---|---|---|---|
| 10 | 10 | 0 | Down, no failed save from the initial drop |
| 10 | 34 | 0 | Down, excess 24 |
| 10 | 35 | 0 | Instant death, excess 25 |
| 0 | 1 | 0 | One failed save |
| 0 | 24 | 0 | One failed save |
| 0 | 25 | 0 | Instant death |

Negative current HP is not accumulated across attacks. Maximum HP remains nonnegative and is
NOT a death marker. Incoming negative stored HP/max-HP values are rejected by update models;
CSV HP input must also be nonnegative. Signed hp_delta remains the damage/healing input.
Absolute HP corrections are NOT interpreted as attacks: use damage actions or negative deltas
when damage-triggered failures or massive death should be applied.

## Coverage across interfaces

The shared helper is used by battle action rows, inline HP deltas and the Encounter tools HP
change control. Battle actions now accept active downed characters as damage targets.
Ordinary actions remain restricted to standing actors; reaction damage/healing rows use their own active source, including down/dead sources; downed characters still receive turns
for manually rolled death saves. The critical-hit checkbox is in each battle damage row, and
critical_hit is also available for CharacterUpdate/MonsterUpdate API damage-delta requests.
The Encounter tools generic HP control and inline Damage button default to noncritical damage;
use the battle row critical checkbox or explicit API flag for a critical hit.

Battle damage logs include failed-save/instant-death events with descriptions. Existing feature
HP controls retain their readable change logging through the previous logging patch. The UI
preview clamps HP to 0 and explains the predicted downing, failed save or instant death.
The server is authoritative if another admin changes state between preview and submission.

## Existing state and undo

Legacy negative stored HP is normalized to 0 on loading. No historical damage is reconstructed,
and no automatic failure is inferred from that normalization. Legacy negative maximum HP is
normalized to 0, NOT used to infer death. If the mistaken patch already marked someone dead,
review that record and explicitly correct maximum HP/life state/counters: the application cannot
reliably distinguish a mistaken mark from an intentional GM mark. Restore a known-good checkpoint
or undo when appropriate; retained audit history can help identify what happened.

Downed/stable active characters retain turns. Instant death, three failures or an explicit dead
state exclude them. The existing turn save/restore fixes are included. Previously removed order
positions might need a one-time manual rebuild. Undo/checkpoints preserve the new HP/counters
using the existing feature storage; old snapshots with negatives normalize when restored.

## Checks and rule boundaries

```bash
python -m unittest discover -s tests -p 'test_damage_logic.py'
python -m unittest discover -s tests -p 'test_turn_eligibility.py'
python -m unittest discover -s tests -p 'test_healing_max_hp_cap.py'
python -m unittest discover -s tests -p 'test_battle_reactions.py'
```

These are validation commands, not a claim that this documentation update ran the application suite. Critical hits are not inferred from proximity or conditions. Death saves, dice, resistance, immunity and resurrection exceptions remain GM-adjudicated. See [User Guide](User-Guide.md) for start-of-turn inputs and reactions.
