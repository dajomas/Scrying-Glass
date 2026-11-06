# 290 - Add Monsters image previews

[Back to handover index](../../HANDOVER.md)

Updated: 2026-11-06. Task: [SG-TODO-011](../todo/110-monster-image-previews.md). Status: implementation included; covering CI and user visual/workflow acceptance pending. Delivery follows the [agreed sequence](../todo/115-admin-delivery-sequence.md), before 009.4; it does not reopen accepted 009.3 or implement 012/013/014.

## User workflow

The manual-entry Image field shows the currently selected D&D Beyond/5e.tools candidate image, or the selected local image when present. Replace image in .monster import has an independent local-file preview. Wide layouts place previews to the right; narrow layouts stack them below their field. Images fit bounded containers without changing aspect ratio. Captions/alt text identify source or local filename. Loading and unavailable states do not alter input files, selected tokens or submission eligibility.

Local files override provider previews even if selected while a lookup/selection is pending. Clearing Image restores a provider image if its candidate is still selected. Species edits, overwrite changes, new lookups, cancellation and manual form reset clear the provider snapshot using the existing selection invalidation path. Reset of .monster upload clears only its replacement preview. Form reset updates preview after native reset; a failed submission does not explicitly clear fields or previews. A selected candidate without an image remains imageless, not replaced by another candidate's image.

Remote previews make browser image requests to selected HTTPS URLs, without URL credentials and using referrerPolicy=no-referrer. There is no extra provider lookup, server-side image proxy/download or bundled third-party image. Local previews use object URLs revoked on file replacement/reset/page hide; page restoration rebuilds them. A preview failure does not change existing server-side upload validation. Remote availability and browser access to provider image hosts still matter.

## Implementation and deployment

New static/monster-image-previews.js and .css are loaded by existing document-start/end fragments. CSS follows admin-panel-forms.css; the classic deferred script follows admin-panel-forms.js. Original input nodes and form ownership are retained. The preview installer waits for DOMContentLoaded for deferred loading/interactive execution and runs immediately for normal post-load injection, with duplicate-install protection. This keeps existing 009.3 field grouping ahead of preview wrapping.

static/monster-candidate-selection.js adds a scrying:monster-selection event containing only species, provider and image_url, or null on invalidation/new lookup. It publishes a selected candidate only after existing current-generation/request/species checks. Signed selection tokens and existing overwrite/stat guards remain owned by the original flow; raw candidate results are not modified. No core fragment, assembled-script marker, Python/API/persistence/schema, monster-row control or workflow configuration changes are included.

Deploy matching templates and the complete static tree together; restart the correct serving process because HTML fragments assemble at import, then refresh browsers. No database migration is required. Without preview initialization, existing file controls remain usable.

## Preparation evidence and limits

Executed: node --check for preview and candidate modules; tinycss2 stylesheet parsing; Python AST parsing for drafted regressions (including the final five-method revision); template inclusion/order/uniqueness/defer checks confirming only the two intended inclusions. A tiny PNG fixture was decoded successfully during preparation.

Simplified real-Chromium fixtures passed provider-source selection display, local-file precedence, independent replacement/reset and idempotence. A separate deferred boot fixture passed grouping-before-wrapping, preserved form ownership, repeat-install protection and zero page errors. Its first attempt failed because a loading-only readyState test did not defer interactive deferred scripts; the corrected condition passed the rerun. These fixtures use synthetic DOM and do not execute the complete Admin page, live providers or all prepared tests. No exhaustive accessibility audit or assistant visual acceptance is claimed.

## Prepared covering regressions and pending acceptance

New tests/test_monster_image_previews.py contains five methods: asset order/size contract; both providers plus local precedence/replacement/reset/revocation; popup selection, newer local file, cancellation/stale selection and no-image result; failed/unsafe URL and idempotence; full-Admin grouping/form ownership, desktop/narrow preview geometry, rejected-submit retention and screenshots. Provider fixtures reuse the existing real selection module and extracted core lookup through intercepted HTTP. The complete new module and full suite have not been executed during preparation; results remain pending CI.

The reviewed Branch tests workflow discovers test_*.py with tools/run_split_tests.py and uploads SG_VISUAL_ARTIFACTS. The full-Admin test prepares 011-1440-image-previews.png and 011-375-image-previews.png in the existing admin-foundations-visual-fixtures artifact. No workflow edit is needed. Screenshot generation/upload/appearance are not yet verified. Existing provider, token, lookup-focus, form, row and header regressions remain in place.

Review covering CI against the actual implementation commit, then obtain desktop/narrow visual and workflow acceptance for provider/local/replacement previews and existing add/import behaviour before closing 011. Retain fixture versus live-provider distinctions. No completed/green CI result is inferred from a commit. This implementation commit omits [skip ci] and relies on the configured push workflow, with no separate dispatch.

README.md and docs/User-Guide.md were reviewed and remain accurate without edits; this indexed handover records the new preview behaviour and deployment details. TODO status is in progress, not completed. The latest unrelated SG-TODO-014 index entry is preserved; its help-text change is not part of this delivery.
