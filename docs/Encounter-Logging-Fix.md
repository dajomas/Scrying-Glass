# Encounter activity logging

Documented baseline: `features/development` at `4f401b4adfca92e9c9599aea8924c14efb49aea4`.

## Behaviour

- Mark concentrating records concentration-started rather than a generic combat-features event.
- Marking an already-concentrating combatant does not create another started event.
- Adding a concentration-linked effect that starts source concentration also records a start event.
- End concentration retains concentration-ended and lists the linked effect names removed.
- Feature changes name the changed fields and record actual before/after values: HP,
  temporary HP, life state, death-save successes and failures.
- Combined changes produce one readable feature-details entry plus a concentration event
  when the concentration flag changes.
- Effect add/remove/expiry events retain their effect names in note.
- The admin log has a Details column that renders note using the existing HTML escape helper.
- CSV export includes note with the existing spreadsheet-formula protection.
- JSON export already includes the entire entry and requires no changes.

Examples:

    concentration-started | Concentration started
    combat-features       | Temporary HP: 0 → 7
    combat-features       | HP: 12 → 9; Temporary HP: 7 → 0
    effect-added          | Blessed
    effect-removed        | Blessed
    concentration-ended  | Concentration ended; removed linked effects: Blessed

Older effect entries already containing note show their names once the new renderer loads.
Older combat-features entries retain their existing JSON notes. Historical events are not
rewritten and missing historical details cannot be recovered by the application.


Reaction rows log their selected source; lair damage logs the acting lair. Undo and checkpoint restore preserve the current audit trail and append events instead of rewinding historical actions. Clear is permanent and clears the associated saved log without saving unrelated encounter changes. Player payloads do not contain activity logs.

Checks: `python -m unittest discover -s tests -p "test_feature_logging.py"` and `python -m unittest discover -s tests -p "test_lair_damage_logging.py"`.
