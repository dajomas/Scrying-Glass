# Corrected damage and death-save logic

This overlay supersedes the mistaken negative-MAX_HP death rule from the earlier turn patch.
It targets the supplied encounter-feature, logging, tidy-layout and campaign-backup patches.
Keep the existing schema-v5 storage, logging service/helper and scoped layout/backup assets.
The two ports and the database schema are unchanged.

## Damage events

HP is never retained below 0. Each incoming damage event is resolved independently:

- Consume temporary HP first unless the explicit bypass is selected.
- Calculate excess damage beyond current HP before clamping current HP to 0.
- For characters, excess damage equal to or greater than maximum HP causes instant death.
- Dropping from positive HP to 0 without lethal excess causes downing, not a failed save.
- Damage received when already at 0 HP causes one failed death save.
- A critical hit at 0 HP causes two failed saves instead; counts cap at 3.
- Three failures mark the character dead and remove their initiative turn.
- Damage to a stable character ends stability and starts a fresh failure tally.
- Healing above 0 and stabilization reset the death-save tally.
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
Ordinary actions remain restricted to standing actors; downed characters still receive turns
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
review that record and explicitly correct maximum HP/life state/counters: this overlay cannot
reliably distinguish a mistaken mark from an intentional GM mark. Restore a known-good checkpoint
or undo when appropriate; retained audit history can help identify what happened.

Downed/stable active characters retain turns. Instant death, three failures or an explicit dead
state exclude them. The existing turn save/restore fixes are included. Previously removed order
positions might need a one-time manual rebuild. Undo/checkpoints preserve the new HP/counters
using the existing feature storage; old snapshots with negatives normalize when restored.

## Install

1. Stop the service and back up source and storage.
2. Extract this ZIP at the application root, preserving paths and replacing included files.
3. Restart and hard-refresh the administration browser.
4. Test the 25-maximum-HP examples on disposable combatants.
5. Check a downed character's next turn, critical-hit failures, healing and restart.

No schema upgrade or data deletion is performed. The footer fragment retains admin.js,
features.js and the prior campaign-backups relocation script and adds damage-preview.js.
The existing scoped CSS links and the moved Campaign backups panel are not replaced.
If your footer is locally customized, merge the new asset links instead of overwriting it.

## Validation

30 focused damage tests and 8 turn tests passed (38 total). They cover threshold equality,
excess calculation, HP clamping, ordinary/critical zero-HP hits, third-failure death, temporary
HP and bypass, stability, healing, legacy negative normalization, models, the actual battle and
character-update functions, turn order/round wrap and saving a zero-HP active turn with real SQLite.
The restart fixture uses the uploaded scalar storage baseline and omits empty effects; it is
not a full schema-v5 effects integration run. Installed feature storage is not replaced here.

All changed Python files compile; Node syntax checks passed for changed/new JavaScript. Node VM
checks passed for the pure damage preview. ZIP integrity is checked. Live browser, HTTP/WebSocket,
and the entire encounter-feature regression suite have not been run in this environment.
The earlier turn test file is replaced because its negative-max-HP expectations were incorrect.

    python -m unittest discover -s tests -p 'test_damage_logic.py'
    python -m unittest discover -s tests -p 'test_turn_eligibility.py'

Rules are implemented as described here, without automatically inferring critical hits from
proximity or conditions, rolling death saves, or handling every resurrection/nonlethal exception.
