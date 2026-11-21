# 086 - SG-TODO-022 Stage D: statblock viewer, keyboard and live synchronization (022.10-022.12)

[Back to handover index](../../HANDOVER.md) · [Stage C2](085-statblock-stage-c2-listener.md) · [TODO 220](../todo/220-admin-statblock-viewer.md)

Date: 2026-11-17. Baseline: `f81a6ffad87142fc97bc7d0b688f34a406581782` (Stage C2) on
`features/claude-statblock`. Delivered as a zip archive; commit SHA not yet known.
CI not run (`[skip ci]`, agreed for Stages A-E until the last code delivery). The user
asked to continue with Stage D before CI results of C1/C2 were reviewed.

## Delivered

### 022.10 - tiles and safe statblocks (`static/statblocks.js`, `static/statblocks-render.js`, `static/statblocks.css`)

- Tiles follow the server projection: the existing viewer's logical membership, monster
  order and distinct instance IDs; SG name, species and configured border colour; a
  status badge (`Partial`, `No statblock`, `Loading…`, `Unavailable`, `Load failed`).
- One expanded tile spans the grid row. Its header shows the six SG values from the live
  projection (name, species, AC, HP/max HP, initiative bonus); snapshot facts, sections,
  entries, lists, tables, emphasis, links and line breaks follow in source order;
  disabled sections are labelled; partial statblocks show a note and their warnings.
- Species placeholders show the current SG species (the source text only if the SG
  species is empty).
- Supporting definitions appear once each, collapsed, under References, with their own
  facts, content, warnings and source. Inline reference buttons open and focus the
  existing definition (also from inside another definition), so repeated or circular
  references never nest copies; several definitions can be open.
- Source and credits list every main provenance row with attribution, publisher and licence.
- Safety: DOM construction with text nodes only; no imported HTML, styles or handlers;
  links only for https URLs without credentials (`rel="noopener noreferrer nofollow"`,
  new tab); unknown node kinds become plain text.

### 022.11 - keyboard and accessibility

- Tile buttons in a list (`h2` per tile, `aria-expanded`, `aria-controls` to a labelled
  region). Click, Enter or Space expand; another tile replaces it; the header button or
  Escape (anywhere in the tile) collapses and returns focus to the tile. Text selection,
  scrolling, links, reference buttons and `<details>` never collapse.
- Arrow keys move by on-screen rows using tile positions, so any width and incomplete last
  rows work; Home/End jump to the first/last tile; one tile is in the tab order (roving
  tabindex). When the focused tile disappears, focus moves to its neighbour.
- Visible focus outlines; headings h1/h2/h3/h4; responsive grid without horizontal scroll
  at 360 px.

### 022.12 - live synchronization and original-source loading

- Each WebSocket `state` frame updates tiles, order, colours, names and the six values in
  place. The expanded statblock is fetched only when its revision is new (cached by
  revision, `known_revision` avoids re-sending content, in-flight requests are not
  repeated, responses for an older campaign/encounter or a collapsed tile are ignored).
- A different campaign or encounter token, a `revoked` frame, a 1008 close or a 401/403
  read clears all tiles and cached content; reconnects resynchronize from a fresh frame.
- `scrying_glass_statblock_autoloading.py`: while a permitted viewer is connected, each
  committed change (and each connection) loads missing statblocks for tile monsters from
  their retained exact tracker source identity only, through the shared scheduler,
  fetcher and isolated workers. The result is saved in a transaction only if campaign,
  encounter, monster, species, source fields, "no statblock yet", membership and the
  provider switch still hold. One attempt per identity at a time; transient failures wait
  `failure_cooldown_seconds`; unavailable records (not found, no public statblock) are not
  retried in that encounter; a disabled provider shows `unavailable`. Projection statuses:
  `missing`, `loading`, `unavailable`, `error` (with `status_detail` and `retry_at`).
- Automatic saves (`load_original_statblock`) neither record nor clear undo history: a top
  undo entry that described the state just before is rebased so Undo stays available.

## Decisions

User review 2026-11-17 (after push `1f754ba`), both accepted:

1. Original-source loading only runs while a permitted statblock viewer is connected and
   only for tile (battle) monsters; nothing is loaded for unseen encounters.
2. After a stale automatic result is discarded (for example because the species was edited
   while it loaded), the next event loads again from the same retained tracker source
   (option A of three discussed). The user's rule: when the species changes and a new
   statblock is chosen from any valid source, the new statblock is shown; when only the
   species changes and the statblock stays, the new species is substituted in the saved
   statblock. Both already hold: a statblock saved with the edit (Edit Monster staging,
   [084](084-statblock-stage-c1-import-apis.md)) gets a new revision that the viewer fetches,
   and automatic loading never replaces an existing statblock; species placeholders render
   the current SG species at display time, so saved content is not rewritten. Covered by
   `test_edit_staging_saves_the_statblock_with_the_ordinary_edit`,
   `test_sg_values_override_and_species_placeholders_follow_live_species` and
   `test_disabled_provider_no_viewer_and_changed_target_load_nothing`.

## Validation (Python 3.13.18, Chromium via local Google Chrome)

- `tests/test_statblock_viewer_browser.py` (8 tests: membership/order/colour/states,
  expand/replace/collapse, live SG values and placeholders without refetch, one refetch per
  new revision, references without nesting, hostile content, grid keyboard at three and one
  columns with removed tiles, revocation/campaign change/403, stale responses): pass.
- `tests/test_statblock_autoload.py` (5 tests: one load and save, undo preserved, cooldown and
  unavailable, disabled provider/no viewer/changed target, inactive monsters and revoked
  viewers): pass.
- `e2e/test_statblock_viewer.py` (real server, Chromium/Firefox: sign-in roles, live tiles,
  keyboard, axe at 360/1440 px, sign-out): **not run** (FastAPI, uvicorn and axe are not
  installed here). axe has therefore not been run on the new page.
- Whole-module regression comparison against `f81a6ff`: see `Patch/` notes.
- Not run: CI, Firefox, live providers.

## Open work

- Stage E (022.13/022.14): Edit Monster and bulk import UI in the Admin.
- e2e/axe evidence for this page (022.15).
