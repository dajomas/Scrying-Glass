# 200 - Monster candidate selection

[Back to handover index](../../HANDOVER.md)

Initial increment: 2c00583fb0c37b940d8580e324816a39960995e8, delivered 2026-11-02.
Locked-page correction prepared: 2026-11-02 against that commit.

## Scope and implementation

This is the agreed public-provider candidate increment, not completion of the
[account-backed SG-TODO-001](../todo/010-monster-lookup.md).
No credentials, account storage, database migration or entitlement checks are added.

GET /api/monsters/lookup requires the existing admin authentication and runs remote
work in a thread without holding the serialized encounter lock. It returns a
status and candidates. D&D Beyond comes first; 5e.tools runs only after successful
zero usable matches or primary disablement. Missing D&D pages (404), positively
identified access gates and pages with no parseable AC/HP are excluded. Other
retrieval/parser exceptions stop enumeration with a sanitized error. A no-stats
page alone cannot distinguish restricted content from unsupported markup.

The deferred script intercepts only the existing UI stats-request path and leaves
the original AC/HP application and edit guards intact. Multiple results use a
native modal dialog with keyboard Escape cancellation, restored focus and source
links. Single results do not open a dialog. Manual creation is blocked while a
lookup/selection is pending. Species edits/reset invalidate the image selection.

POST /api/monsters accepts an optional selection_token. Signed snapshots bind the
species and selected image, expire after 30 minutes and become invalid on process
restart. They are public-result integrity tokens, not account credentials. Invalid
or expired snapshots return 422 unless an uploaded image takes precedence. A
manual sentinel disables automatic image lookup. Absence of a token retains the
legacy API behavior. A selected candidate with no image stays imageless rather
than searching for another candidate. Imports retain their previous behavior.
The old /api/dndbeyond/monster-stats endpoint remains first-result based.

## Limits and operation

Maximum 32 D&D search hits, 32 configured fallback sources and 32 usable fallback
candidates; exceeding limits reports an error instead of silently truncating.
Source searches are sequential and cold requests may be slow. Existing bounded
JSON cache and remote request timeouts are reused. Unresolved 5e.tools inheritance
remains unsupported. Deduplication uses D&D hrefs or fallback source URL plus stats
and image; distinct variants are not merged. Legacy/current labels are provider
metadata/heuristics, not guaranteed edition identifiers. D&D source-book names
are unavailable and are labeled accordingly.

Deploy the changed Python, script and template together, restart and reload the
browser. Native HTML dialog support is required. The Add monster form always
sends a selected snapshot or manual sentinel; manual/cancelled/failed lookup does
not initiate an independent creation-time image search. Upload an image manually
when desired. No new third-party data is bundled.

## Locked-page correction and validation - 2026-11-02

The user reported green CI for the preceding increment, then reported locked
Crawling Claw pages preventing 5e.tools fallback. No actual response/traceback or
workflow run artifact was provided, so neither the precise live failure mechanism
nor an independently inspected successful run is claimed.

The shared dnd_monster_detail_html helper now returns empty HTML for narrowly
matched visible access-denial/purchase messages and HTTPS D&D Beyond redirects
to /marketplace, /login or /sign-in (including descendants). Script, style,
header, footer and nav text is ignored by the message classifier. Recognized
challenge wording vetoes text-based lock classification. A 401/403 is classified
only with positive body evidence, using at most 128001 bytes and refusing oversized
bodies; generic denial statuses do not count as locked. Other HTTP failures,
timeouts and untrusted/unknown redirects continue to raise. The existing 8 MB
successful-page limit remains. Raw redirect URLs are not included in new errors.

Empty HTML is parsed as no stats, so selection excludes that candidate and reaches
5e.tools only if none remain. Existing callers of the shared detail helper also
receive empty HTML for recognized access gates; the separate creation-time legacy
image scraper is unchanged. There is no authentication or attempt to retrieve
locked stats. Unknown wording and other redirect destinations remain a limitation;
this patch is not proof of live D&D Beyond compatibility.

Nine offline regression tests passed on the prepared correction. They cover gate
text, bounded denial bodies, trusted versus untrusted redirects, generic errors,
unchanged usable stats and all-locked versus mixed-candidate provider ordering.
The local tree used the hash-verified original provider source plus the correction,
and reconstructed unchanged production selection-function definitions. Selection
checks execute AST-extracted functions with mocked fallback/token/image-URL helpers,
not the full FastAPI application. Synthetic responses are not captured live pages.
Python source compilation passed. Full CI, browser/application integration and
actual Crawling Claw validation are still pending for this corrective commit.

Earlier draft-harness checks were likewise not application end-to-end coverage.
Existing CI discovers the new test_*.py module; no workflow change or skip marker
is needed. README was reviewed and remains accurate: provider errors still stop
candidate lookup, while confirmed locked pages are excluded candidates. HANDOVER.md
links are unchanged; the existing TODO index and section record the correction.
Keep SG-TODO-001 open pending its acceptance evidence and deferred account work.
