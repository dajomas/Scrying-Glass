# 337. Signed selected monster source identity

[Automatic/shared order](336-monster-automatic-shared-order.md) |
[Task SG-TODO-018](../todo/180-monster-initiative-bonus.md)

Prepared 2026-11-07 for features/perplexity-018. Task remains incomplete.
No merge or write-back authorized.

## Baseline

Run 42387622122 attempt 1 reports success for exact tested commit
583ffb0a43fa8c14f2c3ec370568cd6c2ead026c. Its run.json was read at
publication 5f6a885b8087e6a7a8d3e5d18b0589fc2d05d0fa under
ci-results-42387622122-attempt-1. This is run-level metadata verification;
individual counts and assertions were not audited in this increment. Earlier
failed runs retain their original status.

## Scope

The existing image selection token now signs supported exact provider identity
alongside species, image and issue time. The process-local key, age limit,
species binding, constant-time signature check, token size cap and image URL
validator remain. A pure module handles identity capture/validation and signed
snapshot encoding/decoding. selected_image keeps its existing image-only API;
selected_snapshot exposes the authenticated source fields to creation.
Old signed image-only payloads remain compatible and manual selections retain
no source identity. Unsupported identities do not block otherwise usable image
selection; they simply supply no retained source fields.

Creation copies scalar monster_source_provider/url/name/book/legacy fields only
from a validated signed snapshot. Quantity copies retain the same identity and
separate monster IDs. Uploaded images retain precedence: a valid token may still
supply identity, but an invalid or expired token cannot supply identity and does
not override the existing upload-wins behavior. Selection neither re-fetches nor
re-resolves a browser URL. Lookup/fallback/candidate filtering, Admin UI and
constructor code are unchanged.

The accepted URL shapes are conservative HTTPS D&D Beyond monster paths and
5e.tools bestiary fragments. Credentials, custom ports, alternate hosts, query
substitution, malformed percent escapes and encoded controls are not retained.
The exact URL string is preserved. Available 5e.tools source codes and observed
legacy flags are metadata, not independently verified editions or entitlements.
D&D Beyond's unavailable-book placeholder is not stored as a real book.
No Dexterity inference, initiative extraction or source bonus origin assignment
is introduced. Identity metadata and initiative-bonus provenance stay separate.

## Checks and limitations

All 20 pure identity/signature methods passed locally. They exercise exact and
distinct identities, URL constraints, optional metadata, tampering, key/species
mismatch, expiry/future time, image validation, legacy tokens, manual/no-image
selections and independent snapshots. Image validation is injected into the pure
reader; production still supplies the existing ft.https_url validator.
The original selection module blob was verified and the prepared module parsed.
AST comparisons confirmed provider lookup/filtering/fallback functions unchanged.

Six direct creation methods are prepared, using the existing real constructor
fixture, but have not executed locally because FastAPI is unavailable. They are
not authenticated HTTP or persistence tests. No new-stage full-suite/CI pass is
claimed. Normal CI applies without skip marker or separate dispatch.

Only creation-output retention is delivered here. Actual save/reload/restart,
setup reuse and import provenance still require covering integration tests.
Imported or edited scalar metadata must not later be treated as authenticated
historical provider evidence merely because these field names are present;
source refresh must validate retained identity and handle import/reselection and
scope-bound review explicitly. Existing monsters are not backfilled by name.
No source fetch/refresh endpoint or UI is added. Provider initiative-format
verification/extraction, reviewed selected-monster refresh and all remaining
SG-TODO-018 acceptance still follow before completion.
