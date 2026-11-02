# 200 - Monster candidate selection

[Back to handover index](../../HANDOVER.md)

Initial increment: 2c00583fb0c37b940d8580e324816a39960995e8, delivered 2026-11-02.
Locked-page correction: fe392f77c0080d3ca3540abfbb301fc94ec9655a.
Marketplace and blur-loop fixes: 846971b1ada9b5e44df8b7dca238c092e43efb47.
Regression-test follow-up prepared: 2026-11-02 against 846971b.

## Scope and implementation

This is the agreed public-provider candidate increment, not account-backed access.
See [SG-TODO-001](../todo/010-monster-lookup.md). No credentials, account storage,
database migration or entitlement checks are added.

GET /api/monsters/lookup uses existing admin authentication and threaded remote
work outside the serialized encounter lock. D&D Beyond comes first; 5e.tools runs
only after zero usable matches or primary disablement. Missing pages (404), known
access gates and pages without parseable AC/HP are excluded. Other retrieval or
parser failures stop enumeration with a sanitized error. A no-stats page alone
cannot distinguish restricted content from unsupported markup.

The extension retains the original stats application and overwrite/edit guards.
Single results are automatic; multiple results use a native modal dialog with
source links, Cancel/Escape and focus restoration. Creation is blocked while a
lookup/selection is pending. Species edits/reset invalidate the selection. The
600 ms debounced input lookup remains; the species blur lookup was removed in
846971b because opening the dialog triggered it, cancelled the popup, restored
input focus and repeated the lookup.

POST /api/monsters accepts a signed selection_token binding species and image.
It expires after 30 minutes or process restart. Invalid/expired tokens return 422
unless an uploaded image takes precedence. The manual sentinel disables automatic
image lookup; absence of a token retains legacy API behavior. A selected candidate
with no image remains imageless. Imports and the legacy first-result stats endpoint
retain their previous behavior. These are public-result integrity tokens, not
account credentials.

## Access gates, limits and operation

The shared detail helper returns empty HTML for narrowly matched visible denial
or purchase messages and trusted HTTPS D&D Beyond /marketplace, /login and /sign-in
redirects (including descendants). Since 846971b it also excludes HTTPS redirects
to marketplace.dndbeyond.com/category/, without URL credentials. The observed
Crawling Claw destination was /category/monster-manual on that host. This gate is
not trusted as a source of monster stats. Unknown/external destinations still fail.

The message classifier ignores script/style/header/footer/nav text and recognized
challenge wording vetoes text-based classification. A 401/403 needs positive body
evidence, with a 128001-byte read and rejection above 128000 bytes. Generic denial
statuses, other HTTP errors and timeouts still raise. The successful-page limit
remains 8 MB. No paid-content retrieval or access-control bypass occurs. The shared
helper's other callers also receive empty HTML for access gates; the independent
legacy creation-time image scraper is unchanged.

Limits: 32 D&D search hits, 32 fallback sources and 32 usable fallback candidates.
Overflow is an error, not silent truncation. Searches are sequential; existing JSON
cache and request timeouts remain. Unresolved 5e.tools inheritance is unsupported.
Deduplication uses D&D hrefs or fallback source URL plus stats/image. Source/edition
labels are provider metadata or heuristics; D&D source-book names are unavailable.
Unknown gate wording/destinations may still need evidence-based follow-up.

Deploy Python, script and template together, restart and reload. Native HTML dialog
support is required. Manual/cancelled/failed form lookup does not independently
search again for a creation-time image. Upload an image manually when desired.
No third-party data is bundled.

## Validation evidence and pending close-out - 2026-11-02

Earlier status notes saying the live traceback/redirect was unavailable are
superseded: the user supplied the marketplace hostname/path, applied the targeted
fix and confirmed fallback. The user also confirmed that removing the blur handler
resolved the repeated requests and popup focus issue; both fixes are in 846971b.

On 2026-11-02 the user confirmed green CI for 846971b and all requested manual
checks: locked-page fallback, popup without manually leaving the input, chosen
stats, automatic single match, Cancel/Escape/manual entry, selected-image continuity,
upload precedence and preservation of existing/in-flight AC/HP edits. These are
user-reported results; no workflow run ID, test count or independently inspected
CI artifact is invented.

Nine synthetic offline tests passed during the earlier locked-page correction,
using reconstructed unchanged selection definitions and mocked dependencies, not
full application integration. They missed the real marketplace subdomain and
actual blur wiring. The follow-up adds two test modules:

- test_monster_lookup_live_regressions.py: four offline tests using the real provider
  and selection modules with mocked HTTP/fallback; covers the exact marketplace URL,
  all-locked fallback, mixed-primary priority and rejection boundaries. Despite the
  filename, no live provider request occurs.
- test_monster_lookup_focus_browser.py: three Chromium tests type through extracted
  production species listeners and lookup code, preserving any reintroduced blur
  handler. They check one stable popup/request, focus transfer/restoration, selection,
  Cancel, Escape and ordinary blur without relookup. HTTP is intercepted and unrelated
  page infrastructure is stubbed. This is not full FastAPI/browser end-to-end coverage.

Both new Python sources compiled during preparation. The new tests have not been
executed locally; their runtime results and full-suite compatibility are pending CI.
Existing Branch tests unittest discovery includes both test_*.py modules; no workflow
change or skip marker is needed for the regression push. There are no runtime changes.
README and HANDOVER.md index were reviewed and need no changes for this test delivery.

At the user's request, leave TODO completion for a separate documentation commit
only after the regression commit's CI is confirmed green. That follow-up must use
[skip ci], update the indexed TODO and validation notes, and preserve deferred
account-authentication/entitlement requirements rather than marking them implemented.
No closure or new green-CI result is claimed by this regression-test commit.
