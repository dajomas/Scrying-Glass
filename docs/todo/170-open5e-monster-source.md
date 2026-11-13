# 170. Open5e API monster source

[Back to TODO index](../../TODO.md)

- Task: SG-TODO-017
- Status: proposed
- Recorded: 2026-11-06
- Priority: not assigned; no change to the [agreed Admin delivery sequence](115-admin-delivery-sequence.md).
- Dependencies: verify the current Open5e API contract during implementation planning.
- Related tasks: [source-based monster selection](160-source-based-monster-selection.md), [source help text](140-monster-source-help-text.md), [image previews](110-monster-image-previews.md).

## Requested change

Add Open5e.com, accessed through its API, as a monster source in Scrying Glass.

## Proposed acceptance criteria

- Open5e monsters can be retrieved through the API and used in the Add Monster workflow.
- Supported monster fields map consistently to the application's monster model; missing data is handled explicitly rather than invented.
- Source attribution and distinct candidates remain identifiable when names overlap across providers or documents.
- API failures and empty results are distinguishable, with bounded requests and appropriate pagination handling.
- Existing D&D Beyond, 5e.tools and manual-entry workflows remain usable.
- Relevant source labels, configuration documentation and help texts reflect the delivered integration.

## Implementation decisions to resolve

Verify the supported API version, endpoints, available fields, document/source filtering, pagination, usage requirements and attribution/licensing requirements from current provider documentation. No specific API contract has been verified for this backlog entry.

Agree how Open5e is enabled and configured, its position (if any) in automatic fallback lookup, and how it participates in SG-TODO-016's source/monster dropdowns. Do not assume a new fallback order or default enablement from this request alone. Coordinate image handling with available provider data and SG-TODO-011.

## Validation required

Prepare provider and UI regression tests covering lookup, candidate selection, field mapping, missing data, pagination, empty results and provider failures. Verify representative live API responses separately from fixture-based tests and document any limits on catalog completeness or image availability.

## Delivery status

Backlog entry only. API research, implementation and validation remain outstanding.
