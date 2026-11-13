# 290 - Add Monsters image previews

[Back to handover index](../../HANDOVER.md)

Updated: 2026-11-06. Task: [SG-TODO-011](../todo/110-monster-image-previews.md). Status: completed at the user's request after verified covering corrective local/CI validation and user visual/workflow acceptance. Initial implementation: f8e2018f7c08b3e44011e6d2fcdecd26ab99a6bf. Accepted corrective source: d2c20b9b6ac5dd73218f072b4b07a80ac116ea04. Delivery follows the [agreed sequence](../todo/115-admin-delivery-sequence.md), before 009.4; it does not reopen accepted 009.3 or implement other backlog tasks.

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

Simplified real-Chromium fixtures passed provider-source selection display, local-file precedence, independent replacement/reset and idempotence. A separate deferred boot fixture passed grouping-before-wrapping, preserved form ownership, repeat-install protection and zero page errors. Its first attempt failed because a loading-only readyState test did not defer interactive deferred scripts; the corrected condition passed the rerun. These fixtures use synthetic DOM and did not execute the complete Admin page, live providers or all prepared tests. No exhaustive accessibility audit or assistant visual acceptance is claimed.

## Prepared covering regressions and initial acceptance gates

New tests/test_monster_image_previews.py contains five methods: asset order/size contract; both providers plus local precedence/replacement/reset/revocation; popup selection, newer local file, cancellation/stale selection and no-image result; failed/unsafe URL and idempotence; full-Admin grouping/form ownership, desktop/narrow preview geometry, rejected-submit retention and screenshots. Provider fixtures reuse the existing real selection module and extracted core lookup through intercepted HTTP. The complete new module and full suite were not executed during initial preparation; subsequent corrective validation is recorded below.

The reviewed Branch tests workflow discovers test_*.py with tools/run_split_tests.py and uploads SG_VISUAL_ARTIFACTS. The full-Admin test prepares 011-1440-image-previews.png and 011-375-image-previews.png in the existing admin-foundations-visual-fixtures artifact. No workflow edit was needed. Screenshot generation/upload/appearance were unverified at initial preparation; later successful capture/upload and review limits are recorded below. Existing provider, token, lookup-focus, form, row and header regressions remain in place.

Covering CI against the implementation and desktop/narrow visual/workflow acceptance were required before closure. These gates are satisfied by the corrective results and explicit acceptance below, not by the initial commit alone. Fixture versus live-provider distinctions remain. The mixed implementation commit omitted [skip ci] and relied on the configured push workflow, with no separate dispatch.

README.md and docs/User-Guide.md were reviewed and remain accurate without edits; this indexed handover records the new preview behaviour and deployment details. TODO status was in progress at implementation delivery, not completed. The then-latest unrelated SG-TODO-014 index entry was preserved; its help-text change was not part of that delivery.

## Combined sibling and empty-state alignment correction - 2026-11-06

The user's screenshots identify two presentation defects in initial implementation f8e2018f7c08b3e44011e6d2fcdecd26ab99a6bf. In Appearance and Import options, the shared row's align-items:end bottom-aligns sibling fields against the taller image wrapper. Within the wrapper, the preview starts beside the label rather than the file input, especially obvious for No image selected. The original sibling-only correction was a pending proposal, never committed, and was withdrawn when the empty-state requirement was identified. The revised correction was delivered as d2c20b9b6ac5dd73218f072b4b07a80ac116ea04; no prior commit was amended or rewritten.

static/monster-image-previews.css retains the scoped preview-group flex-start override and changes only the image wrapper's internal layout to a two-column/two-row grid. The existing label occupies column 1 across the two rows with grid-template-rows:subgrid, preserving its semantics and original input. The caption/label occupies row 1; the file input and preview figure share row 2. Input align-self:start prevents stretching to the image height. At max-width:600px the wrapper uses one column and places the preview in row 3 below the input. There is no hard-coded label-height offset, display:contents label removal or JavaScript measurement. CSS :has and subgrid support are required in the browser.

The added tests/test_monster_image_preview_alignment.py uses the existing full-Admin intercepted-HTTP fixture and tiny image data. It checks both groups at widths 1440/375 with loaded images and empty previews. Desktop assertions compare all sibling label tops within 1 px and each preview's top against its file input within 1 px, plus right-side placement. Narrow assertions require previews below the inputs and within viewport bounds. Empty states must actually contain No image selected and no img. Original field visibility, unrelated character-row end alignment, zero page errors and no unexpected mutations remain checked. Existing preview tests are retained; their prior right-of-field/bounds assertions did not cover these relationships.

Executed corrective preparation: stylesheet parsing with no stylesheet parse errors; Python AST parsing of the exact revised test; simplified real-Chromium geometry fixtures for Appearance and Import options at 1440/375, each with loaded/empty previews. Desktop sibling-label offsets and preview/input top offsets were 0 px in both states and groups. Narrow previews stacked below inputs within bounds; unrelated rows retained end alignment. These are synthetic fixture results, not measurements from the deployed page or execution of the full-Admin method. The earlier sibling-only synthetic fixture was not substituted for empty-state checks.

