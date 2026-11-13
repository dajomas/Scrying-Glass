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

## Status

Stage 1 is documentation only, with no application, test or workflow changes and no tests run. Stages 2 and 3 are not started.
