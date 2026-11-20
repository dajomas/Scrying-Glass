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

## Follow-up - access gates as in the Add Monster stats lookup (2026-11-20)

The user asked to use the Add Monster stats lookup's paywall detection. Review of
`dnd_monster_detail_html` (`python/scrying_glass_dndbeyond.py`) and the captured
evidence showed that finding 1 was **not fixed for live pages** by the first commit
(`883d57d`): every captured gated page (Beholder, Mind Flayer, Death Knight, Drow Mage,
2014 and 2024) answered with a redirect to `marketplace.dndbeyond.com/category/...`, not
with a page without a statblock. The statblock fetcher refuses redirects to other hosts
(`unsafe_redirect`), which discovery treated as "could not be checked" and still offered.
The first commit's tests only used fake pages without a statblock root.

The statblock fetcher (`ProviderFetcher`, D&D Beyond monster pages only) now applies the
stats lookup's rules: a redirect to `marketplace.dndbeyond.com/category/...` or to
`/marketplace`, `/login` or `/sign-in` on dndbeyond.com (not followed), a 401/403 whose
visible text says the content is locked (`dnd_monster_content_locked`; the status alone
is not enough), and a 404 (the stats lookup skips those) all return an empty page, as
the stats lookup does. An empty page is cached like any answer, so a repeated search
does not hit a failure cooldown, and both discovery (not offered, counted) and
preparation (`statblock_unavailable`) treat it as having no statblock. Other failures
and redirects are unchanged (`unsafe_redirect`, `provider_error`, `not_found` for the
search page). Like the stats lookup, the decision needs one request per candidate page;
the search listing has no paywall marker.

Validation: new fetcher test drives the real redirect handler with marketplace, relative
`/marketplace` and sign-in targets, 401/403 with and without lock text, 404 on a monster
page versus the search page, and the rules switched off; a local HTTP server confirmed a
real urllib 302 to the marketplace is stopped. The captured-evidence test now asserts that
every captured gated page was a marketplace redirect recognized by the gate and no public
page was. Service tests use the empty page for a redirected candidate. 124 related
modules (statblock, D&D Beyond, monster lookup, 5e.tools, Open5e) give the same results
as before this follow-up (74 pass; the rest need FastAPI/httpx2/aiohttp here).

## CI for `883d57d` and the publication allowlist test (2026-11-20)

Branch tests run 44804204363 attempt 1 (push of `883d57d`, the first CI run on this
branch) failed on one test: 2253 main-suite tests ran with 1 failure,
`test_ci_publication_branch_allowlists.test_workflow_allowlist`, which also failed in the
standalone step. It pins the publish workflow's branch list, which the user's commit
`5a31190` had extended with `features/claude` and `features/claude-statblock`. All other
tests passed, including the statblock modules; the Chromium provisioning messages in the
log are preflight warnings, the browser tests ran. The branch's
`tools/publish_ci_results.sh` gate still allowed only the Perplexity branches (the user
had updated it on `main`, from where the publish workflow runs it). This follow-up makes
the branch's gate identical to `main`'s and extends the test's expected branches and
rejected look-alikes (`features/claude-statblock/other`, `-extra`, `features/claude-statbloc`,
`features/claude/other`). Run 44806218512 attempt 1 for `95ef0ab` ended as `cancelled` (not by Claude); its
published log (`ci-results-44806218512-attempt-1`, publication `c2206de`) shows 2254
main-suite tests with the same single allowlist failure, also in the standalone step.
Both runs were published by Publish CI results, which confirms the publication now works
for this branch.

## Known limitations and open work

- D&D Beyond habitat values run together (for example `ForestGrasslandHill`): the
  adapter joins the footer links without separators. Not changed here.
- Discovery now makes one extra D&D Beyond request per candidate (at most 32 per
  species, within the existing provider limits, deadline and cache).
- 022.15 continues with the CI run for this commit, the e2e suite and further findings;
  022.16 (acceptance) follows.
