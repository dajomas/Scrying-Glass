# 088 - SG-TODO-022.15 correction round 1: statblock search, Edit dialog and viewer layout

[Back to handover index](../../HANDOVER.md) · [Stage E](087-statblock-stage-e-import-ui.md) · [TODO 220](../todo/220-admin-statblock-viewer.md)

Date: 2026-11-20. Baseline: `307e9efd622bef756a8ce01f758e0022ce53027e` on
`features/claude-statblock`. Delivered by push (`CLAUDE_INSTRUCTIONS.md`, delivery
2026-11-20); the commit carries no `[skip ci]`, so Branch tests run. The user reported
four findings while reviewing the delivered 022 implementation.

## Findings and corrections

1. **Find statblock listed unusable entries** (both D&D Beyond entries for Crawling Claw).
   The D&D Beyond search page lists gated content (for example a Monster Manual creature
   outside the SRD) exactly like public content: the captured 2024 Aboleth (public) and
   2024 Beholder (gated) rows are identical. Discovery now fetches each D&D Beyond
   candidate's own page (`public_statblock` in `scrying_glass_dndbeyond_statblock.py`) and
   omits it when the page has no statblock root, the same test preparation uses
   (`statblock_unavailable`). The tracker's original D&D Beyond candidate is checked too.
   The provider row reports `omitted_unavailable` (counted once when the original is also
   a search hit) and the Edit/bulk choosers show "D&D Beyond: n result(s) without a public
   statblock not offered." A page that cannot be checked is still offered and makes the
   provider result `partial` with the failure code. Pages are fetched through the shared
   cache, so preparing a checked candidate reuses its page. Other providers are unchanged.
2. **Statblock controls were misaligned** in Edit Monster. The buttons and the file input
   (below its caption) are now bottom-aligned (`monster-statblock-import.css`).
3. **Show statblock** button in Edit Monster. It shows the staged (chosen, unsaved)
   statblock when there is one, marked "not saved until you save the monster", otherwise
   the saved statblock from `GET /api/statblocks/monsters/{id}` (no new route), always with
   the dialog's current name, species, AC and HP. It is disabled when nothing is saved or
   staged. Close or Escape closes it.
4. **Viewer statblock layout** follows the D&D Beyond (2014/2024) and Open5e statblocks
   the user supplied (`statblocks-render.js`, `statblocks.css`): name and type line over a
   rule; Armor Class, Hit Points, Initiative (live values) and Speed; an ability table in
   two groups of three with MOD and SAVE columns (SAVE from the per-ability save, the
   Saving Throws fact when every part is a plain bonus, otherwise the modifier; the
   Saving Throws row is then not repeated); property rows in the usual order (skills,
   gear, vulnerabilities, resistances, immunities, senses, languages, challenge,
   proficiency bonus, then any others); sections with serif small-caps headings. From a
   statblock width of 48rem the sections sit in a second column; narrower statblocks
   stack. Habitat/source/environment facts follow the sections. The same renderer is
   used by the Admin previews. Asset versions are raised to `?v=2`.

## Validation (Python 3.13.18, Chromium via local Google Chrome)

- `tests/test_statblock_import_service.py`: 3 new discovery tests (gated results omitted
  and counted, unchecked result offered as partial, gated original not offered and
  counted once); 22 tests pass.
- `tests/test_statblock_source_adapters.py`: `public_statblock` agrees with preparation
  for every captured D&D Beyond page (available and gated); 15 tests pass.
- `tests/test_statblock_import_browser.py`: new Show statblock (staged and saved, live
  form values, disabled state, no request for the staged preview) and bottom-alignment
  tests; 9 tests pass.
- `tests/test_statblock_viewer_browser.py`: new layout (core block, ability table,
  two columns at width and stacking when narrow) and Saving Throws/SAVE tests; 10 pass.
- Visual check of captured D&D Beyond 2014/2024, Open5e, `.monster` and 5e.tools
  statblocks at 600-1500 px wide, and of the Edit Monster controls.
- Whole-module comparison against `307e9ef` (every `tests/test_*.py` run separately):
  the same 164 of 248 modules pass before and after; the rest fail or time out
  identically here (FastAPI, httpx2 or aiohttp missing, or slow fixtures). The FastAPI
  route, HTTP and e2e tests were **not run** locally; CI covers the configured suites.

## Known limitations and open work

- D&D Beyond habitat values run together (for example `ForestGrasslandHill`): the
  adapter joins the footer links without separators. Not changed here.
- Discovery now makes one extra D&D Beyond request per candidate (at most 32 per
  species, within the existing provider limits, deadline and cache).
- 022.15 continues with the CI run for this commit, the e2e suite and further findings;
  022.16 (acceptance) follows.
