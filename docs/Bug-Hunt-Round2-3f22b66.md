# Second bug hunt: fixes for source archive 3f22b66

This ZIP is a changed-files overlay for the supplied 3f22b66 source archive,
which already contains the previous 72504c1 fixes. No database, uploaded media,
configuration, secrets or complete source tree is included.

## Findings and fixes

### Monster-only setup import retained original effect links

Imported monsters received new combatant IDs, but effect source_id and anchor_id
still referenced original monsters. Ending the original monster's concentration
could remove an imported monster's effect. Imported conditions could also bind to
unrelated characters with matching IDs when importing from another campaign.

python/scrying_glass_admin_setups.py now allocates all clones first and remaps
self- and cross-monster references to the new batch. Each copied effect receives
a fresh ID. External character/lair references are retained only when importing
within the same campaign and the participant exists in both source and destination.
Missing concentration sources cause their linked effects to be dropped. Other
missing sources are cleared; missing timed anchors become manual effects, retaining
their names and notes. Original source objects are not modified.

### Recovered zero-HP characters stayed out of initiative

FeaturesService.edit_features checked active/alive before inserting a combatant.
Characters restored from dead to down/stable are eligible for turns despite having
alive=False. They were missing from the displayed order until later advance logic
repaired the order.

python/scrying_glass_service_features.py now uses the shared can_take_turn predicate
for insertion. Recovered active down/stable characters return at their initiative
position without taking the current combatant's turn. Inactive characters remain out.

## Files

- python/scrying_glass_admin_setups.py (replacement)
- python/scrying_glass_service_features.py (replacement)
- tests/test_bughunt_round2.py (new: 12 SQLite/transaction regression tests)
- docs/Bug-Hunt-Round2-3f22b66.md (these notes)
- docs/Bug-Hunt-Round2-3f22b66-validation.txt (baseline, failure reproduction and final validation)
- docs/Bug-Hunt-Round2-3f22b66.patch (application-file diff for review; not required for extraction)

## Validation

- Original suite before fixes: 258 Python tests passed.
- New tests against original code: 12 tests, 8 failing assertions.
- Complete patched suite: 270 Python tests passed.
- All 9 existing JavaScript test scripts passed under Node.
- Scope: service handlers, transaction wrappers, real SQLite, and existing Node tests.
  No live HTTP or full-browser integration run was performed.

## Apply

1. Stop the application and back up the code and storage directory.
2. Extract this ZIP at the repository root, preserving its directory structure.
   Review local differences before overwriting: replacements target 3f22b66.
3. Run:

   python -m unittest discover -s tests -v

   for test in tests/test_*.js; do node "$test" || exit 1; done

4. Restart and smoke-test monster import with linked/timed effects and recovery of
   an active dead character to down/stable while another combatant holds the turn.

No schema migration or database repair script is required. This fixes future
imports; it does not infer or rewrite stale references in previously imported
monsters. Existing broken links should be reviewed through the feature controls.
