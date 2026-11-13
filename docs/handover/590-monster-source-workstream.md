# 590 - Monster source workstream (SG-TODO-016/017)

[Back to HANDOVER index](../../HANDOVER.md) · [016 task](../todo/160-source-based-monster-selection.md) · [017 task](../todo/170-open5e-monster-source.md) · [delivery sequence](../todo/115-admin-delivery-sequence.md#source-integration-workstream-investigate-before-fixing-internal-order)

## Accepted plan and decisions - 2026-11-13

On 2026-11-13 the user accepted a coordinated three-stage workstream and recorded these decisions:

1. **Stage 1 - feasibility and design (documentation only, `[skip ci]`).** This section.
2. **Stage 2 - SG-TODO-017 Open5e provider.** Generalize the two-provider lookup into a provider/catalog layer; add the Open5e lookup, field mapping and per-provider toggles; add fixture tests plus a separate live API check.
3. **Stage 3 - SG-TODO-016 source and monster dropdowns,** built on the Stage 2 layer.

User decisions (2026-11-13):

- **D&D Beyond:** left out of the 016 source dropdown because of how it is accessed (public HTML search). It stays available for name search only.
- **Open5e documents:** all documents are included. When several candidates or options match, the source is shown with each choice.
- **Open5e:** enabled by default.
- **Picking a monster:** name, statistics and image are filled in only when those fields are still empty or the overwrite check is ticked.
- **Extra:** add toggles to enable or disable D&D Beyond search, 5e.tools search and Open5e search.

Each stage needs its own bound approval before a GitHub write. Accepting the plan does not approve later payloads, merges or deployments.

## Stage 1 findings - 2026-11-13

Observed against the live services and the current code on 2026-11-13. These are not fixture results.

### Open5e API (v2)

- The [API documentation](https://open5e.com/api-docs) describes v2 as the current, actively maintained version. It uses Django REST Framework filters, `fields` selection, `limit`/`page` pagination (50 per page by default), and returns 404 for an out-of-range page.
- [`/v2/documents/`](https://api.open5e.com/v2/documents/?limit=200&format=json) returned 24 documents in one page. Each carries `key`, `display_name`, `publisher`, `gamesystem` and `licenses`. Game systems seen: `5e-2014`, `5e-2024` and `a5e`. Licences seen: CC-BY-4.0, OGL 1.0a and CC0.
- [`/v2/creatures/`](https://api.open5e.com/v2/creatures/?limit=1) reported `count` 3,541. Each creature has a stable `key` (e.g. `srd-2024_aboleth`), `name`, a nested `document`, `armor_class`, `hit_points`, `hit_dice`, `ability_scores`, `initiative_bonus` and `illustration`.
- Per-document listing works: `document__key=srd-2024` reported 331 creatures and `document__key=tob` 391. With `limit=5000&fields=key,name`, all 391 `tob` creatures came back in one page with `next: null`. The server-side page cap is undocumented, so the provider must still follow `next` until it is null.
- Exact name search works: `name__iexact=goblin` returned 3 candidates from `a5e-mm`, `bfrd` and `srd-2014`. This confirms the need to show the source on each candidate.
- **Unsupported filters are silently ignored.** `illustration__isnull=false` returned the full unfiltered 3,541. The provider must validate each result, e.g. that `document.key` matches the requested document and the name matches, rather than trusting the query. This matches an open upstream issue in which [an endpoint ignores `document__key`](https://github.com/open5e/open5e-api/issues).
- Images: every sampled creature had `illustration: null`. Plan for most Open5e monsters having no image; existing image fallback and upload precedence stay unchanged.
- No API key is required, and no rate-limit headers or documented quota were observed. Content changes only between publisher releases, so the provider should cache bounded catalog responses, as 5e.tools already does.
- Licensing: content carries per-document licences (OGL 1.0a / CC-BY-4.0 / CC0). The [Open5e API licence](https://github.com/open5e/open5e-api/blob/staging/LICENSE.md) states that artistic images in that repository are CC BY-NC 4.0. Stage 2 should show document, publisher and licence attribution with Open5e candidates and add an attribution note to the documentation. It should not bundle Open5e data.

### Existing providers and code

- `python/scrying_glass_combined_lookup.py` hard-codes two providers (D&D Beyond, 5e.tools), fails closed (one failed provider suppresses all candidates) and caps the list at 32 candidates. Stage 2 generalizes this to an ordered provider list without changing the fail-closed rule.
- D&D Beyond is reached through its public HTML name-search page. Complete per-source enumeration was not attempted, because the user excluded it from the dropdown.
- 5e.tools loads one bestiary JSON file per configured source, so a complete per-source list is available from data the app already fetches.
- Existing switches are config keys only: `display.dndbeyond_image_lookup` (also gates D&D Beyond images and monster refresh) and `display.fivetools_fallback`. There is no Open5e key and no Admin toggle yet.

## Proposed Stage 2 design (for review with the Stage 2 payload)

These items are proposals until accepted with the Stage 2 delivery:

- New `display.open5e_lookup` config key, default `true`, and `display.open5e_base_url` with an HTTPS-only default of `https://api.open5e.com/v2`.
- Admin toggles for the three providers, initialized from the config keys and stored server-side. Each toggle disables that provider for candidate lookup and, where the provider is already used, for image lookup and monster refresh, matching the existing D&D Beyond key. Only admin roles allowed to change settings can switch them.
- Candidate order: D&D Beyond, then 5e.tools, then Open5e. All enabled providers are collected and the existing fail-closed and 32-candidate rules are kept.
- Open5e name lookup uses `name__iexact` with result validation. The mapping covers AC, HP, hit dice, ability scores and the initiative bonus through the existing 018 bonus-offer contract; missing fields stay empty rather than invented.
- Candidate labels show the document display name and game system (e.g. `Goblin - 5e 2014 Rules (Open5e)`).
- Monster refresh participation for Open5e is not assumed; it is proposed for Stage 2 only if agreed.

## Stage 3 notes

- Source options: None (default), each configured 5e.tools source, and each Open5e document labelled with its display name and game system. D&D Beyond is not listed.
- Full lists come from per-source catalogs. Open5e loads all pages with validated `document.key`; the list is shown as complete only after every page has loaded.
- Fill-in rules follow the user's decision on empty fields and the overwrite check.

## Stage 2 delivery - 2026-11-13

On 2026-11-13 the user asked to "Start Stage 2 on the proposed design". The proposals above were implemented as follows. Open5e Refresh participation was proposed only "if agreed" and was not agreed, so it is excluded.

### Delivered behaviour

- **Ordered provider layer.** `python/scrying_glass_combined_lookup.py` adds `ordered_candidates` over an ordered `(name, enabled, fetch)` list; `combined_candidates` keeps its signature and appends extra providers. The fail-closed rule and the per-provider 32-candidate limit are unchanged.
- **Open5e provider.** New `python/scrying_glass_open5e.py` queries `/creatures/?name__iexact=…&fields=…`, follows `next` on the configured host only (10-page cap) and rejects incomplete listings, unknown documents, duplicate or malformed keys and more than 32 results. Each creature is validated by normalized exact name because the API ignores unsupported filters. A `/documents/` catalog supplies publisher and licence attribution. Responses are capped at 4 MB, use a 10-second timeout and a separate one-hour/64-entry cache, so 5e.tools bestiary files are not evicted.
- **Field mapping.** AC (0-999); HP as the dice formula only when it reproduces the listed `hit_points` average, otherwise the average; `initiative_bonus` as an available source offer when it is an integer within the 018 storage range, `missing` when null, `invalid` otherwise. Missing values stay empty. `legacy` is true for the `5e-2014` game system. An illustration becomes a remote image URL only when it resolves to HTTPS on the configured API host. Open5e illustrations are CC BY-NC 4.0; most creatures have none.
- **Source identity.** `monster_source_snapshot` accepts provider `Open5e` with canonical `https://api.open5e.com/v2/creatures/<key>/` URLs and keeps the document display name as the source book. Candidates from a non-default `open5e_base_url` still work but are not retained as source identities.
- **Labels.** `monsterSourceLabel` shows `"Open5e / <document>[ / legacy]"` in the selection popup (the same provider / book [/ edition] layout as D&D Beyond and 5e.tools; `legacy` marks the `5e-2014` game system) and `"Open5e (<document>)"` elsewhere; the popup adds the attribution text. Existing labels are unchanged. Follow-up 2026-11-13 after user review of `e07c04de`: the original `"<document>, <game system> (Open5e)"` layout was replaced, and the popup now keeps provider order (first appearance) while sorting rows within each provider by their source label (case-insensitive, numeric-aware; ties keep server order).
- **Configuration.** `display.open5e_lookup` (default `true` in `DEFAULT_CONFIG` and `config.example.yaml`; must be boolean) and `display.open5e_base_url` (HTTPS without credentials, query or fragment). A hand-built configuration mapping without the key leaves Open5e off, so existing offline test contexts never reach the network.
- **Provider switches.** New `python/scrying_glass_provider_settings.py` and a "Monster lookup providers" section on the superadmin User management page (`static/lookup-providers-admin.js`). `GET`/`PUT /api/settings/lookup-providers` are superadmin-only; `PUT` also has the same-origin check and accepts only boolean `dndbeyond`, `fivetools`, `open5e`. Saved switches go in a `lookup_provider_settings` table created on first save (a backup is taken first, as for viewer grants). The schema version is unchanged. Saved switches override the configuration keys through `effective_display` for candidate lookup, the legacy stats endpoint, D&D Beyond/5e.tools image lookup and Refresh. Worker-thread reads use a separate read-only connection plus a cache updated on save. An unreadable settings table disables all optional providers rather than re-enabling one.
- **Refresh.** Originally excluded (lookups passed `include_open5e=False`). Changed 2026-11-13 after the user decided "Yes include it if it is enabled": Refresh lookups include Open5e when its switch is enabled, and a retained Open5e identity is re-resolved by exact identity match (provider, URL, name, document, legacy) like 5e.tools; it fails with "Provider disabled" when Open5e is off and is never substituted.
- **Fill-in rules.** Unchanged from the existing flow: AC, HP range and initiative bonus fill blank fields or overwrite when the overwrite option is ticked; the image comes from the signed selection unless an image is uploaded. Name fill-in from a picked monster belongs to the Stage 3 dropdowns.

### Validation (local, 2026-11-13)

Executed through `tools/run_split_tests.py` on the Stage 2 tree: unittest discovery 1625 tests OK; pytest 1668 passed, 549 subtests; Node 83 files / 664 tests passed, 0 failed; standalone scripts all PASS, including `tests/audit_connection_lifetime.py` (188 modules) after the provider-settings read connection was changed to close explicitly; the targeted pytest pair 43 passed. The pytest, Node and other standalone runs came before that one-line close fix; after it, unittest, the connection audit and the provider/Open5e/refresh pytest modules (33 passed) were rerun. Admin pins: `static/admin/010-source.js` is 19,711 bytes (limit 20,000) and the assembled core bundle is 132,158 bytes, updated in `tests/test_admin_source_preparation.py`. New tests: `tests/test_open5e_provider.py` (fixtures, no network), `tests/test_lookup_provider_settings.py` (real SQLite, FastAPI TestClient routes) and `tests/open5e-source-labels.test.cjs`. `tools/check_open5e_live.py` is a manual live contract check outside CI; on 2026-11-13 it passed for Goblin (3 candidates), Aboleth (4) and Adult Red Dragon (4) against 24 live documents. CI for the Stage 2 commit `e07c04de`: [Branch tests run 43398379138](https://github.com/dajomas/Scrying-Glass/actions/runs/43398379138) concluded success (published in `fe5b4a22`). User acceptance is pending. No browser test covers the Users-page switches or the Open5e popup attribution rendering; these are covered by static and Node checks only.

Popup layout follow-up (local, 2026-11-13): after the label and sort change, unittest discovery 1625 tests OK; Node 83 files / 665 tests passed; standalone scripts all PASS (including the connection audit). The full pytest run showed 2 failures in `tests/test_monster_candidate_browser.py`, whose expectations assumed server order; they were updated to the sorted order and that module then passed (7 tests). `tests/open5e-source-labels.test.cjs` adds a provider-order/book-sort check. `static/admin/010-source.js` is now 19,657 bytes and the assembled core bundle 132,104 bytes. CI for the follow-up commit `aee3b893`: [Branch tests run 43402863879](https://github.com/dajomas/Scrying-Glass/actions/runs/43402863879) concluded success (published in `9938a679`).

UI follow-up (2026-11-13, after user review): the Select monster popup adds a text-only `small.monster-candidate-image` note per row ("Image available" when the candidate carries a non-empty `image_url`, otherwise "No image available"); the button's accessible name is unchanged (`monster-candidate-selection.js?v=6`). In the same commit, unrelated to 017: the Add monster notification (`#monsterAddNotification`) moved directly above the Monster identity group, and the Campaign Setup selector row is bottom-aligned with its buttons with extra space above Import characters CSV (`admin-panel-forms.css?v=2`). Only the related tests were run locally, per the user's instruction; the full suite runs in CI. CI for `2299a07d`: [Branch tests run 43405683876](https://github.com/dajomas/Scrying-Glass/actions/runs/43405683876) concluded success (published in `cc74d402`).

Popup and wording follow-up (2026-11-13, after user review with screenshot): the image status moved into the button text (" — Image available" / " — No image available"), and the View source link plus source details now sit on their own line below the button (`small.monster-candidate-details`). D&D Beyond candidates carry `attribution` from the page's `p.monster-source` text (for example "Basic Rules (2014), pg. 138 via D&D Beyond"); 5e.tools candidates carry "<code>, page N via 5e.tools" when the entry has a positive integer `page`. The D&D Beyond `source` label stayed "Source book unavailable" (superseded by the selection follow-up below). A new admin-role `GET /api/monsters/lookup-providers` returns enabled provider labels in lookup order; the lookup status message ("Looking up X (D&D Beyond, then 5e.tools, then Open5e)…") and the `#monsterLookupSources` help text use it (`monster-candidate-selection.js?v=7`). `static/admin/010-source.js` is 19,692 bytes; core bundle 132,139 bytes. Only related tests were run locally; the full suite runs in CI.

Selection follow-up (2026-11-13, user request): D&D Beyond choices now show the book from the page's source line (text before ", pg."; `dnd_source_book`), falling back to "Source book unavailable", so D&D Beyond rows sort by book like the other providers. Retained D&D Beyond identities are unchanged because `capture_source_fields` stores the book only for 5e.tools and Open5e. The Add monster overwrite checkbox is now ticked by default. After a choice from several found monsters, when another found monster has a different https image and no image file is chosen, a "Select monster image" dialog (`static/monster-image-choice.js?v=1`, split out to keep `monster-candidate-selection.js?v=8` under 20,000 bytes) shows the selected monster's thumbnail first and the other thumbnails labelled by provider and book. Cancel keeps the original image, or no image. The chosen image is sent as the signed `image_selection_token` of that other candidate; `create_monster` takes only that signed image (422 when the token is invalid, for another species, or has no image), the selected monster still supplies identity, and an upload still wins. A "Choose again" button next to Monster species appears after a lookup with several results and reopens the list for the same species without a new lookup for 20 minutes (selection tokens last 30); it hides when the species changes or the form resets. Only related tests were run locally; the full suite runs in CI.

CI for 6b92277d ([run 43408459349](https://github.com/dajomas/Scrying-Glass/actions/runs/43408459349)) failed: `test_fivetools_source_configuration` and `test_dndbeyond_locked_pages` run only some functions copied out of `scrying_glass_monster_selection.py`, and those copies lacked the new source-attribution helpers (NameError). The application code was not affected. Both tests now copy the helpers and pass locally with the next commit.

Choose again follow-up (2026-11-13, user report): Choose again cleared the selected image as soon as the list opened. It now keeps the current monster, image and signed tokens until a new monster is picked; Cancel in "Select monster candidate" keeps them, and Cancel in "Select monster image" after a new pick keeps the image shown before Choose again (`monster-candidate-selection.js?v=9`, `monster-image-choice.js?v=2`). A fresh lookup still starts from no selection, and image Cancel there keeps the selected monster's own image. Only related tests were run locally.

CI for c92119d7 ([run 43411555344](https://github.com/dajomas/Scrying-Glass/actions/runs/43411555344)) failed: the complete-Admin composition tests pin the script count at 44, and the new `monster-image-choice.js` makes 45. `tests/test_admin_global_feedback_composition.py` now expects 45; the 14 failing files pass locally with the next commit.

## Status

Stage 1 is documentation only. Stage 2 is implemented with acceptance pending; Open5e takes part in Refresh when enabled (user decision 2026-11-13). Stage 3 is not started.
