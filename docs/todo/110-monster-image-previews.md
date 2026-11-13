# 110 - Add Monsters image previews

[Back to TODO index](../../TODO.md)

## SG-TODO-011 - Preview images beside Add Monsters image fields

- Status: completed, 2026-11-06, at the user's request after verified covering corrective local/CI results and user visual/workflow acceptance.
- Requested: 2026-11-06. Implementation requested subsequently on the same date.
- Priority, owner and deadline: not assigned. Delivery order is agreed in [Admin delivery sequence](115-admin-delivery-sequence.md): 011 precedes 009.4.
- Scope: image previews in the Add Monsters panel, including manual entry and the .monster import form. This remains separate from accepted SG-TODO-009.3.
- Initial implementation: f8e2018f7c08b3e44011e6d2fcdecd26ab99a6bf. Accepted corrective implementation: d2c20b9b6ac5dd73218f072b4b07a80ac116ea04.

### Requested behaviour

| Image source | Preview location |
|---|---|
| Image collected from D&D Beyond or 5e.tools | On the right side of the Image field in the manual monster-entry form |
| Local image file selected in the Image field | On the right side of that Image field |
| Local image file selected in the Replace image field | On the right side of that Replace image field in the .monster import form |

Display the actual collected or selected image, not only a filename or URL. Update the corresponding preview when a new image is collected or selected. Keep the Image and Replace image previews associated with their own fields rather than showing a single shared preview.

### Acceptance criteria

- Both D&D Beyond and 5e.tools image results can populate the preview beside Image.
- Selecting a local file in Image shows that file beside Image.
- Selecting a local file in Replace image shows that file beside Replace image.
- Previews appear to the right of the corresponding field at widths with sufficient space. Narrow-screen stacking must avoid page-wide overflow or obscuring controls.
- Previews remain consistent with the image that will actually be submitted/imported, preserving existing upload precedence and selected-candidate continuity.
- Existing form IDs, handlers, validation, entered values, image upload/import behaviour and provider-selection semantics remain intact.

### Implementation and initial verification gates - 2026-11-06

The existing candidate lookup already exposes image_url. The implementation publishes selection/invalidation notifications from that guarded flow without changing the signed token or adding another lookup. Separate preview containers retain original file inputs. Local files take precedence; clearing Image restores a still-selected provider result. Species edits, new lookup, Cancel and reset invalidate provider previews. The replacement-file preview stays independent. Load failure reports unavailable without changing submission data. HTTPS provider URLs without embedded credentials are rendered directly by the browser with no referrer; local files use temporary object URLs released on replacement/reset/page hide. Narrow layouts stack the preview below its field.

Matching stylesheet/script references and DOMContentLoaded initialization preserve 009.3 grouping before preview wrapping, including deferred scripts executing while readyState is interactive. See [implementation, deployment and validation record](../handover/290-monster-image-previews.md).

Executed preparation: JavaScript syntax, CSS stylesheet parsing, regression Python AST parsing, template inclusion/order checks and simplified real-Chromium smoke/boot-order fixtures. These were not execution of the complete prepared regression module or authenticated live-server checks. The first synthetic boot-order attempt failed; its initialization condition was corrected and the repeated fixture passed.

Prepared regressions cover both provider labels, selected image/token continuity, local precedence, replacement/reset/URL cleanup, popup choice, a newer local file during pending selection, cancellation/stale selection, missing/failed/unsafe image URLs, idempotence, full-Admin boot/group compatibility, failed-submit retention and desktop/narrow geometry/screenshots. Existing CI discovery and artifact upload cover the new module; workflow configuration is unchanged. Full module/suite/CI execution and visual/workflow acceptance were pending at initial delivery; the verified results and acceptance below supersede that status. Live remote-image availability is distinct from intercepted fixture responses.

### Related work

- [SG-TODO-001: monster lookup and candidate selection](010-monster-lookup.md) and [candidate-selection handover](../handover/200-monster-candidate-selection.md): selected-image continuity, local-upload precedence and edit protection.
- [SG-TODO-009: Admin redesign](090-admin-usability-redesign.md) and [panel/forms handover](../handover/280-admin-panel-forms.md): preserve field groups and .monster disclosure without changing unrelated redesign status.

The original TODO addition was planning only and used [skip ci]. The mixed implementation delivery did not use that marker and relied on normal branch-push CI. SG-TODO-012/013/014 were not implemented by that increment.

### Loaded and empty preview alignment correction - 2026-11-06

The user supplied screenshots showing two alignment defects in initial implementation f8e2018f7c08b3e44011e6d2fcdecd26ab99a6bf: sibling fields bottom-aligned against a tall image preview, and the No image selected box aligned with the field label instead of the file input. The earlier sibling-only proposal was not committed and was superseded by the combined correction in d2c20b9b6ac5dd73218f072b4b07a80ac116ea04.

The scoped stylesheet top-aligns preview-containing group rows and uses a two-row grid with the original image label spanning shared subgrid tracks. Both loaded previews and empty-state boxes start on the file-input row, without a fixed label-height offset. Narrow layouts put the preview in a separate row below the input. Original labels, inputs, handlers and image-selection behaviour are unchanged. Modern browser support for CSS :has and subgrid is required.

The added tests/test_monster_image_preview_alignment.py explicitly checks both Appearance and Import options at 1440/375, loaded and empty, including desktop label-top equality, preview/input top equality, right-side placement, narrow stacking/bounds and unchanged unrelated-row alignment. Corrective preparation passed stylesheet parsing, test Python AST parsing and simplified Chromium geometry checks for both groups in all four width/state combinations; desktop preview/input and sibling-label offsets were 0 px. Covering corrective validation and acceptance were pending at corrective delivery; results below supersede that historical gate.

### Verified completion - 2026-11-06

Completed at the user's request after validation of exact corrective source d2c20b9b6ac5dd73218f072b4b07a80ac116ea04 and the user's visual/workflow acceptance, including loaded and empty alignment. That acceptance was given before the final result review and was not requested again.

Local evidence: commit 93000bf595285cbb706574230ca4ac1cc9faea35, folder local-tests-d2c20b9/run-20261106T162035Z-nUq1rr. Metadata identifies the exact source and completed full run; overall and all command-summary exits are 0. The repeated connection-audit suite reports 1,059 tests OK, 678 connections opened and zero without explicit close; pytest reports 43 passes. Individual preview method pass lines were not separately inspected in the local review.

CI evidence: Branch tests run 42251417154 attempt 1, published at 2f6c8759e822aaea0d6872edc5bac764bafab4d1 under ci-results-42251417154-attempt-1. Metadata identifies exact source above on features/perplexity and completed/success for workflow, tests job and every configured step. Main unittest reports 1,059 tests OK; all five initial preview methods and the corrective alignment method explicitly passed; pytest reports 43 passes; repeated connection audit reports 1,059 tests OK with 678/0 connections. Sixteen screenshots were successfully uploaded and collected, including the two 011 desktop/narrow views. See the handover for inspected log locations and coverage limits.

Fixtures are not authenticated live-server/provider or exhaustive accessibility evidence. Upload/collection is not assistant visual inspection of each image. User acceptance and automated evidence are recorded separately; no broader redesign acceptance or completion of tasks 012-017 is implied. Overall SG-TODO-009 remains in progress and its next agreed work is 009.4 with 012/013 coordination.

This close-out changes documentation only, executes no new tests and leaves application/test/workflow code unchanged. README.md and HANDOVER.md remain accurate without edits. The commit contains [skip ci], dispatches no separate workflow and does not infer any unobserved workflow result.
