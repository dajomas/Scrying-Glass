# 650 - Choose a monster image from the monster sources

[Back to HANDOVER index](../../HANDOVER.md)

User request, 2026-11-14, delivered on `features/perplexity` (no TODO ID assigned). User instruction: "In the Monster edit box, add a button to select an image from the available sources for that monster. In the Monster action dropdown box add an option to select an image from the available sources for the selected monsters."

## Change

New `static/monster-source-image.js?v=1`, loaded after `monster-refresh-review.js` in `templates/admin/190_document_end.html`. No admin fragment changed (the 8 fragments and the 20,000-byte limit are untouched).

- Edit monster: a "Select image from sources" button below "Replace image". It looks up the species currently in the form with the existing `/api/monsters/lookup` (D&D Beyond, 5e.tools and Open5e, following the saved provider switches) and shows every distinct `https` image found. The choice updates the preview and is saved with "Save monster" (hidden `image_selection_token` and `image_species` fields). Cancel keeps the current image. Choosing a file afterwards replaces the source choice, and an uploaded file always wins on the server.
- Monster action dropdown: a "Select image from sources" option, placed before Remove. It looks up each distinct species of the selected monsters, shows all images found (captioned with the species when more than one species is selected), and sets the chosen image on all selected monsters through the new `POST /api/monsters/source-image`. Progress, errors and the result use the Monsters feedback region.
- Server: images are only accepted as signed lookup tokens (the same `selection_token` used when adding a monster), checked for signature, 30-minute age, species and an `https` image. `edit_monster` accepts the optional `image_selection_token`/`image_species` form fields. `set_monster_source_image` (authenticated, same-origin, transactional like the other admin writes) accepts `{ids, image_selection_token, image_species}` for 1-500 monsters and changes only `image_url`; an unknown monster rejects the whole request.

## Tests

- `tests/test_monster_source_image.py` (8 handler tests): edit uses the signed image, upload precedence, tampered token rejected, no token keeps the image, bulk sets only the selected monsters, species mismatch, missing image and empty selection rejected, unknown monster rejected without changes, route registration.
- `tests/test_monster_source_image_browser.py` (5 Chromium tests with intercepted endpoints): Edit button stores the chosen token and preview, Cancel stores nothing, the bulk option posts one image for all selected monsters and reloads, no selection posts nothing, other bulk actions are delegated.

## Validation (local, this sandbox)

- Through `tools/run_split_tests.py`: the two new files plus the related monster edit, initiative, route, feedback-inventory, split-runtime, refresh-review, image-preview, candidate and roster tests: 101 tests OK.
- `e2e/test_layout_accessibility.py` and `e2e/test_rosters.py` in Chromium: 16 passed.
- Not tested against live D&D Beyond, 5e.tools or Open5e lookups (the sandbox tests intercept the lookup). User run and acceptance pending.
