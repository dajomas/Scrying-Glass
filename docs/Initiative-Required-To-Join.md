# Initiative required before joining battle

Characters and monsters must have a whole-number initiative before joining.
Zero and negative initiatives are valid. Empty/unset values are not.

The individual Join Battle button is disabled until the saved initiative is
present; its tooltip explains why. After entering initiative and the normal
state refresh completes, the button becomes available. Existing active
combatants can still leave, including legacy records with missing initiative.

Bulk Join Battle rejects the entire selection if any selected character or
monster has no initiative, naming the missing combatants. Nothing partially
joins. Enter initiatives or roll monster initiatives before retrying.

To avoid removing initiative after joining, clearing initiative on an active
combatant is rejected. Leave battle first, or submit active=false and
initiative=null together. Inactive combatants can retain empty initiative.
Starting a battle also rejects legacy active records without initiative.
Lairs retain their existing fixed-initiative behavior.

## Server enforcement

The shared write-transaction wrapper checks individual updates and bulk joins
before calling their handlers. A transition check catches invalid activations
from imports or clearing initiative through monster edits. Failed transitions
roll back both database writes and runtime state before any deferred broadcast.
Only applicable character/monster operations are checked; setup loading remains
compatible with older stored records, which can be corrected or removed before
starting battle. No stored data is automatically rewritten.

A separate UI script observes character and monster row rendering and updates
button availability from the saved state. It does not replace admin.js or its
message helper. The server remains authoritative if a request bypasses the UI.

## Checks

```sh
python -m unittest discover -s tests -p 'test_initiative_join_gate.py' -v
node --test tests/initiative-join-gate.test.cjs
node --check static/initiative-join-gate.js
```
