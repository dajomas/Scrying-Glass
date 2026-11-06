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

## Combined sibling and empty-state alignment correction - 2026-11-06

The user's screenshots identify two presentation defects in initial implementation f8e2018f7c08b3e44011e6d2fcdecd26ab99a6bf. In Appearance and Import options, the shared row's align-items:end bottom-aligns sibling fields against the taller image wrapper. Within the wrapper, the preview starts beside the label rather than the file input, especially obvious for No image selected. The original sibling-only correction was a pending proposal, never committed, and was withdrawn when the empty-state requirement was identified. This revised payload replaces it; no prior commit is amended or rewritten.

static/monster-image-previews.css retains the scoped preview-group flex-start override and changes only the image wrapper's internal layout to a two-column/two-row grid. The existing label occupies column 1 across the two rows with grid-template-rows:subgrid, preserving its semantics and original input. The caption/label occupies row 1; the file input and preview figure share row 2. Input align-self:start prevents stretching to the image height. At max-width:600px the wrapper uses one column and places the preview in row 3 below the input. There is no hard-coded label-height offset, display:contents label removal or JavaScript measurement. CSS :has and subgrid support are required in the browser.

Prepared tests/test_monster_image_preview_alignment.py uses the existing full-Admin intercepted-HTTP fixture and tiny image data. It checks both groups at widths 1440/375 with loaded images and empty previews. Desktop assertions compare all sibling label tops within 1 px and each preview's top against its file input within 1 px, plus right-side placement. Narrow assertions require previews below the inputs and within viewport bounds. Empty states must actually contain No image selected and no img. Original field visibility, unrelated character-row end alignment, zero page errors and no unexpected mutations remain checked. Existing preview tests are retained; their prior right-of-field/bounds assertions did not cover these relationships.

Executed preparation for the revised proposal: stylesheet parsing with no stylesheet parse errors; Python AST parsing of the exact revised test; simplified real-Chromium geometry fixtures for Appearance and Import options at 1440/375, each with loaded/empty previews. Desktop sibling-label offsets and preview/input top offsets were 0 px in both states and groups. Narrow previews stacked below inputs within bounds; unrelated rows retained end alignment. These are synthetic fixture results, not measurements from the deployed page or execution of the new full-Admin method. The earlier sibling-only synthetic fixture is not substituted for the new empty-state checks.

Existing test_*.py CI discovery covers the new method, with no workflow edits. Full-Admin regression/module/suite execution, covering corrective CI and user deployed visual/workflow acceptance remain pending. SG-TODO-011 remains in progress. Screenshots are defect reports, not acceptance of this correction. No upload/provider/token/persistence logic changes are included.

This correction changes stylesheet, regression test and the existing task/handover notes only. README.md, HANDOVER.md and TODO.md remain accurate without edits because deployment instructions, links and in-progress status are unchanged. Normal push-triggered CI is enabled by omitting [skip ci]; no separate workflow dispatch or unobserved run result is claimed.
