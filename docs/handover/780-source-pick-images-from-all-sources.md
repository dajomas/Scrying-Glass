# 780 - Images from all sources for a dropdown monster pick

[Back to HANDOVER index](../../HANDOVER.md) · [770 - Battle Actions menus](770-battle-action-colour-menus.md)

User request, no TODO ID, 2026-11-23 on `features/claude`: "If you select a monster from the
dropdown menus, do a search on all available sources to select an image." Before, a pick
from the Source and Monster dropdowns (SG-TODO-016) ran as a one-candidate lookup, so the
image picker had nothing to offer: an Open5e monster got no image, and a monster with an
image could not take another.

## Changes

- `static/monster-candidate-selection.js`: a dropdown pick is marked (`preset(...)`). After
  the picked monster is applied, and unless an image file is chosen, the name is searched
  with the normal lookup (`/api/monsters/lookup?species=<name>`, every enabled provider) and
  the found candidates are offered in the existing "Select monster image" dialog. The
  picked monster stays the selection (its stats and `selection_token`); a chosen image
  goes in as `image_selection_token`, which the server already checks against the monster
  species (the picked name, the same name the search used). Duplicate images (the picked
  monster found again) are shown once. A failed search (plain `fetch`, no Admin
  notification) or one without other images adds no dialog; the monster add waits for the
  search like any lookup.
- Tests: `tests/test_monster_source_picker_browser.py` gains three: a pick without an image
  is offered the D&D Beyond and Open5e images and submits the chosen image's token with
  the pick's own token; a pick with an image lists it first and Cancel keeps it; a failed
  search keeps the pick without a dialog.
- User Guide: the Source and Monster dropdown paragraph.

## Evidence

- `test_monster_source_picker_browser` and `test_monster_candidate_browser`: 18 tests pass;
  all `test_monster*` modules show no failures beyond the known FastAPI baseline.
- Delivered in b4d69c9; CI 45248015006 green (tests and connection audit). e2e
  20261123T193746Z on 11121d2 (the CI publish commit on top of b4d69c9, same code):
  137 passed, 0 failed (Chromium and Firefox).
