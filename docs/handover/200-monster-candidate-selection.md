# 200 - Monster candidate selection

[Back to handover index](../../HANDOVER.md)

Prepared: 2026-11-02 against 1dba198c19803747afff78f5d32dd70e982e5467.

## Scope and implementation

This is the agreed public-provider candidate increment, not completion of the
[account-backed SG-TODO-001](../todo/010-monster-lookup.md).
No credentials, account storage, database migration or entitlement checks are added.

GET /api/monsters/lookup requires the existing admin authentication and runs remote
work in a thread without holding the serialized encounter lock. It returns a
status and candidates. D&D Beyond comes first; 5e.tools runs only after successful
zero usable matches or primary disablement. Any retrieval/parser exception other
than a missing D&D page (404) stops enumeration with a sanitized error. Pages with
no parseable AC/HP are excluded; this cannot distinguish restricted content from
unsupported markup. Live provider compatibility is not claimed.

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

## Validation evidence and pending work

During draft preparation, ten offline tests passed in a restricted Python harness
with substituted FastAPI imports and unrelated base class. That evidence does not
validate the final revised files, real route composition, HTTP or live providers.
The final offline and intercepted-HTTP Chromium test modules are prepared but not
yet executed. Existing unittest discovery in Branch tests includes both modules.
No CI run, successful workflow or full application test result is claimed.

Required follow-up: review normal push-triggered CI; verify actual authenticated
lookup/creation, uploads, expired tokens, restart behavior and player images;
perform authorized live-provider checks. Chromium fixtures use intercepted HTTP
and are not full application end-to-end coverage. Keep the TODO open until the
increment's acceptance evidence is reviewed; account authentication remains
separately deferred. README and indexed TODO/handover describe this distinction.
