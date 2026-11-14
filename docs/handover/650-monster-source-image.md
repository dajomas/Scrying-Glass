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

## Follow-up - 2026-11-14

User instruction: "In the Edit monster modal, the Select image from source button needs to be bottom aligned with the Image file selection text box and the Selected text needs to go under the button. When selecting multiple monsters, and using the dropdown action, provide a row per monster with the images found for that monster and allow to select an image per monster. Also let the user know the image lookup is in progress. Make the lookup smart enough that only a single lookup will be done per monster species".

- Edit monster: the button is bottom-aligned with the file input (`align-self: end`); the status text ("Looking up…", "Selected: … Save to apply.") is its own grid item in the next row, under the button, and is hidden while empty.
- Monster action dropdown: the dialog opens at once with one row per selected monster (name and species). Each row has a "Keep current" tile (selected by default) and the images found for that monster's species; one image can be chosen per monster. "Apply images (N)" sends only the changed monsters. A status line shows "Looking up images… X of Y species done", and each row shows "Looking up images for <species>…" until its lookup returns, or the reason when nothing was found or the lookup failed.
- One lookup per species: lookups are cached by species (case-insensitive) for 10 minutes and shared by concurrent requests, the Edit button and the bulk dialog; the selection tokens stay valid for 30 minutes on the server. Failed lookups are not cached. In the bulk dialog the species are looked up one after another.
- `POST /api/monsters/source-image` now takes `{items: [{id, image_selection_token, image_species}]}` (1-500 items, unique ids). All tokens are checked before any monster changes.
- Cache version: `monster-source-image.js?v=2`.

Validation of the follow-up (this sandbox): through `tools/run_split_tests.py`, `test_monster_source_image` (8) and `test_monster_source_image_browser` (8, including button/file-input bottom alignment, one row per monster, per-monster choices, progress text and one lookup per species across two runs) with `test_admin_split_runtime`, `test_admin_global_feedback_inventory`, `test_asset_cache_busting` and `test_admin_asset_wiring`: 39 tests OK. The real Edit and bulk dialogs were checked on a live local server in Chromium with stubbed lookups and images. User run and acceptance pending.

CI run 43636503802 (on `93ffbd0e`) failed one test: `test_edit_rejects_a_tampered_token`. It replaced the last two token characters with `00`, which changes nothing when a token already ends in `00`. The test now always changes the last character; it passed 8 of 8 in `test_monster_source_image`.

Layout fix (user screenshot of the bulk dialog): the "Keep current" tile looked wider because the selected outline was drawn outside the tile, and images with different shapes had no visible frame. The outline is now drawn inside the tile (`outline-offset: -3px`), every thumbnail sits in a 7rem square with a dark backdrop, tiles align to the top, and the "No source images found…" note is smaller and dimmed. Cache version `monster-source-image.js?v=3`. Validation: `test_monster_source_image_browser`, `test_asset_cache_busting` and `test_admin_asset_wiring` through `tools/run_split_tests.py`, plus a Chromium screenshot with wide, tall and square stub images. User run and acceptance pending.

Partial image lookups (user report: Open5e timed out, and the bulk row for Shadow showed "Combined monster lookup incomplete: Open5e. No candidates were offered", plus two tracebacks in the server log):

- Image picking (Edit button and bulk dialog) now calls `GET /api/monsters/lookup?images=true&species=…`. In that mode, `ordered_candidates(partial=True)` returns the candidates from the providers that answered, with `failed` and a `warning` ("Not available right now: Open5e. Showing images from the other sources."). It is still an error when every enabled provider failed. Stats lookups (add, refresh) are unchanged and stay fail-closed.
- The warning is shown in the bulk row note and in the Edit status line. Partial and failed lookups are not cached, so the next attempt retries every source.
- Network timeouts and connection errors are logged once as a single line ("Combined monster lookup: Open5e did not respond (The read operation timed out)") instead of two tracebacks. Other provider errors still log a traceback.
- Cache version `monster-source-image.js?v=4`.

Validation: through `tools/run_split_tests.py`, the new `test_image_lookup_partial` (4) and every test module that uses the lookup, combined lookup or Open5e provider (20 modules, including the source-image browser test with a new partial-warning case): 159 tests OK. Not checked against the real Open5e service. User run and acceptance pending.

## Acceptance

- The user tested and accepted this work on 2026-11-14 and asked to close it. That covers the original delivery `46e3788a` and the follow-ups `b157aef8` (per-monster rows, lookup progress, one lookup per species, aligned Edit button, fixed flaky tampered-token test), `115eb7a6` (even tiles in the bulk dialog) and `11bbe512` (partial image lookups when a source times out). Earlier "user run and acceptance pending" notes in this document are superseded.
- CI on `features/perplexity`, observed: run 43635715705 (`46e3788a`), 43637464939 (`b157aef8`), 43638272866 (`115eb7a6`) and 43639327765 (`11bbe512`) all concluded success. Run 43636503802 on `93ffbd0e` (the port message commit) failed only on the flaky `test_edit_rejects_a_tampered_token`, which was fixed in `b157aef8`.
- Status: completed and closed.
