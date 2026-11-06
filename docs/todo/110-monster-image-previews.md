# 110 - Add Monsters image previews

[Back to TODO index](../../TODO.md)

## SG-TODO-011 - Preview images beside Add Monsters image fields

- Status: in progress; implementation included, covering CI and visual/workflow acceptance pending.
- Requested: 2026-11-06. Implementation requested subsequently on the same date.
- Priority, owner and deadline: not assigned. Delivery order is agreed in [Admin delivery sequence](115-admin-delivery-sequence.md): 011 precedes 009.4.
- Scope: image previews in the Add Monsters panel, including manual entry and the .monster import form. This remains separate from accepted SG-TODO-009.3.

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

### Implementation and pending verification - 2026-11-06

The existing candidate lookup already exposes image_url. The implementation publishes selection/invalidation notifications from that guarded flow without changing the signed token or adding another lookup. Separate preview containers retain original file inputs. Local files take precedence; clearing Image restores a still-selected provider result. Species edits, new lookup, Cancel and reset invalidate provider previews. The replacement-file preview stays independent. Load failure reports unavailable without changing submission data. HTTPS provider URLs without embedded credentials are rendered directly by the browser with no referrer; local files use temporary object URLs released on replacement/reset/page hide. Narrow layouts stack the preview below its field.

Matching stylesheet/script references and DOMContentLoaded initialization preserve 009.3 grouping before preview wrapping, including deferred scripts executing while readyState is interactive. See [implementation, deployment and validation record](../handover/290-monster-image-previews.md).

Executed preparation: JavaScript syntax, CSS stylesheet parsing, regression Python AST parsing, template inclusion/order checks and simplified real-Chromium smoke/boot-order fixtures. These are not execution of the complete prepared regression module or authenticated live-server checks. The first synthetic boot-order attempt failed; its initialization condition was corrected and the repeated fixture passed.

Prepared regressions cover both provider labels, selected image/token continuity, local precedence, replacement/reset/URL cleanup, popup choice, a newer local file during pending selection, cancellation/stale selection, missing/failed/unsafe image URLs, idempotence, full-Admin boot/group compatibility, failed-submit retention and desktop/narrow geometry/screenshots. Existing CI discovery and artifact upload cover the new module; workflow configuration is unchanged. Full module/suite/CI execution and visual/workflow acceptance remain pending. Define no completed status until those gates are reviewed. Live remote-image availability is distinct from intercepted fixture responses.

### Related work

- [SG-TODO-001: monster lookup and candidate selection](010-monster-lookup.md) and [candidate-selection handover](../handover/200-monster-candidate-selection.md): selected-image continuity, local-upload precedence and edit protection.
- [SG-TODO-009: Admin redesign](090-admin-usability-redesign.md) and [panel/forms handover](../handover/280-admin-panel-forms.md): preserve field groups and .monster disclosure without changing unrelated redesign status.

The original TODO addition was planning only and used [skip ci]. This mixed implementation delivery does not use that marker and relies on normal branch-push CI; no run result is inferred. SG-TODO-012/013/014 are not implemented by this increment.