Existing test_*.py CI discovery covers the new method, with no workflow edits. Full-Admin/module/suite execution, covering corrective CI and deployed acceptance were pending at corrective delivery and are verified below. Screenshots were defect reports, not acceptance of the correction. No upload/provider/token/persistence logic changes were included.

The correction changed stylesheet, regression test and the existing task/handover notes only. README.md, HANDOVER.md and TODO.md remained accurate without edits because deployment instructions, links and in-progress status were unchanged. Normal push-triggered CI was enabled by omitting [skip ci]; no separate workflow was dispatched.

## Verified local results - 2026-11-06

Evidence commit 93000bf595285cbb706574230ca4ac1cc9faea35 publishes local-tests-d2c20b9/run-20261106T162035Z-nUq1rr. environment.txt identifies exact corrective source d2c20b9b6ac5dd73218f072b4b07a80ac116ea04, suite=all, detached clone, Python 3.14.7, Node 22.23.2 and WSL2. Run timestamps are 16:20:35Z-16:26:05Z and completed=1; uncommitted working-tree changes are not tested.

Reviewed summary.tsv and exit-code.txt record overall exit 0, syntax/import success, unittest success, pytest success, all 38 JavaScript command exits 0 and all six standalone exits 0. standalone-inventory.tsv maps script-2 to tests/audit_connection_lifetime.py. Its complete suites/standalone/script-2.log reports the repeated 1,059-test suite OK, 678 connections opened and zero without explicit close. suites/pytest/regressions.log reports 43 passes. The review verified command-level success and these selected summaries, not individual local pass lines for all preview methods. Repeated execution of the suite is not an additional set of distinct tests. Mocked provider exceptions in the audit log are fixture output, not test failures.

## Verified CI results - 2026-11-06

Branch tests run 42251417154 attempt 1 tested exact corrective source d2c20b9b6ac5dd73218f072b4b07a80ac116ea04 on features/perplexity via push. Evidence commit 2f6c8759e822aaea0d6872edc5bac764bafab4d1 contains ci-results-42251417154-attempt-1. run.json records completed/success for workflow, tests job and every configured step, including dependencies, syntax/import, unittest/browser fixtures, visual upload, pytest, JavaScript and standalone checks.

reader-chunks/index-000001.jsonl.txt maps workflow.log to file-000023. Reviewed chunks include:

- part-000072.txt: all six preview/alignment methods explicitly pass, including test_fields_and_preview_boxes_align_loaded_and_empty, full-Admin layout/rejected-submit/screenshots, asset order/size, both providers/local precedence/reset, failed/unsafe URL/idempotence and popup/stale/no-image behaviour.
- part-000070.txt: selected existing row controls and candidate-selection browser regressions pass.
- part-000073.txt: selected lookup-focus and marketplace regressions pass.
- part-000079.txt: main unittest summary reports 1,059 tests OK and the upload step identifies 16 fixture images.
- part-000080.txt: successful artifact finalisation/upload, artifact ID 13521101802, and 43 pytest passes.
- part-000106.txt: repeated connection-audit suite reports 1,059 tests OK with 678 connections and zero without explicit close; selected standalone audit output also passes.

artifact-files.txt lists 16 collected screenshots, including 011-1440-image-previews.png and 011-375-image-previews.png alongside existing foundation/header/forms views. Their capture test and upload/collection were verified, not assistant visual inspection of the images. This review covers metadata and selected explicit assertions/summaries, not every assertion in every log. Fixture/browser/provider limitations remain; successful CI does not establish authenticated live-provider/server or exhaustive accessibility coverage. Results validate the exact corrective source, not unrelated later changes automatically.

## User acceptance and completed close-out - 2026-11-06

The user explicitly accepted the visual presentation and workflows, including the combined loaded/empty alignment correction, while local tests and CI were in progress. After the successful local and CI evidence reviews, the user requested marking SG-TODO-011 completed. The existing acceptance was retained without asking for it again. This records user acceptance, not an assistant-executed deployed-server or full screen-reader audit. No further application/test correction was indicated by the reviewed results.

SG-TODO-011 is completed. SG-TODO-009 remains in progress with 009.1-009.3 closed and 009.4-009.7 proposed. Tasks 012-017 are not completed or implemented by this close-out; the next agreed redesign work remains 009.4 with 012 and 013 coordination. The sequence document's At recording status is a historical snapshot, not a new status override.

This documentation-only close-out updates TODO.md, the existing task and this handover. README.md and HANDOVER.md were reviewed and remain accurate without edits; existing links/runtime instructions are unchanged. No application, test or workflow code changes and no new test executions are included. The proposed/actual commit message contains [skip ci], no separate workflow is dispatched and no new workflow state is inferred from the marker.
