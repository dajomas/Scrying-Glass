# 110 - Add Monsters image previews

[Back to TODO index](../../TODO.md)

## SG-TODO-011 - Preview images beside Add Monsters image fields

- Status: proposed; not implemented by this TODO addition.
- Requested: 2026-11-06.
- Priority, owner and deadline: not assigned.
- Scope: image previews in the Add Monsters panel, including manual entry and the .monster import form. This is a separate backlog item, not an expansion or completion of SG-TODO-009.3.

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
- Previews appear to the right of the corresponding field at widths with sufficient space. Define and verify a usable narrow-screen layout without page-wide overflow or obscuring controls.
- Previews remain consistent with the image that will actually be submitted/imported, preserving existing upload precedence and selected-candidate continuity.
- Existing form IDs, handlers, validation, entered values, image upload/import behaviour and provider-selection semantics remain intact.

### Implementation considerations and validation to resolve

These are preparation requirements and safeguards, not claims of existing implementation or separately requested features:

- Inspect when provider images become available to the browser; do not assume an image exists before the current lookup/import pipeline has obtained it. Identify any pipeline changes needed for the requested preview.
- Define behaviour for replacement, clearing a file selection, form reset, failed submission, no-image results and image-load failures; prevent stale previews from representing the wrong image.
- Preserve in-flight edit protection so a delayed provider result does not overwrite a newer selected file/preview. Release temporary object URLs when replaced or cleared if that preview mechanism is used.
- Use bounded image dimensions, preserve aspect ratio, and provide an accessible preview description and clear unavailable-image handling.
- Prepare automated browser coverage for the three requested cases (testing both providers), image replacement/reset, upload precedence, delayed results, load failures and desktop/narrow layouts. Obtain visual/workflow acceptance before closure. Provider fixtures must be distinguished from live-provider evidence.

### Related work and recording scope

- [SG-TODO-001: monster lookup and candidate selection](010-monster-lookup.md) and [candidate-selection handover](../handover/200-monster-candidate-selection.md): preserve selected-image continuity, local-upload precedence and edit protection.
- [SG-TODO-009: Admin redesign](090-admin-usability-redesign.md) and [panel/forms handover](../handover/280-admin-panel-forms.md): integrate with the Add Monsters field groups and .monster import disclosure without changing unrelated redesign status.

This addition records requested work only. No application, test or workflow code is changed, and no tests are executed for this documentation-only addition. README.md and HANDOVER.md were reviewed and remain unchanged because no delivered runtime behaviour or handover index entry changes. The commit includes [skip ci]; no separate workflow dispatch or verified workflow-run outcome is implied.
